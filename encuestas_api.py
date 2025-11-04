#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de API para gestión de encuestas (tipo Google Forms)
Sistema - Capired
"""

import mysql.connector
from flask import jsonify, request, render_template, session, redirect, url_for, make_response
import os
from datetime import datetime
import json
import logging
from werkzeug.utils import secure_filename

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de base de datos (alineado con dotaciones_api)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
    'autocommit': True
}

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as e:
        logger.error(f"Error conectando a la base de datos: {e}")
        return None


def ensure_encuestas_tables():
    """Crear tablas necesarias para encuestas si no existen"""
    connection = get_db_connection()
    if not connection:
        logger.error("No se pudo conectar a la BD para crear tablas de encuestas")
        return False

    try:
        cursor = connection.cursor()

        # Tabla encuestas (cabecera)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS encuestas (
                id_encuesta INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(255) NOT NULL,
                descripcion TEXT NULL,
                estado ENUM('borrador','activa','cerrada') DEFAULT 'borrador',
                anonima TINYINT(1) DEFAULT 0,
                permitir_edicion_respuesta TINYINT(1) DEFAULT 0,
                visibilidad ENUM('privada','publica') DEFAULT 'privada',
                creado_por INT NULL,
                fecha_inicio DATETIME NULL,
                fecha_fin DATETIME NULL,
                fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # Asegurar columnas requeridas en instalaciones existentes usando comprobación explícita
        def column_exists(table, column):
            # table proviene de una lista interna; es seguro interpolarlo
            cursor.execute(f"SHOW COLUMNS FROM {table} LIKE %s", (column,))
            return cursor.fetchone() is not None

        # Lista de columnas requeridas con sus definiciones (conservadoras y compatibles)
        required_columns = [
            ("encuestas", "anonima", "TINYINT(1) DEFAULT 0"),
            ("encuestas", "permitir_edicion_respuesta", "TINYINT(1) DEFAULT 0"),
            ("encuestas", "visibilidad", "ENUM('privada','publica') DEFAULT 'privada'"),
            ("encuestas", "dirigida_a", "ENUM('todos','tecnicos','analistas','supervisores') DEFAULT 'todos'"),
            ("encuestas", "audiencia_carpetas", "TEXT NULL"),
            ("encuestas", "audiencia_supervisores", "TEXT NULL"),
            ("encuestas", "audiencia_tecnicos", "TEXT NULL"),
            ("encuestas", "creado_por", "INT NULL"),
            ("encuestas", "fecha_inicio", "DATETIME NULL"),
            ("encuestas", "fecha_fin", "DATETIME NULL"),
            ("encuestas", "fecha_actualizacion", "DATETIME NULL")
        ]

        for table, col, col_def in required_columns:
            try:
                if not column_exists(table, col):
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}")
            except mysql.connector.Error as e:
                logger.warning(f"No se pudo agregar columna {table}.{col}: {e}")

        # Tabla preguntas
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS encuesta_preguntas (
                id_pregunta INT AUTO_INCREMENT PRIMARY KEY,
                encuesta_id INT NOT NULL,
                tipo ENUM('texto','parrafo','numero','fecha','hora','opcion_multiple','seleccion_unica','checkbox','dropdown','imagen') NOT NULL,
                texto VARCHAR(500) NOT NULL,
                ayuda VARCHAR(500) NULL,
                requerida TINYINT(1) DEFAULT 0,
                orden INT DEFAULT 0,
                config_json JSON NULL,
                FOREIGN KEY (encuesta_id) REFERENCES encuestas(id_encuesta) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # Tabla opciones para preguntas de selección
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS encuesta_opciones (
                id_opcion INT AUTO_INCREMENT PRIMARY KEY,
                pregunta_id INT NOT NULL,
                texto VARCHAR(255) NOT NULL,
                valor VARCHAR(255) NULL,
                orden INT DEFAULT 0,
                FOREIGN KEY (pregunta_id) REFERENCES encuesta_preguntas(id_pregunta) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # Tabla respuestas (cabecera)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS encuesta_respuestas (
                id_respuesta INT AUTO_INCREMENT PRIMARY KEY,
                encuesta_id INT NOT NULL,
                usuario_id INT NULL,
                token_unico VARCHAR(64) NULL,
                estado ENUM('borrador','enviada') DEFAULT 'enviada',
                fecha_respuesta DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                duracion_segundos INT NULL,
                ip VARCHAR(64) NULL,
                user_agent VARCHAR(255) NULL,
                FOREIGN KEY (encuesta_id) REFERENCES encuestas(id_encuesta) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # Tabla detalles de respuestas
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS encuesta_respuestas_detalle (
                id_detalle INT AUTO_INCREMENT PRIMARY KEY,
                respuesta_id INT NOT NULL,
                pregunta_id INT NOT NULL,
                valor_texto TEXT NULL,
                valor_numero DECIMAL(18,6) NULL,
                valor_json JSON NULL,
                opcion_id INT NULL,
                archivo_url VARCHAR(500) NULL,
                FOREIGN KEY (respuesta_id) REFERENCES encuesta_respuestas(id_respuesta) ON DELETE CASCADE,
                FOREIGN KEY (pregunta_id) REFERENCES encuesta_preguntas(id_pregunta) ON DELETE CASCADE,
                FOREIGN KEY (opcion_id) REFERENCES encuesta_opciones(id_opcion) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # Asegurar que el ENUM incluya 'imagen' en instalaciones existentes
        try:
            cursor.execute(
                """
                ALTER TABLE encuesta_preguntas
                MODIFY COLUMN tipo ENUM('texto','parrafo','numero','fecha','hora','opcion_multiple','seleccion_unica','checkbox','dropdown','imagen') NOT NULL
                """
            )
        except mysql.connector.Error as e:
            logger.warning(f"No se modificó ENUM de encuesta_preguntas.tipo (posiblemente ya actualizado): {e}")

        connection.commit()
        cursor.close()
        logger.info("Tablas de encuestas verificadas/creadas correctamente")
        return True
    except mysql.connector.Error as e:
        logger.error(f"Error creando tablas de encuestas: {e}")
        return False
    finally:
        connection.close()


def registrar_rutas_encuestas(app):
    """Registrar rutas del módulo de encuestas"""

    # Asegurar tablas al registrar el módulo
    ensure_encuestas_tables()

    def _is_authenticated():
        """Verifica si el usuario está autenticado.
        Prioriza Flask-Login si está disponible; de lo contrario, usa claves de sesión.
        """
        try:
            # Evitar fallo si flask_login no está configurado
            from flask_login import current_user  # type: ignore
            if getattr(current_user, 'is_authenticated', False):
                return True
        except Exception:
            pass
        return bool(session.get('user_id') or session.get('id_codigo_consumidor'))

    @app.route('/lider/encuestas')
    def encuestas_page():
        try:
            if not _is_authenticated():
                # Redirigir a login si el usuario no está autenticado
                return redirect(url_for('auth.login')) if 'auth' in app.blueprints else redirect('/login')
            return render_template('modulos/lider/encuestas.html')
        except Exception as e:
            logger.error(f"Error cargando página de encuestas: {e}")
            return f"<h1>Error interno del servidor: {e}</h1>", 500

    @app.route('/lider/encuestas/<int:encuesta_id>/preview')
    def encuestas_preview_page(encuesta_id):
        try:
            if not _is_authenticated():
                return redirect(url_for('auth.login')) if 'auth' in app.blueprints else redirect('/login')
            return render_template('modulos/lider/encuesta_preview.html', encuesta_id=encuesta_id)
        except Exception as e:
            logger.error(f"Error cargando previsualización: {e}")
            return f"<h1>Error interno del servidor: {e}</h1>", 500

    @app.route('/lider/encuestas/<int:encuesta_id>/respuestas')
    def encuestas_respuestas_page(encuesta_id):
        try:
            if not _is_authenticated():
                return redirect(url_for('auth.login')) if 'auth' in app.blueprints else redirect('/login')
            return render_template('modulos/lider/encuesta_respuestas.html', encuesta_id=encuesta_id)
        except Exception as e:
            logger.error(f"Error cargando respuestas: {e}")
            return f"<h1>Error interno del servidor: {e}</h1>", 500

    @app.route('/api/encuestas', methods=['GET'])
    def listar_encuestas():
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor(dictionary=True)
            user_id = session.get('user_id') or session.get('id_codigo_consumidor')
            logger.info(f"[encuestas] listar_encuestas session.user_id={user_id} (alt id_codigo_consumidor)")
            if not user_id:
                # Si no hay usuario en sesión, devolver no autorizado para API
                return jsonify({'success': False, 'message': 'No autorizado'}), 401
            cursor.execute(
                """
                SELECT id_encuesta, titulo, descripcion, estado, anonima, visibilidad,
                       DATE_FORMAT(fecha_inicio, %s) AS fecha_inicio,
                       DATE_FORMAT(fecha_fin, %s) AS fecha_fin,
                       DATE_FORMAT(fecha_creacion, %s) AS fecha_creacion,
                       DATE_FORMAT(fecha_actualizacion, %s) AS fecha_actualizacion
                FROM encuestas
                WHERE creado_por = %s
                ORDER BY id_encuesta DESC
                """,
                ('%Y-%m-%d %H:%i:%s', '%Y-%m-%d %H:%i:%s', '%Y-%m-%d %H:%i:%s', '%Y-%m-%d %H:%i:%s', user_id)
            )
            encuestas = cursor.fetchall()
            return jsonify({'success': True, 'encuestas': encuestas, 'total': len(encuestas)})
        except mysql.connector.Error as e:
            logger.error(f"Error listando encuestas: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/encuestas', methods=['POST'])
    def crear_encuesta():
        data = request.get_json(silent=True) or {}
        titulo = data.get('titulo')
        descripcion = data.get('descripcion')
        estado = data.get('estado', 'borrador')
        anonima = 1 if data.get('anonima', False) else 0
        visibilidad = data.get('visibilidad', 'privada')
        dirigida_a = data.get('dirigida_a', 'todos')
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        # Carpetas de audiencia solo aplican a técnicos
        carpetas = data.get('audiencia_carpetas') or data.get('carpetas')
        if dirigida_a == 'tecnicos' and carpetas:
            try:
                audiencia_carpetas = json.dumps(carpetas, ensure_ascii=False)
            except Exception:
                audiencia_carpetas = None
        else:
            audiencia_carpetas = None
        # Supervisores de audiencia (para técnicos)
        supervisores_sel = data.get('audiencia_supervisores') or []
        if dirigida_a == 'tecnicos' and supervisores_sel:
            try:
                audiencia_supervisores = json.dumps(supervisores_sel, ensure_ascii=False)
            except Exception:
                audiencia_supervisores = None
        else:
            audiencia_supervisores = None
        # Técnicos de audiencia (IDs de recurso_operativo)
        tecnicos_sel = data.get('audiencia_tecnicos') or []
        if dirigida_a == 'tecnicos' and tecnicos_sel:
            try:
                audiencia_tecnicos = json.dumps(tecnicos_sel, ensure_ascii=False)
            except Exception:
                audiencia_tecnicos = None
        else:
            audiencia_tecnicos = None
        user_id = session.get('user_id') or session.get('id_codigo_consumidor')
        logger.info(f"[encuestas] crear_encuesta session.user_id={user_id} (alt id_codigo_consumidor) payload.titulo={titulo}")

        if not titulo:
            return jsonify({'success': False, 'message': 'El título es obligatorio'}), 400
        if not user_id:
            return jsonify({'success': False, 'message': 'No autorizado'}), 401

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO encuestas (
                    titulo, descripcion, estado, anonima, visibilidad, dirigida_a,
                    audiencia_carpetas, audiencia_supervisores, audiencia_tecnicos,
                    fecha_inicio, fecha_fin, creado_por
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    titulo, descripcion, estado, anonima, visibilidad, dirigida_a,
                    audiencia_carpetas, audiencia_supervisores, audiencia_tecnicos,
                    fecha_inicio, fecha_fin, user_id
                )
            )
            encuesta_id = cursor.lastrowid
            connection.commit()
            cursor.close()
            return jsonify({'success': True, 'id_encuesta': encuesta_id})
        except mysql.connector.Error as e:
            logger.error(f"Error creando encuesta: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    def _resolver_audiencias_usuario(conn, usuario_id):
        auds = set()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id_roles, UPPER(COALESCE(cargo, '')) AS cargo, 
                       COALESCE(super, 0) AS es_supervisor, COALESCE(analista, 0) AS es_analista
                FROM recurso_operativo
                WHERE id_codigo_consumidor = %s
                """,
                (usuario_id,)
            )
            row = cur.fetchone()
            if row:
                # Técnicos por id_roles == 2 o por rol de sesión
                rol_sesion = (session.get('user_role') or '').lower()
                if row.get('id_roles') == 2 or rol_sesion == 'tecnicos':
                    auds.add('tecnicos')
                # Analistas por flag o por cargo
                cargo = (row.get('cargo') or '').upper()
                if row.get('es_analista') in (1, True) or 'ANALISTA' in cargo:
                    auds.add('analistas')
                # Supervisores por flag o por cargo
                if row.get('es_supervisor') in (1, True) or 'SUPERVIS' in cargo:
                    auds.add('supervisores')
        except Exception as e:
            logger.warning(f"No se pudo resolver audiencia de usuario {usuario_id}: {e}")
        # Si no se pudo determinar, intentar inferir del rol de sesión
        rol_sesion = (session.get('user_role') or '').lower()
        if rol_sesion == 'tecnicos':
            auds.add('tecnicos')
        if rol_sesion == 'analistas':
            auds.add('analistas')
        if rol_sesion == 'lider':
            auds.add('supervisores')
        return list(auds) or []

    @app.route('/api/encuestas/activas/para-mi', methods=['GET'])
    def encuestas_activas_para_mi():
        usuario_id = session.get('user_id') or session.get('id_codigo_consumidor')
        if not usuario_id:
            return jsonify({'success': False, 'message': 'No autorizado'}), 401

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            auds = _resolver_audiencias_usuario(conn, usuario_id)
            # Siempre incluir 'todos' para que aplique a cualquier usuario
            valores = ['todos'] + auds
            if not valores:
                valores = ['todos']

            placeholders = ','.join(['%s'] * len(valores))
            cur = conn.cursor(dictionary=True)
            # Activas y dentro de ventana de fechas (o sin ventana)
            cur.execute(
                f"""
                SELECT id_encuesta, titulo, descripcion, dirigida_a, audiencia_carpetas, audiencia_supervisores, audiencia_tecnicos,
                       DATE_FORMAT(fecha_inicio, %s) AS fecha_inicio,
                       DATE_FORMAT(fecha_fin, %s) AS fecha_fin
                FROM encuestas
                WHERE estado = 'activa'
                  AND (fecha_inicio IS NULL OR fecha_inicio <= NOW())
                  AND (fecha_fin IS NULL OR fecha_fin >= NOW())
                  AND dirigida_a IN ({placeholders})
                  AND NOT EXISTS (
                        SELECT 1 FROM encuesta_respuestas r
                        WHERE r.encuesta_id = encuestas.id_encuesta
                          AND r.usuario_id = %s
                          AND r.estado = 'enviada'
                  )
                ORDER BY id_encuesta DESC
                LIMIT 5
                """,
                ['%Y-%m-%d %H:%i:%s', '%Y-%m-%d %H:%i:%s', *valores, usuario_id]
            )
            rows = cur.fetchall() or []

            # Obtener datos del usuario para filtrado fino cuando aplique
            carpeta_usuario = None
            supervisor_usuario = None
            try:
                cur.execute("SELECT carpeta, super FROM recurso_operativo WHERE id_codigo_consumidor = %s", (usuario_id,))
                r = cur.fetchone()
                carpeta_usuario = (r or {}).get('carpeta') if r else None
                supervisor_usuario = (r or {}).get('super') if r else None
            except Exception as e:
                logger.warning(f"No se pudo obtener carpeta de usuario {usuario_id}: {e}")

            # Filtrar por carpeta/supervisor/técnicos si la encuesta es para tecnicos
            filtradas = []
            for enc in rows:
                if enc.get('dirigida_a') == 'tecnicos':
                    pasa = True
                    # Filtro por carpetas (si está definido)
                    if enc.get('audiencia_carpetas'):
                        try:
                            lista = json.loads(enc.get('audiencia_carpetas'))
                            if lista and not carpeta_usuario:
                                pasa = False
                            elif isinstance(lista, list):
                                pasa = any((carpeta_usuario or '').strip().lower() == (c or '').strip().lower() for c in lista)
                        except Exception:
                            # JSON inválido: permitir por seguridad
                            pasa = True
                    # Filtro por supervisores (si está definido)
                    if pasa and enc.get('audiencia_supervisores'):
                        try:
                            sup_list = json.loads(enc.get('audiencia_supervisores'))
                            if sup_list and not supervisor_usuario:
                                pasa = False
                            elif isinstance(sup_list, list):
                                compara = (supervisor_usuario or '').strip().lower()
                                pasa = any((s or '').strip().lower() == compara for s in sup_list)
                        except Exception:
                            pasa = True
                    # Filtro por técnicos (si está definido). Se espera lista de IDs.
                    if pasa and enc.get('audiencia_tecnicos'):
                        try:
                            t_list = json.loads(enc.get('audiencia_tecnicos'))
                            if isinstance(t_list, list) and len(t_list) > 0:
                                # Si hay lista, debe estar el usuario actual
                                # Convertir a str para comparar sin tipo
                                pasa = str(usuario_id) in set(str(t) for t in t_list)
                        except Exception:
                            # Si hay problema con el JSON, no bloquear
                            pasa = True
                    if pasa:
                        filtradas.append(enc)
                else:
                    filtradas.append(enc)
            rows = filtradas

            return jsonify({'success': True, 'encuestas': rows, 'audiencias': auds, 'carpeta_usuario': carpeta_usuario, 'supervisor_usuario': supervisor_usuario})
        except mysql.connector.Error as e:
            logger.error(f"Error consultando encuestas activas para usuario: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            conn.close()

    @app.route('/api/recursos/carpetas', methods=['GET'])
    def listar_carpetas_recursos():
        """Lista de carpetas únicas de recurso_operativo para técnicos (id_roles=2) activos"""
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT DISTINCT carpeta 
                FROM recurso_operativo 
                WHERE carpeta IS NOT NULL AND carpeta <> '' AND id_roles = 2
                ORDER BY carpeta
                """
            )
            carpetas = [row[0] for row in cur.fetchall()]
            return jsonify({'success': True, 'carpetas': carpetas})
        except mysql.connector.Error as e:
            logger.error(f"Error listando carpetas: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            conn.close()

    @app.route('/api/encuestas/<int:encuesta_id>', methods=['GET'])
    def obtener_encuesta(encuesta_id):
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute("SELECT * FROM encuestas WHERE id_encuesta = %s", (encuesta_id,))
            encuesta = cursor.fetchone()
            if not encuesta:
                return jsonify({'success': False, 'message': 'Encuesta no encontrada'}), 404

            # Normalizar JSON de audiencia (si están como TEXT)
            try:
                if encuesta.get('audiencia_carpetas') and isinstance(encuesta.get('audiencia_carpetas'), str):
                    encuesta['audiencia_carpetas'] = json.loads(encuesta['audiencia_carpetas'])
            except Exception:
                pass
            try:
                if encuesta.get('audiencia_supervisores') and isinstance(encuesta.get('audiencia_supervisores'), str):
                    encuesta['audiencia_supervisores'] = json.loads(encuesta['audiencia_supervisores'])
            except Exception:
                pass
            try:
                if encuesta.get('audiencia_tecnicos') and isinstance(encuesta.get('audiencia_tecnicos'), str):
                    encuesta['audiencia_tecnicos'] = json.loads(encuesta['audiencia_tecnicos'])
            except Exception:
                pass

            # Formatear fechas a string serializable
            try:
                for k in ('fecha_inicio', 'fecha_fin', 'fecha_creacion', 'fecha_actualizacion'):
                    if encuesta.get(k) is not None and not isinstance(encuesta.get(k), str):
                        dt = encuesta.get(k)
                        try:
                            encuesta[k] = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except Exception:
                            encuesta[k] = str(dt)
            except Exception:
                pass

            cursor.execute("SELECT * FROM encuesta_preguntas WHERE encuesta_id = %s ORDER BY orden, id_pregunta", (encuesta_id,))
            preguntas = cursor.fetchall()

            # Obtener opciones por pregunta
            opciones_por_pregunta = {}
            if preguntas:
                pregunta_ids = [p['id_pregunta'] for p in preguntas]
                formato_in = ','.join(['%s'] * len(pregunta_ids))
                cursor.execute(f"SELECT * FROM encuesta_opciones WHERE pregunta_id IN ({formato_in}) ORDER BY orden, id_opcion", pregunta_ids)
                opciones = cursor.fetchall()
                for op in opciones:
                    opciones_por_pregunta.setdefault(op['pregunta_id'], []).append(op)

            # Convertir config_json a dict
            for p in preguntas:
                if p.get('config_json'):
                    try:
                        p['config'] = json.loads(p['config_json']) if isinstance(p['config_json'], str) else p['config_json']
                    except Exception:
                        p['config'] = None
                else:
                    p['config'] = None
                p['opciones'] = opciones_por_pregunta.get(p['id_pregunta'], [])

            encuesta['preguntas'] = preguntas
            # También exponemos preguntas en el nivel raíz para compatibilidad del frontend
            return jsonify({'success': True, 'encuesta': encuesta, 'preguntas': preguntas})
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo encuesta: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/encuestas/<int:encuesta_id>', methods=['PATCH'])
    def actualizar_encuesta(encuesta_id):
        data = request.get_json(silent=True) or {}
        campos = []
        valores = []
        # Campos permitidos de edición
        if 'titulo' in data:
            campos.append('titulo = %s')
            valores.append(data.get('titulo'))
        if 'descripcion' in data:
            campos.append('descripcion = %s')
            valores.append(data.get('descripcion'))
        if 'fecha_inicio' in data:
            campos.append('fecha_inicio = %s')
            valores.append(data.get('fecha_inicio') or None)
        if 'fecha_fin' in data:
            campos.append('fecha_fin = %s')
            valores.append(data.get('fecha_fin') or None)
        if 'visibilidad' in data:
            campos.append('visibilidad = %s')
            valores.append(data.get('visibilidad'))
        if 'anonima' in data:
            campos.append('anonima = %s')
            valores.append(1 if data.get('anonima') else 0)
        if 'dirigida_a' in data:
            dirigida_a = data.get('dirigida_a')
            campos.append('dirigida_a = %s')
            valores.append(dirigida_a)
            # Manejo de carpetas si cambia a tecnicos / otros
            carpetas = data.get('audiencia_carpetas') or data.get('carpetas')
            if dirigida_a == 'tecnicos' and carpetas:
                try:
                    aud_json = json.dumps(carpetas, ensure_ascii=False)
                except Exception:
                    aud_json = None
                campos.append('audiencia_carpetas = %s')
                valores.append(aud_json)
            elif dirigida_a != 'tecnicos':
                campos.append('audiencia_carpetas = NULL')
            # Manejo de supervisores si cambia a tecnicos / otros
            supervisores = data.get('audiencia_supervisores') or []
            if dirigida_a == 'tecnicos' and supervisores:
                try:
                    sup_json = json.dumps(supervisores, ensure_ascii=False)
                except Exception:
                    sup_json = None
                campos.append('audiencia_supervisores = %s')
                valores.append(sup_json)
            elif dirigida_a != 'tecnicos':
                campos.append('audiencia_supervisores = NULL')
            # Manejo de técnicos si cambia a tecnicos / otros
            tecnicos = data.get('audiencia_tecnicos') or []
            if dirigida_a == 'tecnicos' and tecnicos:
                try:
                    tec_json = json.dumps(tecnicos, ensure_ascii=False)
                except Exception:
                    tec_json = None
                campos.append('audiencia_tecnicos = %s')
                valores.append(tec_json)
            elif dirigida_a != 'tecnicos':
                campos.append('audiencia_tecnicos = NULL')
        else:
            # Si no se envía dirigida_a pero llegan carpetas explícitamente
            if 'audiencia_carpetas' in data or 'carpetas' in data:
                carpetas = data.get('audiencia_carpetas') or data.get('carpetas')
                try:
                    aud_json = json.dumps(carpetas, ensure_ascii=False) if carpetas else None
                except Exception:
                    aud_json = None
                campos.append('audiencia_carpetas = %s')
                valores.append(aud_json)
            # Actualización directa de supervisores
            if 'audiencia_supervisores' in data:
                supervisores = data.get('audiencia_supervisores') or []
                try:
                    sup_json = json.dumps(supervisores, ensure_ascii=False) if supervisores else None
                except Exception:
                    sup_json = None
                campos.append('audiencia_supervisores = %s')
                valores.append(sup_json)
            # Actualización directa de técnicos
            if 'audiencia_tecnicos' in data:
                tecnicos = data.get('audiencia_tecnicos') or []
                try:
                    tec_json = json.dumps(tecnicos, ensure_ascii=False) if tecnicos else None
                except Exception:
                    tec_json = None
                campos.append('audiencia_tecnicos = %s')
                valores.append(tec_json)

        # Manejo de estado (borrador/activa)
        if 'estado' in data:
            estado = (data.get('estado') or '').strip().lower()
            if estado not in ('borrador', 'activa'):
                return jsonify({'success': False, 'message': 'Estado inválido'}), 400
            campos.append('estado = %s')
            valores.append(estado)

        if not campos:
            return jsonify({'success': False, 'message': 'No hay campos para actualizar'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cur = connection.cursor()
            sql = f"UPDATE encuestas SET {', '.join(campos)}, fecha_actualizacion = NOW() WHERE id_encuesta = %s"
            valores.append(encuesta_id)
            cur.execute(sql, tuple(valores))
            affected = cur.rowcount
            connection.commit()
            cur.close()
            if affected == 0:
                return jsonify({'success': False, 'message': 'Encuesta no encontrada'}), 404
            return jsonify({'success': True})
        except mysql.connector.Error as e:
            logger.error(f"Error actualizando encuesta {encuesta_id}: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/encuestas/<int:encuesta_id>/preguntas', methods=['POST'])
    def crear_pregunta(encuesta_id):
        data = request.get_json(silent=True) or {}
        tipo = data.get('tipo')
        texto = data.get('texto')
        ayuda = data.get('ayuda')
        requerida = 1 if data.get('requerida', False) else 0
        orden = data.get('orden', 0)
        config = data.get('config')
        opciones = data.get('opciones', [])

        if not tipo or not texto:
            return jsonify({'success': False, 'message': 'Tipo y texto son obligatorios'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor()

            config_json = json.dumps(config, ensure_ascii=False) if config else None
            cursor.execute(
                """
                INSERT INTO encuesta_preguntas (encuesta_id, tipo, texto, ayuda, requerida, orden, config_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (encuesta_id, tipo, texto, ayuda, requerida, orden, config_json)
            )
            pregunta_id = cursor.lastrowid

            # Insertar opciones si aplica
            tipos_con_opciones = {'opcion_multiple', 'seleccion_unica', 'checkbox', 'dropdown'}
            if opciones and tipo in tipos_con_opciones:
                for idx, op in enumerate(opciones):
                    texto_op = (op.get('texto') or '').strip()
                    valor_op = op.get('valor')
                    if not texto_op:
                        texto_op = f"Opción {idx+1}"
                    cursor.execute(
                        """
                        INSERT INTO encuesta_opciones (pregunta_id, texto, valor, orden)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (pregunta_id, texto_op, valor_op, idx)
                    )

            connection.commit()
            cursor.close()
            return jsonify({'success': True, 'id_pregunta': pregunta_id})
        except mysql.connector.Error as e:
            logger.error(f"Error creando pregunta: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/encuestas/<int:encuesta_id>/preguntas/<int:pregunta_id>', methods=['DELETE'])
    def eliminar_pregunta(encuesta_id, pregunta_id):
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                DELETE FROM encuesta_preguntas
                WHERE id_pregunta = %s AND encuesta_id = %s
                """,
                (pregunta_id, encuesta_id)
            )
            affected = cursor.rowcount
            connection.commit()
            cursor.close()
            if affected == 0:
                return jsonify({'success': False, 'message': 'Pregunta no encontrada'}), 404
            return jsonify({'success': True})
        except mysql.connector.Error as e:
            logger.error(f"Error eliminando pregunta: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/encuestas/<int:encuesta_id>/preguntas/<int:pregunta_id>/orden', methods=['PATCH'])
    def actualizar_orden_pregunta(encuesta_id, pregunta_id):
        data = request.get_json(silent=True) or {}
        try:
            nuevo_orden = int(data.get('orden'))
        except (TypeError, ValueError):
            return jsonify({'success': False, 'message': 'Orden inválido'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE encuesta_preguntas SET orden = %s
                WHERE id_pregunta = %s AND encuesta_id = %s
                """,
                (nuevo_orden, pregunta_id, encuesta_id)
            )
            affected = cursor.rowcount
            connection.commit()
            cursor.close()
            if affected == 0:
                return jsonify({'success': False, 'message': 'Pregunta no encontrada'}), 404
            return jsonify({'success': True})
        except mysql.connector.Error as e:
            logger.error(f"Error actualizando orden de pregunta: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/encuestas/<int:encuesta_id>/preguntas/<int:pregunta_id>', methods=['PATCH'])
    def actualizar_pregunta(encuesta_id, pregunta_id):
        data = request.get_json(silent=True) or {}
        tipo = data.get('tipo')
        texto = data.get('texto')
        ayuda = data.get('ayuda')
        requerida = data.get('requerida')
        opciones = data.get('opciones')

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cur = connection.cursor()
            sets = []
            vals = []
            if tipo is not None:
                sets.append('tipo = %s')
                vals.append(tipo)
            if texto is not None:
                sets.append('texto = %s')
                vals.append(texto)
            if ayuda is not None:
                sets.append('ayuda = %s')
                vals.append(ayuda)
            if requerida is not None:
                sets.append('requerida = %s')
                vals.append(1 if requerida else 0)
            if sets:
                sql = f"UPDATE encuesta_preguntas SET {', '.join(sets)} WHERE id_pregunta = %s AND encuesta_id = %s"
                vals.extend([pregunta_id, encuesta_id])
                cur.execute(sql, tuple(vals))

            # Reemplazar opciones si se enviaron
            if opciones is not None:
                cur.execute(
                    "DELETE FROM encuesta_opciones WHERE pregunta_id = %s",
                    (pregunta_id,)
                )
                tipos_con_opciones = {'opcion_multiple', 'seleccion_unica', 'checkbox', 'dropdown'}
                if tipo is None:
                    # Si no se envió tipo, obtener el actual para decidir si insertar opciones
                    cur2 = connection.cursor()
                    cur2.execute("SELECT tipo FROM encuesta_preguntas WHERE id_pregunta = %s", (pregunta_id,))
                    row = cur2.fetchone()
                    cur2.close()
                    tipo_actual = (row[0] if row else None)
                else:
                    tipo_actual = tipo
                if tipo_actual in tipos_con_opciones:
                    for idx, op in enumerate(opciones or []):
                        texto_op = (op.get('texto') or '').strip()
                        valor_op = op.get('valor')
                        if not texto_op:
                            texto_op = f"Opción {idx+1}"
                        cur.execute(
                            """
                            INSERT INTO encuesta_opciones (pregunta_id, texto, valor, orden)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (pregunta_id, texto_op, valor_op, idx)
                        )

            connection.commit()
            cur.close()
            return jsonify({'success': True})
        except mysql.connector.Error as e:
            logger.error(f"Error actualizando pregunta {pregunta_id}: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/encuestas/<int:encuesta_id>/respuestas', methods=['POST'])
    def enviar_respuesta(encuesta_id):
        files = {}
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            try:
                raw = request.form.get('payload') or '{}'
                data = json.loads(raw)
            except Exception:
                return jsonify({'success': False, 'message': 'Payload inválido en formulario'}), 400
            files = request.files or {}
        else:
            data = request.get_json(silent=True) or {}
        usuario_id = data.get('usuario_id') or session.get('user_id') or session.get('id_codigo_consumidor')
        logger.info(f"[encuestas] enviar_respuesta encuesta_id={encuesta_id} usuario_id={usuario_id} (alt id_codigo_consumidor)")
        respuestas = data.get('respuestas', [])  # lista de objetos {pregunta_id, tipo, valor_texto|valor_numero|opcion_id|opcion_ids}

        if not isinstance(respuestas, list) or len(respuestas) == 0:
            return jsonify({'success': False, 'message': 'No hay respuestas a procesar'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor()

            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            user_agent = request.headers.get('User-Agent')

            # Validación de requeridos antes de crear cabecera
            cursor.execute(
                """
                SELECT id_pregunta, tipo, requerida, texto
                FROM encuesta_preguntas
                WHERE encuesta_id = %s
                """,
                (encuesta_id,)
            )
            preguntas = cursor.fetchall()
            # Indexar respuestas recibidas por pregunta
            resp_index = { r.get('pregunta_id'): r for r in respuestas if r.get('pregunta_id') }
            faltantes = []
            for (pid, tipo, requerida, texto) in preguntas:
                if not requerida:
                    continue
                r = resp_index.get(pid)
                ok = True
                if not r:
                    ok = False
                else:
                    if tipo in ('texto','parrafo','fecha','hora'):
                        ok = bool(r.get('valor_texto'))
                    elif tipo == 'numero':
                        ok = (r.get('valor_numero') is not None and r.get('valor_numero') != '')
                    elif tipo in ('seleccion_unica','dropdown'):
                        ok = (r.get('opcion_id') is not None and r.get('opcion_id') != '')
                    elif tipo in ('opcion_multiple','checkbox'):
                        ids = r.get('opcion_ids') or []
                        ok = isinstance(ids, list) and len(ids) > 0
                    elif tipo == 'imagen':
                        fkey = f"file_{pid}"
                        f = files.get(fkey)
                        ok = bool(f and getattr(f, 'filename', '')) or bool(r.get('archivo_url'))
                    else:
                        ok = bool(r.get('valor_texto'))
                if not ok:
                    faltantes.append(texto or f"Pregunta {pid}")

            if faltantes:
                return jsonify({
                    'success': False,
                    'message': 'Faltan respuestas requeridas',
                    'faltantes': faltantes
                }), 400

            # Crear cabecera de respuesta
            cursor.execute(
                """
                INSERT INTO encuesta_respuestas (encuesta_id, usuario_id, estado, ip, user_agent)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (encuesta_id, usuario_id, 'enviada', ip, user_agent)
            )
            respuesta_id = cursor.lastrowid

            # Insertar detalles
            def save_uploaded_file(file_storage, encuesta_id):
                base_dir = os.path.join('static', 'uploads', 'encuestas', str(encuesta_id))
                os.makedirs(base_dir, exist_ok=True)
                filename = secure_filename(getattr(file_storage, 'filename', '') or 'imagen')
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
                final_name = f"enc_{encuesta_id}_{timestamp}{ext or '.bin'}"
                path = os.path.join(base_dir, final_name)
                file_storage.save(path)
                return '/' + path.replace('\\', '/')

            for r in respuestas:
                pregunta_id = r.get('pregunta_id')
                tipo = r.get('tipo')

                if not pregunta_id:
                    continue

                # Manejo por tipo
                if tipo in ('texto', 'parrafo', 'fecha', 'hora'):
                    valor_texto = r.get('valor_texto')
                    cursor.execute(
                        """
                        INSERT INTO encuesta_respuestas_detalle (respuesta_id, pregunta_id, valor_texto)
                        VALUES (%s, %s, %s)
                        """,
                        (respuesta_id, pregunta_id, valor_texto)
                    )
                elif tipo == 'numero':
                    valor_numero = r.get('valor_numero')
                    cursor.execute(
                        """
                        INSERT INTO encuesta_respuestas_detalle (respuesta_id, pregunta_id, valor_numero)
                        VALUES (%s, %s, %s)
                        """,
                        (respuesta_id, pregunta_id, valor_numero)
                    )
                elif tipo in ('seleccion_unica', 'dropdown', 'checkbox', 'opcion_multiple'):
                    opcion_id = r.get('opcion_id')
                    opcion_ids = r.get('opcion_ids') or ([] if opcion_id is None else [opcion_id])
                    for oid in opcion_ids:
                        cursor.execute(
                            """
                            INSERT INTO encuesta_respuestas_detalle (respuesta_id, pregunta_id, opcion_id)
                            VALUES (%s, %s, %s)
                            """,
                            (respuesta_id, pregunta_id, oid)
                        )
                elif tipo == 'imagen':
                    fkey = f"file_{pregunta_id}"
                    f = files.get(fkey)
                    archivo_url = None
                    if f and getattr(f, 'filename', ''):
                        archivo_url = save_uploaded_file(f, encuesta_id)
                    else:
                        archivo_url = r.get('archivo_url')  # fallback por si envían URL
                    cursor.execute(
                        """
                        INSERT INTO encuesta_respuestas_detalle (respuesta_id, pregunta_id, archivo_url)
                        VALUES (%s, %s, %s)
                        """,
                        (respuesta_id, pregunta_id, archivo_url)
                    )
                else:
                    # Por defecto, guardar como texto
                    valor_texto = r.get('valor_texto')
                    cursor.execute(
                        """
                        INSERT INTO encuesta_respuestas_detalle (respuesta_id, pregunta_id, valor_texto)
                        VALUES (%s, %s, %s)
                        """,
                        (respuesta_id, pregunta_id, valor_texto)
                    )

            connection.commit()
            cursor.close()
            return jsonify({'success': True, 'id_respuesta': respuesta_id})
        except mysql.connector.Error as e:
            logger.error(f"Error guardando respuesta: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/encuestas/<int:encuesta_id>/respuestas', methods=['GET'])
    def listar_respuestas(encuesta_id):
        # Requiere autenticación para consultar respuestas
        user_id = session.get('user_id') or session.get('id_codigo_consumidor')
        if not user_id:
            return jsonify({'success': False, 'message': 'No autorizado'}), 401
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor(dictionary=True)
            # Cabeceras de respuestas
            cursor.execute(
                """
                SELECT r.id_respuesta, r.encuesta_id, r.usuario_id,
                       DATE_FORMAT(r.fecha_respuesta, %s) AS fecha_respuesta,
                       r.ip, r.user_agent
                FROM encuesta_respuestas r
                WHERE r.encuesta_id = %s
                ORDER BY r.id_respuesta DESC
                """,
                ('%Y-%m-%d %H:%i:%s', encuesta_id)
            )
            respuestas = cursor.fetchall()

            # Detalles de respuestas con joins para obtener texto de pregunta y opción
            cursor.execute(
                """
                SELECT d.respuesta_id, d.pregunta_id, p.texto AS texto_pregunta, p.tipo,
                       d.valor_texto, d.valor_numero, d.opcion_id, o.texto AS texto_opcion, d.archivo_url
                FROM encuesta_respuestas_detalle d
                JOIN encuesta_preguntas p ON p.id_pregunta = d.pregunta_id
                LEFT JOIN encuesta_opciones o ON o.id_opcion = d.opcion_id
                WHERE p.encuesta_id = %s
                ORDER BY d.respuesta_id, d.pregunta_id
                """,
                (encuesta_id,)
            )
            detalles = cursor.fetchall()

            # Agregar detalles a cada respuesta
            detalles_por_respuesta = {}
            for det in detalles:
                detalles_por_respuesta.setdefault(det['respuesta_id'], []).append(det)
            for r in respuestas:
                r['detalles'] = detalles_por_respuesta.get(r['id_respuesta'], [])

            return jsonify({'success': True, 'encuesta_id': encuesta_id, 'total': len(respuestas), 'respuestas': respuestas})
        except mysql.connector.Error as e:
            logger.error(f"Error listando respuestas: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/encuestas/<int:encuesta_id>/estadisticas', methods=['GET'])
    def estadisticas_encuesta(encuesta_id):
        """Devuelve estadísticas básicas de una encuesta: total de respuestas y distribución por pregunta/opción."""
        user_id = session.get('user_id') or session.get('id_codigo_consumidor')
        logger.info(f"[encuestas] estadisticas_encuesta encuesta_id={encuesta_id} user_id={user_id}")
        if not user_id:
            return jsonify({'success': False, 'message': 'No autorizado'}), 401

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cur = conn.cursor(dictionary=True)
            # Total de respuestas
            cur.execute("SELECT COUNT(*) AS total_respuestas FROM encuesta_respuestas WHERE encuesta_id = %s", (encuesta_id,))
            row_total = cur.fetchone() or {}
            total_respuestas = row_total.get('total_respuestas', 0)

            # Preguntas
            cur.execute("SELECT id_pregunta, texto, tipo, orden FROM encuesta_preguntas WHERE encuesta_id = %s ORDER BY orden, id_pregunta", (encuesta_id,))
            preguntas = cur.fetchall() or []

            # Total respondidas por pregunta
            cur.execute(
                """
                SELECT d.pregunta_id, COUNT(*) AS total
                FROM encuesta_respuestas_detalle d
                JOIN encuesta_preguntas p ON p.id_pregunta = d.pregunta_id
                WHERE p.encuesta_id = %s
                GROUP BY d.pregunta_id
                """,
                (encuesta_id,)
            )
            totals_det = {r['pregunta_id']: r['total'] for r in (cur.fetchall() or [])}

            # Distribución por opción (para tipos con opciones)
            cur.execute(
                """
                SELECT d.pregunta_id, d.opcion_id, o.texto AS texto_opcion, COUNT(*) AS total
                FROM encuesta_respuestas_detalle d
                JOIN encuesta_preguntas p ON p.id_pregunta = d.pregunta_id
                LEFT JOIN encuesta_opciones o ON o.id_opcion = d.opcion_id
                WHERE p.encuesta_id = %s AND d.opcion_id IS NOT NULL
                GROUP BY d.pregunta_id, d.opcion_id, o.texto
                ORDER BY d.pregunta_id, total DESC
                """,
                (encuesta_id,)
            )
            dist_rows = cur.fetchall() or []
            dist_map = {}
            for r in dist_rows:
                dist_map.setdefault(r['pregunta_id'], []).append({
                    'opcion_id': r['opcion_id'],
                    'texto_opcion': r['texto_opcion'],
                    'total': r['total']
                })

            resumen = []
            for p in preguntas:
                resumen.append({
                    'pregunta_id': p['id_pregunta'],
                    'texto': p['texto'],
                    'tipo': p['tipo'],
                    'total_respondidas': totals_det.get(p['id_pregunta'], 0),
                    'opciones': dist_map.get(p['id_pregunta'], [])
                })

            return jsonify({
                'success': True,
                'encuesta_id': encuesta_id,
                'total_respuestas': total_respuestas,
                'preguntas': resumen
            })
        except mysql.connector.Error as e:
            logger.error(f"Error estadísticas encuesta {encuesta_id}: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            conn.close()

    @app.route('/api/encuestas/<int:encuesta_id>/respuestas/export', methods=['GET'])
    def exportar_respuestas(encuesta_id):
        """Exporta las respuestas de la encuesta en formato Excel o CSV (long-form)."""
        user_id = session.get('user_id') or session.get('id_codigo_consumidor')
        if not user_id:
            return jsonify({'success': False, 'message': 'No autorizado'}), 401

        formato = (request.args.get('formato') or 'excel').lower()
        if formato not in ('excel', 'csv'):
            formato = 'excel'

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT r.id_respuesta, r.usuario_id, r.fecha_respuesta, r.ip,
                       d.pregunta_id, p.texto AS texto_pregunta, p.tipo,
                       d.valor_texto, d.valor_numero, d.opcion_id, o.texto AS texto_opcion, d.archivo_url
                FROM encuesta_respuestas r
                JOIN encuesta_respuestas_detalle d ON d.respuesta_id = r.id_respuesta
                JOIN encuesta_preguntas p ON p.id_pregunta = d.pregunta_id
                LEFT JOIN encuesta_opciones o ON o.id_opcion = d.opcion_id
                WHERE r.encuesta_id = %s
                ORDER BY r.id_respuesta, d.pregunta_id
                """,
                (encuesta_id,)
            )
            rows = cur.fetchall() or []

            if not rows:
                return jsonify({'success': False, 'message': 'No hay respuestas para exportar'}), 404

            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if formato == 'csv':
                import io, csv
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
                response = make_response(output.getvalue())
                response.headers['Content-Type'] = 'text/csv; charset=utf-8'
                response.headers['Content-Disposition'] = f'attachment; filename=encuesta_{encuesta_id}_respuestas_{timestamp}.csv'
                return response
            else:
                # Excel
                try:
                    import pandas as pd
                    import io
                    output = io.BytesIO()
                    df = pd.DataFrame(rows)
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name=f"respuestas_{encuesta_id}")
                    response = make_response(output.getvalue())
                    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    response.headers['Content-Disposition'] = f'attachment; filename=encuesta_{encuesta_id}_respuestas_{timestamp}.xlsx'
                    return response
                except Exception as e:
                    logger.warning(f"Fallo export Excel, devolviendo CSV. Error: {e}")
                    import io, csv
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
                    writer.writeheader()
                    writer.writerows(rows)
                    response = make_response(output.getvalue())
                    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
                    response.headers['Content-Disposition'] = f'attachment; filename=encuesta_{encuesta_id}_respuestas_{timestamp}.csv'
                    return response

        except mysql.connector.Error as e:
            logger.error(f"Error exportando respuestas encuesta {encuesta_id}: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        except Exception as e:
            logger.error(f"Error inesperado exportando respuestas {encuesta_id}: {e}")
            return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500
        finally:
            try:
                conn.close()
            except Exception:
                pass

    logger.info("Rutas de encuestas registradas correctamente")

if __name__ == '__main__':
    # Prueba rápida del módulo
    from flask import Flask
    app = Flask(__name__)
    registrar_rutas_encuestas(app)
    print("Módulo de encuestas cargado. Rutas:")
    print("- GET /lider/encuestas")
    print("- GET /api/encuestas")
    print("- POST /api/encuestas")
    print("- GET /api/encuestas/<id>")
    print("- POST /api/encuestas/<id>/preguntas")