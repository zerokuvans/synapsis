import os
import json
import logging
import re
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import request, jsonify, render_template, session, redirect, url_for, current_app

from app import get_db_connection  # Reusar utilidades existentes


def ensure_avisos_tables():
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS avisos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(255),
                mensaje TEXT,
                imagen_url VARCHAR(512),
                activo TINYINT(1) DEFAULT 1,
                fecha_inicio DATETIME NULL,
                fecha_fin DATETIME NULL,
                creado_por VARCHAR(64),
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        conn.commit()
    except Exception as e:
        try:
            current_app.logger.error(f"Error creando tabla avisos: {e}")
        except Exception:
            logging.error(f"Error creando tabla avisos: {e}")
    finally:
        try:
            cur.close()
            if conn.is_connected():
                conn.close()
        except Exception:
            pass


def _is_admin():
    # Intentar usar Flask-Login si existe, si no usar sesión
    try:
        from flask_login import current_user  # type: ignore
        if getattr(current_user, 'is_authenticated', False) and getattr(current_user, 'has_role', lambda r: False)('administrativo'):
            return True
    except Exception:
        pass
    return session.get('user_role') == 'administrativo'


def save_uploaded_file(file_storage):
    base_dir = os.path.join('static', 'uploads', 'avisos')
    os.makedirs(base_dir, exist_ok=True)
    filename = secure_filename(getattr(file_storage, 'filename', '') or 'imagen')
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    final_name = f"aviso_{timestamp}{ext or '.bin'}"
    path = os.path.join(base_dir, final_name)
    file_storage.save(path)
    return '/' + path.replace('\\', '/')


def _normalize_datetime(dt_str):
    """Convierte valores provenientes de inputs datetime-local a 'YYYY-MM-DD HH:MM:SS'.
    Retorna None si no puede convertir.
    """
    if not dt_str:
        return None
    s = str(dt_str).strip()
    try:
        # Soportar ISO con 'T' y posibles zonas horarias
        iso = s.replace('Z', '+00:00')
        dt = datetime.fromisoformat(iso)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        try:
            s2 = s.replace('T', ' ')
            # Quitar zona horaria si viene tipo '+00:00'
            s2 = re.split(r"[+-]\d{2}:?\d{2}$", s2)[0]
            # Agregar segundos si faltan
            if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$', s2):
                return s2 + ':00'
            if re.match(r'^\d{4}-\d{2}-\d{2}$', s2):
                return s2 + ' 00:00:00'
        except Exception:
            pass
    return None

def _parse_activo(value):
    try:
        if value is None:
            return 1
        v = str(value).strip().lower()
        if v in ('1', 'true', 'yes', 'si', 'on'):
            return 1
        if v in ('0', 'false', 'no', 'off'):
            return 0
        # valor inesperado: asumir activo
        return 1
    except Exception:
        return 1

