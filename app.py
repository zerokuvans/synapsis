from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
import logging
import pytz
import os
from datetime import date, datetime
import bcrypt
import json
import io
import csv
import threading
import time
import random
import pandas as pd
import asyncio

import requests
from playwright.sync_api import sync_playwright, TimeoutError
from playwright.async_api import async_playwright
import re
from api_reportes import login_required_api
app = Flask(__name__)
app.secret_key = 'synapsis-secret-key-2024-production-secure-key-12345'
db = SQLAlchemy()

# Configuración de zona horaria
TIMEZONE = pytz.timezone('America/Bogota')

simit_playwright_lock = threading.Lock()

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirigir al login cuando se requiera autenticación

@login_manager.unauthorized_handler
def unauthorized():
    # Devolver JSON para llamadas a API (evitar HTML que rompe fetch)
    try:
        print(f"DEBUG unauthorized_handler: request.path = {request.path}")
        # Endpoints que deben devolver JSON en lugar de redirigir
        api_endpoints = ['/api/', '/preoperacional', '/login']
        if any(request.path.startswith(endpoint) for endpoint in api_endpoints):
            print(f"DEBUG: Devolviendo JSON 401 para {request.path}")
            return jsonify({'success': False, 'error': 'AUTH_REQUIRED', 'message': 'Autenticación requerida'}), 401
        print(f"DEBUG: Redirigiendo a login para {request.path}")
        return redirect(url_for('login'))
    except Exception as e:
        print(f"DEBUG: Exception en unauthorized_handler: {e}")
        # Fallback seguro
        return redirect(url_for('login'))

# Roles definition
ROLES = {
    '1': 'administrativo',
    '2': 'tecnicos',
    '3': 'operativo',
    '4': 'contabilidad',
    '5': 'logistica',
    '6': 'sstt'
}

# Definición de la clase User para Flask-Login
class User(UserMixin):
    def __init__(self, id, nombre, role):
        self.id = id
        self.nombre = nombre
        self.role = role
    
    def has_role(self, role):
        return self.role == role

# Función para cargar usuario para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    connection = get_db_connection()
    if connection is None:
        return None
        
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id_codigo_consumidor, nombre, id_roles FROM recurso_operativo WHERE id_codigo_consumidor = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if user_data:
        return User(
            id=user_data['id_codigo_consumidor'],
            nombre=user_data['nombre'],
            role=ROLES.get(str(user_data['id_roles']))
        )
    return None

# Función para obtener conexión a la base de datos
def get_db_connection():
    try:
        host = os.getenv('MYSQL_HOST') or 'localhost'
        user = os.getenv('MYSQL_USER') or 'root'
        password = os.getenv('MYSQL_PASSWORD') or '732137A031E4b@'
        database = os.getenv('MYSQL_DB') or os.getenv('MYSQL_DATABASE') or 'capired'
        port_val = os.getenv('MYSQL_PORT')
        if port_val:
            connection = mysql.connector.connect(host=host, user=user, password=password, database=database, port=int(port_val))
        else:
            connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        return connection
    except mysql.connector.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Utilidades para columnas dinámicas en mpa_mantenimientos
def ensure_mantenimiento_general_column(connection):
    try:
        if not set_parts:
            connection.close()
            return jsonify({'success': False, 'message': 'Sin cambios'}), 400
        cur = connection.cursor()
        cur.execute("SHOW COLUMNS FROM mpa_mantenimientos LIKE 'tipo_general_mantenimiento'")
        if not cur.fetchone():
            try:
                cur.execute("ALTER TABLE mpa_mantenimientos ADD COLUMN tipo_general_mantenimiento VARCHAR(64) NULL")
                connection.commit()
            except Exception:
                pass
            try:
                cur_null = connection.cursor()
                cur_null.execute(
                    """
                    SELECT IS_NULLABLE FROM information_schema.columns
                    WHERE table_schema = DATABASE() AND table_name = 'sstt_vencimientos_cursos' AND column_name = 'sstt_vencimientos_cursos_fecha'
                    """
                )
                res_f = cur_null.fetchone()
                if res_f and str(res_f[0]).upper() == 'NO':
                    cur_alter_f = connection.cursor()
                    cur_alter_f.execute("ALTER TABLE sstt_vencimientos_cursos MODIFY COLUMN sstt_vencimientos_cursos_fecha DATE NULL DEFAULT NULL")
                    connection.commit()
                    cur_alter_f.close()
                cur_null.execute(
                    """
                    SELECT IS_NULLABLE FROM information_schema.columns
                    WHERE table_schema = DATABASE() AND table_name = 'sstt_vencimientos_cursos' AND column_name = 'sstt_vencimientos_cursos_fecha_ven'
                    """
                )
                res_v = cur_null.fetchone()
                if res_v and str(res_v[0]).upper() == 'NO':
                    cur_alter_v = connection.cursor()
                    cur_alter_v.execute("ALTER TABLE sstt_vencimientos_cursos MODIFY COLUMN sstt_vencimientos_cursos_fecha_ven DATE NULL DEFAULT NULL")
                    connection.commit()
                    cur_alter_v.close()
                cur_null.close()
            except Exception:
                pass
        cur.close()
    except Exception:
        try:
            connection.rollback()
        except Exception:
            pass

def has_mantenimiento_general_column(connection):
    try:
        cur = connection.cursor()
        cur.execute("SHOW COLUMNS FROM mpa_mantenimientos LIKE 'tipo_general_mantenimiento'")
        exists = bool(cur.fetchone())
        cur.close()
        return exists
    except Exception:
        return False

def ensure_mantenimiento_subcats_column(connection):
    try:
        cur = connection.cursor()
        cur.execute("SHOW COLUMNS FROM mpa_mantenimientos LIKE 'tipo_general_subcategorias'")
        if not cur.fetchone():
            try:
                cur.execute("ALTER TABLE mpa_mantenimientos ADD COLUMN tipo_general_subcategorias TEXT NULL")
                connection.commit()
            except Exception:
                pass
        cur.close()
    except Exception:
        try:
            connection.rollback()
        except Exception:
            pass

def has_mantenimiento_subcats_column(connection):
    try:
        cur = connection.cursor()
        cur.execute("SHOW COLUMNS FROM mpa_mantenimientos LIKE 'tipo_general_subcategorias'")
        exists = bool(cur.fetchone())
        cur.close()
        return exists
    except Exception:
        return False

def ensure_riesgo_table():
    try:
        conn = get_db_connection()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mpa_riesgo_accidentes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lat DOUBLE NOT NULL,
                lon DOUBLE NOT NULL,
                fecha DATE NULL,
                tipo_vehiculo VARCHAR(64) NULL,
                localidad VARCHAR(128) NULL,
                gravedad VARCHAR(64) NULL,
                fuente VARCHAR(64) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_lat (lat),
                INDEX idx_lon (lon),
                INDEX idx_fecha (fecha),
                INDEX idx_tipo (tipo_vehiculo),
                INDEX idx_localidad (localidad)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        conn.commit()
        cur.close(); conn.close()
    except Exception:
        pass

ensure_riesgo_table()

def ensure_mpa_comparendos_table():
    try:
        conn = get_db_connection()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mpa_comparendos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                placa VARCHAR(32) NOT NULL,
                tecnico_id INT NULL,
                tecnico_nombre VARCHAR(128) NULL,
                tipo_vehiculo VARCHAR(64) NULL,
                tiene_multas ENUM('SI','NO') NOT NULL,
                cantidad INT NULL,
                valor_total DECIMAL(12,2) NULL,
                fuente VARCHAR(32) DEFAULT 'SIMIT',
                fecha_ultima_consulta DATETIME NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uk_mpa_comparendos_placa (placa),
                INDEX idx_mpa_comparendos_tecnico (tecnico_id),
                INDEX idx_mpa_comparendos_fecha (fecha_ultima_consulta)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        conn.commit()
        cur.close(); conn.close()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass

ensure_mpa_comparendos_table()

def ensure_mpa_comparendos_detalle_table():
    try:
        conn = get_db_connection()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mpa_comparendos_detalle (
                id INT AUTO_INCREMENT PRIMARY KEY,
                placa VARCHAR(32) NOT NULL,
                referencia VARCHAR(128) NULL,
                fecha DATE NULL,
                valor DECIMAL(12,2) NULL,
                entidad VARCHAR(128) NULL,
                estado VARCHAR(64) NULL,
                raw_json TEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_comp_det_placa (placa),
                INDEX idx_comp_det_fecha (fecha)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        conn.commit()
        cur.close(); conn.close()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass

ensure_mpa_comparendos_detalle_table()

@app.route('/api/mpa/simit/resultados', methods=['GET'])
@login_required
def api_simit_resultados():
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        placa = (request.args.get('placa') or '').strip().upper()
        tecnico = (request.args.get('tecnico') or '').strip()
        where = []
        params = []
        if placa:
            where.append("UPPER(TRIM(placa)) = %s")
            params.append(placa)
        if tecnico:
            try:
                tid = int(tecnico)
                where.append("tecnico_id = %s")
                params.append(tid)
            except Exception:
                where.append("tecnico_nombre LIKE %s")
                params.append('%'+tecnico+'%')
        query = "SELECT placa, tecnico_id, tecnico_nombre, tipo_vehiculo, tiene_multas, cantidad, valor_total, fuente, fecha_ultima_consulta FROM mpa_comparendos"
        if where:
            query += " WHERE " + " AND ".join(where)
        query += " ORDER BY fecha_ultima_consulta DESC, placa"
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        for r in rows:
            d = r.get('fecha_ultima_consulta')
            if d:
                try:
                    r['fecha_ultima_consulta'] = d.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    pass
            try:
                c_val = r.get('cantidad')
                v_val = r.get('valor_total')
                c_num = int(str(c_val).strip()) if c_val is not None else 0
            except Exception:
                c_num = 0
            try:
                v_num = float(str(v_val).strip()) if v_val is not None else 0.0
            except Exception:
                v_num = 0.0
            r['tiene_multas'] = 'SI' if (c_num > 0 or v_num > 0) else 'NO'
            if v_num > 0 and c_num <= 0:
                r['cantidad'] = 1
        return jsonify({'success': True, 'data': rows})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

def _num(v):
    try:
        s = str(v).replace(',', '').replace('$', '').strip()
        if s == '':
            return 0.0
        return float(s)
    except Exception:
        return 0.0

def _update_comparendos_from_result(placa, tecnico_id, tecnico_nombre, tipo, result_data):
    conn = get_db_connection()
    if conn is None:
        return {'success': False, 'message': 'BD no disponible'}
    try:
        items = []
        total_multas = None
        if isinstance(result_data, dict):
            for k, v in result_data.items():
                if isinstance(v, list):
                    items.extend(v)
            maybe_data = result_data.get('data')
            if isinstance(maybe_data, dict):
                for k, v in maybe_data.items():
                    if isinstance(v, list):
                        items.extend(v)
            if isinstance(maybe_data, list):
                items.extend(maybe_data)
            try:
                mc = result_data.get('multas')
                if mc is not None:
                    total_multas = int(str(mc).strip())
            except Exception:
                total_multas = None
        elif isinstance(result_data, list):
            items = result_data
        detalles = []
        for it in items:
            if not isinstance(it, (dict,)):
                continue
            valor = _num(it.get('valor') or it.get('valor_total') or it.get('amount') or it.get('monto') or it.get('total'))
            if valor <= 0 and not any(x in it for x in ('valor','valor_total','amount','monto','total')):
                continue
            ref = it.get('numero') or it.get('id') or it.get('referencia') or it.get('code')
            fecha = it.get('fecha') or it.get('date') or None
            entidad = it.get('entidad') or it.get('authority') or it.get('organismo')
            estado = it.get('estado') or it.get('status')
            detalles.append({'referencia': ref, 'fecha': fecha, 'valor': valor, 'entidad': entidad, 'estado': estado, 'raw': it})
            if total_multas is None:
                try:
                    cm = it.get('cantidad_multas')
                    if cm is not None:
                        total_multas = int(str(cm).strip())
                except Exception:
                    pass
        cantidad = total_multas if (isinstance(total_multas, int) and total_multas >= 0) else len(detalles)
        valor_total = sum(d['valor'] for d in detalles)
        tiene_multas = 'SI' if (cantidad > 0 or valor_total > 0) else 'NO'
        now_dt = get_bogota_datetime()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO mpa_comparendos (placa, tecnico_id, tecnico_nombre, tipo_vehiculo, tiene_multas, cantidad, valor_total, fuente, fecha_ultima_consulta)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                tecnico_id=VALUES(tecnico_id),
                tecnico_nombre=VALUES(tecnico_nombre),
                tipo_vehiculo=VALUES(tipo_vehiculo),
                tiene_multas=VALUES(tiene_multas),
                cantidad=VALUES(cantidad),
                valor_total=VALUES(valor_total),
                fuente=VALUES(fuente),
                fecha_ultima_consulta=VALUES(fecha_ultima_consulta)
            """,
            (placa, tecnico_id, tecnico_nombre, tipo, tiene_multas, int(cantidad or 0), float(valor_total or 0.0), 'SIMIT', now_dt)
        )
        conn.commit()
        # Insertar detalles
        cur_det = conn.cursor()
        try:
            cur_det.execute("DELETE FROM mpa_comparendos_detalle WHERE placa = %s", (placa,))
            conn.commit()
        except Exception:
            pass
        for d in detalles:
            fecha_val = None
            try:
                fecha_val = datetime.strptime(str(d['fecha'])[:10], '%Y-%m-%d').date() if d['fecha'] else None
            except Exception:
                fecha_val = None
            raw_str = json.dumps(d['raw']) if isinstance(d.get('raw'), dict) else None
            cur_det.execute(
                """
                INSERT INTO mpa_comparendos_detalle (placa, referencia, fecha, valor, entidad, estado, raw_json)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (placa, d.get('referencia'), fecha_val, float(d.get('valor') or 0.0), d.get('entidad'), d.get('estado'), raw_str)
            )
        conn.commit()
        cur_det.close(); cur.close(); conn.close()
        return {'success': True, 'cantidad': cantidad, 'valor_total': valor_total, 'detalles': detalles}
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except Exception:
            pass
        return {'success': False, 'message': str(e)}

@app.route('/api/mpa/simit/consultar', methods=['POST'])
@login_required
def api_mpa_simit_consultar():
    if not current_user.has_role('administrativo'):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    data = request.get_json(silent=True) or {}
    placa = (data.get('placa') or request.form.get('placa') or '').strip().upper()
    document_type = data.get('document_type') or request.form.get('document_type')
    document_number = data.get('document_number') or request.form.get('document_number')
    if not placa or not document_type or not document_number:
        return jsonify({'success': False, 'message': 'placa, document_type y document_number requeridos'}), 400
    conn_chk = get_db_connection()
    if conn_chk is None:
        return jsonify({'success': False, 'message': 'BD no disponible'}), 500
    try:
        cur_chk = conn_chk.cursor(dictionary=True)
        cur_chk.execute(
            """
            SELECT pa.id_codigo_consumidor AS tecnico_id, ro.estado AS tecnico_estado
            FROM parque_automotor pa
            LEFT JOIN recurso_operativo ro ON pa.id_codigo_consumidor = ro.id_codigo_consumidor
            WHERE UPPER(TRIM(pa.placa)) = %s
            """,
            (placa,)
        )
        row_chk = cur_chk.fetchone() or {}
        cur_chk.close(); conn_chk.close()
        if row_chk.get('tecnico_id') is not None:
            est = (row_chk.get('tecnico_estado') or '').strip()
            if est != 'Activo':
                return jsonify({'success': False, 'message': 'Placa asociada a técnico inactivo'}), 400
    except Exception:
        try:
            conn_chk.close()
        except Exception:
            pass
        return jsonify({'success': False, 'message': 'Error validando placa'}), 500
    req = apitude_simit_create_request(document_type, document_number)
    if not req.get('success'):
        return jsonify(req), req.get('status_code') or 500
    rd = req.get('data') or {}
    request_id = rd.get('request_id')
    if not request_id:
        return jsonify({'success': False, 'message': 'request_id no disponible'}), 500
    import time as _t
    _t.sleep(3)
    res = api_mpa_simit_result.__wrapped__(request_id) if hasattr(api_mpa_simit_result, '__wrapped__') else api_mpa_simit_result(request_id)
    try:
        payload = res.get_json()
    except Exception:
        payload = None
    if not payload or not payload.get('success'):
        return jsonify({'success': False, 'message': 'Consulta SIMIT fallida', 'data': payload}), 500
    data_block = payload.get('data') or {}
    tecnico_id = None
    tecnico_nombre = None
    tipo = None
    upd = _update_comparendos_from_result(placa, tecnico_id, tecnico_nombre, tipo, data_block)
    return jsonify({'success': True, 'placa': placa, 'cantidad': upd.get('cantidad'), 'valor_total': upd.get('valor_total'), 'detalles': upd.get('detalles')})

@app.route('/api/mpa/simit/consultar-playwright', methods=['POST'])
@login_required
def api_mpa_simit_consultar_playwright():
    if not current_user.has_role('administrativo'):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    data = request.get_json(silent=True) or {}
    placa = (data.get('placa') or request.form.get('placa') or '').strip().upper()
    if not placa:
        return jsonify({'success': False, 'message': 'placa requerida'}), 400
    conn_chk = get_db_connection()
    if conn_chk is None:
        return jsonify({'success': False, 'message': 'BD no disponible'}), 500
    try:
        cur_chk = conn_chk.cursor(dictionary=True)
        cur_chk.execute(
            """
            SELECT mv.tipo_vehiculo AS tipo, CAST(mv.tecnico_asignado AS UNSIGNED) AS tecnico_id,
                   ro.nombre AS tecnico_nombre, ro.estado AS tecnico_estado
            FROM mpa_vehiculos mv
            LEFT JOIN recurso_operativo ro ON CAST(mv.tecnico_asignado AS UNSIGNED) = ro.id_codigo_consumidor
            WHERE UPPER(TRIM(mv.placa)) = %s AND mv.estado = 'Activo'
            """,
            (placa,)
        )
        row_chk = cur_chk.fetchone() or {}
        cur_chk.close(); conn_chk.close()
        if row_chk.get('tecnico_id') is not None:
            est = (row_chk.get('tecnico_estado') or '').strip()
            if est != 'Activo':
                return jsonify({'success': False, 'message': 'Placa asociada a técnico inactivo'}), 400
        res = simit_query_by_placa_playwright(placa)
        if not res.get('success'):
            err_msg = res.get('message') or res.get('error') or 'Error consultando SIMIT'
            conn2 = get_db_connection()
            if conn2 is not None:
                try:
                    cur2 = conn2.cursor(dictionary=True)
                    cur2.execute(
                        "SELECT placa, cantidad, valor_total, fuente, fecha_ultima_consulta FROM mpa_comparendos WHERE UPPER(TRIM(placa)) = %s ORDER BY fecha_ultima_consulta DESC LIMIT 1",
                        (placa,)
                    )
                    row2 = cur2.fetchone()
                    cur2.close(); conn2.close()
                    if row2:
                        try:
                            val_total = float(row2.get('valor_total') or 0.0)
                        except Exception:
                            val_total = 0.0
                        try:
                            cant_val = int(str(row2.get('cantidad') or 0).strip())
                        except Exception:
                            cant_val = 0
                        return jsonify({
                            'success': True,
                            'placa': placa,
                            'cantidad': cant_val,
                            'valor_total': val_total,
                            'detalles': [],
                            'from_cache': True,
                            'message': 'Usando último valor guardado. Error SIMIT: ' + err_msg
                        })
                except Exception:
                    try:
                        cur2.close(); conn2.close()
                    except Exception:
                        pass
            return jsonify(res), 500
        data_block = res.get('data') or {}
        upd = _update_comparendos_from_result(
            placa,
            row_chk.get('tecnico_id'),
            row_chk.get('tecnico_nombre'),
            row_chk.get('tipo')
            ,
            data_block
        )
        return jsonify({'success': True, 'placa': placa, 'cantidad': upd.get('cantidad'), 'valor_total': upd.get('valor_total'), 'detalles': upd.get('detalles')})

    except Exception as e:
        try:
            conn_chk.close()
        except Exception:
            pass
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/mpa/simit/export', methods=['GET'])
@login_required
def api_mpa_simit_export():
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        placa = (request.args.get('placa') or '').strip().upper()
        tecnico = (request.args.get('tecnico') or '').strip()
        fmt = (request.args.get('format') or 'csv').strip().lower()
        where = []
        params = []
        if placa:
            where.append("UPPER(TRIM(placa)) = %s")
            params.append(placa)
        if tecnico:
            try:
                tid = int(tecnico)
                where.append("tecnico_id = %s")
                params.append(tid)
            except Exception:
                where.append("tecnico_nombre LIKE %s")
                params.append('%'+tecnico+'%')
        query = (
            "SELECT placa, tecnico_id, tecnico_nombre, tipo_vehiculo, tiene_multas, cantidad, valor_total, fuente, fecha_ultima_consulta "
            "FROM mpa_comparendos"
        )
        if where:
            query += " WHERE " + " AND ".join(where)
        query += " ORDER BY fecha_ultima_consulta DESC, placa"
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        for r in rows:
            d = r.get('fecha_ultima_consulta')
            if d:
                try:
                    r['fecha_ultima_consulta'] = d.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    pass
        df = pd.DataFrame(rows or [])
        if fmt == 'xlsx' or fmt == 'excel':
            buf = io.BytesIO()
            try:
                with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='SIMIT')
                data = buf.getvalue()
            except Exception:
                buf = io.BytesIO()
                df.to_csv(buf, index=False)
                data = buf.getvalue()
                resp = make_response(data)
                resp.headers['Content-Type'] = 'text/csv; charset=utf-8'
                resp.headers['Content-Disposition'] = 'attachment; filename="simit_resultados.csv"'
                return resp
            resp = make_response(data)
            resp.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            resp.headers['Content-Disposition'] = 'attachment; filename="simit_resultados.xlsx"'
            return resp
        else:
            buf = io.StringIO()
            df.to_csv(buf, index=False)
            data = buf.getvalue()
            resp = make_response(data)
            resp.headers['Content-Type'] = 'text/csv; charset=utf-8'
            resp.headers['Content-Disposition'] = 'attachment; filename="simit_resultados.csv"'
            return resp
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

def ensure_sgis_permiso_trabajo_tables():
    try:
        conn = get_db_connection()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sgis_permiso_trabajo (
                id_sgis_permiso_trabajo INT AUTO_INCREMENT PRIMARY KEY,
                id_codigo_consumidor INT NOT NULL,
                sgis_permiso_trabajo_fecha_emision DATE NOT NULL,
                sgis_permiso_trabajo_fecha_finalizacion DATE NOT NULL,
                sgis_permiso_trabajo_trabajadores INT DEFAULT 1,
                sgis_permiso_trabajo_emitido_por VARCHAR(128) NULL,
                sgis_permiso_trabajo_proyecto VARCHAR(128) NULL,
                sgis_permiso_trabajo_ciudad VARCHAR(128) NULL,
                sgis_permiso_trabajo_responsable_trabajo VARCHAR(128) NULL,
                sgis_permiso_trabajo_cargo VARCHAR(128) NULL,
                nombre VARCHAR(128) NULL,
                cargo VARCHAR(128) NULL,
                cedula VARCHAR(32) NULL,
                recurso_operativo_cedula VARCHAR(32) NULL,
                sgis_permiso_trabajo_trabajo_ejecutar VARCHAR(255) NULL,
                sgis_permiso_trabajo_descripcion_tarea TEXT NULL,
                sgis_permiso_trabajo_herramienta TEXT NULL,
                sgis_permiso_trabajo_herramienta_electrica ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_herramienta_manual ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_equipos_alturas ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_otros_herramientas VARCHAR(255) NULL,
                sgis_permiso_trabajo_iluminacion ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_animales ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_izaje_alturas ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_obstaculos_evacuacion ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_vehiculos_area ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_trabajo_alturas ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_trabajo_piso_humedo ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_manejo_energia_peligrosa ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_trabajo_manual ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_caida_objetos ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_otros_area VARCHAR(255) NULL,
                sgis_permiso_trabajo_proyeccion_particulas ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_caidas_menor_2m ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_caidas_mayor_2m ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_acceso_mal_estado ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_levantamiento_carga_mecanica ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_condicion_clima ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_clima VARCHAR(255) NULL,
                sgis_permiso_trabajo_proxi_red_energizasa ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_proxi_red VARCHAR(255) NULL,
                sgis_permiso_trabajo_vibraciones ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_contacto_electrico ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_atrapamiento ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_cable_expuesto ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_corte_no_visible ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_atmosfera_explosiva ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_fuentes_ignicion ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_vapores ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_alta_temperatura ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_baja_temperatura ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_iluminacion_deficiente ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_quemaduras ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_almacenamientos_quimicos ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_extensiones_mal_estado ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_ruido ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_contacto_directo_indirecto ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_caida_objeto ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_espacio_reducido ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_levantamiento_manual_cargas ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_subestacion_inundada ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_excavaciones ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_otros VARCHAR(255) NULL,
                sgis_permiso_trabajo_calzado_dielectrico ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_guantes_nitrilo ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_guantes_vaqueta ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_gafas_proteccion ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_casco_dielectrico ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_tie_off ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_mosqueton ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_eslinga ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_arrestador ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_arnes ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_linea_vida ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_escalera_tijera ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_escalera_extensible ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_cinta_precaucion ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_conos ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_botiquin ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_notificacion_trabajo ENUM('SI','NO') NULL,
                sgis_permiso_trabajo_responsabilidades_permiso ENUM('SI','NO') NULL,
                sgis_permiso_trabajo_condicion_interrupcion ENUM('SI','NO') NULL,
                sgis_permiso_trabajo_cambios_seguridad_trabajo ENUM('SI','NO') NULL,
                sgis_permiso_trabajo_induccion_seguridad ENUM('SI','NO') NULL,
                sgis_permiso_trabajo_capacitacion_tema ENUM('SI','NO') NULL,
                sgis_permiso_trabajo_metodos_inspeccion ENUM('SI','NO') NULL,
                sgis_permiso_trabajo_responsables_area ENUM('SI','NO') NULL,
                sgis_permiso_trabajo_mecanismo_control_riesgo ENUM('SI','NO') NULL,
                sgis_permiso_trabajo_alarmas_puntos_reunion ENUM('SI','NO') NULL,
                sgis_permiso_trabajo_ubicacion_equipos_incendio ENUM('SI','NO') NULL,
                sgis_permiso_trabajo_riesgos_trabajo_area ENUM('SI','NO') NULL,
                sgis_permiso_trabajo_impacto_ambiental ENUM('SI','NO') NULL,
                sgis_permiso_trabajo_ats ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_inspecciones_relizadas ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_procedimientos_trabajo ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_arl_afp_eps ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_confinado_aplica ENUM('APLICA','NO_APLICA') NULL,
                sgis_permiso_trabajo_altura_aplica ENUM('APLICA','NO_APLICA') NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT NULL,
                INDEX idx_permiso_usuario (id_codigo_consumidor),
                INDEX idx_permiso_emision (sgis_permiso_trabajo_fecha_emision),
                INDEX idx_permiso_finalizacion (sgis_permiso_trabajo_fecha_finalizacion)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sgis_permiso_trabajo_historial_semanal_confinado (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_sgis_permiso_trabajo INT NOT NULL,
                id_codigo_consumidor INT NOT NULL,
                sgis_permiso_trabajo_historial_confinado_1 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_confinado_2 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_confinado_3 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_confinado_4 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_confinado_5 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_confinado_6 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_confinado_7 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_confinado_8 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_confinado_9 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_confinado_10 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_confinado_11 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_confinado_fecha DATE NULL,
                sgis_permiso_trabajo_historial_confinado_firma_tecnico LONGTEXT NULL,
                sgis_permiso_trabajo_historial_confinado_firma_supervisor LONGTEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_conf_permiso (id_sgis_permiso_trabajo),
                INDEX idx_conf_usuario (id_codigo_consumidor),
                INDEX idx_conf_fecha (sgis_permiso_trabajo_historial_confinado_fecha)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sgis_permiso_trabajo_historial_semanal_altura (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_sgis_permiso_trabajo INT NOT NULL,
                id_codigo_consumidor INT NOT NULL,
                sgis_permiso_trabajo_historial_altura_1 VARCHAR(64) NULL,
                sgis_permiso_trabajo_historial_altura_2 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_3 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_4 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_5 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_6 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_7 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_8 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_9 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_10 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_11 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_12 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_13 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_14 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_15 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_16 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_17 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_18 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_19 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_20 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_21 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_22 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_23 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_24 ENUM('C','NC','NA') NULL,
                sgis_permiso_trabajo_historial_altura_fecha DATE NULL,
                sgis_permiso_trabajo_historial_semanal_altura_firma_tecnico LONGTEXT NULL,
                sgis_permiso_trabajo_historial_semanal_altura_firma_supervisor LONGTEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_alt_permiso (id_sgis_permiso_trabajo),
                INDEX idx_alt_usuario (id_codigo_consumidor),
                INDEX idx_alt_fecha (sgis_permiso_trabajo_historial_altura_fecha)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        conn.commit()
        cur.close(); conn.close()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass

ensure_sgis_permiso_trabajo_tables()

def ensure_mpa_inspeccion_vehiculo_table():
    try:
        conn = get_db_connection()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mpa_inspeccion_vehiculo (
                id_mpa_inspeccion_vehiculo INT AUTO_INCREMENT PRIMARY KEY,
                id_codigo_consumidor INT NOT NULL,
                nombre VARCHAR(128) NULL,
                recurso_operativo_cedula VARCHAR(32) NULL,
                fecha_inspeccion DATETIME NULL,
                placa VARCHAR(16) NULL,
                marca VARCHAR(64) NULL,
                linea VARCHAR(64) NULL,
                modelo VARCHAR(64) NULL,
                color VARCHAR(32) NULL,
                cilindraje VARCHAR(64) NULL,
                estado_fisico_espejos_laterales ENUM('B','M') NULL,
                estado_fisico_pito ENUM('B','M') NULL,
                estado_fisico_freno_servicio ENUM('B','M') NULL,
                estado_fisico_manillares ENUM('B','M') NULL,
                estado_fisico_guayas ENUM('B','M') NULL,
                estado_fisico_tanque_combustible ENUM('B','M') NULL,
                estado_fisico_encendido ENUM('B','M') NULL,
                estado_fisico_pedales ENUM('B','M') NULL,
                estado_fisico_guardabarros ENUM('B','M') NULL,
                estado_fisico_sillin_tapiceria ENUM('B','M') NULL,
                estado_fisico_tablero ENUM('B','M') NULL,
                estado_fisico_mofle_silenciador ENUM('B','M') NULL,
                estado_fisico_kit_arrastre ENUM('B','M') NULL,
                estado_fisico_reposa_pies ENUM('B','M') NULL,
                estado_fisico_pata_lateral_central ENUM('B','M') NULL,
                estado_fisico_tijera_amortiguador ENUM('B','M') NULL,
                estado_fisico_bateria ENUM('B','M') NULL,
                luces_altas_bajas ENUM('B','M') NULL,
                luces_direccionales_delanteros ENUM('B','M') NULL,
                luces_direccionales_traseros ENUM('B','M') NULL,
                luces_luz_placa ENUM('B','M') NULL,
                luces_stop ENUM('B','M') NULL,
                prevension_casco ENUM('B','M') NULL,
                prevension_guantes ENUM('B','M') NULL,
                prevension_rodilleras ENUM('B','M') NULL,
                prevension_coderas ENUM('B','M') NULL,
                llantas_labrado_llantas ENUM('B','M') NULL,
                llantas_rines ENUM('B','M') NULL,
                llantas_presion_aire ENUM('B','M') NULL,
                otros_aceite ENUM('B','M') NULL,
                otros_suspension_direccion ENUM('B','M') NULL,
                otros_caja_cambios ENUM('B','M') NULL,
                otros_conexiones_electricas ENUM('B','M') NULL,
                vencimiento_licencia DATE NULL,
                vencimiento_soat DATE NULL,
                vencimiento_tecnicomecanica DATE NULL,
                firma_trabajador LONGTEXT NULL,
                firma_trabajador_fecha DATETIME NULL,
                firma_inspector LONGTEXT NULL,
                firma_inspector_fecha DATETIME NULL,
                observaciones TEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT NULL,
                INDEX idx_inspec_usuario (id_codigo_consumidor),
                INDEX idx_inspec_placa (placa),
                INDEX idx_inspec_fecha (fecha_inspeccion)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        conn.commit()
        cur.close(); conn.close()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass

ensure_mpa_inspeccion_vehiculo_table()

def ensure_mpa_inspeccion_kitcarretera_table():
    try:
        conn = get_db_connection()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute("SHOW TABLES LIKE 'mpa_inspeccion_kitcarretera'")
        exists = cur.fetchone() is not None
        if not exists:
            cur.execute("SHOW TABLES LIKE 'mpa_inspecion_kitcarretera'")
            exists_alt = cur.fetchone() is not None
            if exists_alt:
                cur.close(); conn.close()
                return
        if not exists:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS mpa_inspeccion_kitcarretera (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_codigo_consumidor INT NOT NULL,
                    nombre VARCHAR(128) NULL,
                    recurso_operativo_cedula VARCHAR(32) NULL,
                    fecha_inspeccion DATETIME NULL,
                    placa VARCHAR(16) NULL,
                    gato ENUM('SI','NO') NULL,
                    cruceta ENUM('SI','NO') NULL,
                    senales ENUM('SI','NO') NULL,
                    botiquin ENUM('SI','NO') NULL,
                    extintor_vigente ENUM('SI','NO') NULL,
                    extintor_vencimiento DATE NULL,
                    tacos ENUM('SI','NO') NULL,
                    caja_herramienta_basica ENUM('SI','NO') NULL,
                    llanta_repuesto ENUM('SI','NO') NULL,
                    foto_kit LONGTEXT NULL,
                    firma_trabajador LONGTEXT NULL,
                    firma_trabajador_fecha DATETIME NULL,
                    firma_inspector LONGTEXT NULL,
                    firma_inspector_fecha DATETIME NULL,
                    observaciones TEXT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_kit_tecnico (id_codigo_consumidor),
                    INDEX idx_kit_placa (placa),
                    INDEX idx_kit_fecha (fecha_inspeccion)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
        conn.commit()
        cur.close(); conn.close()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass

ensure_mpa_inspeccion_kitcarretera_table()

def _fecha_finalizacion_domingo(fecha_base):
    from datetime import timedelta
    d = fecha_base
    w = d.weekday()
    delta = 6 - w
    return d + timedelta(days=delta)

def import_riesgo_from_shapefile():
    try:
        import os
        import shapefile
        from datetime import datetime
        conn = get_db_connection()
        if not conn:
            return {'success': False, 'message': 'BD no disponible'}
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mpa_riesgo_accidentes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lat DOUBLE NOT NULL,
                lon DOUBLE NOT NULL,
                fecha DATE NULL,
                tipo_vehiculo VARCHAR(64) NULL,
                localidad VARCHAR(128) NULL,
                gravedad VARCHAR(64) NULL,
                fuente VARCHAR(64) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_lat (lat),
                INDEX idx_lon (lon),
                INDEX idx_fecha (fecha),
                INDEX idx_tipo (tipo_vehiculo),
                INDEX idx_localidad (localidad)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        shp_path = os.path.join(os.getcwd(), 'Siniestros', 'Hoja1_XYTableToPoint3.shp')
        if not os.path.isfile(shp_path):
            return {'success': False, 'message': 'No existe shapefile local en Siniestros/'}
        sf = shapefile.Reader(shp_path)
        fields = [f[0] for f in sf.fields[1:]]
        idx_lat = next((i for i,f in enumerate(fields) if f.lower()=='latitud'), None)
        idx_lon = next((i for i,f in enumerate(fields) if f.lower()=='longitud'), None)
        idx_fecha = next((i for i,f in enumerate(fields) if f.lower() in ('fechaacc','fecha','fecha_acc')), None)
        idx_veh = next((i for i,f in enumerate(fields) if f.lower() in ('vehiculo_v','clasenombr','claseveh','clasevehiculo')), None)
        idx_loc = next((i for i,f in enumerate(fields) if f.lower()=='localidad'), None)
        idx_grav = next((i for i,f in enumerate(fields) if 'gravedad' in f.lower()), None)
        data = []
        for rec in sf.iterRecords():
            try:
                lat = float(rec[idx_lat]) if idx_lat is not None else None
                lon = float(rec[idx_lon]) if idx_lon is not None else None
                if lat is None or lon is None:
                    continue
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    continue
                fecha_val = None
                if idx_fecha is not None:
                    d = rec[idx_fecha]
                    if hasattr(d, 'year'):
                        fecha_val = d
                    else:
                        try:
                            fecha_val = datetime.strptime(str(d)[:10], '%Y-%m-%d').date()
                        except Exception:
                            fecha_val = None
                tipo = str(rec[idx_veh]).strip() if idx_veh is not None else None
                loc = str(rec[idx_loc]).strip() if idx_loc is not None else None
                grav = str(rec[idx_grav]).strip() if idx_grav is not None else None
                data.append((lat, lon, fecha_val, tipo, loc, grav, 'shapefile'))
            except Exception:
                pass
        if not data:
            return {'success': False, 'message': 'No se obtuvieron registros válidos'}
        cur.execute("DELETE FROM mpa_riesgo_accidentes WHERE fuente='shapefile'")
        cur.executemany(
            "INSERT INTO mpa_riesgo_accidentes (lat, lon, fecha, tipo_vehiculo, localidad, gravedad, fuente) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            data
        )
        conn.commit()
        cur.close(); conn.close()
        return {'success': True, 'inserted': len(data)}
    except Exception as e:
        return {'success': False, 'message': str(e)}

# Función para obtener la fecha y hora actual en Bogotá
def get_bogota_datetime():
    return datetime.now(TIMEZONE)

# Endpoint de prueba simple para verificar Flask-Login
@app.route('/test_simple', methods=['GET'])
def test_simple():
    return jsonify({'message': 'Endpoint simple funcionando', 'authenticated': current_user.is_authenticated if current_user else False})

@app.route('/test_auth_simple', methods=['GET'])
@login_required
def test_auth_simple():
    return jsonify({'message': 'Autenticado correctamente', 'user': current_user.id})

# Ruta de inicio de sesión para compatibilidad con Flask-Login
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'GET':
            # Respuesta simple para GET; los clientes deben hacer POST para autenticar
            return jsonify({
                'status': 'ready',
                'message': 'Use POST con username y password para iniciar sesión'
            })

        # Método POST: autenticar usuario
        username = request.form.get('username', '')
        password_raw = request.form.get('password', '')

        if not username or not password_raw:
            return jsonify({'status': 'error', 'message': 'Usuario y contraseña requeridos'}), 400

        connection = get_db_connection()
        if connection is None:
            return jsonify({'status': 'error', 'message': 'Error de conexión a la base de datos'}), 500

        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_codigo_consumidor, id_roles, recurso_operativo_password, nombre, estado
            FROM recurso_operativo
            WHERE recurso_operativo_cedula = %s
            """,
            (username,)
        )
        user_data = cursor.fetchone()

        if not user_data:
            cursor.close(); connection.close()
            return jsonify({'status': 'error', 'message': 'Usuario o contraseña inválidos'}), 401

        if user_data.get('estado') != 'Activo':
            cursor.close(); connection.close()
            return jsonify({'status': 'error', 'message': 'Cuenta inactiva'}), 403

        stored_password = user_data.get('recurso_operativo_password')
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')

        # Validar formato del hash y verificar contraseña
        if not (stored_password.startswith(b'$2b$') or stored_password.startswith(b'$2a$')):
            cursor.close(); connection.close()
            return jsonify({'status': 'error', 'message': 'Formato de contraseña inválido'}), 500

        try:
            if not bcrypt.checkpw(password_raw.encode('utf-8'), stored_password):
                cursor.close(); connection.close()
                return jsonify({'status': 'error', 'message': 'Usuario o contraseña inválidos'}), 401
        except Exception as e:
            cursor.close(); connection.close()
            return jsonify({'status': 'error', 'message': f'Error verificando credenciales: {str(e)}'}), 500

        # Crear usuario Flask-Login y establecer sesión
        try:
            from flask_login import login_user
            user_role = ROLES.get(str(user_data['id_roles']))
            user = User(id=user_data['id_codigo_consumidor'], nombre=user_data['nombre'], role=user_role)
            login_user(user)

            # Variables de sesión para compatibilidad
            session['user_id'] = user_data['id_codigo_consumidor']
            session['id_codigo_consumidor'] = user_data['id_codigo_consumidor']
            session['user_cedula'] = username
            session['user_role'] = user_role
            session['user_name'] = user_data['nombre']
        finally:
            cursor.close(); connection.close()

        # Respuesta según cabeceras
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'status': 'success',
                'message': 'Inicio de sesión exitoso',
                'user_id': session.get('id_codigo_consumidor'),
                'user_role': session.get('user_role'),
                'user_name': session.get('user_name')
            })

        # Redirección simple post-login; ajustar si existe dashboard específico
        return redirect(url_for('verificar_registro_preoperacional'))

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error interno: {str(e)}'}), 500

@app.route('/logout')
@login_required
def logout():
    """Cerrar sesión del usuario"""
    logout_user()
    session.clear()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('login'))

@app.route('/check_submission', methods=['GET'])
def check_submission():
    user_id = request.args.get('user_id')
    submission_date = request.args.get('date')
    
    # Replace with your actual database query logic
    # Example: Check if a record exists in the database for the given user_id and date
    submission_exists = False  # Replace with actual database check

    # Example database check (pseudo-code):
    # submission_exists = db.session.query(Submission).filter_by(user_id=user_id, date=submission_date).first() is not None

    return jsonify({'submitted': submission_exists})

@app.route('/logistica/guardar_firma', methods=['POST'])
def guardar_firma():
    try:
        # Obtener datos del formulario
        firma = request.form.get('firma')
        id_asignador = request.form.get('id_asignador')
        id_asignacion = request.form.get('id_asignacion')  # Suponiendo que también envías el ID de la asignación

        # Validar que los datos necesarios estén presentes
        if not firma or not id_asignador or not id_asignacion:
            return jsonify({'status': 'error', 'message': 'Datos incompletos'}), 400

        # Buscar la asignación en la base de datos
        asignacion = Asignacion.query.get(id_asignacion)
        if not asignacion:
            return jsonify({'status': 'error', 'message': 'Asignación no encontrada'}), 404

        # Actualizar la asignación con la firma y el ID del asignador
        asignacion.asignacion_firma = firma
        asignacion.id_asignador = id_asignador
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Firma guardada exitosamente'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/logistica/ultima_asignacion', methods=['GET'])
def obtener_ultima_asignacion():
    try:
        # Suponiendo que tienes un modelo Asignacion con un campo de fecha
        ultima_asignacion = Asignacion.query.order_by(Asignacion.fecha.desc()).first()
        if ultima_asignacion:
            return jsonify({'status': 'success', 'id_asignacion': ultima_asignacion.id_asignacion})
        else:
            return jsonify({'status': 'error', 'message': 'No se encontró ninguna asignación'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/logistica/registrar_asignacion_con_firma', methods=['POST'])
def registrar_asignacion_con_firma():
    try:
        # Obtener datos del formulario
        id_codigo_consumidor = request.form.get('id_codigo_consumidor')
        fecha = request.form.get('fecha')
        cargo = request.form.get('cargo')
        firma = request.form.get('firma')
        id_asignador = request.form.get('id_asignador')

        # Validar datos
        if not all([id_codigo_consumidor, fecha, cargo, firma, id_asignador]):
            return jsonify({'status': 'error', 'message': 'Datos incompletos'}), 400

        # Crear nueva asignación
        nueva_asignacion = Asignacion(
            id_codigo_consumidor=id_codigo_consumidor,
            fecha=fecha,
            cargo=cargo,
            asignacion_firma=firma,
            id_asignador=id_asignador
        )
        db.session.add(nueva_asignacion)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Asignación y firma guardadas correctamente', 'id_asignacion': nueva_asignacion.id_asignacion})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

#@app.route('/indicadores/api')
#def indicadores_api():
    # Obtener la lista de supervisores (esto debe adaptarse a tu modelo de datos)
    #supervisores = ["Juan Pérez", "María García", "Carlos Rodríguez"]
    
    #return render_template('modulos/administrativo/api_indicadores_cumplimiento.html', 
     #                     supervisores=supervisores)





# Ruta para renderizar el template administrativo de asistencia
@app.route('/administrativo/asistencia', methods=['GET'])
@login_required
def administrativo_asistencia():
    """Renderizar el template administrativo de asistencia con datos necesarios"""
    try:
        connection = get_db_connection()
        if connection is None:
            flash('Error de conexión a la base de datos', 'danger')
            return redirect(url_for('dashboard'))
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener información del usuario actual
        user_id = session.get('user_id')
        user_role = session.get('user_role')
        user_name = session.get('user_name')
        
        # Filtrar supervisores según el rol del usuario
        if user_role == 'administrativo':
            # Si es administrador, mostrar todos los supervisores
            cursor.execute("""
                SELECT DISTINCT super
                FROM recurso_operativo
                WHERE super IS NOT NULL AND super != '' AND estado = 'Activo'
                ORDER BY super
            """)
            supervisores_result = cursor.fetchall()
            supervisores = [row['super'] for row in supervisores_result]
            base = "CORTES CUERVO SANDRA CECILIA"
            if base not in supervisores:
                supervisores = [base] + supervisores
        else:
            # Si es supervisor, solo mostrar su propio nombre
            # Obtener el nombre del supervisor desde la base de datos
            cursor.execute("""
                SELECT super
                FROM recurso_operativo
                WHERE id_codigo_consumidor = %s AND estado = 'Activo'
            """, (user_id,))
            supervisor_result = cursor.fetchone()
            
            if supervisor_result and supervisor_result['super']:
                supervisores = [supervisor_result['super']]
            else:
                # Si no tiene supervisor asignado, usar su nombre
                supervisores = [user_name] if user_name else []
        
        # Si no hay supervisores disponibles, redirigir con mensaje
        if not supervisores:
            flash('No tiene permisos para acceder a este módulo o no tiene supervisores asignados.', 'warning')
            return redirect(url_for('dashboard'))
        
        # Obtener lista de tipificaciones para carpeta_dia (solo zona RRHH para administrativo)
        cursor.execute("""
            SELECT codigo_tipificacion, nombre_tipificacion
            FROM tipificacion_asistencia
            WHERE estado = '1' AND zona = 'RRHH'
            ORDER BY codigo_tipificacion
        """)
        carpetas_dia = cursor.fetchall()
        
        return render_template('modulos/administrativo/asistencia.html',
                           supervisores=supervisores,
                           carpetas_dia=carpetas_dia)
                           
    except mysql.connector.Error as e:
        flash(f'Error al cargar datos: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# Submódulo: Novedades asistencia (vista calendario por mes)
@app.route('/administrativo/novedades', methods=['GET'])
@login_required
def administrativo_novedades():
    """Renderiza el submódulo de Novedades asistencia"""
    try:
        # Datos iniciales: mes actual
        now = get_bogota_datetime()
        current_year = now.year
        current_month = now.month
        return render_template(
            'modulos/administrativo/novedades_asistencia.html',
            current_year=current_year,
            current_month=f"{current_month:02d}"
        )
    except Exception as e:
        flash(f'Error al cargar Novedades: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

# API: matriz mensual de novedades de asistencia
@app.route('/api/asistencia/novedades', methods=['GET'])
@login_required
def api_asistencia_novedades():
    """Devuelve matriz de asistencia por usuario y día del mes.
    Verde: tiene registro de asistencia.
    Rojo: registro con carpeta_dia=0 o carpeta=0 (ausencia injustificada).
    """
    try:
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)

        now = get_bogota_datetime()
        if not year:
            year = now.year
        if not month:
            month = now.month

        # Determinar cantidad de días del mes
        import calendar
        days_in_month = calendar.monthrange(year, month)[1]

        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'})

        cursor = connection.cursor(dictionary=True)

        # Usuarios con asistencia registrada en el mes
        cursor.execute(
            """
            SELECT DISTINCT id_codigo_consumidor AS usuario_id, tecnico AS nombre
            FROM asistencia
            WHERE YEAR(fecha_asistencia) = %s AND MONTH(fecha_asistencia) = %s
            ORDER BY nombre
            """,
            (year, month)
        )
        usuarios = cursor.fetchall() or []

        # Registros por día para el mes
        cursor.execute(
            """
            SELECT id_codigo_consumidor AS usuario_id,
                   DATE(fecha_asistencia) AS fecha,
                   MAX(CASE WHEN carpeta_dia = '0' OR carpeta = '0' THEN 1 ELSE 0 END) AS es_ausencia,
                   COUNT(*) AS registros
            FROM asistencia
            WHERE YEAR(fecha_asistencia) = %s AND MONTH(fecha_asistencia) = %s
            GROUP BY id_codigo_consumidor, DATE(fecha_asistencia)
            """,
            (year, month)
        )
        registros = cursor.fetchall() or []

        # Indexar por usuario y día
        por_usuario = {}
        for r in registros:
            uid = r['usuario_id']
            dia = int(str(r['fecha']).split('-')[-1])
            estado = 'absent' if r['es_ausencia'] == 1 else ('present' if (r['registros'] or 0) > 0 else 'none')
            por_usuario.setdefault(uid, {})[dia] = estado

        # Construir matriz
        matriz = []
        for u in usuarios:
            fila = []
            for d in range(1, days_in_month + 1):
                estado = por_usuario.get(u['usuario_id'], {}).get(d, 'none')
                fila.append(estado)
            matriz.append({
                'id': u['usuario_id'],
                'nombre': u['nombre'],
                'dias': fila
            })

        return jsonify({
            'success': True,
            'year': year,
            'month': month,
            'days_in_month': days_in_month,
            'usuarios': matriz
        })
    except mysql.connector.Error as e:
        return jsonify({'success': False, 'message': f'Error de base de datos: {str(e)}'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()
# Endpoints para el sistema administrativo de asistencia
@app.route('/api/supervisores', methods=['GET'])
@login_required
def obtener_supervisores():
    """Obtener lista única de supervisores desde la tabla recurso_operativo con filtrado por rol"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'})
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener información del usuario actual
        user_id = session.get('user_id')
        user_role = session.get('user_role')
        user_name = session.get('user_name')
        
        # Filtrar supervisores según el rol del usuario
        if user_role == 'administrativo':
            # Si es administrador, mostrar todos los supervisores
            cursor.execute("""
                SELECT DISTINCT super
                FROM recurso_operativo
                WHERE super IS NOT NULL AND super != '' AND estado = 'Activo'
                ORDER BY super
            """)
            supervisores_result = cursor.fetchall()
            supervisores = [row['super'] for row in supervisores_result]
        else:
            # Si es supervisor, solo mostrar su propio nombre
            cursor.execute("""
                SELECT super
                FROM recurso_operativo
                WHERE id_codigo_consumidor = %s AND estado = 'Activo'
            """, (user_id,))
            supervisor_result = cursor.fetchone()
            
            if supervisor_result and supervisor_result['super']:
                supervisores = [supervisor_result['super']]
            else:
                # Si no tiene supervisor asignado, usar su nombre
                supervisores = [user_name] if user_name else []
        
        return jsonify({
            'success': True,
            'supervisores': supervisores
        })
        
    except mysql.connector.Error as e:
        return jsonify({'success': False, 'message': f'Error de base de datos: {str(e)}'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/tecnicos_por_supervisor', methods=['GET'])
def obtener_tecnicos_por_supervisor():
    """Obtener técnicos asociados a un supervisor específico desde recurso_operativo"""
    try:
        supervisor = request.args.get('supervisor')
        if not supervisor:
            return jsonify({'success': False, 'message': 'Supervisor no especificado'})
            
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'})
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener técnicos del supervisor especificado
        if supervisor.strip().upper() == "CORTES CUERVO SANDRA CECILIA":
            cursor.execute("""
                SELECT DISTINCT id_codigo_consumidor, recurso_operativo_cedula, nombre, carpeta, super
                FROM recurso_operativo
                WHERE estado = 'Activo' AND (
                    UPPER(TRIM(super)) = %s OR UPPER(TRIM(carpeta)) IN ('SUPERVISOR','CONDUCTOR')
                )
                ORDER BY nombre
            """, (supervisor,))
        else:
            cursor.execute("""
                SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, carpeta, super
                FROM recurso_operativo
                WHERE super = %s AND estado = 'Activo'
                ORDER BY nombre
            """, (supervisor,))
        
        tecnicos = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'tecnicos': tecnicos,
            'supervisor': supervisor
        })
        
    except mysql.connector.Error as e:
        return jsonify({'success': False, 'message': f'Error de base de datos: {str(e)}'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# === API Operativo: Vencimientos de técnicos a cargo ===
@app.route('/api/operativo/vencimientos_tecnicos', methods=['GET'])
@login_required
def api_vencimientos_tecnicos_operativo():
    """Devuelve documentos vencidos de los técnicos a cargo de un supervisor (SOAT, Técnico Mecánica, Licencia)."""
    # Permitir a roles operativo y administrativo
    if not (current_user.has_role('operativo') or current_user.has_role('administrativo')):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    supervisor = request.args.get('supervisor')
    dias_param = request.args.get('dias', default='30')
    try:
        dias_ventana = int(dias_param)
    except Exception:
        dias_ventana = 30

    if not supervisor:
        return jsonify({'success': False, 'message': 'Supervisor no especificado'}), 400

    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        cursor = connection.cursor(dictionary=True)

        vencimientos = []

        # SOAT por técnicos del supervisor
        # Mejora: considerar vínculos por técnico_asignado o por placa del vehículo asignado
        query_soat = """
            SELECT DISTINCT
                s.id_mpa_soat AS id,
                s.fecha_vencimiento,
                ro.id_codigo_consumidor AS tecnico_id,
                ro.nombre AS tecnico_nombre,
                'SOAT' AS tipo
            FROM recurso_operativo ro
            LEFT JOIN mpa_vehiculos mv ON mv.tecnico_asignado = ro.id_codigo_consumidor
            LEFT JOIN mpa_soat s ON (s.tecnico_asignado = ro.id_codigo_consumidor OR (mv.placa IS NOT NULL AND s.placa = mv.placa))
            WHERE ro.super = %s AND ro.estado = 'Activo'
              AND s.fecha_vencimiento IS NOT NULL
              AND s.fecha_vencimiento NOT LIKE '0000-00-00%'
              AND s.fecha_vencimiento > '1900-01-01'
        """
        cursor.execute(query_soat, (supervisor,))
        soats = cursor.fetchall()

        # Técnico Mecánica por técnicos del supervisor
        query_tm = """
            SELECT DISTINCT
                tm.id_mpa_tecnico_mecanica AS id,
                tm.fecha_vencimiento,
                ro.id_codigo_consumidor AS tecnico_id,
                ro.nombre AS tecnico_nombre,
                'Técnico Mecánica' AS tipo
            FROM recurso_operativo ro
            LEFT JOIN mpa_vehiculos mv ON mv.tecnico_asignado = ro.id_codigo_consumidor
            LEFT JOIN mpa_tecnico_mecanica tm ON (tm.tecnico_asignado = ro.id_codigo_consumidor OR (mv.placa IS NOT NULL AND tm.placa = mv.placa))
            WHERE ro.super = %s AND ro.estado = 'Activo'
              AND tm.fecha_vencimiento IS NOT NULL
              AND tm.fecha_vencimiento NOT LIKE '0000-00-00%'
              AND tm.fecha_vencimiento > '1900-01-01'
        """
        cursor.execute(query_tm, (supervisor,))
        tms = cursor.fetchall()

        # Licencias de conducir por técnicos del supervisor
        query_lc = """
            SELECT 
                lc.id_mpa_licencia_conducir AS id,
                lc.fecha_vencimiento,
                ro.id_codigo_consumidor AS tecnico_id,
                ro.nombre AS tecnico_nombre,
                'Licencia de Conducir' AS tipo
            FROM mpa_licencia_conducir lc
            LEFT JOIN recurso_operativo ro ON lc.tecnico = ro.id_codigo_consumidor
            WHERE ro.super = %s AND ro.estado = 'Activo'
              AND lc.fecha_vencimiento IS NOT NULL
              AND lc.fecha_vencimiento NOT LIKE '0000-00-00%'
              AND lc.fecha_vencimiento > '1900-01-01'
        """
        cursor.execute(query_lc, (supervisor,))
        lcs = cursor.fetchall()

        # Unificar y calcular estado
        from datetime import datetime, date
        import pytz
        import re
        colombia_tz = pytz.timezone('America/Bogota')
        hoy = datetime.now(colombia_tz).date()

        def validar_fecha(fecha_str):
            if not fecha_str or fecha_str == '0000-00-00':
                return False, None
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(fecha_str)):
                return False, None
            try:
                if isinstance(fecha_str, date):
                    return True, fecha_str
                y, m, d = map(int, str(fecha_str).split('-'))
                return True, date(y, m, d)
            except Exception:
                return False, None

        def procesar(items):
            for v in items:
                ok, fv = validar_fecha(v['fecha_vencimiento'])
                if not ok:
                    continue
                dias = (fv - hoy).days
                # Consistencia de bloqueo: Vencido solo cuando días restantes < 0
                estado = 'Vencido' if dias < 0 else ('Próximo a vencer' if dias <= dias_ventana else 'Vigente')
                vencimientos.append({
                    'id': v['id'],
                    'tipo': v['tipo'],
                    'tecnico_id': v['tecnico_id'],
                    'tecnico_nombre': v['tecnico_nombre'],
                    'fecha_vencimiento': fv.strftime('%Y-%m-%d'),
                    'dias_restantes': dias,
                    'estado': estado
                })

        procesar(soats)
        procesar(tms)
        procesar(lcs)

        # Clasificaciones: vencidos para bloqueo, próximos (<= ventana) informativos (no bloqueo)
        vencidos = [v for v in vencimientos if v['estado'] == 'Vencido']
        proximos = [v for v in vencimientos if v['estado'] == 'Próximo a vencer']

        return jsonify({
            'success': True,
            # Mantener compatibilidad: 'data' sigue siendo la lista de vencidos usada por el frontend actual para bloqueo
            'data': vencidos,
            'proximos': proximos,
            'supervisor': supervisor,
            'total_vencidos': len(vencidos),
            'total_proximos': len(proximos),
        })

    except mysql.connector.Error as e:
        return jsonify({'success': False, 'message': f'Error de base de datos: {str(e)}'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/asistencia/guardar', methods=['POST'])
def guardar_asistencia_administrativa():
    """Guardar asistencias desde el sistema administrativo"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if not data.get('asistencias'):
            return jsonify({"success": False, "message": "Datos de asistencias faltantes"}), 400
            
        # Insertar en base de datos
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'})
            
        cursor = connection.cursor()
        cursor_dict = connection.cursor(dictionary=True)
        
        # Insertar cada asistencia
        asistencias_guardadas = 0
        for asistencia in data['asistencias']:
            try:
                eventos_val = None
                valor_val = None
                codigo = asistencia.get('carpeta_dia')
                if codigo:
                    cursor_dict.execute("SELECT nombre_tipificacion FROM tipificacion_asistencia WHERE codigo_tipificacion = %s LIMIT 1", (codigo,))
                    tip = cursor_dict.fetchone()
                    if tip and tip.get('nombre_tipificacion'):
                        cursor_dict.execute(
                            "SELECT presupuesto_eventos, presupuesto_diario FROM presupuesto_carpeta WHERE presupuesto_carpeta = %s LIMIT 1",
                            (tip['nombre_tipificacion'],)
                        )
                        pres = cursor_dict.fetchone()
                        if pres:
                            eventos_val = pres.get('presupuesto_eventos')
                            valor_val = pres.get('presupuesto_diario')
                cursor.execute("""
                    INSERT INTO asistencia (
                        cedula, tecnico, carpeta_dia, carpeta, super,
                        id_codigo_consumidor, fecha_asistencia, eventos, valor
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s)
                """, (
                    asistencia['cedula'],
                    asistencia['tecnico'],
                    asistencia['carpeta_dia'],
                    asistencia.get('carpeta', ''),
                    asistencia['super'],
                    asistencia['id_codigo_consumidor'],
                    eventos_val,
                    valor_val
                ))
                asistencias_guardadas += 1
            except mysql.connector.Error as e:
                logging.error(f"Error insertando asistencia para {asistencia.get('tecnico', 'N/A')}: {str(e)}")
                continue
        
        connection.commit()
        
        if asistencias_guardadas > 0:
            return jsonify({
                'success': True, 
                'message': f'Se guardaron {asistencias_guardadas} asistencias correctamente'
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'No se pudo guardar ninguna asistencia'
            })
        
    except Exception as e:
        logging.error(f"Error guardando asistencias administrativas: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'cursor_dict' in locals() and cursor_dict:
            cursor_dict.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/asistencia/consultar', methods=['GET'])
@login_required
def consultar_asistencia():
    supervisor = request.args.get('supervisor')
    fecha = request.args.get('fecha')
    if not supervisor or not fecha:
        return jsonify({'success': False, 'message': 'Supervisor y fecha requeridos'}), 400
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_asistencia, cedula, tecnico, carpeta_dia, carpeta, super,
                   fecha_asistencia, id_codigo_consumidor, eventos, valor,
                   hora_inicio, estado, novedad
            FROM asistencia
            WHERE super = %s AND DATE(fecha_asistencia) = %s
            ORDER BY tecnico, cedula
            """,
            (supervisor, fecha)
        )
        registros = cursor.fetchall() or []
        return jsonify({'success': True, 'registros': registros})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/asistencia/tipificacion', methods=['GET'])
@login_required
def api_asistencia_tipificacion():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT codigo_tipificacion AS codigo, nombre_tipificacion AS descripcion
            FROM tipificacion_asistencia
            WHERE estado = '1' AND zona = 'RRHH'
            ORDER BY codigo_tipificacion
            """
        )
        tipificaciones = cursor.fetchall() or []
        return jsonify({'success': True, 'tipificaciones': tipificaciones})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/asistencia/supervisores', methods=['GET'])
@login_required
def api_asistencia_supervisores():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        user_id = session.get('user_id')
        user_role = session.get('user_role')
        user_name = session.get('user_name')
        if user_role == 'administrativo':
            cursor.execute(
                """
                SELECT DISTINCT super
                FROM recurso_operativo
                WHERE super IS NOT NULL AND super <> '' AND estado = 'Activo'
                ORDER BY super
                """
            )
            rows = cursor.fetchall() or []
            supervisores = [r['super'] for r in rows]
            base = "CORTES CUERVO SANDRA CECILIA"
            if base not in supervisores:
                supervisores = [base] + supervisores
        else:
            cursor.execute(
                """
                SELECT super
                FROM recurso_operativo
                WHERE id_codigo_consumidor = %s AND estado = 'Activo'
                """,
                (user_id,)
            )
            row = cursor.fetchone()
            if row and row.get('super'):
                supervisores = [row['super']]
            else:
                supervisores = [user_name] if user_name else []
        return jsonify({'success': True, 'supervisores': supervisores})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/asistencia/actualizar', methods=['PUT'])
@login_required
def api_asistencia_actualizar():
    data = request.get_json(silent=True) or {}
    ida = data.get('id_asistencia')
    if not ida:
        return jsonify({'success': False, 'message': 'id_asistencia requerido'}), 400
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        cursor2 = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT fecha_asistencia FROM asistencia WHERE id_asistencia = %s",
            (ida,)
        )
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Registro no encontrado'}), 404
        fa = row['fecha_asistencia']
        hoy = get_bogota_datetime().date()
        try:
            f_reg = fa.date() if hasattr(fa, 'date') else datetime.strptime(str(fa)[:10], '%Y-%m-%d').date()
        except Exception:
            f_reg = hoy
        diff = (hoy - f_reg).days
        if diff < 0 or diff > 4:
            return jsonify({'success': False, 'message': 'Registro no editable'}), 400
        set_parts = []
        params = []
        for k in ('carpeta_dia', 'carpeta', 'super'):
            v = data.get(k)
            if v is not None:
                set_parts.append(f"{k} = %s")
                params.append(v)
        if data.get('carpeta_dia') is not None:
            codigo = data.get('carpeta_dia')
            eventos_val = None
            valor_val = None
            if codigo:
                cursor2.execute("SELECT nombre_tipificacion FROM tipificacion_asistencia WHERE codigo_tipificacion = %s LIMIT 1", (codigo,))
                tip = cursor2.fetchone()
                if tip and tip.get('nombre_tipificacion'):
                    cursor2.execute(
                        "SELECT presupuesto_eventos, presupuesto_diario FROM presupuesto_carpeta WHERE presupuesto_carpeta = %s LIMIT 1",
                        (tip['nombre_tipificacion'],)
                    )
                    pres = cursor2.fetchone()
                    if pres:
                        eventos_val = pres.get('presupuesto_eventos')
                        valor_val = pres.get('presupuesto_diario')
            set_parts.append("eventos = %s")
            params.append(eventos_val)
            set_parts.append("valor = %s")
            params.append(valor_val)
        elif data.get('carpeta') is not None:
            nombre = data.get('carpeta')
            eventos_val = None
            valor_val = None
            if nombre:
                cursor2.execute(
                    "SELECT presupuesto_eventos, presupuesto_diario FROM presupuesto_carpeta WHERE presupuesto_carpeta = %s LIMIT 1",
                    (nombre,)
                )
                pres = cursor2.fetchone()
                if pres:
                    eventos_val = pres.get('presupuesto_eventos')
                    valor_val = pres.get('presupuesto_diario')
                else:
                    cursor2.execute(
                        "SELECT codigo_tipificacion FROM tipificacion_asistencia WHERE nombre_tipificacion = %s LIMIT 1",
                        (nombre,)
                    )
                    tip2 = cursor2.fetchone()
                    if tip2 and tip2.get('codigo_tipificacion'):
                        cursor2.execute(
                            "SELECT presupuesto_eventos, presupuesto_diario FROM presupuesto_carpeta WHERE presupuesto_carpeta = %s LIMIT 1",
                            (nombre,)
                        )
                        pres2 = cursor2.fetchone()
                        if pres2:
                            eventos_val = pres2.get('presupuesto_eventos')
                            valor_val = pres2.get('presupuesto_diario')
            set_parts.append("eventos = %s")
            params.append(eventos_val)
            set_parts.append("valor = %s")
            params.append(valor_val)
        if not set_parts:
            return jsonify({'success': False, 'message': 'Sin cambios'}), 400
        params.append(ida)
        cursor.execute(
            f"UPDATE asistencia SET {', '.join(set_parts)} WHERE id_asistencia = %s",
            tuple(params)
        )
        connection.commit()
        return jsonify({'success': True})
    except Exception as e:
        try:
            if 'connection' in locals() and connection:
                connection.rollback()
        except Exception:
            pass
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'cursor2' in locals() and cursor2:
            cursor2.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/asistencia/eliminar', methods=['DELETE'])
@login_required
def api_asistencia_eliminar():
    data = request.get_json(silent=True) or {}
    ida = data.get('id_asistencia')
    if not ida:
        return jsonify({'success': False, 'message': 'id_asistencia requerido'}), 400
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT fecha_asistencia FROM asistencia WHERE id_asistencia = %s",
            (ida,)
        )
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Registro no encontrado'}), 404
        fa = row['fecha_asistencia']
        hoy = get_bogota_datetime().date()
        try:
            f_reg = fa.date() if hasattr(fa, 'date') else datetime.strptime(str(fa)[:10], '%Y-%m-%d').date()
        except Exception:
            f_reg = hoy
        diff = (hoy - f_reg).days
        if diff < 0 or diff > 4:
            return jsonify({'success': False, 'message': 'Registro no editable'}), 400
        cursor.execute("DELETE FROM asistencia WHERE id_asistencia = %s", (ida,))
        connection.commit()
        return jsonify({'success': True})
    except Exception as e:
        try:
            if 'connection' in locals() and connection:
                connection.rollback()
        except Exception:
            pass
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/asistencia/exportar_excel', methods=['GET'])
@login_required
def exportar_asistencia_excel():
    supervisor = request.args.get('supervisor')
    fi = request.args.get('fecha_inicio')
    ff = request.args.get('fecha_fin')
    if not supervisor or not fi or not ff:
        return jsonify({'success': False, 'message': 'Supervisor, fecha_inicio y fecha_fin requeridos'}), 400
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        where = ["DATE(fecha_asistencia) BETWEEN %s AND %s"]
        params = [fi, ff]
        if supervisor and supervisor != 'TODOS':
            where.append("super = %s")
            params.append(supervisor)
        query = (
            "SELECT fecha_asistencia, super, tecnico, cedula, carpeta_dia, carpeta, id_codigo_consumidor, eventos, valor, hora_inicio, estado, novedad "
            "FROM asistencia WHERE " + " AND ".join(where) + " ORDER BY fecha_asistencia, super, tecnico"
        )
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall() or []
        try:
            import pandas as pd
            df = pd.DataFrame(rows)
        except Exception:
            df = None
        from io import BytesIO
        buf = BytesIO()
        if df is not None and not df.empty:
            try:
                with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Asistencia')
            except Exception:
                buf = BytesIO(json.dumps(rows).encode('utf-8'))
        else:
            buf = BytesIO(json.dumps(rows).encode('utf-8'))
        buf.seek(0)
        resp = make_response(buf.read())
        resp.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        filename = f"asistencia_{supervisor}_{fi}_{ff}.xlsx"
        resp.headers['Content-Disposition'] = f"attachment; filename={filename}"
        return resp
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

def _build_periods(fi, ff, agrupacion):
    from datetime import datetime as _dt, timedelta as _td
    start = _dt.strptime(fi, '%Y-%m-%d').date()
    end = _dt.strptime(ff, '%Y-%m-%d').date()
    labels = []
    keys = []
    if agrupacion == 'mes':
        cur = start.replace(day=1)
        while cur <= end:
            labels.append(cur.strftime('%Y-%m'))
            keys.append((cur.year, cur.month))
            nm = cur.replace(day=28) + _td(days=4)
            cur = nm - _td(days=nm.day - 1)
            cur = (cur.replace(day=28) + _td(days=4)) - _td(days=(cur.replace(day=28) + _td(days=4)).day - 1)
    else:
        cur = start
        while cur <= end:
            labels.append(cur.strftime('%Y-%m-%d'))
            keys.append((cur.year, cur.month, cur.day))
            cur = cur + _td(days=1)
    return labels, keys

@app.route('/api/asistencia/graficas/operacion-recurso', methods=['GET'])
@login_required
def api_asistencia_grafica_operacion_recurso():
    fi = request.args.get('fecha_inicio')
    ff = request.args.get('fecha_fin')
    agrupacion = (request.args.get('agrupacion') or 'dia').strip().lower()
    supervisor = request.args.get('supervisor')
    if not fi or not ff:
        return jsonify({'success': False, 'message': 'fechas requeridas'}), 400
    try:
        labels, keys = _build_periods(fi, ff, agrupacion)
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        where = ["DATE(a.fecha_asistencia) BETWEEN %s AND %s"]
        params = [fi, ff]
        if supervisor:
            where.append("a.super = %s")
            params.append(supervisor)
        cursor.execute(
            """
            SELECT a.fecha_asistencia, t.grupo
            FROM asistencia a
            INNER JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
            WHERE """ + " AND ".join(where)
        , tuple(params))
        rows = cursor.fetchall() or []
        from collections import defaultdict
        data_map = defaultdict(lambda: defaultdict(int))
        for r in rows:
            dt = r.get('fecha_asistencia')
            try:
                y = dt.year; m = dt.month; d = dt.day
            except Exception:
                try:
                    y, m, d = map(int, str(dt)[:10].split('-'))
                except Exception:
                    continue
            grp = (r.get('grupo') or '').strip().upper()
            if agrupacion == 'mes':
                data_map[grp][(y, m)] += 1
            else:
                data_map[grp][(y, m, d)] += 1
        grupos = ['ARREGLOS', 'INSTALACIONES', 'POSTVENTA']
        datasets = []
        for g in grupos:
            serie = []
            for k in keys:
                serie.append(int(data_map[g].get(k, 0)))
            datasets.append({'label': g, 'data': serie})
        return jsonify({'success': True, 'labels': labels, 'datos': datasets, 'agrupacion': agrupacion})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/asistencia/graficas/carpeta-dia', methods=['GET'])
@login_required
def api_asistencia_grafica_carpeta_dia():
    fi = request.args.get('fecha_inicio')
    ff = request.args.get('fecha_fin')
    agrupacion = (request.args.get('agrupacion') or 'dia').strip().lower()
    supervisor = request.args.get('supervisor')
    if not fi or not ff:
        return jsonify({'success': False, 'message': 'fechas requeridas'}), 400
    try:
        labels, keys = _build_periods(fi, ff, agrupacion)
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        where = ["DATE(a.fecha_asistencia) BETWEEN %s AND %s"]
        params = [fi, ff]
        if supervisor:
            where.append("a.super = %s")
            params.append(supervisor)
        cursor.execute(
            """
            SELECT a.fecha_asistencia, t.grupo
            FROM asistencia a
            INNER JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
            WHERE """ + " AND ".join(where)
        , tuple(params))
        rows = cursor.fetchall() or []
        from collections import defaultdict
        data_map = defaultdict(lambda: defaultdict(int))
        for r in rows:
            dt = r.get('fecha_asistencia')
            try:
                y = dt.year; m = dt.month; d = dt.day
            except Exception:
                try:
                    y, m, d = map(int, str(dt)[:10].split('-'))
                except Exception:
                    continue
            grp = (r.get('grupo') or '').strip().upper()
            if agrupacion == 'mes':
                data_map[grp][(y, m)] += 1
            else:
                data_map[grp][(y, m, d)] += 1
        grupos = ['ARREGLOS', 'INSTALACIONES', 'POSTVENTA']
        datasets = []
        for g in grupos:
            serie = []
            for k in keys:
                serie.append(int(data_map[g].get(k, 0)))
            datasets.append({'label': g, 'data': serie})
        return jsonify({'success': True, 'labels': labels, 'datos': datasets, 'agrupacion': agrupacion})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/asistencia/resumen_categorias', methods=['GET'])
@login_required
def api_asistencia_resumen_categorias():
    fecha = request.args.get('fecha')
    supervisor = request.args.get('supervisor')
    if not fecha:
        return jsonify({'success': False, 'message': 'fecha requerida'}), 400
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        params = [fecha]
        where_sup = ''
        if supervisor and supervisor.strip() not in ('', 'TODOS'):
            where_sup = ' AND a.super = %s'
            params.append(supervisor)
        cursor.execute(
            """
            SELECT t.nombre_tipificacion AS carpeta_dia, COUNT(DISTINCT a.cedula) AS total
            FROM asistencia a
            INNER JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
            WHERE DATE(a.fecha_asistencia) = %s
              AND t.grupo IN ('ARREGLOS','INSTALACIONES','POSTVENTA')
            """ + where_sup + """
            GROUP BY t.nombre_tipificacion
            ORDER BY t.nombre_tipificacion
            """,
            tuple(params)
        )
        oper_items = cursor.fetchall() or []
        cursor.execute(
            """
            SELECT a.carpeta_dia AS carpeta_dia, COUNT(DISTINCT a.cedula) AS total
            FROM asistencia a
            WHERE DATE(a.fecha_asistencia) = %s
              AND a.carpeta_dia IN ('0','0-A','A-O')
            """ + where_sup + """
            GROUP BY a.carpeta_dia
            ORDER BY a.carpeta_dia
            """,
            tuple(params)
        )
        aus_items = cursor.fetchall() or []
        cursor.execute(
            """
            SELECT a.carpeta_dia AS carpeta_dia, COUNT(DISTINCT a.cedula) AS total
            FROM asistencia a
            WHERE DATE(a.fecha_asistencia) = %s
              AND a.carpeta_dia IN (
                   'AUXILIAR','APOYO CAMIONETAS','AUXILIAR DE MOTO','AUXILIAR CAMIONETA',
                   'AUXMOTO','APOCAMIONETA','AUXCAM'
              )
            """ + where_sup + """
            GROUP BY a.carpeta_dia
            ORDER BY a.carpeta_dia
            """,
            tuple(params)
        )
        aux_items = cursor.fetchall() or []
        cursor.execute(
            """
            SELECT a.carpeta_dia AS carpeta_dia, COUNT(DISTINCT a.cedula) AS total
            FROM asistencia a
            WHERE DATE(a.fecha_asistencia) = %s
              AND a.carpeta_dia IN ('I.ARL','D/F','LM','LL','SUS','PER','VAC','DFAM','RM','RN','I.MED','CP')
            """ + where_sup + """
            GROUP BY a.carpeta_dia
            ORDER BY a.carpeta_dia
            """,
            tuple(params)
        )
        inc_items = cursor.fetchall() or []
        resp = {
            'success': True,
            'fecha': fecha,
            'supervisor': supervisor,
            'operacion': {
                'items': oper_items,
                'total': sum(int(x.get('total') or 0) for x in oper_items)
            },
            'ausencias': {
                'items': aus_items,
                'total': sum(int(x.get('total') or 0) for x in aus_items)
            },
            'auxiliares_camioneta': {
                'items': aux_items,
                'total': sum(int(x.get('total') or 0) for x in aux_items)
            },
            'incapacidad_otros': {
                'items': inc_items,
                'total': sum(int(x.get('total') or 0) for x in inc_items)
            }
        }
        return jsonify(resp)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/asistencia/listado_por_carpeta_dia', methods=['GET'])
@login_required
def api_asistencia_listado_por_carpeta_dia():
    fecha = request.args.get('fecha')
    carpeta_dia = request.args.get('carpeta_dia')
    supervisor = request.args.get('supervisor')
    if not fecha or not carpeta_dia:
        return jsonify({'success': False, 'message': 'fecha y carpeta_dia requeridas'}), 400
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        where = ["DATE(a.fecha_asistencia) = %s"]
        params = [fecha]
        codes = [c.strip() for c in str(carpeta_dia).split(',') if c.strip()]
        if len(codes) > 1:
            where.append("a.carpeta_dia IN (" + ",".join(["%s"] * len(codes)) + ")")
            params.extend(codes)
        else:
            where.append("a.carpeta_dia = %s")
            params.append(carpeta_dia)
        if supervisor and supervisor.strip() not in ('', 'TODOS'):
            where.append("a.super = %s")
            params.append(supervisor)
        cursor.execute(
            """
            SELECT DISTINCT a.cedula, a.tecnico, a.super, COALESCE(a.carpeta,'-') AS carpeta, a.carpeta_dia
            FROM asistencia a
            WHERE """ + " AND ".join(where) + " "
            """
            ORDER BY a.tecnico
            """,
            tuple(params)
        )
        items = cursor.fetchall() or []
        return jsonify({'success': True, 'fecha': fecha, 'supervisor': supervisor, 'carpeta_dia': carpeta_dia, 'items': items})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/asistencia/listado_por_tipificacion', methods=['GET'])
@login_required
def api_asistencia_listado_por_tipificacion():
    fecha = request.args.get('fecha')
    nombre_tipificacion = request.args.get('nombre_tipificacion')
    supervisor = request.args.get('supervisor')
    if not fecha or not nombre_tipificacion:
        return jsonify({'success': False, 'message': 'fecha y nombre_tipificacion requeridas'}), 400
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        where = ["DATE(a.fecha_asistencia) = %s"]
        params = [fecha]
        nombres = [n.strip() for n in str(nombre_tipificacion).split(',') if n.strip()]
        if len(nombres) > 1:
            where.append("t.nombre_tipificacion IN (" + ",".join(["%s"] * len(nombres)) + ")")
            params.extend(nombres)
        else:
            where.append("t.nombre_tipificacion = %s")
            params.append(nombre_tipificacion)
        if supervisor and supervisor.strip() not in ('', 'TODOS'):
            where.append("a.super = %s")
            params.append(supervisor)
        cursor.execute(
            """
            SELECT DISTINCT a.cedula, a.tecnico, a.super, COALESCE(a.carpeta,'-') AS carpeta, a.carpeta_dia
            FROM asistencia a
            INNER JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
            WHERE """ + " AND ".join(where) + " "
            """
            ORDER BY a.tecnico
            """,
            tuple(params)
        )
        items = cursor.fetchall() or []
        return jsonify({'success': True, 'fecha': fecha, 'supervisor': supervisor, 'nombre_tipificacion': nombre_tipificacion, 'items': items})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/test_auth', methods=['GET'])
@login_required
def test_auth():
    return jsonify({'message': 'Autenticado correctamente', 'user': current_user.id})

@app.route('/preoperacional', methods=['POST'])
@login_required
def preoperacional():
    try:
        print(f"DEBUG: Sesión actual: {session}")
        print(f"DEBUG: id_codigo_consumidor en sesión: {session.get('id_codigo_consumidor')}")
        
        # Obtener datos del formulario
        data = request.get_json()
        print(f"DEBUG: Datos recibidos: {data}")
        
        # Obtener la fecha actual en zona horaria de Bogotá
        bogota_tz = pytz.timezone('America/Bogota')
        fecha_actual = datetime.now(bogota_tz).date()
        
        # Verificar si ya existe un registro para este usuario en la fecha actual
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM preoperacional 
            WHERE id_codigo_consumidor = %s AND DATE(fecha) = %s
        """, (session['id_codigo_consumidor'], fecha_actual))
        
        if cursor.fetchone()[0] > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'success': False, 
                'message': 'Ya existe un registro preoperacional para hoy'
            }), 400
        
        # Verificar que el id_codigo_consumidor existe en la tabla recurso_operativo
        cursor.execute("SELECT id_codigo_consumidor FROM recurso_operativo WHERE id_codigo_consumidor = %s", 
                      (session['id_codigo_consumidor'],))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({
                'success': False, 
                'message': 'Usuario no encontrado'
            }), 400

        # VALIDACIÓN CRÍTICA: Verificar si el vehículo tiene mantenimientos abiertos
        placa_vehiculo = data.get('placa_vehiculo')
        if placa_vehiculo:
            cursor.execute("""
                SELECT COUNT(*) FROM mpa_mantenimientos 
                WHERE placa = %s AND estado = 'Abierto'
            """, (placa_vehiculo,))
            
            mantenimientos_abiertos = cursor.fetchone()[0]
            
            if mantenimientos_abiertos > 0:
                cursor.close()
                connection.close()
                return jsonify({
                    'success': False,
                    'message': f'No se puede completar el preoperacional. El vehículo {placa_vehiculo} tiene {mantenimientos_abiertos} mantenimiento(s) abierto(s) pendiente(s). Contacte al área de MPA para finalizar el mantenimiento antes de continuar.',
                    'tiene_mantenimientos_abiertos': True,
                    'placa': placa_vehiculo,
                    'mantenimientos_abiertos': mantenimientos_abiertos
                }), 400

        # Insertar el nuevo registro seleccionando la columna de kilometraje existente
        km_col = None
        try:
            cursor.execute("SHOW COLUMNS FROM preoperacional LIKE 'kilometraje'")
            if cursor.fetchone():
                km_col = 'kilometraje'
            else:
                cursor.execute("SHOW COLUMNS FROM preoperacional LIKE 'kilometraje_actual'")
                if cursor.fetchone():
                    km_col = 'kilometraje_actual'
        except Exception:
            km_col = 'kilometraje'
        insert_query = f"""
            INSERT INTO preoperacional (
                id_codigo_consumidor, fecha, vehiculo_asignado, placa_vehiculo,
                {km_col}, nivel_combustible, nivel_aceite, nivel_liquido_frenos,
                nivel_refrigerante, presion_llantas, luces_funcionando, espejos_estado,
                cinturon_seguridad, extintor_presente, botiquin_presente, triangulos_seguridad,
                chaleco_reflectivo, casco_presente, guantes_presente, rodilleras_presente,
                impermeable_presente, observaciones_generales
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        cursor.execute(insert_query, (
            session['id_codigo_consumidor'],
            datetime.now(bogota_tz),
            data.get('vehiculo_asignado'),
            data.get('placa_vehiculo'),
            data.get('kilometraje'),
            data.get('nivel_combustible'),
            data.get('nivel_aceite'),
            data.get('nivel_liquido_frenos'),
            data.get('nivel_refrigerante'),
            data.get('presion_llantas'),
            data.get('luces_funcionando'),
            data.get('espejos_estado'),
            data.get('cinturon_seguridad'),
            data.get('extintor_presente'),
            data.get('botiquin_presente'),
            data.get('triangulos_seguridad'),
            data.get('chaleco_reflectivo'),
            data.get('casco_presente'),
            data.get('guantes_presente'),
            data.get('rodilleras_presente'),
            data.get('impermeable_presente'),
            data.get('observaciones_generales')
        ))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True, 
            'message': 'Registro preoperacional guardado exitosamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error al guardar el registro: {str(e)}'
        }), 500

@app.route('/verificar_registro_preoperacional', methods=['GET'])
@login_required
def verificar_registro_preoperacional():
    try:
        # Obtener la fecha actual en zona horaria de Bogotá
        bogota_tz = pytz.timezone('America/Bogota')
        fecha_actual = datetime.now(bogota_tz).date()
        hora_actual = datetime.now(bogota_tz).time()
        
        # Verificar si ya existe un registro para este usuario en la fecha actual
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT fecha FROM preoperacional 
            WHERE id_codigo_consumidor = %s AND DATE(fecha) = %s
            ORDER BY fecha DESC LIMIT 1
        """, (session['id_codigo_consumidor'], fecha_actual))
        
        resultado = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if resultado:
            return jsonify({
                'existe_registro': True,
                'ultimo_registro': resultado[0].strftime('%Y-%m-%d %H:%M:%S'),
                'fecha_actual': fecha_actual.strftime('%Y-%m-%d'),
                'hora_bogota': hora_actual.strftime('%H:%M:%S')
            })
        else:
            return jsonify({
                'existe_registro': False,
                'fecha_actual': fecha_actual.strftime('%Y-%m-%d'),
                'hora_bogota': hora_actual.strftime('%H:%M:%S')
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al verificar registro: {str(e)}'
        }), 500

@app.route('/api/validar-mantenimiento-preoperacional', methods=['GET'])
@login_required
def validar_mantenimiento_preoperacional():
    """Valida si el vehículo del técnico tiene mantenimientos abiertos"""
    try:
        # Obtener la placa del vehículo del técnico desde la sesión o datos del usuario
        placa_vehiculo = request.args.get('placa')
        
        if not placa_vehiculo:
            return jsonify({
                'success': False,
                'message': 'Placa del vehículo requerida'
            }), 400
        
        # Verificar si hay mantenimientos abiertos para esta placa
        cursor = get_db_connection().cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM mpa_mantenimientos 
            WHERE placa = %s AND estado = 'Abierto'
        """, (placa_vehiculo,))
        
        mantenimientos_abiertos = cursor.fetchone()[0]
        cursor.close()
        
        if mantenimientos_abiertos > 0:
            return jsonify({
                'success': False,
                'tiene_mantenimientos_abiertos': True,
                'message': f'No se puede completar el preoperacional. El vehículo {placa_vehiculo} tiene {mantenimientos_abiertos} mantenimiento(s) abierto(s) pendiente(s). Contacte al área de MPA.'
            })
        else:
            return jsonify({
                'success': True,
                'tiene_mantenimientos_abiertos': False,
                'message': 'El vehículo no tiene mantenimientos abiertos. Puede proceder con el preoperacional.'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al validar mantenimientos: {str(e)}'
        }), 500

# Alias para envío del formulario preoperacional desde Operativo (FormData)
@app.route('/preoperacional_operativo', methods=['POST'])
@login_required
def preoperacional_operativo():
    try:
        bogota_tz = pytz.timezone('America/Bogota')
        fecha_actual = datetime.now(bogota_tz).date()

        connection = get_db_connection()
        if connection is None:
            return jsonify({'status': 'error', 'message': 'Error de conexión a la base de datos.'}), 500
        cursor = connection.cursor()

        # Evitar doble registro en el mismo día
        cursor.execute(
            """
            SELECT COUNT(*) FROM preoperacional 
            WHERE id_codigo_consumidor = %s AND DATE(fecha) = %s
            """,
            (session.get('id_codigo_consumidor'), fecha_actual)
        )
        if cursor.fetchone()[0] > 0:
            cursor.close()
            connection.close()
            return jsonify({'status': 'error', 'message': 'Ya existe un registro preoperacional para hoy'}), 400

        # Validar mantenimientos abiertos por placa
        placa_vehiculo = request.form.get('placa_vehiculo')
        if placa_vehiculo:
            cursor.execute(
                """
                SELECT COUNT(*) FROM mpa_mantenimientos 
                WHERE placa = %s AND estado = 'Abierto'
                """,
                (placa_vehiculo,)
            )
            abiertos = cursor.fetchone()[0]
            if abiertos > 0:
                cursor.close()
                connection.close()
                return jsonify({
                    'status': 'error',
                    'message': f'No se puede completar el preoperacional. El vehículo {placa_vehiculo} tiene {abiertos} mantenimiento(s) abierto(s).',
                    'tiene_mantenimientos_abiertos': True,
                    'placa': placa_vehiculo,
                    'mantenimientos_abiertos': abiertos
                }), 400

        # Insertar registro tomando campos del formulario (detectar columna de kilometraje)
        km_col = None
        try:
            cursor.execute("SHOW COLUMNS FROM preoperacional LIKE 'kilometraje'")
            if cursor.fetchone():
                km_col = 'kilometraje'
            else:
                cursor.execute("SHOW COLUMNS FROM preoperacional LIKE 'kilometraje_actual'")
                if cursor.fetchone():
                    km_col = 'kilometraje_actual'
        except Exception:
            km_col = 'kilometraje'
        insert_query = f"""
            INSERT INTO preoperacional (
                id_codigo_consumidor, fecha, vehiculo_asignado, placa_vehiculo,
                {km_col}, nivel_combustible, nivel_aceite, nivel_liquido_frenos,
                nivel_refrigerante, presion_llantas, luces_funcionando, espejos_estado,
                cinturon_seguridad, extintor_presente, botiquin_presente, triangulos_seguridad,
                chaleco_reflectivo, casco_presente, guantes_presente, rodilleras_presente,
                impermeable_presente, observaciones_generales
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        cursor.execute(
            insert_query,
            (
                session.get('id_codigo_consumidor'),
                datetime.now(bogota_tz),
                request.form.get('vehiculo_asignado'),
                request.form.get('placa_vehiculo'),
                (lambda v: v if (v is not None and v != '') else request.form.get('kilometraje_actual'))(request.form.get('kilometraje')),
                request.form.get('nivel_combustible'),
                request.form.get('nivel_aceite'),
                request.form.get('nivel_liquido_frenos'),
                request.form.get('nivel_refrigerante'),
                request.form.get('presion_llantas'),
                request.form.get('luces_funcionando'),
                request.form.get('espejos_estado'),
                request.form.get('cinturon_seguridad'),
                request.form.get('extintor_presente'),
                request.form.get('botiquin_presente'),
                request.form.get('triangulos_seguridad'),
                request.form.get('chaleco_reflectivo'),
                request.form.get('casco_presente'),
                request.form.get('guantes_presente'),
                request.form.get('rodilleras_presente'),
                request.form.get('impermeable_presente'),
                request.form.get('observaciones_generales')
            )
        )
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'status': 'success', 'message': 'Preoperacional registrado exitosamente'})
    except Exception as e:
        try:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'connection' in locals() and connection and connection.is_connected():
                connection.close()
        except Exception:
            pass
        return jsonify({'status': 'error', 'message': f'Error al registrar preoperacional: {str(e)}'}), 500

# Datos para precargar formulario de preoperacional operativo
@app.route('/api/operativo/datos-preoperacional', methods=['GET'])
@login_required
def api_operativo_datos_preoperacional():
    try:
        bogota_tz = pytz.timezone('America/Bogota')
        hoy = datetime.now(bogota_tz).date()

        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'})
        cursor = connection.cursor(dictionary=True)

        # Datos del usuario operativo
        cursor.execute(
            """
            SELECT ciudad, super, id_codigo_consumidor
            FROM recurso_operativo
            WHERE id_codigo_consumidor = %s AND estado = 'Activo'
            """,
            (session.get('id_codigo_consumidor'),)
        )
        ro = cursor.fetchone() or {}

        # Vehículo asignado
        cursor.execute(
            """
            SELECT placa, marca, modelo, tipo_vehiculo
            FROM mpa_vehiculos
            WHERE tecnico_asignado = %s AND estado = 'Activo'
            ORDER BY id_mpa_vehiculos DESC
            LIMIT 1
            """,
            (session.get('id_codigo_consumidor'),)
        )
        veh = cursor.fetchone() or {}
        placa = veh.get('placa')

        # Último kilometraje
        cursor.execute(
            """
            SELECT kilometraje, fecha
            FROM preoperacional
            WHERE id_codigo_consumidor = %s
            ORDER BY fecha DESC
            LIMIT 1
            """,
            (session.get('id_codigo_consumidor'),)
        )
        km_row = cursor.fetchone() or {}

        # Helper para calcular días
        def dias_restantes(fecha_str):
            try:
                y, m, d = map(int, str(fecha_str).split('-'))
                fv = date(y, m, d)
                return (fv - hoy).days
            except Exception:
                return None

        # Consultar vencimientos propios (SOAT, Tecnomecánica del vehículo y Licencia del técnico)
        fecha_venc_soat = None
        fecha_venc_tm = None
        fecha_venc_lic = None
        alertas = []

        if placa:
            cursor.execute(
                """
                SELECT fecha_vencimiento
                FROM mpa_soat
                WHERE placa = %s AND estado = 'Activo' AND fecha_vencimiento IS NOT NULL AND fecha_vencimiento > '1900-01-01'
                ORDER BY fecha_vencimiento DESC
                LIMIT 1
                """,
                (placa,)
            )
            r = cursor.fetchone()
            if r and r.get('fecha_vencimiento'):
                fv = str(r['fecha_vencimiento'])
                fecha_venc_soat = fv
                dias = dias_restantes(fv)
                if dias is not None:
                    if dias <= 0:
                        alertas.append({'tipo': 'error', 'mensaje': f'SOAT vencido (placa {placa})'})
                    elif dias <= 30:
                        alertas.append({'tipo': 'warning', 'mensaje': f'SOAT próximo a vencer en {dias} días (placa {placa})'})

            cursor.execute(
                """
                SELECT fecha_vencimiento
                FROM mpa_tecnico_mecanica
                WHERE placa = %s AND estado = 'Activo' AND fecha_vencimiento IS NOT NULL AND fecha_vencimiento > '1900-01-01'
                ORDER BY fecha_vencimiento DESC
                LIMIT 1
                """,
                (placa,)
            )
            r2 = cursor.fetchone()
            if r2 and r2.get('fecha_vencimiento'):
                fv = str(r2['fecha_vencimiento'])
                fecha_venc_tm = fv
                dias = dias_restantes(fv)
                if dias is not None:
                    if dias <= 0:
                        alertas.append({'tipo': 'error', 'mensaje': f'Tecnomecánica vencida (placa {placa})'})
                    elif dias <= 30:
                        alertas.append({'tipo': 'warning', 'mensaje': f'Tecnomecánica próxima a vencer en {dias} días (placa {placa})'})

        cursor.execute(
            """
            SELECT tipo_licencia, fecha_vencimiento
            FROM mpa_licencia_conducir
            WHERE tecnico = %s AND estado = 'Activo' AND fecha_vencimiento IS NOT NULL AND fecha_vencimiento > '1900-01-01'
            ORDER BY fecha_vencimiento DESC
            LIMIT 1
            """,
            (session.get('id_codigo_consumidor'),)
        )
        r3 = cursor.fetchone()
        if r3 and r3.get('fecha_vencimiento'):
            fv = str(r3['fecha_vencimiento'])
            fecha_venc_lic = fv
            dias = dias_restantes(fv)
            if dias is not None:
                if dias <= 0:
                    alertas.append({'tipo': 'error', 'mensaje': 'Licencia de conducir vencida'})
                elif dias <= 30:
                    alertas.append({'tipo': 'warning', 'mensaje': f'Licencia próxima a vencer en {dias} días'})

        data = {
            'ciudad': ro.get('ciudad'),
            'supervisor': ro.get('super'),
            'tipo_vehiculo': veh.get('tipo_vehiculo'),
            'placa': placa,
            'modelo': veh.get('modelo'),
            'marca': veh.get('marca'),
            'tipo_licencia': (r3.get('tipo_licencia') if r3 else None),
            'fecha_venc_licencia': fecha_venc_lic,
            'fecha_venc_soat': fecha_venc_soat,
            'fecha_venc_tecnico_mecanica': fecha_venc_tm,
            'ultimo_kilometraje': km_row.get('kilometraje') or 0,
            'fecha_ultimo_kilometraje': km_row.get('fecha').strftime('%Y-%m-%d %H:%M:%S') if km_row.get('fecha') else None
        }

        cursor.close()
        connection.close()
        return jsonify({'success': True, 'data': data, 'alertas': alertas})
    except Exception as e:
        try:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'connection' in locals() and connection and connection.is_connected():
                connection.close()
        except Exception:
            pass
        return jsonify({'success': False, 'message': str(e)})

# Validación de kilometraje en tiempo real para Operativo
@app.route('/api/operativo/validar-kilometraje', methods=['POST'])
@login_required
def api_operativo_validar_kilometraje():
    try:
        if not (current_user.has_role('operativo') or current_user.has_role('administrativo')):
            return jsonify({'success': False, 'message': 'Sin permisos'}), 403

        data = request.get_json() or {}
        placa_raw = data.get('placa') or ''
        km_prop = data.get('kilometraje_propuesto')

        try:
            km_prop = int(km_prop)
        except Exception:
            return jsonify({'success': False, 'message': 'El kilometraje debe ser un número entero'}), 400

        if km_prop < 0:
            return jsonify({'success': False, 'message': 'El kilometraje no puede ser negativo'}), 400

        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        placa_norm = placa_raw.strip().upper().replace('-', '').replace(' ', '')
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT kilometraje, fecha
            FROM preoperacional 
            WHERE UPPER(REPLACE(REPLACE(TRIM(placa_vehiculo), '-', ''), ' ', '')) = %s
            ORDER BY fecha DESC 
            LIMIT 1
            """,
            (placa_norm,)
        )
        row = cursor.fetchone()
        cursor.close(); connection.close()

        if not row:
            return jsonify({'success': True, 'valido': True, 'ultimo_kilometraje': 0, 'fecha_ultimo_registro': '', 'mensaje': 'Primer registro de kilometraje para este vehículo'})

        ultimo_km = row.get('kilometraje') or 0
        fecha_ult = row.get('fecha')

        if km_prop < ultimo_km:
            return jsonify({
                'success': True,
                'valido': False,
                'ultimo_kilometraje': ultimo_km,
                'fecha_ultimo_registro': fecha_ult.strftime('%d/%m/%Y') if fecha_ult else '',
                'mensaje': f"El kilometraje no puede ser menor al último registrado: {ultimo_km} km en fecha {fecha_ult.strftime('%d/%m/%Y') if fecha_ult else 'N/A'}"
            })

        if km_prop > 1000000:
            return jsonify({
                'success': True,
                'valido': False,
                'ultimo_kilometraje': ultimo_km,
                'fecha_ultimo_registro': fecha_ult.strftime('%d/%m/%Y') if fecha_ult else '',
                'mensaje': 'El kilometraje no puede superar los 1,000,000 km.'
            })

        return jsonify({
            'success': True,
            'valido': True,
            'ultimo_kilometraje': ultimo_km,
            'fecha_ultimo_registro': fecha_ult.strftime('%d/%m/%Y') if fecha_ult else '',
            'mensaje': 'Kilometraje válido'
        })
    except Exception as e:
        try:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'connection' in locals() and connection and connection.is_connected():
                connection.close()
        except Exception:
            pass
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500

# ============================================================================
# MÓDULO ANALISTAS - API ENDPOINTS
# ============================================================================

@app.route('/analistas')
@login_required
def analistas_index():
    """Renderizar el dashboard del módulo analistas"""
    return render_template('modulos/analistas/dashboard.html')

# ============================================================================
# MÓDULO OPERATIVO - RUTAS
# ============================================================================

@app.route('/operativo')
@login_required
def operativo_dashboard():
    """Renderizar el dashboard del módulo operativo"""
    try:
        return render_template('modulos/operativo/dashboard.html')
    except Exception as e:
        flash(f'Error al cargar el módulo operativo: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/analistas/causas')
@login_required
def analistas_causas():
    """Renderizar la página de causas de cierre"""
    return render_template('modulos/analistas/index.html')

@app.route('/analistas/dashboard')
@login_required
def analistas_dashboard():
    """Renderizar el dashboard del módulo analistas"""
    return render_template('modulos/analistas/dashboard.html')

@app.route('/analistas/codigos')
@login_required
def analistas_codigos():
    """Renderizar la página de códigos de facturación"""
    return render_template('modulos/analistas/codigos.html')

@app.route('/analistas/inicio-operacion-tecnicos')
@login_required
def inicio_operacion_tecnicos():
    """Renderizar la página de inicio de operación para técnicos"""
    return render_template('inicio_operacion_tecnicos.html')

@app.route('/api/analistas/causas-cierre', methods=['GET'])
@login_required
def api_causas_cierre():
    """API endpoint para obtener todas las causas de cierre con filtros opcionales"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify([])
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener parámetros de filtro
        texto_busqueda = request.args.get('busqueda', '').strip()
        tecnologia = request.args.get('tecnologia', '').strip()
        agrupacion = request.args.get('agrupacion', '').strip()
        grupo = request.args.get('grupo', '').strip()
        
        # Construir consulta base
        query = """
            SELECT 
                idbase_causas_cierre,
                codigo_causas_cierre,
                tipo_causas_cierre,
                nombre_causas_cierre,
                tecnologia_causas_cierre,
                instrucciones_de_uso_causas_cierre,
                agrupaciones_causas_cierre,
                todos_los_grupos_causas_cierre,
                facturable_causas_cierre
            FROM base_causas_cierre
            WHERE 1=1
        """
        
        params = []
        
        # Agregar filtros dinámicamente
        if texto_busqueda:
            query += """
                AND (
                    codigo_causas_cierre LIKE %s OR 
                    nombre_causas_cierre LIKE %s OR 
                    instrucciones_de_uso_causas_cierre LIKE %s
                )
            """
            busqueda_param = f"%{texto_busqueda}%"
            params.extend([busqueda_param, busqueda_param, busqueda_param])
            
        if tecnologia:
            query += " AND tecnologia_causas_cierre = %s"
            params.append(tecnologia)
            
        if agrupacion:
            query += " AND agrupaciones_causas_cierre = %s"
            params.append(agrupacion)
            
        if grupo:
            query += " AND todos_los_grupos_causas_cierre = %s"
            params.append(grupo)
            
        query += " ORDER BY codigo_causas_cierre ASC"
        
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        
        return jsonify(resultados)
        
    except mysql.connector.Error as e:
        try:
            errno = getattr(e, 'errno', None)
        except Exception:
            errno = None
        logging.error(f"Error en API causas-cierre: {str(e)} (errno={errno})")
        if errno == 1146:
            return jsonify([])
        return jsonify({'error': 'Error al consultar la base de datos'}), 500
    except Exception as e:
        logging.error(f"Error inesperado en API causas-cierre: {str(e)}")
        return jsonify([])
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/analistas/grupos', methods=['GET'])
@login_required
def api_grupos_causas_cierre():
    """API endpoint para obtener la lista única de grupos disponibles, opcionalmente filtrados por tecnología y agrupación"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify([])
            
        cursor = connection.cursor()
        
        # Obtener parámetros de filtrado si se proporcionan
        tecnologia = request.args.get('tecnologia', '').strip()
        agrupacion = request.args.get('agrupacion', '').strip()
        
        # Construir la consulta base
        query = """
            SELECT DISTINCT todos_los_grupos_causas_cierre
            FROM base_causas_cierre
            WHERE todos_los_grupos_causas_cierre IS NOT NULL 
                AND todos_los_grupos_causas_cierre != ''
        """
        
        params = []
        
        # Agregar filtros según los parámetros proporcionados
        if tecnologia:
            query += " AND tecnologia_causas_cierre = %s"
            params.append(tecnologia)
            
        if agrupacion:
            query += " AND agrupaciones_causas_cierre = %s"
            params.append(agrupacion)
            
        query += " ORDER BY todos_los_grupos_causas_cierre ASC"
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        resultados = cursor.fetchall()
        
        # Extraer solo los valores de la tupla
        grupos = [row[0] for row in resultados]
        
        return jsonify(grupos)
        
    except mysql.connector.Error as e:
        errno = getattr(e, 'errno', None)
        logging.error(f"Error en API grupos: {str(e)} (errno={errno})")
        if errno == 1146:
            return jsonify([])
        return jsonify({'error': 'Error al consultar la base de datos'}), 500
    except Exception as e:
        logging.error(f"Error inesperado en API grupos: {str(e)}")
        return jsonify([])
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/analistas/tecnologias', methods=['GET'])
@login_required
def api_tecnologias_causas_cierre():
    """API endpoint para obtener la lista única de tecnologías disponibles"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify([])
            
        cursor = connection.cursor()
        
        query = """
            SELECT DISTINCT tecnologia_causas_cierre
            FROM base_causas_cierre
            WHERE tecnologia_causas_cierre IS NOT NULL 
                AND tecnologia_causas_cierre != ''
            ORDER BY tecnologia_causas_cierre ASC
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        # Extraer solo los valores de la tupla
        tecnologias = [row[0] for row in resultados]
        
        return jsonify(tecnologias)
        
    except mysql.connector.Error as e:
        errno = getattr(e, 'errno', None)
        logging.error(f"Error en API tecnologías: {str(e)} (errno={errno})")
        if errno == 1146:
            return jsonify([])
        return jsonify({'error': 'Error al consultar la base de datos'}), 500
    except Exception as e:
        logging.error(f"Error inesperado en API tecnologías: {str(e)}")
        return jsonify([])
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/analistas/agrupaciones', methods=['GET'])
@login_required
def api_agrupaciones_causas_cierre():
    """API endpoint para obtener la lista única de agrupaciones disponibles, opcionalmente filtradas por tecnología"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify([])
            
        cursor = connection.cursor()
        
        # Obtener parámetro de tecnología si se proporciona
        tecnologia = request.args.get('tecnologia', '').strip()
        
        if tecnologia:
            # Filtrar agrupaciones por tecnología específica
            query = """
                SELECT DISTINCT agrupaciones_causas_cierre
                FROM base_causas_cierre
                WHERE agrupaciones_causas_cierre IS NOT NULL 
                    AND agrupaciones_causas_cierre != ''
                    AND tecnologia_causas_cierre = %s
                ORDER BY agrupaciones_causas_cierre ASC
            """
            cursor.execute(query, (tecnologia,))
        else:
            # Obtener todas las agrupaciones
            query = """
                SELECT DISTINCT agrupaciones_causas_cierre
                FROM base_causas_cierre
                WHERE agrupaciones_causas_cierre IS NOT NULL 
                    AND agrupaciones_causas_cierre != ''
                ORDER BY agrupaciones_causas_cierre ASC
            """
            cursor.execute(query)
        
        resultados = cursor.fetchall()
        
        # Extraer solo los valores de la tupla
        agrupaciones = [row[0] for row in resultados]
        
        return jsonify(agrupaciones)
        
    except mysql.connector.Error as e:
        errno = getattr(e, 'errno', None)
        logging.error(f"Error en API agrupaciones: {str(e)} (errno={errno})")
        if errno == 1146:
            return jsonify([])
        return jsonify({'error': 'Error al consultar la base de datos'}), 500
    except Exception as e:
        logging.error(f"Error inesperado en API agrupaciones: {str(e)}")
        return jsonify([])
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/analistas/estadisticas', methods=['GET'])
@login_required
def api_estadisticas_causas_cierre():
    """API endpoint para obtener estadísticas generales de las causas de cierre"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Estadísticas generales
        estadisticas = {}
        
        # Total de registros
        cursor.execute("SELECT COUNT(*) as total FROM base_causas_cierre")
        estadisticas['total_registros'] = cursor.fetchone()['total']
        
        # Distribución por tecnología
        cursor.execute("""
            SELECT tecnologia_causas_cierre, COUNT(*) as cantidad
            FROM base_causas_cierre
            WHERE tecnologia_causas_cierre IS NOT NULL
            GROUP BY tecnologia_causas_cierre
            ORDER BY cantidad DESC
        """)
        estadisticas['por_tecnologia'] = cursor.fetchall()
        
        # Distribución por agrupación
        cursor.execute("""
            SELECT agrupaciones_causas_cierre, COUNT(*) as cantidad
            FROM base_causas_cierre
            WHERE agrupaciones_causas_cierre IS NOT NULL
            GROUP BY agrupaciones_causas_cierre
            ORDER BY cantidad DESC
        """)
        estadisticas['por_agrupacion'] = cursor.fetchall()
        
        # Top 10 grupos más frecuentes
        cursor.execute("""
            SELECT todos_los_grupos_causas_cierre, COUNT(*) as cantidad
            FROM base_causas_cierre
            WHERE todos_los_grupos_causas_cierre IS NOT NULL
            GROUP BY todos_los_grupos_causas_cierre
            ORDER BY cantidad DESC
            LIMIT 10
        """)
        estadisticas['top_grupos'] = cursor.fetchall()
        
        return jsonify(estadisticas)
        
    except mysql.connector.Error as e:
        logging.error(f"Error en API estadísticas: {str(e)}")
        return jsonify({'error': 'Error al consultar la base de datos'}), 500
    except Exception as e:
        logging.error(f"Error inesperado en API estadísticas: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/analistas/tecnicos-asignados', methods=['GET'])
@login_required
def api_tecnicos_asignados():
    """API endpoint para obtener técnicos asignados al analista actual con su información de asistencia"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener el nombre del analista actual desde la sesión
        analista_nombre = current_user.nombre if current_user else None
        
        if not analista_nombre:
            return jsonify({'error': 'No se pudo identificar al analista actual'}), 401
        
        # Obtener parámetro de fecha opcional
        fecha_consulta = request.args.get('fecha')
        if not fecha_consulta:
            # Si no se proporciona fecha, usar la fecha actual
            fecha_consulta = 'CURDATE()'
            fecha_param = None
        else:
            # Si se proporciona fecha, usarla como parámetro
            fecha_param = fecha_consulta
        
        # Consulta para obtener técnicos asignados al analista actual
        query_tecnicos = """
            SELECT DISTINCT
                ro.id_codigo_consumidor,
                ro.recurso_operativo_cedula as cedula,
                ro.nombre as tecnico,
                ro.carpeta,
                ro.cliente,
                ro.ciudad,
                ro.super as supervisor,
                ro.analista
            FROM recurso_operativo ro
            WHERE ro.analista = %s
            AND ro.estado = 'Activo'
            ORDER BY ro.nombre
        """
        
        cursor.execute(query_tecnicos, (analista_nombre,))
        tecnicos = cursor.fetchall()
        
        # Para cada técnico, obtener información de asistencia del día actual
        tecnicos_con_asistencia = []
        
        for tecnico in tecnicos:
            # Buscar asistencia del día especificado o actual
            if fecha_param:
                query_asistencia = """
                    SELECT 
                        a.carpeta_dia,
                        a.fecha_asistencia,
                        a.hora_inicio,
                        a.estado,
                        a.novedad,
                        ta.nombre_tipificacion,
                        ta.codigo_tipificacion,
                        ta.grupo as grupo_tipificacion,
                        pc.presupuesto_eventos,
                        pc.presupuesto_diario,
                        pc.presupuesto_carpeta as nombre_presupuesto_carpeta
                    FROM asistencia a
                    LEFT JOIN tipificacion_asistencia ta ON a.carpeta_dia = ta.codigo_tipificacion
                    LEFT JOIN presupuesto_carpeta pc ON ta.nombre_tipificacion = pc.presupuesto_carpeta
                    WHERE a.cedula = %s
                    AND DATE(a.fecha_asistencia) = %s
                    ORDER BY a.fecha_asistencia DESC
                    LIMIT 1
                """
                cursor.execute(query_asistencia, (tecnico['cedula'], fecha_param))
            else:
                query_asistencia = """
                    SELECT 
                        a.carpeta_dia,
                        a.fecha_asistencia,
                        a.hora_inicio,
                        a.estado,
                        a.novedad,
                        ta.nombre_tipificacion,
                        ta.codigo_tipificacion,
                        ta.grupo as grupo_tipificacion,
                        pc.presupuesto_eventos,
                        pc.presupuesto_diario,
                        pc.presupuesto_carpeta as nombre_presupuesto_carpeta
                    FROM asistencia a
                    LEFT JOIN tipificacion_asistencia ta ON a.carpeta_dia = ta.codigo_tipificacion
                    LEFT JOIN presupuesto_carpeta pc ON ta.nombre_tipificacion = pc.presupuesto_carpeta
                    WHERE a.cedula = %s
                    AND DATE(a.fecha_asistencia) = CURDATE()
                    ORDER BY a.fecha_asistencia DESC
                    LIMIT 1
                """
                cursor.execute(query_asistencia, (tecnico['cedula'],))
            asistencia = cursor.fetchone()

            inspeccion_info = {
                'fecha_ultima': None,
                'items_malos': 0,
                'dias_restantes_subsanar': None,
                'placa': None
            }
            try:
                cursor.execute(
                    """
                    SELECT *
                    FROM mpa_inspeccion_vehiculo
                    WHERE id_codigo_consumidor = %s
                    ORDER BY fecha_inspeccion DESC
                    LIMIT 1
                    """,
                    (tecnico['id_codigo_consumidor'],)
                )
                ultima_inspeccion = cursor.fetchone()
                if not ultima_inspeccion:
                    cursor.execute(
                        """
                        SELECT *
                        FROM mpa_inspeccion_vehiculo
                        WHERE recurso_operativo_cedula = %s
                        ORDER BY fecha_inspeccion DESC
                        LIMIT 1
                        """,
                        (tecnico['cedula'],)
                    )
                    ultima_inspeccion = cursor.fetchone()
                if ultima_inspeccion:
                    fi = ultima_inspeccion.get('fecha_inspeccion')
                    fecha_str = None
                    fi_date = None
                    if fi:
                        try:
                            fi_date = fi.date() if hasattr(fi, 'date') else datetime.strptime(str(fi)[:19], '%Y-%m-%d %H:%M:%S').date()
                        except Exception:
                            try:
                                fi_date = datetime.strptime(str(fi)[:10], '%Y-%m-%d').date()
                            except Exception:
                                fi_date = None
                        if fi_date:
                            try:
                                fecha_str = fi_date.strftime('%Y-%m-%d')
                            except Exception:
                                fecha_str = str(fi)[:10]
                    bm_fields = [
                        'estado_fisico_espejos_laterales','estado_fisico_pito','estado_fisico_freno_servicio','estado_fisico_manillares','estado_fisico_guayas','estado_fisico_tanque_combustible','estado_fisico_encendido','estado_fisico_pedales','estado_fisico_guardabarros','estado_fisico_sillin_tapiceria','estado_fisico_tablero','estado_fisico_mofle_silenciador','estado_fisico_kit_arrastre','estado_fisico_reposa_pies','estado_fisico_pata_lateral_central','estado_fisico_tijera_amortiguador','estado_fisico_bateria','luces_altas_bajas','luces_direccionales_delanteros','luces_direccionales_traseros','luces_luz_placa','luces_stop','prevension_casco','prevension_guantes','prevension_rodilleras','prevension_coderas','llantas_labrado_llantas','llantas_rines','llantas_presion_aire','otros_aceite','otros_suspension_direccion','otros_caja_cambios','otros_conexiones_electricas'
                    ]
                    bm_synonyms = {
                        'prevension_casco': ['prevencion_casco'],
                        'prevension_guantes': ['prevencion_guantes'],
                        'prevension_rodilleras': ['prevencion_rodilleras'],
                        'prevension_coderas': ['prevencion_coderas']
                    }
                    malos = 0
                    for k in bm_fields:
                        v = ultima_inspeccion.get(k)
                        if v is None and k in bm_synonyms:
                            for alt in bm_synonyms[k]:
                                if ultima_inspeccion.get(alt) is not None:
                                    v = ultima_inspeccion.get(alt)
                                    break
                        s = str(v or '').strip().upper()
                        if s == 'M' or s == 'MALO':
                            malos += 1
                    dias_restantes = None
                    if fi_date:
                        try:
                            hoy = get_bogota_datetime().date()
                            transcurridos = (hoy - fi_date).days
                            dias_restantes = 5 - transcurridos
                            if dias_restantes < 0:
                                dias_restantes = 0
                        except Exception:
                            dias_restantes = None
                    inspeccion_info = {
                        'fecha_ultima': fecha_str,
                        'items_malos': malos,
                        'dias_restantes_subsanar': dias_restantes,
                        'placa': ultima_inspeccion.get('placa')
                    }
            except Exception:
                pass
            
            # Agregar información de asistencia al técnico
            tecnico_info = {
                'id_codigo_consumidor': tecnico['id_codigo_consumidor'],
                'cedula': tecnico['cedula'],
                'tecnico': tecnico['tecnico'],
                'carpeta': tecnico['carpeta'],
                'cliente': tecnico['cliente'],
                'ciudad': tecnico['ciudad'],
                'supervisor': tecnico['supervisor'],
                'analista': tecnico['analista'],
                'asistencia_hoy': {
                    'carpeta_dia': asistencia['carpeta_dia'] if asistencia else None,
                    'fecha_asistencia': asistencia['fecha_asistencia'].isoformat() if asistencia and asistencia['fecha_asistencia'] else None,
                    # Normalizar hora_inicio a formato HH:MM para compatibilidad con input type="time"
                    'hora_inicio': (
                        asistencia['hora_inicio'].strftime('%H:%M')
                        if asistencia and asistencia['hora_inicio'] else None
                    ),
                    'estado': asistencia['estado'] if asistencia else None,
                    'novedad': asistencia['novedad'] if asistencia else None,
                    'tipificacion': asistencia['nombre_tipificacion'] if asistencia else 'Sin registro',
                    'codigo_tipificacion': asistencia['codigo_tipificacion'] if asistencia else None,
                    'grupo_tipificacion': asistencia['grupo_tipificacion'] if asistencia else None,
                    'presupuesto_eventos': asistencia['presupuesto_eventos'] if asistencia else None,
                    'presupuesto_diario': asistencia['presupuesto_diario'] if asistencia else None,
                    'nombre_presupuesto_carpeta': asistencia['nombre_presupuesto_carpeta'] if asistencia else None
                },
                'revision_vehicular': inspeccion_info,
                'mostrar_alerta_revision': bool(inspeccion_info['items_malos'])
            }
            
            tecnicos_con_asistencia.append(tecnico_info)
        
        return jsonify({
            'success': True,
            'analista': analista_nombre,
            'total_tecnicos': len(tecnicos_con_asistencia),
            'tecnicos': tecnicos_con_asistencia
        })
        
    except mysql.connector.Error as e:
        logging.error(f"Error en API técnicos asignados: {str(e)}")
        return jsonify({'error': 'Error al consultar la base de datos'}), 500
    except Exception as e:
        logging.error(f"Error inesperado en API técnicos asignados: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# ============================================================================
# MÓDULO SSTT (SEGURIDAD Y SALUD EN EL TRABAJO) - RUTAS Y API ENDPOINTS
# ============================================================================

@app.route('/sstt')
@login_required
def sstt_dashboard():
    """Dashboard principal del módulo SSTT"""
    if not current_user.has_role('sstt') and not current_user.has_role('administrativo'):
        return redirect(url_for('login'))
    return render_template('modulos/sstt/dashboard.html')

@app.route('/sstt/inspecciones')
@login_required
def sstt_inspecciones():
    """Página de gestión de inspecciones de seguridad"""
    if not current_user.has_role('sstt') and not current_user.has_role('administrativo'):
        return redirect(url_for('login'))
    return render_template('modulos/sstt/inspecciones.html')

@app.route('/sstt/capacitaciones')
@login_required
def sstt_capacitaciones():
    """Página de gestión de capacitaciones"""
    if not current_user.has_role('sstt') and not current_user.has_role('administrativo'):
        return redirect(url_for('login'))
    return render_template('modulos/sstt/capacitaciones.html')

@app.route('/sstt/incidentes')
@login_required
def sstt_incidentes():
    """Página de gestión de incidentes laborales"""
    if not current_user.has_role('sstt') and not current_user.has_role('administrativo'):
        return redirect(url_for('login'))
    return render_template('modulos/sstt/incidentes.html')

@app.route('/sstt/epp')
@login_required
def sstt_epp():
    """Página de control de EPP (Elementos de Protección Personal)"""
    if not current_user.has_role('sstt') and not current_user.has_role('administrativo'):
        return redirect(url_for('login'))
    return render_template('modulos/sstt/epp.html')

@app.route('/sstt/vencimientos-cursos')
@login_required
def sstt_vencimientos_cursos():
    if not current_user.has_role('sstt') and not current_user.has_role('administrativo'):
        return redirect(url_for('login'))
    return render_template('modulos/sstt/vencimientos_cursos.html')

@app.route('/sstt/preoperacional')
@login_required
def sstt_preoperacional_visual():
    if not current_user.has_role('sstt') and not current_user.has_role('administrativo'):
        return redirect(url_for('login'))
    return render_template('modulos/sstt/preoperacional_visual.html')

# API Endpoints para SSTT

@app.route('/api/sstt/tipos-riesgo', methods=['GET'])
@login_required
def api_sstt_tipos_riesgo():
    """API para obtener tipos de riesgo"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sstt_tipos_riesgo ORDER BY nombre_riesgo")
        tipos_riesgo = cursor.fetchall()
        
        return jsonify({'tipos_riesgo': tipos_riesgo})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/sstt/vencimientos-cursos/tipos', methods=['GET'])
@login_required_api()
def api_sstt_vencimientos_cursos_tipos():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sstt_vencimientos_cursos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_codigo_consumidor INT NOT NULL,
                sstt_vencimientos_cursos_nombre VARCHAR(200),
                recurso_operativo_cedula VARCHAR(20),
                sstt_vencimientos_cursos_tipo_curso VARCHAR(100) NOT NULL,
                sstt_vencimientos_cursos_fecha DATE NULL DEFAULT NULL,
                sstt_vencimientos_cursos_fecha_ven DATE NULL DEFAULT NULL,
                sstt_vencimientos_cursos_observacion TEXT,
                sstt_vencimientos_cursos_validado TINYINT(1) DEFAULT 0,
                sstt_vencimientos_cursos_pendiente TINYINT(1) NOT NULL DEFAULT 0,
                sstt_vencimientos_cursos_fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_cedula (recurso_operativo_cedula),
                INDEX idx_tipo (sstt_vencimientos_cursos_tipo_curso),
                INDEX idx_fecha_ven (sstt_vencimientos_cursos_fecha_ven)
            )
            """
        )
        cursor.execute(
            """
            SELECT DISTINCT sstt_vencimientos_cursos_tipo_curso AS tipo
            FROM sstt_vencimientos_cursos
            WHERE sstt_vencimientos_cursos_tipo_curso IS NOT NULL
              AND TRIM(sstt_vencimientos_cursos_tipo_curso) <> ''
            ORDER BY 1
            """
        )
        _ = cursor.fetchall()
        tipos = [
            'EXAMEN MEDICO INGRESO',
  'EXAMEN MEDICO PERIODICO',
  'CURSO ALTURAS',
  'CURSO MANEJO DEFENSIVO',
  'CURSO INDUCCION SST',
  'CURSO REINDUCCION SST'
        ]
        cursor.close(); connection.close()
        return jsonify({'success': True, 'data': tipos})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sstt/inspecciones', methods=['GET', 'POST'])
@login_required
def api_sstt_inspecciones():
    """API para gestionar inspecciones de seguridad"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        if request.method == 'GET':
            # Obtener inspecciones con filtros opcionales
            fecha_desde = request.args.get('fecha_desde')
            fecha_hasta = request.args.get('fecha_hasta')
            estado = request.args.get('estado')
            
            query = """
                SELECT i.*, tr.nombre_riesgo, ro.nombre as inspector_nombre
                FROM sstt_inspecciones i
                LEFT JOIN sstt_tipos_riesgo tr ON i.tipo_riesgo_id = tr.id
                LEFT JOIN recurso_operativo ro ON i.usuario_creador = ro.id_codigo_consumidor
                WHERE 1=1
            """
            params = []
            
            if fecha_desde:
                query += " AND i.fecha_inspeccion >= %s"
                params.append(fecha_desde)
            if fecha_hasta:
                query += " AND i.fecha_inspeccion <= %s"
                params.append(fecha_hasta)
            if estado:
                query += " AND i.estado = %s"
                params.append(estado)
                
            query += " ORDER BY i.fecha_inspeccion DESC"
            
            cursor.execute(query, params)
            inspecciones = cursor.fetchall()
            
            return jsonify({'inspecciones': inspecciones})
            
        elif request.method == 'POST':
            # Crear nueva inspección
            data = request.get_json()
            
            cursor.execute("""
                INSERT INTO sstt_inspecciones 
                (area_inspeccionada, fecha_inspeccion, tipo_riesgo_id, descripcion, 
                 estado, usuario_creador, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (
                data['area_inspeccionada'],
                data['fecha_inspeccion'],
                data['tipo_riesgo_id'],
                data['descripcion'],
                data.get('estado', 'pendiente'),
                current_user.id
            ))
            
            connection.commit()
            inspeccion_id = cursor.lastrowid
            
            return jsonify({
                'success': True, 
                'message': 'Inspección creada exitosamente',
                'inspeccion_id': inspeccion_id
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/sstt/usuarios', methods=['GET'])
@login_required
def api_sstt_usuarios():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        q = (request.args.get('q') or '').strip()
        limit_param = request.args.get('limit')
        try:
            limit = int(limit_param) if limit_param else 50
        except Exception:
            limit = 50
        solo_activos_param = (request.args.get('solo_activos') or '1').strip().lower()
        solo_activos = solo_activos_param in ['1', 'true', 't', 'yes', 'y']
        where = []
        params = []
        if solo_activos:
            where.append("estado = 'Activo'")
        if q:
            where.append("(recurso_operativo_cedula LIKE %s OR nombre LIKE %s)")
            like = f"%{q}%"
            params.extend([like, like])
        sql = "SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, id_roles, estado FROM recurso_operativo"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY nombre ASC LIMIT %s"
        params.append(limit)
        try:
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall() or []
        except Exception:
            sql_fb = (
                'SELECT '
                'ro.recurso_operativo_cedula AS cedula, '
                'ro.nombre AS nombre, '
                '(SELECT COUNT(*) FROM sstt_vencimientos_cursos vcX WHERE vcX.recurso_operativo_cedula = ro.recurso_operativo_cedula) AS total_cursos, '
                '('
                    'SELECT COUNT(*) FROM sstt_vencimientos_cursos vc '
                    'WHERE vc.recurso_operativo_cedula = ro.recurso_operativo_cedula '
                      'AND vc.sstt_vencimientos_cursos_fecha_ven IS NOT NULL '
                      "AND vc.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') "
                      "AND vc.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' "
                      'AND DATE(vc.sstt_vencimientos_cursos_fecha_ven) <= CURDATE() '
                      'AND (vc.sstt_vencimientos_cursos_validado IS NULL OR vc.sstt_vencimientos_cursos_validado = 0) '
                      'AND (vc.sstt_vencimientos_cursos_pendiente IS NULL OR vc.sstt_vencimientos_cursos_pendiente = 0) '
                      'AND NOT EXISTS ('
                          'SELECT 1 FROM sstt_vencimientos_cursos vc2 '
                          'WHERE vc2.recurso_operativo_cedula = vc.recurso_operativo_cedula '
                            'AND vc2.sstt_vencimientos_cursos_tipo_curso = vc.sstt_vencimientos_cursos_tipo_curso '
                            'AND vc2.sstt_vencimientos_cursos_fecha_ven IS NOT NULL '
                            "AND vc2.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') "
                            "AND vc2.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' "
                            'AND DATE(vc2.sstt_vencimientos_cursos_fecha_ven) > CURDATE() '
                            'AND DATEDIFF(vc2.sstt_vencimientos_cursos_fecha_ven, CURDATE()) > 30'
                      ') '
                      'AND ('
                          "vc.sstt_vencimientos_cursos_tipo_curso <> 'EXAMEN MEDICO INGRESO' "
                          'OR NOT EXISTS ('
                              'SELECT 1 FROM sstt_vencimientos_cursos vcP '
                              'WHERE vcP.recurso_operativo_cedula = ro.recurso_operativo_cedula '
                                "AND vcP.sstt_vencimientos_cursos_tipo_curso = 'EXAMEN MEDICO PERIODICO' "
                                'AND vcP.sstt_vencimientos_cursos_fecha_ven IS NOT NULL '
                                "AND vcP.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') "
                                "AND vcP.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' "
                                'AND DATEDIFF(vcP.sstt_vencimientos_cursos_fecha_ven, CURDATE()) > 30'
                          ')'
                      ')'
                ') AS vencidos, '
                '('
                    'SELECT COUNT(*) FROM sstt_vencimientos_cursos vc '
                    'WHERE vc.recurso_operativo_cedula = ro.recurso_operativo_cedula '
                      'AND vc.sstt_vencimientos_cursos_fecha_ven IS NOT NULL '
                      "AND vc.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') "
                      "AND vc.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' "
                      'AND DATE(vc.sstt_vencimientos_cursos_fecha_ven) > CURDATE() '
                      'AND DATEDIFF(vc.sstt_vencimientos_cursos_fecha_ven, CURDATE()) <= 30 '
                      'AND (vc.sstt_vencimientos_cursos_validado IS NULL OR vc.sstt_vencimientos_cursos_validado = 0) '
                      'AND (vc.sstt_vencimientos_cursos_pendiente IS NULL OR vc.sstt_vencimientos_cursos_pendiente = 0) '
                      'AND NOT EXISTS ('
                          'SELECT 1 FROM sstt_vencimientos_cursos vc2 '
                          'WHERE vc2.recurso_operativo_cedula = vc.recurso_operativo_cedula '
                            'AND vc2.sstt_vencimientos_cursos_tipo_curso = vc.sstt_vencimientos_cursos_tipo_curso '
                            'AND vc2.sstt_vencimientos_cursos_fecha_ven IS NOT NULL '
                            "AND vc2.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') "
                            "AND vc2.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' "
                            'AND DATE(vc2.sstt_vencimientos_cursos_fecha_ven) > CURDATE() '
                            'AND DATEDIFF(vc2.sstt_vencimientos_cursos_fecha_ven, CURDATE()) > 30'
                      ') '
                      'AND ('
                          "vc.sstt_vencimientos_cursos_tipo_curso <> 'EXAMEN MEDICO INGRESO' "
                          'OR NOT EXISTS ('
                              'SELECT 1 FROM sstt_vencimientos_cursos vcP '
                              'WHERE vcP.recurso_operativo_cedula = ro.recurso_operativo_cedula '
                                "AND vcP.sstt_vencimientos_cursos_tipo_curso = 'EXAMEN MEDICO PERIODICO' "
                                'AND vcP.sstt_vencimientos_cursos_fecha_ven IS NOT NULL '
                                "AND vcP.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') "
                                "AND vcP.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' "
                                'AND DATE(vcP.sstt_vencimientos_cursos_fecha_ven) >= CURDATE()'
                          ')'
                      ')'
                ') AS por_vencer '
                'FROM recurso_operativo ro '
            )
            if where:
                sql_fb += ' WHERE ' + ' AND '.join(where)
            sql_fb += ' ORDER BY ro.nombre ASC'
            cursor.execute(sql_fb, tuple(params))
            rows = cursor.fetchall() or []
        data = [{
            'id_codigo_consumidor': r.get('id_codigo_consumidor'),
            'cedula': r.get('recurso_operativo_cedula'),
            'nombre': r.get('nombre'),
            'id_roles': r.get('id_roles'),
            'estado': r.get('estado')
        } for r in rows]
        cursor.close(); connection.close()
        return jsonify({'success': True, 'data': data, 'total': len(data)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sstt/tecnicos', methods=['GET'])
@login_required
def api_sstt_tecnicos():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        q = (request.args.get('q') or '').strip()
        limit_param = request.args.get('limit')
        try:
            limit = int(limit_param) if limit_param else 50
        except Exception:
            limit = 50
        where = ["estado = 'Activo'", "id_roles = 2"]
        params = []
        if q:
            where.append("(recurso_operativo_cedula LIKE %s OR nombre LIKE %s)")
            like = f"%{q}%"
            params.extend([like, like])
        sql = (
            "SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre "
            "FROM recurso_operativo"
        )
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY nombre ASC LIMIT %s"
        params.append(limit)
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall() or []
        data = [{
            'id_codigo_consumidor': r.get('id_codigo_consumidor'),
            'cedula': r.get('recurso_operativo_cedula'),
            'nombre': r.get('nombre')
        } for r in rows]
        cursor.close(); connection.close()
        return jsonify({'success': True, 'data': data, 'total': len(data)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sstt/vencimientos-cursos', methods=['GET', 'POST'])
@login_required_api()
def api_sstt_vencimientos_cursos():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sstt_vencimientos_cursos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_codigo_consumidor INT NOT NULL,
                sstt_vencimientos_cursos_nombre VARCHAR(200),
                recurso_operativo_cedula VARCHAR(20),
                sstt_vencimientos_cursos_tipo_curso VARCHAR(100) NOT NULL,
                sstt_vencimientos_cursos_fecha DATE NOT NULL,
                sstt_vencimientos_cursos_fecha_ven DATE NOT NULL,
                sstt_vencimientos_cursos_observacion TEXT,
                sstt_vencimientos_cursos_validado TINYINT(1) DEFAULT 0,
                sstt_vencimientos_cursos_fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_cedula (recurso_operativo_cedula),
                INDEX idx_tipo (sstt_vencimientos_cursos_tipo_curso),
                INDEX idx_fecha_ven (sstt_vencimientos_cursos_fecha_ven)
            )
            """
        )
        if request.method == 'GET':
            cedula = (request.args.get('cedula') or '').strip()
            tipo = (request.args.get('tipo') or '').strip()
            fecha_desde = (request.args.get('fecha_desde') or '').strip()
            fecha_hasta = (request.args.get('fecha_hasta') or '').strip()
            solo_activos_param = (request.args.get('solo_activos') or '1').strip().lower()
            solo_activos = solo_activos_param in ['1', 'true', 't', 'yes', 'y']
            params = []
            where = []
            try:
                cur_check = connection.cursor()
                cur_check.execute("SHOW COLUMNS FROM sstt_vencimientos_cursos LIKE 'id'")
                has_id = bool(cur_check.fetchone())
                cur_check.close()
                if not has_id:
                    try:
                        cur_pk = connection.cursor()
                        cur_pk.execute("SHOW KEYS FROM sstt_vencimientos_cursos WHERE Key_name = 'PRIMARY'")
                        has_pk = bool(cur_pk.fetchone())
                        cur_pk.close()
                        cur_alter = connection.cursor()
                        if has_pk:
                            cur_alter.execute("ALTER TABLE sstt_vencimientos_cursos ADD COLUMN id INT NOT NULL AUTO_INCREMENT FIRST")
                            cur_alter.execute("ALTER TABLE sstt_vencimientos_cursos ADD UNIQUE KEY idx_sstt_vc_id (id)")
                        else:
                            cur_alter.execute("ALTER TABLE sstt_vencimientos_cursos ADD COLUMN id INT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST")
                        connection.commit()
                        cur_alter.close()
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                cur_check2 = connection.cursor()
                cur_check2.execute(
                    """
                    SELECT COUNT(*) FROM information_schema.columns
                    WHERE table_schema = DATABASE()
                      AND table_name = 'sstt_vencimientos_cursos'
                      AND column_name = 'sstt_vencimientos_cursos_validado'
                    """
                )
                has_validado = (cur_check2.fetchone() or [0])[0]
                cur_check2.close()
                if not has_validado:
                    try:
                        cur_alter2 = connection.cursor()
                        cur_alter2.execute("ALTER TABLE sstt_vencimientos_cursos ADD COLUMN sstt_vencimientos_cursos_validado TINYINT(1) DEFAULT 0 AFTER sstt_vencimientos_cursos_observacion")
                        connection.commit()
                        cur_alter2.close()
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                cur_check_p = connection.cursor()
                cur_check_p.execute(
                    """
                    SELECT COUNT(*) FROM information_schema.columns
                    WHERE table_schema = DATABASE()
                      AND table_name = 'sstt_vencimientos_cursos'
                      AND column_name = 'sstt_vencimientos_cursos_pendiente'
                    """
                )
                has_pendiente = (cur_check_p.fetchone() or [0])[0]
                cur_check_p.close()
                if not has_pendiente:
                    try:
                        cur_alter_p = connection.cursor()
                        cur_alter_p.execute("ALTER TABLE sstt_vencimientos_cursos ADD COLUMN sstt_vencimientos_cursos_pendiente TINYINT(1) NOT NULL DEFAULT 0 AFTER sstt_vencimientos_cursos_observacion")
                        connection.commit()
                        cur_alter_p.close()
                    except Exception:
                        pass
            except Exception:
                pass
            if cedula:
                where.append("vc.recurso_operativo_cedula = %s")
                params.append(cedula)
            if tipo:
                where.append("vc.sstt_vencimientos_cursos_tipo_curso = %s")
                params.append(tipo)
            if fecha_desde:
                where.append("vc.sstt_vencimientos_cursos_fecha >= %s")
                params.append(fecha_desde)
            if fecha_hasta:
                where.append("vc.sstt_vencimientos_cursos_fecha <= %s")
                params.append(fecha_hasta)
            select_id_prefix = "vc.id AS id, " if has_id else "NULL AS id, "
            sql = (
                "SELECT " + select_id_prefix + "vc.id_codigo_consumidor, vc.sstt_vencimientos_cursos_nombre, "
                "vc.recurso_operativo_cedula, vc.sstt_vencimientos_cursos_tipo_curso, "
                "vc.sstt_vencimientos_cursos_fecha, vc.sstt_vencimientos_cursos_fecha_ven, "
                "vc.sstt_vencimientos_cursos_observacion, vc.sstt_vencimientos_cursos_validado, vc.sstt_vencimientos_cursos_pendiente "
                "FROM sstt_vencimientos_cursos vc "
                "LEFT JOIN recurso_operativo ro ON vc.recurso_operativo_cedula = ro.recurso_operativo_cedula"
            )
            if solo_activos:
                where.append("ro.estado = 'Activo'")
            if where:
                sql += " WHERE " + " AND ".join(where)
            sql += " ORDER BY vc.sstt_vencimientos_cursos_fecha_ven ASC"
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall() or []
            hoy = date.today()
            out = []
            for r in rows:
                f = r.get('sstt_vencimientos_cursos_fecha')
                fv = r.get('sstt_vencimientos_cursos_fecha_ven')
                fv_date = None
                try:
                    if fv:
                        if hasattr(fv, 'strftime'):
                            fv_date = fv
                        else:
                            s = str(fv).strip()
                            if s:
                                try:
                                    fv_date = datetime.strptime(s, '%Y-%m-%d').date()
                                except Exception:
                                    try:
                                        fv_date = datetime.strptime(s, '%Y-%m-%d %H:%M:%S').date()
                                    except Exception:
                                        fv_date = None
                except Exception:
                    fv_date = None
                def _fmt_date(val):
                    try:
                        if not val:
                            return ''
                        if hasattr(val, 'strftime'):
                            return val.strftime('%Y-%m-%d')
                        s = str(val).strip()
                        if not s:
                            return ''
                        try:
                            dt = datetime.strptime(s, '%Y-%m-%d')
                            return dt.strftime('%Y-%m-%d')
                        except Exception:
                            try:
                                dt = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
                                return dt.strftime('%Y-%m-%d')
                            except Exception:
                                parts = s.split('-')
                                if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit():
                                    y = parts[0]; m = parts[1].zfill(2); d = parts[2].zfill(2)
                                    return f"{y}-{m}-{d}"
                                return s
                    except Exception:
                        return ''
                f_str = _fmt_date(f)
                fv_str = _fmt_date(fv)
                dias = (fv_date - hoy).days if fv_date else None
                try:
                    pend_val = int(r.get('sstt_vencimientos_cursos_pendiente') or 0)
                except Exception:
                    pend_val = 0
                if pend_val == 1:
                    f_str = ''
                    fv_str = ''
                    fv_date = None
                    dias = None
                anio_val = None
                try:
                    if f_str and len(f_str) >= 4 and f_str[0:4].isdigit():
                        anio_val = int(f_str[0:4])
                except Exception:
                    anio_val = None
                out.append({
                    'id': r.get('id'),
                    'recurso_operativo_cedula': r.get('recurso_operativo_cedula'),
                    'nombre': r.get('sstt_vencimientos_cursos_nombre'),
                    'tipo_curso': r.get('sstt_vencimientos_cursos_tipo_curso'),
                    'fecha': f_str,
                    'fecha_vencimiento': fv_str,
                    'dias_por_vencer': dias,
                    'observacion': r.get('sstt_vencimientos_cursos_observacion'),
                    'anio': anio_val,
                    'validado': r.get('sstt_vencimientos_cursos_validado'),
                    'pendiente': pend_val
                })

            # Integración de encuesta 10 por usuario (por año presente)
            if cedula:
                cur_user = connection.cursor(dictionary=True)
                cur_user.execute("SELECT id_codigo_consumidor, nombre, estado FROM recurso_operativo WHERE recurso_operativo_cedula = %s", (cedula,))
                ru = cur_user.fetchone()
                cur_user.close()
                if ru and (not solo_activos or str(ru.get('estado') or '') == 'Activo'):
                    idc = ru.get('id_codigo_consumidor')
                    nombre_u = ru.get('nombre')
                    cur_enc = connection.cursor(dictionary=True)
                    try:
                        try:
                            cur_chk_enc = connection.cursor()
                            cur_chk_enc.execute(
                                """
                                SELECT COUNT(*) FROM information_schema.columns
                                WHERE table_schema = DATABASE() AND table_name = 'encuesta_respuestas' AND column_name = 'sstt_vencimientos_cursos_fecha_ven'
                                """
                            )
                            has_er_col = (cur_chk_enc.fetchone() or [0])[0]
                            cur_chk_enc.close()
                            if not has_er_col:
                                cur_alt_enc = connection.cursor()
                                try:
                                    cur_alt_enc.execute("ALTER TABLE encuesta_respuestas ADD COLUMN sstt_vencimientos_cursos_fecha_ven DATE NULL AFTER fecha_respuesta")
                                    connection.commit()
                                except Exception:
                                    pass
                                finally:
                                    cur_alt_enc.close()
                        except Exception:
                            pass
                        cur_enc.execute(
                            """
                            SELECT DATE(fecha_respuesta) AS fecha, sstt_vencimientos_cursos_fecha_ven AS fecha_ven
                            FROM encuesta_respuestas
                            WHERE encuesta_id = %s AND usuario_id = %s AND estado IN ('enviada','respondida','finalizada') AND YEAR(fecha_respuesta) = YEAR(CURDATE())
                            ORDER BY fecha_respuesta DESC
                            LIMIT 1
                            """,
                            (10, idc)
                        )
                        er = cur_enc.fetchone()
                    except Exception:
                        er = None
                    finally:
                        cur_enc.close()
                    if er:
                        fecha_enc = er.get('fecha')
                        fecha_ven_enc = er.get('fecha_ven')
                        has_induccion = any(('INDUCCION' in str(i.get('tipo_curso') or '').strip().upper().replace('Ó','O').replace('Ú','U').replace('Á','A').replace('É','E').replace('Í','I').replace('Ñ','N')) for i in out)
                        enc_year = None
                        try:
                            if hasattr(fecha_enc, 'year'):
                                enc_year = int(fecha_enc.year)
                            else:
                                s = str(fecha_enc)
                                enc_year = int(s[0:4]) if len(s) >= 4 and s[0:4].isdigit() else None
                        except Exception:
                            enc_year = None
                        has_reinduccion_same_year = any(('REINDUCCION' in str(i.get('tipo_curso') or '').strip().upper().replace('Ó','O').replace('Ú','U').replace('Á','A').replace('É','E').replace('Í','I').replace('Ñ','N')) and (i.get('anio') == enc_year) for i in out)
                        fv_date_enc = None
                        fv_str_enc = ''
                        try:
                            if fecha_ven_enc:
                                if hasattr(fecha_ven_enc, 'strftime'):
                                    fv_date_enc = fecha_ven_enc
                                    fv_str_enc = fecha_ven_enc.strftime('%Y-%m-%d')
                                else:
                                    s = str(fecha_ven_enc).strip()
                                    if s:
                                        try:
                                            fv_date_enc = datetime.strptime(s, '%Y-%m-%d').date()
                                            fv_str_enc = fv_date_enc.strftime('%Y-%m-%d')
                                        except Exception:
                                            try:
                                                fv_date_enc = datetime.strptime(s, '%Y-%m-%d %H:%M:%S').date()
                                                fv_str_enc = fv_date_enc.strftime('%Y-%m-%d')
                                            except Exception:
                                                fv_date_enc = None
                                                fv_str_enc = ''
                        except Exception:
                            fv_date_enc = None
                            fv_str_enc = ''
                        dias_enc = (fv_date_enc - hoy).days if fv_date_enc else None
                        synthetic_item = {
                            'recurso_operativo_cedula': cedula,
                            'nombre': nombre_u,
                            'tipo_curso': ('CURSO INDUCCION SST' if not has_induccion else 'CURSO REINDUCCION SST'),
                            'fecha': (fecha_enc.strftime('%Y-%m-%d') if hasattr(fecha_enc, 'strftime') else str(fecha_enc)),
                            'fecha_vencimiento': fv_str_enc,
                            'dias_por_vencer': dias_enc,
                            'observacion': 'Origen: Encuesta 10',
                            'anio': enc_year
                        }
                        if not has_induccion:
                            out.append(synthetic_item)
                        elif not has_reinduccion_same_year:
                            out.append(synthetic_item)

            cursor.close(); connection.close()
            return jsonify({'success': True, 'data': out, 'total': len(out)})
        else:
            data = request.get_json() or {}
            cedula = (data.get('recurso_operativo_cedula') or '').strip()
            tipo = (data.get('sstt_vencimientos_cursos_tipo_curso') or '').strip()
            fecha = (data.get('sstt_vencimientos_cursos_fecha') or '').strip()
            fecha_ven = (data.get('sstt_vencimientos_cursos_fecha_ven') or '').strip()
            pendiente_val_pre = data.get('sstt_vencimientos_cursos_pendiente')
            try:
                p_int_pre = 1 if str(pendiente_val_pre).strip().lower() in ['1','true','t','yes','y'] else 0
            except Exception:
                p_int_pre = 0
            observ = (data.get('sstt_vencimientos_cursos_observacion') or ('Pendiente' if p_int_pre == 1 else '')).strip()
            if not cedula or not tipo or (p_int_pre != 1 and (not fecha or not fecha_ven)):
                cursor.close(); connection.close()
                return jsonify({'success': False, 'message': 'Campos requeridos faltantes'}), 400
            cur2 = connection.cursor()
            cur2.execute("SELECT id_codigo_consumidor, nombre FROM recurso_operativo WHERE recurso_operativo_cedula = %s", (cedula,))
            ru = cur2.fetchone()
            if not ru:
                cur2.close(); cursor.close(); connection.close()
                return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
            idc = ru[0]
            nombre = ru[1]
            cur2.close()
            pendiente_val = pendiente_val_pre
            p_int = p_int_pre
            fecha_val = (fecha if fecha else None)
            fecha_ven_val = (fecha_ven if fecha_ven else None)
            try:
                cur_null = connection.cursor()
                cur_null.execute(
                    """
                    SELECT IS_NULLABLE FROM information_schema.columns
                    WHERE table_schema = DATABASE() AND table_name = 'sstt_vencimientos_cursos' AND column_name = 'sstt_vencimientos_cursos_fecha'
                    """
                )
                res_f = cur_null.fetchone()
                if res_f and str(res_f[0]).upper() == 'NO':
                    cur_alter_f = connection.cursor()
                    cur_alter_f.execute("ALTER TABLE sstt_vencimientos_cursos MODIFY COLUMN sstt_vencimientos_cursos_fecha DATE NULL DEFAULT NULL")
                    connection.commit()
                    cur_alter_f.close()
                cur_null.execute(
                    """
                    SELECT IS_NULLABLE FROM information_schema.columns
                    WHERE table_schema = DATABASE() AND table_name = 'sstt_vencimientos_cursos' AND column_name = 'sstt_vencimientos_cursos_fecha_ven'
                    """
                )
                res_v = cur_null.fetchone()
                if res_v and str(res_v[0]).upper() == 'NO':
                    cur_alter_v = connection.cursor()
                    cur_alter_v.execute("ALTER TABLE sstt_vencimientos_cursos MODIFY COLUMN sstt_vencimientos_cursos_fecha_ven DATE NULL DEFAULT NULL")
                    connection.commit()
                    cur_alter_v.close()
                cur_null.close()
            except Exception:
                pass
            cursor.execute(
                """
                INSERT INTO sstt_vencimientos_cursos (
                    id_codigo_consumidor,
                    sstt_vencimientos_cursos_nombre,
                    recurso_operativo_cedula,
                    sstt_vencimientos_cursos_tipo_curso,
                    sstt_vencimientos_cursos_fecha,
                    sstt_vencimientos_cursos_fecha_ven,
                    sstt_vencimientos_cursos_observacion
                ) VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (idc, nombre, cedula, tipo, fecha_val, fecha_ven_val, observ)
            )
            connection.commit()
            new_id = cursor.lastrowid
            if p_int == 1:
                curp = connection.cursor()
                try:
                    curp.execute("UPDATE sstt_vencimientos_cursos SET sstt_vencimientos_cursos_pendiente = 1 WHERE id = %s", (new_id,))
                    connection.commit()
                except Exception:
                    pass
                finally:
                    curp.close()
            tipo_cmp = str(tipo).strip().upper().replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ü','U').replace('Ñ','N')
            if tipo_cmp == 'EXAMEN MEDICO PERIODICO':
                try:
                    cur_check = connection.cursor()
                    cur_check.execute(
                        """
                        SELECT COUNT(*) FROM information_schema.columns
                        WHERE table_schema = DATABASE()
                          AND table_name = 'sstt_vencimientos_cursos'
                          AND column_name = 'sstt_vencimientos_cursos_validado'
                        """
                    )
                    has_val = (cur_check.fetchone() or [0])[0]
                    cur_check.close()
                    if not has_val:
                        cur_alter = connection.cursor()
                        try:
                            cur_alter.execute("ALTER TABLE sstt_vencimientos_cursos ADD COLUMN sstt_vencimientos_cursos_validado TINYINT(1) DEFAULT 0 AFTER sstt_vencimientos_cursos_observacion")
                            connection.commit()
                        except Exception:
                            pass
                        finally:
                            cur_alter.close()
                except Exception:
                    pass
                cur_auto = connection.cursor()
                try:
                    cur_auto.execute(
                        """
                        UPDATE sstt_vencimientos_cursos
                        SET sstt_vencimientos_cursos_validado = 1
                        WHERE TRIM(recurso_operativo_cedula) = %s
                          AND TRIM(sstt_vencimientos_cursos_tipo_curso) = 'EXAMEN MEDICO INGRESO'
                        """,
                        (cedula,)
                    )
                    connection.commit()
                except Exception:
                    pass
                finally:
                    cur_auto.close()
            cursor.close(); connection.close()
            return jsonify({'success': True, 'id': new_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sstt/vencimientos-cursos/<int:item_id>', methods=['PUT'])
@login_required_api()
def api_sstt_vencimientos_cursos_update(item_id):
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        data = request.get_json() or {}
        cedula = (data.get('recurso_operativo_cedula') or '').strip()
        tipo = (data.get('sstt_vencimientos_cursos_tipo_curso') or '').strip()
        fecha = (data.get('sstt_vencimientos_cursos_fecha') or '').strip()
        fecha_ven = (data.get('sstt_vencimientos_cursos_fecha_ven') or '').strip()
        observ = (data.get('sstt_vencimientos_cursos_observacion') or '').strip()
        validado_val = data.get('sstt_vencimientos_cursos_validado')
        pendiente_val = data.get('sstt_vencimientos_cursos_pendiente')
        pendiente_val = data.get('sstt_vencimientos_cursos_pendiente')
        campos = []
        params = []
        idc = None
        nombre = None
        if cedula:
            cur2 = connection.cursor()
            cur2.execute("SELECT id_codigo_consumidor, nombre FROM recurso_operativo WHERE recurso_operativo_cedula = %s", (cedula,))
            ru = cur2.fetchone()
            cur2.close()
            if ru:
                idc = ru[0]
                nombre = ru[1]
        if idc is not None:
            campos.append("id_codigo_consumidor = %s")
            params.append(idc)
        if nombre is not None:
            campos.append("sstt_vencimientos_cursos_nombre = %s")
            params.append(nombre)
        if cedula:
            campos.append("recurso_operativo_cedula = %s")
            params.append(cedula)
        if tipo:
            campos.append("sstt_vencimientos_cursos_tipo_curso = %s")
            params.append(tipo)
        if fecha:
            campos.append("sstt_vencimientos_cursos_fecha = %s")
            params.append(fecha)
        if fecha_ven:
            campos.append("sstt_vencimientos_cursos_fecha_ven = %s")
            params.append(fecha_ven)
        campos.append("sstt_vencimientos_cursos_observacion = %s")
        params.append(observ)
        try:
            cur_check3 = connection.cursor()
            cur_check3.execute(
            	"""
            	SELECT COUNT(*) FROM information_schema.columns
            	WHERE table_schema = DATABASE()
            	  AND table_name = 'sstt_vencimientos_cursos'
            	  AND column_name = 'sstt_vencimientos_cursos_pendiente'
            	"""
            )
            has_pend2 = (cur_check3.fetchone() or [0])[0]
            cur_check3.close()
        except Exception:
            has_pend2 = 0
        if pendiente_val is not None and has_pend2:
            try:
                p2_int = 1 if str(pendiente_val).strip().lower() in ['1','true','t','yes','y'] else 0
            except Exception:
                p2_int = 0
            campos.append("sstt_vencimientos_cursos_pendiente = %s")
            params.append(p2_int)
        try:
            cur_check_v = connection.cursor()
            cur_check_v.execute(
            	"""
            	SELECT COUNT(*) FROM information_schema.columns
            	WHERE table_schema = DATABASE()
            	  AND table_name = 'sstt_vencimientos_cursos'
            	  AND column_name = 'sstt_vencimientos_cursos_validado'
            	"""
            )
            has_valid2 = (cur_check_v.fetchone() or [0])[0]
            cur_check_v.close()
        except Exception:
            has_valid2 = 0
        if validado_val is not None and has_valid2:
            try:
                v_int = 1 if str(validado_val).strip().lower() in ['1', 'true', 't', 'yes', 'y'] else 0
            except Exception:
                v_int = 0
            campos.append("sstt_vencimientos_cursos_validado = %s")
            params.append(v_int)
        if not campos:
            connection.close()
            return jsonify({'success': False, 'message': 'Sin cambios'}), 400
        sql = "UPDATE sstt_vencimientos_cursos SET " + ", ".join(campos) + " WHERE id = %s"
        params.append(item_id)
        cur = connection.cursor()
        cur.execute(sql, tuple(params))
        connection.commit()
        cur.close(); connection.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sstt/vencimientos-cursos/<int:item_id>', methods=['DELETE'])
@login_required_api()
def api_sstt_vencimientos_cursos_delete(item_id):
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cur = connection.cursor()
        cur.execute("DELETE FROM sstt_vencimientos_cursos WHERE id = %s", (item_id,))
        connection.commit()
        affected = cur.rowcount
        cur.close(); connection.close()
        if affected == 0:
            return jsonify({'success': False, 'message': 'Registro no encontrado'}), 404
        return jsonify({'success': True, 'deleted': affected})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sstt/vencimientos-cursos/delete-by', methods=['DELETE'])
@login_required_api()
def api_sstt_vencimientos_cursos_delete_by():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        data = request.get_json() or {}
        oc = (data.get('original_cedula') or '').strip()
        ot = (data.get('original_tipo') or '').strip()
        of = (data.get('original_fecha') or '').strip()
        if not oc or not ot or not of:
            connection.close()
            return jsonify({'success': False, 'message': 'Faltan claves originales'}), 400
        cur = connection.cursor()
        sql1 = "DELETE FROM sstt_vencimientos_cursos WHERE recurso_operativo_cedula = %s AND sstt_vencimientos_cursos_tipo_curso = %s AND sstt_vencimientos_cursos_fecha = %s LIMIT 1"
        params1 = (oc, ot, of)
        cur.execute(sql1, params1)
        connection.commit()
        affected = cur.rowcount
        if affected == 0:
            sql2 = "DELETE FROM sstt_vencimientos_cursos WHERE recurso_operativo_cedula = %s AND sstt_vencimientos_cursos_tipo_curso = %s AND DATE(sstt_vencimientos_cursos_fecha) = %s LIMIT 1"
            params2 = (oc, ot, of)
            cur.execute(sql2, params2)
            connection.commit()
            affected = cur.rowcount
        if affected == 0:
            sql3 = "DELETE FROM sstt_vencimientos_cursos WHERE TRIM(recurso_operativo_cedula) = %s AND TRIM(sstt_vencimientos_cursos_tipo_curso) = %s AND DATE(sstt_vencimientos_cursos_fecha) = %s LIMIT 1"
            params3 = (oc, ot, of)
            cur.execute(sql3, params3)
            connection.commit()
            affected = cur.rowcount
        cur.close(); connection.close()
        if affected == 0:
            return jsonify({'success': False, 'message': 'No se encontró registro para eliminar'}), 404
        return jsonify({'success': True, 'deleted': affected})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sstt/vencimientos-cursos/update-by', methods=['PUT'])
@login_required_api()
def api_sstt_vencimientos_cursos_update_by():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        data = request.get_json() or {}
        oc = (data.get('original_cedula') or '').strip()
        ot = (data.get('original_tipo') or '').strip()
        of = (data.get('original_fecha') or '').strip()
        cedula = (data.get('recurso_operativo_cedula') or '').strip()
        tipo = (data.get('sstt_vencimientos_cursos_tipo_curso') or '').strip()
        fecha = (data.get('sstt_vencimientos_cursos_fecha') or '').strip()
        fecha_ven = (data.get('sstt_vencimientos_cursos_fecha_ven') or '').strip()
        observ = (data.get('sstt_vencimientos_cursos_observacion') or '').strip()
        validado_val = data.get('sstt_vencimientos_cursos_validado')
        if not oc or not ot or not of:
            connection.close()
            return jsonify({'success': False, 'message': 'Faltan claves originales'}), 400
        cur2 = connection.cursor()
        cur2.execute("SELECT id_codigo_consumidor, nombre FROM recurso_operativo WHERE recurso_operativo_cedula = %s", (cedula,))
        ru = cur2.fetchone()
        cur2.close()
        idc = ru[0] if ru else None
        nombre = ru[1] if ru else None
        params_set = []
        set_parts = []
        if idc is not None:
            set_parts.append("id_codigo_consumidor = %s")
            params_set.append(idc)
        if nombre is not None:
            set_parts.append("sstt_vencimientos_cursos_nombre = %s")
            params_set.append(nombre)
        fecha_norm = (fecha if str(fecha).strip() else None)
        fecha_ven_norm = (fecha_ven if str(fecha_ven).strip() else None)
        if cedula:
            set_parts.append("recurso_operativo_cedula = %s")
            params_set.append(cedula)
        if tipo:
            set_parts.append("sstt_vencimientos_cursos_tipo_curso = %s")
            params_set.append(tipo)
        if fecha_norm is not None:
            set_parts.append("sstt_vencimientos_cursos_fecha = %s")
            params_set.append(fecha_norm)
        if fecha_ven_norm is not None:
            set_parts.append("sstt_vencimientos_cursos_fecha_ven = %s")
            params_set.append(fecha_ven_norm)
        try:
            cur_chk_obs = connection.cursor()
            cur_chk_obs.execute(
                """
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_schema = DATABASE() AND table_name = 'sstt_vencimientos_cursos' AND column_name = 'sstt_vencimientos_cursos_observacion'
                """
            )
            has_obs = (cur_chk_obs.fetchone() or [0])[0]
            cur_chk_obs.close()
        except Exception:
            has_obs = 0
        if has_obs:
            set_parts.append("sstt_vencimientos_cursos_observacion = %s")
            params_set.append(observ)
        try:
            cur_check = connection.cursor()
            cur_check.execute(
                """
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_schema = DATABASE() AND table_name = 'sstt_vencimientos_cursos' AND column_name = 'sstt_vencimientos_cursos_pendiente'
                """
            )
            has_pend = (cur_check.fetchone() or [0])[0]
            cur_check.close()
        except Exception:
            has_pend = 0
        if pendiente_val is not None and has_pend:
            try:
                p_int = 1 if str(pendiente_val).strip().lower() in ['1','true','t','yes','y'] else 0
            except Exception:
                p_int = 0
            set_parts.append("sstt_vencimientos_cursos_pendiente = %s")
            params_set.append(p_int)
        try:
            cur_check_v = connection.cursor()
            cur_check_v.execute(
                """
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_schema = DATABASE() AND table_name = 'sstt_vencimientos_cursos' AND column_name = 'sstt_vencimientos_cursos_validado'
                """
            )
            has_validado = (cur_check_v.fetchone() or [0])[0]
            cur_check_v.close()
        except Exception:
            has_validado = 0
        if validado_val is not None and has_validado:
            try:
                v_int = 1 if str(validado_val).strip().lower() in ['1', 'true', 't', 'yes', 'y'] else 0
            except Exception:
                v_int = 0
            set_parts.append("sstt_vencimientos_cursos_validado = %s")
            params_set.append(v_int)
        cur = connection.cursor()
        affected = 0
        if of:
            sql = "UPDATE sstt_vencimientos_cursos SET " + ", ".join(set_parts) + " WHERE recurso_operativo_cedula = %s AND sstt_vencimientos_cursos_tipo_curso = %s AND sstt_vencimientos_cursos_fecha = %s LIMIT 1"
            params = params_set + [oc, ot, of]
            cur.execute(sql, tuple(params))
            connection.commit()
            affected = cur.rowcount
            if affected == 0:
                sql2 = (
                    "UPDATE sstt_vencimientos_cursos SET " + ", ".join(set_parts) +
                    " WHERE recurso_operativo_cedula = %s AND sstt_vencimientos_cursos_tipo_curso = %s AND DATE(sstt_vencimientos_cursos_fecha) = %s LIMIT 1"
                )
                params2 = params_set + [oc, ot, of]
                cur.execute(sql2, tuple(params2))
                connection.commit()
                affected = cur.rowcount
            if affected == 0:
                sql3 = (
                    "UPDATE sstt_vencimientos_cursos SET " + ", ".join(set_parts) +
                    " WHERE TRIM(recurso_operativo_cedula) = %s AND TRIM(sstt_vencimientos_cursos_tipo_curso) = %s AND DATE(sstt_vencimientos_cursos_fecha) = %s LIMIT 1"
                )
                params3 = params_set + [oc, ot, of]
                cur.execute(sql3, tuple(params3))
                connection.commit()
                affected = cur.rowcount
        else:
            try:
                sqln = (
                    "UPDATE sstt_vencimientos_cursos SET " + ", ".join(set_parts) +
                    " WHERE TRIM(recurso_operativo_cedula) = %s AND TRIM(sstt_vencimientos_cursos_tipo_curso) = %s ORDER BY sstt_vencimientos_cursos_fecha DESC LIMIT 1"
                )
                paramsn = params_set + [oc, ot]
                cur.execute(sqln, tuple(paramsn))
                connection.commit()
                affected = cur.rowcount
            except Exception:
                affected = 0
            if affected == 0:
                try:
                    sqln2 = (
                        "UPDATE sstt_vencimientos_cursos SET " + ", ".join(set_parts) +
                        " WHERE TRIM(recurso_operativo_cedula) = %s AND TRIM(sstt_vencimientos_cursos_tipo_curso) = %s LIMIT 1"
                    )
                    paramsn2 = params_set + [oc, ot]
                    cur.execute(sqln2, tuple(paramsn2))
                    connection.commit()
                    affected = cur.rowcount
                except Exception:
                    affected = 0
        cur.close(); connection.close()
        if affected == 0:
            return jsonify({'success': False, 'message': 'No se encontró registro para actualizar'}), 404
        return jsonify({'success': True, 'updated': affected})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sstt/vencimientos-cursos/resumen', methods=['GET'])
@login_required_api()
def api_sstt_vencimientos_cursos_resumen():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        try:
            cur_check_v = connection.cursor()
            cur_check_v.execute(
                """
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_schema = DATABASE()
                  AND table_name = 'sstt_vencimientos_cursos'
                  AND column_name = 'sstt_vencimientos_cursos_validado'
                """
            )
            has_validado = (cur_check_v.fetchone() or [0])[0]
            cur_check_v.close()
            if not has_validado:
                cur_alter_v = connection.cursor()
                try:
                    cur_alter_v.execute("ALTER TABLE sstt_vencimientos_cursos ADD COLUMN sstt_vencimientos_cursos_validado TINYINT(1) DEFAULT 0 AFTER sstt_vencimientos_cursos_observacion")
                    connection.commit()
                except Exception:
                    pass
                finally:
                    cur_alter_v.close()
        except Exception:
            pass
        try:
            cur_check_p = connection.cursor()
            cur_check_p.execute(
                """
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_schema = DATABASE()
                  AND table_name = 'sstt_vencimientos_cursos'
                  AND column_name = 'sstt_vencimientos_cursos_pendiente'
                """
            )
            has_pendiente = (cur_check_p.fetchone() or [0])[0]
            cur_check_p.close()
            if not has_pendiente:
                cur_alter_p = connection.cursor()
                try:
                    cur_alter_p.execute("ALTER TABLE sstt_vencimientos_cursos ADD COLUMN sstt_vencimientos_cursos_pendiente TINYINT(1) NOT NULL DEFAULT 0 AFTER sstt_vencimientos_cursos_observacion")
                    connection.commit()
                except Exception:
                    pass
                finally:
                    cur_alter_p.close()
        except Exception:
            pass
        cedula = (request.args.get('cedula') or '').strip()
        q = (request.args.get('q') or '').strip()
        solo_activos_param = (request.args.get('solo_activos') or '1').strip().lower()
        solo_activos = solo_activos_param in ['1', 'true', 't', 'yes', 'y']
        where = []
        params = []
        if solo_activos:
            where.append("ro.estado = 'Activo'")
        if cedula:
            where.append('ro.recurso_operativo_cedula = %s')
            params.append(cedula)
        if q:
            where.append('(ro.recurso_operativo_cedula LIKE %s OR ro.nombre LIKE %s)')
            like = f"%{q}%"
            params.extend([like, like])
        sql = (
            'SELECT '
            'ro.recurso_operativo_cedula AS cedula, '
            'ro.nombre AS nombre, '
            'COUNT(*) AS total_cursos, '
            "SUM(CASE WHEN vc.sstt_vencimientos_cursos_fecha_ven IS NOT NULL AND vc.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') AND vc.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' AND DATE(vc.sstt_vencimientos_cursos_fecha_ven) <= CURDATE() AND (vc.sstt_vencimientos_cursos_validado IS NULL OR vc.sstt_vencimientos_cursos_validado = 0) AND (vc.sstt_vencimientos_cursos_pendiente IS NULL OR vc.sstt_vencimientos_cursos_pendiente = 0) AND NOT EXISTS (SELECT 1 FROM sstt_vencimientos_cursos vc2 WHERE vc2.recurso_operativo_cedula = vc.recurso_operativo_cedula AND vc2.sstt_vencimientos_cursos_tipo_curso = vc.sstt_vencimientos_cursos_tipo_curso AND vc2.sstt_vencimientos_cursos_fecha_ven IS NOT NULL AND vc2.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') AND vc2.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' AND DATE(vc2.sstt_vencimientos_cursos_fecha_ven) > CURDATE() AND DATEDIFF(vc2.sstt_vencimientos_cursos_fecha_ven, CURDATE()) > 30) AND (vc.sstt_vencimientos_cursos_tipo_curso <> 'EXAMEN MEDICO INGRESO' OR NOT EXISTS (SELECT 1 FROM sstt_vencimientos_cursos vcP WHERE vcP.recurso_operativo_cedula = vc.recurso_operitivo_cedula AND vcP.sstt_vencimientos_cursos_tipo_curso = 'EXAMEN MEDICO PERIODICO' AND vcP.sstt_vencimientos_cursos_fecha_ven IS NOT NULL AND vcP.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') AND vcP.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' AND DATE(vcP.sstt_vencimientos_cursos_fecha_ven) > CURDATE() AND DATEDIFF(vcP.sstt_vencimientos_cursos_fecha_ven, CURDATE()) > 30)) THEN 1 ELSE 0 END) AS vencidos, "
            "SUM(CASE WHEN vc.sstt_vencimientos_cursos_fecha_ven IS NOT NULL AND vc.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') AND vc.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' AND DATE(vc.sstt_vencimientos_cursos_fecha_ven) > CURDATE() AND DATEDIFF(vc.sstt_vencimientos_cursos_fecha_ven, CURDATE()) <= 30 AND (vc.sstt_vencimientos_cursos_validado IS NULL OR vc.sstt_vencimientos_cursos_validado = 0) AND (vc.sstt_vencimientos_cursos_pendiente IS NULL OR vc.sstt_vencimientos_cursos_pendiente = 0) AND NOT EXISTS (SELECT 1 FROM sstt_vencimientos_cursos vc2 WHERE vc2.recurso_operativo_cedula = vc.recurso_operativo_cedula AND vc2.sstt_vencimientos_cursos_tipo_curso = vc.sstt_vencimientos_cursos_tipo_curso AND vc2.sstt_vencimientos_cursos_fecha_ven IS NOT NULL AND vc2.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') AND vc2.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' AND DATE(vc2.sstt_vencimientos_cursos_fecha_ven) > CURDATE() AND DATEDIFF(vc2.sstt_vencimientos_cursos_fecha_ven, CURDATE()) > 30) AND (vc.sstt_vencimientos_cursos_tipo_curso <> 'EXAMEN MEDICO INGRESO' OR NOT EXISTS (SELECT 1 FROM sstt_vencimientos_cursos vcP WHERE vcP.recurso_operativo_cedula = vc.recurso_operativo_cedula AND vcP.sstt_vencimientos_cursos_tipo_curso = 'EXAMEN MEDICO PERIODICO' AND vcP.sstt_vencimientos_cursos_fecha_ven IS NOT NULL AND vcP.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') AND vcP.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' AND DATE(vcP.sstt_vencimientos_cursos_fecha_ven) >= CURDATE())) THEN 1 ELSE 0 END) AS por_vencer "
            'FROM recurso_operativo ro '
            'LEFT JOIN sstt_vencimientos_cursos vc ON vc.recurso_operativo_cedula = ro.recurso_operativo_cedula '
        )
        if where:
            sql += ' WHERE ' + ' AND '.join(where)
        sql += ' GROUP BY ro.recurso_operativo_cedula, ro.nombre ORDER BY ro.nombre ASC'
        rows = []
        try:
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall() or []
        except Exception:
            sql_fb = (
                'SELECT '
                'ro.recurso_operativo_cedula AS cedula, '
                'ro.nombre AS nombre, '
                '(SELECT COUNT(*) FROM sstt_vencimientos_cursos vcX WHERE vcX.recurso_operativo_cedula = ro.recurso_operativo_cedula) AS total_cursos, '
                '('
                    'SELECT COUNT(*) FROM sstt_vencimientos_cursos vc '
                    'WHERE vc.recurso_operativo_cedula = ro.recurso_operativo_cedula '
                      'AND vc.sstt_vencimientos_cursos_fecha_ven IS NOT NULL '
                      "AND vc.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') "
                      "AND vc.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' "
                      'AND DATE(vc.sstt_vencimientos_cursos_fecha_ven) <= CURDATE() '
                      'AND (vc.sstt_vencimientos_cursos_validado IS NULL OR vc.sstt_vencimientos_cursos_validado = 0) '
                      'AND (vc.sstt_vencimientos_cursos_pendiente IS NULL OR vc.sstt_vencimientos_cursos_pendiente = 0) '
                      'AND NOT EXISTS ('
                          'SELECT 1 FROM sstt_vencimientos_cursos vc2 '
                          'WHERE vc2.recurso_operativo_cedula = vc.recurso_operativo_cedula '
                            'AND vc2.sstt_vencimientos_cursos_tipo_curso = vc.sstt_vencimientos_cursos_tipo_curso '
                            'AND vc2.sstt_vencimientos_cursos_fecha_ven IS NOT NULL '
                            "AND vc2.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') "
                            "AND vc2.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' "
                            'AND DATE(vc2.sstt_vencimientos_cursos_fecha_ven) > CURDATE() '
                            'AND DATEDIFF(vc2.sstt_vencimientos_cursos_fecha_ven, CURDATE()) > 30'
                      ') '
                      'AND ('
                          "vc.sstt_vencimientos_cursos_tipo_curso <> 'EXAMEN MEDICO INGRESO' "
                          'OR NOT EXISTS ('
                              'SELECT 1 FROM sstt_vencimientos_cursos vcP '
                              'WHERE vcP.recurso_operativo_cedula = ro.recurso_operativo_cedula '
                                "AND vcP.sstt_vencimientos_cursos_tipo_curso = 'EXAMEN MEDICO PERIODICO' "
                                'AND vcP.sstt_vencimientos_cursos_fecha_ven IS NOT NULL '
                                "AND vcP.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') "
                                "AND vcP.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' "
                                'AND DATEDIFF(vcP.sstt_vencimientos_cursos_fecha_ven, CURDATE()) > 30'
                          ')'
                      ')'
                ') AS vencidos, '
                '('
                    'SELECT COUNT(*) FROM sstt_vencimientos_cursos vc '
                    'WHERE vc.recurso_operativo_cedula = ro.recurso_operativo_cedula '
                      'AND vc.sstt_vencimientos_cursos_fecha_ven IS NOT NULL '
                      "AND vc.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') "
                      "AND vc.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' "
                      'AND DATE(vc.sstt_vencimientos_cursos_fecha_ven) > CURDATE() '
                      'AND DATEDIFF(vc.sstt_vencimientos_cursos_fecha_ven, CURDATE()) <= 30 '
                      'AND (vc.sstt_vencimientos_cursos_validado IS NULL OR vc.sstt_vencimientos_cursos_validado = 0) '
                      'AND (vc.sstt_vencimientos_cursos_pendiente IS NULL OR vc.sstt_vencimientos_cursos_pendiente = 0) '
                      'AND NOT EXISTS ('
                          'SELECT 1 FROM sstt_vencimientos_cursos vc2 '
                          'WHERE vc2.recurso_operativo_cedula = vc.recurso_operativo_cedula '
                            'AND vc2.sstt_vencimientos_cursos_tipo_curso = vc.sstt_vencimientos_cursos_tipo_curso '
                            'AND vc2.sstt_vencimientos_cursos_fecha_ven IS NOT NULL '
                            "AND vc2.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') "
                            "AND vc2.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' "
                            'AND DATE(vc2.sstt_vencimientos_cursos_fecha_ven) > CURDATE() '
                            'AND DATEDIFF(vc2.sstt_vencimientos_cursos_fecha_ven, CURDATE()) > 30'
                      ') '
                      'AND ('
                          "vc.sstt_vencimientos_cursos_tipo_curso <> 'EXAMEN MEDICO INGRESO' "
                          'OR NOT EXISTS ('
                              'SELECT 1 FROM sstt_vencimientos_cursos vcP '
                              'WHERE vcP.recurso_operativo_cedula = ro.recurso_operativo_cedula '
                                "AND vcP.sstt_vencimientos_cursos_tipo_curso = 'EXAMEN MEDICO PERIODICO' "
                                'AND vcP.sstt_vencimientos_cursos_fecha_ven IS NOT NULL '
                                "AND vcP.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') "
                                "AND vcP.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' "
                                'AND DATE(vcP.sstt_vencimientos_cursos_fecha_ven) >= CURDATE()'
                          ')'
                      ')'
                ') AS por_vencer '
                'FROM recurso_operativo ro '
            )
            if where:
                sql_fb += ' WHERE ' + ' AND '.join(where)
            sql_fb += ' ORDER BY ro.nombre ASC'
            cursor.execute(sql_fb, tuple(params))
            rows = cursor.fetchall() or []
        data = [{
            'cedula': r.get('cedula'),
            'nombre': r.get('nombre'),
            'total_cursos': int(r.get('total_cursos') or 0),
            'vencidos': int(r.get('vencidos') or 0),
            'por_vencer': int(r.get('por_vencer') or 0)
        } for r in rows]
        cursor.close(); connection.close()
        return jsonify({'success': True, 'data': data, 'total': len(data)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sstt/vencimientos-cursos/export', methods=['GET'])
@login_required_api()
def api_sstt_vencimientos_cursos_export():
    try:
        connection = get_db_connection()
        if connection is None:
            return Response('Error de conexión a la base de datos', status=500)
        cursor = connection.cursor(dictionary=True)
        cedula = (request.args.get('cedula') or '').strip()
        solo_activos_param = (request.args.get('solo_activos') or '1').strip().lower()
        solo_activos = solo_activos_param in ['1', 'true', 't', 'yes', 'y']
        params = []
        emp_filters = []
        if solo_activos:
            emp_filters.append("ro.estado = 'Activo'")
        if cedula:
            emp_filters.append('ro.recurso_operativo_cedula = %s')
            params.append(cedula)
        date_cond = (
            "vc.sstt_vencimientos_cursos_fecha_ven IS NOT NULL AND "
            "vc.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') AND "
            "vc.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' AND "
            "( DATE(vc.sstt_vencimientos_cursos_fecha_ven) <= CURDATE() OR (DATE(vc.sstt_vencimientos_cursos_fecha_ven) > CURDATE() AND DATEDIFF(vc.sstt_vencimientos_cursos_fecha_ven, CURDATE()) <= 30) )"
        )
        validado_cond = "(vc.sstt_vencimientos_cursos_validado IS NULL OR vc.sstt_vencimientos_cursos_validado = 0)"
        sql = (
            'SELECT '
            'ro.recurso_operativo_cedula AS cedula, '
            'ro.nombre AS nombre, '
            'vc.sstt_vencimientos_cursos_tipo_curso AS curso, '
            "DATE(vc.sstt_vencimientos_cursos_fecha_ven) AS vencimiento "
            'FROM sstt_vencimientos_cursos vc '
            'LEFT JOIN recurso_operativo ro ON vc.recurso_operativo_cedula = ro.recurso_operativo_cedula '
        )
        filter_sql = ''
        if emp_filters:
            filter_sql += '( ' + ' AND '.join(emp_filters) + ' ) AND '
        filter_sql += '( ' + date_cond + ' AND ' + validado_cond + ' AND (vc.sstt_vencimientos_cursos_pendiente IS NULL OR vc.sstt_vencimientos_cursos_pendiente = 0) '
        filter_sql += " AND NOT EXISTS (SELECT 1 FROM sstt_vencimientos_cursos vc2 WHERE vc2.recurso_operativo_cedula = vc.recurso_operativo_cedula AND vc2.sstt_vencimientos_cursos_tipo_curso = vc.sstt_vencimientos_cursos_tipo_curso AND vc2.sstt_vencimientos_cursos_fecha_ven IS NOT NULL AND vc2.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') AND vc2.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' AND DATE(vc2.sstt_vencimientos_cursos_fecha_ven) > CURDATE() AND DATEDIFF(vc2.sstt_vencimientos_cursos_fecha_ven, CURDATE()) > 30) "
        filter_sql += " AND (vc.sstt_vencimientos_cursos_tipo_curso <> 'EXAMEN MEDICO INGRESO' OR NOT EXISTS (SELECT 1 FROM sstt_vencimientos_cursos vcP WHERE vcP.recurso_operativo_cedula = vc.recurso_operitivo_cedula AND vcP.sstt_vencimientos_cursos_tipo_curso = 'EXAMEN MEDICO PERIODICO' AND vcP.sstt_vencimientos_cursos_fecha_ven IS NOT NULL AND vcP.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') AND vcP.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' AND DATE(vcP.sstt_vencimientos_cursos_fecha_ven) > CURDATE() AND DATEDIFF(vcP.sstt_vencimientos_cursos_fecha_ven, CURDATE()) > 30)) )"
        filter_sql = ''
        if emp_filters:
            filter_sql += '( ' + ' AND '.join(emp_filters) + ' ) AND '
        filter_sql += '( ' + date_cond + ' AND ' + validado_cond + ' AND (vc.sstt_vencimientos_cursos_pendiente IS NULL OR vc.sstt_vencimientos_cursos_pendiente = 0) '
        filter_sql += " AND NOT EXISTS (SELECT 1 FROM sstt_vencimientos_cursos vc2 WHERE vc2.recurso_operativo_cedula = vc.recurso_operativo_cedula AND vc2.sstt_vencimientos_cursos_tipo_curso = vc.sstt_vencimientos_cursos_tipo_curso AND vc2.sstt_vencimientos_cursos_fecha_ven IS NOT NULL AND vc2.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') AND vc2.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' AND DATE(vc2.sstt_vencimientos_cursos_fecha_ven) > CURDATE() AND DATEDIFF(vc2.sstt_vencimientos_cursos_fecha_ven, CURDATE()) > 30) "
        filter_sql += " AND (vc.sstt_vencimientos_cursos_tipo_curso <> 'EXAMEN MEDICO INGRESO' OR NOT EXISTS (SELECT 1 FROM sstt_vencimientos_cursos vcP WHERE vcP.recurso_operativo_cedula = vc.recurso_operativo_cedula AND vcP.sstt_vencimientos_cursos_tipo_curso = 'EXAMEN MEDICO PERIODICO' AND vcP.sstt_vencimientos_cursos_fecha_ven IS NOT NULL AND vcP.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01') AND vcP.sstt_vencimientos_cursos_fecha_ven > '1900-01-01' AND ((DATE(vc.sstt_vencimientos_cursos_fecha_ven) <= CURDATE() AND DATEDIFF(vcP.sstt_vencimientos_cursos_fecha_ven, CURDATE()) > 30) OR (DATE(vc.sstt_vencimientos_cursos_fecha_ven) > CURDATE() AND DATEDIFF(vc.sstt_vencimientos_cursos_fecha_ven, CURDATE()) <= 30 AND DATE(vcP.sstt_vencimientos_cursos_fecha_ven) >= CURDATE()))) )"
        sql += ' WHERE ' + filter_sql
        sql += ' ORDER BY ro.nombre ASC, vc.sstt_vencimientos_cursos_fecha_ven ASC'
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall() or []
        import csv, io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['cedula','nombre','curso','vencimiento'])
        for r in rows:
            fv = r.get('vencimiento')
            if hasattr(fv, 'strftime'):
                fv_str = fv.strftime('%Y-%m-%d')
            else:
                s = str(fv).strip() if fv else ''
                if s and ' ' in s:
                    s = s.split(' ')[0]
                fv_str = s
            writer.writerow([r.get('cedula') or '', r.get('nombre') or '', r.get('curso') or '', fv_str])
        csv_data = output.getvalue()
        output.close()
        cursor.close(); connection.close()
        filename = f"vencimientos_cursos_export_{get_bogota_datetime().strftime('%Y%m%d')}.csv"
        resp = Response(csv_data, mimetype='text/csv')
        resp.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sstt/vencimientos-cursos/encuesta-vto', methods=['PUT'])
@login_required_api()
def api_sstt_vencimientos_cursos_encuesta_vto():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        data = request.get_json() or {}
        cedula = (data.get('cedula') or '').strip()
        usuario_id = data.get('usuario_id')
        encuesta_id = int(data.get('encuesta_id') or 10)
        anio = data.get('anio')
        fecha = (data.get('fecha') or '').strip()
        fecha_vto = (data.get('fecha_vencimiento') or '').strip()
        if not fecha_vto:
            return jsonify({'success': False, 'message': 'Falta fecha_vencimiento'}), 400
        cur = connection.cursor()
        if not usuario_id:
            if not cedula:
                return jsonify({'success': False, 'message': 'Faltan parámetros de usuario'}), 400
            cur.execute("SELECT id_codigo_consumidor FROM recurso_operativo WHERE recurso_operativo_cedula = %s", (cedula,))
            ru = cur.fetchone()
            if not ru:
                return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
            usuario_id = ru[0]
        cur.execute(
            """
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = DATABASE() AND table_name = 'encuesta_respuestas' AND column_name = 'sstt_vencimientos_cursos_fecha_ven'
            """
        )
        has_col = (cur.fetchone() or [0])[0]
        if not has_col:
            try:
                cur.execute("ALTER TABLE encuesta_respuestas ADD COLUMN sstt_vencimientos_cursos_fecha_ven DATE NULL AFTER fecha_respuesta")
                connection.commit()
            except Exception:
                pass
        params = [fecha_vto, encuesta_id, usuario_id]
        where_extra = ''
        if anio:
            where_extra = ' AND YEAR(fecha_respuesta) = %s'
            params.append(int(anio))
        elif fecha:
            where_extra = ' AND DATE(fecha_respuesta) = %s'
            params.append(fecha)
        cur.execute(
            "UPDATE encuesta_respuestas SET sstt_vencimientos_cursos_fecha_ven = %s WHERE encuesta_id = %s AND usuario_id = %s" + where_extra + " ORDER BY fecha_respuesta DESC LIMIT 1",
            tuple(params)
        )
        connection.commit()
        affected = cur.rowcount
        cur.close(); connection.close()
        if affected == 0:
            return jsonify({'success': False, 'message': 'No se encontró respuesta para actualizar'}), 404
        return jsonify({'success': True, 'updated': affected})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
@app.route('/api/sstt/capacitaciones', methods=['GET', 'POST'])
@login_required
def api_sstt_capacitaciones():
    """API para gestionar capacitaciones"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        if request.method == 'GET':
            cursor.execute("""
                SELECT c.*, ro.nombre as instructor_nombre
                FROM sstt_capacitaciones c
                LEFT JOIN recurso_operativo ro ON c.usuario_creador = ro.id_codigo_consumidor
                ORDER BY c.fecha_programada DESC
            """)
            capacitaciones = cursor.fetchall()
            
            return jsonify({'capacitaciones': capacitaciones})
            
        elif request.method == 'POST':
            data = request.get_json()
            
            cursor.execute("""
                INSERT INTO sstt_capacitaciones 
                (titulo, descripcion, fecha_programada, duracion_horas, 
                 ubicacion, estado, usuario_creador, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                data['titulo'],
                data['descripcion'],
                data['fecha_programada'],
                data['duracion_horas'],
                data['ubicacion'],
                data.get('estado', 'programada'),
                current_user.id
            ))
            
            connection.commit()
            capacitacion_id = cursor.lastrowid
            
            return jsonify({
                'success': True, 
                'message': 'Capacitación creada exitosamente',
                'capacitacion_id': capacitacion_id
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/sstt/preoperacional', methods=['GET'])
@login_required
def api_sstt_preoperacional():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        tecnico_id = (request.args.get('tecnico_id') or '').strip()
        fecha = (request.args.get('fecha') or '').strip()
        if not tecnico_id or not fecha:
            cursor.close(); connection.close()
            return jsonify({'success': False, 'message': 'Parámetros requeridos: tecnico_id y fecha'}), 400
        cursor.execute(
            """
            SELECT * FROM preoperacional 
            WHERE id_codigo_consumidor = %s AND DATE(fecha) = %s
            ORDER BY fecha DESC LIMIT 1
            """,
            (tecnico_id, fecha)
        )
        row = cursor.fetchone()
        if not row:
            cursor.close(); connection.close()
            return jsonify({'success': True, 'data': None})
        for k, v in list(row.items()):
            try:
                if hasattr(v, 'strftime'):
                    row[k] = v.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass
        cursor.close(); connection.close()
        return jsonify({'success': True, 'data': row})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sstt/preoperacional/export', methods=['GET'])
@login_required
def api_sstt_preoperacional_export():
    try:
        if not current_user.has_role('sstt') and not current_user.has_role('administrativo'):
            return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        mes = (request.args.get('mes') or '').strip()
        if not mes or not re.match(r'^\d{4}-\d{2}$', mes):
            return jsonify({'success': False, 'message': 'Parámetro mes requerido (YYYY-MM)'}), 400
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT 
                p.*,
                r.nombre as nombre_tecnico,
                r.cargo as cargo_tecnico,
                r.recurso_operativo_cedula as cedula_tecnico
            FROM preoperacional p
            JOIN recurso_operativo r ON p.id_codigo_consumidor = r.id_codigo_consumidor
            WHERE DATE_FORMAT(p.fecha, '%Y-%m') = %s
            ORDER BY p.fecha ASC
            """,
            (mes,)
        )
        registros = cursor.fetchall()
        cursor.close(); connection.close()
        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        output.write('\ufeff')
        writer.writerow([
            'Fecha', 'Técnico', 'Cédula', 'Cargo', 'Centro de Trabajo', 'Ciudad', 'Supervisor',
            'Vehículo Asistió', 'Tipo Vehículo', 'Placa', 'Modelo', 'Marca',
            'Licencia Conducción', 'Vencimiento Licencia', 'Vencimiento SOAT',
            'Vencimiento Tecnomecánica', 'Estado Espejos', 'Bocina/Pito',
            'Frenos', 'Encendido', 'Batería', 'Amortiguadores', 'Llantas',
            'Kilometraje', 'Luces Altas/Bajas', 'Direccionales',
            'Elementos Prevención Casco', 'Casco Certificado', 'Casco Identificado',
            'Estado Guantes', 'Estado Rodilleras', 'Coderas', 'Impermeable', 'Observaciones'
        ])
        for registro in registros:
            try:
                fecha_lic = registro.get('fecha_vencimiento_licencia')
                fecha_soat = registro.get('fecha_vencimiento_soat')
                fecha_tec = registro.get('fecha_vencimiento_tecnomecanica')
                fl = fecha_lic.strftime('%Y-%m-%d') if hasattr(fecha_lic, 'strftime') else (fecha_lic or '')
                fs = fecha_soat.strftime('%Y-%m-%d') if hasattr(fecha_soat, 'strftime') else (fecha_soat or '')
                ft = fecha_tec.strftime('%Y-%m-%d') if hasattr(fecha_tec, 'strftime') else (fecha_tec or '')
            except Exception:
                fl = fs = ft = ''
            try:
                fdt = registro.get('fecha')
                fecha_str = fdt.strftime('%Y-%m-%d %H:%M:%S') if hasattr(fdt, 'strftime') else (fdt or '')
            except Exception:
                fecha_str = ''
            km = registro.get('kilometraje_actual') if 'kilometraje_actual' in registro else registro.get('kilometraje')
            writer.writerow([
                fecha_str,
                registro.get('nombre_tecnico') or '',
                registro.get('cedula_tecnico') or '',
                registro.get('cargo_tecnico') or '',
                registro.get('centro_de_trabajo') or '',
                registro.get('ciudad') or '',
                registro.get('supervisor') or '',
                registro.get('vehiculo_asistio_operacion') or '',
                registro.get('tipo_vehiculo') or '',
                registro.get('placa_vehiculo') or '',
                registro.get('modelo_vehiculo') or '',
                registro.get('marca_vehiculo') or '',
                registro.get('licencia_conduccion') or '',
                fl,
                fs,
                ft,
                registro.get('estado_espejos') or '',
                registro.get('bocina_pito') or '',
                registro.get('frenos') or '',
                registro.get('encendido') or '',
                registro.get('estado_bateria') or '',
                registro.get('estado_amortiguadores') or '',
                registro.get('estado_llantas') or '',
                km or '',
                registro.get('luces_altas_bajas') or '',
                registro.get('direccionales_delanteras_traseras') or '',
                registro.get('elementos_prevencion_seguridad_vial_casco') or '',
                registro.get('casco_certificado') or '',
                registro.get('casco_identificado') or '',
                registro.get('estado_guantes') or registro.get('elementos_prevencion_seguridad_vial_guantes') or '',
                registro.get('estado_rodilleras') or registro.get('elementos_prevencion_seguridad_vial_rodilleras') or '',
                registro.get('elementos_prevencion_seguridad_vial_coderas') or '',
                registro.get('impermeable') or registro.get('elementos_prevencion_seguridad_vial_impermeable') or '',
                registro.get('observaciones') or ''
            ])
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv; charset=utf-8-sig',
            as_attachment=True,
            download_name=f'preoperacional_{mes}.csv'
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sstt/incidentes', methods=['GET', 'POST'])
@login_required
def api_sstt_incidentes():
    """API para gestionar incidentes laborales"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        if request.method == 'GET':
            cursor.execute("""
                SELECT i.*, ro.nombre as reporta_nombre
                FROM sstt_incidentes i
                LEFT JOIN recurso_operativo ro ON i.usuario_reporta = ro.id_codigo_consumidor
                ORDER BY i.fecha_incidente DESC
            """)
            incidentes = cursor.fetchall()
            
            return jsonify({'incidentes': incidentes})
            
        elif request.method == 'POST':
            data = request.get_json()
            
            cursor.execute("""
                INSERT INTO sstt_incidentes 
                (fecha_incidente, ubicacion, descripcion, tipo_incidente, 
                 gravedad, usuario_reporta, fecha_reporte)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (
                data['fecha_incidente'],
                data['ubicacion'],
                data['descripcion'],
                data['tipo_incidente'],
                data['gravedad'],
                current_user.id
            ))
            
            connection.commit()
            incidente_id = cursor.lastrowid
            
            return jsonify({
                'success': True, 
                'message': 'Incidente reportado exitosamente',
                'incidente_id': incidente_id
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/sstt/epp', methods=['GET', 'POST'])
@login_required
def api_sstt_epp():
    """API para control de EPP (Elementos de Protección Personal)"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        if request.method == 'GET':
            cursor.execute("""
                SELECT e.*, ro.nombre as usuario_nombre
                FROM sstt_epp_control e
                LEFT JOIN recurso_operativo ro ON e.usuario_id = ro.id_codigo_consumidor
                ORDER BY e.fecha_entrega DESC
            """)
            epp_registros = cursor.fetchall()
            
            return jsonify({'epp_registros': epp_registros})
            
        elif request.method == 'POST':
            data = request.get_json()
            
            cursor.execute("""
                INSERT INTO sstt_epp_control 
                (usuario_id, tipo_epp, marca, modelo, fecha_entrega, 
                 fecha_vencimiento, estado, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['usuario_id'],
                data['tipo_epp'],
                data['marca'],
                data['modelo'],
                data['fecha_entrega'],
                data.get('fecha_vencimiento'),
                data.get('estado', 'activo'),
                data.get('observaciones', '')
            ))
            
            connection.commit()
            epp_id = cursor.lastrowid
            
            return jsonify({
                'success': True, 
                'message': 'Registro de EPP creado exitosamente',
                'epp_id': epp_id
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/sstt/dashboard-stats', methods=['GET'])
@login_required
def api_sstt_dashboard_stats():
    """API para estadísticas del dashboard SSTT"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        stats = {}
        
        # Estadísticas de inspecciones
        cursor.execute("SELECT COUNT(*) as total FROM sstt_inspecciones")
        stats['total_inspecciones'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as pendientes FROM sstt_inspecciones WHERE estado = 'pendiente'")
        stats['inspecciones_pendientes'] = cursor.fetchone()['pendientes']
        
        # Estadísticas de capacitaciones
        cursor.execute("SELECT COUNT(*) as total FROM sstt_capacitaciones")
        stats['total_capacitaciones'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as programadas FROM sstt_capacitaciones WHERE estado = 'programada'")
        stats['capacitaciones_programadas'] = cursor.fetchone()['programadas']
        
        # Estadísticas de incidentes
        cursor.execute("SELECT COUNT(*) as total FROM sstt_incidentes")
        stats['total_incidentes'] = cursor.fetchone()['total']
        
        cursor.execute("""
            SELECT COUNT(*) as recientes 
            FROM sstt_incidentes 
            WHERE fecha_incidente >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """)
        stats['incidentes_mes'] = cursor.fetchone()['recientes']
        
        # Estadísticas de EPP
        cursor.execute("SELECT COUNT(*) as total FROM sstt_epp_control")
        stats['total_epp'] = cursor.fetchone()['total']
        
        cursor.execute("""
            SELECT COUNT(*) as vencidos 
            FROM sstt_epp_control 
            WHERE fecha_vencimiento <= NOW() AND estado = 'activo'
        """)
        stats['epp_vencidos'] = cursor.fetchone()['vencidos']
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# Función de login removida - se usa la de main.py

@app.route('/api/asistencia/resumen_agrupado', methods=['GET'])
@login_required
def obtener_resumen_agrupado_asistencia():
    """Obtener resumen de asistencia agrupado por grupos de tipificación"""
    try:
        # Obtener parámetros de filtro
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        supervisor_filtro = request.args.get('supervisor')
        
        # Si no se proporcionan fechas, usar la fecha actual
        if not fecha_inicio or not fecha_fin:
            fecha_actual = get_bogota_datetime().date()
            fecha_inicio = fecha_fin = fecha_actual
        else:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                
                # Validaciones adicionales de rango de fechas
                if fecha_inicio > fecha_fin:
                    return jsonify({
                        'success': False,
                        'message': 'La fecha de inicio no puede ser mayor que la fecha de fin'
                    }), 400
                
                # Validar que las fechas no sean futuras
                fecha_actual = get_bogota_datetime().date()
                if fecha_inicio > fecha_actual or fecha_fin > fecha_actual:
                    return jsonify({
                        'success': False,
                        'message': 'No se pueden consultar fechas futuras'
                    }), 400
                
                # Validar rango máximo (1 año)
                diferencia_dias = (fecha_fin - fecha_inicio).days
                if diferencia_dias > 365:
                    return jsonify({
                        'success': False,
                        'message': 'El rango de fechas no puede ser mayor a 1 año'
                    }), 400
                    
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }), 400
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Consulta base para obtener datos agrupados (solo registros con grupo válido)
        query_base = """
            SELECT 
                t.grupo,
                t.nombre_tipificacion as carpeta,
                COUNT(DISTINCT a.id_codigo_consumidor) as total_tecnicos
            FROM asistencia a
            INNER JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
            WHERE DATE(a.fecha_asistencia) BETWEEN %s AND %s
                AND t.grupo IS NOT NULL 
                AND t.grupo != ''
                AND t.grupo IN ('ARREGLOS', 'AUSENCIA INJUSTIFICADA', 'AUSENCIA JUSTIFICADA', 'INSTALACIONES', 'POSTVENTA')
        """
        
        params = [fecha_inicio, fecha_fin]
        
        # Agregar filtro por supervisor si se proporciona
        if supervisor_filtro:
            query_base += " AND a.super = %s"
            params.append(supervisor_filtro)
        
        query_base += """
            GROUP BY t.grupo, t.nombre_tipificacion
            ORDER BY t.grupo, t.nombre_tipificacion
        """
        
        # Ejecutar consulta principal
        cursor.execute(query_base, tuple(params))
        resultados = cursor.fetchall()
        
        # Calcular total de técnicos para porcentajes (solo registros con grupo válido)
        query_total = """
            SELECT COUNT(DISTINCT a.id_codigo_consumidor) as total_general
            FROM asistencia a
            INNER JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
            WHERE DATE(a.fecha_asistencia) BETWEEN %s AND %s
                AND t.grupo IS NOT NULL 
                AND t.grupo != ''
                AND t.grupo IN ('ARREGLOS', 'AUSENCIA INJUSTIFICADA', 'AUSENCIA JUSTIFICADA', 'INSTALACIONES', 'POSTVENTA')
        """
        
        params_total = [fecha_inicio, fecha_fin]
        if supervisor_filtro:
            query_total += " AND a.super = %s"
            params_total.append(supervisor_filtro)
        
        cursor.execute(query_total, tuple(params_total))
        total_general = cursor.fetchone()['total_general'] or 0
        
        # Procesar resultados y calcular porcentajes
        resumen_agrupado = []
        grupos_totales = {}
        
        # Primero, calcular totales por grupo
        for resultado in resultados:
            grupo = resultado['grupo']
            if grupo not in grupos_totales:
                grupos_totales[grupo] = 0
            grupos_totales[grupo] += resultado['total_tecnicos']
        
        # Luego, crear el resumen con porcentajes
        for resultado in resultados:
            grupo = resultado['grupo']
            carpeta = resultado['carpeta']
            total_tecnicos = resultado['total_tecnicos']
            
            # Calcular porcentaje respecto al total general
            porcentaje = round((total_tecnicos * 100) / total_general, 2) if total_general > 0 else 0
            
            resumen_agrupado.append({
                'grupo': grupo,
                'carpeta': carpeta,
                'total_tecnicos': total_tecnicos,
                'porcentaje': porcentaje
            })
        
        # Calcular resumen por grupos
        resumen_grupos = []
        for grupo, total_grupo in grupos_totales.items():
            porcentaje_grupo = round((total_grupo * 100) / total_general, 2) if total_general > 0 else 0
            resumen_grupos.append({
                'grupo': grupo,
                'total_tecnicos': total_grupo,
                'porcentaje': porcentaje_grupo
            })
        
        return jsonify({
            'success': True,
            'data': {
                'detallado': resumen_agrupado,
                'resumen_grupos': resumen_grupos,
                'total_general': total_general,
                'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
                'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
                'supervisor_filtro': supervisor_filtro
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# ==================== RUTAS DEL MÓDULO MPA ====================

@app.route('/mpa')
@login_required
def mpa_dashboard():
    """Dashboard principal del módulo MPA (Módulo de Parque Automotor)"""
    if not current_user.has_role('administrativo'):
        flash('No tienes permisos para acceder a este módulo.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('modulos/mpa/dashboard.html')

@app.route('/api/mpa/dashboard-stats')
@login_required
def mpa_dashboard_stats():
    """API para obtener estadísticas del dashboard MPA"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        stats = {}
        
        # Estadísticas de Vehículos (por ahora retornamos 0 hasta crear las tablas)
        stats['total_vehiculos'] = 0
        stats['vehiculos_activos'] = 0
        
        # Estadísticas de Vencimientos
        stats['total_vencimientos'] = 0
        stats['vencimientos_proximos'] = 0
        
        # Estadísticas de Mantenimientos
        stats['total_mantenimientos'] = 0
        stats['mantenimientos_mes'] = 0
        
        # Estadísticas de Siniestros
        stats['total_siniestros'] = 0
        stats['siniestros_mes'] = 0
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# Rutas para los módulos individuales del MPA
@app.route('/mpa/vehiculos')
@login_required
def mpa_vehiculos():
    """Módulo de gestión de vehículos"""
    if not current_user.has_role('administrativo'):
        flash('No tienes permisos para acceder a este módulo.', 'error')
        return redirect(url_for('mpa_dashboard'))
    
    return render_template('modulos/mpa/vehicles.html')

@app.route('/mpa/rutas')
@login_required
def mpa_rutas():
    if not (current_user.has_role('administrativo') or current_user.has_role('operativo') or current_user.has_role('logistica')):
        flash('No tienes permisos para acceder a este módulo.', 'error')
        return redirect(url_for('mpa_dashboard'))
    return render_template('modulos/mpa/rutas.html')

def ensure_rutas_table(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS mpa_rutas_tecnicos (
            id_ruta INT AUTO_INCREMENT PRIMARY KEY,
            cedula VARCHAR(32),
            nombre VARCHAR(255),
            lat_inicio DECIMAL(9,6),
            lon_inicio DECIMAL(9,6),
            lat_fin DECIMAL(9,6),
            lon_fin DECIMAL(9,6),
            fecha DATE NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )
    conn.commit()
    cursor.close()

@app.route('/api/mpa/rutas/import-excel', methods=['POST'])
@login_required
def api_import_rutas_excel():
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        ensure_rutas_table(conn)
        try:
            import pandas as pd
            from io import BytesIO
        except Exception:
            return jsonify({'success': False, 'message': 'Dependencia faltante: pandas.'}), 500
        df = None
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            buf = BytesIO(file.read())
            ext = (file.filename.split('.')[-1] or '').lower()
            try:
                df = pd.read_excel(buf) if ext in ['xlsx', 'xls'] else pd.read_csv(buf, sep=None, engine='python')
            except Exception as e:
                return jsonify({'success': False, 'message': 'No se pudo leer el archivo', 'error': str(e)}), 400
        else:
            file_path = request.json.get('file_path') if request.is_json else None
            if not file_path:
                return jsonify({'success': False, 'message': 'No se proporcionó archivo'}), 400
            try:
                df = pd.read_excel(file_path)
            except Exception as e:
                return jsonify({'success': False, 'message': 'No se pudo leer el archivo', 'error': str(e)}), 400
        df.columns = [str(c).strip() for c in df.columns]
        alias = {
            'Coordenada X Inicio': 'lat_inicio',
            'Coordenada Y Inicio': 'lon_inicio',
            'Coordenada X Fin': 'lat_fin',
            'Coordenada Y Fin': 'lon_fin',
            'cedula': 'cedula',
            'Nombre': 'nombre'
        }
        df.rename(columns=alias, inplace=True)
        required = ['cedula', 'nombre', 'lat_inicio', 'lon_inicio', 'lat_fin', 'lon_fin']
        missing = [c for c in required if c not in df.columns]
        if missing:
            return jsonify({'success': False, 'message': 'Columnas faltantes: ' + ', '.join(missing)}), 400
        def fix_num(x):
            s = str(x).strip()
            s = s.replace('..', '.')
            try:
                return float(s)
            except Exception:
                return None
        df['lat_inicio'] = df['lat_inicio'].apply(fix_num)
        df['lon_inicio'] = df['lon_inicio'].apply(fix_num)
        df['lat_fin'] = df['lat_fin'].apply(fix_num)
        df['lon_fin'] = df['lon_fin'].apply(fix_num)
        df = df.dropna(subset=['lat_inicio', 'lon_inicio', 'lat_fin', 'lon_fin'])
        rows = []
        for _, r in df.iterrows():
            rows.append((
                str(r['cedula']).strip(),
                str(r['nombre']).strip(),
                float(r['lat_inicio']),
                float(r['lon_inicio']),
                float(r['lat_fin']),
                float(r['lon_fin']),
                None
            ))
        cur = conn.cursor()
        cur.executemany(
            """
            INSERT INTO mpa_rutas_tecnicos (cedula, nombre, lat_inicio, lon_inicio, lat_fin, lon_fin, fecha)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            rows
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'inserted': len(rows)})
    except Exception as e:
        try:
            if 'conn' in locals() and conn:
                conn.rollback()
        except Exception:
            pass
        return jsonify({'success': False, 'message': 'Error procesando archivo', 'error': str(e)}), 500

@app.route('/api/mpa/rutas/tecnicos', methods=['GET'])
@login_required
def api_rutas_tecnicos():
    if not (current_user.has_role('administrativo') or current_user.has_role('operativo') or current_user.has_role('logistica')):
        return jsonify({'error': 'Sin permisos'}), 403
    estado = (request.args.get('estado') or '').strip()
    periodo = (request.args.get('periodo') or 'dia').strip().lower()
    fecha_in = (request.args.get('fecha') or '').strip()
    solo_ot = (request.args.get('solo_ot', '1') or '1').strip().lower()
    try:
        from datetime import datetime, timedelta
        base = None
        if fecha_in:
            try:
                base = datetime.strptime(fecha_in, '%Y-%m-%d').date()
            except Exception:
                base = get_bogota_datetime().date()
        else:
            base = get_bogota_datetime().date()
        start = base
        end = base
        if periodo == 'semana':
            start = base - timedelta(days=6)
            end = base
        elif periodo == 'mes':
            start = base.replace(day=1)
            nm = start.replace(day=28) + timedelta(days=4)
            end = nm - timedelta(days=nm.day)
        conn = get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cur = conn.cursor(dictionary=True)
        sql = (
            "SELECT DISTINCT CAST(o.external_id AS CHAR) AS cedula, ro.nombre "
            "FROM operaciones_actividades_diarias o "
            "LEFT JOIN recurso_operativo ro ON CAST(o.external_id AS CHAR) = CAST(ro.recurso_operativo_cedula AS CHAR) "
            "WHERE o.coordenada_x IS NOT NULL AND o.coordenada_y IS NOT NULL "
            "AND DATE(o.fecha) BETWEEN %s AND %s"
        )
        params = [start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')]
        if estado:
            en = estado.strip().lower()
            if en != 'todos':
                if en in ('cancelado'):
                    sql += " AND UPPER(TRIM(o.estado)) = 'CANCELADO'"
                elif en in ('completado','finalizado','terminado','ok'):
                    sql += " AND UPPER(TRIM(o.estado)) IN ('COMPLETADO','OK')"
                elif en in ('no_completado','no-completado','pendiente','sin_finalizar'):
                    sql += " AND UPPER(TRIM(o.estado)) IN ('NO COMPLETADO','NO-COMPLETADO')"
                else:
                    sql += " AND UPPER(TRIM(o.estado)) = %s"
                    params.append(estado.upper())
        if solo_ot in ('1','true','yes','si','sí'):
            sql += " AND o.orden_de_trabajo IS NOT NULL"
        sql += " ORDER BY ro.nombre, cedula"
        cur.execute(sql, params)
        data = cur.fetchall() or []
        if not data and periodo == 'dia':
            sql_fb = (
                "SELECT DISTINCT CAST(o.external_id AS CHAR) AS cedula, ro.nombre "
                "FROM operaciones_actividades_diarias o "
                "LEFT JOIN recurso_operativo ro ON CAST(o.external_id AS CHAR) = CAST(ro.recurso_operativo_cedula AS CHAR) "
                "WHERE o.coordenada_x IS NOT NULL AND o.coordenada_y IS NOT NULL "
                "AND DATE(o.fecha) BETWEEN %s AND %s"
            )
            params_fb = [ (base - timedelta(days=6)).strftime('%Y-%m-%d'), base.strftime('%Y-%m-%d') ]
            en = (estado or '').strip().lower()
            if en and en != 'todos':
                if en in ('cancelado'):
                    sql_fb += " AND UPPER(TRIM(o.estado)) = 'CANCELADO'"
                elif en in ('completado','finalizado','terminado','ok'):
                    sql_fb += " AND UPPER(TRIM(o.estado)) IN ('COMPLETADO','OK')"
                elif en in ('no_completado','no-completado','pendiente','sin_finalizar'):
                    sql_fb += " AND UPPER(TRIM(o.estado)) IN ('NO COMPLETADO','NO-COMPLETADO')"
                else:
                    sql_fb += " AND UPPER(TRIM(o.estado)) = %s"
                    params_fb.append(estado.upper())
            if solo_ot in ('1','true','yes','si','sí'):
                sql_fb += " AND o.orden_de_trabajo IS NOT NULL"
            sql_fb += " ORDER BY ro.nombre, cedula"
            cur.execute(sql_fb, params_fb)
            data = cur.fetchall() or []
        cur.close(); conn.close()
        return jsonify({'success': True, 'tecnicos': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/mpa/rutas/estados', methods=['GET'])
@login_required
def api_rutas_estados():
    if not (current_user.has_role('administrativo') or current_user.has_role('operativo') or current_user.has_role('logistica')):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cur = conn.cursor()
        cur.execute(
            """
            SELECT DISTINCT UPPER(TRIM(estado)) AS estado
            FROM operaciones_actividades_diarias
            WHERE estado IS NOT NULL AND TRIM(estado) <> ''
            ORDER BY estado
            """
        )
        estados = [r[0] for r in cur.fetchall()] or []
        cur.close(); conn.close()
        return jsonify({'success': True, 'estados': estados})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/mpa/rutas/por-tecnico', methods=['GET'])
@login_required
def api_rutas_por_tecnico():
    if not (current_user.has_role('administrativo') or current_user.has_role('operativo') or current_user.has_role('logistica')):
        return jsonify({'error': 'Sin permisos'}), 403
    cedula = request.args.get('cedula')
    if not cedula:
        return jsonify({'success': False, 'message': 'Cedula requerida'}), 400
    estado = (request.args.get('estado') or '').strip()
    periodo = (request.args.get('periodo') or 'dia').strip().lower()
    fecha_in = (request.args.get('fecha') or '').strip()
    try:
        from datetime import datetime, timedelta
        base = None
        if fecha_in:
            try:
                base = datetime.strptime(fecha_in, '%Y-%m-%d').date()
            except Exception:
                base = get_bogota_datetime().date()
        else:
            base = get_bogota_datetime().date()
        start = base
        end = base
        if periodo == 'semana':
            start = base - timedelta(days=6)
            end = base
        elif periodo == 'mes':
            start = base.replace(day=1)
            nm = start.replace(day=28) + timedelta(days=4)
            end = nm - timedelta(days=nm.day)
        conn = get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cur = conn.cursor(dictionary=True)
        has_window = False
        account_col = None
        try:
            cur_cols = conn.cursor()
            cur_cols.execute("SELECT COLUMN_NAME FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name='operaciones_actividades_diarias'")
            cols = [r[0] for r in cur_cols.fetchall()]
            lc = {c.lower(): c for c in cols}
            has_window = ('ventana_de_entrega' in lc)
            cand_accounts = ['numero_de_cuenta','cuenta','nro_cuenta','num_cuenta']
            for n in cand_accounts:
                if n in lc:
                    account_col = lc[n]
                    break
            if not account_col:
                for c in cols:
                    for n in cand_accounts:
                        if n in c.lower():
                            account_col = c
                            break
                    if account_col:
                        break
            cur_cols.close()
        except Exception:
            pass
        sel = "external_id, orden_de_trabajo, fecha, estado AS estado, coordenada_y AS lat, coordenada_x AS lon"
        if has_window:
            sel = "external_id, orden_de_trabajo, fecha, ventana_de_entrega AS ventana, estado AS estado, coordenada_y AS lat, coordenada_x AS lon"
        if account_col:
            sel += f", `{account_col}` AS cuenta"
        sql = (
            f"SELECT {sel} "
            "FROM operaciones_actividades_diarias o "
            "WHERE external_id = %s AND coordenada_x IS NOT NULL AND coordenada_y IS NOT NULL "
            "AND DATE(fecha) BETWEEN %s AND %s"
        )
        params = [cedula, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')]
        if estado:
            en = estado.strip().lower()
            if en != 'todos':
                if en in ('cancelado'):
                    sql += " AND UPPER(TRIM(o.estado)) = 'CANCELADO'"
                elif en in ('completado','finalizado','terminado','ok'):
                    sql += " AND UPPER(TRIM(o.estado)) IN ('COMPLETADO','OK')"
                elif en in ('no_completado','no-completado','pendiente','sin_finalizar'):
                    sql += " AND UPPER(TRIM(o.estado)) IN ('NO COMPLETADO','NO-COMPLETADO')"
        solo_ot = (request.args.get('solo_ot', '1') or '1').strip().lower()
        if solo_ot in ('1','true','yes','si','sí'):
            sql += " AND orden_de_trabajo IS NOT NULL"
        sql += " ORDER BY fecha ASC"
        cur.execute(sql, params)
        rows = cur.fetchall() or []
        if not rows and periodo == 'dia':
            cur = conn.cursor(dictionary=True)
            sql_fb = (
                f"SELECT {sel} "
                "FROM operaciones_actividades_diarias o "
                "WHERE external_id = %s AND coordenada_x IS NOT NULL AND coordenada_y IS NOT NULL "
                "AND DATE(fecha) BETWEEN %s AND %s"
            )
            params_fb = [cedula, (base - timedelta(days=6)).strftime('%Y-%m-%d'), base.strftime('%Y-%m-%d')]
            if estado:
                en = estado.strip().lower()
                if en != 'todos':
                    if en in ('cancelado'):
                        sql_fb += " AND UPPER(TRIM(o.estado)) = 'CANCELADO'"
                    elif en in ('completado','finalizado','terminado','ok'):
                        sql_fb += " AND UPPER(TRIM(o.estado)) IN ('COMPLETADO','OK')"
                    elif en in ('no_completado','no-completado','pendiente','sin_finalizar'):
                        sql_fb += " AND UPPER(TRIM(o.estado)) IN ('NO COMPLETADO','NO-COMPLETADO')"
                    else:
                        sql_fb += " AND UPPER(TRIM(o.estado)) = %s"
                        params_fb.append(estado.upper())
            if solo_ot in ('1','true','yes','si','sí'):
                sql_fb += " AND orden_de_trabajo IS NOT NULL"
            sql_fb += " ORDER BY fecha ASC"
            cur.execute(sql_fb, params_fb)
            rows = cur.fetchall() or []
        cur.close()
        conn.close()
        rutas = []
        prev = None
        prev_day = None
        empresa_lat = 4.680969
        empresa_lon = -74.094884
        for r in rows:
            f = r['fecha']
            d = f.date() if hasattr(f, 'date') else f
            if prev is None:
                tip = None
                est = (r.get('estado') or '').strip().upper()
                if est == 'CANCELADO':
                    tip = 'Cancelado'
                elif est in ('COMPLETADO','OK'):
                    tip = 'Completado'
                elif est in ('NO COMPLETADO','NO-COMPLETADO'):
                    tip = 'No completado'
                else:
                    tip = ''
                rutas.append({
                    'lat_inicio': empresa_lat,
                    'lon_inicio': empresa_lon,
                    'lat_fin': float(r['lat']) if r['lat'] is not None else None,
                    'lon_fin': float(r['lon']) if r['lon'] is not None else None,
                    'fecha': d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d),
                    'hora': (r.get('ventana') or (f.strftime('%H:%M') if hasattr(f, 'strftime') else '')),
                    'orden_de_trabajo': r.get('orden_de_trabajo'),
                    'tip_estado': tip,
                    'cuenta': r.get('cuenta')
                })
                prev = (r['lat'], r['lon'])
                prev_day = d
                continue
            if prev_day != d:
                tip = None
                est = (r.get('estado') or '').upper()
                conf = (r.get('conf') or '').upper()
                cierre = (r.get('cierre') or '').upper()
                if est == 'CANCELADO':
                    tip = 'Cancelado'
                elif est in ('OK','COMPLETADO','FINALIZADO') or conf in ('SI','SI ') or cierre in ('SI','SI '):
                    tip = 'Completado'
                else:
                    tip = 'No completado'
                rutas.append({
                    'lat_inicio': empresa_lat,
                    'lon_inicio': empresa_lon,
                    'lat_fin': float(r['lat']) if r['lat'] is not None else None,
                    'lon_fin': float(r['lon']) if r['lon'] is not None else None,
                    'fecha': d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d),
                    'hora': (r.get('ventana') or (f.strftime('%H:%M') if hasattr(f, 'strftime') else '')),
                    'orden_de_trabajo': r.get('orden_de_trabajo'),
                    'tip_estado': tip,
                    'cuenta': r.get('cuenta')
                })
                prev = (r['lat'], r['lon'])
                prev_day = d
                continue
            tip = None
            est = (r.get('estado') or '').strip().upper()
            if est == 'CANCELADO':
                tip = 'Cancelado'
            elif est in ('COMPLETADO','OK'):
                tip = 'Completado'
            elif est in ('NO COMPLETADO','NO-COMPLETADO'):
                tip = 'No completado'
            else:
                tip = ''
            rutas.append({
                'lat_inicio': float(prev[0]) if prev and prev[0] is not None else None,
                'lon_inicio': float(prev[1]) if prev and prev[1] is not None else None,
                'lat_fin': float(r['lat']) if r['lat'] is not None else None,
                'lon_fin': float(r['lon']) if r['lon'] is not None else None,
                'fecha': d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d),
                'hora': (r.get('ventana') or (f.strftime('%H:%M') if hasattr(f, 'strftime') else '')),
                'orden_de_trabajo': r.get('orden_de_trabajo'),
                'tip_estado': tip,
                'cuenta': r.get('cuenta')
            })
            prev = (r['lat'], r['lon'])
        
        return jsonify({'success': True, 'rutas': rutas})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/mpa/rutas/google-directions', methods=['GET'])
@login_required
def api_google_directions_route():
    if not (current_user.has_role('administrativo') or current_user.has_role('operativo') or current_user.has_role('logistica')):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    try:
        import os
        import requests
        key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not key:
            return jsonify({'success': False, 'message': 'Falta GOOGLE_MAPS_API_KEY en entorno'}), 500
        olat = request.args.get('origin_lat', type=float)
        olon = request.args.get('origin_lon', type=float)
        dlat = request.args.get('dest_lat', type=float)
        dlon = request.args.get('dest_lon', type=float)
        if olat is None or olon is None or dlat is None or dlon is None:
            return jsonify({'success': False, 'message': 'Coordenadas inválidas'}), 400
        url = (
            'https://maps.googleapis.com/maps/api/directions/json'
            f'?origin={olat},{olon}&destination={dlat},{dlon}&mode=driving&alternatives=false&key={key}'
        )
        r = requests.get(url, timeout=10)
        data = r.json()
        routes = data.get('routes') or []
        if not routes:
            return jsonify({'success': False, 'message': 'Sin ruta'}), 200
        route = routes[0]
        poly = ((route.get('overview_polyline') or {}).get('points'))
        bounds = route.get('bounds') or {}
        return jsonify({'success': True, 'polyline': poly, 'bounds': bounds})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/mpa/rutas/riesgo-motos', methods=['GET'])
@login_required
def api_riesgo_motos():
    if not (current_user.has_role('administrativo') or current_user.has_role('operativo') or current_user.has_role('logistica')):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    try:
        import os
        import csv
        import requests
        import time
        min_lat = request.args.get('min_lat', type=float)
        min_lon = request.args.get('min_lon', type=float)
        max_lat = request.args.get('max_lat', type=float)
        max_lon = request.args.get('max_lon', type=float)
        months = request.args.get('months', default=12, type=int)
        vehicle_in = (request.args.get('vehicle') or '').strip().lower()

        global RISK_CACHE, RISK_CACHE_TTL
        if 'RISK_CACHE' not in globals():
            RISK_CACHE = {}
            RISK_CACHE_TTL = 300
        key = (
            round((min_lat or 0), 2),
            round((min_lon or 0), 2),
            round((max_lat or 0), 2),
            round((max_lon or 0), 2),
            int(months or 12),
            vehicle_in or ''
        )
        now = time.time()
        if key in RISK_CACHE and (now - RISK_CACHE[key]['ts'] < RISK_CACHE_TTL):
            pts = RISK_CACHE[key]['points']
            return jsonify({'success': True, 'points': pts, 'count': len(pts), 'cached': True, 'vehicle': vehicle_in, 'months': int(months or 12), 'bbox': [min_lat, min_lon, max_lat, max_lon], 'source': 'cache'})

        puntos = []

        # Preferir datos guardados en BD
        try:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                cur.execute("""
                            CREATE TABLE IF NOT EXISTS mpa_riesgo_accidentes (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                lat DOUBLE NOT NULL,
                                lon DOUBLE NOT NULL,
                                fecha DATE NULL,
                                tipo_vehiculo VARCHAR(64) NULL,
                                localidad VARCHAR(128) NULL,
                                gravedad VARCHAR(64) NULL,
                                fuente VARCHAR(64) NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                INDEX idx_lat (lat),
                                INDEX idx_lon (lon),
                                INDEX idx_fecha (fecha),
                                INDEX idx_tipo (tipo_vehiculo),
                                INDEX idx_localidad (localidad)
                            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                        """)
                where_parts = []
                params = []
                if all(v is not None for v in [min_lat, min_lon, max_lat, max_lon]):
                    where_parts.append("lat BETWEEN %s AND %s")
                    where_parts.append("lon BETWEEN %s AND %s")
                    params.extend([min_lat, max_lat, min_lon, max_lon])
                if months and months > 0:
                    where_parts.append("fecha >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)")
                    params.append(months)
                if vehicle_in and vehicle_in not in ('todos','all'):
                    where_parts.append("LOWER(tipo_vehiculo) = %s")
                    params.append(vehicle_in)
                sql = "SELECT lat, lon FROM mpa_riesgo_accidentes"
                if where_parts:
                    sql += " WHERE " + " AND ".join(where_parts)
                sql += " LIMIT 8000"
                cur.execute(sql, params)
                for lat, lon in cur.fetchall():
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        puntos.append([lat, lon])
                cur.close()
                conn.close()
                RISK_CACHE[key] = { 'points': puntos, 'ts': now }
                return jsonify({'success': True, 'points': puntos, 'count': len(puntos), 'cached': False, 'vehicle': vehicle_in, 'months': int(months or 12), 'bbox': [min_lat, min_lon, max_lat, max_lon], 'source': 'db'})
        except Exception:
            return jsonify({'success': False, 'message': 'Error consultando BD'})
        RISK_CACHE[key] = { 'points': [], 'ts': now }
        return jsonify({'success': True, 'points': [], 'count': 0, 'cached': False, 'vehicle': vehicle_in, 'months': int(months or 12), 'bbox': [min_lat, min_lon, max_lat, max_lon], 'source': 'db'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/mpa/rutas/riesgo-debug', methods=['GET'])
@login_required
def api_riesgo_debug():
    if not (current_user.has_role('administrativo') or current_user.has_role('operativo') or current_user.has_role('logistica')):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    try:
        min_lat = request.args.get('min_lat', type=float)
        min_lon = request.args.get('min_lon', type=float)
        max_lat = request.args.get('max_lat', type=float)
        max_lon = request.args.get('max_lon', type=float)
        months = request.args.get('months', default=12, type=int)
        vehicle_in = (request.args.get('vehicle') or '').strip().lower()
        limit = request.args.get('limit', default=100, type=int)
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'BD no disponible'}), 500
        cur = conn.cursor()
        where_parts = []
        params = []
        if all(v is not None for v in [min_lat, min_lon, max_lat, max_lon]):
            where_parts.append("lat BETWEEN %s AND %s")
            where_parts.append("lon BETWEEN %s AND %s")
            params.extend([min_lat, max_lat, min_lon, max_lon])
        if months and months > 0:
            where_parts.append("fecha >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)")
            params.append(months)
        if vehicle_in and vehicle_in not in ('todos','all'):
            where_parts.append("LOWER(tipo_vehiculo) = %s")
            params.append(vehicle_in)
        sql_base = "FROM mpa_riesgo_accidentes"
        sql_where = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""
        sql_count = "SELECT COUNT(*) " + sql_base + sql_where
        cur.execute(sql_count, params)
        row = cur.fetchone()
        total = int(row[0]) if row else 0
        sql_sample = "SELECT lat, lon " + sql_base + sql_where + " LIMIT %s"
        cur.execute(sql_sample, params + [max(1, min(1000, limit))])
        puntos = []
        for lat, lon in cur.fetchall():
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                puntos.append([lat, lon])
        cur.close(); conn.close()
        return jsonify({'success': True, 'count_total': total, 'count_sample': len(puntos), 'points': puntos, 'vehicle': vehicle_in, 'months': int(months or 12), 'bbox': [min_lat, min_lon, max_lat, max_lon]})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/mpa/rutas/riesgo-por-localidad', methods=['GET'])
@login_required
def api_riesgo_por_localidad():
    if not (current_user.has_role('administrativo') or current_user.has_role('operativo') or current_user.has_role('logistica')):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    try:
        months = request.args.get('months', default=12, type=int)
        vehicle_in = (request.args.get('vehicle') or '').strip().lower()
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'BD no disponible'}), 500
        cur = conn.cursor()
        where_parts = []
        params = []
        if months and months > 0:
            where_parts.append("fecha >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)")
            params.append(months)
        if vehicle_in and vehicle_in not in ('todos','all'):
            where_parts.append("LOWER(tipo_vehiculo) = %s")
            params.append(vehicle_in)
        sql = "SELECT COALESCE(localidad,'Sin dato') AS localidad, COUNT(*) FROM mpa_riesgo_accidentes"
        if where_parts:
            sql += " WHERE " + " AND ".join(where_parts)
        sql += " GROUP BY localidad ORDER BY COUNT(*) DESC"
        cur.execute(sql, params)
        result = [{'localidad': row[0], 'count': int(row[1])} for row in cur.fetchall()]
        cur.close(); conn.close()
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/mpa/localidades', methods=['GET'])
@login_required
def api_localidades():
    if not (current_user.has_role('administrativo') or current_user.has_role('operativo') or current_user.has_role('logistica')):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    try:
        import os
        import time
        import requests
        global LOCALIDADES_CACHE
        global LOCALIDADES_CACHE_TTL
        if 'LOCALIDADES_CACHE' not in globals():
            LOCALIDADES_CACHE = None
            LOCALIDADES_CACHE_TTL = 86400
        now = time.time()
        if LOCALIDADES_CACHE and (now - LOCALIDADES_CACHE['ts'] < LOCALIDADES_CACHE_TTL):
            return jsonify({'success': True, 'geojson': LOCALIDADES_CACHE['geojson']})
        url_gj = os.getenv('BOGOTA_LOCALIDADES_GEOJSON_URL')
        if url_gj:
            r = requests.get(url_gj, timeout=15)
            if r.ok:
                data = r.json()
                LOCALIDADES_CACHE = {'geojson': data, 'ts': now}
                return jsonify({'success': True, 'geojson': data})
        url_fs = os.getenv('BOGOTA_LOCALIDADES_ARCGIS_URL')
        layer = os.getenv('BOGOTA_LOCALIDADES_ARCGIS_LAYER', '0')
        if not url_fs:
            url_fs = 'https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/ordenamientoterritorial/localidad/MapServer'
            layer = '0'
        if url_fs:
            params = {
                'where': '1=1',
                'outFields': '*',
                'returnGeometry': 'true',
                'outSR': 4326,
                'f': 'geojson'
            }
            r = requests.get(url_fs.rstrip('/') + f'/{layer}/query', params=params, timeout=15)
            if r.ok:
                data = r.json()
                LOCALIDADES_CACHE = {'geojson': data, 'ts': now}
                return jsonify({'success': True, 'geojson': data})
        import json
        import os as _os
        local_file = _os.path.join(_os.getcwd(), 'excel', 'localidades_bogota.geojson')
        if _os.path.isfile(local_file):
            with open(local_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                LOCALIDADES_CACHE = {'geojson': data, 'ts': now}
                return jsonify({'success': True, 'geojson': data})
        return jsonify({'success': False, 'message': 'No hay fuente de localidades configurada'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/mpa/rutas/riesgo-importar', methods=['POST'])
@login_required
def api_riesgo_importar():
    if not (current_user.has_role('administrativo') or current_user.has_role('operativo') or current_user.has_role('logistica')):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    try:
        import os
        import shapefile
        from datetime import datetime
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'BD no disponible'}), 500
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mpa_riesgo_accidentes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lat DOUBLE NOT NULL,
                lon DOUBLE NOT NULL,
                fecha DATE NULL,
                tipo_vehiculo VARCHAR(64) NULL,
                localidad VARCHAR(128) NULL,
                gravedad VARCHAR(64) NULL,
                fuente VARCHAR(64) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_lat (lat),
                INDEX idx_lon (lon),
                INDEX idx_fecha (fecha),
                INDEX idx_tipo (tipo_vehiculo),
                INDEX idx_localidad (localidad)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        shp_path = os.path.join(os.getcwd(), 'Siniestros', 'Hoja1_XYTableToPoint3.shp')
        if not os.path.isfile(shp_path):
            return jsonify({'success': False, 'message': 'No existe shapefile local en Siniestros/'}), 200
        sf = shapefile.Reader(shp_path)
        fields = [f[0] for f in sf.fields[1:]]
        idx_lat = next((i for i,f in enumerate(fields) if f.lower()=='latitud'), None)
        idx_lon = next((i for i,f in enumerate(fields) if f.lower()=='longitud'), None)
        idx_fecha = next((i for i,f in enumerate(fields) if f.lower() in ('fechaacc','fecha','fecha_acc')), None)
        idx_veh = next((i for i,f in enumerate(fields) if f.lower() in ('vehiculo_v','clasenombr','claseveh','clasevehiculo')), None)
        idx_loc = next((i for i,f in enumerate(fields) if f.lower()=='localidad'), None)
        idx_grav = next((i for i,f in enumerate(fields) if 'gravedad' in f.lower()), None)
        data = []
        for rec in sf.iterRecords():
            try:
                lat = float(rec[idx_lat]) if idx_lat is not None else None
                lon = float(rec[idx_lon]) if idx_lon is not None else None
                if lat is None or lon is None:
                    continue
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    continue
                fecha_val = None
                if idx_fecha is not None:
                    d = rec[idx_fecha]
                    if hasattr(d, 'year'):
                        fecha_val = d
                    else:
                        try:
                            fecha_val = datetime.strptime(str(d)[:10], '%Y-%m-%d').date()
                        except Exception:
                            fecha_val = None
                tipo = str(rec[idx_veh]).strip() if idx_veh is not None else None
                loc = str(rec[idx_loc]).strip() if idx_loc is not None else None
                grav = str(rec[idx_grav]).strip() if idx_grav is not None else None
                data.append((lat, lon, fecha_val, tipo, loc, grav, 'shapefile'))
            except Exception:
                pass
        if not data:
            return jsonify({'success': False, 'message': 'No se obtuvieron registros válidos'}), 200
        cur.execute("DELETE FROM mpa_riesgo_accidentes WHERE fuente='shapefile'")
        cur.executemany(
            "INSERT INTO mpa_riesgo_accidentes (lat, lon, fecha, tipo_vehiculo, localidad, gravedad, fuente) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            data
        )
        conn.commit()
        cur.close(); conn.close()
        return jsonify({'success': True, 'inserted': len(data)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# API para obtener lista de vehículos
@app.route('/api/mpa/vehiculos', methods=['GET'])
@login_required
def api_get_vehiculos():
    """API para obtener la lista de vehículos"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        placa = (request.args.get('placa') or '').strip().upper()
        tecnico = (request.args.get('tecnico') or '').strip()
        where_parts = []
        params = []
        cursor.execute("SHOW TABLES LIKE 'mpa_vehiculos'")
        if not cursor.fetchone():
            return jsonify({'success': True, 'data': []})
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        ro_exists = cursor.fetchone() is not None

        cursor.execute("DESCRIBE mpa_vehiculos")
        cols_info = cursor.fetchall() or []
        col_names = set()
        for ci in cols_info:
            try:
                col_names.add(ci.get('Field') or ci.get('field') or ci[0])
            except Exception:
                pass

        select_cols = [
            "v.id_mpa_vehiculos",
            "v.placa",
            "v.tipo_vehiculo",
            "v.vin",
            "v.estado",
            "v.marca",
            "v.linea",
            "v.modelo",
            "v.color",
            "v.kilometraje_actual",
            "v.fecha_creacion",
            "v.tecnico_asignado",
            "v.observaciones"
        ]

        if 'numero_motor' in col_names:
            select_cols.append("v.numero_motor")
        elif 'numero_de_motor' in col_names:
            select_cols.append("v.numero_de_motor AS numero_motor")

        if 'cilindraje' in col_names:
            select_cols.append("v.cilindraje")
        elif 'cilindraje_cc' in col_names:
            select_cols.append("v.cilindraje_cc AS cilindraje")

        if 'fecha_matricula' in col_names:
            select_cols.append("v.fecha_matricula AS fecha_de_matricula")
        elif 'fecha_de_matricula' in col_names:
            select_cols.append("v.fecha_de_matricula")
        if ro_exists:
            select_cols.append("ro.nombre as tecnico_nombre")
        else:
            select_cols.append("CAST(v.tecnico_asignado AS CHAR) as tecnico_nombre")

        joins = []
        if ro_exists:
            joins.append("LEFT JOIN recurso_operativo ro ON v.tecnico_asignado = ro.id_codigo_consumidor")

        query = """
        SELECT {select_cols}
        FROM mpa_vehiculos v
        {joins}
        {where_clause}
        ORDER BY v.fecha_creacion DESC
        """
        if placa:
            where_parts.append("UPPER(TRIM(v.placa)) = %s")
            params.append(placa)
        if tecnico:
            where_parts.append("v.tecnico_asignado = %s")
            params.append(tecnico)
        where_clause = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
        query = query.format(select_cols=', '.join(select_cols), joins=' '.join(joins), where_clause=where_clause)
        print(f"/api/mpa/vehiculos placa={placa} tecnico={tecnico} where={where_clause}")
        cursor.execute(query, params)
        vehiculos = cursor.fetchall()
        print(f"/api/mpa/vehiculos resultados={len(vehiculos)}")
        
        # Formatear fechas para el frontend
        for vehiculo in vehiculos:
            if vehiculo.get('fecha_de_matricula'):
                vehiculo['fecha_de_matricula'] = vehiculo['fecha_de_matricula'].strftime('%Y-%m-%d')
            if vehiculo.get('fecha_creacion'):
                vehiculo['fecha_creacion'] = vehiculo['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'data': vehiculos
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/mpa/vehiculos/export', methods=['GET'])
@login_required
def api_export_vehiculos():
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        from flask import Response
        import io, csv
        placa = (request.args.get('placa') or '').strip().upper()
        tecnico = (request.args.get('tecnico') or '').strip()
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        where = []
        params = []
        where.append("v.estado = 'Activo'")
        presentado_dico_param = (request.args.get('presentado_dico') or request.args.get('presentados_dico') or '').strip().lower()
        apply_presentados = presentado_dico_param in ('si','true','1','yes')
        if apply_presentados:
            where.append("ro.estado = 'Activo'")
            where.append("ro.presentado_dico = 'SI'")
        if placa:
            where.append("v.placa = %s")
            params.append(placa)
        if tecnico:
            where.append("v.tecnico_asignado = %s")
            params.append(tecnico)
        sql = f"""
        SELECT 
            v.placa,
            v.tipo_vehiculo,
            v.marca,
            v.linea,
            v.modelo,
            v.color,
            ro.nombre AS tecnico_nombre,
            (
                SELECT s.fecha_vencimiento
                FROM mpa_soat s 
                WHERE s.placa = v.placa AND s.estado='Activo' AND s.fecha_vencimiento IS NOT NULL AND s.fecha_vencimiento > '1900-01-01'
                ORDER BY s.fecha_vencimiento DESC LIMIT 1
            ) AS soat_vencimiento,
            (
                SELECT tm.fecha_vencimiento
                FROM mpa_tecnico_mecanica tm 
                WHERE tm.placa = v.placa AND tm.estado='Activo' AND tm.fecha_vencimiento IS NOT NULL AND tm.fecha_vencimiento > '1900-01-01'
                ORDER BY tm.fecha_vencimiento DESC LIMIT 1
            ) AS tecnomecanica_vencimiento,
            (
                SELECT lc.tipo_licencia
                FROM mpa_licencia_conducir lc 
                WHERE lc.tecnico = v.tecnico_asignado AND lc.fecha_vencimiento IS NOT NULL AND lc.fecha_vencimiento > '1900-01-01'
                ORDER BY lc.fecha_vencimiento DESC LIMIT 1
            ) AS licencia_tipo,
            (
                SELECT lc2.fecha_vencimiento
                FROM mpa_licencia_conducir lc2 
                WHERE lc2.tecnico = v.tecnico_asignado AND lc2.fecha_vencimiento IS NOT NULL AND lc2.fecha_vencimiento > '1900-01-01'
                ORDER BY lc2.fecha_vencimiento DESC LIMIT 1
            ) AS licencia_vencimiento
        FROM mpa_vehiculos v
        LEFT JOIN recurso_operativo ro ON v.tecnico_asignado = ro.id_codigo_consumidor
        {('WHERE ' + ' AND '.join(where)) if where else ''}
        ORDER BY v.placa ASC
        """
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Placa','Tipo Vehículo','Marca','Línea','Modelo','Color','Técnico Asignado',
            'Vencimiento SOAT','Vencimiento Tecnomecánica','Tipo Licencia','Vencimiento Licencia'
        ])
        for r in rows:
            soat = r['soat_vencimiento'].strftime('%Y-%m-%d') if r['soat_vencimiento'] else ''
            tm = r['tecnomecanica_vencimiento'].strftime('%Y-%m-%d') if r['tecnomecanica_vencimiento'] else ''
            lic_v = r['licencia_vencimiento'].strftime('%Y-%m-%d') if r['licencia_vencimiento'] else ''
            writer.writerow([
                r['placa'] or '', r['tipo_vehiculo'] or '', r['marca'] or '', r['linea'] or '', r['modelo'] or '', r['color'] or '',
                r['tecnico_nombre'] or '', soat, tm, r['licencia_tipo'] or '', lic_v
            ])
        cursor.close(); connection.close()
        csv_data = output.getvalue()
        resp = Response(csv_data, mimetype='text/csv')
        resp.headers['Content-Disposition'] = f"attachment; filename=vehiculos_export{('_'+placa) if placa else ''}.csv"
        return resp
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# API para crear un nuevo vehículo
@app.route('/api/mpa/vehiculos', methods=['POST'])
@login_required
def api_create_vehiculo():
    """API para crear un nuevo vehículo"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['cedula_propietario', 'nombre_propietario', 'placa', 'tipo_vehiculo']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'El campo {field} es requerido'}), 400
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor()
        
        # Verificar si ya existe un vehículo con la misma placa
        cursor.execute("SELECT id_mpa_vehiculos FROM mpa_vehiculos WHERE placa = %s", (data['placa'],))
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Ya existe un vehículo con esta placa'}), 400
        
        # Obtener fecha actual en zona horaria de Bogotá
        from pytz import timezone
        bogota_tz = timezone('America/Bogota')
        fecha_creacion = datetime.now(bogota_tz).strftime('%Y-%m-%d %H:%M:%S')
        
        insert_query = """
        INSERT INTO mpa_vehiculos (
            cedula_propietario, nombre_propietario, placa, tipo_vehiculo, vin,
            numero_de_motor, fecha_de_matricula, estado, marca, linea, modelo,
            color, kilometraje_actual, fecha_creacion, tecnico_asignado, observaciones
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data.get('cedula_propietario'),
            data.get('nombre_propietario'),
            data.get('placa'),
            data.get('tipo_vehiculo'),
            data.get('vin'),
            data.get('numero_de_motor'),
            data.get('fecha_de_matricula'),
            data.get('estado', 'Activo'),
            data.get('marca'),
            data.get('linea'),
            data.get('modelo'),
            data.get('color'),
            data.get('kilometraje_actual'),
            fecha_creacion,
            data.get('tecnico_asignado'),
            data.get('observaciones')
        )
        cursor.execute(insert_query, values)
        vehiculo_id = cursor.lastrowid
        created = {'vehiculo_id': vehiculo_id}

        s = data.get('soat')
        if isinstance(s, dict):
            sp = s.get('numero_poliza')
            sa = s.get('aseguradora')
            sv = s.get('valor_prima')
            sfi = s.get('fecha_inicio')
            sfv = s.get('fecha_vencimiento')
            if sp and sa and sv and sfi and sfv:
                cursor.execute("SELECT id_mpa_soat FROM mpa_soat WHERE placa = %s AND estado = 'Activo' AND fecha_vencimiento >= CURDATE()", (data.get('placa'),))
                if cursor.fetchone():
                    created['soat_skipped'] = 'Ya existe SOAT activo'
                else:
                    cursor.execute(
                        """
                        INSERT INTO mpa_soat (
                            placa, numero_poliza, aseguradora, fecha_inicio, fecha_vencimiento,
                            valor_prima, tecnico_asignado, estado, observaciones, fecha_creacion
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            data.get('placa'), sp, sa, sfi, sfv,
                            sv, data.get('tecnico_asignado'), s.get('estado', 'Activo'), s.get('observaciones', ''), fecha_creacion
                        )
                    )
                    created['soat_id'] = cursor.lastrowid
            else:
                created['soat_skipped'] = 'Campos incompletos'

        tm = data.get('tecnico_mecanica')
        if isinstance(tm, dict):
            tfi = tm.get('fecha_inicio')
            tfv = tm.get('fecha_vencimiento')
            if tfi and tfv:
                cursor.execute("SELECT id_mpa_tecnico_mecanica FROM mpa_tecnico_mecanica WHERE placa = %s AND estado = 'Activo'", (data.get('placa'),))
                if cursor.fetchone():
                    created['tm_skipped'] = 'Ya existe revisión activa'
                else:
                    cursor.execute(
                        """
                        INSERT INTO mpa_tecnico_mecanica (
                            placa, fecha_inicio, fecha_vencimiento, tecnico_asignado, tipo_vehiculo, estado, observaciones, fecha_creacion
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            data.get('placa'), tfi, tfv, data.get('tecnico_asignado'), data.get('tipo_vehiculo'), tm.get('estado', 'Activo'), tm.get('observaciones', ''), fecha_creacion
                        )
                    )
                    created['tm_id'] = cursor.lastrowid
            else:
                created['tm_skipped'] = 'Campos incompletos'

        lic = data.get('licencia')
        if isinstance(lic, dict):
            tl = lic.get('tipo_licencia')
            lfi = lic.get('fecha_inicial')
            lfv = lic.get('fecha_vencimiento')
            tech_id = lic.get('tecnico_id') or data.get('tecnico_asignado')
            if tl and lfi and lfv and tech_id:
                cursor.execute("SELECT id_mpa_licencia_conducir FROM mpa_licencia_conducir WHERE tecnico = %s AND fecha_vencimiento > CURDATE()", (tech_id,))
                if cursor.fetchone():
                    created['licencia_skipped'] = 'Ya existe licencia vigente'
                else:
                    cursor.execute(
                        """
                        INSERT INTO mpa_licencia_conducir (
                            tecnico, tipo_licencia, fecha_inicio, fecha_vencimiento, observacion, fecha_creacion
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            tech_id, tl, lfi, lfv, lic.get('observacion', ''), fecha_creacion
                        )
                    )
                    created['licencia_id'] = cursor.lastrowid
            else:
                created['licencia_skipped'] = 'Campos incompletos'

        connection.commit()

        return jsonify({
            'success': True,
            'message': 'Vehículo creado exitosamente',
            'id': vehiculo_id,
            'created': created
        })
        
    except Exception as e:
        if 'connection' in locals() and connection:
            connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para obtener un vehículo específico
@app.route('/api/mpa/vehiculos/<int:vehiculo_id>', methods=['GET'])
@login_required
def api_get_vehiculo(vehiculo_id):
    """API para obtener un vehículo específico"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT 
            v.*,
            ro.nombre as tecnico_nombre
        FROM mpa_vehiculos v
        LEFT JOIN recurso_operativo ro ON v.tecnico_asignado = ro.id_codigo_consumidor
        WHERE v.id_mpa_vehiculos = %s
        """
        
        cursor.execute(query, (vehiculo_id,))
        vehiculo = cursor.fetchone()
        
        if not vehiculo:
            return jsonify({'success': False, 'error': 'Vehículo no encontrado'}), 404
        
        # Consultar dinámicamente el último kilometraje desde preoperacional según columna existente
        try:
            km_col = None
            cursor2 = connection.cursor()
            try:
                cursor2.execute("SHOW COLUMNS FROM preoperacional LIKE 'kilometraje'")
                if cursor2.fetchone():
                    km_col = 'kilometraje'
                else:
                    cursor2.execute("SHOW COLUMNS FROM preoperacional LIKE 'kilometraje_actual'")
                    if cursor2.fetchone():
                        km_col = 'kilometraje_actual'
            except Exception:
                km_col = None
            if km_col:
                cursor2.execute(
                    f"""
                    SELECT p.{km_col} AS km
                    FROM preoperacional p
                    WHERE p.placa_vehiculo = %s
                    ORDER BY p.fecha DESC
                    LIMIT 1
                    """,
                    (vehiculo['placa'],)
                )
                row = cursor2.fetchone()
                if row and row[0] is not None:
                    vehiculo['kilometraje_actual'] = row[0]
            cursor2.close()
        except Exception:
            try:
                cursor2.close()
            except Exception:
                pass
        # Formatear fechas
        if vehiculo['fecha_de_matricula']:
            vehiculo['fecha_de_matricula'] = vehiculo['fecha_de_matricula'].strftime('%Y-%m-%d')
        if vehiculo['fecha_creacion']:
            vehiculo['fecha_creacion'] = vehiculo['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'data': vehiculo
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para actualizar un vehículo
@app.route('/api/mpa/vehiculos/<int:vehiculo_id>', methods=['PUT'])
@login_required
def api_update_vehiculo(vehiculo_id):
    """API para actualizar un vehículo y opcionalmente sus registros relacionados (SOAT, Técnico Mecánica y Licencia)"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        data = request.get_json()
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor()
        
        # Verificar si el vehículo existe
        cursor.execute("SELECT id_mpa_vehiculos FROM mpa_vehiculos WHERE id_mpa_vehiculos = %s", (vehiculo_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Vehículo no encontrado'}), 404
        
        # Verificar si la placa ya existe en otro vehículo
        if data.get('placa'):
            cursor.execute(
                "SELECT id_mpa_vehiculos FROM mpa_vehiculos WHERE placa = %s AND id_mpa_vehiculos != %s", 
                (data['placa'], vehiculo_id)
            )
            if cursor.fetchone():
                return jsonify({'success': False, 'error': 'Ya existe otro vehículo con esta placa'}), 400
        
        # Construir query de actualización dinámicamente
        update_fields = []
        values = []
        
        allowed_fields = [
            'cedula_propietario', 'nombre_propietario', 'placa', 'tipo_vehiculo', 'vin',
            'numero_de_motor', 'fecha_de_matricula', 'estado', 'marca', 'linea', 'modelo',
            'color', 'kilometraje_actual', 'tecnico_asignado', 'observaciones'
        ]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                values.append(data[field])
        
        if not update_fields:
            return jsonify({'success': False, 'error': 'No hay campos para actualizar'}), 400
        
        values.append(vehiculo_id)
        update_query = f"UPDATE mpa_vehiculos SET {', '.join(update_fields)} WHERE id_mpa_vehiculos = %s"
        
        cursor.execute(update_query, values)
        updated = {'vehiculo_id': vehiculo_id}

        s = data.get('soat')
        if isinstance(s, dict):
            try:
                sp = s.get('numero_poliza')
                sa = s.get('aseguradora')
                sv = s.get('valor_prima')
                sfi = s.get('fecha_inicio')
                sfv = s.get('fecha_vencimiento')
                fecha_actual = get_bogota_datetime().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("SELECT id_mpa_soat FROM mpa_soat WHERE placa = (SELECT placa FROM mpa_vehiculos WHERE id_mpa_vehiculos=%s) AND estado='Activo'", (vehiculo_id,))
                row = cursor.fetchone()
                if row:
                    soat_id = row[0]
                    up_fields = []
                    vals = []
                    if sp: up_fields.append("numero_poliza=%s"); vals.append(sp)
                    if sa: up_fields.append("aseguradora=%s"); vals.append(sa)
                    if sv: up_fields.append("valor_prima=%s"); vals.append(sv)
                    if sfi: up_fields.append("fecha_inicio=%s"); vals.append(sfi)
                    if sfv: up_fields.append("fecha_vencimiento=%s"); vals.append(sfv)
                    if 'observaciones' in s: up_fields.append("observaciones=%s"); vals.append(s.get('observaciones',''))
                    if 'estado' in s: up_fields.append("estado=%s"); vals.append(s.get('estado','Activo'))
                    if 'tecnico_asignado' in s: up_fields.append("tecnico_asignado=%s"); vals.append(s.get('tecnico_asignado'))
                    if up_fields:
                        up_fields.append("fecha_actualizacion=%s"); vals.append(fecha_actual)
                        vals.append(soat_id)
                        cursor.execute(f"UPDATE mpa_soat SET {', '.join(up_fields)} WHERE id_mpa_soat=%s", tuple(vals))
                        updated['soat_id'] = soat_id
                else:
                    placa = data.get('placa')
                    if placa and sp and sa and sv and sfi and sfv:
                        cursor.execute(
                            """
                            INSERT INTO mpa_soat (
                                placa, numero_poliza, aseguradora, fecha_inicio, fecha_vencimiento,
                                valor_prima, tecnico_asignado, estado, observaciones, fecha_creacion
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                placa, sp, sa, sfi, sfv,
                                s.get('tecnico_asignado', data.get('tecnico_asignado')), s.get('estado','Activo'), s.get('observaciones',''), fecha_actual
                            )
                        )
                        updated['soat_id'] = cursor.lastrowid
            except Exception as e:
                updated['soat_error'] = str(e)

        tm = data.get('tecnico_mecanica')
        if isinstance(tm, dict):
            try:
                tfi = tm.get('fecha_inicio')
                tfv = tm.get('fecha_vencimiento')
                cursor.execute("SELECT placa, tipo_vehiculo FROM mpa_vehiculos WHERE id_mpa_vehiculos=%s", (vehiculo_id,))
                vr = cursor.fetchone()
                placa = data.get('placa') or (vr[0] if vr else None)
                tipo_v = data.get('tipo_vehiculo') or (vr[1] if vr else None)
                cursor.execute("SELECT id_mpa_tecnico_mecanica FROM mpa_tecnico_mecanica WHERE placa=%s AND estado='Activo'", (placa,))
                row = cursor.fetchone()
                if row:
                    tm_id = row[0]
                    up_fields = []
                    vals = []
                    if tfi: up_fields.append("fecha_inicio=%s"); vals.append(tfi)
                    if tfv: up_fields.append("fecha_vencimiento=%s"); vals.append(tfv)
                    if 'observaciones' in tm: up_fields.append("observaciones=%s"); vals.append(tm.get('observaciones',''))
                    if 'estado' in tm: up_fields.append("estado=%s"); vals.append(tm.get('estado','Activo'))
                    if 'tecnico_asignado' in data: up_fields.append("tecnico_asignado=%s"); vals.append(data.get('tecnico_asignado'))
                    if 'tipo_vehiculo' in data or tipo_v: up_fields.append("tipo_vehiculo=%s"); vals.append(data.get('tipo_vehiculo', tipo_v))
                    if up_fields:
                        up_fields.append("fecha_actualizacion=NOW()")
                        vals.append(tm_id)
                        cursor.execute(f"UPDATE mpa_tecnico_mecanica SET {', '.join(up_fields)} WHERE id_mpa_tecnico_mecanica=%s", tuple(vals))
                        updated['tm_id'] = tm_id
                else:
                    if placa and tfi and tfv:
                        cursor.execute(
                            """
                            INSERT INTO mpa_tecnico_mecanica (
                                placa, fecha_inicio, fecha_vencimiento, tecnico_asignado, tipo_vehiculo, estado, observaciones, fecha_creacion
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                            """,
                            (
                                placa, tfi, tfv, data.get('tecnico_asignado'), data.get('tipo_vehiculo', tipo_v), tm.get('estado','Activo'), tm.get('observaciones','')
                            )
                        )
                        updated['tm_id'] = cursor.lastrowid
            except Exception as e:
                updated['tm_error'] = str(e)

        lic = data.get('licencia')
        if isinstance(lic, dict):
            try:
                tl = lic.get('tipo_licencia')
                lfi = lic.get('fecha_inicial')
                lfv = lic.get('fecha_vencimiento')
                tech_id = lic.get('tecnico_id') or data.get('tecnico_asignado')
                if tech_id:
                    cursor.execute("SELECT id_mpa_licencia_conducir FROM mpa_licencia_conducir WHERE tecnico=%s AND fecha_vencimiento>CURDATE()", (tech_id,))
                    row = cursor.fetchone()
                    if row:
                        lic_id = row[0]
                        up_fields = []
                        vals = []
                        if tl: up_fields.append("tipo_licencia=%s"); vals.append(tl)
                        if lfi: up_fields.append("fecha_inicio=%s"); vals.append(lfi)
                        if lfv: up_fields.append("fecha_vencimiento=%s"); vals.append(lfv)
                        if 'observacion' in lic or 'observaciones' in lic:
                            up_fields.append("observacion=%s"); vals.append(lic.get('observacion', lic.get('observaciones','')))
                        up_fields.append("fecha_actualizacion=NOW()")
                        vals.append(lic_id)
                        cursor.execute(f"UPDATE mpa_licencia_conducir SET {', '.join(up_fields)} WHERE id_mpa_licencia_conducir=%s", tuple(vals))
                        updated['licencia_id'] = lic_id
                    else:
                        if tl and lfi and lfv:
                            cursor.execute(
                                """
                                INSERT INTO mpa_licencia_conducir (
                                    tecnico, tipo_licencia, fecha_inicio, fecha_vencimiento, observacion, fecha_creacion
                                ) VALUES (%s, %s, %s, %s, %s, NOW())
                                """,
                                (
                                    tech_id, tl, lfi, lfv, lic.get('observacion', lic.get('observaciones',''))
                                )
                            )
                            updated['licencia_id'] = cursor.lastrowid
            except Exception as e:
                updated['licencia_error'] = str(e)

        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vehículo actualizado exitosamente',
            'updated': updated
        })
        
    except Exception as e:
        if 'connection' in locals() and connection:
            connection.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para eliminar un vehículo
@app.route('/api/mpa/vehiculos/<int:vehiculo_id>', methods=['DELETE'])
@login_required
def api_delete_vehiculo(vehiculo_id):
    """API para eliminar un vehículo"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor()
        
        # Verificar si el vehículo existe
        cursor.execute("SELECT id_mpa_vehiculos FROM mpa_vehiculos WHERE id_mpa_vehiculos = %s", (vehiculo_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Vehículo no encontrado'}), 404
        
        # Eliminar vehículo
        cursor.execute("DELETE FROM mpa_vehiculos WHERE id_mpa_vehiculos = %s", (vehiculo_id,))
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vehículo eliminado exitosamente'
        })
        
    except Exception as e:
        if 'connection' in locals() and connection:
            connection.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para importar vehículos desde Excel/CSV
@app.route('/api/mpa/vehiculos/import-excel', methods=['POST'])
@login_required
def api_import_vehiculos_excel():
    """Importa vehículos a la tabla mpa_vehiculos desde un archivo Excel o CSV"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No se adjuntó archivo'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Nombre de archivo vacío'}), 400
        
        # Intentar leer el archivo con pandas; si no está instalado, retornar error claro
        try:
            import pandas as pd
            from io import BytesIO
        except Exception:
            return jsonify({'success': False, 'message': 'Dependencia faltante: pandas. Por favor instalar para lectura de Excel/CSV.'}), 500
        
        file_bytes = file.read()
        buffer = BytesIO(file_bytes)
        
        # Detectar formato por extensión
        ext = (file.filename.split('.')[-1] or '').lower()
        df = None

        def read_csv_auto(buf):
            """Leer CSV detectando separador y codificación (maneja BOM y ';')."""
            for enc in ['utf-8-sig', 'latin1', 'utf-8']:
                buf.seek(0)
                try:
                    # Intento con autodetección de separador
                    df_local = pd.read_csv(buf, sep=None, engine='python', encoding=enc)
                    # Si vino todo en una sola columna con ';' en el encabezado, reintentar con ';'
                    if df_local.shape[1] == 1 and ';' in str(df_local.columns[0]):
                        buf.seek(0)
                        df_local = pd.read_csv(buf, sep=';', encoding=enc)
                    return df_local
                except Exception:
                    continue
            raise ValueError('CSV no legible: encoding/sep')

        try:
            if ext in ['xlsx', 'xls']:
                df = pd.read_excel(buffer)
            else:
                df = read_csv_auto(buffer)
        except Exception as e:
            return jsonify({'success': False, 'message': 'No se pudo leer el archivo. Verifique formato Excel/CSV.', 'error': str(e)}), 400
        
        # Normalizar encabezados y eliminar BOM
        df.columns = [str(c).strip().lower().lstrip('\ufeff') for c in df.columns]
        # Mapear posibles alias de columnas
        alias = {
            'numero_motor': 'numero_de_motor',
            'fecha_matricula': 'fecha_de_matricula',
            'tipo': 'tipo_vehiculo',
            'tecnico': 'tecnico_asignado'
        }
        df.rename(columns=alias, inplace=True)
        
        # Columnas requeridas mínimas según creación de vehículo
        required_cols = ['cedula_propietario', 'nombre_propietario', 'placa', 'tipo_vehiculo']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            return jsonify({'success': False, 'message': f'Columnas faltantes: {", ".join(missing)}'}), 400
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = conn.cursor(dictionary=True)
        
        inserted = 0
        updated = 0
        skipped = 0
        
        for _, row in df.iterrows():
            # Tomar valores con saneamiento básico
            placa = (str(row.get('placa')) if row.get('placa') is not None else '').strip().upper()
            if not placa:
                skipped += 1
                continue
            
            cedula_propietario = (str(row.get('cedula_propietario')) if row.get('cedula_propietario') is not None else '').strip()
            nombre_propietario = (str(row.get('nombre_propietario')) if row.get('nombre_propietario') is not None else '').strip()
            tipo_vehiculo = (str(row.get('tipo_vehiculo')) if row.get('tipo_vehiculo') is not None else '').strip()
            vin = (str(row.get('vin')) if row.get('vin') is not None else '').strip() or None
            numero_de_motor = (str(row.get('numero_de_motor')) if row.get('numero_de_motor') is not None else '').strip() or None
            estado = (str(row.get('estado')) if row.get('estado') is not None else 'Activo').strip() or 'Activo'
            marca = (str(row.get('marca')) if row.get('marca') is not None else '').strip() or None
            linea = (str(row.get('linea')) if row.get('linea') is not None else '').strip() or None
            color = (str(row.get('color')) if row.get('color') is not None else '').strip() or None
            observaciones = (str(row.get('observaciones')) if row.get('observaciones') is not None else '').strip() or None
            
            # Numericos y fechas
            try:
                modelo = int(row.get('modelo')) if row.get('modelo') is not None and str(row.get('modelo')).strip() != '' else None
            except Exception:
                modelo = None
            try:
                kilometraje_actual = int(row.get('kilometraje_actual')) if row.get('kilometraje_actual') is not None else 0
            except Exception:
                kilometraje_actual = 0
            
            fecha_de_matricula = None
            if row.get('fecha_de_matricula') is not None and str(row.get('fecha_de_matricula')).strip() != '':
                try:
                    fecha_de_matricula = pd.to_datetime(row.get('fecha_de_matricula')).date()
                except Exception:
                    fecha_de_matricula = None
            
            # Técnico asignado opcional
            tecnico_asignado = None
            if 'tecnico_asignado' in df.columns:
                val = row.get('tecnico_asignado')
                if val is not None and str(val).strip() != '':
                    tecnico_asignado = str(val).strip()
            
            # Validación mínima
            if not cedula_propietario or not nombre_propietario or not tipo_vehiculo:
                skipped += 1
                continue
            
            # ¿Existe por placa?
            cursor.execute("SELECT id_mpa_vehiculos FROM mpa_vehiculos WHERE placa = %s", (placa,))
            existing = cursor.fetchone()
            
            if existing:
                # Actualización
                cursor.execute(
                    """
                    UPDATE mpa_vehiculos
                    SET cedula_propietario=%s, nombre_propietario=%s, tipo_vehiculo=%s, vin=%s,
                        numero_de_motor=%s, fecha_de_matricula=%s, estado=%s, marca=%s, linea=%s,
                        modelo=%s, color=%s, kilometraje_actual=%s, tecnico_asignado=%s, observaciones=%s
                    WHERE id_mpa_vehiculos=%s
                    """,
                    (
                        cedula_propietario, nombre_propietario, tipo_vehiculo, vin,
                        numero_de_motor, fecha_de_matricula, estado, marca, linea,
                        modelo, color, kilometraje_actual, tecnico_asignado, observaciones,
                        existing['id_mpa_vehiculos']
                    )
                )
                updated += 1
            else:
                # Inserción
                cursor.execute(
                    """
                    INSERT INTO mpa_vehiculos (
                        cedula_propietario, nombre_propietario, placa, tipo_vehiculo, vin,
                        numero_de_motor, fecha_de_matricula, estado, marca, linea, modelo, color,
                        kilometraje_actual, fecha_creacion, tecnico_asignado, observaciones
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        cedula_propietario, nombre_propietario, placa, tipo_vehiculo, vin,
                        numero_de_motor, fecha_de_matricula, estado, marca, linea, modelo, color,
                        kilometraje_actual, get_bogota_datetime().strftime('%Y-%m-%d %H:%M:%S'), tecnico_asignado, observaciones
                    )
                )
                inserted += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'inserted': inserted, 'updated': updated, 'skipped': skipped})
    except Exception as e:
        if 'conn' in locals() and conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return jsonify({'success': False, 'message': 'Error procesando archivo', 'error': str(e)}), 500

# API para importar Técnico Mecánica desde Excel/CSV
@app.route('/api/mpa/tecnico_mecanica/import-excel', methods=['POST'])
@login_required
def api_import_tecnico_mecanica_excel():
    """Importa registros a la tabla mpa_tecnico_mecanica desde un archivo Excel o CSV"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No se adjuntó archivo'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Nombre de archivo vacío'}), 400
        
        try:
            import pandas as pd
            from io import BytesIO
        except Exception:
            return jsonify({'success': False, 'message': 'Dependencia faltante: pandas. Por favor instalar para lectura de Excel/CSV.'}), 500
        
        def read_csv_auto(buf):
            for enc in ['utf-8-sig', 'latin1', 'utf-8']:
                buf.seek(0)
                try:
                    df_local = pd.read_csv(buf, sep=None, engine='python', encoding=enc)
                    if df_local.shape[1] == 1 and ';' in str(df_local.columns[0]):
                        buf.seek(0)
                        df_local = pd.read_csv(buf, sep=';', encoding=enc)
                    return df_local
                except Exception:
                    continue
            raise ValueError('CSV no legible: encoding/sep')
        
        file_bytes = file.read()
        buffer = BytesIO(file_bytes)
        ext = (file.filename.split('.')[-1] or '').lower()
        
        try:
            df = pd.read_excel(buffer) if ext in ['xlsx', 'xls'] else read_csv_auto(buffer)
        except Exception as e:
            return jsonify({'success': False, 'message': 'No se pudo leer el archivo. Verifique formato Excel/CSV.', 'error': str(e)}), 400
        
        df.columns = [str(c).strip().lower().lstrip('\ufeff') for c in df.columns]
        alias = {
            'fecha_inicial': 'fecha_inicio',
            'tipo': 'tipo_vehiculo'
        }
        df.rename(columns=alias, inplace=True)
        
        required_cols = ['placa', 'fecha_inicio', 'fecha_vencimiento']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            return jsonify({'success': False, 'message': f'Columnas faltantes: {", ".join(missing)}'}), 400
        
        def parse_date(val):
            try:
                s = str(val).strip()
                if s == '' or s.upper() in ['NA', 'N/A'] or s.startswith('0/01/1900'):
                    return None
                return pd.to_datetime(s, dayfirst=True, errors='coerce').date() if pd.to_datetime(s, dayfirst=True, errors='coerce') is not pd.NaT else None
            except Exception:
                return None
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = conn.cursor(dictionary=True)
        
        inserted = 0
        updated = 0
        skipped = 0
        
        for _, row in df.iterrows():
            placa = (str(row.get('placa')) if row.get('placa') is not None else '').strip().upper()
            if not placa:
                skipped += 1
                continue
            
            fecha_inicio = parse_date(row.get('fecha_inicio'))
            fecha_vencimiento = parse_date(row.get('fecha_vencimiento'))
            tecnico_asignado = None
            if 'tecnico_asignado' in df.columns:
                val = row.get('tecnico_asignado')
                if val is not None and str(val).strip() != '':
                    tecnico_asignado = str(val).strip()
            estado = (str(row.get('estado')) if row.get('estado') is not None else 'Activo').strip() or 'Activo'
            tipo_vehiculo = None
            if 'tipo_vehiculo' in df.columns:
                tv = str(row.get('tipo_vehiculo')) if row.get('tipo_vehiculo') is not None else ''
                tipo_vehiculo = tv.strip() or None
            observaciones = (str(row.get('observaciones')) if row.get('observaciones') is not None else '').strip() or None
            
            # Completar técnico y tipo_vehiculo desde mpa_vehiculos si faltan
            cursor.execute("SELECT tecnico_asignado, tipo_vehiculo FROM mpa_vehiculos WHERE placa = %s", (placa,))
            veh = cursor.fetchone()
            if veh:
                if not tecnico_asignado:
                    tecnico_asignado = veh.get('tecnico_asignado')
                if not tipo_vehiculo:
                    tipo_vehiculo = veh.get('tipo_vehiculo')
            
            # Buscar registro activo existente
            cursor.execute("""
                SELECT id_mpa_tecnico_mecanica FROM mpa_tecnico_mecanica
                WHERE placa = %s AND estado = 'Activo'
                ORDER BY fecha_vencimiento DESC LIMIT 1
            """, (placa,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute(
                    """
                    UPDATE mpa_tecnico_mecanica
                    SET fecha_inicio=%s, fecha_vencimiento=%s, tecnico_asignado=%s,
                        tipo_vehiculo=%s, estado=%s, observaciones=%s, fecha_actualizacion=NOW()
                    WHERE id_mpa_tecnico_mecanica=%s
                    """,
                    (fecha_inicio, fecha_vencimiento, tecnico_asignado, tipo_vehiculo, estado, observaciones, existing['id_mpa_tecnico_mecanica'])
                )
                updated += 1
            else:
                cursor.execute(
                    """
                    INSERT INTO mpa_tecnico_mecanica (
                        placa, fecha_inicio, fecha_vencimiento, tecnico_asignado,
                        tipo_vehiculo, estado, observaciones, fecha_creacion
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    """,
                    (placa, fecha_inicio, fecha_vencimiento, tecnico_asignado, tipo_vehiculo, estado, observaciones)
                )
                inserted += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'inserted': inserted, 'updated': updated, 'skipped': skipped})
    except Exception as e:
        if 'conn' in locals() and conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return jsonify({'success': False, 'message': 'Error procesando archivo', 'error': str(e)}), 500

# API para importar SOAT desde Excel/CSV
@app.route('/api/mpa/soat/import-excel', methods=['POST'])
@login_required
def api_import_soat_excel():
    """Importa registros a la tabla mpa_soat desde un archivo Excel o CSV"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No se adjuntó archivo'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Nombre de archivo vacío'}), 400
        
        try:
            import pandas as pd
            from io import BytesIO
        except Exception:
            return jsonify({'success': False, 'message': 'Dependencia faltante: pandas. Por favor instalar para lectura de Excel/CSV.'}), 500
        
        def read_csv_auto(buf):
            for enc in ['utf-8-sig', 'latin1', 'utf-8']:
                buf.seek(0)
                try:
                    df_local = pd.read_csv(buf, sep=None, engine='python', encoding=enc)
                    if df_local.shape[1] == 1 and ';' in str(df_local.columns[0]):
                        buf.seek(0)
                        df_local = pd.read_csv(buf, sep=';', encoding=enc)
                    return df_local
                except Exception:
                    continue
            raise ValueError('CSV no legible: encoding/sep')
        
        file_bytes = file.read()
        buffer = BytesIO(file_bytes)
        ext = (file.filename.split('.')[-1] or '').lower()
        
        try:
            df = pd.read_excel(buffer) if ext in ['xlsx', 'xls'] else read_csv_auto(buffer)
        except Exception as e:
            return jsonify({'success': False, 'message': 'No se pudo leer el archivo. Verifique formato Excel/CSV.', 'error': str(e)}), 400
        
        df.columns = [str(c).strip().lower().lstrip('\ufeff') for c in df.columns]
        
        required_cols = ['placa', 'fecha_inicio', 'fecha_vencimiento']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            return jsonify({'success': False, 'message': f'Columnas faltantes: {", ".join(missing)}'}), 400
        
        def parse_date(val):
            try:
                s = str(val).strip()
                if s == '' or s.upper() in ['NA', 'N/A'] or s.startswith('0/01/1900'):
                    return None
                return pd.to_datetime(s, dayfirst=True, errors='coerce').date() if pd.to_datetime(s, dayfirst=True, errors='coerce') is not pd.NaT else None
            except Exception:
                return None
        
        def parse_float(val):
            try:
                s = str(val).replace(',', '').strip()
                return float(s) if s != '' else None
            except Exception:
                return None
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = conn.cursor(dictionary=True)
        
        inserted = 0
        updated = 0
        skipped = 0
        
        for _, row in df.iterrows():
            placa = (str(row.get('placa')) if row.get('placa') is not None else '').strip().upper()
            if not placa:
                skipped += 1
                continue
            
            fecha_inicio = parse_date(row.get('fecha_inicio'))
            fecha_vencimiento = parse_date(row.get('fecha_vencimiento'))
            valor_prima = parse_float(row.get('valor_prima'))
            tecnico_asignado = None
            if 'tecnico_asignado' in df.columns:
                val = row.get('tecnico_asignado')
                if val is not None and str(val).strip() != '':
                    tecnico_asignado = str(val).strip()
            estado = (str(row.get('estado')) if row.get('estado') is not None else 'Activo').strip() or 'Activo'
            numero_poliza = (str(row.get('numero_poliza')) if row.get('numero_poliza') is not None else '').strip() or None
            aseguradora = (str(row.get('aseguradora')) if row.get('aseguradora') is not None else '').strip() or None
            observaciones = (str(row.get('observaciones')) if row.get('observaciones') is not None else '').strip() or None
            
            # Completar técnico desde mpa_vehiculos si falta
            cursor.execute("SELECT tecnico_asignado FROM mpa_vehiculos WHERE placa = %s", (placa,))
            veh = cursor.fetchone()
            if veh and not tecnico_asignado:
                tecnico_asignado = veh.get('tecnico_asignado')
            
            # Buscar SOAT activo existente por placa
            cursor.execute("""
                SELECT id_mpa_soat FROM mpa_soat
                WHERE placa = %s AND estado = 'Activo'
                ORDER BY fecha_vencimiento DESC LIMIT 1
            """, (placa,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute(
                    """
                    UPDATE mpa_soat
                    SET numero_poliza=%s, aseguradora=%s, fecha_inicio=%s, fecha_vencimiento=%s,
                        valor_prima=%s, tecnico_asignado=%s, estado=%s, observaciones=%s, fecha_actualizacion=NOW()
                    WHERE id_mpa_soat=%s
                    """,
                    (numero_poliza, aseguradora, fecha_inicio, fecha_vencimiento, valor_prima, tecnico_asignado, estado, observaciones, existing['id_mpa_soat'])
                )
                updated += 1
            else:
                cursor.execute(
                    """
                    INSERT INTO mpa_soat (
                        placa, numero_poliza, aseguradora, fecha_inicio, fecha_vencimiento,
                        valor_prima, tecnico_asignado, estado, observaciones, fecha_creacion
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """,
                    (placa, numero_poliza, aseguradora, fecha_inicio, fecha_vencimiento, valor_prima, tecnico_asignado, estado, observaciones)
                )
                inserted += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'inserted': inserted, 'updated': updated, 'skipped': skipped})
    except Exception as e:
        if 'conn' in locals() and conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return jsonify({'success': False, 'message': 'Error procesando archivo', 'error': str(e)}), 500

# API para importar Licencias de Conducir desde Excel/CSV
@app.route('/api/mpa/licencias-conducir/import-excel', methods=['POST'])
@login_required
def api_import_licencias_excel():
    """Importa registros a la tabla mpa_licencia_conducir desde un archivo Excel o CSV"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No se adjuntó archivo'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Nombre de archivo vacío'}), 400
        
        try:
            import pandas as pd
            from io import BytesIO
        except Exception:
            return jsonify({'success': False, 'message': 'Dependencia faltante: pandas. Por favor instalar para lectura de Excel/CSV.'}), 500
        
        def read_csv_auto(buf):
            for enc in ['utf-8-sig', 'latin1', 'utf-8']:
                buf.seek(0)
                try:
                    df_local = pd.read_csv(buf, sep=None, engine='python', encoding=enc)
                    if df_local.shape[1] == 1 and ';' in str(df_local.columns[0]):
                        buf.seek(0)
                        df_local = pd.read_csv(buf, sep=';', encoding=enc)
                    return df_local
                except Exception:
                    continue
            raise ValueError('CSV no legible: encoding/sep')
        
        file_bytes = file.read()
        buffer = BytesIO(file_bytes)
        ext = (file.filename.split('.')[-1] or '').lower()
        
        try:
            df = pd.read_excel(buffer) if ext in ['xlsx', 'xls'] else read_csv_auto(buffer)
        except Exception as e:
            return jsonify({'success': False, 'message': 'No se pudo leer el archivo. Verifique formato Excel/CSV.', 'error': str(e)}), 400
        
        df.columns = [str(c).strip().lower().lstrip('\ufeff') for c in df.columns]
        alias = {
            'fecha_inicial': 'fecha_inicio',
            'observaciones': 'observacion'
        }
        df.rename(columns=alias, inplace=True)
        
        required_cols = ['tecnico', 'tipo_licencia', 'fecha_inicio', 'fecha_vencimiento']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            return jsonify({'success': False, 'message': f'Columnas faltantes: {", ".join(missing)}'}), 400
        
        def parse_date(val):
            try:
                if val is None:
                    return None
                # Manejo de valores 0 o equivalentes
                if isinstance(val, (int, float)):
                    if val == 0:
                        return None
                s = str(val).strip()
                if s == '' or s.upper() in ['NA', 'N/A', 'NULL', 'NONE']:
                    return None
                if s in ['0', '0000-00-00', '00/00/0000']:
                    return None
                if s.startswith('0/01/1900') or s.startswith('01/01/1900') or s.startswith('1900-01-01'):
                    return None
                dt = pd.to_datetime(s, dayfirst=True, errors='coerce')
                return dt.date() if not pd.isna(dt) else None
            except Exception:
                return None
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = conn.cursor(dictionary=True)
        
        inserted = 0
        updated = 0
        skipped = 0
        skipped_details = []
        ajustes_fecha_inicio = []
        
        # Procesar filas
        for idx, row in df.iterrows():
            row_num = int(idx) + 1
            tecnico_id = (str(row.get('tecnico')) if row.get('tecnico') is not None else '').strip()
            if not tecnico_id:
                skipped += 1
                skipped_details.append({'row': row_num, 'reason': 'tecnico vacío'})
                continue
            
            tipo_licencia = (str(row.get('tipo_licencia')) if row.get('tipo_licencia') is not None else '').strip()
            if not tipo_licencia:
                skipped += 1
                skipped_details.append({'row': row_num, 'tecnico': tecnico_id, 'reason': 'tipo_licencia vacío'})
                continue
            
            fecha_inicio = parse_date(row.get('fecha_inicio'))
            fecha_vencimiento = parse_date(row.get('fecha_vencimiento'))
            if fecha_vencimiento is None:
                skipped += 1
                skipped_details.append({'row': row_num, 'tecnico': tecnico_id, 'reason': 'fecha_vencimiento inválida o vacía'})
                continue
            
            estado = (str(row.get('estado')) if row.get('estado') is not None else 'Activo').strip()
            if estado.upper() == 'ACTIVO':
                estado = 'Activo'
            observacion = (str(row.get('observacion')) if row.get('observacion') is not None else '').strip() or None
            
            # Validar técnico activo
            cursor.execute("SELECT id_codigo_consumidor FROM recurso_operativo WHERE id_codigo_consumidor = %s AND estado = 'Activo'", (tecnico_id,))
            if not cursor.fetchone():
                skipped += 1
                skipped_details.append({'row': row_num, 'tecnico': tecnico_id, 'reason': 'técnico no encontrado o inactivo'})
                continue
            
            # Si fecha_inicio es inválida o vacía, permitir NULL y registrar ajuste
            if fecha_inicio is None:
                ajustes_fecha_inicio.append({'row': row_num, 'tecnico': tecnico_id, 'note': 'fecha_inicio vacía/0 -> NULL'})
            
            # Buscar licencia vigente existente para el técnico
            cursor.execute(
                """
                SELECT id_mpa_licencia_conducir FROM mpa_licencia_conducir
                WHERE tecnico = %s AND fecha_vencimiento > CURDATE()
                ORDER BY fecha_vencimiento DESC LIMIT 1
                """,
                (tecnico_id,)
            )
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute(
                    """
                    UPDATE mpa_licencia_conducir
                    SET tipo_licencia=%s, fecha_inicio=%s, fecha_vencimiento=%s,
                        observacion=%s, fecha_actualizacion=NOW()
                    WHERE id_mpa_licencia_conducir=%s
                    """,
                    (tipo_licencia, fecha_inicio, fecha_vencimiento, observacion, existing['id_mpa_licencia_conducir'])
                )
                updated += 1
            else:
                cursor.execute(
                    """
                    INSERT INTO mpa_licencia_conducir (
                        tecnico, tipo_licencia, fecha_inicio, fecha_vencimiento, observacion, fecha_creacion
                    ) VALUES (%s, %s, %s, %s, %s, NOW())
                    """,
                    (tecnico_id, tipo_licencia, fecha_inicio, fecha_vencimiento, observacion)
                )
                inserted += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({
            'success': True,
            'inserted': inserted,
            'updated': updated,
            'skipped': skipped,
            'skipped_details': skipped_details,
            'ajustes_fecha_inicio': ajustes_fecha_inicio
        })
    except Exception as e:
        if 'conn' in locals() and conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return jsonify({'success': False, 'message': 'Error procesando archivo', 'error': str(e)}), 500

# API para obtener lista de técnicos
@app.route('/api/mpa/tecnicos', methods=['GET'])
@login_required
def api_get_tecnicos():
    """API para obtener la lista de técnicos disponibles"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener técnicos activos
        query = """
        SELECT 
            id_codigo_consumidor,
            recurso_operativo_cedula as cedula,
            nombre,
            cargo
        FROM recurso_operativo 
        WHERE estado = 'Activo'
        ORDER BY nombre
        """
        
        cursor.execute(query)
        tecnicos = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'data': tecnicos
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/mpa/vencimientos')
@login_required
def mpa_vencimientos():
    """Módulo de gestión de vencimientos consolidados"""
    if not current_user.has_role('administrativo'):
        flash('No tienes permisos para acceder a este módulo.', 'error')
        return redirect(url_for('mpa_dashboard'))
    
    return render_template('modulos/mpa/vencimientos.html')

@app.route('/mpa/soat')
@login_required
def mpa_soat():
    """Módulo de gestión de SOAT"""
    if not current_user.has_role('administrativo'):
        flash('No tienes permisos para acceder a este módulo.', 'error')
        return redirect(url_for('mpa_dashboard'))
    
    return render_template('modulos/mpa/soat.html')

@app.route('/mpa/tecnico-mecanica')
@login_required
def mpa_tecnico_mecanica():
    """Módulo de gestión de revisión técnico mecánica"""
    if not current_user.has_role('administrativo'):
        flash('No tienes permisos para acceder a este módulo.', 'error')
        return redirect(url_for('mpa_dashboard'))
    
    return render_template('modulos/mpa/tecnico_mecanica.html')

@app.route('/mpa/licencias-conducir')
@login_required
def mpa_licencias_conducir():
    """Módulo de gestión de licencias de conducir"""
    if not current_user.has_role('administrativo'):
        flash('No tienes permisos para acceder a este módulo.', 'error')
        return redirect(url_for('mpa_dashboard'))
    
    return render_template('modulos/mpa/licencias_conducir.html')

@app.route('/mpa/licencias')
@login_required
def mpa_licencias():
    """Módulo de gestión de licencias de conducir (redirige a la nueva ruta)"""
    if not current_user.has_role('administrativo'):
        flash('No tienes permisos para acceder a este módulo.', 'error')
        return redirect(url_for('mpa_dashboard'))
    
    return redirect(url_for('mpa_licencias_conducir'))

@app.route('/mpa/simit')
@login_required
def mpa_simit():
    if not current_user.has_role('administrativo'):
        flash('No tienes permisos para acceder a este módulo.', 'error')
        return redirect(url_for('mpa_dashboard'))
    return render_template('modulos/mpa/simit.html')

@app.route('/mpa/inspecciones')
@login_required
def mpa_inspecciones():
    if not current_user.has_role('administrativo'):
        flash('No tienes permisos para acceder a este módulo.', 'error')
        return redirect(url_for('mpa_dashboard'))
    return render_template('modulos/mpa/inspecciones.html')

@app.route('/mpa/kit-carretera')
@login_required
def mpa_kit_carretera():
    if not current_user.has_role('administrativo'):
        flash('No tienes permisos para acceder a este módulo.', 'error')
        return redirect(url_for('mpa_dashboard'))
    return render_template('modulos/mpa/kit_carretera.html')

@app.route('/mpa/kitcarretera')
@login_required
def mpa_kitcarretera_alias():
    return mpa_kit_carretera()

@app.route('/mpa/kit-carretera/')
@login_required
def mpa_kit_carretera_slash():
    return mpa_kit_carretera()

@app.route('/mpa/siniestros')
@login_required
def mpa_siniestros():
    """Módulo de gestión de siniestros"""
    if not current_user.has_role('administrativo'):
        flash('No tienes permisos para acceder a este módulo.', 'error')
        return redirect(url_for('mpa_dashboard'))
    
    # TODO: Implementar página de siniestros
    flash('Módulo en desarrollo', 'info')
    return redirect(url_for('mpa_dashboard'))

# ==================== MANTENIMIENTOS APIs ====================

# API para obtener lista de mantenimientos
@app.route('/api/mpa/mantenimientos', methods=['GET'])
@login_required
def api_get_mantenimientos():
    """API para obtener la lista de mantenimientos"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        ensure_mantenimiento_general_column(connection)
        ensure_mantenimiento_subcats_column(connection)
        has_general = has_mantenimiento_general_column(connection)
        has_subcats = has_mantenimiento_subcats_column(connection)
        
        # Obtener mantenimientos con información del vehículo
        general_sel = "m.tipo_general_mantenimiento" if has_general else "NULL AS tipo_general_mantenimiento"
        subcats_sel = "m.tipo_general_subcategorias" if has_subcats else "NULL AS tipo_general_subcategorias"
        query = f"""
        SELECT 
            m.id_mpa_mantenimientos,
            m.placa,
            m.fecha_mantenimiento,
            m.kilometraje,
            m.observacion,
            m.soporte_foto_geo as foto_taller,
            m.soporte_foto_factura as foto_factura,
            m.tipo_vehiculo,
            COALESCE(ro_v.nombre, ro_m.nombre, m.tecnico) AS tecnico_nombre,
            m.tipo_mantenimiento,
            {general_sel},
            {subcats_sel},
            m.estado
        FROM mpa_mantenimientos m
        LEFT JOIN mpa_vehiculos v ON v.placa = m.placa
        LEFT JOIN recurso_operativo ro_v ON ro_v.id_codigo_consumidor = v.tecnico_asignado
        LEFT JOIN recurso_operativo ro_m ON ro_m.id_codigo_consumidor = CAST(m.tecnico AS UNSIGNED)
        ORDER BY m.fecha_mantenimiento DESC
        """
        
        cursor.execute(query)
        mantenimientos = cursor.fetchall()
        
        # Formatear fechas para el frontend
        for mantenimiento in mantenimientos:
            if mantenimiento['fecha_mantenimiento']:
                mantenimiento['fecha_mantenimiento'] = mantenimiento['fecha_mantenimiento'].strftime('%Y-%m-%d %H:%M:%S')
            try:
                val = mantenimiento.get('tipo_general_subcategorias')
                if isinstance(val, (bytes, bytearray)):
                    val = val.decode('utf-8', errors='ignore')
                if isinstance(val, str) and val:
                    import json as _json
                    mantenimiento['tipo_general_subcategorias'] = _json.loads(val)
            except Exception:
                pass
        
        return jsonify({
            'success': True,
            'data': mantenimientos
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para obtener un mantenimiento específico
@app.route('/api/mpa/mantenimientos/<int:mantenimiento_id>', methods=['GET'])
@login_required
def api_get_mantenimiento(mantenimiento_id):
    """API para obtener detalles de un mantenimiento específico"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        ensure_mantenimiento_general_column(connection)
        ensure_mantenimiento_subcats_column(connection)
        has_general = has_mantenimiento_general_column(connection)
        has_subcats = has_mantenimiento_subcats_column(connection)
        
        general_sel = "m.tipo_general_mantenimiento" if has_general else "NULL AS tipo_general_mantenimiento"
        subcats_sel = "m.tipo_general_subcategorias" if has_subcats else "NULL AS tipo_general_subcategorias"
        query = f"""
        SELECT 
            m.id_mpa_mantenimientos,
            m.placa,
            m.fecha_mantenimiento,
            m.kilometraje,
            m.observacion,
            m.soporte_foto_geo as foto_taller,
            m.soporte_foto_factura as foto_factura,
            m.tipo_vehiculo,
            COALESCE(ro_v.nombre, ro_m.nombre, m.tecnico) AS tecnico_nombre,
            m.tipo_mantenimiento,
            {general_sel},
            {subcats_sel},
            m.estado
        FROM mpa_mantenimientos m
        LEFT JOIN mpa_vehiculos v ON v.placa = m.placa
        LEFT JOIN recurso_operativo ro_v ON ro_v.id_codigo_consumidor = v.tecnico_asignado
        LEFT JOIN recurso_operativo ro_m ON ro_m.id_codigo_consumidor = CAST(m.tecnico AS UNSIGNED)
        WHERE m.id_mpa_mantenimientos = %s
        """
        
        cursor.execute(query, (mantenimiento_id,))
        mantenimiento = cursor.fetchone()
        
        if not mantenimiento:
            return jsonify({'success': False, 'error': 'Mantenimiento no encontrado'}), 404
        
        # Formatear fecha
        if mantenimiento['fecha_mantenimiento']:
            mantenimiento['fecha_mantenimiento'] = mantenimiento['fecha_mantenimiento'].strftime('%Y-%m-%d %H:%M:%S')
        try:
            val = mantenimiento.get('tipo_general_subcategorias')
            if isinstance(val, (bytes, bytearray)):
                val = val.decode('utf-8', errors='ignore')
            if isinstance(val, str) and val:
                import json as _json
                mantenimiento['tipo_general_subcategorias'] = _json.loads(val)
        except Exception:
            pass
        
        return jsonify({
            'success': True,
            'data': mantenimiento
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para crear un nuevo mantenimiento
@app.route('/api/mpa/mantenimientos', methods=['POST'])
@login_required
def api_create_mantenimiento():
    """API para crear un nuevo mantenimiento"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['placa', 'kilometraje', 'tipo_mantenimiento', 'observacion']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor()
        
        # Verificar que la placa existe y obtener tipo de vehículo
        cursor.execute("SELECT tipo_vehiculo FROM mpa_vehiculos WHERE placa = %s", (data['placa'],))
        vehiculo = cursor.fetchone()
        if not vehiculo:
            return jsonify({'success': False, 'message': 'Placa no encontrada'}), 404
        
        tipo_vehiculo = vehiculo[0]
        
        # Obtener fecha actual en zona horaria de Bogotá
        from datetime import datetime
        import pytz
        bogota_tz = pytz.timezone('America/Bogota')
        fecha_mantenimiento = datetime.now(bogota_tz).replace(tzinfo=None)
        
        # Normalizar el valor de técnico: si es UID numérico, mapear a nombre
        tecnico_input = (data.get('tecnico', '') or '').strip()
        tecnico_guardar = tecnico_input
        if tecnico_input.isdigit():
            try:
                cursor.execute(
                    "SELECT nombre FROM recurso_operativo WHERE CAST(TRIM(id_codigo_consumidor) AS UNSIGNED) = %s",
                    (int(tecnico_input),)
                )
                row = cursor.fetchone()
                if row:
                    tecnico_guardar = row[0]
            except Exception:
                pass

        ensure_mantenimiento_general_column(connection)
        ensure_mantenimiento_subcats_column(connection)
        has_general = has_mantenimiento_general_column(connection)
        has_subcats = has_mantenimiento_subcats_column(connection)

        # Insertar nuevo mantenimiento
        if has_general and has_subcats:
            insert_query = """
            INSERT INTO mpa_mantenimientos 
            (placa, fecha_mantenimiento, kilometraje, tipo_vehiculo, tipo_mantenimiento, tipo_general_mantenimiento, tipo_general_subcategorias, observacion, soporte_foto_geo, soporte_foto_factura, tecnico, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        elif has_general and not has_subcats:
            insert_query = """
            INSERT INTO mpa_mantenimientos 
            (placa, fecha_mantenimiento, kilometraje, tipo_vehiculo, tipo_mantenimiento, tipo_general_mantenimiento, observacion, soporte_foto_geo, soporte_foto_factura, tecnico, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        elif has_subcats and not has_general:
            insert_query = """
            INSERT INTO mpa_mantenimientos 
            (placa, fecha_mantenimiento, kilometraje, tipo_vehiculo, tipo_mantenimiento, tipo_general_subcategorias, observacion, soporte_foto_geo, soporte_foto_factura, tecnico, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        else:
            insert_query = """
            INSERT INTO mpa_mantenimientos 
            (placa, fecha_mantenimiento, kilometraje, tipo_vehiculo, tipo_mantenimiento, observacion, soporte_foto_geo, soporte_foto_factura, tecnico, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        
        if has_general and has_subcats:
            cursor.execute(insert_query, (
                data['placa'],
                fecha_mantenimiento,
                data['kilometraje'],
                tipo_vehiculo,
                data['tipo_mantenimiento'],
                (data.get('tipo_general') or None),
                json.dumps(data.get('tipo_general_subcategorias') or []),
                data['observacion'],
                data.get('foto_taller', ''),
                data.get('foto_factura', ''),
                tecnico_guardar,
                data.get('estado', 'Abierto')
            ))
        elif has_general and not has_subcats:
            cursor.execute(insert_query, (
                data['placa'],
                fecha_mantenimiento,
                data['kilometraje'],
                tipo_vehiculo,
                data['tipo_mantenimiento'],
                (data.get('tipo_general') or None),
                data['observacion'],
                data.get('foto_taller', ''),
                data.get('foto_factura', ''),
                tecnico_guardar,
                data.get('estado', 'Abierto')
            ))
        elif has_subcats and not has_general:
            cursor.execute(insert_query, (
                data['placa'],
                fecha_mantenimiento,
                data['kilometraje'],
                tipo_vehiculo,
                data['tipo_mantenimiento'],
                json.dumps(data.get('tipo_general_subcategorias') or []),
                data['observacion'],
                data.get('foto_taller', ''),
                data.get('foto_factura', ''),
                tecnico_guardar,
                data.get('estado', 'Abierto')
            ))
        else:
            cursor.execute(insert_query, (
                data['placa'],
                fecha_mantenimiento,
                data['kilometraje'],
                tipo_vehiculo,
                data['tipo_mantenimiento'],
                data['observacion'],
                data.get('foto_taller', ''),
                data.get('foto_factura', ''),
                tecnico_guardar,
                data.get('estado', 'Abierto')
            ))
        
        connection.commit()
        mantenimiento_id = cursor.lastrowid

        try:
            ensure_cronograma_table()
            cursor2 = connection.cursor(dictionary=True)
            cursor2.execute("SELECT kilometraje_frecuencia, kilometraje_promedio_diario FROM cronograma_mantenimientos WHERE placa = %s", (data['placa'],))
            row = cursor2.fetchone()
            km_freq = int((row or {}).get('kilometraje_frecuencia') or 2500)
            km_avg = int((row or {}).get('kilometraje_promedio_diario') or 80)
            from datetime import timedelta
            proximo_km = int(data['kilometraje']) + km_freq
            dias = max(0, int(km_freq / max(1, km_avg)))
            fecha_prox = fecha_mantenimiento + timedelta(days=dias)
            cursor2.execute("SELECT id_cronograma FROM cronograma_mantenimientos WHERE placa = %s", (data['placa'],))
            ex = cursor2.fetchone()
            if ex:
                cursor2.execute(
                    """
                    UPDATE cronograma_mantenimientos
                    SET fecha_mantenimiento = %s,
                        kilometraje_actual = %s,
                        fecha_proximo_mantenimiento = %s,
                        proximo_kilometraje = %s,
                        cumplido = 1,
                        cumplido_fecha = %s,
                        cumplido_mantenimiento_id = %s
                    WHERE placa = %s
                    """,
                    (fecha_mantenimiento, int(data['kilometraje']), fecha_prox, proximo_km, fecha_mantenimiento, mantenimiento_id, data['placa'])
                )
            else:
                cursor2.execute(
                    """
                    INSERT INTO cronograma_mantenimientos
                    (placa, fecha_mantenimiento, tipo_mantenimiento,
                     kilometraje_actual, kilometraje_frecuencia, kilometraje_promedio_diario,
                     estado, fecha_proximo_mantenimiento, proximo_kilometraje,
                     observaciones, cumplido, cumplido_fecha, cumplido_mantenimiento_id)
                    VALUES (%s, %s, %s, %s, %s, %s, 'Activo', %s, %s, %s, 1, %s, %s)
                    """,
                    (data['placa'], fecha_mantenimiento, data['tipo_mantenimiento'], int(data['kilometraje']), km_freq, km_avg, fecha_prox, proximo_km, data.get('observacion',''), fecha_mantenimiento, mantenimiento_id)
                )
            connection.commit()
            cursor2.close()
        except Exception:
            try:
                connection.rollback()
            except Exception:
                pass

        return jsonify({
            'success': True,
            'message': 'Mantenimiento creado exitosamente',
            'id': mantenimiento_id
        })
        
    except Exception as e:
        if 'connection' in locals() and connection:
            connection.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para actualizar un mantenimiento
@app.route('/api/mpa/mantenimientos/<int:mantenimiento_id>', methods=['PUT'])
@login_required
def api_update_mantenimiento(mantenimiento_id):
    """API para actualizar un mantenimiento"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        data = request.get_json()
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor()
        
        # Verificar que el mantenimiento existe
        cursor.execute("SELECT id_mpa_mantenimientos FROM mpa_mantenimientos WHERE id_mpa_mantenimientos = %s", (mantenimiento_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Mantenimiento no encontrado'}), 404
        
        # Construir query de actualización dinámicamente
        update_fields = []
        values = []
        
        if 'placa' in data:
            # Verificar que la placa existe
            cursor.execute("SELECT placa FROM mpa_vehiculos WHERE placa = %s", (data['placa'],))
            if not cursor.fetchone():
                return jsonify({'success': False, 'error': 'Placa no encontrada'}), 404
            update_fields.append("placa = %s")
            values.append(data['placa'])
        
        if 'kilometraje' in data:
            update_fields.append("kilometraje = %s")
            values.append(data['kilometraje'])
        
        if 'tipo_mantenimiento' in data:
            update_fields.append("tipo_mantenimiento = %s")
            values.append(data['tipo_mantenimiento'])
        if 'tipo_general' in data:
            ensure_mantenimiento_general_column(connection)
            if has_mantenimiento_general_column(connection):
                update_fields.append("tipo_general_mantenimiento = %s")
                values.append(data['tipo_general'])
        if 'tipo_general_subcategorias' in data:
            ensure_mantenimiento_subcats_column(connection)
            if has_mantenimiento_subcats_column(connection):
                update_fields.append("tipo_general_subcategorias = %s")
                values.append(json.dumps(data['tipo_general_subcategorias']))
        
        if 'tecnico' in data:
            tecnico_input = (data.get('tecnico', '') or '').strip()
            tecnico_guardar = tecnico_input
            if tecnico_input.isdigit():
                try:
                    cursor.execute(
                        "SELECT nombre FROM recurso_operativo WHERE CAST(TRIM(id_codigo_consumidor) AS UNSIGNED) = %s",
                        (int(tecnico_input),)
                    )
                    row = cursor.fetchone()
                    if row:
                        tecnico_guardar = row[0]
                except Exception:
                    pass
            update_fields.append("tecnico = %s")
            values.append(tecnico_guardar)
        
        if 'observacion' in data:
            update_fields.append("observacion = %s")
            values.append(data['observacion'])
        
        if 'foto_taller' in data:
            update_fields.append("soporte_foto_geo = %s")
            values.append(data['foto_taller'])
        
        if 'foto_factura' in data:
            update_fields.append("soporte_foto_factura = %s")
            values.append(data['foto_factura'])
        
        if 'estado' in data:
            update_fields.append("estado = %s")
            values.append(data['estado'])
        
        if not update_fields:
            return jsonify({'success': False, 'error': 'No hay campos para actualizar'}), 400
        
        values.append(mantenimiento_id)
        update_query = f"UPDATE mpa_mantenimientos SET {', '.join(update_fields)} WHERE id_mpa_mantenimientos = %s"
        
        cursor.execute(update_query, values)
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Mantenimiento actualizado exitosamente'
        })
        
    except Exception as e:
        if 'connection' in locals() and connection:
            connection.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para eliminar un mantenimiento
@app.route('/api/mpa/mantenimientos/<int:mantenimiento_id>', methods=['DELETE'])
@login_required
def api_delete_mantenimiento(mantenimiento_id):
    """API para eliminar un mantenimiento"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor()
        
        # Verificar si el mantenimiento existe
        cursor.execute("SELECT id_mpa_mantenimientos FROM mpa_mantenimientos WHERE id_mpa_mantenimientos = %s", (mantenimiento_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Mantenimiento no encontrado'}), 404
        
        # Eliminar mantenimiento
        cursor.execute("DELETE FROM mpa_mantenimientos WHERE id_mpa_mantenimientos = %s", (mantenimiento_id,))
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Mantenimiento eliminado exitosamente'
        })
        
    except Exception as e:
        if 'connection' in locals() and connection:
            connection.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para obtener placas de vehículos
@app.route('/api/mpa/vehiculos/placas', methods=['GET'])
@login_required
def api_get_placas():
    """API para obtener lista de placas de vehículos"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT 
            v.placa,
            v.tipo_vehiculo,
            v.tecnico_asignado,
            COALESCE(ro.nombre, CAST(v.tecnico_asignado AS CHAR)) as tecnico_nombre
        FROM mpa_vehiculos v
        LEFT JOIN recurso_operativo ro 
            ON CAST(TRIM(ro.id_codigo_consumidor) AS UNSIGNED) = CAST(v.tecnico_asignado AS UNSIGNED)
        WHERE v.estado = 'Activo'
        ORDER BY v.placa
        """
        
        cursor.execute(query)
        placas = cursor.fetchall()

        # Resolver el último km de preoperacional por placa, detectando columna
        try:
            km_col = None
            cursor2 = connection.cursor(dictionary=True)
            try:
                cursor2.execute("SHOW COLUMNS FROM preoperacional LIKE 'kilometraje'")
                if cursor2.fetchone():
                    km_col = 'kilometraje'
                else:
                    cursor2.execute("SHOW COLUMNS FROM preoperacional LIKE 'kilometraje_actual'")
                    if cursor2.fetchone():
                        km_col = 'kilometraje_actual'
            except Exception:
                km_col = None
            km_map = {}
            if km_col:
                cursor2.execute(
                    f"""
                    SELECT p.placa_vehiculo, p.{km_col} AS km
                    FROM preoperacional p
                    INNER JOIN (
                        SELECT placa_vehiculo, MAX(fecha) AS last_fecha
                        FROM preoperacional
                        GROUP BY placa_vehiculo
                    ) t ON t.placa_vehiculo = p.placa_vehiculo AND t.last_fecha = p.fecha
                    """
                )
                for row in cursor2.fetchall():
                    km_map[row['placa_vehiculo']] = row['km']
            cursor2.close()
            for v in placas:
                v['ultimo_km_preoperacional'] = km_map.get(v['placa'])
        except Exception:
            try:
                cursor2.close()
            except Exception:
                pass

        return jsonify({
            'success': True,
            'data': placas
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para obtener categorías de mantenimiento por tipo de vehículo
@app.route('/api/mpa/categorias-mantenimiento/<tipo_vehiculo>', methods=['GET'])
@login_required
def api_get_categorias_mantenimiento(tipo_vehiculo):
    """API para obtener categorías de mantenimiento por tipo de vehículo"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT 
            id_mpa_categoria_mantenimiento,
            categoria,
            tipo_mantenimiento,
            tipo_vehiculo
        FROM mpa_categoria_mantenimiento
        WHERE tipo_vehiculo = %s
        ORDER BY categoria, tipo_mantenimiento
        """
        
        cursor.execute(query, (tipo_vehiculo,))
        categorias = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'data': categorias
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/mpa/inspecciones', methods=['GET'])
@login_required
def api_list_inspecciones():
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SHOW TABLES LIKE 'mpa_inspeccion_vehiculo'")
            if not cursor.fetchone():
                return jsonify({'success': True, 'data': []})
        except Exception:
            return jsonify({'success': True, 'data': []})
        placa = (request.args.get('placa') or '').strip().upper()
        tecnico_id = (request.args.get('tecnico_id') or '').strip()
        mes_raw = (request.args.get('mes') or '').strip()
        desde_raw = (request.args.get('desde') or '').strip()
        hasta_raw = (request.args.get('hasta') or '').strip()
        if mes_raw and len(mes_raw) >= 7 and mes_raw[4] == '-':
            try:
                from datetime import datetime as _dt
                y = int(mes_raw[:4])
                m = int(mes_raw[5:7])
                fm = _dt(y, m, 1)
                nm = _dt(y + (1 if m == 12 else 0), 1 if m == 12 else m + 1, 1)
                desde_raw = fm.strftime('%Y-%m-%d %H:%M:%S')
                hasta_raw = nm.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass
        desde_raw = (request.args.get('desde') or '').strip()
        hasta_raw = (request.args.get('hasta') or '').strip()

        cursor.execute("DESCRIBE mpa_inspeccion_vehiculo")
        cols_info = cursor.fetchall() or []
        col_names = set()
        for ci in cols_info:
            try:
                col_names.add(ci.get('Field') or ci.get('field') or ci[0])
            except Exception:
                pass

        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        ro_exists = cursor.fetchone() is not None

        col_placa = 'placa' if 'placa' in col_names else None
        posibles_tecnico_fk = ['id_codigo_consumidor','tecnico_id','tecnico','id_tecnico']
        col_tecnico_fk = next((c for c in posibles_tecnico_fk if c in col_names), None)
        col_nombre = 'nombre' if 'nombre' in col_names else None
        col_fecha = 'fecha_inspeccion' if 'fecha_inspeccion' in col_names else None

        where = []
        params = []
        if col_placa and placa:
            where.append(f"UPPER(TRIM(i.{col_placa})) = %s")
            params.append(placa)
        if col_tecnico_fk and tecnico_id:
            where.append(f"i.{col_tecnico_fk} = %s")
            params.append(tecnico_id)
        if col_fecha and desde_raw:
            where.append("i.fecha_inspeccion >= %s")
            params.append(desde_raw)
        if col_fecha and hasta_raw:
            where.append("i.fecha_inspeccion < %s")
            params.append(hasta_raw)

        if ro_exists and col_tecnico_fk:
            tecnico_select = f"COALESCE(ro.nombre, CAST(i.{col_tecnico_fk} AS CHAR)) AS tecnico_nombre"
            joins = f"LEFT JOIN recurso_operativo ro ON ro.id_codigo_consumidor = i.{col_tecnico_fk}"
        elif col_nombre:
            tecnico_select = "i.nombre AS tecnico_nombre"
            joins = ""
        elif col_tecnico_fk:
            tecnico_select = f"CAST(i.{col_tecnico_fk} AS CHAR) AS tecnico_nombre"
            joins = ""
        else:
            tecnico_select = "NULL AS tecnico_nombre"
            joins = ""

        lim_raw = request.args.get('limit')
        lim = None
        try:
            if lim_raw is not None:
                lim = max(1, min(int(lim_raw), 1000))
        except Exception:
            lim = None
        query = """
        SELECT i.*, {tecnico_select}
        FROM mpa_inspeccion_vehiculo i
        {joins}
        {where_clause}
        ORDER BY i.fecha_inspeccion DESC {limit_clause}
        """
        where_clause = ("WHERE " + " AND ".join(where)) if where else ""
        limit_clause = ("LIMIT " + str(lim)) if lim else ""
        query = query.format(tecnico_select=tecnico_select, joins=joins, where_clause=where_clause, limit_clause=limit_clause)
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        for r in rows:
            fi = r.get('fecha_inspeccion')
            if fi:
                try:
                    r['fecha_inspeccion'] = fi.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    pass
            vl = r.get('vencimiento_licencia')
            vs = r.get('vencimiento_soat')
            vt = r.get('vencimiento_tecnicomecanica')
            for k in ('vencimiento_licencia','vencimiento_soat','vencimiento_tecnicomecanica'):
                v = r.get(k)
                if v:
                    try:
                        r[k] = v.strftime('%Y-%m-%d')
                    except Exception:
                        pass
        return jsonify({'success': True, 'data': rows})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

MPA_INSP_IDX_DONE = False

def ensure_mpa_indexes():
    global MPA_INSP_IDX_DONE
    if MPA_INSP_IDX_DONE:
        return
    conn = get_db_connection()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM information_schema.statistics WHERE table_schema = DATABASE() AND table_name='mpa_inspeccion_vehiculo' AND index_name='idx_mpa_insp_fecha'")
        if not cur.fetchone():
            try:
                cur.execute("CREATE INDEX idx_mpa_insp_fecha ON mpa_inspeccion_vehiculo (fecha_inspeccion)")
            except Exception:
                pass
        cur.execute("SELECT 1 FROM information_schema.statistics WHERE table_schema = DATABASE() AND table_name='mpa_inspeccion_vehiculo' AND index_name='idx_mpa_insp_placa'")
        if not cur.fetchone():
            try:
                cur.execute("CREATE INDEX idx_mpa_insp_placa ON mpa_inspeccion_vehiculo (placa)")
            except Exception:
                pass
        cur.execute("SELECT 1 FROM information_schema.statistics WHERE table_schema = DATABASE() AND table_name='mpa_vehiculos' AND index_name='idx_mpa_veh_placa'")
        if not cur.fetchone():
            try:
                cur.execute("CREATE INDEX idx_mpa_veh_placa ON mpa_vehiculos (placa)")
            except Exception:
                pass
        cur.execute("DESCRIBE mpa_vehiculos")
        cols_v = {r[0] if not isinstance(r, dict) else (r.get('Field') or r.get('field')) for r in (cur.fetchall() or [])}
        if 'tecnico_asignado' in cols_v:
            cur.execute("SELECT 1 FROM information_schema.statistics WHERE table_schema = DATABASE() AND table_name='mpa_vehiculos' AND index_name='idx_mpa_veh_tecnico'")
            if not cur.fetchone():
                try:
                    cur.execute("CREATE INDEX idx_mpa_veh_tecnico ON mpa_vehiculos (tecnico_asignado)")
                except Exception:
                    pass
        conn.commit()
        try:
            cur.close()
        except Exception:
            pass
        MPA_INSP_IDX_DONE = True
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
    try:
        conn.close()
    except Exception:
        pass

@app.route('/api/mpa/inspecciones/pendientes-mes', methods=['GET'])
@login_required
def api_inspecciones_pendientes_mes():
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        ensure_mpa_indexes()
        limit_raw = request.args.get('limit')
        limit = 5
        try:
            if limit_raw is not None:
                limit = max(1, min(int(limit_raw), 100))
        except Exception:
            limit = 5
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        cursor.execute("DESCRIBE mpa_vehiculos")
        v_cols = set()
        for ci in cursor.fetchall() or []:
            try:
                v_cols.add(ci.get('Field') or ci.get('field') or ci[0])
            except Exception:
                pass
        if 'placa' not in v_cols:
            return jsonify({'success': True, 'data': []})
        tcol = None
        for c in ('tecnico_asignado','id_codigo_consumidor','tecnico','id_tecnico'):
            if c in v_cols:
                tcol = c; break
        if not tcol:
            return jsonify({'success': True, 'data': []})
        cursor.execute("DESCRIBE mpa_inspeccion_vehiculo")
        i_cols = set()
        for ci in cursor.fetchall() or []:
            try:
                i_cols.add(ci.get('Field') or ci.get('field') or ci[0])
            except Exception:
                pass
        if 'placa' not in i_cols or 'fecha_inspeccion' not in i_cols:
            return jsonify({'success': True, 'data': []})
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        ro_exists = cursor.fetchone() is not None
        from datetime import date, datetime as _dt
        now = get_bogota_datetime()
        fm = _dt(now.year, now.month, 1)
        nm = _dt(now.year + (1 if now.month == 12 else 0), 1 if now.month == 12 else now.month + 1, 1)
        joins = ""
        if ro_exists:
            joins = f"LEFT JOIN recurso_operativo ro ON ro.id_codigo_consumidor = v.{tcol}"
        extra_where = " AND ro.estado = 'Activo'" if ro_exists else ""
        query = f"""
        SELECT v.placa, v.{tcol} AS tecnico_id, {('COALESCE(ro.nombre, CAST(v.' + tcol + ' AS CHAR))' if ro_exists else 'CAST(v.' + tcol + ' AS CHAR)')} AS tecnico_nombre
        FROM mpa_vehiculos v
        LEFT JOIN mpa_inspeccion_vehiculo i ON UPPER(TRIM(i.placa)) = UPPER(TRIM(v.placa)) AND i.fecha_inspeccion >= %s AND i.fecha_inspeccion < %s
        {joins}
        WHERE v.{tcol} IS NOT NULL AND i.placa IS NULL{extra_where}
        ORDER BY RAND()
        LIMIT {limit}
        """
        cursor.execute(query, (fm, nm))
        rows = cursor.fetchall() or []
        return jsonify({'success': True, 'data': rows})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/mpa/inspecciones/resumen-mes', methods=['GET'])
@login_required
def api_inspecciones_resumen_mes():
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        ensure_mpa_indexes()
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        # Validar estructuras
        cursor.execute("DESCRIBE mpa_vehiculos")
        v_cols = set()
        for ci in cursor.fetchall() or []:
            try:
                v_cols.add(ci.get('Field') or ci.get('field') or ci[0])
            except Exception:
                pass
        if 'placa' not in v_cols:
            return jsonify({'success': True, 'data': {'inspecciones': 0, 'faltantes': 0, 'total': 0, 'cumplimiento': 0.0}})
        tcol = None
        for c in ('tecnico_asignado','id_codigo_consumidor','tecnico','id_tecnico'):
            if c in v_cols:
                tcol = c; break
        if not tcol:
            return jsonify({'success': True, 'data': {'inspecciones': 0, 'faltantes': 0, 'total': 0, 'cumplimiento': 0.0}})
        cursor.execute("DESCRIBE mpa_inspeccion_vehiculo")
        i_cols = set()
        for ci in cursor.fetchall() or []:
            try:
                i_cols.add(ci.get('Field') or ci.get('field') or ci[0])
            except Exception:
                pass
        if 'placa' not in i_cols or 'fecha_inspeccion' not in i_cols:
            return jsonify({'success': True, 'data': {'inspecciones': 0, 'faltantes': 0, 'total': 0, 'cumplimiento': 0.0}})
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        ro_exists = cursor.fetchone() is not None
        # Rango de fechas
        mes_raw = (request.args.get('mes') or '').strip()
        desde_raw = (request.args.get('desde') or '').strip()
        hasta_raw = (request.args.get('hasta') or '').strip()
        if mes_raw and len(mes_raw) >= 7 and mes_raw[4] == '-':
            try:
                from datetime import datetime as _dt
                y = int(mes_raw[:4]); m = int(mes_raw[5:7])
                fm = _dt(y, m, 1)
                nm = _dt(y + (1 if m == 12 else 0), 1 if m == 12 else m + 1, 1)
                desde_raw = fm.strftime('%Y-%m-%d %H:%M:%S')
                hasta_raw = nm.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass
        if not (desde_raw and hasta_raw):
            now = get_bogota_datetime()
            from datetime import datetime as _dt
            fm = _dt(now.year, now.month, 1)
            nm = _dt(now.year + (1 if now.month == 12 else 0), 1 if now.month == 12 else now.month + 1, 1)
            desde_raw = fm.strftime('%Y-%m-%d %H:%M:%S')
            hasta_raw = nm.strftime('%Y-%m-%d %H:%M:%S')
        # Filtros opcionales
        tecnico_id = (request.args.get('tecnico_id') or '').strip()
        # Total vehículos asignados
        if tecnico_id:
            if ro_exists:
                cursor.execute(
                    f"SELECT COUNT(DISTINCT v.placa) AS c FROM mpa_vehiculos v LEFT JOIN recurso_operativo ro ON ro.id_codigo_consumidor = v.{tcol} WHERE v.{tcol} = %s AND ro.estado = 'Activo'",
                    (tecnico_id,)
                )
            else:
                cursor.execute(f"SELECT COUNT(DISTINCT v.placa) AS c FROM mpa_vehiculos v WHERE v.{tcol} = %s", (tecnico_id,))
        else:
            if ro_exists:
                cursor.execute(
                    f"SELECT COUNT(DISTINCT v.placa) AS c FROM mpa_vehiculos v LEFT JOIN recurso_operativo ro ON ro.id_codigo_consumidor = v.{tcol} WHERE v.{tcol} IS NOT NULL AND ro.estado = 'Activo'"
                )
            else:
                cursor.execute(f"SELECT COUNT(DISTINCT v.placa) AS c FROM mpa_vehiculos v WHERE v.{tcol} IS NOT NULL")
        total = (cursor.fetchone() or {}).get('c') or 0
        if tecnico_id:
            if ro_exists:
                cursor.execute(
                    f"""
                    SELECT COUNT(DISTINCT v.placa) AS c
                    FROM mpa_vehiculos v
                    INNER JOIN recurso_operativo ro ON ro.id_codigo_consumidor = v.{tcol}
                    INNER JOIN mpa_inspeccion_vehiculo i
                      ON UPPER(TRIM(i.placa)) = UPPER(TRIM(v.placa)) AND i.fecha_inspeccion >= %s AND i.fecha_inspeccion < %s
                    WHERE v.{tcol} = %s AND ro.estado = 'Activo'
                    """,
                    (desde_raw, hasta_raw, tecnico_id)
                )
            else:
                cursor.execute(
                    f"""
                    SELECT COUNT(DISTINCT v.placa) AS c
                    FROM mpa_vehiculos v
                    INNER JOIN mpa_inspeccion_vehiculo i
                      ON UPPER(TRIM(i.placa)) = UPPER(TRIM(v.placa)) AND i.fecha_inspeccion >= %s AND i.fecha_inspeccion < %s
                    WHERE v.{tcol} = %s
                    """,
                    (desde_raw, hasta_raw, tecnico_id)
                )
        else:
            if ro_exists:
                cursor.execute(
                    f"""
                    SELECT COUNT(DISTINCT v.placa) AS c
                    FROM mpa_vehiculos v
                    INNER JOIN recurso_operativo ro ON ro.id_codigo_consumidor = v.{tcol}
                    INNER JOIN mpa_inspeccion_vehiculo i
                      ON UPPER(TRIM(i.placa)) = UPPER(TRIM(v.placa)) AND i.fecha_inspeccion >= %s AND i.fecha_inspeccion < %s
                    WHERE v.{tcol} IS NOT NULL AND ro.estado = 'Activo'
                    """,
                    (desde_raw, hasta_raw)
                )
            else:
                cursor.execute(
                    f"""
                    SELECT COUNT(DISTINCT v.placa) AS c
                    FROM mpa_vehiculos v
                    INNER JOIN mpa_inspeccion_vehiculo i
                      ON UPPER(TRIM(i.placa)) = UPPER(TRIM(v.placa)) AND i.fecha_inspeccion >= %s AND i.fecha_inspeccion < %s
                    WHERE v.{tcol} IS NOT NULL
                    """,
                    (desde_raw, hasta_raw)
                )
        realizadas = (cursor.fetchone() or {}).get('c') or 0
        if tecnico_id:
            if ro_exists:
                cursor.execute(
                    f"""
                    SELECT COUNT(DISTINCT v.placa) AS c
                    FROM mpa_vehiculos v
                    LEFT JOIN recurso_operativo ro ON ro.id_codigo_consumidor = v.{tcol}
                    LEFT JOIN mpa_inspeccion_vehiculo i
                      ON UPPER(TRIM(i.placa)) = UPPER(TRIM(v.placa)) AND i.fecha_inspeccion >= %s AND i.fecha_inspeccion < %s
                    WHERE v.{tcol} = %s AND ro.estado = 'Activo' AND i.placa IS NULL
                    """,
                    (desde_raw, hasta_raw, tecnico_id)
                )
            else:
                cursor.execute(
                    f"""
                    SELECT COUNT(DISTINCT v.placa) AS c
                    FROM mpa_vehiculos v
                    LEFT JOIN mpa_inspeccion_vehiculo i
                      ON UPPER(TRIM(i.placa)) = UPPER(TRIM(v.placa)) AND i.fecha_inspeccion >= %s AND i.fecha_inspeccion < %s
                    WHERE v.{tcol} = %s AND i.placa IS NULL
                    """,
                    (desde_raw, hasta_raw, tecnico_id)
                )
        else:
            if ro_exists:
                cursor.execute(
                    f"""
                    SELECT COUNT(DISTINCT v.placa) AS c
                    FROM mpa_vehiculos v
                    LEFT JOIN recurso_operativo ro ON ro.id_codigo_consumidor = v.{tcol}
                    LEFT JOIN mpa_inspeccion_vehiculo i
                      ON UPPER(TRIM(i.placa)) = UPPER(TRIM(v.placa)) AND i.fecha_inspeccion >= %s AND i.fecha_inspeccion < %s
                    WHERE v.{tcol} IS NOT NULL AND ro.estado = 'Activo' AND i.placa IS NULL
                    """,
                    (desde_raw, hasta_raw)
                )
            else:
                cursor.execute(
                    f"""
                    SELECT COUNT(DISTINCT v.placa) AS c
                    FROM mpa_vehiculos v
                    LEFT JOIN mpa_inspeccion_vehiculo i
                      ON UPPER(TRIM(i.placa)) = UPPER(TRIM(v.placa)) AND i.fecha_inspeccion >= %s AND i.fecha_inspeccion < %s
                    WHERE v.{tcol} IS NOT NULL AND i.placa IS NULL
                    """,
                    (desde_raw, hasta_raw)
                )
        faltantes = (cursor.fetchone() or {}).get('c') or 0
        cumplimiento = float(0.0 if int(total) == 0 else round(100.0 * float(realizadas) / float(total), 1))
        return jsonify({'success': True, 'data': {
            'inspecciones': int(realizadas),
            'faltantes': int(faltantes),
            'total': int(total),
            'cumplimiento': cumplimiento
        }})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

def _kit_table_name(cursor):
    try:
        cursor.execute("SHOW TABLES LIKE 'mpa_inspeccion_kitcarretera'")
        if cursor.fetchone():
            return 'mpa_inspeccion_kitcarretera'
        cursor.execute("SHOW TABLES LIKE 'mpa_inspecion_kitcarretera'")
        if cursor.fetchone():
            return 'mpa_inspecion_kitcarretera'
        return 'mpa_inspeccion_kitcarretera'
    except Exception:
        return 'mpa_inspeccion_kitcarretera'

@app.route('/api/mpa/kitcarretera', methods=['GET'])
@login_required
def api_list_kitcarretera():
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        tname = _kit_table_name(cursor)
        try:
            cursor.execute(f"DESCRIBE {tname}")
        except Exception:
            return jsonify({'success': True, 'data': []})
        cols_info = cursor.fetchall() or []
        col_names = set()
        for ci in cols_info:
            try:
                col_names.add(ci.get('Field') or ci.get('field') or ci[0])
            except Exception:
                pass
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        ro_exists = cursor.fetchone() is not None
        placa = (request.args.get('placa') or '').strip().upper()
        tecnico_id = (request.args.get('tecnico_id') or '').strip()
        where = []
        params = []
        if 'placa' in col_names and placa:
            where.append("UPPER(TRIM(i.placa)) = %s")
            params.append(placa)
        posibles_tecnico_fk = ['id_codigo_consumidor','tecnico_id','tecnico','id_tecnico']
        col_tecnico_fk = next((c for c in posibles_tecnico_fk if c in col_names), None)
        col_nombre = 'nombre' if 'nombre' in col_names else None
        if col_tecnico_fk and tecnico_id:
            where.append(f"i.{col_tecnico_fk} = %s")
            params.append(tecnico_id)
        if ro_exists and col_tecnico_fk:
            tecnico_select = f"COALESCE(ro.nombre, CAST(i.{col_tecnico_fk} AS CHAR)) AS tecnico_nombre"
            joins = f"LEFT JOIN recurso_operativo ro ON ro.id_codigo_consumidor = i.{col_tecnico_fk}"
        elif col_nombre:
            tecnico_select = "i.nombre AS tecnico_nombre"
            joins = ""
        else:
            tecnico_select = "NULL AS tecnico_nombre"
            joins = ""
        query = f"""
        SELECT i.*, {tecnico_select}
        FROM {tname} i
        {joins}
        {('WHERE ' + ' AND '.join(where)) if where else ''}
        ORDER BY i.fecha_inspeccion DESC
        """
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall() or []
        for r in rows:
            fi = r.get('fecha_inspeccion')
            if fi:
                try:
                    r['fecha_inspeccion'] = fi.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    pass
            ev = r.get('extintor_vencimiento')
            if ev:
                try:
                    r['extintor_vencimiento'] = ev.strftime('%Y-%m-%d')
                except Exception:
                    pass
            ftf = r.get('firma_trabajador_fecha')
            if ftf:
                try:
                    r['firma_trabajador_fecha'] = ftf.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    pass
            fif = r.get('firma_inspector_fecha')
            if fif:
                try:
                    r['firma_inspector_fecha'] = fif.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    pass
        return jsonify({'success': True, 'data': rows})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/mpa/kitcarretera/<int:item_id>', methods=['GET'])
@login_required
def api_get_kitcarretera(item_id):
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        tname = _kit_table_name(cursor)
        cursor.execute(f"DESCRIBE {tname}")
        cols_info = cursor.fetchall() or []
        col_names = set()
        for ci in cols_info:
            try:
                col_names.add(ci.get('Field') or ci.get('field') or ci[0])
            except Exception:
                pass
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        ro_exists = cursor.fetchone() is not None
        posibles_tecnico_fk = ['id_codigo_consumidor','tecnico_id','tecnico','id_tecnico']
        col_tecnico_fk = next((c for c in posibles_tecnico_fk if c in col_names), None)
        col_nombre = 'nombre' if 'nombre' in col_names else None
        if ro_exists and col_tecnico_fk:
            tecnico_select = f"COALESCE(ro.nombre, CAST(i.{col_tecnico_fk} AS CHAR)) AS tecnico_nombre"
            joins = f"LEFT JOIN recurso_operativo ro ON ro.id_codigo_consumidor = i.{col_tecnico_fk}"
        elif col_nombre:
            tecnico_select = "i.nombre AS tecnico_nombre"
            joins = ""
        else:
            tecnico_select = "NULL AS tecnico_nombre"
            joins = ""
        query = f"""
            SELECT i.*, {tecnico_select}
            FROM {tname} i
            {joins}
            WHERE i.id = %s
        """
        cursor.execute(query, (item_id,))
        r = cursor.fetchone()
        if not r:
            return jsonify({'success': False, 'error': 'No encontrado'}), 404
        for k in ('fecha_inspeccion','extintor_vencimiento','firma_trabajador_fecha','firma_inspector_fecha'):
            v = r.get(k)
            if v:
                try:
                    r[k] = v.strftime('%Y-%m-%d %H:%M:%S') if k.endswith('_fecha') or k=='fecha_inspeccion' else v.strftime('%Y-%m-%d')
                except Exception:
                    pass
        return jsonify({'success': True, 'data': r})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/mpa/kitcarretera', methods=['POST'])
@login_required
def api_create_kitcarretera():
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        data = request.get_json(silent=True) or {}
        tecnico_id = data.get('tecnico_id')
        placa = (data.get('placa') or '').strip().upper()
        observaciones = data.get('observaciones') or ''
        foto_kit = data.get('foto_kit')
        ext_v = data.get('extintor_vencimiento')
        nombre = (data.get('nombre') or '').strip()
        recurso_operativo_cedula = (data.get('recurso_operativo_cedula') or data.get('cedula') or '').strip()
        fecha_inspeccion_raw = data.get('fecha_inspeccion')
        fecha_inspeccion = get_bogota_datetime().replace(tzinfo=None)
        if fecha_inspeccion_raw:
            try:
                from datetime import datetime as _dt
                s = str(fecha_inspeccion_raw).replace('T', ' ')
                fecha_inspeccion = _dt.strptime(s[:19], '%Y-%m-%d %H:%M:%S')
            except Exception:
                pass
        missing = []
        invalid = []
        if not tecnico_id:
            missing.append('tecnico_id')
        if not nombre:
            missing.append('nombre')
        if not recurso_operativo_cedula:
            missing.append('recurso_operativo_cedula')
        if not fecha_inspeccion_raw:
            missing.append('fecha_inspeccion')
        if not placa:
            missing.append('placa')
        if not ext_v:
            missing.append('extintor_vencimiento')
        if not observaciones:
            missing.append('observaciones')
        req_elems = ['gato','cruceta','senales','botiquin','extintor_vigente','tacos','caja_herramienta_basica','llanta_repuesto']
        for k in req_elems:
            v = (data.get(k) or '').strip().upper()
            if not v:
                missing.append(k)
            elif v not in ('SI','NO'):
                invalid.append(k)
        if not (isinstance(foto_kit, str) and foto_kit.strip()):
            missing.append('foto_kit')
        ft = data.get('firma_trabajador')
        fi = data.get('firma_inspector')
        ftf_raw = data.get('firma_trabajador_fecha')
        fif_raw = data.get('firma_inspector_fecha')
        if not (isinstance(ft, str) and ft.strip()):
            missing.append('firma_trabajador')
        if not (isinstance(fi, str) and fi.strip()):
            missing.append('firma_inspector')
        if not ftf_raw:
            missing.append('firma_trabajador_fecha')
        if not fif_raw:
            missing.append('firma_inspector_fecha')
        if missing or invalid:
            msg = ''
            if missing:
                msg += 'Faltan: ' + ', '.join(missing)
            if invalid:
                msg += ('; ' if msg else '') + 'Valores inválidos en: ' + ', '.join(invalid)
            return jsonify({'success': False, 'error': msg}), 400
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor()
        tname = _kit_table_name(cursor)
        try:
            cursor.execute(f"DESCRIBE {tname}")
        except Exception:
            ensure_mpa_inspeccion_kitcarretera_table()
            cursor.execute(f"DESCRIBE {tname}")
        cols = ['id_codigo_consumidor','nombre','recurso_operativo_cedula','placa','observaciones','foto_kit','fecha_inspeccion','extintor_vencimiento','gato','cruceta','senales','botiquin','extintor_vigente','tacos','caja_herramienta_basica','llanta_repuesto','firma_trabajador','firma_trabajador_fecha','firma_inspector','firma_inspector_fecha']
        payload = {
            'id_codigo_consumidor': tecnico_id,
            'nombre': nombre or None,
            'recurso_operativo_cedula': recurso_operativo_cedula or None,
            'placa': placa,
            'observaciones': observaciones,
            'foto_kit': foto_kit,
            'fecha_inspeccion': fecha_inspeccion,
            'extintor_vencimiento': None
        }
        if ext_v:
            try:
                from datetime import datetime as _dt
                payload['extintor_vencimiento'] = _dt.strptime(str(ext_v)[:10], '%Y-%m-%d').date()
            except Exception:
                payload['extintor_vencimiento'] = None
        for k in ['gato','cruceta','senales','botiquin','extintor_vigente','tacos','caja_herramienta_basica','llanta_repuesto']:
            v = data.get(k)
            payload[k] = v if v in ('SI','NO') else ''
        ft = data.get('firma_trabajador')
        fi = data.get('firma_inspector')
        payload['firma_trabajador'] = ft if isinstance(ft, str) and ft.strip() else None
        payload['firma_inspector'] = fi if isinstance(fi, str) and fi.strip() else None
        # Parseo de fechas de firma cuando se suministran desde el frontend
        from datetime import datetime as _dt
        if ftf_raw and 'firma_trabajador_fecha' in cols:
            try:
                s = str(ftf_raw).replace('T', ' ')
                payload['firma_trabajador_fecha'] = _dt.strptime(s[:19], '%Y-%m-%d %H:%M:%S')
            except Exception:
                payload['firma_trabajador_fecha'] = get_bogota_datetime().replace(tzinfo=None)
        elif payload['firma_trabajador'] and 'firma_trabajador_fecha' in cols:
            payload['firma_trabajador_fecha'] = get_bogota_datetime().replace(tzinfo=None)
        if fif_raw and 'firma_inspector_fecha' in cols:
            try:
                s2 = str(fif_raw).replace('T', ' ')
                payload['firma_inspector_fecha'] = _dt.strptime(s2[:19], '%Y-%m-%d %H:%M:%S')
            except Exception:
                payload['firma_inspector_fecha'] = get_bogota_datetime().replace(tzinfo=None)
        elif payload['firma_inspector'] and 'firma_inspector_fecha' in cols:
            payload['firma_inspector_fecha'] = get_bogota_datetime().replace(tzinfo=None)
        filtered = {k: payload[k] for k in cols if k in payload}
        insert_cols = ','.join(filtered.keys())
        insert_vals = ','.join(['%s']*len(filtered))
        cursor.execute(f"INSERT INTO {tname} ({insert_cols}) VALUES ({insert_vals})", tuple(filtered.values()))
        connection.commit()
        nid = cursor.lastrowid
        cursor.close(); connection.close()
        return jsonify({'success': True, 'id': nid})
    except Exception as e:
        try:
            connection.rollback()
        except Exception:
            pass
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mpa/kitcarretera/<int:item_id>/firma-trabajador', methods=['PUT'])
@login_required
def api_kitcarretera_firma_trabajador(item_id):
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        data = request.get_json(silent=True) or {}
        firma = data.get('firma')
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor()
        tname = _kit_table_name(cursor)
        cursor.execute(f"UPDATE {tname} SET firma_trabajador=%s, firma_trabajador_fecha=NOW() WHERE id=%s", (firma, item_id))
        connection.commit()
        cursor.close(); connection.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mpa/kitcarretera/<int:item_id>/firma-inspector', methods=['PUT'])
@login_required
def api_kitcarretera_firma_inspector(item_id):
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        data = request.get_json(silent=True) or {}
        firma = data.get('firma')
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor()
        tname = _kit_table_name(cursor)
        cursor.execute(f"UPDATE {tname} SET firma_inspector=%s, firma_inspector_fecha=NOW() WHERE id=%s", (firma, item_id))
        connection.commit()
        cursor.close(); connection.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mpa/inspecciones/<int:inspeccion_id>', methods=['GET'])
@login_required
def api_get_inspeccion(inspeccion_id):
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)

        # Descubrir columnas disponibles para construir JOIN dinámico
        cursor.execute("DESCRIBE mpa_inspeccion_vehiculo")
        cols_info = cursor.fetchall() or []
        col_names = set()
        for ci in cols_info:
            try:
                col_names.add(ci.get('Field') or ci.get('field') or ci[0])
            except Exception:
                pass

        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        ro_exists = cursor.fetchone() is not None

        posibles_tecnico_fk = ['id_codigo_consumidor','tecnico_id','tecnico','id_tecnico']
        col_tecnico_fk = next((c for c in posibles_tecnico_fk if c in col_names), None)
        col_nombre = 'nombre' if 'nombre' in col_names else None

        if ro_exists and col_tecnico_fk:
            tecnico_select = f"COALESCE(ro.nombre, CAST(i.{col_tecnico_fk} AS CHAR)) AS tecnico_nombre"
            joins = f"LEFT JOIN recurso_operativo ro ON ro.id_codigo_consumidor = i.{col_tecnico_fk}"
        elif col_nombre:
            tecnico_select = "i.nombre AS tecnico_nombre"
            joins = ""
        elif col_tecnico_fk:
            tecnico_select = f"CAST(i.{col_tecnico_fk} AS CHAR) AS tecnico_nombre"
            joins = ""
        else:
            tecnico_select = "NULL AS tecnico_nombre"
            joins = ""

        query = f"""
            SELECT i.*, {tecnico_select}
            FROM mpa_inspeccion_vehiculo i
            {joins}
            WHERE i.id_mpa_inspeccion_vehiculo = %s
        """

        cursor.execute(query, (inspeccion_id,))
        r = cursor.fetchone()
        if not r:
            return jsonify({'success': False, 'error': 'Inspección no encontrada'}), 404
        fi = r.get('fecha_inspeccion')
        if fi:
            try:
                r['fecha_inspeccion'] = fi.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass
        for k in ('vencimiento_licencia','vencimiento_soat','vencimiento_tecnicomecanica'):
            v = r.get(k)
            if v:
                try:
                    r[k] = v.strftime('%Y-%m-%d')
                except Exception:
                    pass
        return jsonify({'success': True, 'data': r})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/mpa/inspecciones', methods=['POST'])
@login_required
def api_create_inspeccion():
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        data = request.get_json(silent=True) or {}
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SHOW TABLES LIKE 'mpa_inspeccion_vehiculo'")
            if not cursor.fetchone():
                try:
                    ensure_mpa_inspeccion_vehiculo_table()
                    cursor.execute("SHOW TABLES LIKE 'mpa_inspeccion_vehiculo'")
                    if not cursor.fetchone():
                        return jsonify({'success': False, 'error': 'Tabla de inspecciones no disponible'}), 500
                except Exception:
                    return jsonify({'success': False, 'error': 'Tabla de inspecciones no disponible'}), 500
        except Exception:
            return jsonify({'success': False, 'error': 'Tabla de inspecciones no disponible'}), 500
        tecnico_id = data.get('tecnico_id')
        placa = (data.get('placa') or '').strip().upper()
        ro = None
        if tecnico_id:
            cursor.execute("SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula FROM recurso_operativo WHERE id_codigo_consumidor=%s AND estado='Activo'", (tecnico_id,))
            ro = cursor.fetchone()
        if not placa and tecnico_id:
            cursor.execute("SELECT placa FROM mpa_vehiculos WHERE tecnico_asignado=%s ORDER BY fecha_creacion DESC LIMIT 1", (tecnico_id,))
            rowp = cursor.fetchone()
            placa = (rowp or {}).get('placa') if rowp else placa
        veh = None
        if placa:
            cursor.execute("DESCRIBE mpa_vehiculos")
            cols_info_v = cursor.fetchall() or []
            v_cols = set()
            for ci in cols_info_v:
                try:
                    v_cols.add(ci.get('Field') or ci.get('field') or ci[0])
                except Exception:
                    pass
            sel_cols = ["marca","linea","modelo","color"]
            if 'cilindraje' in v_cols:
                sel_cols.append("cilindraje")
            elif 'cilindraje_cc' in v_cols:
                sel_cols.append("cilindraje_cc AS cilindraje")
            else:
                sel_cols.append("NULL AS cilindraje")
            cursor.execute(f"SELECT {', '.join(sel_cols)} FROM mpa_vehiculos WHERE placa=%s", (placa,))
            veh = cursor.fetchone()
        fecha_inspeccion = get_bogota_datetime().replace(tzinfo=None)
        venc_lic = None
        venc_soat = None
        venc_tm = None
        if tecnico_id:
            cursor.execute("SELECT fecha_vencimiento FROM mpa_licencia_conducir WHERE tecnico=%s AND fecha_vencimiento IS NOT NULL AND fecha_vencimiento > '1900-01-01' ORDER BY fecha_vencimiento DESC LIMIT 1", (tecnico_id,))
            rl = cursor.fetchone()
            venc_lic = (rl or {}).get('fecha_vencimiento')
        if placa:
            cursor.execute("SELECT fecha_vencimiento FROM mpa_soat WHERE placa=%s AND fecha_vencimiento IS NOT NULL AND fecha_vencimiento > '1900-01-01' ORDER BY fecha_vencimiento DESC LIMIT 1", (placa,))
            rs = cursor.fetchone()
            venc_soat = (rs or {}).get('fecha_vencimiento')
            cursor.execute("SELECT fecha_vencimiento FROM mpa_tecnico_mecanica WHERE placa=%s AND fecha_vencimiento IS NOT NULL AND fecha_vencimiento > '1900-01-01' ORDER BY fecha_vencimiento DESC LIMIT 1", (placa,))
            rt = cursor.fetchone()
            venc_tm = (rt or {}).get('fecha_vencimiento')
        def bm(v):
            s = str(v or '').strip().upper()
            return 'B' if s in ('B','BUENO') else ('M' if s in ('M','MALO') else None)
        bm_fields = [
            'estado_fisico_espejos_laterales','estado_fisico_pito','estado_fisico_freno_servicio','estado_fisico_manillares','estado_fisico_guayas','estado_fisico_tanque_combustible','estado_fisico_encendido','estado_fisico_pedales','estado_fisico_guardabarros','estado_fisico_sillin_tapiceria','estado_fisico_tablero','estado_fisico_mofle_silenciador','estado_fisico_kit_arrastre','estado_fisico_reposa_pies','estado_fisico_pata_lateral_central','estado_fisico_tijera_amortiguador','estado_fisico_bateria','luces_altas_bajas','luces_direccionales_delanteros','luces_direccionales_traseros','luces_luz_placa','luces_stop','prevension_casco','prevension_guantes','prevension_rodilleras','prevension_coderas','llantas_labrado_llantas','llantas_rines','llantas_presion_aire','otros_aceite','otros_suspension_direccion','otros_caja_cambios','otros_conexiones_electricas'
        ]
        fields = {
            'id_codigo_consumidor': tecnico_id,
            'nombre': (ro or {}).get('nombre') or data.get('nombre'),
            'recurso_operativo_cedula': (ro or {}).get('recurso_operativo_cedula') or data.get('cedula'),
            'fecha_inspeccion': fecha_inspeccion,
            'placa': placa or data.get('placa'),
            'marca': (veh or {}).get('marca'),
            'linea': (veh or {}).get('linea'),
            'modelo': (veh or {}).get('modelo'),
            'color': (veh or {}).get('color'),
            'cilindraje': (veh or {}).get('cilindraje'),
            'vencimiento_licencia': venc_lic,
            'vencimiento_soat': venc_soat,
            'vencimiento_tecnicomecanica': venc_tm,
            'observaciones': data.get('observaciones')
        }
        for k in bm_fields:
            fields[k] = bm(data.get(k))
        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'mpa_inspeccion_vehiculo'
            """
        )
        existing_cols = {r['COLUMN_NAME'] if isinstance(r, dict) else r[0] for r in cursor.fetchall()}

        # Asegurar columnas de evidencia y tipos adecuados (foto1, foto2, foto3 como LONGTEXT)
        try:
            cur_alter = connection.cursor(dictionary=True)
            for c in ('foto1','foto2','foto3'):
                if c not in existing_cols:
                    try:
                        cur_alter.execute(f"ALTER TABLE mpa_inspeccion_vehiculo ADD COLUMN {c} LONGTEXT NULL")
                        connection.commit()
                        existing_cols.add(c)
                    except Exception:
                        pass
                else:
                    try:
                        cur_alter.execute(
                            """
                            SELECT DATA_TYPE
                            FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'mpa_inspeccion_vehiculo' AND COLUMN_NAME = %s
                            """,
                            (c,)
                        )
                        dt = (cur_alter.fetchone() or {}).get('DATA_TYPE')
                        if dt and dt.lower() != 'longtext':
                            try:
                                cur_alter.execute(f"ALTER TABLE mpa_inspeccion_vehiculo MODIFY COLUMN {c} LONGTEXT NULL")
                                connection.commit()
                            except Exception:
                                pass
                    except Exception:
                        pass
            # Asegurar columnas observaciones y recurso_operativo_cedula
            if 'observaciones' not in existing_cols:
                try:
                    cur_alter.execute("ALTER TABLE mpa_inspeccion_vehiculo ADD COLUMN observaciones TEXT NULL")
                    connection.commit(); existing_cols.add('observaciones')
                except Exception:
                    pass
            if 'recurso_operativo_cedula' not in existing_cols:
                try:
                    cur_alter.execute("ALTER TABLE mpa_inspeccion_vehiculo ADD COLUMN recurso_operativo_cedula VARCHAR(32) NULL")
                    connection.commit(); existing_cols.add('recurso_operativo_cedula')
                except Exception:
                    pass
            cur_alter.close()
        except Exception:
            try:
                connection.rollback()
            except Exception:
                pass

        # Asegurar que el id del técnico se almacene en la columna correcta según exista
        if tecnico_id:
            for tk in ('id_codigo_consumidor','tecnico_id','tecnico','id_tecnico'):
                if tk in existing_cols:
                    fields[tk] = tecnico_id
                    break

        # Mapear sinónimos prevension_* -> prevencion_* si la tabla usa la ortografía 'prevencion'
        syn_map = {
            'prevension_casco': 'prevencion_casco',
            'prevension_guantes': 'prevencion_guantes',
            'prevension_rodilleras': 'prevencion_rodilleras',
            'prevension_coderas': 'prevencion_coderas'
        }
        for src, dst in syn_map.items():
            if dst in existing_cols and src in fields and src not in existing_cols:
                fields[dst] = fields.get(src)
        # Incluir fotos en los campos si existen
        for fk in ('foto1','foto2','foto3'):
            if fk in data and fk in existing_cols:
                fields[fk] = data.get(fk)

        filtered = [(k, v) for k, v in fields.items() if k in existing_cols]
        cols = ",".join([k for k, _ in filtered])
        vals = tuple([v for _, v in filtered])
        set_stmt = ",".join([f"{k}=%s" for k, _ in filtered])
        cursor.execute(f"INSERT INTO mpa_inspeccion_vehiculo ({cols}) VALUES ({','.join(['%s']*len(filtered))})", vals)
        connection.commit()
        nid = cursor.lastrowid
        return jsonify({'success': True, 'id_mpa_inspeccion_vehiculo': nid})
    except Exception as e:
        if 'connection' in locals() and connection:
            try:
                connection.rollback()
            except Exception:
                pass
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/mpa/inspecciones/<int:inspeccion_id>/firma-trabajador', methods=['PUT'])
@login_required
def api_inspecciones_firma_trabajador(inspeccion_id):
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        data = request.get_json(silent=True) or {}
        firma = data.get('firma')
        if not firma:
            return jsonify({'success': False, 'error': 'Firma requerida'}), 400
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor()
        try:
            cur_chk = connection.cursor(dictionary=True)
            cur_chk.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'mpa_inspeccion_vehiculo'")
            rows = cur_chk.fetchall() or []
            col_types = {}
            for row in rows:
                try:
                    cn = row.get('COLUMN_NAME') or row.get('column_name') or row[0]
                    dt = (row.get('DATA_TYPE') or row.get('data_type') or row[1] or '').lower()
                    col_types[cn] = dt
                except Exception:
                    pass
            cur_chk.close()
            for c in ('firma_trabajador','firma_inspector'):
                if c not in col_types:
                    cur_alter_add = connection.cursor()
                    try:
                        cur_alter_add.execute(f"ALTER TABLE mpa_inspeccion_vehiculo ADD COLUMN {c} LONGTEXT NULL")
                        connection.commit()
                    except Exception:
                        pass
                    finally:
                        cur_alter_add.close()
                else:
                    dt = col_types.get(c)
                    if dt and dt != 'longtext':
                        cur_alter_mod = connection.cursor()
                        try:
                            cur_alter_mod.execute(f"ALTER TABLE mpa_inspeccion_vehiculo MODIFY COLUMN {c} LONGTEXT NULL")
                            connection.commit()
                        except Exception:
                            pass
                        finally:
                            cur_alter_mod.close()
        except Exception:
            try:
                connection.rollback()
            except Exception:
                pass
        cursor.execute("UPDATE mpa_inspeccion_vehiculo SET firma_trabajador=%s, firma_trabajador_fecha=NOW() WHERE id_mpa_inspeccion_vehiculo=%s", (firma, inspeccion_id))
        connection.commit()
        return jsonify({'success': True})
    except Exception as e:
        if 'connection' in locals() and connection:
            try:
                connection.rollback()
            except Exception:
                pass
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        try:
            cursor.close(); connection.close()
        except Exception:
            pass

@app.route('/api/mpa/inspecciones/<int:inspeccion_id>/firma-inspector', methods=['PUT'])
@login_required
def api_inspecciones_firma_inspector(inspeccion_id):
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        data = request.get_json(silent=True) or {}
        firma = data.get('firma')
        if not firma:
            return jsonify({'success': False, 'error': 'Firma requerida'}), 400
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor()
        try:
            cur_chk = connection.cursor(dictionary=True)
            cur_chk.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'mpa_inspeccion_vehiculo'")
            rows = cur_chk.fetchall() or []
            col_types = {}
            for row in rows:
                try:
                    cn = row.get('COLUMN_NAME') or row.get('column_name') or row[0]
                    dt = (row.get('DATA_TYPE') or row.get('data_type') or row[1] or '').lower()
                    col_types[cn] = dt
                except Exception:
                    pass
            cur_chk.close()
            for c in ('firma_trabajador','firma_inspector'):
                if c not in col_types:
                    cur_alter_add = connection.cursor()
                    try:
                        cur_alter_add.execute(f"ALTER TABLE mpa_inspeccion_vehiculo ADD COLUMN {c} LONGTEXT NULL")
                        connection.commit()
                    except Exception:
                        pass
                    finally:
                        cur_alter_add.close()
                else:
                    dt = col_types.get(c)
                    if dt and dt != 'longtext':
                        cur_alter_mod = connection.cursor()
                        try:
                            cur_alter_mod.execute(f"ALTER TABLE mpa_inspeccion_vehiculo MODIFY COLUMN {c} LONGTEXT NULL")
                            connection.commit()
                        except Exception:
                            pass
                        finally:
                            cur_alter_mod.close()
        except Exception:
            try:
                connection.rollback()
            except Exception:
                pass
        cursor.execute("UPDATE mpa_inspeccion_vehiculo SET firma_inspector=%s, firma_inspector_fecha=NOW() WHERE id_mpa_inspeccion_vehiculo=%s", (firma, inspeccion_id))
        connection.commit()
        return jsonify({'success': True})
    except Exception as e:
        if 'connection' in locals() and connection:
            try:
                connection.rollback()
            except Exception:
                pass
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        try:
            cursor.close(); connection.close()
        except Exception:
            pass

@app.route('/api/mpa/inspecciones/<int:inspeccion_id>/pdf', methods=['GET'])
@login_required
def api_inspeccion_pdf(inspeccion_id):
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)

        cursor.execute("DESCRIBE mpa_inspeccion_vehiculo")
        cols_info = cursor.fetchall() or []
        col_names = set()
        for ci in cols_info:
            try:
                col_names.add(ci.get('Field') or ci.get('field') or ci[0])
            except Exception:
                pass

        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        ro_exists = cursor.fetchone() is not None

        posibles_tecnico_fk = ['id_codigo_consumidor','tecnico_id','tecnico','id_tecnico']
        col_tecnico_fk = next((c for c in posibles_tecnico_fk if c in col_names), None)
        col_nombre = 'nombre' if 'nombre' in col_names else None

        if ro_exists and col_tecnico_fk:
            tecnico_select = f"COALESCE(ro.nombre, CAST(i.{col_tecnico_fk} AS CHAR)) AS tecnico_nombre"
            joins = f"LEFT JOIN recurso_operativo ro ON ro.id_codigo_consumidor = i.{col_tecnico_fk}"
        elif col_nombre:
            tecnico_select = "i.nombre AS tecnico_nombre"
            joins = ""
        elif col_tecnico_fk:
            tecnico_select = f"CAST(i.{col_tecnico_fk} AS CHAR) AS tecnico_nombre"
            joins = ""
        else:
            tecnico_select = "NULL AS tecnico_nombre"
            joins = ""

        query = f"""
            SELECT i.*, {tecnico_select}
            FROM mpa_inspeccion_vehiculo i
            {joins}
            WHERE i.id_mpa_inspeccion_vehiculo = %s
        """
        cursor.execute(query, (inspeccion_id,))
        r = cursor.fetchone()
        if not r:
            return jsonify({'success': False, 'error': 'Inspección no encontrada'}), 404

        fi = r.get('fecha_inspeccion')
        if fi:
            try:
                r['fecha_inspeccion'] = fi.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass
        for k in ('vencimiento_licencia','vencimiento_soat','vencimiento_tecnicomecanica'):
            v = r.get(k)
            if v:
                try:
                    r[k] = v.strftime('%Y-%m-%d')
                except Exception:
                    pass

        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors

        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm)
        styles = getSampleStyleSheet()
        elements = []

        title = Paragraph("Inspección Vehicular", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        resumen_data = [
            ["Fecha", str(r.get('fecha_inspeccion') or '')],
            ["Técnico", str(r.get('tecnico_nombre') or '')],
            ["Placa", str(r.get('placa') or '')],
            ["Observaciones", str(r.get('observaciones') or '')]
        ]
        resumen_table = Table(resumen_data, colWidths=[120, 380])
        resumen_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke)
        ]))
        elements.append(resumen_table)
        elements.append(Spacer(1, 12))

        venc_data = [
            ["Venc. Licencia", str(r.get('vencimiento_licencia') or '-')],
            ["Venc. SOAT", str(r.get('vencimiento_soat') or '-')],
            ["Venc. Tecnicomecánica", str(r.get('vencimiento_tecnicomecanica') or '-')]
        ]

        bm_groups = {
            'Estado físico': [
                ('estado_fisico_espejos_laterales','Espejos laterales'),
                ('estado_fisico_pito','Pito'),
                ('estado_fisico_freno_servicio','Freno servicio'),
                ('estado_fisico_manillares','Manillares'),
                ('estado_fisico_guayas','Guayas'),
                ('estado_fisico_tanque_combustible','Tanque de combustible'),
                ('estado_fisico_encendido','Encendido'),
                ('estado_fisico_pedales','Pedales'),
                ('estado_fisico_guardabarros','Guardabarros'),
                ('estado_fisico_sillin_tapiceria','Sillín/Tapicería'),
                ('estado_fisico_tablero','Tablero'),
                ('estado_fisico_mofle_silenciador','Mofle/Silenciador'),
                ('estado_fisico_kit_arrastre','Kit de arrastre'),
                ('estado_fisico_reposa_pies','Reposa pies'),
                ('estado_fisico_pata_lateral_central','Pata lateral/central'),
                ('estado_fisico_tijera_amortiguador','Tijera/Amortiguador'),
                ('estado_fisico_bateria','Batería')
            ],
            'Luces': [
                ('luces_altas_bajas','Luces altas/bajas'),
                ('luces_direccionales_delanteros','Direccionales delanteros'),
                ('luces_direccionales_traseros','Direccionales traseros'),
                ('luces_luz_placa','Luz placa'),
                ('luces_stop','Stop')
            ],
            'Prevención': [
                ('prevension_casco','Casco'),
                ('prevension_guantes','Guantes'),
                ('prevension_rodilleras','Rodilleras'),
                ('prevension_coderas','Coderas')
            ],
            'Llantas': [
                ('llantas_labrado_llantas','Labrado de llantas'),
                ('llantas_rines','Rines'),
                ('llantas_presion_aire','Presión de aire')
            ],
            'Otros': [
                ('otros_aceite','Aceite'),
                ('otros_suspension_direccion','Suspensión/Dirección'),
                ('otros_caja_cambios','Caja de cambios'),
                ('otros_conexiones_electricas','Conexiones eléctricas')
            ]
        }

        bm_synonyms = {
            'prevension_casco': ['prevencion_casco'],
            'prevension_guantes': ['prevencion_guantes'],
            'prevension_rodilleras': ['prevencion_rodilleras'],
            'prevension_coderas': ['prevencion_coderas']
        }

        def norm_bm(v):
            s = str(v or '').strip().upper()
            if s in ('B','BUENO'):
                return 'Bueno'
            if s in ('M','MALO'):
                return 'Malo'
            return '-'

        total_b = 0
        total_m = 0
        # Calcular totales antes de renderizar tablas
        for _grupo, _items in bm_groups.items():
            for key,_label in _items:
                v = r.get(key)
                if v is None:
                    for alt in bm_synonyms.get(key, []):
                        if alt in r:
                            v = r.get(alt)
                            break
                valp = norm_bm(v)
                if valp == 'Bueno':
                    total_b += 1
                elif valp == 'Malo':
                    total_m += 1

        # Construir tabla combinada de Vencimientos (2 columnas) y Estado (2 columnas) en la misma fila
        combined_rows = [["Vencimientos", "", "Estado", ""]]
        estado_data = [["Total Bueno", str(total_b)], ["Total Malo", str(total_m)]]
        max_rows = max(len(venc_data), len(estado_data))
        for i in range(max_rows):
            left = venc_data[i] if i < len(venc_data) else ["", ""]
            right = estado_data[i] if i < len(estado_data) else ["", ""]
            combined_rows.append([left[0], left[1], right[0], right[1]])
        comb_table = Table(combined_rows, colWidths=[doc.width/4, doc.width/4, doc.width/4, doc.width/4])
        comb_style = TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
            ('SPAN', (0,0), (1,0)),
            ('SPAN', (2,0), (3,0)),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('ALIGN', (0,1), (1,-1), 'LEFT'),
            ('ALIGN', (2,1), (3,-1), 'LEFT')
        ])
        # Colorear valores de Total Bueno/Malo
        for idx in range(1, len(combined_rows)):
            if combined_rows[idx][2] == 'Total Bueno':
                comb_style.add('TEXTCOLOR', (3, idx), (3, idx), colors.green)
            if combined_rows[idx][2] == 'Total Malo':
                comb_style.add('TEXTCOLOR', (3, idx), (3, idx), colors.red)
        comb_table.setStyle(comb_style)
        elements.append(comb_table)
        elements.append(Spacer(1, 12))
        for grupo, items in bm_groups.items():
            data = [['Ítem','Estado']]
            for key,label in items:
                v = r.get(key)
                if v is None:
                    for alt in bm_synonyms.get(key, []):
                        if alt in r:
                            v = r.get(alt)
                            break
                val = norm_bm(v)
                data.append([label, val])
                if val == 'Bueno':
                    total_b += 1
                elif val == 'Malo':
                    total_m += 1
            table = Table(data, colWidths=[300, 200])
            style = TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('ALIGN', (0,0), (-1,-1), 'LEFT')
            ])
            for i in range(1, len(data)):
                v = data[i][1]
                if v == 'Bueno':
                    style.add('TEXTCOLOR', (1,i), (1,i), colors.green)
                elif v == 'Malo':
                    style.add('TEXTCOLOR', (1,i), (1,i), colors.red)
            table.setStyle(style)
            elements.append(Paragraph(grupo, styles['Heading3']))
            elements.append(table)
            elements.append(Spacer(1, 8))

        # (Totales integrados en la tabla combinada con vencimientos)

        def img_from_data_url(data_url, max_w=180, max_h=180):
            try:
                if not data_url or 'base64,' not in data_url:
                    return None
                b64 = data_url.split('base64,', 1)[1]
                import base64
                raw = base64.b64decode(b64)
                bio = io.BytesIO(raw)
                im = Image(bio)
                im._restrictSize(max_w, max_h)
                return im
            except Exception:
                return None

        elements.append(Paragraph("Evidencias", styles['Heading2']))
        evid_cells = []
        fotos_keys = ('foto1','foto2','foto3')
        for k in fotos_keys:
            im = img_from_data_url(r.get(k), max_w=int(doc.width/3 - 12), max_h=160)
            evid_cells.append(im if im else Paragraph("", styles['Normal']))
        evid_table = Table([evid_cells], colWidths=[doc.width/3, doc.width/3, doc.width/3])
        evid_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        elements.append(KeepTogether(evid_table))
        elements.append(Spacer(1, 12))

        ft = img_from_data_url(r.get('firma_trabajador'), max_w=250, max_h=100)
        fi_img = img_from_data_url(r.get('firma_inspector'), max_w=250, max_h=100)
        elements.append(Paragraph("Firmas", styles['Heading2']))
        if ft or fi_img:
            left_cell = [Paragraph("Trabajador", styles['Heading3'])]
            if ft:
                left_cell.append(ft)
            else:
                left_cell.append(Paragraph("Sin firma", styles['Normal']))
            right_cell = [Paragraph("Inspector", styles['Heading3'])]
            if fi_img:
                right_cell.append(fi_img)
            else:
                right_cell.append(Paragraph("Sin firma", styles['Normal']))
            sig_table = Table([[left_cell, right_cell]], colWidths=[doc.width/2, doc.width/2])
            sig_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP')
            ]))
            elements.append(KeepTogether(sig_table))
        else:
            elements.append(Paragraph("Sin firmas", styles['Normal']))

        doc.build(elements)
        output.seek(0)
        fn = f"inspeccion_{str(r.get('placa') or 'sinplaca')}_{str(r.get('fecha_inspeccion') or '').replace(' ','_').replace(':','-')}.pdf"
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={fn}'
        return response
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            connection.close()
        except Exception:
            pass
# API para subir imágenes de mantenimiento
@app.route('/api/mpa/mantenimientos/upload-image', methods=['POST'])
@login_required
def api_upload_mantenimiento_image():
    """API para subir imágenes de mantenimiento"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No se encontró archivo de imagen'}), 400
        
        file = request.files['image']
        image_type = request.form.get('type', 'taller')  # 'taller' o 'factura'
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'}), 400
        
        # Validar tipo de archivo
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'error': 'Tipo de archivo no permitido'}), 400
        
        # Crear directorio si no existe
        import os
        upload_dir = os.path.join('static', 'uploads', 'mantenimientos')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generar nombre único para el archivo
        import uuid
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{image_type}_{file.filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Guardar archivo
        file.save(file_path)
        
        # Retornar ruta relativa para almacenar en BD
        relative_path = f"uploads/mantenimientos/{unique_filename}"
        
        return jsonify({
            'success': True,
            'message': 'Imagen subida exitosamente',
            'file_path': relative_path
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== APIS DE SOAT =====

# API para obtener todos los SOATs
@app.route('/api/mpa/soat', methods=['GET'])
@login_required
def api_get_soat():
    """API para obtener lista de SOATs (soporta filtros opcionales por placa y estado)"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener fecha actual de Bogotá
        fecha_bogota = get_bogota_datetime().date()
        
        placa = request.args.get('placa')
        estado = request.args.get('estado')
        where = []
        params = [fecha_bogota]

        if placa:
            where.append("UPPER(TRIM(s.placa)) = %s")
            params.append((placa or '').strip().upper())
        if estado:
            where.append("s.estado = %s")
            params.append(estado)

        cursor.execute("SHOW TABLES LIKE 'mpa_soat'")
        if not cursor.fetchone():
            return jsonify({'success': True, 'data': []})
        cursor.execute("SHOW TABLES LIKE 'mpa_vehiculos'")
        veh_exists = cursor.fetchone() is not None
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        ro_exists = cursor.fetchone() is not None

        select_cols = [
            "s.id_mpa_soat",
            "s.placa",
            "s.numero_poliza",
            "s.aseguradora",
            "s.fecha_inicio",
            "s.fecha_vencimiento",
            "s.valor_prima",
            "s.tecnico_asignado",
            "s.estado",
            "s.observaciones",
            "s.fecha_creacion",
            "s.fecha_actualizacion",
            "DATEDIFF(s.fecha_vencimiento, %s) as dias_vencimiento"
        ]
        if veh_exists:
            select_cols.append("v.tipo_vehiculo")
        else:
            select_cols.append("NULL as tipo_vehiculo")
        if ro_exists:
            select_cols.append("COALESCE(ro.nombre, CAST(s.tecnico_asignado AS CHAR)) as tecnico_nombre")
        else:
            select_cols.append("CAST(s.tecnico_asignado AS CHAR) as tecnico_nombre")

        joins = []
        if veh_exists:
            joins.append("LEFT JOIN mpa_vehiculos v ON s.placa = v.placa")
        if ro_exists:
            joins.append("LEFT JOIN recurso_operativo ro ON s.tecnico_asignado = ro.id_codigo_consumidor")

        query = f"""
        SELECT {', '.join(select_cols)}
        FROM mpa_soat s
        {' '.join(joins)}
        {('WHERE ' + ' AND '.join(where)) if where else ''}
        ORDER BY s.fecha_vencimiento DESC
        """
        
        cursor.execute(query, tuple(params))
        soats = cursor.fetchall()
        
        # Convertir fechas a string para JSON
        for soat in soats:
            if soat['fecha_inicio']:
                soat['fecha_inicio'] = soat['fecha_inicio'].strftime('%Y-%m-%d')
            if soat['fecha_vencimiento']:
                soat['fecha_vencimiento'] = soat['fecha_vencimiento'].strftime('%Y-%m-%d')
            if soat['fecha_creacion']:
                soat['fecha_creacion'] = soat['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')
            if soat['fecha_actualizacion']:
                soat['fecha_actualizacion'] = soat['fecha_actualizacion'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'data': soats
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para obtener un SOAT específico
@app.route('/api/mpa/soat/<int:soat_id>', methods=['GET'])
@login_required
def api_get_soat_by_id(soat_id):
    """API para obtener un SOAT específico por ID"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener fecha actual de Bogotá
        fecha_bogota = get_bogota_datetime().date()
        
        cursor.execute("SHOW TABLES LIKE 'mpa_soat'")
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'SOAT no encontrado'}), 404
        cursor.execute("SHOW TABLES LIKE 'mpa_vehiculos'")
        veh_exists = cursor.fetchone() is not None
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        ro_exists = cursor.fetchone() is not None

        select_cols = [
            "s.id_mpa_soat",
            "s.placa",
            "s.numero_poliza",
            "s.aseguradora",
            "s.fecha_inicio",
            "s.fecha_vencimiento",
            "s.valor_prima",
            "s.tecnico_asignado",
            "s.estado",
            "s.observaciones",
            "s.fecha_creacion",
            "s.fecha_actualizacion",
            "DATEDIFF(s.fecha_vencimiento, %s) as dias_vencimiento"
        ]
        if veh_exists:
            select_cols.append("v.tipo_vehiculo")
        else:
            select_cols.append("NULL as tipo_vehiculo")
        if ro_exists:
            select_cols.append("COALESCE(ro.nombre, CAST(s.tecnico_asignado AS CHAR)) as tecnico_nombre")
        else:
            select_cols.append("CAST(s.tecnico_asignado AS CHAR) as tecnico_nombre")

        joins = []
        if veh_exists:
            joins.append("LEFT JOIN mpa_vehiculos v ON s.placa = v.placa")
        if ro_exists:
            joins.append("LEFT JOIN recurso_operativo ro ON s.tecnico_asignado = ro.id_codigo_consumidor")

        query = f"""
        SELECT {', '.join(select_cols)}
        FROM mpa_soat s
        {' '.join(joins)}
        WHERE s.id_mpa_soat = %s
        """
        
        cursor.execute(query, (fecha_bogota, soat_id))
        soat = cursor.fetchone()
        
        if not soat:
            return jsonify({'success': False, 'error': 'SOAT no encontrado'}), 404
        
        # Convertir fechas a string para JSON
        if soat['fecha_inicio']:
            soat['fecha_inicio'] = soat['fecha_inicio'].strftime('%Y-%m-%d')
        if soat['fecha_vencimiento']:
            soat['fecha_vencimiento'] = soat['fecha_vencimiento'].strftime('%Y-%m-%d')
        if soat['fecha_creacion']:
            soat['fecha_creacion'] = soat['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')
        if soat['fecha_actualizacion']:
            soat['fecha_actualizacion'] = soat['fecha_actualizacion'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'data': soat
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para crear un nuevo SOAT
@app.route('/api/mpa/soat', methods=['POST'])
@login_required
def api_create_soat():
    """API para crear un nuevo SOAT"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['placa', 'numero_poliza', 'aseguradora', 'fecha_inicio', 'fecha_vencimiento', 'valor_prima']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor()
        
        # Verificar que la placa existe en vehículos
        cursor.execute("SELECT placa, tecnico_asignado FROM mpa_vehiculos WHERE placa = %s AND estado = 'Activo'", (data['placa'],))
        vehiculo = cursor.fetchone()
        
        if not vehiculo:
            return jsonify({'success': False, 'error': 'Vehículo no encontrado o inactivo'}), 400
        
        # Usar el técnico asignado del vehículo si no se especifica
        tecnico_asignado = data.get('tecnico_asignado', vehiculo[1])
        
        # Verificar si ya existe un SOAT activo y vigente para esta placa
        cursor.execute("""
            SELECT id_mpa_soat FROM mpa_soat 
            WHERE placa = %s AND estado = 'Activo' AND fecha_vencimiento >= CURDATE()
        """, (data['placa'],))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Ya existe un SOAT activo para esta placa'}), 400
        
        # Insertar nuevo SOAT
        query = """
        INSERT INTO mpa_soat (
            placa, numero_poliza, aseguradora, fecha_inicio, fecha_vencimiento,
            valor_prima, tecnico_asignado, estado, observaciones, fecha_creacion
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        
        values = (
            data['placa'],
            data['numero_poliza'],
            data['aseguradora'],
            data['fecha_inicio'],
            data['fecha_vencimiento'],
            data['valor_prima'],
            tecnico_asignado,
            data.get('estado', 'Activo'),
            data.get('observaciones', '')
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        soat_id = cursor.lastrowid
        
        return jsonify({
            'success': True,
            'message': 'SOAT creado exitosamente',
            'data': {'id_mpa_soat': soat_id}
        })
        
    except Exception as e:
        if 'connection' in locals() and connection:
            connection.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para actualizar un SOAT
@app.route('/api/mpa/soat/<int:soat_id>', methods=['PUT'])
@login_required
def api_update_soat(soat_id):
    """API para actualizar un SOAT existente"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        data = request.get_json()
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor()
        
        # Verificar que el SOAT existe
        cursor.execute("SELECT id_mpa_soat FROM mpa_soat WHERE id_mpa_soat = %s", (soat_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'SOAT no encontrado'}), 404
        
        # Construir query de actualización dinámicamente
        update_fields = []
        values = []
        
        allowed_fields = ['numero_poliza', 'aseguradora', 'fecha_inicio', 'fecha_vencimiento', 
                         'valor_prima', 'tecnico_asignado', 'estado', 'observaciones']
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                values.append(data[field])
        
        if not update_fields:
            return jsonify({'success': False, 'error': 'No hay campos para actualizar'}), 400
        
        # Agregar fecha de actualización
        update_fields.append("fecha_actualizacion = NOW()")
        values.append(soat_id)
        
        query = f"UPDATE mpa_soat SET {', '.join(update_fields)} WHERE id_mpa_soat = %s"
        
        cursor.execute(query, values)
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'SOAT actualizado exitosamente'
        })
        
    except Exception as e:
        if 'connection' in locals() and connection:
            connection.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para eliminar un SOAT
@app.route('/api/mpa/soat/<int:soat_id>', methods=['DELETE'])
@login_required
def api_delete_soat(soat_id):
    """API para eliminar un SOAT"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor()
        
        # Verificar si el SOAT existe
        cursor.execute("SELECT id_mpa_soat FROM mpa_soat WHERE id_mpa_soat = %s", (soat_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'SOAT no encontrado'}), 404
        
        # Eliminar SOAT
        cursor.execute("DELETE FROM mpa_soat WHERE id_mpa_soat = %s", (soat_id,))
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'SOAT eliminado exitosamente'
        })
        
    except Exception as e:
        if 'connection' in locals() and connection:
            connection.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# ===== APIs VENCIMIENTOS =====

# API consolidada para obtener todos los vencimientos
@app.route('/api/mpa/vencimientos', methods=['GET'])
@login_required
def api_vencimientos_consolidados():
    """API consolidada para obtener vencimientos de SOAT, Técnico Mecánica y Licencias de Conducir"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        vencimientos_consolidados = []
        
        # 1. Obtener vencimientos de SOAT
        query_soat = """
        SELECT 
            s.id_mpa_soat as id,
            s.placa,
            s.fecha_vencimiento,
            s.tecnico_asignado,
            ro.nombre as tecnico_nombre,
            'SOAT' as tipo,
            s.estado
        FROM mpa_soat s
        LEFT JOIN recurso_operativo ro ON s.tecnico_asignado = ro.id_codigo_consumidor
        JOIN mpa_vehiculos v2 ON v2.placa = s.placa
            AND v2.id_mpa_vehiculos = (
                SELECT MAX(v3.id_mpa_vehiculos)
                FROM mpa_vehiculos v3
                WHERE v3.placa = s.placa
            )
        WHERE s.fecha_vencimiento IS NOT NULL
          AND s.fecha_vencimiento NOT LIKE '0000-00-00%'
          AND s.fecha_vencimiento > '1900-01-01'
          AND s.estado = 'Activo'
          AND UPPER(TRIM(COALESCE(v2.estado, ''))) = 'ACTIVO'
          AND (
              s.tecnico_asignado IS NULL
              OR TRIM(s.tecnico_asignado) = ''
              OR ro.estado = 'Activo'
          )
        ORDER BY s.fecha_vencimiento ASC
        """
        
        cursor.execute(query_soat)
        soats = cursor.fetchall()
        
        for soat in soats:
            vencimientos_consolidados.append({
                'id': soat['id'],
                'tipo': 'SOAT',
                'placa': soat['placa'],
                'fecha_vencimiento': soat['fecha_vencimiento'].strftime('%Y-%m-%d') if soat['fecha_vencimiento'] else None,
                'tecnico_nombre': soat['tecnico_nombre'] or 'Sin asignar',
                'estado_original': soat['estado']
            })
        
        # 2. Obtener vencimientos de Técnico Mecánica
        query_tm = """
        SELECT 
            tm.id_mpa_tecnico_mecanica as id,
            tm.placa,
            tm.fecha_vencimiento,
            tm.tecnico_asignado,
            ro.nombre as tecnico_nombre,
            'Técnico Mecánica' as tipo,
            tm.estado
        FROM mpa_tecnico_mecanica tm
        LEFT JOIN recurso_operativo ro ON tm.tecnico_asignado = ro.id_codigo_consumidor
        JOIN mpa_vehiculos v2 ON v2.placa = tm.placa
            AND v2.id_mpa_vehiculos = (
                SELECT MAX(v3.id_mpa_vehiculos)
                FROM mpa_vehiculos v3
                WHERE v3.placa = tm.placa
            )
        WHERE tm.fecha_vencimiento IS NOT NULL
          AND tm.fecha_vencimiento NOT LIKE '0000-00-00%'
          AND tm.fecha_vencimiento > '1900-01-01'
          AND tm.estado = 'Activo'
          AND UPPER(TRIM(COALESCE(v2.estado, ''))) = 'ACTIVO'
          AND (
              tm.tecnico_asignado IS NULL
              OR TRIM(tm.tecnico_asignado) = ''
              OR ro.estado = 'Activo'
          )
        ORDER BY tm.fecha_vencimiento ASC
        """
        
        cursor.execute(query_tm)
        tecnicos = cursor.fetchall()
        
        for tm in tecnicos:
            vencimientos_consolidados.append({
                'id': tm['id'],
                'tipo': 'Técnico Mecánica',
                'placa': tm['placa'],
                'fecha_vencimiento': tm['fecha_vencimiento'].strftime('%Y-%m-%d') if tm['fecha_vencimiento'] else None,
                'tecnico_nombre': tm['tecnico_nombre'] or 'Sin asignar',
                'estado_original': tm['estado']
            })
        
        # 3. Obtener vencimientos de Licencias de Conducir
        query_lc = """
        SELECT 
            lc.id_mpa_licencia_conducir as id,
            lc.fecha_vencimiento,
            lc.tecnico,
            ro.nombre as tecnico_nombre,
            'Licencia de Conducir' as tipo
        FROM mpa_licencia_conducir lc
        LEFT JOIN recurso_operativo ro ON lc.tecnico = ro.id_codigo_consumidor
        WHERE lc.fecha_vencimiento IS NOT NULL
          AND lc.fecha_vencimiento NOT LIKE '0000-00-00%'
          AND lc.fecha_vencimiento > '1900-01-01'
          AND (
              lc.tecnico IS NULL
              OR TRIM(lc.tecnico) = ''
              OR ro.estado = 'Activo'
          )
        ORDER BY lc.fecha_vencimiento ASC
        """
        
        cursor.execute(query_lc)
        licencias = cursor.fetchall()
        
        for lc in licencias:
            vencimientos_consolidados.append({
                'id': lc['id'],
                'tipo': 'Licencia de Conducir',
                'placa': None,
                'fecha_vencimiento': lc['fecha_vencimiento'].strftime('%Y-%m-%d') if lc['fecha_vencimiento'] else None,
                'tecnico_nombre': lc['tecnico_nombre'] or 'Sin asignar',
                'estado_original': None
            })

        # Filtro adicional por estado del vehículo usando el último registro por placa
        try:
            cursor.execute(
                """
                SELECT v1.placa, v1.estado
                FROM mpa_vehiculos v1
                JOIN (
                    SELECT placa, MAX(id_mpa_vehiculos) AS max_id
                    FROM mpa_vehiculos
                    GROUP BY placa
                ) t ON t.placa = v1.placa AND v1.id_mpa_vehiculos = t.max_id
                """
            )
            estados_vehiculos_rows = cursor.fetchall() or []
            estados_vehiculos = { (r.get('placa') or '').strip().upper(): (r.get('estado') or '').strip().upper() for r in estados_vehiculos_rows }
            vencimientos_consolidados = [
                v for v in vencimientos_consolidados
                if (v.get('placa') is None) or estados_vehiculos.get((v.get('placa') or '').strip().upper()) == 'ACTIVO'
            ]
        except Exception:
            pass
        
        # 4. Calcular días restantes y estado para todos los vencimientos
        from datetime import datetime, date
        import pytz
        import re
        
        colombia_tz = pytz.timezone('America/Bogota')
        fecha_actual = datetime.now(colombia_tz).date()
        
        def validar_fecha(fecha_str):
            """Valida que una fecha tenga el formato YYYY-MM-DD y sea válida"""
            if not fecha_str or fecha_str == '0000-00-00':
                return False, None, 'Sin fecha'
                
            # Validar formato YYYY-MM-DD
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', fecha_str):
                return False, None, 'Fecha inválida'
                
            try:
                # Convertir a fecha y validar
                year, month, day = map(int, fecha_str.split('-'))
                fecha = date(year, month, day)
                
                # Validar que los componentes coincidan (para detectar fechas inválidas como 2024-02-31)
                if fecha.year != year or fecha.month != month or fecha.day != day:
                    return False, None, 'Fecha inválida'
                    
                return True, fecha, None
            except ValueError:
                return False, None, 'Fecha inválida'
        
        for vencimiento in vencimientos_consolidados:
            try:
                fecha_str = vencimiento['fecha_vencimiento']
                es_valida, fecha_venc, estado_error = validar_fecha(fecha_str)
                
                if not es_valida:
                    vencimiento['dias_restantes'] = None
                    vencimiento['estado'] = estado_error
                    continue
                
                # Calcular días restantes
                dias_restantes = (fecha_venc - fecha_actual).days
                vencimiento['dias_restantes'] = dias_restantes
                
                # Determinar estado basado en días restantes
                if dias_restantes < 0:
                    vencimiento['estado'] = 'Vencido'
                elif dias_restantes <= 30:
                    vencimiento['estado'] = 'Próximo a vencer'
                else:
                    vencimiento['estado'] = 'Vigente'
                    
            except Exception as e:
                vencimiento['dias_restantes'] = None
                vencimiento['estado'] = 'Fecha inválida'
                app.logger.error(f"Error procesando fecha para vencimiento ID {vencimiento['id']}: {str(e)}", exc_info=True)
        
        # 5. Ordenar por fecha de vencimiento (más próximos primero)
        def get_sort_key(x):
            try:
                fecha_str = x['fecha_vencimiento']
                es_valida, fecha, _ = validar_fecha(fecha_str)
                if not es_valida:
                    return '9999-12-31'
                return fecha_str
            except Exception as e:
                app.logger.error(f"Error al ordenar vencimiento ID {x['id']}: {str(e)}", exc_info=True)
                return '9999-12-31'
        
        vencimientos_consolidados.sort(key=get_sort_key)
        
        # 6. Agregar estadísticas
        estadisticas = {
            'total': len(vencimientos_consolidados),
            'vencidos': sum(1 for v in vencimientos_consolidados if v['estado'] == 'Vencido'),
            'proximos_vencer': sum(1 for v in vencimientos_consolidados if v['estado'] == 'Próximo a vencer'),
            'vigentes': sum(1 for v in vencimientos_consolidados if v['estado'] == 'Vigente'),
            'sin_fecha': sum(1 for v in vencimientos_consolidados if v['estado'] in ['Sin fecha', 'Fecha inválida'])
        }
        
        return jsonify({
            'success': True,
            'data': vencimientos_consolidados,
            'total': len(vencimientos_consolidados),
            'estadisticas': estadisticas
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para obtener detalles de un vencimiento específico
@app.route('/api/mpa/vencimiento/<string:tipo>/<int:documento_id>', methods=['GET'])
@login_required
def api_get_vencimiento_detalle(tipo, documento_id):
    """API para obtener detalles de un vencimiento específico"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Determinar la tabla y consulta según el tipo
        if tipo.lower() == 'soat':
            query = """
            SELECT 
                s.*,
                ro.nombre as tecnico_nombre,
                ro.recurso_operativo_cedula as tecnico_cedula
            FROM mpa_soat s
            LEFT JOIN recurso_operativo ro ON s.tecnico_asignado = ro.id_codigo_consumidor
            WHERE s.id_mpa_soat = %s
            """
        elif tipo.lower() == 'tecnico_mecanica':
            query = """
            SELECT 
                tm.*,
                ro.nombre as tecnico_nombre,
                ro.recurso_operativo_cedula as tecnico_cedula
            FROM mpa_tecnico_mecanica tm
            LEFT JOIN recurso_operativo ro ON tm.tecnico_asignado = ro.id_codigo_consumidor
            WHERE tm.id_mpa_tecnico_mecanica = %s
            """
        elif tipo.lower() == 'licencia_conducir':
            query = """
            SELECT 
                lc.*,
                ro.nombre as tecnico_nombre,
                ro.recurso_operativo_cedula as tecnico_cedula
            FROM mpa_licencia_conducir lc
            LEFT JOIN recurso_operativo ro ON lc.tecnico = ro.id_codigo_consumidor
            WHERE lc.id_mpa_licencia_conducir = %s
            """
        else:
            return jsonify({'success': False, 'error': 'Tipo de documento no válido'}), 400
        
        cursor.execute(query, (documento_id,))
        documento = cursor.fetchone()
        
        if not documento:
            return jsonify({'success': False, 'error': 'Documento no encontrado'}), 404
        
        # Formatear fechas y calcular días restantes
        from datetime import datetime
        import pytz
        
        colombia_tz = pytz.timezone('America/Bogota')
        fecha_actual = datetime.now(colombia_tz).date()
        
        # Formatear fechas
        for key, value in documento.items():
            if isinstance(value, datetime):
                documento[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            elif hasattr(value, 'strftime'):  # Para objetos date
                documento[key] = value.strftime('%Y-%m-%d')
        
        # Calcular días restantes si hay fecha de vencimiento
        if documento.get('fecha_vencimiento'):
            try:
                fecha_venc = datetime.strptime(documento['fecha_vencimiento'], '%Y-%m-%d').date()
                dias_restantes = (fecha_venc - fecha_actual).days
                documento['dias_restantes'] = dias_restantes
                
                # Determinar estado
                if dias_restantes < 0:
                    documento['estado_calculado'] = 'Vencido'
                elif dias_restantes <= 30:
                    documento['estado_calculado'] = 'Próximo a vencer'
                else:
                    documento['estado_calculado'] = 'Vigente'
            except:
                documento['dias_restantes'] = None
                documento['estado_calculado'] = 'Sin fecha'
        
        return jsonify({
            'success': True,
            'data': documento,
            'tipo': tipo
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API de prueba con ruta diferente
@app.route('/api/mpa/test-vencimientos', methods=['GET'])
def api_test_vencimientos():
    """API de prueba para vencimientos"""
    return jsonify({
        'success': True,
        'data': [],
        'message': 'API de prueba funcionando correctamente'
    })

# ===== APIs TÉCNICO MECÁNICA =====

# API para listar todas las técnico mecánicas
@app.route('/api/mpa/tecnico_mecanica', methods=['GET'])
@login_required
def api_list_tecnico_mecanica():
    """API para obtener todas las técnico mecánicas (filtros opcionales por placa y estado)"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        placa = request.args.get('placa')
        estado = request.args.get('estado')
        where = []
        params = []

        if placa:
            where.append("UPPER(TRIM(tm.placa)) = %s")
            params.append((placa or '').strip().upper())
        if estado:
            where.append("tm.estado = %s")
            params.append(estado)

        cursor.execute("SHOW TABLES LIKE 'mpa_tecnico_mecanica'")
        if not cursor.fetchone():
            return jsonify({'success': True, 'data': []})
        cursor.execute("SHOW TABLES LIKE 'mpa_vehiculos'")
        veh_exists = cursor.fetchone() is not None
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        ro_exists = cursor.fetchone() is not None

        select_cols = [
            "tm.id_mpa_tecnico_mecanica",
            "tm.placa",
            "tm.fecha_inicio",
            "tm.fecha_vencimiento",
            "tm.tecnico_asignado",
            "tm.estado",
            "tm.observaciones",
            "tm.fecha_creacion",
            "tm.fecha_actualizacion",
            "tm.tipo_vehiculo"
        ]
        if veh_exists:
            select_cols.append("v.tipo_vehiculo as vehiculo_tipo")
            select_cols.append("v.tecnico_asignado as vehiculo_tecnico")
        else:
            select_cols.append("NULL as vehiculo_tipo")
            select_cols.append("NULL as vehiculo_tecnico")
        if ro_exists:
            select_cols.append("ro.nombre as tecnico_nombre")
        else:
            select_cols.append("CAST(tm.tecnico_asignado AS CHAR) as tecnico_nombre")

        joins = []
        if veh_exists:
            joins.append("LEFT JOIN mpa_vehiculos v ON tm.placa = v.placa")
        if ro_exists:
            joins.append("LEFT JOIN recurso_operativo ro ON tm.tecnico_asignado = ro.id_codigo_consumidor")

        query = f"""
        SELECT {', '.join(select_cols)}
        FROM mpa_tecnico_mecanica tm
        {' '.join(joins)}
        {('WHERE ' + ' AND '.join(where)) if where else ''}
        ORDER BY tm.fecha_creacion DESC
        """
        
        cursor.execute(query, tuple(params))
        tecnico_mecanicas = cursor.fetchall()
        
        # Formatear fechas y calcular días restantes
        for tm in tecnico_mecanicas:
            if tm['fecha_inicio']:
                tm['fecha_inicio'] = tm['fecha_inicio'].strftime('%Y-%m-%d')
            if tm['fecha_vencimiento']:
                tm['fecha_vencimiento'] = tm['fecha_vencimiento'].strftime('%Y-%m-%d')
                
                # Calcular días restantes usando timezone de Colombia
                from datetime import datetime
                import pytz
                
                colombia_tz = pytz.timezone('America/Bogota')
                fecha_actual = datetime.now(colombia_tz).date()
                fecha_vencimiento = tm['fecha_vencimiento']
                
                if isinstance(fecha_vencimiento, str):
                    fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date()
                
                dias_restantes = (fecha_vencimiento - fecha_actual).days
                tm['dias_vencimiento'] = dias_restantes
                
                # Determinar estado automático basado en días restantes
                if dias_restantes < 0:
                    tm['estado_calculado'] = 'Vencido'
                elif dias_restantes <= 30:
                    tm['estado_calculado'] = 'Próximo a vencer'
                else:
                    tm['estado_calculado'] = 'Vigente'
            else:
                tm['dias_vencimiento'] = None
                tm['estado_calculado'] = 'Sin fecha'
            
            if tm['fecha_creacion']:
                tm['fecha_creacion'] = tm['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')
            if tm['fecha_actualizacion']:
                tm['fecha_actualizacion'] = tm['fecha_actualizacion'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'data': tecnico_mecanicas
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para obtener una técnico mecánica específica
@app.route('/api/mpa/tecnico_mecanica/<int:tm_id>', methods=['GET'])
@login_required
def api_get_tecnico_mecanica(tm_id):
    """API para obtener una técnico mecánica específica"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SHOW TABLES LIKE 'mpa_tecnico_mecanica'")
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Técnico mecánica no encontrada'}), 404
        cursor.execute("SHOW TABLES LIKE 'mpa_vehiculos'")
        veh_exists = cursor.fetchone() is not None
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        ro_exists = cursor.fetchone() is not None

        select_cols = [
            "tm.id_mpa_tecnico_mecanica",
            "tm.placa",
            "tm.fecha_inicio",
            "tm.fecha_vencimiento",
            "tm.tecnico_asignado",
            "tm.estado",
            "tm.observaciones",
            "tm.fecha_creacion",
            "tm.fecha_actualizacion",
            "tm.tipo_vehiculo"
        ]
        if veh_exists:
            select_cols.append("v.tipo_vehiculo as vehiculo_tipo")
            select_cols.append("v.tecnico_asignado as vehiculo_tecnico")
        else:
            select_cols.append("NULL as vehiculo_tipo")
            select_cols.append("NULL as vehiculo_tecnico")
        if ro_exists:
            select_cols.append("ro.nombre as tecnico_nombre")
        else:
            select_cols.append("CAST(tm.tecnico_asignado AS CHAR) as tecnico_nombre")

        joins = []
        if veh_exists:
            joins.append("LEFT JOIN mpa_vehiculos v ON tm.placa = v.placa")
        if ro_exists:
            joins.append("LEFT JOIN recurso_operativo ro ON tm.tecnico_asignado = ro.id_codigo_consumidor")

        query = f"""
        SELECT {', '.join(select_cols)}
        FROM mpa_tecnico_mecanica tm
        {' '.join(joins)}
        WHERE tm.id_mpa_tecnico_mecanica = %s
        """
        
        cursor.execute(query, (tm_id,))
        tm = cursor.fetchone()
        
        if not tm:
            return jsonify({'success': False, 'error': 'Técnico mecánica no encontrada'}), 404
        
        # Formatear fechas y calcular días restantes
        if tm['fecha_inicio']:
            tm['fecha_inicio'] = tm['fecha_inicio'].strftime('%Y-%m-%d')
        if tm['fecha_vencimiento']:
            tm['fecha_vencimiento'] = tm['fecha_vencimiento'].strftime('%Y-%m-%d')
            
            # Calcular días restantes
            from datetime import datetime
            import pytz
            
            colombia_tz = pytz.timezone('America/Bogota')
            fecha_actual = datetime.now(colombia_tz).date()
            fecha_vencimiento = tm['fecha_vencimiento']
            
            if isinstance(fecha_vencimiento, str):
                fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date()
            
            dias_restantes = (fecha_vencimiento - fecha_actual).days
            tm['dias_vencimiento'] = dias_restantes
            
            # Determinar estado automático
            if dias_restantes < 0:
                tm['estado_calculado'] = 'Vencido'
            elif dias_restantes <= 30:
                tm['estado_calculado'] = 'Próximo a vencer'
            else:
                tm['estado_calculado'] = 'Vigente'
        else:
            tm['dias_vencimiento'] = None
            tm['estado_calculado'] = 'Sin fecha'
        
        if tm['fecha_creacion']:
            tm['fecha_creacion'] = tm['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')
        if tm['fecha_actualizacion']:
            tm['fecha_actualizacion'] = tm['fecha_actualizacion'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'data': tm
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para crear una nueva técnico mecánica
@app.route('/api/mpa/tecnico_mecanica', methods=['POST'])
@login_required
def api_create_tecnico_mecanica():
    """API para crear una nueva técnico mecánica"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['placa', 'fecha_inicio', 'fecha_vencimiento']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor()
        
        # Verificar que la placa existe en vehículos
        cursor.execute("SELECT placa, tecnico_asignado, tipo_vehiculo FROM mpa_vehiculos WHERE placa = %s AND estado = 'Activo'", (data['placa'],))
        vehiculo = cursor.fetchone()
        
        if not vehiculo:
            return jsonify({'success': False, 'error': 'Vehículo no encontrado o inactivo'}), 400
        
        # Auto-asignar técnico y tipo de vehículo del vehículo
        tecnico_asignado = data.get('tecnico_asignado', vehiculo[1])
        tipo_vehiculo = data.get('tipo_vehiculo', vehiculo[2])
        
        # Verificar si ya existe una técnico mecánica activa para esta placa
        cursor.execute("""
            SELECT id_mpa_tecnico_mecanica FROM mpa_tecnico_mecanica 
            WHERE placa = %s AND estado = 'Activo'
        """, (data['placa'],))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Ya existe una técnico mecánica activa para esta placa'}), 400
        
        # Validar fechas
        from datetime import datetime
        try:
            fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
            fecha_vencimiento = datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d').date()
            
            if fecha_vencimiento <= fecha_inicio:
                return jsonify({'success': False, 'error': 'La fecha de vencimiento debe ser posterior a la fecha de inicio'}), 400
                
        except ValueError:
            return jsonify({'success': False, 'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
        
        # Insertar nueva técnico mecánica
        query = """
        INSERT INTO mpa_tecnico_mecanica (
            placa, fecha_inicio, fecha_vencimiento, tecnico_asignado, 
            tipo_vehiculo, estado, observaciones, fecha_creacion
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """
        
        values = (
            data['placa'],
            data['fecha_inicio'],
            data['fecha_vencimiento'],
            tecnico_asignado,
            tipo_vehiculo,
            data.get('estado', 'Activo'),
            data.get('observaciones', '')
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        tm_id = cursor.lastrowid
        
        return jsonify({
            'success': True,
            'message': 'Técnico mecánica creada exitosamente',
            'data': {'id_mpa_tecnico_mecanica': tm_id}
        })
        
    except Exception as e:
        if 'connection' in locals() and connection:
            connection.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para actualizar una técnico mecánica
@app.route('/api/mpa/tecnico_mecanica/<int:tm_id>', methods=['PUT'])
@login_required
def api_update_tecnico_mecanica(tm_id):
    """API para actualizar una técnico mecánica existente"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        data = request.get_json()
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor()
        
        # Verificar que la técnico mecánica existe
        cursor.execute("SELECT id_mpa_tecnico_mecanica FROM mpa_tecnico_mecanica WHERE id_mpa_tecnico_mecanica = %s", (tm_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Técnico mecánica no encontrada'}), 404
        
        # Validar fechas si se proporcionan
        if 'fecha_inicio' in data and 'fecha_vencimiento' in data:
            try:
                from datetime import datetime
                fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
                fecha_vencimiento = datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d').date()
                
                if fecha_vencimiento <= fecha_inicio:
                    return jsonify({'success': False, 'error': 'La fecha de vencimiento debe ser posterior a la fecha de inicio'}), 400
                    
            except ValueError:
                return jsonify({'success': False, 'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
        
        # Construir query de actualización dinámicamente
        update_fields = []
        values = []
        
        allowed_fields = ['fecha_inicio', 'fecha_vencimiento', 'tecnico_asignado', 
                         'tipo_vehiculo', 'estado', 'observaciones']
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                values.append(data[field])
        
        if not update_fields:
            return jsonify({'success': False, 'error': 'No hay campos para actualizar'}), 400
        
        # Agregar fecha de actualización
        update_fields.append("fecha_actualizacion = NOW()")
        values.append(tm_id)
        
        query = f"UPDATE mpa_tecnico_mecanica SET {', '.join(update_fields)} WHERE id_mpa_tecnico_mecanica = %s"
        
        cursor.execute(query, values)
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Técnico mecánica actualizada exitosamente'
        })
        
    except Exception as e:
        if 'connection' in locals() and connection:
            connection.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para eliminar una técnico mecánica
@app.route('/api/mpa/tecnico_mecanica/<int:tm_id>', methods=['DELETE'])
@login_required
def api_delete_tecnico_mecanica(tm_id):
    """API para eliminar una técnico mecánica"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor()
        
        # Verificar si la técnico mecánica existe
        cursor.execute("SELECT id_mpa_tecnico_mecanica FROM mpa_tecnico_mecanica WHERE id_mpa_tecnico_mecanica = %s", (tm_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Técnico mecánica no encontrada'}), 404
        
        # Eliminar técnico mecánica
        cursor.execute("DELETE FROM mpa_tecnico_mecanica WHERE id_mpa_tecnico_mecanica = %s", (tm_id,))
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Técnico mecánica eliminada exitosamente'
        })
        
    except Exception as e:
        if 'connection' in locals() and connection:
            connection.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# ===== APIs LICENCIAS DE CONDUCIR =====

# API para listar todas las licencias de conducir
@app.route('/api/mpa/licencias-conducir', methods=['GET'])
@login_required
def api_list_licencias_conducir():
    """API para obtener todas las licencias de conducir (filtros opcionales por tecnico_id)"""
    allowed_roles = ('administrativo', 'sstt', 'tecnicos')
    if not any(current_user.has_role(r) for r in allowed_roles):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener fecha actual de Bogotá
        fecha_bogota = get_bogota_datetime().date()
        
        tecnico_id = request.args.get('tecnico_id')
        where = []
        params = [fecha_bogota]
        if tecnico_id:
            where.append("lc.tecnico = %s")
            params.append(tecnico_id)
        cursor.execute("SHOW TABLES LIKE 'mpa_licencia_conducir'")
        if not cursor.fetchone():
            return jsonify({'success': True, 'data': []})
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        ro_exists = cursor.fetchone() is not None

        select_cols = [
            "lc.id_mpa_licencia_conducir as id",
            "lc.tecnico as tecnico_id",
            "lc.tipo_licencia",
            "lc.fecha_inicio as fecha_inicial",
            "lc.fecha_vencimiento",
            "lc.observacion as observaciones",
            "lc.fecha_creacion as created_at",
            "lc.fecha_actualizacion as updated_at",
            "DATEDIFF(lc.fecha_vencimiento, %s) as dias_vencimiento"
        ]
        if ro_exists:
            select_cols.append("COALESCE(ro.nombre, lc.tecnico) as tecnico_nombre")
        else:
            select_cols.append("CAST(lc.tecnico AS CHAR) as tecnico_nombre")

        joins = []
        if ro_exists:
            joins.append("LEFT JOIN recurso_operativo ro ON lc.tecnico = ro.id_codigo_consumidor")

        query = f"""
        SELECT {', '.join(select_cols)}
        FROM mpa_licencia_conducir lc
        {' '.join(joins)}
        {('WHERE ' + ' AND '.join(where)) if where else ''}
        ORDER BY lc.fecha_vencimiento DESC
        """
        
        cursor.execute(query, tuple(params))
        licencias = cursor.fetchall()
        
        # Formatear fechas y calcular estado
        for licencia in licencias:
            fi = licencia.get('fecha_inicial')
            fv = licencia.get('fecha_vencimiento')
            ca = licencia.get('created_at')
            ua = licencia.get('updated_at')

            # Formateo seguro de fechas si vienen como objetos de fecha
            if isinstance(fi, (datetime, date)):
                licencia['fecha_inicial'] = fi.strftime('%Y-%m-%d')
            elif fi is None:
                licencia['fecha_inicial'] = None

            if isinstance(fv, (datetime, date)):
                licencia['fecha_vencimiento'] = fv.strftime('%Y-%m-%d')
            elif fv is None:
                licencia['fecha_vencimiento'] = None

            if isinstance(ca, (datetime, date)):
                licencia['created_at'] = ca.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(ua, (datetime, date)):
                licencia['updated_at'] = ua.strftime('%Y-%m-%d %H:%M:%S')
            
            # Calcular estado automático basado en días restantes, tolerando NULL
            dias_restantes = licencia.get('dias_vencimiento')
            if dias_restantes is None:
                # Fallback: calcular desde fecha_vencimiento si está disponible
                if fv:
                    try:
                        fv_dt = fv if isinstance(fv, (datetime, date)) else datetime.strptime(fv, '%Y-%m-%d').date()
                        dias_restantes = (fv_dt - fecha_bogota).days
                    except Exception:
                        dias_restantes = 0
                else:
                    dias_restantes = 0

            licencia['dias_vencimiento'] = dias_restantes

            if dias_restantes < 0:
                licencia['estado_calculado'] = 'Vencido'
            elif dias_restantes <= 30:
                licencia['estado_calculado'] = 'Próximo a vencer'
            else:
                licencia['estado_calculado'] = 'Vigente'
        
        return jsonify({
            'success': True,
            'data': licencias
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para obtener una licencia de conducir específica
@app.route('/api/mpa/licencias-conducir/<int:licencia_id>', methods=['GET'])
@login_required
def api_get_licencia_conducir(licencia_id):
    """API para obtener una licencia de conducir específica"""
    allowed_roles = ('administrativo', 'sstt', 'tecnicos')
    if not any(current_user.has_role(r) for r in allowed_roles):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener fecha actual de Bogotá
        fecha_bogota = get_bogota_datetime().date()
        
        cursor.execute("SHOW TABLES LIKE 'mpa_licencia_conducir'")
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Licencia no encontrada'}), 404
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        ro_exists = cursor.fetchone() is not None

        select_cols = [
            "lc.id_mpa_licencia_conducir as id",
            "lc.tecnico as tecnico_id",
            "lc.tipo_licencia",
            "lc.fecha_inicio as fecha_inicial",
            "lc.fecha_vencimiento",
            "lc.observacion as observaciones",
            "lc.fecha_creacion as created_at",
            "lc.fecha_actualizacion as updated_at",
            "DATEDIFF(lc.fecha_vencimiento, %s) as dias_vencimiento"
        ]
        if ro_exists:
            select_cols.append("COALESCE(ro.nombre, lc.tecnico) as tecnico_nombre")
        else:
            select_cols.append("CAST(lc.tecnico AS CHAR) as tecnico_nombre")

        joins = []
        if ro_exists:
            joins.append("LEFT JOIN recurso_operativo ro ON lc.tecnico = ro.id_codigo_consumidor")

        query = f"""
        SELECT {', '.join(select_cols)}
        FROM mpa_licencia_conducir lc
        {' '.join(joins)}
        WHERE lc.id_mpa_licencia_conducir = %s
        """
        
        cursor.execute(query, (fecha_bogota, licencia_id))
        licencia = cursor.fetchone()
        
        if not licencia:
            return jsonify({'success': False, 'error': 'Licencia de conducir no encontrada'}), 404
        
        # Formatear fechas y calcular estado
        fi = licencia.get('fecha_inicial')
        fv = licencia.get('fecha_vencimiento')
        ca = licencia.get('created_at')
        ua = licencia.get('updated_at')

        if isinstance(fi, (datetime, date)):
            licencia['fecha_inicial'] = fi.strftime('%Y-%m-%d')
        elif fi is None:
            licencia['fecha_inicial'] = None

        if isinstance(fv, (datetime, date)):
            licencia['fecha_vencimiento'] = fv.strftime('%Y-%m-%d')
        elif fv is None:
            licencia['fecha_vencimiento'] = None

        if isinstance(ca, (datetime, date)):
            licencia['created_at'] = ca.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(ua, (datetime, date)):
            licencia['updated_at'] = ua.strftime('%Y-%m-%d %H:%M:%S')

        # Calcular estado automático basado en días restantes, tolerando NULL
        dias_restantes = licencia.get('dias_vencimiento')
        if dias_restantes is None:
            if fv:
                try:
                    fv_dt = fv if isinstance(fv, (datetime, date)) else datetime.strptime(fv, '%Y-%m-%d').date()
                    dias_restantes = (fv_dt - fecha_bogota).days
                except Exception:
                    dias_restantes = 0
            else:
                dias_restantes = 0

        licencia['dias_vencimiento'] = dias_restantes

        if dias_restantes < 0:
            licencia['estado_calculado'] = 'Vencido'
        elif dias_restantes <= 30:
            licencia['estado_calculado'] = 'Próximo a vencer'
        else:
            licencia['estado_calculado'] = 'Vigente'

        return jsonify({
            'success': True,
            'data': licencia
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para crear una nueva licencia de conducir
@app.route('/api/mpa/licencias-conducir', methods=['POST'])
@login_required
def api_create_licencia_conducir():
    """API para crear una nueva licencia de conducir"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['tecnico_id', 'tipo_licencia', 'fecha_inicial', 'fecha_vencimiento']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor()
        
        # Verificar que el técnico existe en recurso_operativo
        cursor.execute("SELECT id_codigo_consumidor, nombre FROM recurso_operativo WHERE id_codigo_consumidor = %s AND estado = 'Activo'", (data['tecnico_id'],))
        tecnico = cursor.fetchone()
        
        if not tecnico:
            return jsonify({'success': False, 'error': 'Técnico no encontrado o inactivo'}), 400
        
        # Verificar si ya existe una licencia activa para este técnico
        cursor.execute("""
            SELECT id_mpa_licencia_conducir FROM mpa_licencia_conducir 
            WHERE tecnico = %s AND fecha_vencimiento > CURDATE()
        """, (data['tecnico_id'],))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Ya existe una licencia vigente para este técnico'}), 400
        
        # Validar fechas
        from datetime import datetime
        try:
            fecha_inicial = datetime.strptime(data['fecha_inicial'], '%Y-%m-%d').date()
            fecha_vencimiento = datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d').date()
            
            if fecha_vencimiento <= fecha_inicial:
                return jsonify({'success': False, 'error': 'La fecha de vencimiento debe ser posterior a la fecha inicial'}), 400
                
        except ValueError:
            return jsonify({'success': False, 'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
        
        # Insertar nueva licencia de conducir
        query = """
        INSERT INTO mpa_licencia_conducir (
            tecnico, tipo_licencia, fecha_inicio, fecha_vencimiento, observacion, fecha_creacion
        ) VALUES (%s, %s, %s, %s, %s, NOW())
        """
        
        values = (
            data['tecnico_id'],
            data['tipo_licencia'],
            data['fecha_inicial'],
            data['fecha_vencimiento'],
            data.get('observaciones', '')
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        licencia_id = cursor.lastrowid
        
        return jsonify({
            'success': True,
            'message': 'Licencia de conducir creada exitosamente',
            'data': {'id': licencia_id}
        })
        
    except Exception as e:
        if 'connection' in locals() and connection:
            connection.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para actualizar una licencia de conducir
@app.route('/api/mpa/licencias-conducir/<int:licencia_id>', methods=['PUT'])
@login_required
def api_update_licencia_conducir(licencia_id):
    """API para actualizar una licencia de conducir existente"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        data = request.get_json()
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor()
        
        # Verificar que la licencia existe
        cursor.execute("SELECT id_mpa_licencia_conducir FROM mpa_licencia_conducir WHERE id_mpa_licencia_conducir = %s", (licencia_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Licencia de conducir no encontrada'}), 404
        
        # Validar fechas si se proporcionan
        if 'fecha_inicial' in data and 'fecha_vencimiento' in data:
            try:
                from datetime import datetime
                fecha_inicial = datetime.strptime(data['fecha_inicial'], '%Y-%m-%d').date()
                fecha_vencimiento = datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d').date()
                
                if fecha_vencimiento <= fecha_inicial:
                    return jsonify({'success': False, 'error': 'La fecha de vencimiento debe ser posterior a la fecha inicial'}), 400
                    
            except ValueError:
                return jsonify({'success': False, 'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
        
        # Construir query de actualización dinámicamente
        update_fields = []
        values = []
        
        allowed_fields = {
            'tecnico_id': 'tecnico',
            'tipo_licencia': 'tipo_licencia',
            'fecha_inicial': 'fecha_inicio', 
            'fecha_vencimiento': 'fecha_vencimiento',
            'observaciones': 'observacion'
        }
        
        for field, db_field in allowed_fields.items():
            if field in data:
                update_fields.append(f"{db_field} = %s")
                values.append(data[field])
        
        if not update_fields:
            return jsonify({'success': False, 'error': 'No hay campos para actualizar'}), 400
        
        # Agregar fecha de actualización
        update_fields.append("fecha_actualizacion = NOW()")
        values.append(licencia_id)
        
        query = f"UPDATE mpa_licencia_conducir SET {', '.join(update_fields)} WHERE id_mpa_licencia_conducir = %s"
        
        cursor.execute(query, values)
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Licencia de conducir actualizada exitosamente'
        })
        
    except Exception as e:
        if 'connection' in locals() and connection:
            connection.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

# API para eliminar una licencia de conducir
@app.route('/api/mpa/licencias-conducir/<int:licencia_id>', methods=['DELETE'])
@login_required
def api_delete_licencia_conducir(licencia_id):
    """API para eliminar una licencia de conducir"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor()
        
        # Verificar si la licencia existe
        cursor.execute("SELECT id_mpa_licencia_conducir FROM mpa_licencia_conducir WHERE id_mpa_licencia_conducir = %s", (licencia_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Licencia de conducir no encontrada'}), 404
        
        # Eliminar licencia de conducir
        cursor.execute("DELETE FROM mpa_licencia_conducir WHERE id_mpa_licencia_conducir = %s", (licencia_id,))
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Licencia de conducir eliminada exitosamente'
        })
        
    except Exception as e:
        if 'connection' in locals() and connection:
            connection.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/mpa/mantenimientos')
@login_required
def mpa_mantenimientos():
    """Módulo de gestión de mantenimientos"""
    if not current_user.has_role('administrativo'):
        flash('No tienes permisos para acceder a este módulo.', 'error')
        return redirect(url_for('mpa_dashboard'))
    
    return render_template('modulos/mpa/maintenance.html')

def ensure_cronograma_table():
    connection = get_db_connection()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cronograma_mantenimientos (
                id_cronograma INT AUTO_INCREMENT PRIMARY KEY,
                placa VARCHAR(20) NOT NULL,
                tecnico VARCHAR(255) NULL,
                fecha_mantenimiento DATETIME NULL,
                tipo_mantenimiento VARCHAR(100) DEFAULT 'Cambio de Aceite',
                kilometraje_actual INT NOT NULL,
                kilometraje_frecuencia INT DEFAULT 2500,
                kilometraje_promedio_diario INT DEFAULT 80,
                estado ENUM('Activo','Inactivo') DEFAULT 'Activo',
                fecha_proximo_mantenimiento DATETIME NULL,
                proximo_kilometraje INT NULL,
                observaciones TEXT NULL,
                cumplido TINYINT(1) DEFAULT 0,
                cumplido_fecha DATETIME NULL,
                cumplido_mantenimiento_id INT NULL,
                cumplido_observaciones TEXT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uq_cronograma_placa (placa)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        try:
            cursor.execute("ALTER TABLE cronograma_mantenimientos ADD COLUMN cumplido TINYINT(1) DEFAULT 0")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE cronograma_mantenimientos ADD COLUMN cumplido_fecha DATETIME NULL")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE cronograma_mantenimientos ADD COLUMN cumplido_mantenimiento_id INT NULL")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE cronograma_mantenimientos ADD COLUMN cumplido_observaciones TEXT NULL")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE cronograma_mantenimientos ADD COLUMN cumplido_tipo VARCHAR(64) NULL")
        except Exception:
            pass
        connection.commit()
        cursor.close()
        return True
    except Exception:
        try:
            connection.rollback()
        except Exception:
            pass
        return False
    finally:
        try:
            connection.close()
        except Exception:
            pass

def ensure_cronograma_historial_table():
    connection = get_db_connection()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cronograma_cumplimientos_historial (
                id INT AUTO_INCREMENT PRIMARY KEY,
                placa VARCHAR(20) NOT NULL,
                tipo_cumplido VARCHAR(64) NOT NULL,
                fecha DATETIME NOT NULL,
                kilometraje INT NOT NULL,
                mantenimiento_id INT NULL,
                observaciones TEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_placa (placa),
                INDEX idx_fecha (fecha),
                INDEX idx_tipo (tipo_cumplido)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        connection.commit()
        cursor.close()
        return True
    except Exception:
        try:
            connection.rollback()
        except Exception:
            pass
        return False
    finally:
        try:
            connection.close()
        except Exception:
            pass

@app.route('/mpa/cronograma')
@login_required
def mpa_cronograma():
    if not current_user.has_role('administrativo'):
        flash('No tienes permisos para acceder a este módulo.', 'error')
        return redirect(url_for('mpa_dashboard'))
    ensure_cronograma_table()
    return render_template('modulos/mpa/cronograma.html')

def _cronograma_tasks(base_km, ultimo_fecha, freq_aceite=2500, avg_per_day=80):
    import math
    from datetime import timedelta
    tasks = []
    niveles = [
        {
            'tipo': 'Cambio de Aceite',
            'frecuencia_km': freq_aceite,
            'detalles': ['Cambio de aceite', 'Inspección/limpieza del filtro de aceite', 'Cadena: limpieza, lubricación y ajuste', 'Frenos: inspección de nivel y pastillas/bandas']
        },
        {
            'tipo': 'Preventivo Completo',
            'frecuencia_km': 5000,
            'detalles': ['Filtro de aire: limpieza/reemplazo', 'Sistema de combustible: limpieza', 'Frenos: ajuste/cambio si >80% desgaste', 'Suspensión: revisión de fugas y estado', 'Tornillería: reapriete']
        },
        {
            'tipo': 'Mantenimiento Mayor',
            'frecuencia_km': 10000,
            'detalles': ['Ajuste de válvulas', 'Reemplazo de bujías', 'Filtro de aire (si aplica)', 'Líquido de frenos (1–2 años o según km)']
        }
    ]
    for niv in niveles:
        freq = int(niv['frecuencia_km'])
        # Calcular próximo km como múltiplo superior del base_km respecto a la frecuencia
        mod = base_km % freq
        proximo_km = (base_km + (freq - mod)) if mod != 0 else (base_km + freq)
        restantes = max(0, proximo_km - base_km)
        dias = math.ceil(restantes / max(1, int(avg_per_day)))
        fecha_tentativa = (ultimo_fecha + timedelta(days=dias)) if ultimo_fecha else None
        tasks.append({
            'tipo': niv['tipo'],
            'frecuencia_km': freq,
            'proximo_kilometraje': proximo_km,
            'kilometraje_restante': restantes,
            'alerta': restantes <= 200,
            'fecha_tentativa': (fecha_tentativa.strftime('%Y-%m-%d') if fecha_tentativa else None),
            'dias_estimados': dias,
            'detalles': niv['detalles']
        })
    return tasks

@app.route('/api/mpa/cronograma', methods=['GET', 'POST'])
@login_required
def api_cronograma_list_create():
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    ensure_cronograma_table()
    if request.method == 'GET':
        try:
            connection = get_db_connection()
            if not connection:
                return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
            cursor = connection.cursor(dictionary=True)
            placa = (request.args.get('placa') or '').strip().upper()
            sql = """
                SELECT c.*, v.tipo_vehiculo, ro.nombre AS tecnico_asignado
                FROM cronograma_mantenimientos c
                LEFT JOIN mpa_vehiculos v ON v.placa = c.placa
                LEFT JOIN recurso_operativo ro ON v.tecnico_asignado = ro.id_codigo_consumidor
                {where}
                ORDER BY c.fecha_actualizacion DESC
            """
            where = ""
            params = []
            if placa:
                where = "WHERE c.placa LIKE %s"
                params.append(f"%{placa}%")
            cursor.execute(sql.format(where=where), params)
            rows = cursor.fetchall()
            from datetime import datetime
            now = datetime.now()
            for r in rows:
                fm = r.get('fecha_mantenimiento')
                fp = r.get('fecha_proximo_mantenimiento')
                cf = r.get('cumplido_fecha')
                if fm:
                    r['fecha_mantenimiento'] = fm.strftime('%Y-%m-%d')
                if fp:
                    try:
                        dias = (fp.date() - now.date()).days
                    except Exception:
                        dias = None
                    r['dias_hasta_fecha'] = dias
                    r['vencido'] = (dias is not None and dias < 0)
                    r['fecha_proximo_mantenimiento'] = fp.strftime('%Y-%m-%d')
                if cf:
                    r['cumplido_fecha'] = cf.strftime('%Y-%m-%d')
            return jsonify({'success': True, 'data': rows})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            try:
                cursor.close(); connection.close()
            except Exception:
                pass
    else:
        try:
            data = request.get_json(silent=True) or {}
            placa = (data.get('placa') or '').strip().upper()
            if not placa:
                return jsonify({'success': False, 'message': 'placa es obligatoria'}), 400
            connection = get_db_connection()
            if not connection:
                return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT tipo_vehiculo, tecnico_asignado FROM mpa_vehiculos WHERE placa = %s", (placa,))
            v = cursor.fetchone()
            if not v:
                return jsonify({'success': False, 'message': 'Placa no existe'}), 404
            tecnico_nombre = None
            try:
                if v.get('tecnico_asignado'):
                    cursor.execute("SELECT nombre FROM recurso_operativo WHERE id_codigo_consumidor = %s", (v['tecnico_asignado'],))
                    rn = cursor.fetchone()
                    if rn and rn.get('nombre'): tecnico_nombre = rn['nombre']
            except Exception:
                pass
            from datetime import datetime
            fecha_mant = (data.get('fecha_mantenimiento') or '').strip()
            try:
                fecha_dt = datetime.strptime(fecha_mant, '%Y-%m-%d') if fecha_mant else datetime.now()
            except Exception:
                fecha_dt = datetime.now()
            km_actual = int(data.get('kilometraje_actual') or 0)
            km_freq = int(data.get('kilometraje_frecuencia') or 2500)
            km_avg = int(data.get('kilometraje_promedio_diario') or 80)
            # Calcular próximo mantenimiento tentativo y próximo km
            proximo_km = km_actual + km_freq
            from datetime import timedelta
            dias = max(0, int((km_freq) / max(1, km_avg)))
            fecha_prox = fecha_dt + timedelta(days=dias)
            # Upsert por placa
            cursor.execute("SELECT id_cronograma FROM cronograma_mantenimientos WHERE placa = %s", (placa,))
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    """
                    UPDATE cronograma_mantenimientos
                    SET tecnico = %s, fecha_mantenimiento = %s, tipo_mantenimiento = %s,
                        kilometraje_actual = %s, kilometraje_frecuencia = %s,
                        kilometraje_promedio_diario = %s, estado = %s,
                        fecha_proximo_mantenimiento = %s, proximo_kilometraje = %s,
                        observaciones = %s
                    WHERE placa = %s
                    """,
                    (
                        data.get('tecnico') or tecnico_nombre,
                        fecha_dt,
                        (data.get('tipo_mantenimiento') or 'Cambio de Aceite'),
                        km_actual, km_freq, km_avg,
                        (data.get('estado') or 'Activo'),
                        fecha_prox, proximo_km,
                        data.get('observaciones'),
                        placa,
                    )
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO cronograma_mantenimientos
                    (placa, tecnico, fecha_mantenimiento, tipo_mantenimiento,
                     kilometraje_actual, kilometraje_frecuencia, kilometraje_promedio_diario,
                     estado, fecha_proximo_mantenimiento, proximo_kilometraje, observaciones)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        placa,
                        data.get('tecnico') or tecnico_nombre,
                        fecha_dt,
                        (data.get('tipo_mantenimiento') or 'Cambio de Aceite'),
                        km_actual, km_freq, km_avg,
                        (data.get('estado') or 'Activo'),
                        fecha_prox, proximo_km,
                        data.get('observaciones'),
                    )
                )
            connection.commit()
            return jsonify({'success': True})
        except Exception as e:
            try:
                connection.rollback()
            except Exception:
                pass
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            try:
                cursor.close(); connection.close()
            except Exception:
                pass

@app.route('/api/mpa/cronograma/<placa>', methods=['GET'])
@login_required
def api_cronograma_detalle(placa):
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    ensure_cronograma_table()
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT c.*, v.tipo_vehiculo, ro.nombre AS tecnico_asignado
            FROM cronograma_mantenimientos c
            LEFT JOIN mpa_vehiculos v ON v.placa = c.placa
            LEFT JOIN recurso_operativo ro ON v.tecnico_asignado = ro.id_codigo_consumidor
            WHERE c.placa = %s
            """,
            (placa.upper(),)
        )
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Placa sin cronograma'}), 404
        from datetime import datetime
        ultimo_fecha = row.get('fecha_mantenimiento') or datetime.now()
        base_km = int(row.get('kilometraje_actual') or 0)
        avg = int(row.get('kilometraje_promedio_diario') or 80)
        freq_aceite = int(row.get('kilometraje_frecuencia') or 2500)
        tasks = _cronograma_tasks(base_km, ultimo_fecha, freq_aceite=freq_aceite, avg_per_day=avg)
        if row.get('fecha_mantenimiento'):
            row['fecha_mantenimiento'] = row['fecha_mantenimiento'].strftime('%Y-%m-%d')
        if row.get('fecha_proximo_mantenimiento'):
            row['fecha_proximo_mantenimiento'] = row['fecha_proximo_mantenimiento'].strftime('%Y-%m-%d')
        return jsonify({'success': True, 'cronograma': row, 'tareas': tasks})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        try:
            cursor.close(); connection.close()
        except Exception:
            pass

@app.route('/api/mpa/cronograma/<placa>/cumplir', methods=['POST'])
@login_required
def api_cronograma_cumplir(placa):
    role = session.get('user_role') or getattr(current_user, 'role', None)
    if role not in ['operativo', 'administrativo', 'tecnicos']:
        return jsonify({'error': 'Sin permisos'}), 403
    ensure_cronograma_table()
    try:
        data = request.get_json(silent=True) or {}
        km_real = int(data.get('kilometraje_real') or 0)
        fecha_real = (data.get('fecha_real') or '').strip()
        obs = (data.get('observaciones') or '').strip()
        tipo_cumplido = (data.get('tipo_cumplido') or 'Cambio de Aceite').strip()
        mant_id = data.get('mantenimiento_id')
        try:
            mant_id = int(mant_id) if mant_id is not None and str(mant_id).isdigit() else None
        except Exception:
            mant_id = None
        from datetime import datetime, timedelta
        try:
            fecha_dt = datetime.strptime(fecha_real, '%Y-%m-%d') if fecha_real else datetime.now()
        except Exception:
            fecha_dt = datetime.now()
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        ensure_cronograma_historial_table()
        cursor.execute("SELECT kilometraje_frecuencia, kilometraje_promedio_diario FROM cronograma_mantenimientos WHERE placa = %s", (placa.upper(),))
        row = cursor.fetchone()
        if mant_id is None:
            try:
                cursor2 = connection.cursor()
                cursor2.execute("SELECT id_mpa_mantenimientos FROM mpa_mantenimientos WHERE placa = %s ORDER BY fecha_mantenimiento DESC LIMIT 1", (placa.upper(),))
                r2 = cursor2.fetchone()
                if r2:
                    try:
                        mant_id = int(r2[0])
                    except Exception:
                        mant_id = r2[0]
                cursor2.close()
            except Exception:
                pass
        km_freq = int((row or {}).get('kilometraje_frecuencia') or 2500)
        km_avg = int((row or {}).get('kilometraje_promedio_diario') or 80)
        proximo_km = km_real + km_freq
        dias = max(0, int(km_freq / max(1, km_avg)))
        fecha_prox = fecha_dt + timedelta(days=dias)
        if row:
            cursor.execute(
                """
                UPDATE cronograma_mantenimientos
                SET fecha_mantenimiento = %s,
                    kilometraje_actual = %s,
                    fecha_proximo_mantenimiento = %s,
                    proximo_kilometraje = %s,
                    cumplido = 1,
                    cumplido_fecha = %s,
                    cumplido_mantenimiento_id = %s,
                    cumplido_observaciones = %s,
                    cumplido_tipo = %s
                WHERE placa = %s
                """,
                (fecha_dt, km_real, fecha_prox, proximo_km, fecha_dt, mant_id, obs, tipo_cumplido, placa.upper())
            )
        else:
            cursor.execute(
                """
                INSERT INTO cronograma_mantenimientos
                (placa, fecha_mantenimiento, tipo_mantenimiento,
                 kilometraje_actual, kilometraje_frecuencia, kilometraje_promedio_diario,
                 estado, fecha_proximo_mantenimiento, proximo_kilometraje,
                 observaciones, cumplido, cumplido_fecha, cumplido_mantenimiento_id, cumplido_observaciones, cumplido_tipo)
                VALUES (%s, %s, %s, %s, %s, %s, 'Activo', %s, %s, %s, 1, %s, %s, %s, %s)
                """,
                (placa.upper(), fecha_dt, 'Cambio de Aceite', km_real, km_freq, km_avg, fecha_prox, proximo_km, obs, fecha_dt, mant_id, obs, tipo_cumplido)
            )
        try:
            cursor.execute(
                """
                INSERT INTO cronograma_cumplimientos_historial
                (placa, tipo_cumplido, fecha, kilometraje, mantenimiento_id, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (placa.upper(), tipo_cumplido, fecha_dt, km_real, mant_id, obs)
            )
        except Exception:
            pass
        connection.commit()
        return jsonify({'success': True})
    except Exception as e:
        try:
            connection.rollback()
        except Exception:
            pass
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        try:
            cursor.close(); connection.close()
        except Exception:
            pass

@app.route('/api/mpa/cronograma/<placa>/historial', methods=['GET'])
@login_required
def api_cronograma_historial(placa):
    role = session.get('user_role') or getattr(current_user, 'role', None)
    if role not in ['operativo', 'administrativo', 'tecnicos']:
        return jsonify({'error': 'Sin permisos'}), 403
    ensure_cronograma_historial_table()
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT placa, tipo_cumplido, fecha, kilometraje, mantenimiento_id, observaciones
            FROM cronograma_cumplimientos_historial
            WHERE placa = %s
            ORDER BY fecha DESC
            """,
            (placa.upper(),)
        )
        rows = cursor.fetchall()
        for r in rows:
            try:
                if r.get('fecha'):
                    r['fecha'] = r['fecha'].strftime('%Y-%m-%d')
            except Exception:
                pass
        return jsonify({'success': True, 'data': rows})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        try:
            cursor.close(); connection.close()
        except Exception:
            pass

@app.route('/api/mpa/cronograma/indicadores', methods=['GET'])
@login_required
def api_cronograma_indicadores():
    role = session.get('user_role') or getattr(current_user, 'role', None)
    if role not in ['administrativo']:
        return jsonify({'error': 'Sin permisos'}), 403
    ensure_cronograma_table()
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        from datetime import datetime
        now = get_bogota_datetime()
        per = (request.args.get('period') or 'mensual').strip().lower()
        placa = (request.args.get('placa') or '').strip().upper()
        try:
            year = int(request.args.get('year') or now.year)
        except Exception:
            year = now.year
        params_s = [year]
        where_s = "WHERE c.fecha_proximo_mantenimiento IS NOT NULL AND YEAR(c.fecha_proximo_mantenimiento) = %s"
        if placa:
            where_s += " AND UPPER(TRIM(c.placa)) = %s"
            params_s.append(placa)
        cursor.execute(
            f"""
            SELECT c.placa, c.fecha_proximo_mantenimiento
            FROM cronograma_mantenimientos c
            LEFT JOIN mpa_vehiculos v ON v.placa = c.placa
            LEFT JOIN recurso_operativo ro ON v.tecnico_asignado = ro.id_codigo_consumidor
            {where_s} AND ro.estado = 'Activo'
            """,
            tuple(params_s)
        )
        sched_rows = cursor.fetchall() or []
        params_m = [year]
        where_m = "WHERE m.fecha_mantenimiento IS NOT NULL AND YEAR(m.fecha_mantenimiento) = %s"
        if placa:
            where_m += " AND UPPER(TRIM(m.placa)) = %s"
            params_m.append(placa)
        cursor.execute(
            f"""
            SELECT m.placa, m.fecha_mantenimiento
            FROM mpa_mantenimientos m
            LEFT JOIN mpa_vehiculos v ON v.placa = m.placa
            LEFT JOIN recurso_operativo ro ON v.tecnico_asignado = ro.id_codigo_consumidor
            {where_m} AND ro.estado = 'Activo'
            """,
            tuple(params_m)
        )
        mant_rows = cursor.fetchall() or []
        mant_set = set()
        for r in mant_rows:
            try:
                dt = r.get('fecha_mantenimiento')
                if dt:
                    mant_set.add((str(r.get('placa') or '').strip().upper(), dt.month))
            except Exception:
                pass
        m_prog = {i: 0 for i in range(1, 13)}
        m_comp = {i: 0 for i in range(1, 13)}
        for r in sched_rows:
            try:
                dt = r.get('fecha_proximo_mantenimiento')
                if dt and dt.year == year:
                    m = dt.month
                    m_prog[m] = m_prog.get(m, 0) + 1
                    key = (str(r.get('placa') or '').strip().upper(), m)
                    if key in mant_set:
                        m_comp[m] = m_comp.get(m, 0) + 1
            except Exception:
                pass
        meses_series = []
        total_prog = 0
        total_comp = 0
        for m in range(1, 13):
            p = int(m_prog.get(m, 0) or 0)
            c = int(m_comp.get(m, 0) or 0)
            total_prog += p
            total_comp += c
            pct = (c * 100.0 / p) if p > 0 else None
            meses_series.append({'mes': m, 'programados': p, 'cumplen_en_mes': c, 'cumplimiento': pct})
        q_map = {1: 'Q1', 2: 'Q1', 3: 'Q1', 4: 'Q2', 5: 'Q2', 6: 'Q2', 7: 'Q3', 8: 'Q3', 9: 'Q3', 10: 'Q4', 11: 'Q4', 12: 'Q4'}
        q_prog = {'Q1': 0, 'Q2': 0, 'Q3': 0, 'Q4': 0}
        q_comp = {'Q1': 0, 'Q2': 0, 'Q3': 0, 'Q4': 0}
        for m in range(1, 13):
            q = q_map[m]
            q_prog[q] += int(m_prog.get(m, 0) or 0)
            q_comp[q] += int(m_comp.get(m, 0) or 0)
        trimestral_series = []
        for q in ['Q1', 'Q2', 'Q3', 'Q4']:
            p = q_prog[q]
            c = q_comp[q]
            pct = (c * 100.0 / p) if p > 0 else None
            trimestral_series.append({'trimestre': q, 'programados': p, 'cumplen_en_mes': c, 'cumplimiento': pct})
        anual_resumen = {
            'programados_total': total_prog,
            'cumplen_en_mes_total': total_comp,
            'cumplimiento': (total_comp * 100.0 / total_prog) if total_prog > 0 else None,
            'anio': year
        }
        data = {
            'mensual': {'series': meses_series, 'resumen': anual_resumen},
            'trimestral': {'series': trimestral_series, 'resumen': anual_resumen},
            'anual': {'resumen': anual_resumen}
        }
        if per == 'mensual':
            res = {'success': True, 'data': data['mensual']}
        elif per == 'trimestral':
            res = {'success': True, 'data': data['trimestral']}
        elif per == 'anual':
            res = {'success': True, 'data': data['anual']}
        else:
            res = {'success': True, 'data': data}
        return jsonify(res)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        try:
            cursor.close(); connection.close()
        except Exception:
            pass

@app.route('/api/mpa/cronograma/indicadores/detalle', methods=['GET'])
@login_required
def api_cronograma_indicadores_detalle():
    role = session.get('user_role') or getattr(current_user, 'role', None)
    if role not in ['administrativo']:
        return jsonify({'error': 'Sin permisos'}), 403
    ensure_cronograma_table()
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        from datetime import datetime
        now = get_bogota_datetime()
        try:
            year = int(request.args.get('year') or now.year)
        except Exception:
            year = now.year
        try:
            month = int(request.args.get('month') or now.month)
        except Exception:
            month = now.month
        placa = (request.args.get('placa') or '').strip().upper()
        params_s = [year, month]
        where_s = "WHERE c.fecha_proximo_mantenimiento IS NOT NULL AND YEAR(c.fecha_proximo_mantenimiento) = %s AND MONTH(c.fecha_proximo_mantenimiento) = %s"
        if placa:
            where_s += " AND UPPER(TRIM(c.placa)) = %s"
            params_s.append(placa)
        cursor.execute(
            f"""
            SELECT c.placa, c.fecha_proximo_mantenimiento,
                   v.tipo_vehiculo,
                   ro.id_codigo_consumidor AS tecnico_id,
                   ro.nombre AS tecnico_nombre
            FROM cronograma_mantenimientos c
            LEFT JOIN mpa_vehiculos v ON v.placa = c.placa
            LEFT JOIN recurso_operativo ro ON v.tecnico_asignado = ro.id_codigo_consumidor
            {where_s} AND ro.estado = 'Activo'
            ORDER BY c.fecha_proximo_mantenimiento ASC, c.placa
            """,
            tuple(params_s)
        )
        sched_rows = cursor.fetchall() or []
        params_m = [year, month]
        where_m = "WHERE m.fecha_mantenimiento IS NOT NULL AND YEAR(m.fecha_mantenimiento) = %s AND MONTH(m.fecha_mantenimiento) = %s"
        if placa:
            where_m += " AND UPPER(TRIM(m.placa)) = %s"
            params_m.append(placa)
        cursor.execute(
            f"""
            SELECT m.placa, m.fecha_mantenimiento
            FROM mpa_mantenimientos m
            LEFT JOIN mpa_vehiculos v ON v.placa = m.placa
            LEFT JOIN recurso_operativo ro ON v.tecnico_asignado = ro.id_codigo_consumidor
            {where_m} AND ro.estado = 'Activo'
            """,
            tuple(params_m)
        )
        mant_rows = cursor.fetchall() or []
        mant_map = {}
        for r in mant_rows:
            p = (r.get('placa') or '').strip().upper()
            dt = r.get('fecha_mantenimiento')
            if not p or not dt:
                continue
            mant_map.setdefault(p, []).append(dt)
        detalle = []
        for r in sched_rows:
            p = (r.get('placa') or '').strip().upper()
            fp = r.get('fecha_proximo_mantenimiento')
            realizado = False
            realizado_fecha = None
            if p in mant_map:
                try:
                    # Elegir la primera fecha de mantenimiento del mes
                    fechas = [d for d in mant_map[p] if d and d.year == year and d.month == month]
                except Exception:
                    fechas = mant_map[p]
                if fechas:
                    realizado = True
                    try:
                        realizado_fecha = fechas[0].strftime('%Y-%m-%d')
                    except Exception:
                        realizado_fecha = None
            item = {
                'placa': p,
                'tecnico_id': r.get('tecnico_id'),
                'tecnico_nombre': r.get('tecnico_nombre'),
                'tipo_vehiculo': r.get('tipo_vehiculo'),
                'programado_fecha': (fp.strftime('%Y-%m-%d') if fp else None),
                'realizado_en_mes': bool(realizado),
                'realizado_fecha': realizado_fecha,
                'estado': 'OK' if realizado else 'Pendiente'
            }
            detalle.append(item)
        total_prog = len(sched_rows)
        total_ok = sum(1 for d in detalle if d.get('realizado_en_mes'))
        resumen = {
            'anio': year,
            'mes': month,
            'programados': total_prog,
            'realizados_en_mes': total_ok,
            'cumplimiento': (total_ok * 100.0 / total_prog) if total_prog > 0 else None
        }
        return jsonify({'success': True, 'data': {'detalle': detalle, 'resumen': resumen}})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        try:
            cursor.close(); connection.close()
        except Exception:
            pass

@app.route('/api/mpa/cronograma/indicadores/detalle-trimestre', methods=['GET'])
@login_required
def api_cronograma_indicadores_detalle_trimestre():
    role = session.get('user_role') or getattr(current_user, 'role', None)
    if role not in ['administrativo']:
        return jsonify({'error': 'Sin permisos'}), 403
    ensure_cronograma_table()
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        from datetime import datetime
        now = get_bogota_datetime()
        try:
            year = int(request.args.get('year') or now.year)
        except Exception:
            year = now.year
        q = (request.args.get('q') or '').strip().upper()
        q_map = {
            'Q1': (1, 2, 3),
            'Q2': (4, 5, 6),
            'Q3': (7, 8, 9),
            'Q4': (10, 11, 12)
        }
        months = q_map.get(q)
        if not months:
            try:
                m = int(request.args.get('month') or now.month)
            except Exception:
                m = now.month
            if m in (1, 2, 3):
                months = (1, 2, 3); q = 'Q1'
            elif m in (4, 5, 6):
                months = (4, 5, 6); q = 'Q2'
            elif m in (7, 8, 9):
                months = (7, 8, 9); q = 'Q3'
            else:
                months = (10, 11, 12); q = 'Q4'
        placa = (request.args.get('placa') or '').strip().upper()
        params_s = [year, months[0], months[1], months[2]]
        where_s = "WHERE c.fecha_proximo_mantenimiento IS NOT NULL AND YEAR(c.fecha_proximo_mantenimiento) = %s AND MONTH(c.fecha_proximo_mantenimiento) IN (%s,%s,%s)"
        if placa:
            where_s += " AND UPPER(TRIM(c.placa)) = %s"
            params_s.append(placa)
        cursor.execute(
            f"""
            SELECT c.placa, c.fecha_proximo_mantenimiento,
                   v.tipo_vehiculo,
                   ro.id_codigo_consumidor AS tecnico_id,
                   ro.nombre AS tecnico_nombre
            FROM cronograma_mantenimientos c
            LEFT JOIN mpa_vehiculos v ON v.placa = c.placa
            LEFT JOIN recurso_operativo ro ON v.tecnico_asignado = ro.id_codigo_consumidor
            {where_s} AND ro.estado = 'Activo'
            ORDER BY c.fecha_proximo_mantenimiento ASC, c.placa
            """,
            tuple(params_s)
        )
        sched_rows = cursor.fetchall() or []
        params_m = [year, months[0], months[1], months[2]]
        where_m = "WHERE m.fecha_mantenimiento IS NOT NULL AND YEAR(m.fecha_mantenimiento) = %s AND MONTH(m.fecha_mantenimiento) IN (%s,%s,%s)"
        if placa:
            where_m += " AND UPPER(TRIM(m.placa)) = %s"
            params_m.append(placa)
        cursor.execute(
            f"""
            SELECT m.placa, m.fecha_mantenimiento
            FROM mpa_mantenimientos m
            LEFT JOIN mpa_vehiculos v ON v.placa = m.placa
            LEFT JOIN recurso_operativo ro ON v.tecnico_asignado = ro.id_codigo_consumidor
            {where_m} AND ro.estado = 'Activo'
            """,
            tuple(params_m)
        )
        mant_rows = cursor.fetchall() or []
        mant_map = {}
        for r in mant_rows:
            p = (r.get('placa') or '').strip().upper()
            dt = r.get('fecha_mantenimiento')
            if not p or not dt:
                continue
            mant_map.setdefault(p, []).append(dt)
        detalle = []
        for r in sched_rows:
            p = (r.get('placa') or '').strip().upper()
            fp = r.get('fecha_proximo_mantenimiento')
            programado_mes = fp.month if fp else None
            realizado = False
            realizado_fecha = None
            if p in mant_map:
                try:
                    fechas = [d for d in mant_map[p] if d and d.year == year and d.month in months]
                except Exception:
                    fechas = mant_map[p]
                if fechas:
                    realizado = True
                    try:
                        realizado_fecha = fechas[0].strftime('%Y-%m-%d')
                    except Exception:
                        realizado_fecha = None
            item = {
                'placa': p,
                'tecnico_id': r.get('tecnico_id'),
                'tecnico_nombre': r.get('tecnico_nombre'),
                'tipo_vehiculo': r.get('tipo_vehiculo'),
                'programado_mes': programado_mes,
                'programado_fecha': (fp.strftime('%Y-%m-%d') if fp else None),
                'realizado_en_trimestre': bool(realizado),
                'realizado_fecha': realizado_fecha,
                'estado': 'OK' if realizado else 'Pendiente'
            }
            detalle.append(item)
        total_prog = len(sched_rows)
        total_ok = sum(1 for d in detalle if d.get('realizado_en_trimestre'))
        resumen = {
            'anio': year,
            'trimestre': q,
            'programados': total_prog,
            'realizados_en_trimestre': total_ok,
            'cumplimiento': (total_ok * 100.0 / total_prog) if total_prog > 0 else None
        }
        return jsonify({'success': True, 'data': {'detalle': detalle, 'resumen': resumen}})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        try:
            cursor.close(); connection.close()
        except Exception:
            pass

@app.route('/api/mpa/cronograma/alerts-my', methods=['GET'])
@login_required
def api_cronograma_alerts_my():
    role = session.get('user_role') or getattr(current_user, 'role', None)
    if role not in ['operativo', 'administrativo', 'tecnicos']:
        return jsonify({'error': 'Sin permisos'}), 403
    ensure_cronograma_table()
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        uid = str(getattr(current_user, 'id', session.get('id_codigo_consumidor') or '0')).strip()
        cursor.execute(
            """
            SELECT c.placa, c.kilometraje_actual, c.proximo_kilometraje,
                   c.fecha_proximo_mantenimiento, c.estado, c.kilometraje_promedio_diario
            FROM cronograma_mantenimientos c
            INNER JOIN mpa_vehiculos v ON v.placa = c.placa
            WHERE CAST(TRIM(v.tecnico_asignado) AS UNSIGNED) = CAST(%s AS UNSIGNED)
              AND (c.estado = 'Activo')
            ORDER BY c.fecha_proximo_mantenimiento ASC
            """,
            (uid,)
        )
        rows = cursor.fetchall()
        res = []
        for r in rows:
            try:
                restante = int(r.get('proximo_kilometraje') or 0) - int(r.get('kilometraje_actual') or 0)
            except Exception:
                restante = 0
            try:
                km_avg = int(r.get('kilometraje_promedio_diario') or 80)
            except Exception:
                km_avg = 80
            try:
                import math
                dias = math.ceil(max(0, restante) / max(1, km_avg))
            except Exception:
                dias = None
            item = {
                'placa': r.get('placa'),
                'kilometraje_actual': r.get('kilometraje_actual'),
                'proximo_kilometraje': r.get('proximo_kilometraje'),
                'restante': max(-999999, restante),
                'alerta': restante <= 200,
                'estado': r.get('estado'),
                'fecha_proximo_mantenimiento': (r.get('fecha_proximo_mantenimiento').strftime('%Y-%m-%d') if r.get('fecha_proximo_mantenimiento') else None),
                'kilometraje_promedio_diario': km_avg,
                'dias_estimados_restantes': dias
            }
            res.append(item)
        return jsonify({'success': True, 'data': res})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        try:
            cursor.close(); connection.close()
        except Exception:
            pass


class Asignacion(db.Model):
    id_asignacion = db.Column(db.Integer, primary_key=True)
    id_codigo_consumidor = db.Column(db.String(50))
    fecha = db.Column(db.DateTime)
    cargo = db.Column(db.String(100))
    asignacion_firma = db.Column(db.Text)
    id_asignador = db.Column(db.Integer)

# ===== Submódulo Operativo: Equipos Disponibles =====
@app.route('/operativo/equipos_disponibles')
@login_required
def operativo_equipos_disponibles():
    """Renderiza la vista de equipos disponibles para el supervisor logueado"""
    try:
        connection = get_db_connection()
        if connection is None:
            flash('Error de conexión a la base de datos', 'error')
            return redirect(url_for('verificar_registro_preoperacional'))
        cursor = connection.cursor(dictionary=True)
        # Verificar asistencia del día
        today = date.today().strftime('%Y-%m-%d')
        cursor.execute(
            """
            SELECT COUNT(*) as total
            FROM asistencia
            WHERE DATE(fecha_asistencia) = %s
              AND (id_codigo_consumidor = %s OR cedula = %s)
            """,
            (today, session.get('id_codigo_consumidor'), session.get('user_cedula'))
        )
        row = cursor.fetchone()
        tiene_asistencia = (row.get('total', 0) if isinstance(row, dict) else (row[0] if row else 0)) > 0
        cursor.close()
        if connection.is_connected():
            connection.close()
        return render_template(
            'modulos/operativo/equipos_disponibles.html',
            user_name=session.get('user_name', ''),
            user_role=session.get('user_role', ''),
            tiene_asistencia=tiene_asistencia,
            api_equipos_url='/api/equipos_disponibles'
        )
    except Exception as e:
        print(f"Error en operativo_equipos_disponibles: {e}")
        flash('Error al cargar la página de equipos disponibles', 'error')
        return redirect(url_for('verificar_registro_preoperacional'))

# Vista pública de previsualización (sin login) para validar UI
@app.route('/operativo/equipos_disponibles_preview')
def operativo_equipos_disponibles_preview():
    try:
        # No validar asistencia para preview; solo renderizar la vista con API pública
        return render_template(
            'modulos/operativo/equipos_disponibles.html',
            user_name=session.get('user_name', 'Preview'),
            user_role=session.get('user_role', ''),
            tiene_asistencia=True,
            api_equipos_url='/api/equipos_disponibles_public'
        )
    except Exception as e:
        print(f"Error en operativo_equipos_disponibles_preview: {e}")
        return render_template('modulos/operativo/equipos_disponibles.html', api_equipos_url='/api/equipos_disponibles_public')

@app.route('/api/current_user', methods=['GET'])
@login_required
def api_current_user_operativo():
    """Devuelve información del usuario actual para el frontend"""
    try:
        return jsonify({
            'nombre': session.get('user_name', ''),
            'role': session.get('user_role', ''),
            'id_codigo_consumidor': session.get('id_codigo_consumidor', 0),
            'cedula': session.get('user_cedula', '')
        })
    except Exception as e:
        return jsonify({'error': f'Error obteniendo usuario: {str(e)}'}), 500

# Endpoint público con datos simulados para previsualización
@app.route('/api/equipos_disponibles_public', methods=['GET'])
def api_equipos_disponibles_public():
    try:
        demo = [
            {
                'tecnico': 'DEMO 1', 'familia': 'ONT', 'elemento': 'MODEM', 'serial': 'DEM001',
                'fecha_ultimo_movimiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'dias_ultimo': 3, 'cuenta': '', 'ot': '', 'observacion': ''
            },
            {
                'tecnico': 'DEMO 2', 'familia': 'ROUTER', 'elemento': 'CPE', 'serial': 'DEM002',
                'fecha_ultimo_movimiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'dias_ultimo': 12, 'cuenta': 'AC-123', 'ot': 'OT-567', 'observacion': 'Equipo revisado'
            }
        ]
        return jsonify({'equipos': demo})
    except Exception as e:
        return jsonify({'error': 'Error datos demo', 'message': str(e)}), 500

@app.route('/api/equipos_disponibles', methods=['GET'])
@login_required
def api_equipos_disponibles_operativo():
    """Lista equipos disponibles del supervisor logueado.
    - Serializa fechas/decimales para evitar HTTP 500
    - Soporta filtros opcionales y ordenamiento en memoria
    """
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        supervisor = session.get('user_name', '')
        try:
            cursor.execute(
                """
                SELECT 
                    cedula,
                    codigo_tercero,
                    elemento,
                    familia,
                    serial,
                    estado,
                    fecha_ultimo_movimiento,
                    dias_ultimo,
                    tecnico,
                    super,
                    cuenta,
                    ot,
                    observacion,
                    fecha_creacion
                FROM disponibilidad_equipos
                WHERE super = %s
                ORDER BY tecnico, familia, elemento
                """,
                (supervisor,)
            )
        except mysql.connector.Error as err:
            # Fallback si falta alguna columna (p.ej. fecha_ultimo_movimiento o dias_ultimo)
            if getattr(err, 'errno', None) == 1054:
                cursor.execute(
                    """
                    SELECT 
                        id_disponibilidad_equipos AS id,
                        cedula,
                        codigo_tercero,
                        elemento,
                        familia,
                        serial,
                        estado,
                        NULL AS fecha_ultimo_movimiento,
                        DATEDIFF(NOW(), fecha_creacion) AS dias_ultimo,
                        tecnico,
                        super,
                        cuenta,
                        ot,
                        observacion,
                        fecha_creacion
                    FROM disponibilidad_equipos
                    WHERE super = %s
                    ORDER BY tecnico, familia, elemento
                    """,
                    (supervisor,)
                )
            else:
                raise
        equipos = cursor.fetchall() or []
        cursor.close()
        if connection.is_connected():
            connection.close()
        # Normalizar tipos para JSON
        from decimal import Decimal
        def _norm(v):
            if isinstance(v, datetime):
                return v.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(v, date):
                return v.strftime('%Y-%m-%d')
            if isinstance(v, Decimal):
                try:
                    return float(v)
                except Exception:
                    return str(v)
            return v
        equipos = [{k: _norm(v) for k, v in row.items()} for row in equipos]
        # Filtros opcionales
        filtro_tecnico = (request.args.get('tecnico') or '').strip()
        filtro_familia = (request.args.get('familia') or '').strip()
        filtro_elemento = (request.args.get('elemento') or '').strip()
        q = (request.args.get('q') or '').strip().lower()
        def _pasa(e):
            if filtro_tecnico and e.get('tecnico') != filtro_tecnico:
                return False
            if filtro_familia and e.get('familia') != filtro_familia:
                return False
            if filtro_elemento and e.get('elemento') != filtro_elemento:
                return False
            if q:
                s = (e.get('serial') or '').lower()
                el = (e.get('elemento') or '').lower()
                if q not in s and q not in el:
                    return False
            return True
        equipos = list(filter(_pasa, equipos))
        # Ordenamiento opcional
        sort_by = (request.args.get('sort_by') or '').strip()
        sort_dir = (request.args.get('sort_dir') or 'asc').lower()
        allowed = {'tecnico','familia','elemento','serial','dias_ultimo','estado','cuenta','ot'}
        if sort_by in allowed:
            reverse = sort_dir == 'desc'
            def sort_key(e):
                v = e.get(sort_by)
                if sort_by == 'dias_ultimo':
                    try:
                        return int(v) if v is not None else -1
                    except:
                        return -1
                return (v or '')
            equipos = sorted(equipos, key=sort_key, reverse=reverse)
        return jsonify(equipos)
    except Exception as e:
        print(f"Error en api_equipos_disponibles_operativo: {e}")
        return jsonify({'error': 'Error al obtener equipos disponibles', 'message': str(e)}), 500

@app.route('/api/equipos_disponibles/export', methods=['GET'])
@login_required
def api_export_equipos_disponibles():
    """Exporta equipos disponibles a CSV (Excel-compatible) con filtros opcionales."""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        supervisor = session.get('user_name', '')
        try:
            cursor.execute(
                """
                SELECT 
                    tecnico,
                    familia,
                    elemento,
                    serial,
                    fecha_ultimo_movimiento,
                    dias_ultimo,
                    cuenta,
                    ot,
                    observacion,
                    fecha_creacion
                FROM disponibilidad_equipos
                WHERE super = %s AND (estado IS NULL OR estado = 'Activo')
                ORDER BY tecnico, familia, elemento
                """,
                (supervisor,)
            )
        except mysql.connector.Error as err:
            if getattr(err, 'errno', None) == 1054:
                cursor.execute(
                    """
                    SELECT 
                        tecnico,
                        familia,
                        elemento,
                        serial,
                        NULL AS fecha_ultimo_movimiento,
                        DATEDIFF(NOW(), fecha_creacion) AS dias_ultimo,
                        cuenta,
                        ot,
                        observacion,
                        fecha_creacion
                    FROM disponibilidad_equipos
                    WHERE super = %s AND (estado IS NULL OR estado = 'Activo')
                    ORDER BY tecnico, familia, elemento
                    """,
                    (supervisor,)
                )
            else:
                raise
        equipos = cursor.fetchall() or []
        cursor.close()
        if connection.is_connected():
            connection.close()
        # Aplicar filtros de query params
        filtro_tecnico = (request.args.get('tecnico') or '').strip()
        filtro_familia = (request.args.get('familia') or '').strip()
        filtro_elemento = (request.args.get('elemento') or '').strip()
        q = (request.args.get('q') or '').strip().lower()
        def _pasa(e):
            if filtro_tecnico and e.get('tecnico') != filtro_tecnico:
                return False
            if filtro_familia and e.get('familia') != filtro_familia:
                return False
            if filtro_elemento and e.get('elemento') != filtro_elemento:
                return False
            if q:
                s = (e.get('serial') or '').lower()
                el = (e.get('elemento') or '').lower()
                if q not in s and q not in el:
                    return False
            return True
        equipos = list(filter(_pasa, equipos))
        # Construir CSV
        from decimal import Decimal
        def fmt_fecha(v):
            if isinstance(v, datetime):
                return v.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(v, date):
                return v.strftime('%Y-%m-%d')
            return v or ''
        def fmt_num(v):
            if isinstance(v, Decimal):
                try:
                    return float(v)
                except Exception:
                    return str(v)
            return v
        headers = ['Tecnico','Familia','Elemento','Serial','FechaUltimoMovimiento','Dias','Cuenta','OT','Observacion']
        rows = []
        for e in equipos:
            rows.append([
                e.get('tecnico',''),
                e.get('familia',''),
                e.get('elemento',''),
                e.get('serial',''),
                fmt_fecha(e.get('fecha_ultimo_movimiento')),
                fmt_num(e.get('dias_ultimo')) if e.get('dias_ultimo') is not None else '',
                e.get('cuenta',''),
                e.get('ot',''),
                e.get('observacion','')
            ])
        def escape_csv(val):
            s = str(val).replace('"','""')
            return f'"{s}"'
        lines = [','.join(headers)] + [','.join(escape_csv(v) for v in row) for row in rows]
        csv_data = '\n'.join(lines)
        from flask import Response
        resp = Response(csv_data, mimetype='text/csv')
        resp.headers['Content-Disposition'] = 'attachment; filename="equipos_disponibles.csv"'
        return resp
    except Exception as e:
        print(f"Error en api_export_equipos_disponibles: {e}")
        return jsonify({'error': 'Error al exportar datos', 'message': str(e)}), 500

@app.route('/api/actualizar_equipo', methods=['POST'])
@login_required
def api_actualizar_equipo_operativo():
    """Actualiza cuenta, OT u observación de un equipo por serial.
    - Permite guardar si al menos uno de los 3 campos viene con dato
    - Bloquea cada campo individualmente una vez tiene valor (no se sobreescribe)
    """
    try:
        data = request.get_json(force=True) or {}
        serial = (data.get('serial') or '').strip()
        cuenta_in = (data.get('cuenta') or '').strip()
        ot_in = (data.get('ot') or '').strip()
        observ_in = (data.get('observacion') or '').strip()
        if not serial:
            return jsonify({'message': 'Serial del equipo es requerido'}), 400
        if not (cuenta_in or ot_in or observ_in):
            return jsonify({'message': 'Debe suministrar al menos cuenta, OT u observación'}), 400
        print(f"[actualizar_equipo] payload serial={serial} cuenta='{cuenta_in}' ot='{ot_in}' observacion='{observ_in}'")
        connection = get_db_connection()
        if connection is None:
            return jsonify({'message': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)
        supervisor = session.get('user_name', '')
        # Validar que el equipo pertenece al supervisor y obtener valores actuales
        cursor.execute(
            """
            SELECT cuenta, ot, observacion
            FROM disponibilidad_equipos
            WHERE serial = %s AND super = %s
            LIMIT 1
            """,
            (serial, supervisor)
        )
        current = cursor.fetchone()
        if not current:
            cursor.close()
            if connection.is_connected():
                connection.close()
            return jsonify({'message': 'No tiene permisos para actualizar este equipo'}), 403
        # Determinar qué campos se pueden actualizar (solo si están vacíos actualmente)
        def is_empty(v):
            return v is None or (isinstance(v, str) and v.strip() == '')
        update_fields = []
        values = []
        if cuenta_in and is_empty(current.get('cuenta')):
            update_fields.append('cuenta = %s')
            values.append(cuenta_in)
        if ot_in and is_empty(current.get('ot')):
            update_fields.append('ot = %s')
            values.append(ot_in)
        if observ_in:
            update_fields.append('observacion = %s')
            values.append(observ_in)
        if not update_fields:
            cursor.close()
            if connection.is_connected():
                connection.close()
            return jsonify({'message': 'No hay campos disponibles para actualizar (ya bloqueados).'}), 409
        # Aplicar actualización y fecha del último movimiento
        update_sql = f"UPDATE disponibilidad_equipos SET {', '.join(update_fields)}, fecha_ultimo_movimiento = NOW() WHERE serial = %s AND super = %s"
        values.extend([serial, supervisor])
        print(f"[actualizar_equipo] SQL: {update_sql} | values={values}")
        cursor.execute(update_sql, tuple(values))
        connection.commit()
        # Recalcular días
        cursor.execute(
            """
            UPDATE disponibilidad_equipos
            SET dias_ultimo = DATEDIFF(NOW(), fecha_ultimo_movimiento)
            WHERE serial = %s
            """,
            (serial,)
        )
        connection.commit()
        cursor.close()
        if connection.is_connected():
            connection.close()
        return jsonify({'success': True, 'message': 'Datos actualizados exitosamente'})
    except Exception as e:
        print(f"Error en api_actualizar_equipo_operativo: {e}")
        try:
            if 'connection' in locals() and connection and connection.is_connected():
                connection.rollback()
        except Exception:
            pass
        return jsonify({'message': 'Error al guardar los cambios'}), 500

@app.route('/dev/login', methods=['POST'])
def dev_login():
    try:
        # Solo disponible en modo debug
        if not app.debug:
            return jsonify({'message': 'No disponible en producción'}), 403
        data = request.get_json(force=True) or {}
        name = (data.get('user_name') or '').strip()
        cedula = (data.get('user_cedula') or '').strip()
        role = (data.get('user_role') or 'operativo').strip()
        if not name:
            return jsonify({'message': 'user_name requerido'}), 400
        user = User(id=cedula or 'dev', nombre=name, role=role)
        login_user(user)
        session['user_name'] = name
        session['user_cedula'] = cedula
        session['user_role'] = role
        return jsonify({'success': True, 'message': 'Sesión de desarrollo creada', 'user_name': name, 'user_role': role})
    except Exception as e:
        return jsonify({'message': 'Error en dev login', 'error': str(e)}), 500

# ============================================================================
# MÓDULO ANALISTAS - API ENDPOINTS Códigos de Facturación
# ============================================================================

@app.route('/api/analistas/codigos', methods=['GET'])
@login_required
def api_codigos_facturacion():
    """Lista de códigos de facturación con filtros opcionales"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor(dictionary=True)

        texto_busqueda = request.args.get('busqueda', '').strip()
        tecnologia = request.args.get('tecnologia', '').strip()
        agrupacion = request.args.get('agrupacion', '').strip()
        grupo = request.args.get('grupo', '').strip()

        query = """
            SELECT 
                id_base_codigos_facturacion AS idbase_codigos_facturacion,
                codigo AS codigo_codigos_facturacion,
                descripcion AS nombre_codigos_facturacion,
                tecnologia,
                '' AS instrucciones_de_uso_codigos_facturacion,
                categoria,
                nombre,
                0 AS facturable_codigos_facturacion
            FROM base_codigos_facturacion
            WHERE 1=1
        """
        params = []

        if texto_busqueda:
            query += """
                AND (
                    codigo LIKE %s OR 
                    descripcion LIKE %s
                )
            """
            busqueda_param = f"%{texto_busqueda}%"
            params.extend([busqueda_param, busqueda_param])
        if tecnologia:
            query += " AND tecnologia = %s"
            params.append(tecnologia)
        if agrupacion:
            query += " AND categoria = %s"
            params.append(agrupacion)
        if grupo:
            query += " AND nombre = %s"
            params.append(grupo)

        query += " ORDER BY codigo ASC"
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        return jsonify(resultados)

    except mysql.connector.Error as e:
        logging.error(f"Error en API codigos: {str(e)}")
        return jsonify({'error': 'Error al consultar la base de datos'}), 500
    except Exception as e:
        logging.error(f"Error inesperado en API codigos: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/analistas/codigos/grupos', methods=['GET'])
@login_required
def api_grupos_codigos_facturacion():
    """Lista única de grupos en códigos de facturación"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor()

        tecnologia = request.args.get('tecnologia', '').strip()
        agrupacion = request.args.get('agrupacion', '').strip()

        query = """
            SELECT DISTINCT nombre
            FROM base_codigos_facturacion
            WHERE nombre IS NOT NULL 
              AND nombre != ''
        """
        params = []
        if tecnologia:
            query += " AND tecnologia = %s"
            params.append(tecnologia)
        if agrupacion:
            query += " AND categoria = %s"
            params.append(agrupacion)
        query += " ORDER BY nombre ASC"

        cursor.execute(query, params) if params else cursor.execute(query)
        resultados = cursor.fetchall()
        grupos = [row[0] for row in resultados]
        return jsonify(grupos)

    except mysql.connector.Error as e:
        logging.error(f"Error en API grupos codigos: {str(e)}")
        return jsonify({'error': 'Error al consultar la base de datos'}), 500
    except Exception as e:
        logging.error(f"Error inesperado en API grupos codigos: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/analistas/codigos/tecnologias', methods=['GET'])
@login_required
def api_tecnologias_codigos_facturacion():
    """Lista única de tecnologías en códigos de facturación"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor()

        query = """
            SELECT DISTINCT tecnologia
            FROM base_codigos_facturacion
            WHERE tecnologia IS NOT NULL 
              AND tecnologia != ''
            ORDER BY tecnologia ASC
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        tecnologias = [row[0] for row in resultados]
        return jsonify(tecnologias)

    except mysql.connector.Error as e:
        logging.error(f"Error en API tecnologias codigos: {str(e)}")
        return jsonify({'error': 'Error al consultar la base de datos'}), 500
    except Exception as e:
        logging.error(f"Error inesperado en API tecnologias codigos: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

@app.route('/api/sgis/trabajo-seguro-rutinario/status', methods=['GET'])
@login_required
def api_sgis_tsr_status():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'error': 'DB_UNAVAILABLE'}), 200
        try:
            ddl = (
                """
                CREATE TABLE IF NOT EXISTS sgis_trabajos_seguridad_rutina (
                    id_sgis_trabajo_seguridad_rutina INT AUTO_INCREMENT PRIMARY KEY,
                    id_codigo_consumidor INT NOT NULL,
                    recurso_operativo_cedula VARCHAR(20) NULL,
                    nombre VARCHAR(128) NULL,
                    cargo VARCHAR(128) NULL,
                    ciudad VARCHAR(128) NULL,
                    placa VARCHAR(32) NULL,
                    actividad_asociada VARCHAR(64) NULL,
                    descripcion_tareas TEXT,
                    observaciones TEXT,
                    respuesta_1 VARCHAR(4),
                    respuesta_2 VARCHAR(4),
                    respuesta_3 VARCHAR(4),
                    respuesta_4 VARCHAR(4),
                    respuesta_5 VARCHAR(4),
                    respuesta_6 VARCHAR(4),
                    respuesta_7 VARCHAR(4),
                    respuesta_8 VARCHAR(4),
                    respuesta_9 VARCHAR(4),
                    respuesta_10 VARCHAR(4),
                    respuesta_11 VARCHAR(4),
                    respuesta_12 VARCHAR(4),
                    respuesta_13 VARCHAR(4),
                    respuesta_14 VARCHAR(4),
                    respuesta_15 VARCHAR(4),
                    respuesta_16 VARCHAR(4),
                    respuesta_17 VARCHAR(4),
                    riesgo VARCHAR(128) NULL,
                    peligro VARCHAR(128) NULL,
                    consecuencia TEXT,
                    control_propuesto TEXT,
                    firma_trabajador LONGTEXT,
                    firma_supervisor LONGTEXT,
                    fecha_registro DATETIME,
                    fecha_dia DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            cur_ddl = connection.cursor()
            cur_ddl.execute(ddl)
            try:
                connection.commit()
            except Exception:
                pass
            try:
                cur_ddl.close()
            except Exception:
                pass
        except Exception:
            # Si no se puede crear la tabla por permisos, continuar y usar fallback en SELECT
            pass
        # Intentar eliminar índice único existente para permitir múltiples gestiones al día
        try:
            cur_idx = connection.cursor()
            cur_idx.execute("SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = DATABASE() AND table_name='sgis_trabajos_seguridad_rutina' AND index_name='uq_tecnico_dia_rutina'")
            has_idx = (cur_idx.fetchone() or [0])[0]
            cur_idx.close()
            if has_idx:
                try:
                    cur_drop = connection.cursor()
                    cur_drop.execute("ALTER TABLE sgis_trabajos_seguridad_rutina DROP INDEX uq_tecnico_dia_rutina")
                    connection.commit()
                    cur_drop.close()
                except Exception:
                    pass
        except Exception:
            pass
        uid = session.get('id_codigo_consumidor') or session.get('user_id') or getattr(current_user, 'id', None)
        hoy = get_bogota_datetime().date()
        if not uid:
            return jsonify({'success': True, 'already_today': False})
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT COUNT(*) AS c FROM sgis_trabajos_seguridad_rutina WHERE id_codigo_consumidor = %s AND fecha_dia = %s", (uid, hoy))
        except Exception:
            cursor.execute("SELECT COUNT(*) AS c FROM capired.sgis_trabajos_seguridad_rutina WHERE id_codigo_consumidor = %s AND fecha_dia = %s", (uid, hoy))
        row = cursor.fetchone() or {}
        c = int(row.get('c',0) or 0)
        return jsonify({'success': True, 'count_today': c, 'limit_reached': c >= 10, 'already_today': c >= 1})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 200
    finally:
        if 'cursor' in locals():
            try:
                cursor.close()
            except Exception:
                pass
        if 'connection' in locals() and connection:
            try:
                connection.close()
            except Exception:
                pass

@app.route('/api/sgis/trabajo-seguridad-rutina/riesgos', methods=['GET'])
@login_required
def api_sgis_tsr_riesgos():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'error': 'DB_UNAVAILABLE'}), 200
        try:
            cur_ddl = connection.cursor()
            cur_ddl.execute(
                """
                CREATE TABLE IF NOT EXISTS sgis_riesgo_seguridad_rutina (
                    id_sgis_riesgo_seguridad_rutina INT AUTO_INCREMENT PRIMARY KEY,
                    riesgo VARCHAR(128) NOT NULL,
                    peligro VARCHAR(128) NULL,
                    consecuencia TEXT NULL,
                    controles TEXT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            try:
                connection.commit()
            except Exception:
                pass
            try:
                cur_ddl.close()
            except Exception:
                pass
        except Exception:
            # Si no se puede crear la tabla por permisos, continuar y usar fallback en SELECT
            pass
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id_sgis_riesgo_seguridad_rutina AS id, riesgo, peligro, consecuencia, controles FROM sgis_riesgo_seguridad_rutina")
        except Exception:
            try:
                cursor.execute("SELECT id_sgis_riesgo_seguridad_rutina AS id, riesgo, peligro, consecuencia, controles FROM capired.sgis_riesgo_seguridad_rutina")
            except Exception:
                cursor.execute("SELECT id AS id, riesgo, peligro, consecuencia, controles FROM sgis_riesgo_seguridad_rutina")
        rows = cursor.fetchall()
        if not rows:
            try:
                cur_seed = connection.cursor()
                cur_seed.executemany(
                    "INSERT INTO sgis_riesgo_seguridad_rutina (riesgo, peligro, consecuencia, controles) VALUES (%s,%s,%s,%s)",
                    [
                        ('Caídas de altura', 'Alturas', 'Lesiones graves por caída', 'Uso de arnés, línea de vida, puntos de anclaje certificados'),
                        ('Golpes por objetos', 'Impactos', 'Contusiones o fracturas', 'Orden y aseo, delimitación del área, uso de casco'),
                        ('Electrocución', 'Energía eléctrica', 'Paro cardiorrespiratorio', 'Bloqueo y etiquetado, herramientas aisladas, verificación de desenergización'),
                        ('Cortes y pinchazos', 'Herramientas', 'Heridas en extremidades', 'Uso de guantes y herramientas en buen estado'),
                        ('Exposición a calor', 'Trabajo en caliente', 'Quemaduras', 'Avisos, extintor disponible, cortinas térmicas y EPP adecuado')
                    ]
                )
                connection.commit()
                cur_seed.close()
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT id, riesgo, peligro, consecuencia, controles FROM sgis_riesgo_seguridad_rutina")
                rows = cursor.fetchall()
            except Exception:
                # Si no se puede sembrar (por permisos), dejar lista vacía para no romper
                rows = []
        data = []
        for r in rows:
            data.append({
                'id': r.get('id'),
                'riesgo': r.get('riesgo') or '',
                'peligro': r.get('peligro') or '',
                'consecuencia': r.get('consecuencia') or '',
                'controles': r.get('controles') or ''
            })
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 200
    finally:
        if 'cursor' in locals():
            try:
                cursor.close()
            except Exception:
                pass
        if 'connection' in locals() and connection:
            try:
                connection.close()
            except Exception:
                pass

@app.route('/api/analistas/codigos/agrupaciones', methods=['GET'])
@login_required
def api_agrupaciones_codigos_facturacion():
    """Lista única de agrupaciones en códigos de facturación, opcional por tecnología"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        cursor = connection.cursor()

        tecnologia = request.args.get('tecnologia', '').strip()
        if tecnologia:
            query = """
                SELECT DISTINCT categoria
                FROM base_codigos_facturacion
                WHERE categoria IS NOT NULL 
                  AND categoria != ''
                  AND tecnologia = %s
                ORDER BY categoria ASC
            """
            cursor.execute(query, (tecnologia,))
        else:
            query = """
                SELECT DISTINCT categoria
                FROM base_codigos_facturacion
                WHERE categoria IS NOT NULL 
                  AND categoria != ''
                ORDER BY categoria ASC
            """
            cursor.execute(query)

        resultados = cursor.fetchall()
        agrupaciones = [row[0] for row in resultados]
        return jsonify(agrupaciones)

    except mysql.connector.Error as e:
        logging.error(f"Error en API agrupaciones codigos: {str(e)}")
        return jsonify({'error': 'Error al consultar la base de datos'}), 500
    except Exception as e:
        logging.error(f"Error inesperado en API agrupaciones codigos: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

APITUDE_BASE_URL = 'https://apitude.co'
APITUDE_SIMIT_ENDPOINT = '/api/v1.0/requests/simit-co/'

SIMIT_PROXY_SERVER = None
SIMIT_PROXY_LIST = None
SIMIT_PROXY_INDEX = 0

def get_simit_proxy_server(reset=False):
    global SIMIT_PROXY_SERVER, SIMIT_PROXY_LIST, SIMIT_PROXY_INDEX
    if reset:
        SIMIT_PROXY_SERVER = None
    if SIMIT_PROXY_SERVER is not None:
        return SIMIT_PROXY_SERVER
    v = os.getenv('SIMIT_PROXY')
    if v:
        SIMIT_PROXY_SERVER = v.strip()
        return SIMIT_PROXY_SERVER
    if SIMIT_PROXY_LIST is None:
        try:
            list_url = os.getenv('SIMIT_PROXY_LIST_URL')
            if not list_url:
                key = os.getenv('PROXYSCRAPE_API_KEY')
                if key:
                    list_url = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all&auth=' + key.strip()
                else:
                    list_url = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
            r = requests.get(list_url, timeout=5)
            proxies = []
            if r.status_code == 200:
                for line in r.text.splitlines():
                    line = (line or '').strip()
                    if not line:
                        continue
                    if not line.startswith('http'):
                        line = 'http://' + line
                    proxies.append(line)
            SIMIT_PROXY_LIST = proxies
            SIMIT_PROXY_INDEX = 0
        except Exception:
            SIMIT_PROXY_LIST = []
            SIMIT_PROXY_INDEX = 0
    if SIMIT_PROXY_LIST:
        if SIMIT_PROXY_INDEX >= len(SIMIT_PROXY_LIST):
            return None
        SIMIT_PROXY_SERVER = SIMIT_PROXY_LIST[SIMIT_PROXY_INDEX]
        SIMIT_PROXY_INDEX += 1
        return SIMIT_PROXY_SERVER
    return None

def simit_query_by_placa_playwright(placa):
    try:
        s = (placa or '').strip().upper()
        if not s:
            return {'success': False, 'message': 'placa requerida'}
        async def _approx_from_page_async(page):
            return None
        def _run_async_fallback(val):
            try:
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = None
                if loop is not None and loop.is_running():
                    result_container = {}
                    error_container = {}
                    def _target():
                        try:
                            new_loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(new_loop)
                            result_container['result'] = new_loop.run_until_complete(_async_flow(val))
                        except Exception as exc:
                            error_container['error'] = exc
                        finally:
                            try:
                                new_loop.close()
                            except Exception:
                                pass
                    t = threading.Thread(target=_target)
                    t.start()
                    t.join()
                    if 'error' in error_container:
                        raise error_container['error']
                    return result_container.get('result')
                return asyncio.run(_async_flow(val))
            except Exception as e:
                return {'success': False, 'message': str(e)}
        async def _async_flow(val):
            try:
                async with async_playwright() as ap:
                    for attempt in range(3):
                        proxy_server = get_simit_proxy_server()
                        args = ["--disable-blink-features=AutomationControlled"]
                        launch_kwargs = {"headless": True, "args": args, "slow_mo": 50}
                        if proxy_server:
                            launch_kwargs["proxy"] = {"server": proxy_server}
                        else:
                            args.append("--no-proxy-server")
                        browser = await ap.chromium.launch(**launch_kwargs)
                        ctx2 = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', locale='es-ES')
                        pg = await ctx2.new_page()
                        try:
                            await pg.goto('https://www.fcm.org.co/simit/#/home-public', timeout=120000)
                        except Exception as e:
                            msg = str(e)
                            try:
                                await ctx2.close()
                            except Exception:
                                pass
                            try:
                                await browser.close()
                            except Exception:
                                pass
                            if 'ERR_TUNNEL_CONNECTION_FAILED' in msg or 'ERR_PROXY_CONNECTION_FAILED' in msg:
                                get_simit_proxy_server(reset=True)
                                if attempt == 2:
                                    return {'success': False, 'message': msg}
                                continue
                            return {'success': False, 'message': msg}
                    try:
                        await pg.wait_for_selector("text=Por placa", timeout=60000)
                    except Exception:
                        pass
                    try:
                        for txt in ['Aceptar','Acepto','Entendido','Continuar','Cerrar']:
                            cand = pg.locator(f'button:has-text("{txt}")')
                            if await cand.count() > 0:
                                await cand.first.click()
                                break
                    except Exception:
                        pass
                    try:
                        por_placa = pg.get_by_text('Por placa', exact=False)
                        if await por_placa.count() > 0:
                            await por_placa.first.click()
                        else:
                            lnk = pg.locator('a[href*="por-placa"], button:has-text("Por placa")')
                            if await lnk.count() > 0:
                                await lnk.first.click()
                            else:
                                await pg.evaluate("()=>{ const txt='por placa'; const nodes=Array.from(document.querySelectorAll('a,button,div,span')); for(const n of nodes){ const t=(n.innerText||n.textContent||'').toLowerCase(); if(t.includes(txt)){ n.click(); return true; } } return false; }")
                    except Exception:
                        try:
                            await pg.evaluate("()=>{ const txt='por placa'; const nodes=Array.from(document.querySelectorAll('a,button,div,span')); for(const n of nodes){ const t=(n.innerText||n.textContent||'').toLowerCase(); if(t.includes(txt)){ n.click(); return true; } } return false; }")
                        except Exception:
                            pass
                    try:
                        await pg.wait_for_timeout(1500)
                    except Exception:
                        pass
                    try:
                        await pg.wait_for_selector('form input, mat-form-field input, input[formcontrolname], input[ng-reflect-form-control-name]', timeout=12000)
                    except Exception:
                        pass
                    ok = False
                    try:
                        ok = await pg.evaluate(
                            """
                            (val)=>{
                              const vis = el => !!(el && (el.offsetParent || el.getClientRects().length));
                              const txt = el => (el && (el.innerText||el.textContent)||'').toLowerCase();
                              let el = null;
                              let inputs = Array.from(document.querySelectorAll('mat-form-field input'));
                              if(inputs.length === 0){ inputs = Array.from(document.querySelectorAll('input')); }
                              for(const i of inputs){
                                if(!vis(i)) continue;
                                const aria = (i.getAttribute('aria-label')||'').toLowerCase();
                                if(aria.includes('placa')){ el=i; break; }
                                const labels = i.labels ? Array.from(i.labels) : [];
                                const ltext = labels.map(x=>txt(x)).join(' ');
                                if(ltext.includes('placa')){ el=i; break; }
                                const f = i.closest('form');
                                const ptxt = txt(f)||txt(i.parentElement);
                                if(ptxt.includes('placa')){ el=i; break; }
                              }
                              if(!el){
                                const lbls = Array.from(document.querySelectorAll('label, mat-label, span, div'));
                                const l = lbls.find(x=>vis(x) && txt(x).includes('placa'));
                                if(l){
                                  const cont = l.closest('form') || l.parentElement;
                                  if(cont){
                                    let ins = Array.from(cont.querySelectorAll('mat-form-field input')).filter(vis);
                                    if(ins.length === 0){ ins = Array.from(cont.querySelectorAll('input')).filter(vis); }
                                    el = ins[0]||null;
                                  }
                                }
                              }
                              if(el){
                                el.focus();
                                try{ el.value=''; }catch(e){}
                                try{ el.dispatchEvent(new Event('input',{bubbles:true})); }catch(e){}
                                try{ el.value=val; }catch(e){}
                                try{ el.dispatchEvent(new Event('input',{bubbles:true})); }catch(e){}
                                try{ el.dispatchEvent(new Event('change',{bubbles:true})); }catch(e){}
                                return true;
                              }
                              return false;
                            }
                            """,
                            val
                        )
                    except Exception:
                        ok = False
                    if not ok:
                        try:
                            await pg.evaluate(
                                """
                                (val)=>{
                                  try{
                                    const ins = Array.from(document.querySelectorAll('input')).filter(el=>el && el.offsetParent);
                                    if(ins.length){
                                      ins[0].focus();
                                      ins[0].value='';
                                      ins[0].dispatchEvent(new Event('input',{bubbles:true}));
                                      ins[0].value=val;
                                      ins[0].dispatchEvent(new Event('input',{bubbles:true}));
                                      ins[0].dispatchEvent(new Event('change',{bubbles:true}));
                                    }
                                    return true;
                                  }catch(e){ return false; }
                                }
                                """,
                                val
                            )
                        except Exception:
                            pass
                    try:
                        sub_ok = await pg.evaluate("()=>{ const f=document.querySelector('form')||document; const q=sel=>Array.from(f.querySelectorAll(sel)); const bv=q('button[type=submit], button.mat-raised-button, button.mat-flat-button').find(x=>/(consultar|buscar)/i.test((x.innerText||x.textContent||''))); if(bv){ bv.click(); return true;} const b=q('button').find(x=>/(consultar|buscar)/i.test((x.innerText||x.textContent||''))); if(b){ b.click(); return true;} return false; }")
                        if not sub_ok:
                            try:
                                await pg.keyboard.press('Enter')
                            except Exception:
                                pass
                    except Exception:
                        await ctx2.close(); await browser.close()
                        return {'success': False, 'message': 'boton consultar no encontrado'}
                    try:
                        await pg.wait_for_function("()=>{ const t=(document.body.innerText||''); return /NO REGISTRA COMPARENDOS|NO REGISTRA MULTAS|TOTAL A PAGAR|TOTAL\s*\(/i.test(t); }", timeout=30000)
                    except Exception:
                        pass
                    await pg.wait_for_timeout(1000)
                    data2 = None
                    try:
                        body_txt = await pg.inner_text('body')
                    except Exception:
                        body_txt = ''
                    up = (body_txt or '').upper()
                    no_multas = ('NO REGISTRA MULTAS' in up) or ('NO REGISTRA COMPARENDOS NI MULTAS' in up) or ('NO REGISTRA COMPARENDOS Y MULTAS' in up) or ('NO REGISTRA COMPARENDOS O MULTAS' in up)
                    if no_multas:
                        data2 = {'results': []}
                    else:
                        try:
                            import re as _re
                            m = _re.search(r"TOTAL\s*\((\d+)\)\s*[:$]\s*\$?\s*([\d\.,]+)", body_txt, flags=_re.IGNORECASE)
                            multas_count = None
                            val_s = None
                            if m:
                                multas_count = int(m.group(1))
                                val_s = m.group(2)
                            else:
                                m = _re.search(r"TOTAL\s*A\s*PAGAR\s*[:$]?\s*\$?\s*([\d\.,]+)", body_txt, flags=_re.IGNORECASE)
                                if not m:
                                    m = _re.search(r"TOTAL\s*[:$]\s*\$?\s*([\d\.,]+)", body_txt, flags=_re.IGNORECASE)
                                val_s = m.group(1) if m else None
                            val_f = float(str(val_s).replace('.', '').replace(',', '.')) if val_s else None
                        except Exception:
                            multas_count = None
                            val_f = None
                        if val_f is not None and val_f > 0:
                            if multas_count is None:
                                try:
                                    mm = _re.search(r"MULTAS\s*:\s*(\d+)", up, flags=_re.IGNORECASE)
                                    if mm:
                                        multas_count = int(mm.group(1))
                                except Exception:
                                    multas_count = None
                            item = {'numero': 'TOTAL', 'valor_total': val_f, 'entidad': 'SIMIT', 'estado': 'TOTAL'}
                            data2 = {'results': [item]}
                            if multas_count is not None and multas_count >= 0:
                                data2['multas'] = multas_count
                                item['cantidad_multas'] = multas_count
                        else:
                            data2 = {'results': []}
                    await ctx2.close(); await browser.close()
                    if data2 is None:
                        return {'success': False, 'message': 'sin datos'}
                    return {'success': True, 'data': data2}
            except Exception as e:
                return {'success': False, 'message': str(e)}
        p = None
        b = None
        ctx = None
        page = None
        stopped = False
        def _cleanup():
            nonlocal stopped
            try:
                if ctx:
                    ctx.close()
            except Exception:
                pass
            try:
                if b:
                    b.close()
            except Exception:
                pass
            if not stopped:
                try:
                    if p:
                        p.stop()
                except Exception:
                    pass
                stopped = True
        def _approx_from_page(page):
            return None
        for attempt in range(3):
            with simit_playwright_lock:
                try:
                    p = sync_playwright().start()
                except Exception:
                    fb = _run_async_fallback(s)
                    return fb if isinstance(fb, dict) else {'success': False, 'message': ''}
                proxy_server = get_simit_proxy_server()
                if proxy_server:
                    b = p.chromium.launch(headless=True, proxy={"server": proxy_server}, args=["--disable-blink-features=AutomationControlled"], slow_mo=50)
                else:
                    b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled", "--no-proxy-server"], slow_mo=50)
                ctx = b.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', locale='es-ES')
                page = ctx.new_page()
                try:
                    page.goto('https://www.fcm.org.co/simit/#/home-public', timeout=120000)
                except Exception as e:
                    msg = str(e)
                    _cleanup()
                    if 'ERR_TUNNEL_CONNECTION_FAILED' in msg or 'ERR_PROXY_CONNECTION_FAILED' in msg:
                        get_simit_proxy_server(reset=True)
                        if attempt == 2:
                            fb = _run_async_fallback(s)
                            return fb if isinstance(fb, dict) else {'success': False, 'message': msg}
                        continue
                    return {'success': False, 'message': msg}
                try:
                    page.wait_for_selector("text=Por placa", timeout=60000)
                except Exception:
                    pass
                try:
                    for txt in ['Aceptar','Acepto','Entendido','Continuar','Cerrar']:
                        cand = page.locator(f'button:has-text("{txt}")')
                        if cand.count() > 0:
                            cand.first.click()
                            break
                except Exception:
                    pass
            try:
                por_placa = page.get_by_text('Por placa', exact=False)
                if por_placa.count() > 0:
                    por_placa.first.click()
                else:
                    lnk = page.locator('a[href*="por-placa"], button:has-text("Por placa")')
                    if lnk.count() > 0:
                        lnk.first.click()
                    else:
                        page.evaluate("()=>{ const txt='por placa'; const nodes=Array.from(document.querySelectorAll('a,button,div,span')); for(const n of nodes){ const t=(n.innerText||n.textContent||'').toLowerCase(); if(t.includes(txt)){ n.click(); return true; } } return false; }")
            except Exception:
                try:
                    page.evaluate("()=>{ const txt='por placa'; const nodes=Array.from(document.querySelectorAll('a,button,div,span')); for(const n of nodes){ const t=(n.innerText||n.textContent||'').toLowerCase(); if(t.includes(txt)){ n.click(); return true; } } return false; }")
                except Exception:
                    pass
            if True:
                try:
                    for fr in page.frames:
                        try:
                            por_placa_fr = fr.get_by_text('Por placa', exact=False)
                            if por_placa_fr.count() > 0:
                                por_placa_fr.first.click()
                                break
                        except Exception:
                            pass
                except Exception:
                    pass
            try:
                page.wait_for_timeout(1500)
            except Exception:
                pass
                try:
                    page.wait_for_selector('form input, mat-form-field input, input[formcontrolname], input[ng-reflect-form-control-name]', timeout=12000)
                except Exception:
                    pass
            form = None
            try:
                forms = page.locator('form')
                cnt = forms.count()
                for i in range(cnt):
                    f = forms.nth(i)
                    try:
                        t = f.inner_text().lower()
                    except Exception:
                        t = ''
                    if 'placa' in t:
                        form = f
                        break
            except Exception:
                form = None
            inp = None
            try:
                special = page.locator('input#txtBusqueda, input[name="txtBusqueda"], input[placeholder*="placa del vehículo" i], input[placeholder*="placa del veh" i], input[aria-label*="placa del vehículo" i], input[aria-label*="placa del veh" i]')
                if special.count() > 0:
                    inp = special.first
            except Exception:
                inp = None
            if form is not None:
                candidates = form.locator('input[placeholder*="placa" i], input[name*="placa" i], input[id*="placa" i], input[type="text"]')
                if candidates.count() > 0:
                    inp = candidates.first
            if inp is None:
                candidates = page.locator('input[formcontrolname="placa"], input[ng-reflect-form-control-name*="placa"], input[placeholder*="placa" i], input[placeholder*="vehículo" i], input[placeholder*="vehiculo" i], input[name*="placa" i], input[id*="placa" i], input.mat-input-element')
                if candidates.count() > 0:
                    inp = candidates.first
            if inp is None:
                try:
                    any_inp = page.locator('form input')
                    if any_inp.count() > 0:
                        inp = any_inp.first
                except Exception:
                    pass
            if inp is None:
                try:
                    lb = page.get_by_label('Placa', exact=False)
                    if lb.count() > 0:
                        inp = lb.first
                except Exception:
                    pass
            if inp is None:
                try:
                    tb = page.get_by_role('textbox', name='Placa', exact=False)
                    if tb.count() > 0:
                        inp = tb.first
                except Exception:
                    pass
            if inp is None:
                try:
                    ph = page.get_by_placeholder('Placa', exact=False)
                    if ph.count() > 0:
                        inp = ph.first
                except Exception:
                    pass
            if inp is None:
                txts = page.locator('form input[type="text"]')
                if txts.count() > 0:
                    inp = txts.first
            if inp is None:
                try:
                    xp = page.locator('xpath=//*[contains(text(),"Placa")]/following::input[1]')
                    if xp.count() > 0:
                        inp = xp.first
                except Exception:
                    pass
            if inp is None:
                try:
                    for fr in page.frames:
                        try:
                            lb = fr.get_by_label('Placa', exact=False)
                            if lb.count() > 0:
                                inp = lb.first
                                break
                        except Exception:
                            pass
                        try:
                            tb = fr.get_by_role('textbox', name='Placa', exact=False)
                            if tb.count() > 0:
                                inp = tb.first
                                break
                        except Exception:
                            pass
                        try:
                            cand = fr.locator('input[placeholder*="placa" i], input[name*="placa" i], input[id*="placa" i], input[type="text"], input')
                            if cand.count() > 0:
                                inp = cand.first
                                break
                        except Exception:
                            pass
                except Exception:
                    pass
            if inp is None or (inp is not None and not inp.is_visible()):
                try:
                    ok = page.evaluate("""
                        (val)=>{
                          const vis = el => !!(el && (el.offsetParent || el.getClientRects().length));
                          const txt = el => (el && (el.innerText||el.textContent)||'').toLowerCase();
                          let el = null;
                          let inputs = Array.from(document.querySelectorAll('mat-form-field input'));
                          if(inputs.length === 0){ inputs = Array.from(document.querySelectorAll('input')); }
                          for(const i of inputs){
                            if(!vis(i)) continue;
                            const aria = (i.getAttribute('aria-label')||'').toLowerCase();
                            if(aria.includes('placa')){ el=i; break; }
                            const labels = i.labels ? Array.from(i.labels) : [];
                            const ltext = labels.map(x=>txt(x)).join(' ');
                            if(ltext.includes('placa')){ el=i; break; }
                            const f = i.closest('form');
                            const ptxt = txt(f)||txt(i.parentElement);
                            if(ptxt.includes('placa')){ el=i; break; }
                          }
                          if(!el){
                            const lbls = Array.from(document.querySelectorAll('label, mat-label, span, div'));
                            const l = lbls.find(x=>vis(x) && txt(x).includes('placa'));
                            if(l){
                              const cont = l.closest('form') || l.parentElement;
                              if(cont){
                                let ins = Array.from(cont.querySelectorAll('mat-form-field input')).filter(vis);
                                if(ins.length === 0){ ins = Array.from(cont.querySelectorAll('input')).filter(vis); }
                                el = ins[0]||null;
                              }
                            }
                          }
                          if(!el){
                            const nodes = Array.from(document.querySelectorAll('*'));
                            for(const n of nodes){
                              const sr = n.shadowRoot;
                              if(!sr) continue;
                              const ins = Array.from(sr.querySelectorAll('input'));
                              const cand = ins.find(i=>vis(i) && ((i.getAttribute('aria-label')||'').toLowerCase().includes('placa') || (i.placeholder||'').toLowerCase().includes('placa')));
                              if(cand){ el=cand; break; }
                            }
                          }
                          if(el){
                            el.focus();
                            try{ el.value=''; }catch(e){}
                            try{ el.dispatchEvent(new Event('input',{bubbles:true})); }catch(e){}
                            try{ el.value=val; }catch(e){}
                            try{ el.dispatchEvent(new Event('input',{bubbles:true})); }catch(e){}
                            try{ el.dispatchEvent(new Event('change',{bubbles:true})); }catch(e){}
                            return true;
                          }
                          return false;
                        }
                    """, s)
                    if not ok:
                        try:
                            page.evaluate(
                                """
                                (val)=>{
                                  try{
                                    const ins = Array.from(document.querySelectorAll('input')).filter(el=>el && el.offsetParent);
                                    if(ins.length){
                                      ins[0].focus();
                                      ins[0].value='';
                                      ins[0].dispatchEvent(new Event('input',{bubbles:true}));
                                      ins[0].value=val;
                                      ins[0].dispatchEvent(new Event('input',{bubbles:true}));
                                      ins[0].dispatchEvent(new Event('change',{bubbles:true}));
                                    }
                                    return true;
                                  }catch(e){ return false; }
                                }
                                """,
                                s
                            )
                        except Exception:
                            pass
                except Exception:
                    pass
                if inp is None or (inp is not None and not inp.is_visible()):
                    try:
                        filled = False
                        for fr in page.frames:
                            try:
                                ok_fr = fr.evaluate("""
                                    (val)=>{
                                      const vis = el => !!(el && (el.offsetParent || el.getClientRects().length));
                                      const txt = el => (el && (el.innerText||el.textContent)||'').toLowerCase();
                                      let el = null;
                                      let inputs = Array.from(document.querySelectorAll('mat-form-field input'));
                                      if(inputs.length === 0){ inputs = Array.from(document.querySelectorAll('input')); }
                                      for(const i of inputs){
                                        if(!vis(i)) continue;
                                        const aria = (i.getAttribute('aria-label')||'').toLowerCase();
                                        if(aria.includes('placa')){ el=i; break; }
                                        const labels = i.labels ? Array.from(i.labels) : [];
                                        const ltext = labels.map(x=>txt(x)).join(' ');
                                        if(ltext.includes('placa')){ el=i; break; }
                                        const f = i.closest('form');
                                        const ptxt = txt(f)||txt(i.parentElement);
                                        if(ptxt.includes('placa')){ el=i; break; }
                                      }
                                      if(!el){
                                        const lbls = Array.from(document.querySelectorAll('label, mat-label, span, div'));
                                        const l = lbls.find(x=>vis(x) && txt(x).includes('placa'));
                                        if(l){
                                          const cont = l.closest('form') || l.parentElement;
                                          if(cont){
                                            let ins = Array.from(cont.querySelectorAll('mat-form-field input')).filter(vis);
                                            if(ins.length === 0){ ins = Array.from(cont.querySelectorAll('input')).filter(vis); }
                                            el = ins[0]||null;
                                          }
                                        }
                                      }
                                      if(!el){
                                        const nodes = Array.from(document.querySelectorAll('*'));
                                        for(const n of nodes){
                                          const sr = n.shadowRoot;
                                          if(!sr) continue;
                                          const ins = Array.from(sr.querySelectorAll('input'));
                                          const cand = ins.find(i=>vis(i) && ((i.getAttribute('aria-label')||'').toLowerCase().includes('placa') || (i.placeholder||'').toLowerCase().includes('placa')));
                                          if(cand){ el=cand; break; }
                                        }
                                      }
                                      if(el){
                                        el.focus();
                                        try{ el.value=''; }catch(e){}
                                        try{ el.dispatchEvent(new Event('input',{bubbles:true})); }catch(e){}
                                        try{ el.value=val; }catch(e){}
                                        try{ el.dispatchEvent(new Event('input',{bubbles:true})); }catch(e){}
                                        try{ el.dispatchEvent(new Event('change',{bubbles:true})); }catch(e){}
                                        return true;
                                      }
                                      return false;
                                    }
                                """, s)
                                if ok_fr:
                                    filled = True
                                    break
                            except Exception:
                                pass
                        if not filled:
                            try:
                                inputs = page.locator('input')
                                c = inputs.count()
                                cand = None
                                for i in range(c):
                                    el = inputs.nth(i)
                                    try:
                                        if el.is_visible():
                                            cand = el
                                            break
                                    except Exception:
                                        pass
                                if cand:
                                    try:
                                        cand.focus()
                                        cand.fill(s)
                                    except Exception:
                                        try:
                                            cand.click()
                                        except Exception:
                                            pass
                                        try:
                                            page.keyboard.type(s)
                                        except Exception:
                                            pass
                                else:
                                    _cleanup()
                                    return {'success': False, 'message': 'input placa no encontrado'}
                            except Exception:
                                _cleanup()
                                return {'success': False, 'message': 'input placa no encontrado'}
                    except Exception:
                        _cleanup()
                        return {'success': False, 'message': 'input placa no encontrado'}
            else:
                inp.fill(s)
            btn = None
            if form is not None:
                bts = form.locator('button[type="submit"]')
                if bts.count() > 0:
                    btn = bts.first
            captured = []
            if btn is None:
                btn_candidates = [
                    'button:has-text("Consultar")',
                    'button:has-text("Buscar")'
                ]
                for bs in btn_candidates:
                    if page.locator(bs).count() > 0:
                        btn = page.locator(bs).first
                        break
            if btn is None and form is not None:
                bts2 = form.locator('button')
                if bts2.count() > 0:
                    btn = bts2.first
            if btn is None:
                try:
                    sub_ok = page.evaluate("()=>{ const f=document.querySelector('form')||document; const q=sel=>Array.from(f.querySelectorAll(sel)); const bv=q('button[type=submit], button.mat-raised-button, button.mat-flat-button').find(x=>/(consultar|buscar)/i.test((x.innerText||x.textContent||''))); if(bv){ bv.click(); return true;} const b=q('button').find(x=>/(consultar|buscar)/i.test((x.innerText||x.textContent||''))); if(b){ b.click(); return true;} return false; }")
                    if not sub_ok:
                        try:
                            page.keyboard.press('Enter')
                        except Exception:
                            pass
                except Exception:
                    _cleanup()
                    return {'success': False, 'message': 'boton consultar no encontrado'}
            else:
                try:
                    btn.click()
                except Exception:
                    try:
                        page.keyboard.press('Enter')
                    except Exception:
                        pass
            try:
                page.wait_for_function("()=>{ const t=(document.body.innerText||''); return /NO REGISTRA COMPARENDOS|NO REGISTRA MULTAS|TOTAL A PAGAR|TOTAL\s*\(/i.test(t); }", timeout=30000)
            except Exception:
                pass
            page.wait_for_timeout(1000)
            data = None
            if data is None:
                try:
                    body_txt = page.inner_text('body')
                except Exception:
                    body_txt = ''
                up = (body_txt or '').upper()
                no_multas = ('NO REGISTRA MULTAS' in up) or ('NO REGISTRA COMPARENDOS NI MULTAS' in up) or ('NO REGISTRA COMPARENDOS Y MULTAS' in up) or ('NO REGISTRA COMPARENDOS O MULTAS' in up)
                if no_multas:
                    data = {'results': []}
                else:
                    try:
                        m = re.search(r"TOTAL\s*\((\d+)\)\s*[:$]\s*\$?\s*([\d\.,]+)", body_txt, flags=re.IGNORECASE)
                        multas_count = None
                        val_s = None
                        if m:
                            multas_count = int(m.group(1))
                            val_s = m.group(2)
                        else:
                            m = re.search(r"TOTAL\s*A\s*PAGAR\s*[:$]?\s*\$?\s*([\d\.,]+)", body_txt, flags=re.IGNORECASE)
                            if not m:
                                m = re.search(r"TOTAL\s*[:$]\s*\$?\s*([\d\.,]+)", body_txt, flags=re.IGNORECASE)
                            val_s = m.group(1) if m else None
                        val_f = float(str(val_s).replace('.', '').replace(',', '.')) if val_s else None
                    except Exception:
                        multas_count = None
                        val_f = None
                    if val_f is not None and val_f > 0:
                        if multas_count is None:
                            try:
                                mm = re.search(r"MULTAS\s*:\s*(\d+)", up, flags=re.IGNORECASE)
                                if mm:
                                    multas_count = int(mm.group(1))
                            except Exception:
                                multas_count = None
                        item = {'numero': 'TOTAL', 'valor_total': val_f, 'entidad': 'SIMIT', 'estado': 'TOTAL'}
                        data = {'results': [item]}
                        if multas_count is not None and multas_count >= 0:
                            data['multas'] = multas_count
                            item['cantidad_multas'] = multas_count
                    else:
                        data = {'results': []}
            _cleanup()
            if data is None:
                wait_s = random.randint(6, 10)
                time.sleep(wait_s)
                continue
            return {'success': True, 'data': data}
        return {'success': False, 'message': 'sin datos'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def apitude_simit_create_request(document_type, document_number):
    api_key = os.getenv('APITUDE_API_KEY')
    if not api_key:
        return {'success': False, 'error': 'CONFIG', 'message': 'API key no configurada'}
    url = f"{APITUDE_BASE_URL}{APITUDE_SIMIT_ENDPOINT}"
    headers = {'x-api-key': api_key, 'Content-Type': 'application/json'}
    payload = {'document_type': document_type, 'document_number': document_number}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code >= 400:
            return {'success': False, 'status_code': r.status_code, 'error': 'HTTP', 'response': r.text}
        data = r.json()
        return {'success': True, 'data': data}
    except Exception as e:
        return {'success': False, 'error': 'EXCEPTION', 'message': str(e)}

def apitude_simit_get_result(request_id):
    api_key = os.getenv('APITUDE_API_KEY')
    if not api_key:
        return {'success': False, 'message': 'API key no configurada'}
    path = f"/api/v1.0/requests/simit-co/{request_id}/"
    url = f"{APITUDE_BASE_URL}{path}"
    headers = {'x-api-key': api_key, 'Accept': 'application/json'}
    try:
        r = requests.get(url, headers=headers, timeout=30)
        content_type = r.headers.get('Content-Type') or ''
        data = r.json() if 'application/json' in content_type else {'raw': r.text}
        if r.status_code >= 400:
            return {'success': False, 'status_code': r.status_code, 'data': data}
        return {'success': True, 'data': data}
    except Exception as e:
        return {'success': False, 'message': str(e)}

@app.route('/api/mpa/simit/request', methods=['POST'])
@login_required
def api_mpa_simit_request():
    data = request.get_json(silent=True) or {}
    document_type = data.get('document_type') or request.form.get('document_type')
    document_number = data.get('document_number') or request.form.get('document_number')
    if not document_type or not document_number:
        return jsonify({'success': False, 'message': 'document_type y document_number requeridos'}), 400
    result = apitude_simit_create_request(document_type, document_number)
    if not result.get('success'):
        status = result.get('status_code') or 500
        return jsonify(result), status
    d = result.get('data') or {}
    return jsonify({'success': True, 'message': d.get('message'), 'url': d.get('url'), 'request_id': d.get('request_id')})

@app.route('/api/mpa/simit/result/<request_id>', methods=['GET'])
@login_required
def api_mpa_simit_result(request_id):
    api_key = os.getenv('APITUDE_API_KEY')
    if not api_key:
        return jsonify({'success': False, 'message': 'API key no configurada'}), 500
    path = f"/api/v1.0/requests/simit-co/{request_id}/"
    url = f"{APITUDE_BASE_URL}{path}"
    headers = {'x-api-key': api_key, 'Accept': 'application/json'}
    try:
        r = requests.get(url, headers=headers, timeout=30)
        content_type = r.headers.get('Content-Type') or ''
        data = r.json() if 'application/json' in content_type else {'raw': r.text}
        if r.status_code >= 400:
            return jsonify({'success': False, 'status_code': r.status_code, 'data': data}), r.status_code
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def ensure_mpa_simit_job_runs_table():
    try:
        conn = get_db_connection()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mpa_simit_job_runs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                started_at DATETIME NULL,
                finished_at DATETIME NULL,
                total INT DEFAULT 0,
                processed INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        conn.commit()
        cur.close(); conn.close()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass

ensure_mpa_simit_job_runs_table()

simit_job_state = {
	'running': False,
	'started_at': None,
	'finished_at': None,
	'total': 0,
	'processed': 0,
	'interval': 30,
	'stop_requested': False
}

simit_job_stop_event = threading.Event()

def _mpa_simit_job_run():
    try:
        simit_job_stop_event.clear()
    except Exception:
        pass
    connection = get_db_connection()
    if connection is None:
        simit_job_state['running'] = False
        simit_job_state['finished_at'] = get_bogota_datetime()
        return
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT 
                mv.placa,
                mv.tipo_vehiculo,
                CAST(mv.tecnico_asignado AS UNSIGNED) AS tecnico_id,
                ro.nombre AS tecnico_nombre,
                ro.recurso_operativo_cedula AS cedula
            FROM mpa_vehiculos mv
            LEFT JOIN recurso_operativo ro ON CAST(mv.tecnico_asignado AS UNSIGNED) = ro.id_codigo_consumidor
            WHERE mv.placa IS NOT NULL AND TRIM(mv.placa) != ''
              AND mv.estado = 'Activo'
              AND mv.tecnico_asignado IS NOT NULL AND TRIM(mv.tecnico_asignado) <> ''
              AND ro.estado = 'Activo'
            ORDER BY mv.placa
            """
        )
        rows = cursor.fetchall() or []
        simit_job_state['total'] = len(rows)
        simit_job_state['processed'] = 0
        run_conn = get_db_connection()
        run_cur = run_conn.cursor()
        run_cur.execute("INSERT INTO mpa_simit_job_runs (started_at, total, processed) VALUES (%s,%s,%s)", (get_bogota_datetime(), simit_job_state['total'], 0))
        run_conn.commit()
        run_cur.execute("SELECT LAST_INSERT_ID()")
        run_id_row = run_cur.fetchone()
        run_id = run_id_row[0] if run_id_row else None
        for r in rows:
            if simit_job_stop_event.is_set():
                break
            placa = (r.get('placa') or '').strip().upper()
            tipo = r.get('tipo_vehiculo') or None
            tecnico_id = r.get('tecnico_id')
            tecnico_nombre = r.get('tecnico_nombre') or None
            res = simit_query_by_placa_playwright(placa)
            if not res.get('success'):
                try:
                    _update_comparendos_from_result(placa, tecnico_id, tecnico_nombre, tipo, [])
                except Exception:
                    pass
                simit_job_state['processed'] += 1
                if run_id is not None:
                    run_cur.execute("UPDATE mpa_simit_job_runs SET processed=%s WHERE id=%s", (simit_job_state['processed'], run_id))
                    run_conn.commit()
                continue
            data_block = res.get('data') or {}
            _update_comparendos_from_result(placa, tecnico_id, tecnico_nombre, tipo, data_block)
            simit_job_state['processed'] += 1
            if run_id is not None:
                run_cur.execute("UPDATE mpa_simit_job_runs SET processed=%s WHERE id=%s", (simit_job_state['processed'], run_id))
                run_conn.commit()
            try:
                iv = int(simit_job_state.get('interval') or 60)
            except Exception:
                iv = 60
            if iv < 1:
                iv = 1
            for _ in range(iv):
                if simit_job_stop_event.is_set():
                    break
                time.sleep(1)
        if run_id is not None:
            run_cur.execute("UPDATE mpa_simit_job_runs SET finished_at=%s WHERE id=%s", (get_bogota_datetime(), run_id))
            run_conn.commit()
        run_cur.close(); run_conn.close()
    except Exception:
        try:
            run_conn.rollback()
        except Exception:
            pass
    finally:
        try:
            cursor.close()
            connection.close()
        except Exception:
            pass
        simit_job_state['running'] = False
        simit_job_state['finished_at'] = get_bogota_datetime()
        simit_job_state['stop_requested'] = False

def _simit_job_due():
    now_dt = get_bogota_datetime()
    day = now_dt.day
    if day not in (1, 15):
        return False
    if now_dt.hour < 21:
        return False
    try:
        conn = get_db_connection()
        if conn is None:
            return True
        cur = conn.cursor()
        cur.execute("SELECT MAX(finished_at) FROM mpa_simit_job_runs")
        row = cur.fetchone()
        cur.close(); conn.close()
        last = row[0] if row else None
        if not last:
            return True
        return last.date() != now_dt.date()
    except Exception:
        return True

def _maybe_start_simit_job_auto():
    if simit_job_state['running']:
        return
    if _simit_job_due():
        simit_job_state['running'] = True
        simit_job_state['started_at'] = get_bogota_datetime()
        t = threading.Thread(target=_mpa_simit_job_run, daemon=True)
        t.start()

@app.route('/api/mpa/simit/job/run', methods=['POST'])
@login_required
def api_mpa_simit_job_run():
    if not current_user.has_role('administrativo'):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    if simit_job_state['running']:
        return jsonify({'success': False, 'message': 'Job en ejecución'}), 400
    data = request.get_json(silent=True) or {}
    force_param = request.args.get('force') or request.form.get('force') or data.get('force')
    force = False
    try:
        force = str(force_param).strip().lower() in ('1','true','t','yes','y','si','s')
    except Exception:
        force = False
    # intervalo configurable
    iv_param = request.args.get('interval') or request.form.get('interval') or data.get('interval')
    try:
        iv = int(str(iv_param)) if iv_param is not None else int(simit_job_state.get('interval') or 60)
    except Exception:
        iv = int(simit_job_state.get('interval') or 60)
    if iv < 3:
        iv = 3
    if iv > 300:
        iv = 300
    simit_job_state['interval'] = iv
    if not force and not _simit_job_due():
        return jsonify({'success': False, 'message': 'No corresponde ejecutar'}), 400
    simit_job_state['running'] = True
    simit_job_state['started_at'] = get_bogota_datetime()
    simit_job_state['stop_requested'] = False
    try:
        simit_job_stop_event.clear()
    except Exception:
        pass
    t = threading.Thread(target=_mpa_simit_job_run, daemon=True)
    t.start()
    return jsonify({'success': True, 'message': 'Job iniciado'})

@app.route('/api/mpa/simit/job/status', methods=['GET'])
@login_required
def api_mpa_simit_job_status():
    if not current_user.has_role('administrativo'):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    s = simit_job_state.copy()
    def _fmt(dt):
        try:
            return dt.strftime('%Y-%m-%d %H:%M:%S') if dt else None
        except Exception:
            return None
    return jsonify({
        'success': True,
        'data': {
            'running': s.get('running'),
            'started_at': _fmt(s.get('started_at')),
            'finished_at': _fmt(s.get('finished_at')),
            'total': s.get('total'),
            'processed': s.get('processed'),
            'interval': s.get('interval'),
            'stop_requested': s.get('stop_requested')
        }
    })

@app.route('/api/mpa/simit/job/stop', methods=['POST','GET'])
@login_required
def api_mpa_simit_job_stop():
    if not current_user.has_role('administrativo'):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    if not simit_job_state.get('running'):
        return jsonify({'success': False, 'message': 'Job no está en ejecución'}), 400
    try:
        simit_job_stop_event.set()
        simit_job_state['stop_requested'] = True
        return jsonify({'success': True, 'message': 'Solicitud de detener enviada'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

_maybe_start_simit_job_auto()

@app.route('/api/sgis/permiso-trabajo', methods=['POST'])
@login_required
def api_sgis_permiso_trabajo_crear():
    u = session.get('user_id') or session.get('id_codigo_consumidor')
    if not u:
        return jsonify({'success': False, 'message': 'No autenticado'}), 401
    payload = request.get_json(silent=True) or {}
    conn = get_db_connection()
    if conn is None:
        return jsonify({'success': False, 'message': 'BD no disponible'}), 500
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT nombre, cargo, recurso_operativo_cedula, super, cliente, ciudad
            FROM recurso_operativo
            WHERE id_codigo_consumidor = %s AND estado = 'Activo'
        """, (u,))
        ro = cur.fetchone() or {}
        hoy = get_bogota_datetime().date()
        fin = _fecha_finalizacion_domingo(hoy)
        cur.execute("""
            SELECT id_sgis_permiso_trabajo
            FROM sgis_permiso_trabajo
            WHERE id_codigo_consumidor = %s AND sgis_permiso_trabajo_fecha_emision = %s AND sgis_permiso_trabajo_fecha_finalizacion = %s
        """, (u, hoy, fin))
        existing = cur.fetchone()
        def _tri(v):
            if v is None:
                return None
            s = str(v).strip().upper()
            if s in ('C','NC','NA','N.A','N/A'):
                return 'NA' if s in ('NA','N.A','N/A') else s
            return None
        def _yn(v):
            if v is None:
                return None
            s = str(v).strip().upper()
            if s in ('SI','NO'):
                return s
            return None
        def _ap(v):
            if v is None:
                return None
            s = str(v).strip().upper().replace(' ','_')
            if s in ('APLICA','NO_APLICA'):
                return s
            return None
        fields = {
            'id_codigo_consumidor': u,
            'sgis_permiso_trabajo_fecha_emision': hoy,
            'sgis_permiso_trabajo_fecha_finalizacion': fin,
            'sgis_permiso_trabajo_trabajadores': 1,
            'sgis_permiso_trabajo_emitido_por': ro.get('super'),
            'sgis_permiso_trabajo_proyecto': ro.get('cliente'),
            'sgis_permiso_trabajo_ciudad': ro.get('ciudad'),
            'sgis_permiso_trabajo_responsable_trabajo': ro.get('nombre'),
            'sgis_permiso_trabajo_cargo': ro.get('cargo'),
            'nombre': ro.get('nombre'),
            'cargo': ro.get('cargo'),
            'cedula': ro.get('recurso_operativo_cedula'),
            'recurso_operativo_cedula': ro.get('recurso_operativo_cedula'),
            'sgis_permiso_trabajo_trabajo_ejecutar': payload.get('sgis_permiso_trabajo_trabajo_ejecutar'),
            'sgis_permiso_trabajo_descripcion_tarea': payload.get('sgis_permiso_trabajo_descripcion_tarea'),
            'sgis_permiso_trabajo_herramienta': payload.get('sgis_permiso_trabajo_herramienta'),
            'sgis_permiso_trabajo_herramienta_electrica': _tri(payload.get('sgis_permiso_trabajo_herramienta_electrica')),
            'sgis_permiso_trabajo_herramienta_manual': _tri(payload.get('sgis_permiso_trabajo_herramienta_manual')),
            'sgis_permiso_trabajo_equipos_alturas': _tri(payload.get('sgis_permiso_trabajo_equipos_alturas')),
            'sgis_permiso_trabajo_otros_herramientas': payload.get('sgis_permiso_trabajo_otros_herramientas'),
            'sgis_permiso_trabajo_iluminacion': _tri(payload.get('sgis_permiso_trabajo_iluminacion')),
            'sgis_permiso_trabajo_animales': _tri(payload.get('sgis_permiso_trabajo_animales')),
            'sgis_permiso_trabajo_izaje_alturas': _tri(payload.get('sgis_permiso_trabajo_izaje_alturas')),
            'sgis_permiso_trabajo_obstaculos_evacuacion': _tri(payload.get('sgis_permiso_trabajo_obstaculos_evacuacion')),
            'sgis_permiso_trabajo_vehiculos_area': _tri(payload.get('sgis_permiso_trabajo_vehiculos_area')),
            'sgis_permiso_trabajo_trabajo_alturas': _tri(payload.get('sgis_permiso_trabajo_trabajo_alturas')),
            'sgis_permiso_trabajo_trabajo_piso_humedo': _tri(payload.get('sgis_permiso_trabajo_trabajo_piso_humedo')),
            'sgis_permiso_trabajo_manejo_energia_peligrosa': _tri(payload.get('sgis_permiso_trabajo_manejo_energia_peligrosa')),
            'sgis_permiso_trabajo_trabajo_manual': _tri(payload.get('sgis_permiso_trabajo_trabajo_manual')),
            'sgis_permiso_trabajo_caida_objetos': _tri(payload.get('sgis_permiso_trabajo_caida_objetos')),
            'sgis_permiso_trabajo_otros_area': payload.get('sgis_permiso_trabajo_otros_area'),
            'sgis_permiso_trabajo_proyeccion_particulas': _tri(payload.get('sgis_permiso_trabajo_proyeccion_particulas')),
            'sgis_permiso_trabajo_caidas_menor_2m': _tri(payload.get('sgis_permiso_trabajo_caidas_menor_2m')),
            'sgis_permiso_trabajo_caidas_mayor_2m': _tri(payload.get('sgis_permiso_trabajo_caidas_mayor_2m')),
            'sgis_permiso_trabajo_acceso_mal_estado': _tri(payload.get('sgis_permiso_trabajo_acceso_mal_estado')),
            'sgis_permiso_trabajo_levantamiento_carga_mecanica': _tri(payload.get('sgis_permiso_trabajo_levantamiento_carga_mecanica')),
            'sgis_permiso_trabajo_condicion_clima': _tri(payload.get('sgis_permiso_trabajo_condicion_clima')),
            'sgis_permiso_trabajo_clima': payload.get('sgis_permiso_trabajo_clima'),
            'sgis_permiso_trabajo_proxi_red_energizasa': _tri(payload.get('sgis_permiso_trabajo_proxi_red_energizasa')),
            'sgis_permiso_trabajo_proxi_red': payload.get('sgis_permiso_trabajo_proxi_red'),
            'sgis_permiso_trabajo_vibraciones': _tri(payload.get('sgis_permiso_trabajo_vibraciones')),
            'sgis_permiso_trabajo_contacto_electrico': _tri(payload.get('sgis_permiso_trabajo_contacto_electrico')),
            'sgis_permiso_trabajo_atrapamiento': _tri(payload.get('sgis_permiso_trabajo_atrapamiento')),
            'sgis_permiso_trabajo_cable_expuesto': _tri(payload.get('sgis_permiso_trabajo_cable_expuesto')),
            'sgis_permiso_trabajo_corte_no_visible': _tri(payload.get('sgis_permiso_trabajo_corte_no_visible')),
            'sgis_permiso_trabajo_atmosfera_explosiva': _tri(payload.get('sgis_permiso_trabajo_atmosfera_explosiva')),
            'sgis_permiso_trabajo_fuentes_ignicion': _tri(payload.get('sgis_permiso_trabajo_fuentes_ignicion')),
            'sgis_permiso_trabajo_vapores': _tri(payload.get('sgis_permiso_trabajo_vapores')),
            'sgis_permiso_trabajo_alta_temperatura': _tri(payload.get('sgis_permiso_trabajo_alta_temperatura')),
            'sgis_permiso_trabajo_baja_temperatura': _tri(payload.get('sgis_permiso_trabajo_baja_temperatura')),
            'sgis_permiso_trabajo_iluminacion_deficiente': _tri(payload.get('sgis_permiso_trabajo_iluminacion_deficiente')),
            'sgis_permiso_trabajo_quemaduras': _tri(payload.get('sgis_permiso_trabajo_quemaduras')),
            'sgis_permiso_trabajo_almacenamientos_quimicos': _tri(payload.get('sgis_permiso_trabajo_almacenamientos_quimicos')),
            'sgis_permiso_trabajo_extensiones_mal_estado': _tri(payload.get('sgis_permiso_trabajo_extensiones_mal_estado')),
            'sgis_permiso_trabajo_ruido': _tri(payload.get('sgis_permiso_trabajo_ruido')),
            'sgis_permiso_trabajo_contacto_directo_indirecto': _tri(payload.get('sgis_permiso_trabajo_contacto_directo_indirecto')),
            'sgis_permiso_trabajo_caida_objeto': _tri(payload.get('sgis_permiso_trabajo_caida_objeto')),
            'sgis_permiso_trabajo_espacio_reducido': _tri(payload.get('sgis_permiso_trabajo_espacio_reducido')),
            'sgis_permiso_trabajo_levantamiento_manual_cargas': _tri(payload.get('sgis_permiso_trabajo_levantamiento_manual_cargas')),
            'sgis_permiso_trabajo_subestacion_inundada': _tri(payload.get('sgis_permiso_trabajo_subestacion_inundada')),
            'sgis_permiso_trabajo_excavaciones': _tri(payload.get('sgis_permiso_trabajo_excavaciones')),
            'sgis_permiso_trabajo_otros': payload.get('sgis_permiso_trabajo_otros'),
            'sgis_permiso_trabajo_calzado_dielectrico': _tri(payload.get('sgis_permiso_trabajo_calzado_dielectrico')),
            'sgis_permiso_trabajo_guantes_nitrilo': _tri(payload.get('sgis_permiso_trabajo_guantes_nitrilo')),
            'sgis_permiso_trabajo_guantes_vaqueta': _tri(payload.get('sgis_permiso_trabajo_guantes_vaqueta')),
            'sgis_permiso_trabajo_gafas_proteccion': _tri(payload.get('sgis_permiso_trabajo_gafas_proteccion')),
            'sgis_permiso_trabajo_casco_dielectrico': _tri(payload.get('sgis_permiso_trabajo_casco_dielectrico')),
            'sgis_permiso_trabajo_tie_off': _tri(payload.get('sgis_permiso_trabajo_tie_off')),
            'sgis_permiso_trabajo_mosqueton': _tri(payload.get('sgis_permiso_trabajo_mosqueton')),
            'sgis_permiso_trabajo_eslinga': _tri(payload.get('sgis_permiso_trabajo_eslinga')),
            'sgis_permiso_trabajo_arrestador': _tri(payload.get('sgis_permiso_trabajo_arrestador')),
            'sgis_permiso_trabajo_arnes': _tri(payload.get('sgis_permiso_trabajo_arnes')),
            'sgis_permiso_trabajo_linea_vida': _tri(payload.get('sgis_permiso_trabajo_linea_vida')),
            'sgis_permiso_trabajo_escalera_tijera': _tri(payload.get('sgis_permiso_trabajo_escalera_tijera')),
            'sgis_permiso_trabajo_escalera_extensible': _tri(payload.get('sgis_permiso_trabajo_escalera_extensible')),
            'sgis_permiso_trabajo_cinta_precaucion': _tri(payload.get('sgis_permiso_trabajo_cinta_precaucion')),
            'sgis_permiso_trabajo_conos': _tri(payload.get('sgis_permiso_trabajo_conos')),
            'sgis_permiso_trabajo_botiquin': _tri(payload.get('sgis_permiso_trabajo_botiquin')),
            'sgis_permiso_trabajo_notificacion_trabajo': _yn(payload.get('sgis_permiso_trabajo_notificacion_trabajo')),
            'sgis_permiso_trabajo_responsabilidades_permiso': _yn(payload.get('sgis_permiso_trabajo_responsabilidades_permiso')),
            'sgis_permiso_trabajo_condicion_interrupcion': _yn(payload.get('sgis_permiso_trabajo_condicion_interrupcion')),
            'sgis_permiso_trabajo_cambios_seguridad_trabajo': _yn(payload.get('sgis_permiso_trabajo_cambios_seguridad_trabajo')),
            'sgis_permiso_trabajo_induccion_seguridad': _yn(payload.get('sgis_permiso_trabajo_induccion_seguridad')),
            'sgis_permiso_trabajo_capacitacion_tema': _yn(payload.get('sgis_permiso_trabajo_capacitacion_tema')),
            'sgis_permiso_trabajo_metodos_inspeccion': _yn(payload.get('sgis_permiso_trabajo_metodos_inspeccion')),
            'sgis_permiso_trabajo_responsables_area': _yn(payload.get('sgis_permiso_trabajo_responsables_area')),
            'sgis_permiso_trabajo_mecanismo_control_riesgo': _yn(payload.get('sgis_permiso_trabajo_mecanismo_control_riesgo')),
            'sgis_permiso_trabajo_alarmas_puntos_reunion': _yn(payload.get('sgis_permiso_trabajo_alarmas_puntos_reunion')),
            'sgis_permiso_trabajo_ubicacion_equipos_incendio': _yn(payload.get('sgis_permiso_trabajo_ubicacion_equipos_incendio')),
            'sgis_permiso_trabajo_riesgos_trabajo_area': _yn(payload.get('sgis_permiso_trabajo_riesgos_trabajo_area')),
            'sgis_permiso_trabajo_impacto_ambiental': _yn(payload.get('sgis_permiso_trabajo_impacto_ambiental')),
            'sgis_permiso_trabajo_ats': _tri(payload.get('sgis_permiso_trabajo_ats')),
            'sgis_permiso_trabajo_inspecciones_relizadas': _tri(payload.get('sgis_permiso_trabajo_inspecciones_relizadas')),
            'sgis_permiso_trabajo_procedimientos_trabajo': _tri(payload.get('sgis_permiso_trabajo_procedimientos_trabajo')),
            'sgis_permiso_trabajo_arl_afp_eps': _tri(payload.get('sgis_permiso_trabajo_arl_afp_eps')),
            'sgis_permiso_trabajo_confinado_aplica': _ap(payload.get('sgis_permiso_trabajo_confinado_aplica')),
            'sgis_permiso_trabajo_altura_aplica': _ap(payload.get('sgis_permiso_trabajo_altura_aplica'))
        }
        cols = ",".join(fields.keys())
        vals = tuple(fields.values())
        if existing:
            pid = existing['id_sgis_permiso_trabajo']
            set_stmt = ",".join([f"{k}=%s" for k in fields.keys()])
            cur.execute(f"UPDATE sgis_permiso_trabajo SET {set_stmt}, updated_at=NOW() WHERE id_sgis_permiso_trabajo=%s", vals + (pid,))
            conn.commit()
            return jsonify({'success': True, 'id_sgis_permiso_trabajo': pid, 'message': 'Actualizado'}), 200
        cur.execute(f"INSERT INTO sgis_permiso_trabajo ({cols}) VALUES ({','.join(['%s']*len(fields))})", vals)
        conn.commit()
        pid = cur.lastrowid
        return jsonify({'success': True, 'id_sgis_permiso_trabajo': pid, 'message': 'Creado'}), 201
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        try:
            cur.close(); conn.close()
        except Exception:
            pass

@app.route('/api/sgis/permiso-trabajo/current', methods=['GET'])
@login_required
def api_sgis_permiso_trabajo_actual():
    u = session.get('user_id') or session.get('id_codigo_consumidor')
    if not u:
        return jsonify({'success': False, 'message': 'No autenticado'}), 401
    conn = get_db_connection()
    if conn is None:
        return jsonify({'success': False, 'message': 'BD no disponible'}), 500
    try:
        cur = conn.cursor(dictionary=True)
        hoy = get_bogota_datetime().date()
        fin = _fecha_finalizacion_domingo(hoy)
        cur.execute("""
            SELECT * FROM sgis_permiso_trabajo
            WHERE id_codigo_consumidor=%s AND sgis_permiso_trabajo_fecha_emision=%s AND sgis_permiso_trabajo_fecha_finalizacion=%s
        """, (u, hoy, fin))
        row = cur.fetchone()
        if not row:
            cur.execute(
                """
                SELECT nombre, cargo, recurso_operativo_cedula, super, cliente, ciudad
                FROM recurso_operativo
                WHERE id_codigo_consumidor = %s AND estado = 'Activo'
                """,
                (u,)
            )
            ro = cur.fetchone() or {}
            row = {
                'sgis_permiso_trabajo_emitido_por': ro.get('super'),
                'sgis_permiso_trabajo_proyecto': ro.get('cliente'),
                'sgis_permiso_trabajo_ciudad': ro.get('ciudad'),
                'sgis_permiso_trabajo_responsable_trabajo': ro.get('nombre'),
                'sgis_permiso_trabajo_cargo': ro.get('cargo'),
                'recurso_operativo_cedula': ro.get('recurso_operativo_cedula'),
                'nombre': ro.get('nombre'),
                'cargo': ro.get('cargo'),
                'cedula': ro.get('recurso_operativo_cedula')
            }
        return jsonify({'success': True, 'data': row})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        try:
            cur.close(); conn.close()
        except Exception:
            pass

@app.route('/api/sgis/permiso-trabajo/historial/confinado', methods=['POST','GET'])
@login_required
def api_sgis_historial_confinado():
    u = session.get('user_id') or session.get('id_codigo_consumidor')
    if not u:
        return jsonify({'success': False, 'message': 'No autenticado'}), 401
    conn = get_db_connection()
    if conn is None:
        return jsonify({'success': False, 'message': 'BD no disponible'}), 500
    try:
        cur = conn.cursor(dictionary=True)
        if request.method == 'GET':
            pid = request.args.get('id_sgis_permiso_trabajo', type=int)
            if not pid:
                return jsonify({'success': False, 'message': 'id_sgis_permiso_trabajo requerido'}), 400
            cur.execute("""SELECT * FROM sgis_permiso_trabajo_historial_semanal_confinado WHERE id_sgis_permiso_trabajo=%s ORDER BY sgis_permiso_trabajo_historial_confinado_fecha ASC""", (pid,))
            rows = cur.fetchall()
            return jsonify({'success': True, 'data': rows})
        data = request.get_json(silent=True) or {}
        pid = data.get('id_sgis_permiso_trabajo')
        if not pid:
            return jsonify({'success': False, 'message': 'id_sgis_permiso_trabajo requerido'}), 400
        fecha = data.get('sgis_permiso_trabajo_historial_confinado_fecha') or get_bogota_datetime().date()
        cols = [
            'id_sgis_permiso_trabajo','id_codigo_consumidor','sgis_permiso_trabajo_historial_confinado_1','sgis_permiso_trabajo_historial_confinado_2','sgis_permiso_trabajo_historial_confinado_3','sgis_permiso_trabajo_historial_confinado_4','sgis_permiso_trabajo_historial_confinado_5','sgis_permiso_trabajo_historial_confinado_6','sgis_permiso_trabajo_historial_confinado_7','sgis_permiso_trabajo_historial_confinado_8','sgis_permiso_trabajo_historial_confinado_9','sgis_permiso_trabajo_historial_confinado_10','sgis_permiso_trabajo_historial_confinado_11','sgis_permiso_trabajo_historial_confinado_fecha','sgis_permiso_trabajo_historial_confinado_firma_tecnico','sgis_permiso_trabajo_historial_confinado_firma_supervisor'
        ]
        vals = [
            pid, u,
            data.get('sgis_permiso_trabajo_historial_confinado_1'),
            data.get('sgis_permiso_trabajo_historial_confinado_2'),
            data.get('sgis_permiso_trabajo_historial_confinado_3'),
            data.get('sgis_permiso_trabajo_historial_confinado_4'),
            data.get('sgis_permiso_trabajo_historial_confinado_5'),
            data.get('sgis_permiso_trabajo_historial_confinado_6'),
            data.get('sgis_permiso_trabajo_historial_confinado_7'),
            data.get('sgis_permiso_trabajo_historial_confinado_8'),
            data.get('sgis_permiso_trabajo_historial_confinado_9'),
            data.get('sgis_permiso_trabajo_historial_confinado_10'),
            data.get('sgis_permiso_trabajo_historial_confinado_11'),
            fecha,
            data.get('sgis_permiso_trabajo_historial_confinado_firma_tecnico'),
            data.get('sgis_permiso_trabajo_historial_confinado_firma_supervisor')
        ]
        cur.execute(f"INSERT INTO sgis_permiso_trabajo_historial_semanal_confinado ({','.join(cols)}) VALUES ({','.join(['%s']*len(cols))})", tuple(vals))
        conn.commit()
        return jsonify({'success': True}), 201
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        try:
            cur.close(); conn.close()
        except Exception:
            pass

@app.route('/api/sgis/permiso-trabajo/historial/alturas', methods=['POST','GET'])
@login_required
def api_sgis_historial_alturas():
    u = session.get('user_id') or session.get('id_codigo_consumidor')
    if not u:
        return jsonify({'success': False, 'message': 'No autenticado'}), 401
    conn = get_db_connection()
    if conn is None:
        return jsonify({'success': False, 'message': 'BD no disponible'}), 500
    try:
        cur = conn.cursor(dictionary=True)
        if request.method == 'GET':
            pid = request.args.get('id_sgis_permiso_trabajo', type=int)
            if not pid:
                return jsonify({'success': False, 'message': 'id_sgis_permiso_trabajo requerido'}), 400
            cur.execute("""SELECT * FROM sgis_permiso_trabajo_historial_semanal_altura WHERE id_sgis_permiso_trabajo=%s ORDER BY sgis_permiso_trabajo_historial_altura_fecha ASC""", (pid,))
            rows = cur.fetchall()
            return jsonify({'success': True, 'data': rows})
        data = request.get_json(silent=True) or {}
        pid = data.get('id_sgis_permiso_trabajo')
        if not pid:
            return jsonify({'success': False, 'message': 'id_sgis_permiso_trabajo requerido'}), 400
        fecha = data.get('sgis_permiso_trabajo_historial_altura_fecha') or get_bogota_datetime().date()
        cols = [
            'id_sgis_permiso_trabajo','id_codigo_consumidor','sgis_permiso_trabajo_historial_altura_1','sgis_permiso_trabajo_historial_altura_2','sgis_permiso_trabajo_historial_altura_3','sgis_permiso_trabajo_historial_altura_4','sgis_permiso_trabajo_historial_altura_5','sgis_permiso_trabajo_historial_altura_6','sgis_permiso_trabajo_historial_altura_7','sgis_permiso_trabajo_historial_altura_8','sgis_permiso_trabajo_historial_altura_9','sgis_permiso_trabajo_historial_altura_10','sgis_permiso_trabajo_historial_altura_11','sgis_permiso_trabajo_historial_altura_12','sgis_permiso_trabajo_historial_altura_13','sgis_permiso_trabajo_historial_altura_14','sgis_permiso_trabajo_historial_altura_15','sgis_permiso_trabajo_historial_altura_16','sgis_permiso_trabajo_historial_altura_17','sgis_permiso_trabajo_historial_altura_18','sgis_permiso_trabajo_historial_altura_19','sgis_permiso_trabajo_historial_altura_20','sgis_permiso_trabajo_historial_altura_21','sgis_permiso_trabajo_historial_altura_22','sgis_permiso_trabajo_historial_altura_23','sgis_permiso_trabajo_historial_altura_24','sgis_permiso_trabajo_historial_altura_fecha','sgis_permiso_trabajo_historial_semanal_altura_firma_tecnico','sgis_permiso_trabajo_historial_semanal_altura_firma_supervisor'
        ]
        vals = [
            pid, u,
            data.get('sgis_permiso_trabajo_historial_altura_1'),
            data.get('sgis_permiso_trabajo_historial_altura_2'),
            data.get('sgis_permiso_trabajo_historial_altura_3'),
            data.get('sgis_permiso_trabajo_historial_altura_4'),
            data.get('sgis_permiso_trabajo_historial_altura_5'),
            data.get('sgis_permiso_trabajo_historial_altura_6'),
            data.get('sgis_permiso_trabajo_historial_altura_7'),
            data.get('sgis_permiso_trabajo_historial_altura_8'),
            data.get('sgis_permiso_trabajo_historial_altura_9'),
            data.get('sgis_permiso_trabajo_historial_altura_10'),
            data.get('sgis_permiso_trabajo_historial_altura_11'),
            data.get('sgis_permiso_trabajo_historial_altura_12'),
            data.get('sgis_permiso_trabajo_historial_altura_13'),
            data.get('sgis_permiso_trabajo_historial_altura_14'),
            data.get('sgis_permiso_trabajo_historial_altura_15'),
            data.get('sgis_permiso_trabajo_historial_altura_16'),
            data.get('sgis_permiso_trabajo_historial_altura_17'),
            data.get('sgis_permiso_trabajo_historial_altura_18'),
            data.get('sgis_permiso_trabajo_historial_altura_19'),
            data.get('sgis_permiso_trabajo_historial_altura_20'),
            data.get('sgis_permiso_trabajo_historial_altura_21'),
            data.get('sgis_permiso_trabajo_historial_altura_22'),
            data.get('sgis_permiso_trabajo_historial_altura_23'),
            data.get('sgis_permiso_trabajo_historial_altura_24'),
            fecha,
            data.get('sgis_permiso_trabajo_historial_semanal_altura_firma_tecnico'),
            data.get('sgis_permiso_trabajo_historial_semanal_altura_firma_supervisor')
        ]
        cur.execute(f"INSERT INTO sgis_permiso_trabajo_historial_semanal_altura ({','.join(cols)}) VALUES ({','.join(['%s']*len(cols))})", tuple(vals))
        conn.commit()
        return jsonify({'success': True}), 201
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        try:
            cur.close(); conn.close()
        except Exception:
            pass

if __name__ == '__main__':
    print(f"🚀 Iniciando servidor Flask...")
    print(f"📋 Total de rutas registradas: {len(list(app.url_map.iter_rules()))}")
    
    # Verificar rutas específicas
    test_routes = []
    preoperacional_routes = []
    
    for rule in app.url_map.iter_rules():
        if 'test' in rule.rule:
            test_routes.append(f"   🔗 {rule.rule} -> {rule.endpoint}")
        if 'preoperacional' in rule.rule:
            preoperacional_routes.append(f"   🔗 {rule.rule} -> {rule.endpoint}")
    
    print(f"🧪 Rutas de test: {len(test_routes)}")
    for route in test_routes:
        print(route)
        
    print(f"🎯 Rutas de preoperacional: {len(preoperacional_routes)}")
    for route in preoperacional_routes:
        print(route)
    
    app.run(debug=True, host='0.0.0.0', port=8080)