def registrar_rutas_avisos(app):
    """Registrar rutas del módulo de Avisos"""

    ensure_avisos_tables()

    @app.route('/admin/avisos')
    def admin_avisos_page():
        if not _is_admin():
            return redirect(url_for('login'))
        return render_template('modulos/administrativo/avisos.html')

    @app.route('/api/avisos', methods=['GET'])
    def api_list_avisos():
        if not _is_admin():
            return jsonify({'success': False, 'message': 'No autorizado'}), 403
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión'}), 500
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id, titulo, mensaje, imagen_url, activo,
                       DATE_FORMAT(fecha_inicio, %s) AS fecha_inicio,
                       DATE_FORMAT(fecha_fin, %s) AS fecha_fin,
                       DATE_FORMAT(fecha_creacion, %s) AS fecha_creacion,
                       creado_por
                FROM avisos
                ORDER BY fecha_creacion DESC
                """,
                ('%Y-%m-%d %H:%i:%s', '%Y-%m-%d %H:%i:%s', '%Y-%m-%d %H:%i:%s')
            )
            rows = cur.fetchall()
            return jsonify({'success': True, 'avisos': rows})
        except Exception as e:
            try:
                current_app.logger.error(f"Error listando avisos: {e}")
            except Exception:
                logging.error(f"Error listando avisos: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            try:
                cur.close()
                if conn.is_connected():
                    conn.close()
            except Exception:
                pass

    @app.route('/api/avisos/<int:aviso_id>', methods=['DELETE'])
    def api_delete_aviso(aviso_id):
        if not _is_admin():
            return jsonify({'success': False, 'message': 'No autorizado'}), 403
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión'}), 500
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT imagen_url FROM avisos WHERE id = %s", (aviso_id,))
            row = cur.fetchone()
            if not row:
                return jsonify({'success': False, 'message': 'Aviso no encontrado'}), 404
            imagen_url = row.get('imagen_url')
            cur.close()

            cur = conn.cursor()
            cur.execute("DELETE FROM avisos WHERE id = %s", (aviso_id,))
            conn.commit()

            # Intentar eliminar el archivo asociado si pertenece a avisos
            if imagen_url:
                try:
                    rel = imagen_url.lstrip('/').replace('\\', '/')
                    if rel.startswith('static/uploads/avisos/'):
                        full_path = os.path.join(current_app.root_path, rel)
                        if os.path.exists(full_path):
                            os.remove(full_path)
                except Exception as fe:
                    try:
                        current_app.logger.warning(f"No se pudo eliminar archivo de aviso {imagen_url}: {fe}")
                    except Exception:
                        logging.warning(f"No se pudo eliminar archivo de aviso {imagen_url}: {fe}")

            return jsonify({'success': True, 'message': 'Aviso eliminado'})
        except Exception as e:
            try:
                current_app.logger.error(f"Error eliminando aviso: {e}")
            except Exception:
                logging.error(f"Error eliminando aviso: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            try:
                cur.close()
                if conn.is_connected():
                    conn.close()
            except Exception:
                pass

    @app.route('/api/avisos', methods=['POST'])
    def api_create_aviso():
        if not _is_admin():
            return jsonify({'success': False, 'message': 'No autorizado'}), 403
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión'}), 500
        try:
            titulo = request.form.get('titulo')
            mensaje = request.form.get('mensaje')
            activo = _parse_activo(request.form.get('activo'))
            fecha_inicio = _normalize_datetime(request.form.get('fecha_inicio'))
            fecha_fin = _normalize_datetime(request.form.get('fecha_fin'))
            imagen_url = None
            if 'imagen' in request.files and request.files['imagen']:
                imagen_url = save_uploaded_file(request.files['imagen'])
            creado_por = session.get('user_id') or session.get('id_codigo_consumidor')

            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO avisos (titulo, mensaje, imagen_url, activo, fecha_inicio, fecha_fin, creado_por)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (titulo, mensaje, imagen_url, activo, fecha_inicio, fecha_fin, creado_por)
            )
            conn.commit()
            return jsonify({'success': True, 'message': 'Aviso creado', 'id': cur.lastrowid})
        except Exception as e:
            try:
                current_app.logger.error(f"Error creando aviso: {e}")
            except Exception:
                logging.error(f"Error creando aviso: {e}")
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            try:
                cur.close()
                if conn.is_connected():
                    conn.close()
            except Exception:
                pass

    @app.route('/api/avisos/<int:aviso_id>', methods=['PATCH'])
    def api_update_aviso(aviso_id):
        if not _is_admin():
            return jsonify({'success': False, 'message': 'No autorizado'}), 403
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión'}), 500
        try:
            content_type = request.headers.get('Content-Type', '')
            campos = []
            valores = []

            if 'application/json' in content_type:
                data = request.get_json(silent=True) or {}
                if 'titulo' in data:
                    campos.append('titulo = %s')
                    valores.append(data.get('titulo'))
                if 'mensaje' in data:
                    campos.append('mensaje = %s')
                    valores.append(data.get('mensaje'))
                if 'activo' in data:
                    campos.append('activo = %s')
                    valores.append(1 if data.get('activo') else 0)
                if 'fecha_inicio' in data:
                    campos.append('fecha_inicio = %s')
                    valores.append(_normalize_datetime(data.get('fecha_inicio')))
                if 'fecha_fin' in data:
                    campos.append('fecha_fin = %s')
                    valores.append(_normalize_datetime(data.get('fecha_fin')))
            else:
                # multipart/form-data o application/x-www-form-urlencoded
                titulo = request.form.get('titulo')
                mensaje = request.form.get('mensaje')
                activo = request.form.get('activo')
                fecha_inicio = request.form.get('fecha_inicio')
                fecha_fin = request.form.get('fecha_fin')
                if titulo is not None:
                    campos.append('titulo = %s')
                    valores.append(titulo)
                if mensaje is not None:
                    campos.append('mensaje = %s')
                    valores.append(mensaje)
                if activo is not None:
                    campos.append('activo = %s')
                    valores.append(_parse_activo(activo))
                if fecha_inicio is not None:
                    campos.append('fecha_inicio = %s')
                    valores.append(_normalize_datetime(fecha_inicio))
                if fecha_fin is not None:
                    campos.append('fecha_fin = %s')
                    valores.append(_normalize_datetime(fecha_fin))
                # Imagen opcional: si viene archivo, reemplazar
                if 'imagen' in request.files and getattr(request.files['imagen'], 'filename', ''):
                    try:
                        imagen_url = save_uploaded_file(request.files['imagen'])
                        campos.append('imagen_url = %s')
                        valores.append(imagen_url)
                    except Exception as e:
                        try:
                            current_app.logger.warning(f"No se pudo guardar imagen en actualización de aviso {aviso_id}: {e}")
                        except Exception:
                            logging.warning(f"No se pudo guardar imagen en actualización de aviso {aviso_id}: {e}")
            if not campos:
                return jsonify({'success': False, 'message': 'Sin cambios'}), 400
            valores.append(aviso_id)
            cur = conn.cursor()
            cur.execute(f"UPDATE avisos SET {', '.join(campos)} WHERE id = %s", valores)
            conn.commit()
            return jsonify({'success': True, 'message': 'Aviso actualizado'})
        except Exception as e:
            try:
                current_app.logger.error(f"Error actualizando aviso: {e}")
            except Exception:
                logging.error(f"Error actualizando aviso: {e}")
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            try:
                cur.close()
                if conn.is_connected():
                    conn.close()
            except Exception:
                pass

    @app.route('/api/avisos/para-mi', methods=['GET'])
    def api_avisos_para_mi():
        # No requiere admin: muestra avisos activos para cualquier usuario autenticado
        usuario_id = session.get('user_id') or session.get('id_codigo_consumidor')
        if not usuario_id:
            return jsonify({'success': False, 'message': 'No autorizado'}), 401
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión'}), 500
        try:
            cur = conn.cursor(dictionary=True)
            # Avisos activos y dentro de la ventana de tiempo, o sin fechas
            cur.execute(
                """
                SELECT id, titulo, mensaje, imagen_url
                FROM avisos
                WHERE activo = 1
                  AND (fecha_inicio IS NULL OR fecha_inicio <= NOW())
                  AND (fecha_fin IS NULL OR fecha_fin >= NOW())
                ORDER BY fecha_inicio IS NULL ASC, fecha_inicio DESC, fecha_creacion DESC
                LIMIT 3
                """
            )
            rows = cur.fetchall()
            return jsonify({'success': True, 'avisos': rows})
        except Exception as e:
            try:
                current_app.logger.error(f"Error obteniendo avisos activos: {e}")
            except Exception:
                logging.error(f"Error obteniendo avisos activos: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            try:
                cur.close()
                if conn.is_connected():
                    conn.close()
            except Exception:
                pass