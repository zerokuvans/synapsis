#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de API para gestión de encuestas (tipo Google Forms)
Sistema - Capired
"""

import mysql.connector
from flask import jsonify, request, render_template, session, redirect, url_for, make_response
from flask_login import login_required
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
                con_puntaje TINYINT(1) DEFAULT 0,
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
            ("encuestas", "con_puntaje", "TINYINT(1) DEFAULT 0"),
            ("encuestas", "visibilidad", "ENUM('privada','publica') DEFAULT 'privada'"),
            ("encuestas", "dirigida_a", "ENUM('todos','tecnicos','analistas','supervisores') DEFAULT 'todos'"),
            ("encuestas", "audiencia_carpetas", "TEXT NULL"),
            ("encuestas", "audiencia_supervisores", "TEXT NULL"),
            ("encuestas", "audiencia_tecnicos", "TEXT NULL"),
            ("encuestas", "creado_por", "INT NULL"),
            ("encuestas", "fecha_inicio", "DATETIME NULL"),
            ("encuestas", "fecha_fin", "DATETIME NULL"),
            ("encuestas", "fecha_actualizacion", "DATETIME NULL"),
            # Campos para sistema de votaciones
            ("encuestas", "tipo_encuesta", "ENUM('encuesta','votacion') DEFAULT 'encuesta'"),
            ("encuestas", "mostrar_resultados", "TINYINT(1) DEFAULT 0"),
            ("encuestas", "fecha_inicio_votacion", "DATETIME NULL"),
            ("encuestas", "fecha_fin_votacion", "DATETIME NULL")
        ]

        for table, col, col_def in required_columns:
            try:
                if not column_exists(table, col):
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}")
            except mysql.connector.Error as e:
                logger.warning(f"No se pudo agregar columna {table}.{col}: {e}")

        # Asegurar columnas de múltiples respuestas
        try:
            if not column_exists("encuestas", "permitir_multiples_respuestas"):
                cursor.execute("ALTER TABLE encuestas ADD COLUMN permitir_multiples_respuestas TINYINT(1) DEFAULT 1")
            if not column_exists("encuestas", "modo_multiples_respuestas"):
                cursor.execute("ALTER TABLE encuestas ADD COLUMN modo_multiples_respuestas ENUM('por_mes','por_periodo','libre','unica') DEFAULT 'por_mes'")
            # Campos para encuestas de puntaje: umbral de aprobación y límite de intentos
            if not column_exists("encuestas", "porcentaje_aprobacion"):
                cursor.execute("ALTER TABLE encuestas ADD COLUMN porcentaje_aprobacion DECIMAL(5,2) DEFAULT 90.00")
            if not column_exists("encuestas", "maximo_intentos"):
                cursor.execute("ALTER TABLE encuestas ADD COLUMN maximo_intentos INT DEFAULT 2")
        except mysql.connector.Error as e:
            logger.warning(f"No se pudo agregar columnas de múltiples respuestas: {e}")

        # Tabla de candidatos para votaciones
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS candidatos (
                id_candidato INT AUTO_INCREMENT PRIMARY KEY,
                id_encuesta INT NOT NULL,
                nombre VARCHAR(255) NOT NULL,
                descripcion TEXT NULL,
                foto_url VARCHAR(500) NULL,
                orden INT DEFAULT 0,
                fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_candidatos_encuesta FOREIGN KEY (id_encuesta)
                    REFERENCES encuestas(id_encuesta) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # Tabla de votos para votaciones
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS votos (
                id_voto INT AUTO_INCREMENT PRIMARY KEY,
                id_encuesta INT NOT NULL,
                id_candidato INT NOT NULL,
                id_usuario INT NOT NULL,
                fecha_voto DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45) NULL,
                UNIQUE KEY uniq_voto (id_encuesta, id_usuario),
                CONSTRAINT fk_votos_encuesta FOREIGN KEY (id_encuesta)
                    REFERENCES encuestas(id_encuesta) ON DELETE CASCADE,
                CONSTRAINT fk_votos_candidato FOREIGN KEY (id_candidato)
                    REFERENCES candidatos(id_candidato) ON DELETE CASCADE,
                CONSTRAINT fk_votos_usuario FOREIGN KEY (id_usuario)
                    REFERENCES usuarios(idusuarios) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # Tabla secciones
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS encuesta_secciones (
                id_seccion INT AUTO_INCREMENT PRIMARY KEY,
                encuesta_id INT NOT NULL,
                titulo VARCHAR(255) NOT NULL,
                descripcion TEXT NULL,
                orden INT DEFAULT 0,
                fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (encuesta_id) REFERENCES encuestas(id_encuesta) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # Tabla preguntas
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS encuesta_preguntas (
                id_pregunta INT AUTO_INCREMENT PRIMARY KEY,
                encuesta_id INT NOT NULL,
                seccion_id INT NULL,
                tipo ENUM('texto','parrafo','numero','fecha','hora','opcion_multiple','seleccion_unica','checkbox','dropdown','imagen') NOT NULL,
                texto VARCHAR(500) NOT NULL,
                ayuda VARCHAR(500) NULL,
                requerida TINYINT(1) DEFAULT 0,
                orden INT DEFAULT 0,
                config_json JSON NULL,
                imagen_referencia_url VARCHAR(500) NULL,
                FOREIGN KEY (encuesta_id) REFERENCES encuestas(id_encuesta) ON DELETE CASCADE,
                FOREIGN KEY (seccion_id) REFERENCES encuesta_secciones(id_seccion) ON DELETE SET NULL
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
                es_correcta TINYINT(1) DEFAULT 0,
                puntaje DECIMAL(10,2) NULL,
                orden INT DEFAULT 0,
                FOREIGN KEY (pregunta_id) REFERENCES encuesta_preguntas(id_pregunta) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # Asegurar columnas de opciones en instalaciones existentes
        for table, col, col_def in [
            ("encuesta_opciones", "es_correcta", "TINYINT(1) DEFAULT 0"),
            ("encuesta_opciones", "puntaje", "DECIMAL(10,2) NULL")
        ]:
            try:
                if not column_exists(table, col):
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}")
            except mysql.connector.Error as e:
                logger.warning(f"No se pudo agregar columna {table}.{col}: {e}")

        # Asegurar columna seccion_id en preguntas para instalaciones existentes
        try:
            if not column_exists("encuesta_preguntas", "seccion_id"):
                cursor.execute("ALTER TABLE encuesta_preguntas ADD COLUMN seccion_id INT NULL")
                cursor.execute("ALTER TABLE encuesta_preguntas ADD CONSTRAINT fk_pregunta_seccion FOREIGN KEY (seccion_id) REFERENCES encuesta_secciones(id_seccion) ON DELETE SET NULL")
            # Asegurar columna imagen_referencia_url en instalaciones existentes
            if not column_exists("encuesta_preguntas", "imagen_referencia_url"):
                cursor.execute("ALTER TABLE encuesta_preguntas ADD COLUMN imagen_referencia_url VARCHAR(500) NULL")
        except mysql.connector.Error as e:
            logger.warning(f"No se pudo agregar columnas a encuesta_preguntas: {e}")

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

        # Asegurar columnas para encuestas con puntaje en respuestas
        try:
            if not column_exists("encuesta_respuestas", "aprobado"):
                cursor.execute("ALTER TABLE encuesta_respuestas ADD COLUMN aprobado TINYINT(1) NULL")
            if not column_exists("encuesta_respuestas", "porcentaje_obtenido"):
                cursor.execute("ALTER TABLE encuesta_respuestas ADD COLUMN porcentaje_obtenido DECIMAL(5,2) NULL")
        except mysql.connector.Error as e:
            logger.warning(f"No se pudo agregar columnas a encuesta_respuestas (aprobado/porcentaje_obtenido): {e}")

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

    def _get_usuario_id():
        """Obtiene el ID de usuario desde Flask-Login o desde la sesión.
        Retorna None si no hay usuario autenticado.
        """
        # Intentar con Flask-Login
        try:
            from flask_login import current_user  # type: ignore
            if getattr(current_user, 'is_authenticated', False):
                # Soporta atributos comunes: id, get_id()
                if hasattr(current_user, 'get_id'):
                    try:
                        return str(current_user.get_id())
                    except Exception:
                        pass
                if hasattr(current_user, 'id'):
                    try:
                        return str(current_user.id)
                    except Exception:
                        pass
        except Exception:
            # Ignorar si Flask-Login no está disponible
            pass
        # Fallback a claves en sesión
        uid = session.get('user_id') or session.get('id_codigo_consumidor')
        return str(uid) if uid is not None else None

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
            user_id = _get_usuario_id()
            logger.info(f"[encuestas] listar_encuestas user_id={user_id} (Flask-Login o sesión)")
            if not user_id:
                # Si no hay usuario en sesión, devolver no autorizado para API
                return jsonify({'success': False, 'message': 'No autorizado'}), 401

            # Usuario especial 1988914 puede ver todas las encuestas
            es_admin_encuestas = str(user_id) == '1988914'

            if es_admin_encuestas:
                cursor.execute(
                    """
                    SELECT id_encuesta, titulo, descripcion, estado, anonima, visibilidad,
                           DATE_FORMAT(fecha_inicio, %s) AS fecha_inicio,
                           DATE_FORMAT(fecha_fin, %s) AS fecha_fin,
                           DATE_FORMAT(fecha_creacion, %s) AS fecha_creacion,
                           DATE_FORMAT(fecha_actualizacion, %s) AS fecha_actualizacion,
                           creado_por
                    FROM encuestas
                    ORDER BY id_encuesta DESC
                    """,
                    ('%Y-%m-%d %H:%i:%s', '%Y-%m-%d %H:%i:%s', '%Y-%m-%d %H:%i:%s', '%Y-%m-%d %H:%i:%s')
                )
            else:
                cursor.execute(
                    """
                    SELECT id_encuesta, titulo, descripcion, estado, anonima, visibilidad,
                           DATE_FORMAT(fecha_inicio, %s) AS fecha_inicio,
                           DATE_FORMAT(fecha_fin, %s) AS fecha_fin,
                           DATE_FORMAT(fecha_creacion, %s) AS fecha_creacion,
                           DATE_FORMAT(fecha_actualizacion, %s) AS fecha_actualizacion,
                           creado_por
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
        con_puntaje = 1 if data.get('con_puntaje', False) else 0
        porcentaje_aprobacion = None
        try:
            porcentaje_aprobacion = float(data.get('porcentaje_aprobacion')) if data.get('porcentaje_aprobacion') is not None else 90.0
        except Exception:
            porcentaje_aprobacion = 90.0
        if porcentaje_aprobacion < 0: porcentaje_aprobacion = 0.0
        if porcentaje_aprobacion > 100: porcentaje_aprobacion = 100.0
        maximo_intentos = None
        try:
            maximo_intentos = int(data.get('maximo_intentos')) if data.get('maximo_intentos') is not None else 2
        except Exception:
            maximo_intentos = 2
        if maximo_intentos < 1: maximo_intentos = 1
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
        user_id = _get_usuario_id()
        logger.info(f"[encuestas] crear_encuesta user_id={user_id} (Flask-Login o sesión) payload.titulo={titulo}")

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
                    titulo, descripcion, estado, anonima, con_puntaje, visibilidad, dirigida_a,
                    audiencia_carpetas, audiencia_supervisores, audiencia_tecnicos,
                    fecha_inicio, fecha_fin, creado_por,
                    permitir_multiples_respuestas, modo_multiples_respuestas,
                    porcentaje_aprobacion, maximo_intentos
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    titulo, descripcion, estado, anonima, con_puntaje, visibilidad, dirigida_a,
                    audiencia_carpetas, audiencia_supervisores, audiencia_tecnicos,
                    fecha_inicio, fecha_fin, user_id,
                    1 if (data.get('permitir_multiples_respuestas') in (1, True)) else 0,
                    (data.get('modo_multiples_respuestas') or 'por_mes'),
                    porcentaje_aprobacion, maximo_intentos
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
                       COALESCE(analista, 0) AS es_analista
                FROM recurso_operativo
                WHERE id_codigo_consumidor = %s
                """,
                (usuario_id,)
            )
            row = cur.fetchone()
            if row:
                rol_sesion = (session.get('user_role') or '').lower()
                # Técnicos por id_roles == 2 o por rol de sesión
                if row.get('id_roles') == 2 or rol_sesion == 'tecnicos':
                    auds.add('tecnicos')
                cargo = (row.get('cargo') or '').upper()
                # Analistas por flag o por cargo
                if row.get('es_analista') in (1, True) or 'ANALISTA' in cargo or rol_sesion == 'analistas':
                    auds.add('analistas')
                # Supervisores por cargo o rol líder (id_roles == 7) o rol de sesión
                if row.get('id_roles') == 7 or 'SUPERVIS' in cargo or rol_sesion == 'lider':
                    auds.add('supervisores')
        except Exception as e:
            logger.warning(f"No se pudo resolver audiencia de usuario {usuario_id}: {e}")
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
            # Diferenciar filtros de visibilidad según tipo de encuesta:
            # - Para votaciones: ocultar si el usuario ya votó (tabla votos)
            # - Para encuestas normales: ocultar si el usuario ya envió respuesta (tabla encuesta_respuestas)
            cur.execute(
                f"""
                SELECT id_encuesta, titulo, descripcion, dirigida_a, audiencia_carpetas, audiencia_supervisores, audiencia_tecnicos,
                       tipo_encuesta,
                       permitir_multiples_respuestas, modo_multiples_respuestas,
                       DATE_FORMAT(fecha_inicio, %s) AS fecha_inicio,
                       DATE_FORMAT(fecha_fin, %s) AS fecha_fin
                FROM encuestas
                WHERE estado = 'activa'
                  AND (
                       fecha_inicio IS NULL
                       OR fecha_inicio <= NOW()
                       OR DATE(fecha_inicio) <= CURDATE()
                  )
                  AND (
                       fecha_fin IS NULL
                       OR fecha_fin >= NOW()
                       OR DATE(fecha_fin) >= CURDATE()
                  )
                  AND (
                      LOWER(CASE
                        WHEN LOWER(dirigida_a) IN ('supervisor','supervisores') THEN 'supervisores'
                        WHEN LOWER(dirigida_a) IN ('analista','analistas') THEN 'analistas'
                        WHEN LOWER(dirigida_a) IN ('tecnico','tecnicos') THEN 'tecnicos'
                        ELSE LOWER(dirigida_a)
                      END) IN ({placeholders})
                      OR (
                        LOWER(CASE
                            WHEN LOWER(dirigida_a) IN ('supervisor','supervisores') THEN 'supervisores'
                            WHEN LOWER(dirigida_a) IN ('analista','analistas') THEN 'analistas'
                            WHEN LOWER(dirigida_a) IN ('tecnico','tecnicos') THEN 'tecnicos'
                            ELSE LOWER(dirigida_a)
                        END) = 'tecnicos'
                        AND audiencia_tecnicos IS NOT NULL
                      )
                  )
                  AND (
                        (COALESCE(tipo_encuesta, 'encuesta') = 'votacion' AND NOT EXISTS (
                            SELECT 1 FROM votos v
                            WHERE v.id_encuesta = encuestas.id_encuesta
                              AND v.id_usuario = %s
                        ))
                        OR
                        (
                          COALESCE(tipo_encuesta, 'encuesta') <> 'votacion' AND (
                            (
                              COALESCE(permitir_multiples_respuestas, 1) = 1 AND COALESCE(modo_multiples_respuestas, 'por_mes') = 'libre'
                            )
                            OR
                            (
                              COALESCE(permitir_multiples_respuestas, 1) = 1 AND COALESCE(modo_multiples_respuestas, 'por_mes') = 'por_mes'
                              AND NOT EXISTS (
                                SELECT 1 FROM encuesta_respuestas r
                                WHERE r.encuesta_id = encuestas.id_encuesta
                                  AND r.usuario_id = %s
                                  AND r.estado = 'enviada'
                                  AND YEAR(r.fecha_respuesta) = YEAR(NOW())
                                  AND MONTH(r.fecha_respuesta) = MONTH(NOW())
                              )
                            )
                            OR
                            (
                              COALESCE(permitir_multiples_respuestas, 1) = 1 AND COALESCE(modo_multiples_respuestas, 'por_mes') = 'por_periodo'
                              AND NOT EXISTS (
                                SELECT 1 FROM encuesta_respuestas r
                                WHERE r.encuesta_id = encuestas.id_encuesta
                                  AND r.usuario_id = %s
                                  AND r.estado = 'enviada'
                                  AND (
                                    (encuestas.fecha_inicio IS NOT NULL AND encuestas.fecha_fin IS NOT NULL AND r.fecha_respuesta BETWEEN encuestas.fecha_inicio AND encuestas.fecha_fin)
                                    OR
                                    (encuestas.fecha_inicio IS NOT NULL AND encuestas.fecha_fin IS NULL AND r.fecha_respuesta >= encuestas.fecha_inicio)
                                    OR
                                    (encuestas.fecha_inicio IS NULL AND encuestas.fecha_fin IS NOT NULL AND r.fecha_respuesta <= encuestas.fecha_fin)
                                  )
                              )
                            )
                            OR
                            (
                              (COALESCE(permitir_multiples_respuestas, 1) = 0 OR COALESCE(modo_multiples_respuestas, 'por_mes') = 'unica')
                              AND NOT EXISTS (
                                SELECT 1 FROM encuesta_respuestas r
                                WHERE r.encuesta_id = encuestas.id_encuesta
                                  AND r.usuario_id = %s
                                  AND r.estado = 'enviada'
                              )
                            )
                          )
                          AND (
                            COALESCE(con_puntaje, 0) = 0
                            OR NOT EXISTS (
                              SELECT 1 FROM encuesta_respuestas r
                              WHERE r.encuesta_id = encuestas.id_encuesta
                                AND r.usuario_id = %s
                                AND r.estado = 'enviada'
                                AND r.aprobado = 1
                            )
                          )
                        )
                  )
                ORDER BY fecha_inicio ASC, id_encuesta ASC
                """,
                ['%Y-%m-%d %H:%i:%s', '%Y-%m-%d %H:%i:%s', *valores, usuario_id, usuario_id, usuario_id, usuario_id, usuario_id]
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
                # Normalizar dirigida_a para evaluación
                dirigida = (enc.get('dirigida_a') or '').strip().lower()
                if dirigida in ('tecnico', 'técnico'):
                    dirigida = 'tecnicos'

                if dirigida == 'tecnicos':
                    pasa = True
                    # Filtro por carpetas (ignorar listas vacías)
                    if pasa and enc.get('audiencia_carpetas'):
                        try:
                            lista = json.loads(enc.get('audiencia_carpetas'))
                            if isinstance(lista, list):
                                if len(lista) > 0:
                                    if not carpeta_usuario:
                                        pasa = False
                                    else:
                                        cu = (carpeta_usuario or '').strip().lower()
                                        pasa = any((c or '').strip().lower() == cu for c in lista)
                                # Si la lista está vacía, no restringe
                            else:
                                # Formato inesperado: no bloquear
                                pasa = True
                        except Exception:
                            # JSON inválido: permitir por seguridad
                            pasa = True

                    # Filtro por supervisores (ignorar listas vacías)
                    if pasa and enc.get('audiencia_supervisores'):
                        try:
                            sup_list = json.loads(enc.get('audiencia_supervisores'))
                            if isinstance(sup_list, list):
                                if len(sup_list) > 0:
                                    if not supervisor_usuario:
                                        pasa = False
                                    else:
                                        compara = (supervisor_usuario or '').strip().lower()
                                        pasa = any((s or '').strip().lower() == compara for s in sup_list)
                                # Lista vacía: no restringe
                            else:
                                pasa = True
                        except Exception:
                            pasa = True

                    # Filtro por técnicos (si está definido). Se espera lista de IDs.
                    if pasa and enc.get('audiencia_tecnicos'):
                        try:
                            t_list = json.loads(enc.get('audiencia_tecnicos'))
                            if isinstance(t_list, list) and len(t_list) > 0:
                                # Si hay lista, debe estar el usuario actual (comparar como str)
                                pasa = str(usuario_id) in set(str(t) for t in t_list)
                            # Lista vacía: no restringe
                        except Exception:
                            # Si hay problema con el JSON, no bloquear
                            pasa = True

                    if pasa:
                        filtradas.append(enc)
                else:
                    # Audiencias distintas a técnicos no requieren filtro adicional
                    filtradas.append(enc)
            rows = filtradas

            return jsonify({'success': True, 'encuestas': rows, 'audiencias': auds, 'carpeta_usuario': carpeta_usuario, 'supervisor_usuario': supervisor_usuario})
        except mysql.connector.Error as e:
            logger.error(f"Error consultando encuestas activas para usuario: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            conn.close()

    @app.route('/api/encuestas/activas/diagnostico', methods=['GET'])
    def encuestas_activas_diagnostico():
        """Diagnóstico de por qué una encuesta se muestra u oculta para el usuario actual."""
        usuario_id = request.args.get('user_id') or session.get('user_id') or session.get('id_codigo_consumidor')
        if not usuario_id:
            return jsonify({'success': False, 'message': 'No autorizado'}), 401

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        try:
            cur = conn.cursor(dictionary=True)
            auds = _resolver_audiencias_usuario(conn, usuario_id)
            valores = ['todos'] + (auds or [])
            placeholders = ','.join(['%s'] * len(valores))

            cur.execute(
                f"""
                SELECT id_encuesta, titulo, descripcion, dirigida_a, audiencia_carpetas, audiencia_supervisores, audiencia_tecnicos,
                       tipo_encuesta,
                       permitir_multiples_respuestas, modo_multiples_respuestas,
                       con_puntaje,
                       fecha_inicio, fecha_fin
                FROM encuestas
                WHERE estado = 'activa'
                  AND (
                       fecha_inicio IS NULL OR fecha_inicio <= NOW() OR DATE(fecha_inicio) <= CURDATE()
                  )
                  AND (
                       fecha_fin IS NULL OR fecha_fin >= NOW() OR DATE(fecha_fin) >= CURDATE()
                  )
                  AND (
                      LOWER(CASE
                        WHEN LOWER(dirigida_a) IN ('supervisor','supervisores') THEN 'supervisores'
                        WHEN LOWER(dirigida_a) IN ('analista','analistas') THEN 'analistas'
                        WHEN LOWER(dirigida_a) IN ('tecnico','tecnicos') THEN 'tecnicos'
                        ELSE LOWER(dirigida_a)
                      END) IN ({placeholders})
                      OR (
                        LOWER(CASE
                            WHEN LOWER(dirigida_a) IN ('supervisor','supervisores') THEN 'supervisores'
                            WHEN LOWER(dirigida_a) IN ('analista','analistas') THEN 'analistas'
                            WHEN LOWER(dirigida_a) IN ('tecnico','tecnicos') THEN 'tecnicos'
                            ELSE LOWER(dirigida_a)
                        END) = 'tecnicos'
                        AND audiencia_tecnicos IS NOT NULL
                      )
                  )
                ORDER BY id_encuesta ASC
                """,
                valores
            )
            encs = cur.fetchall() or []

            # Datos adicionales del usuario para filtro fino
            carpeta_usuario = None
            supervisor_usuario = None
            try:
                cur.execute("SELECT carpeta, super FROM recurso_operativo WHERE id_codigo_consumidor = %s", (usuario_id,))
                r = cur.fetchone()
                carpeta_usuario = (r or {}).get('carpeta') if r else None
                supervisor_usuario = (r or {}).get('super') if r else None
            except Exception as e:
                logger.warning(f"No se pudo obtener carpeta/supervisor del usuario {usuario_id}: {e}")

            diagnostico = []
            for enc in encs:
                dirigida = (enc.get('dirigida_a') or '').strip().lower()
                if dirigida in ('tecnico','técnico'):
                    dirigida = 'tecnicos'

                # Validación de audiencia específica (carpetas/supervisores/técnicos)
                audiencia_ok = True
                motivo_aud = None
                if dirigida == 'tecnicos':
                    # Carpetas
                    if enc.get('audiencia_carpetas'):
                        try:
                            lista = json.loads(enc.get('audiencia_carpetas'))
                            if isinstance(lista, list) and len(lista) > 0:
                                cu = (carpeta_usuario or '').strip().lower()
                                audiencia_ok = any((c or '').strip().lower() == cu for c in lista)
                                if not audiencia_ok:
                                    motivo_aud = f"carpeta '{carpeta_usuario}' no incluida"
                        except Exception as e:
                            motivo_aud = f"error leyendo carpetas: {e}"
                            audiencia_ok = True
                    # Supervisores
                    if audiencia_ok and enc.get('audiencia_supervisores'):
                        try:
                            lista = json.loads(enc.get('audiencia_supervisores'))
                            if isinstance(lista, list) and len(lista) > 0:
                                su = (supervisor_usuario or '').strip().lower()
                                audiencia_ok = any((s or '').strip().lower() == su for s in lista)
                                if not audiencia_ok:
                                    motivo_aud = f"supervisor '{supervisor_usuario}' no incluido"
                        except Exception as e:
                            motivo_aud = f"error leyendo supervisores: {e}"
                            audiencia_ok = True
                    # Técnicos (lista de IDs)
                    if audiencia_ok and enc.get('audiencia_tecnicos'):
                        try:
                            t_list = json.loads(enc.get('audiencia_tecnicos'))
                            if isinstance(t_list, list) and len(t_list) > 0:
                                audiencia_ok = str(usuario_id) in set(str(t) for t in t_list)
                                if not audiencia_ok:
                                    motivo_aud = f"usuario {usuario_id} no está en audiencia_tecnicos"
                        except Exception as e:
                            motivo_aud = f"error leyendo tecnicos: {e}"
                            audiencia_ok = True

                # Conteos de respuestas para el usuario
                aprobada = 0
                respondida_total = 0
                respondida_mes = 0
                try:
                    cur.execute("""
                        SELECT COUNT(1) AS cnt FROM encuesta_respuestas r
                        WHERE r.encuesta_id = %s AND r.usuario_id = %s AND r.estado = 'enviada' AND r.aprobado = 1
                    """, (enc['id_encuesta'], usuario_id))
                    aprobada = (cur.fetchone() or {}).get('cnt') or 0
                    cur.execute("""
                        SELECT COUNT(1) AS cnt FROM encuesta_respuestas r
                        WHERE r.encuesta_id = %s AND r.usuario_id = %s AND r.estado = 'enviada'
                    """, (enc['id_encuesta'], usuario_id))
                    respondida_total = (cur.fetchone() or {}).get('cnt') or 0
                    cur.execute("""
                        SELECT COUNT(1) AS cnt FROM encuesta_respuestas r
                        WHERE r.encuesta_id = %s AND r.usuario_id = %s AND r.estado = 'enviada'
                          AND YEAR(r.fecha_respuesta) = YEAR(NOW()) AND MONTH(r.fecha_respuesta) = MONTH(NOW())
                    """, (enc['id_encuesta'], usuario_id))
                    respondida_mes = (cur.fetchone() or {}).get('cnt') or 0
                except Exception as e:
                    logger.warning(f"Error consultando respuestas para diagnóstico: {e}")

                permitir_multi = int(enc.get('permitir_multiples_respuestas') or 1)
                modo = (enc.get('modo_multiples_respuestas') or 'por_mes')
                con_puntaje = int(enc.get('con_puntaje') or 0)

                activa = True
                motivos = []
                if not audiencia_ok:
                    activa = False
                    motivos.append(motivo_aud or 'audiencia no coincide')
                if con_puntaje == 1 and aprobada > 0:
                    activa = False
                    motivos.append('ya aprobada por puntaje')
                if activa and permitir_multi == 1 and modo == 'por_mes' and respondida_mes > 0:
                    activa = False
                    motivos.append('ya respondida este mes')
                if activa and (permitir_multi == 0 or modo == 'unica') and respondida_total > 0:
                    activa = False
                    motivos.append('modo única ya respondida')

                diagnostico.append({
                    'id_encuesta': enc['id_encuesta'],
                    'titulo': enc.get('titulo'),
                    'dirigida_a': dirigida,
                    'permitir_multiples_respuestas': permitir_multi,
                    'modo_multiples_respuestas': modo,
                    'con_puntaje': con_puntaje,
                    'audiencia_ok': audiencia_ok,
                    'aprobada': int(aprobada),
                    'respondida_total': int(respondida_total),
                    'respondida_mes': int(respondida_mes),
                    'activa': activa,
                    'motivos': motivos,
                })

            return jsonify({'success': True, 'usuario_id': usuario_id, 'audiencias_usuario': auds, 'carpeta_usuario': carpeta_usuario, 'supervisor_usuario': supervisor_usuario, 'diagnostico': diagnostico})
        except mysql.connector.Error as e:
            logger.error(f"Error generando diagnóstico: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            try:
                conn.close()
            except Exception:
                pass

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

            # Obtener secciones de la encuesta
            cursor.execute("SELECT * FROM encuesta_secciones WHERE encuesta_id = %s ORDER BY orden ASC", (encuesta_id,))
            secciones = cursor.fetchall()

            # Crear mapeo de secciones por ID para fácil acceso
            secciones_por_id = {seccion['id_seccion']: seccion for seccion in secciones}

            # Convertir config_json a dict y agregar información de sección a cada pregunta
            for p in preguntas:
                if p.get('config_json'):
                    try:
                        p['config'] = json.loads(p['config_json']) if isinstance(p['config_json'], str) else p['config_json']
                    except Exception:
                        p['config'] = None
                else:
                    p['config'] = None
                p['opciones'] = opciones_por_pregunta.get(p['id_pregunta'], [])
                
                # Agregar título de sección si la pregunta tiene seccion_id
                if p.get('seccion_id') and p['seccion_id'] in secciones_por_id:
                    p['titulo_seccion'] = secciones_por_id[p['seccion_id']]['titulo']
                else:
                    p['titulo_seccion'] = None

            encuesta['preguntas'] = preguntas
            encuesta['secciones'] = secciones
            # También exponemos preguntas en el nivel raíz para compatibilidad del frontend
            return jsonify({'success': True, 'encuesta': encuesta, 'preguntas': preguntas, 'secciones': secciones})
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo encuesta: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/encuestas/<int:encuesta_id>', methods=['DELETE'])
    def eliminar_encuesta(encuesta_id):
        """Elimina una encuesta si el usuario es 1988914 o el creador.
        Valida que no existan respuestas enviadas asociadas. Elimina en orden:
        opciones -> preguntas -> secciones -> encuesta.
        """
        usuario_id = session.get('user_id') or session.get('id_codigo_consumidor')
        if not usuario_id:
            return jsonify({'success': False, 'message': 'No autorizado'}), 401

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            admin_total = str(usuario_id) == '1988914'
            cur = conn.cursor(dictionary=True)
            # Verificar existencia y creador
            cur.execute("SELECT id_encuesta, creado_por FROM encuestas WHERE id_encuesta = %s", (encuesta_id,))
            enc = cur.fetchone()
            if not enc:
                return jsonify({'success': False, 'message': 'Encuesta no encontrada'}), 404

            creador = str(enc.get('creado_por')) if enc.get('creado_por') is not None else None
            if not admin_total and creador != str(usuario_id):
                return jsonify({'success': False, 'message': 'No tiene permisos para eliminar esta encuesta'}), 403

            # Validar que no haya respuestas enviadas
            cur.execute("SELECT COUNT(*) AS total FROM encuesta_respuestas WHERE encuesta_id = %s AND estado = 'enviada'", (encuesta_id,))
            total_env = (cur.fetchone() or {}).get('total', 0)
            if total_env and int(total_env) > 0:
                return jsonify({'success': False, 'message': 'No se puede eliminar: existen respuestas enviadas asociadas'}), 400

            # Iniciar transacción manual
            conn.start_transaction()

            # Eliminar opciones de preguntas de esta encuesta
            cur2 = conn.cursor()
            cur2.execute("SELECT id_pregunta FROM encuesta_preguntas WHERE encuesta_id = %s", (encuesta_id,))
            ids_preg = [row[0] for row in (cur2.fetchall() or [])]
            if ids_preg:
                for pid in ids_preg:
                    try:
                        cur2.execute("DELETE FROM encuesta_opciones WHERE pregunta_id = %s", (pid,))
                    except Exception:
                        pass
            # Eliminar preguntas
            cur2.execute("DELETE FROM encuesta_preguntas WHERE encuesta_id = %s", (encuesta_id,))
            # Eliminar secciones
            cur2.execute("DELETE FROM encuesta_secciones WHERE encuesta_id = %s", (encuesta_id,))
            # Eliminar respuestas (borrador o no enviadas) si existieran
            cur2.execute("DELETE FROM encuesta_respuestas_detalle WHERE respuesta_id IN (SELECT id_respuesta FROM encuesta_respuestas WHERE encuesta_id = %s)", (encuesta_id,))
            cur2.execute("DELETE FROM encuesta_respuestas WHERE encuesta_id = %s AND (estado IS NULL OR estado <> 'enviada')", (encuesta_id,))
            # Finalmente eliminar encuesta
            cur2.execute("DELETE FROM encuestas WHERE id_encuesta = %s", (encuesta_id,))

            conn.commit()
            cur.close(); cur2.close()
            return jsonify({'success': True, 'message': 'Encuesta eliminada'})
        except mysql.connector.Error as e:
            try:
                conn.rollback()
            except Exception:
                pass
            logger.error(f"Error eliminando encuesta {encuesta_id}: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            conn.close()

    @app.route('/api/encuestas/<int:encuesta_id>/audiencia-estado', methods=['GET'])
    def audiencia_estado_encuesta(encuesta_id):
        """Devuelve la lista de técnicos habilitados para la encuesta y su estado de respuesta.
        Respuesta: { success: true, encuesta, tecnicos: [{ id, nombre, carpeta, super, fecha, estado }] }
        estado: 'ok' si tiene respuesta enviada, 'pendiente' en otro caso.
        """
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id_encuesta, dirigida_a, audiencia_carpetas, audiencia_supervisores, audiencia_tecnicos
                FROM encuestas
                WHERE id_encuesta = %s
                """,
                (encuesta_id,)
            )
            enc = cur.fetchone()
            if not enc:
                return jsonify({'success': False, 'message': 'Encuesta no encontrada'}), 404

            dirigida_a = (enc.get('dirigida_a') or '').strip().lower()
            aud_carpetas = enc.get('audiencia_carpetas')
            aud_supervisores = enc.get('audiencia_supervisores')
            aud_tecnicos = enc.get('audiencia_tecnicos')

            # Parsear JSONs si son textos
            try:
                if isinstance(aud_carpetas, str) and aud_carpetas:
                    aud_carpetas = json.loads(aud_carpetas)
            except Exception:
                aud_carpetas = None
            try:
                if isinstance(aud_supervisores, str) and aud_supervisores:
                    aud_supervisores = json.loads(aud_supervisores)
            except Exception:
                aud_supervisores = None
            try:
                if isinstance(aud_tecnicos, str) and aud_tecnicos:
                    aud_tecnicos = json.loads(aud_tecnicos)
            except Exception:
                aud_tecnicos = None

            tecnicos_rows = []

            if dirigida_a == 'tecnicos':
                # Construir consulta base de técnicos habilitados
                if isinstance(aud_tecnicos, list) and len(aud_tecnicos) > 0:
                    # Lista explícita de técnicos
                    ids = [str(t).strip() for t in aud_tecnicos if str(t).strip()]
                    placeholders = ','.join(['%s'] * len(ids))
                    cur.execute(
                        f"""
                        SELECT ro.id_codigo_consumidor AS id, ro.nombre, ro.carpeta, ro.super
                        FROM recurso_operativo ro
                        WHERE ro.id_codigo_consumidor IN ({placeholders})
                          AND (ro.estado IS NULL OR ro.estado = 'Activo')
                        ORDER BY ro.nombre
                        """,
                        ids
                    )
                    tecnicos_rows = cur.fetchall() or []
                else:
                    # Filtrar por supervisores y/o carpetas
                    where_clauses = ["(ro.estado IS NULL OR ro.estado = 'Activo')"]
                    params = []
                    if isinstance(aud_supervisores, list) and len(aud_supervisores) > 0:
                        # Comparación case-insensitive
                        placeholders = ','.join(['%s'] * len(aud_supervisores))
                        where_clauses.append(f"LOWER(ro.super) IN ({placeholders})")
                        params.extend([(s or '').strip().lower() for s in aud_supervisores])
                    if isinstance(aud_carpetas, list) and len(aud_carpetas) > 0:
                        placeholders = ','.join(['%s'] * len(aud_carpetas))
                        where_clauses.append(f"LOWER(ro.carpeta) IN ({placeholders})")
                        params.extend([(c or '').strip().lower() for c in aud_carpetas])

                    # Si no hay filtros, por seguridad retornar vacío para evitar listados masivos
                    if len(where_clauses) == 1:
                        tecnicos_rows = []
                    else:
                        cur.execute(
                            f"""
                            SELECT ro.id_codigo_consumidor AS id, ro.nombre, ro.carpeta, ro.super
                            FROM recurso_operativo ro
                            WHERE {' AND '.join(where_clauses)}
                            ORDER BY ro.nombre
                            """,
                            params
                        )
                        tecnicos_rows = cur.fetchall() or []
            elif dirigida_a == 'todos':
                # Encuesta dirigida a todos los técnicos activos
                cur.execute(
                    """
                    SELECT ro.id_codigo_consumidor AS id, ro.nombre, ro.carpeta, ro.super
                    FROM recurso_operativo ro
                    WHERE ro.estado = 'Activo'
                    ORDER BY ro.nombre
                    """
                )
                tecnicos_rows = cur.fetchall() or []
            else:
                # Otros tipos de audiencia (por ahora no soportados)
                tecnicos_rows = []

            # Obtener última fecha de respuesta por usuario para esta encuesta
            cur.execute(
                """
                SELECT usuario_id, MAX(fecha_respuesta) AS fecha, MAX(CASE WHEN estado = 'enviada' THEN 1 ELSE 0 END) AS enviada
                FROM encuesta_respuestas
                WHERE encuesta_id = %s
                GROUP BY usuario_id
                """,
                (encuesta_id,)
            )
            respuestas_map = {}
            for r in cur.fetchall() or []:
                respuestas_map[str(r['usuario_id'])] = {
                    'fecha': r['fecha'],
                    'enviada': r['enviada'] == 1
                }

            # Armar salida con estado
            tecnicos = []
            for t in tecnicos_rows:
                rid = str(t.get('id'))
                info = respuestas_map.get(rid)
                estado = 'ok' if (info and info.get('enviada')) else ('ok' if info else 'pendiente')
                fecha = info.get('fecha') if info else None
                tecnicos.append({
                    'id': t.get('id'),
                    'nombre': t.get('nombre'),
                    'carpeta': t.get('carpeta'),
                    'supervisor': t.get('super'),
                    'fecha': fecha.strftime('%Y-%m-%d %H:%M:%S') if isinstance(fecha, datetime) else (fecha if fecha else None),
                    'estado': estado
                })

            return jsonify({'success': True, 'encuesta': {
                'id_encuesta': enc.get('id_encuesta'),
                'dirigida_a': dirigida_a,
                'audiencia_carpetas': aud_carpetas,
                'audiencia_supervisores': aud_supervisores,
                'audiencia_tecnicos': aud_tecnicos
            }, 'tecnicos': tecnicos})

        except mysql.connector.Error as e:
            logger.error(f"Error consultando audiencia/estado de encuesta {encuesta_id}: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            conn.close()

    @app.route('/api/encuestas/<int:encuesta_id>', methods=['PATCH'])
    def actualizar_encuesta(encuesta_id):
        data = request.get_json(silent=True) or {}
        campos = []
        valores = []
        # Campos permitidos de edición
        # Datos generales
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
        if 'con_puntaje' in data:
            campos.append('con_puntaje = %s')
            valores.append(1 if data.get('con_puntaje') else 0)
        if 'porcentaje_aprobacion' in data:
            try:
                pa = float(data.get('porcentaje_aprobacion'))
            except Exception:
                pa = 90.0
            if pa < 0: pa = 0.0
            if pa > 100: pa = 100.0
            campos.append('porcentaje_aprobacion = %s')
            valores.append(pa)
        if 'maximo_intentos' in data:
            try:
                mi = int(data.get('maximo_intentos'))
            except Exception:
                mi = 2
            if mi < 1: mi = 1
            campos.append('maximo_intentos = %s')
            valores.append(mi)
        if 'permitir_multiples_respuestas' in data:
            campos.append('permitir_multiples_respuestas = %s')
            valores.append(1 if data.get('permitir_multiples_respuestas') else 0)
        if 'modo_multiples_respuestas' in data:
            campos.append('modo_multiples_respuestas = %s')
            valores.append(data.get('modo_multiples_respuestas'))
        # Campos específicos de votaciones
        if 'tipo_encuesta' in data:
            tipo_encuesta = (data.get('tipo_encuesta') or '').strip()
            if tipo_encuesta not in ('encuesta', 'votacion'):
                return jsonify({'success': False, 'message': 'tipo_encuesta inválido'}), 400
            campos.append('tipo_encuesta = %s')
            valores.append(tipo_encuesta)
        if 'mostrar_resultados' in data:
            mostrar = 1 if bool(data.get('mostrar_resultados')) else 0
            campos.append('mostrar_resultados = %s')
            valores.append(mostrar)
        if 'fecha_inicio_votacion' in data:
            campos.append('fecha_inicio_votacion = %s')
            valores.append(data.get('fecha_inicio_votacion') or None)
        if 'fecha_fin_votacion' in data:
            campos.append('fecha_fin_votacion = %s')
            valores.append(data.get('fecha_fin_votacion') or None)
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
        # Soportar JSON y multipart con 'payload' + archivo 'imagen_referencia'
        data = request.get_json(silent=True)
        if not data:
            try:
                payload_str = request.form.get('payload')
                data = json.loads(payload_str) if payload_str else {}
            except Exception:
                data = {}
        data = data or {}

        tipo = data.get('tipo')
        texto = data.get('texto')
        ayuda = data.get('ayuda')
        requerida = 1 if data.get('requerida', False) else 0
        orden = data.get('orden', 0)
        config = data.get('config')
        opciones = data.get('opciones', [])
        seccion_id = data.get('seccion_id') if data.get('seccion_id') not in (None, '', 'null') else None
        imagen_referencia_url = data.get('imagen_referencia_url')

        if not tipo or not texto:
            return jsonify({'success': False, 'message': 'Tipo y texto son obligatorios'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor()

            # Guardar imagen de referencia si viene adjunta
            try:
                f = request.files.get('imagen_referencia')
            except Exception:
                f = None
            if f and getattr(f, 'filename', ''):
                try:
                    base_dir = os.path.join('static', 'uploads', 'encuestas', str(encuesta_id), 'preguntas')
                    os.makedirs(base_dir, exist_ok=True)
                    filename = secure_filename(getattr(f, 'filename', '') or 'imagen')
                    name, ext = os.path.splitext(filename)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
                    final_name = f"preg_{encuesta_id}_{timestamp}{ext or '.bin'}"
                    path = os.path.join(base_dir, final_name)
                    f.save(path)
                    imagen_referencia_url = '/' + path.replace('\\', '/')
                except Exception as e:
                    logger.warning(f"No se pudo guardar imagen de referencia: {e}")

            config_json = json.dumps(config, ensure_ascii=False) if config else None
            cursor.execute(
                """
                INSERT INTO encuesta_preguntas (encuesta_id, seccion_id, tipo, texto, ayuda, requerida, orden, config_json, imagen_referencia_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (encuesta_id, seccion_id, tipo, texto, ayuda, requerida, orden, config_json, imagen_referencia_url)
            )
            pregunta_id = cursor.lastrowid

            # Insertar opciones si aplica
            tipos_con_opciones = {'opcion_multiple', 'seleccion_unica', 'checkbox', 'dropdown'}
            if opciones and tipo in tipos_con_opciones:
                for idx, op in enumerate(opciones):
                    texto_op = (op.get('texto') or '').strip()
                    valor_op = op.get('valor')
                    es_correcta = 1 if op.get('es_correcta', False) else 0
                    puntaje = op.get('puntaje')
                    if not texto_op:
                        texto_op = f"Opción {idx+1}"
                    cursor.execute(
                        """
                        INSERT INTO encuesta_opciones (pregunta_id, texto, valor, es_correcta, puntaje, orden)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (pregunta_id, texto_op, valor_op, es_correcta, puntaje, idx)
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
        # Soportar JSON y multipart con 'payload' + archivo 'imagen_referencia'
        data = request.get_json(silent=True)
        if not data:
            try:
                payload_str = request.form.get('payload')
                data = json.loads(payload_str) if payload_str else {}
            except Exception:
                data = {}
        data = data or {}

        tipo = data.get('tipo')
        texto = data.get('texto')
        ayuda = data.get('ayuda')
        requerida = data.get('requerida')
        opciones = data.get('opciones')
        seccion_id = data.get('seccion_id')
        imagen_referencia_url = data.get('imagen_referencia_url')

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
            if seccion_id is not None:
                sets.append('seccion_id = %s')
                vals.append(seccion_id if seccion_id != 'null' else None)
            # Manejo de imagen de referencia
            try:
                f = request.files.get('imagen_referencia')
            except Exception:
                f = None
            if f and getattr(f, 'filename', ''):
                try:
                    base_dir = os.path.join('static', 'uploads', 'encuestas', str(encuesta_id), 'preguntas')
                    os.makedirs(base_dir, exist_ok=True)
                    filename = secure_filename(getattr(f, 'filename', '') or 'imagen')
                    name, ext = os.path.splitext(filename)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
                    final_name = f"preg_{encuesta_id}_{pregunta_id}_{timestamp}{ext or '.bin'}"
                    path = os.path.join(base_dir, final_name)
                    f.save(path)
                    imagen_referencia_url = '/' + path.replace('\\', '/')
                    sets.append('imagen_referencia_url = %s')
                    vals.append(imagen_referencia_url)
                except Exception as e:
                    logger.warning(f"No se pudo guardar imagen de referencia (update): {e}")

            if imagen_referencia_url is not None and not (f and getattr(f, 'filename', '')):
                sets.append('imagen_referencia_url = %s')
                vals.append(imagen_referencia_url if imagen_referencia_url != 'null' else None)

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
                        es_correcta = 1 if op.get('es_correcta', False) else 0
                        puntaje = op.get('puntaje')
                        if not texto_op:
                            texto_op = f"Opción {idx+1}"
                        cur.execute(
                            """
                            INSERT INTO encuesta_opciones (pregunta_id, texto, valor, es_correcta, puntaje, orden)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (pregunta_id, texto_op, valor_op, es_correcta, puntaje, idx)
                        )

            connection.commit()
            cur.close()
            return jsonify({'success': True})
        except mysql.connector.Error as e:
            logger.error(f"Error actualizando pregunta {pregunta_id}: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    # ============================================================================
    # ENDPOINTS PARA SECCIONES
    # ============================================================================

    @app.route('/api/encuestas/<int:encuesta_id>/secciones', methods=['GET'])
    def obtener_secciones_encuesta(encuesta_id):
        """Obtener todas las secciones de una encuesta"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id_seccion, encuesta_id, titulo, descripcion, orden, fecha_creacion, fecha_actualizacion
                FROM encuesta_secciones
                WHERE encuesta_id = %s
                ORDER BY orden ASC
                """,
                (encuesta_id,)
            )
            secciones = cursor.fetchall()
            cursor.close()
            return jsonify({'success': True, 'secciones': secciones})
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo secciones: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    # Alias: obtener una sección por ID sin requerir encuesta_id
    @app.route('/api/secciones/<int:seccion_id>', methods=['GET'])
    @login_required
    def obtener_seccion_por_id(seccion_id):
        """Obtener una sección por su ID"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id_seccion, encuesta_id, titulo, descripcion, orden
                FROM encuesta_secciones
                WHERE id_seccion = %s
                """,
                (seccion_id,)
            )
            seccion = cursor.fetchone()
            cursor.close()
            if not seccion:
                return jsonify({'success': False, 'message': 'Sección no encontrada'}), 404
            return jsonify({'success': True, 'seccion': seccion})
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo sección: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/encuestas/<int:encuesta_id>/secciones', methods=['POST'])
    def crear_seccion(encuesta_id):
        """Crear una nueva sección en una encuesta"""
        data = request.get_json(silent=True) or {}
        titulo = data.get('titulo', '').strip()
        descripcion = data.get('descripcion', '').strip()
        
        if not titulo:
            return jsonify({'success': False, 'message': 'El título de la sección es requerido'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor()
            
            # Obtener el máximo orden actual para esta encuesta
            cursor.execute(
                """
                SELECT COALESCE(MAX(orden), 0) + 1 as nuevo_orden
                FROM encuesta_secciones
                WHERE encuesta_id = %s
                """,
                (encuesta_id,)
            )
            nuevo_orden = cursor.fetchone()[0]
            
            # Insertar la nueva sección
            cursor.execute(
                """
                INSERT INTO encuesta_secciones (encuesta_id, titulo, descripcion, orden)
                VALUES (%s, %s, %s, %s)
                """,
                (encuesta_id, titulo, descripcion, nuevo_orden)
            )
            seccion_id = cursor.lastrowid
            
            connection.commit()
            cursor.close()
            
            return jsonify({'success': True, 'id_seccion': seccion_id, 'message': 'Sección creada exitosamente'})
        except mysql.connector.Error as e:
            logger.error(f"Error creando sección: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    # Alias: actualizar sección por ID sin requerir encuesta_id
    @app.route('/api/secciones/<int:seccion_id>', methods=['PATCH'])
    @login_required
    def actualizar_seccion_por_id(seccion_id):
        """Actualizar una sección por su ID (titulo/descripcion)"""
        data = request.get_json(silent=True) or {}
        titulo = data.get('titulo')
        descripcion = data.get('descripcion')

        if titulo is not None:
            titulo = titulo.strip()
            if not titulo:
                return jsonify({'success': False, 'message': 'El título de la sección no puede estar vacío'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor()

            # Verificar existencia
            cursor.execute("SELECT encuesta_id FROM encuesta_secciones WHERE id_seccion = %s", (seccion_id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'success': False, 'message': 'Sección no encontrada'}), 404

            update_fields = []
            params = []
            if titulo is not None:
                update_fields.append("titulo = %s")
                params.append(titulo)
            if descripcion is not None:
                update_fields.append("descripcion = %s")
                params.append(descripcion)

            if not update_fields:
                return jsonify({'success': False, 'message': 'No hay campos para actualizar'}), 400

            params.append(seccion_id)
            query = f"""
                UPDATE encuesta_secciones
                SET {', '.join(update_fields)}
                WHERE id_seccion = %s
            """
            cursor.execute(query, params)

            if cursor.rowcount == 0:
                return jsonify({'success': False, 'message': 'Sección no encontrada'}), 404

            connection.commit()
            cursor.close()
            return jsonify({'success': True, 'message': 'Sección actualizada exitosamente'})
        except mysql.connector.Error as e:
            logger.error(f"Error actualizando sección: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    # Alias: eliminar sección por ID sin requerir encuesta_id
    @app.route('/api/secciones/<int:seccion_id>', methods=['DELETE'])
    @login_required
    def eliminar_seccion_por_id(seccion_id):
        """Eliminar una sección por su ID"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor()

            # Obtener encuesta_id asociado para logging/coherencia
            cursor.execute("SELECT encuesta_id FROM encuesta_secciones WHERE id_seccion = %s", (seccion_id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'success': False, 'message': 'Sección no encontrada'}), 404

            # Mover preguntas a "sin sección"
            cursor.execute(
                """
                UPDATE encuesta_preguntas
                SET seccion_id = NULL
                WHERE seccion_id = %s
                """,
                (seccion_id,)
            )

            # Eliminar la sección
            cursor.execute(
                """
                DELETE FROM encuesta_secciones
                WHERE id_seccion = %s
                """,
                (seccion_id,)
            )

            if cursor.rowcount == 0:
                return jsonify({'success': False, 'message': 'Sección no encontrada'}), 404

            connection.commit()
            cursor.close()
            return jsonify({'success': True, 'message': 'Sección eliminada exitosamente'})
        except mysql.connector.Error as e:
            logger.error(f"Error eliminando sección: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/encuestas/<int:encuesta_id>/secciones/<int:seccion_id>', methods=['PATCH'])
    def actualizar_seccion(encuesta_id, seccion_id):
        """Actualizar una sección existente"""
        data = request.get_json(silent=True) or {}
        titulo = data.get('titulo')
        descripcion = data.get('descripcion')
        
        if titulo is not None:
            titulo = titulo.strip()
            if not titulo:
                return jsonify({'success': False, 'message': 'El título de la sección no puede estar vacío'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor()
            
            # Construir la consulta dinámicamente
            update_fields = []
            params = []
            
            if titulo is not None:
                update_fields.append("titulo = %s")
                params.append(titulo)
            
            if descripcion is not None:
                update_fields.append("descripcion = %s")
                params.append(descripcion)
            
            if not update_fields:
                return jsonify({'success': False, 'message': 'No hay campos para actualizar'}), 400
            
            params.append(seccion_id)
            params.append(encuesta_id)
            
            query = f"""
                UPDATE encuesta_secciones
                SET {', '.join(update_fields)}
                WHERE id_seccion = %s AND encuesta_id = %s
                """
            
            cursor.execute(query, params)
            
            if cursor.rowcount == 0:
                return jsonify({'success': False, 'message': 'Sección no encontrada'}), 404
            
            connection.commit()
            cursor.close()
            
            return jsonify({'success': True, 'message': 'Sección actualizada exitosamente'})
        except mysql.connector.Error as e:
            logger.error(f"Error actualizando sección: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/encuestas/<int:encuesta_id>/secciones/<int:seccion_id>', methods=['DELETE'])
    def eliminar_seccion(encuesta_id, seccion_id):
        """Eliminar una sección"""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor()
            
            # Primero, mover todas las preguntas de esta sección a "sin sección" (NULL)
            cursor.execute(
                """
                UPDATE encuesta_preguntas
                SET seccion_id = NULL
                WHERE seccion_id = %s AND encuesta_id = %s
                """,
                (seccion_id, encuesta_id)
            )
            
            # Luego eliminar la sección
            cursor.execute(
                """
                DELETE FROM encuesta_secciones
                WHERE id_seccion = %s AND encuesta_id = %s
                """,
                (seccion_id, encuesta_id)
            )
            
            if cursor.rowcount == 0:
                return jsonify({'success': False, 'message': 'Sección no encontrada'}), 404
            
            connection.commit()
            cursor.close()
            
            return jsonify({'success': True, 'message': 'Sección eliminada exitosamente'})
        except mysql.connector.Error as e:
            logger.error(f"Error eliminando sección: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/encuestas/<int:encuesta_id>/secciones/orden', methods=['PATCH'])
    def actualizar_orden_secciones(encuesta_id):
        """Actualizar el orden de las secciones"""
        data = request.get_json(silent=True) or {}
        secciones_orden = data.get('secciones', [])
        
        if not isinstance(secciones_orden, list):
            return jsonify({'success': False, 'message': 'Formato inválido para el orden de secciones'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor()
            
            for orden, seccion_id in enumerate(secciones_orden):
                cursor.execute(
                    """
                    UPDATE encuesta_secciones
                    SET orden = %s
                    WHERE id_seccion = %s AND encuesta_id = %s
                    """,
                    (orden, seccion_id, encuesta_id)
                )
            
            connection.commit()
            cursor.close()
            
            return jsonify({'success': True, 'message': 'Orden de secciones actualizado exitosamente'})
        except mysql.connector.Error as e:
            logger.error(f"Error actualizando orden de secciones: {e}")
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

            # Validar según modo de respuestas configurado
            cursor.execute("SELECT permitir_multiples_respuestas, modo_multiples_respuestas, fecha_inicio, fecha_fin FROM encuestas WHERE id_encuesta = %s", (encuesta_id,))
            enc = cursor.fetchone()
            permitir_multi = 1
            modo_multi = 'por_mes'
            fecha_inicio = None
            fecha_fin = None
            if enc:
                permitir_multi = int(enc[0]) if enc[0] is not None else 1
                modo_multi = enc[1] or 'por_mes'
                fecha_inicio = enc[2]
                fecha_fin = enc[3]

            if permitir_multi == 0 or modo_multi == 'unica':
                cursor.execute(
                    """
                    SELECT 1 FROM encuesta_respuestas
                    WHERE encuesta_id = %s AND usuario_id = %s AND estado = 'enviada'
                    LIMIT 1
                    """,
                    (encuesta_id, usuario_id)
                )
                if cursor.fetchone():
                    return jsonify({'success': False, 'message': 'Ya respondiste esta encuesta'}), 409
            elif modo_multi == 'por_mes':
                # Si la encuesta maneja puntaje y tiene más de 1 intento, permitir reintentar
                try:
                    cursor.execute("SELECT con_puntaje, maximo_intentos FROM encuestas WHERE id_encuesta = %s", (encuesta_id,))
                    row_cfg = cursor.fetchone()
                    con_puntaje_flag_tmp = int(row_cfg[0]) if row_cfg and row_cfg[0] is not None else 0
                    max_intentos_tmp = int(row_cfg[1]) if row_cfg and row_cfg[1] is not None else 1
                except Exception:
                    con_puntaje_flag_tmp = 0
                    max_intentos_tmp = 1
                # Contar intentos del mes actual
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM encuesta_respuestas
                    WHERE encuesta_id = %s AND usuario_id = %s AND estado = 'enviada'
                      AND YEAR(fecha_respuesta) = YEAR(NOW())
                      AND MONTH(fecha_respuesta) = MONTH(NOW())
                    """,
                    (encuesta_id, usuario_id)
                )
                cnt_mes = cursor.fetchone()
                intentos_mes = 0
                try:
                    intentos_mes = int(cnt_mes[0]) if cnt_mes and cnt_mes[0] is not None else 0
                except Exception:
                    intentos_mes = 0
                if con_puntaje_flag_tmp:
                    if intentos_mes >= max_intentos_tmp:
                        return jsonify({'success': False, 'message': 'Has alcanzado el máximo de intentos'}), 409
                    # Si aún hay intentos disponibles, permitir continuar (no bloquear por mes)
                else:
                    if intentos_mes > 0:
                        return jsonify({'success': False, 'message': 'Ya respondiste esta encuesta en el mes actual'}), 409
            elif modo_multi == 'por_periodo':
                cursor.execute(
                    """
                    SELECT 1 FROM encuesta_respuestas r
                    JOIN encuestas e ON e.id_encuesta = r.encuesta_id
                    WHERE r.encuesta_id = %s AND r.usuario_id = %s AND r.estado = 'enviada'
                      AND (
                        (e.fecha_inicio IS NOT NULL AND e.fecha_fin IS NOT NULL AND r.fecha_respuesta BETWEEN e.fecha_inicio AND e.fecha_fin)
                        OR (e.fecha_inicio IS NOT NULL AND e.fecha_fin IS NULL AND r.fecha_respuesta >= e.fecha_inicio)
                        OR (e.fecha_inicio IS NULL AND e.fecha_fin IS NOT NULL AND r.fecha_respuesta <= e.fecha_fin)
                      )
                    LIMIT 1
                    """,
                    (encuesta_id, usuario_id)
                )
                if cursor.fetchone():
                    return jsonify({'success': False, 'message': 'Ya respondiste esta encuesta en el periodo activo'}), 409

            # Si la encuesta es con puntaje, verificar intentos y preparar cálculo
            cursor.execute("SELECT con_puntaje, porcentaje_aprobacion, maximo_intentos FROM encuestas WHERE id_encuesta = %s", (encuesta_id,))
            row_enc = cursor.fetchone()
            con_puntaje_flag = 1
            pct_aprob = 90.0
            max_intentos = 2
            if row_enc:
                con_puntaje_flag = int(row_enc[0]) if row_enc[0] is not None else 0
                try:
                    pct_aprob = float(row_enc[1]) if row_enc[1] is not None else 90.0
                except Exception:
                    pct_aprob = 90.0
                try:
                    max_intentos = int(row_enc[2]) if row_enc[2] is not None else 2
                except Exception:
                    max_intentos = 2
                if pct_aprob < 0: pct_aprob = 0.0
                if pct_aprob > 100: pct_aprob = 100.0
                if max_intentos < 1: max_intentos = 1
            # En modo única (o cuando no se permiten múltiples) el máximo de intentos es 1
            try:
                if (permitir_multi == 0) or (str(modo_multi or '').lower() == 'unica'):
                    max_intentos = 1
            except Exception:
                pass

            # Control de intentos (aplica si hay puntaje); respeta el modo configurado
            intentos_previos = 0
            if con_puntaje_flag:
                if modo_multi == 'por_mes':
                    cursor.execute(
                        """
                        SELECT COUNT(*) FROM encuesta_respuestas
                        WHERE encuesta_id = %s AND usuario_id = %s AND estado = 'enviada'
                          AND YEAR(fecha_respuesta) = YEAR(NOW())
                          AND MONTH(fecha_respuesta) = MONTH(NOW())
                        """,
                        (encuesta_id, usuario_id)
                    )
                elif modo_multi == 'por_periodo':
                    cursor.execute(
                        """
                        SELECT COUNT(*) FROM encuesta_respuestas r
                        JOIN encuestas e ON e.id_encuesta = r.encuesta_id
                        WHERE r.encuesta_id = %s AND r.usuario_id = %s AND r.estado = 'enviada'
                          AND (
                            (e.fecha_inicio IS NOT NULL AND e.fecha_fin IS NOT NULL AND r.fecha_respuesta BETWEEN e.fecha_inicio AND e.fecha_fin)
                            OR (e.fecha_inicio IS NOT NULL AND e.fecha_fin IS NULL AND r.fecha_respuesta >= e.fecha_inicio)
                            OR (e.fecha_inicio IS NULL AND e.fecha_fin IS NOT NULL AND r.fecha_respuesta <= e.fecha_fin)
                          )
                        """,
                        (encuesta_id, usuario_id)
                    )
                else:
                    cursor.execute(
                        """
                        SELECT COUNT(*) FROM encuesta_respuestas
                        WHERE encuesta_id = %s AND usuario_id = %s AND estado = 'enviada'
                        """,
                        (encuesta_id, usuario_id)
                    )
                cnt = cursor.fetchone()
                try:
                    intentos_previos = int(cnt[0]) if cnt and cnt[0] is not None else 0
                except Exception:
                    intentos_previos = 0
                if intentos_previos >= max_intentos:
                    return jsonify({'success': False, 'message': 'Has alcanzado el máximo de intentos'}), 409

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
            def save_uploaded_file(file_storage, encuesta_id, pregunta_id=None):
                if pregunta_id:
                    base_dir = os.path.join('static', 'uploads', 'encuestas', str(encuesta_id), 'preguntas')
                else:
                    base_dir = os.path.join('static', 'uploads', 'encuestas', str(encuesta_id))
                os.makedirs(base_dir, exist_ok=True)
                filename = secure_filename(getattr(file_storage, 'filename', '') or 'imagen')
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
                if pregunta_id:
                    final_name = f"preg_{pregunta_id}_{timestamp}{ext or '.bin'}"
                else:
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
                        archivo_url = save_uploaded_file(f, encuesta_id, pregunta_id)
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

            # Si la encuesta maneja puntaje, calcular aprobación por respuestas correctas
            resultado_eval = None
            if con_puntaje_flag:
                try:
                    # Contar preguntas evaluables (con opciones y al menos una correcta) y cuántas se respondieron correctamente
                    tipos_con_opciones = ('opcion_multiple','seleccion_unica','checkbox','dropdown')
                    cursor.execute(
                        """
                        SELECT id_pregunta, tipo
                        FROM encuesta_preguntas
                        WHERE encuesta_id = %s AND tipo IN ('opcion_multiple','seleccion_unica','checkbox','dropdown')
                        """,
                        (encuesta_id,)
                    )
                    preguntas_rows = cursor.fetchall() or []
                    total_evaluable = 0
                    correctas = 0

                    for pr in preguntas_rows:
                        try:
                            p_id = pr[0]
                            p_tipo = pr[1]
                        except Exception:
                            # fallback por seguridad
                            p_id = pr.get('id_pregunta') if isinstance(pr, dict) else None
                            p_tipo = pr.get('tipo') if isinstance(pr, dict) else None
                        if not p_id:
                            continue

                        # Verificar que la pregunta tiene al menos una opción marcada como correcta
                        cursor.execute(
                            """
                            SELECT COUNT(*) FROM encuesta_opciones
                            WHERE pregunta_id = %s AND es_correcta = 1
                            """,
                            (p_id,)
                        )
                        row_cnt_cor = cursor.fetchone()
                        cnt_correct_opts = int(row_cnt_cor[0]) if row_cnt_cor and row_cnt_cor[0] is not None else 0
                        if cnt_correct_opts <= 0:
                            # No evaluable si no hay opciones correctas definidas
                            continue
                        total_evaluable += 1

                        if p_tipo in ('seleccion_unica','dropdown'):
                            # Correcta si la opción seleccionada está marcada como correcta
                            cursor.execute(
                                """
                                SELECT o.es_correcta
                                FROM encuesta_respuestas_detalle d
                                JOIN encuesta_opciones o ON o.id_opcion = d.opcion_id
                                WHERE d.respuesta_id = %s AND d.pregunta_id = %s
                                LIMIT 1
                                """,
                                (respuesta_id, p_id)
                            )
                            row_sel = cursor.fetchone()
                            es_cor = int(row_sel[0]) if row_sel and row_sel[0] is not None else 0
                            if es_cor == 1:
                                correctas += 1
                        elif p_tipo in ('opcion_multiple','checkbox'):
                            # Correcta si: seleccionó exactamente todas las opciones correctas y ninguna incorrecta
                            cursor.execute(
                                """
                                SELECT COUNT(*) FROM encuesta_respuestas_detalle
                                WHERE respuesta_id = %s AND pregunta_id = %s
                                """,
                                (respuesta_id, p_id)
                            )
                            row_sel_total = cursor.fetchone()
                            cnt_sel_total = int(row_sel_total[0]) if row_sel_total and row_sel_total[0] is not None else 0

                            cursor.execute(
                                """
                                SELECT COUNT(*)
                                FROM encuesta_respuestas_detalle d
                                JOIN encuesta_opciones o ON o.id_opcion = d.opcion_id
                                WHERE d.respuesta_id = %s AND d.pregunta_id = %s AND o.es_correcta = 0
                                """,
                                (respuesta_id, p_id)
                            )
                            row_sel_incor = cursor.fetchone()
                            cnt_sel_incor = int(row_sel_incor[0]) if row_sel_incor and row_sel_incor[0] is not None else 0

                            if cnt_sel_incor == 0 and cnt_sel_total == cnt_correct_opts and cnt_sel_total > 0:
                                correctas += 1
                        else:
                            # Tipos no evaluables
                            pass

                    porcentaje_obtenido = 0.0
                    if total_evaluable > 0:
                        porcentaje_obtenido = round((correctas / total_evaluable) * 100.0, 2)

                    aprobo = porcentaje_obtenido >= pct_aprob
                    intentos_totales = intentos_previos + 1

                    # Devolver resultado y si puede reintentar
                    resultado_eval = {
                        'correctas': correctas,
                        'total_preguntas': total_evaluable,
                        'porcentaje_obtenido': porcentaje_obtenido,
                        'porcentaje_aprobacion': pct_aprob,
                        'aprobado': aprobo,
                        'intentos_utilizados': intentos_totales,
                        'maximo_intentos': max_intentos,
                        'puede_reintentar': (not aprobo) and (intentos_totales < max_intentos),
                        # compatibilidad con frontend previo
                        'puntaje_total': porcentaje_obtenido
                    }
                except Exception as _e_calc:
                    logger.warning(f"No se pudo calcular evaluación por correctas: {_e_calc}")
                    # fallback: sin evaluación
                    resultado_eval = None

            # Persistir resultado de aprobación si aplica
            try:
                if con_puntaje_flag:
                    aprobado_val = None
                    porc_val = None
                    if resultado_eval is not None:
                        aprobado_val = 1 if (resultado_eval.get('aprobado')) else 0
                        porc_val = resultado_eval.get('porcentaje_obtenido')
                    cursor.execute(
                        """
                        UPDATE encuesta_respuestas
                        SET aprobado = %s, porcentaje_obtenido = %s
                        WHERE id_respuesta = %s
                        """,
                        (aprobado_val, porc_val, respuesta_id)
                    )
            except Exception as _e_upd:
                logger.warning(f"No se pudo actualizar aprobado/porcentaje_obtenido en respuesta {respuesta_id}: {_e_upd}")

            connection.commit()
            cursor.close()
            return jsonify({'success': True, 'id_respuesta': respuesta_id, 'evaluacion': resultado_eval})
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
        if formato not in ('excel', 'csv', 'zip'):
            formato = 'excel'

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT r.id_respuesta, r.usuario_id, r.fecha_respuesta, r.estado,
                       ro.nombre AS tecnico, ro.super AS supervisor, ro.carpeta AS carpeta,
                       d.pregunta_id, p.texto AS texto_pregunta, p.tipo,
                       d.valor_texto, d.valor_numero, d.opcion_id, o.texto AS texto_opcion, d.archivo_url, r.ip
                FROM encuesta_respuestas r
                JOIN encuesta_respuestas_detalle d ON d.respuesta_id = r.id_respuesta
                JOIN encuesta_preguntas p ON p.id_pregunta = d.pregunta_id
                LEFT JOIN encuesta_opciones o ON o.id_opcion = d.opcion_id
                LEFT JOIN recurso_operativo ro ON ro.id_codigo_consumidor = r.usuario_id
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

            # Transformar filas para incluir columnas pedidas: técnico, supervisor, fecha, pregunta y respuesta, estado
            def formatear_respuesta(r, formato_export='excel'):
                # Derivar valor de respuesta en texto
                if r.get('archivo_url'):
                    archivo_url = r.get('archivo_url')
                    if formato_export == 'zip':
                        # Para ZIP, generar hipervínculo relativo
                        # Extraer solo el nombre del archivo de la URL completa
                        import os
                        filename = os.path.basename(archivo_url)
                        return f'=HIPERVINCULO("imagenes/{filename}", "Ver imagen")'
                    return archivo_url
                if r.get('texto_opcion') is not None:
                    return r.get('texto_opcion')
                if r.get('valor_numero') is not None:
                    return str(r.get('valor_numero'))
                return r.get('valor_texto')

            export_rows = []
            for r in rows:
                estado_label = 'OK' if (r.get('estado') == 'enviada') else 'Pendiente'
                export_rows.append({
                    'Tecnico': r.get('tecnico') or str(r.get('usuario_id') or ''),
                    'Supervisor': r.get('supervisor') or '',
                    'Carpeta': r.get('carpeta') or '',
                    'Fecha': r.get('fecha_respuesta'),
                    'Estado': estado_label,
                    'Pregunta': r.get('texto_pregunta'),
                    'Respuesta': formatear_respuesta(r, formato)
                })

            if formato == 'csv':
                import io, csv
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=list(export_rows[0].keys()))
                writer.writeheader()
                writer.writerows(export_rows)
                response = make_response(output.getvalue())
                response.headers['Content-Type'] = 'text/csv; charset=utf-8'
                response.headers['Content-Disposition'] = f'attachment; filename=encuesta_{encuesta_id}_respuestas_{timestamp}.csv'
                return response
            elif formato == 'zip':
                # Exportación ZIP con Excel e imágenes
                try:
                    logger.info(f"Iniciando exportación ZIP para encuesta {encuesta_id}")
                    import pandas as pd
                    import io
                    import zipfile
                    import os
                    from werkzeug.utils import secure_filename
                    
                    # Crear Excel con hipervínculos relativos
                    output = io.BytesIO()
                    
                    # Por defecto exportar en wide-form en Excel (una fila por respuesta, columnas por pregunta)
                    wide_param = (request.args.get('wide', '').strip().lower())
                    wide_requested = True if wide_param in ('', '1', 'true', 'yes', 'si', 'sí', 'y') else False
                    
                    if wide_requested:
                        # Construir estructura wide usando id_respuesta como fila
                        # Columnas base
                        base_cols = ['Tecnico', 'Supervisor', 'Carpeta', 'Fecha', 'Estado']
                        # Descubrir preguntas únicas
                        preguntas_unicas = []
                        seen = set()
                        for r in rows:
                            txt = r.get('texto_pregunta')
                            if txt not in seen:
                                seen.add(txt)
                                preguntas_unicas.append(txt)
                        # Mapear respuesta -> fila
                        filas = {}
                        for r in rows:
                            resp_id = r.get('id_respuesta')
                            estado_label = 'OK' if (r.get('estado') == 'enviada') else 'Pendiente'
                            if resp_id not in filas:
                                filas[resp_id] = {
                                    'Tecnico': r.get('tecnico') or str(r.get('usuario_id') or ''),
                                    'Supervisor': r.get('supervisor') or '',
                                    'Carpeta': r.get('carpeta') or '',
                                    'Fecha': r.get('fecha_respuesta'),
                                    'Estado': estado_label,
                                }
                            ans = formatear_respuesta(r, formato)
                            col = r.get('texto_pregunta')
                            if col:
                                if col in filas[resp_id] and filas[resp_id][col]:
                                    # Concatenar múltiples respuestas para la misma pregunta
                                    filas[resp_id][col] = f"{filas[resp_id][col]} | {ans}" if ans else filas[resp_id][col]
                                else:
                                    filas[resp_id][col] = ans
                        # Ordenar columnas: base + preguntas
                        ordered_cols = base_cols + preguntas_unicas
                        df = pd.DataFrame(list(filas.values()))
                        # Asegurar orden de columnas y presencia de todas
                        for c in ordered_cols:
                            if c not in df.columns:
                                df[c] = None
                        df = df[ordered_cols]
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False, sheet_name=f"respuestas_{encuesta_id}")
                    else:
                        # long-form
                        df = pd.DataFrame(export_rows)
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False, sheet_name=f"respuestas_{encuesta_id}")
                    
                    # Crear archivo ZIP
                    zip_output = io.BytesIO()
                    with zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        # Agregar Excel al ZIP
                        zipf.writestr(f'encuesta_{encuesta_id}_respuestas_{timestamp}.xlsx', output.getvalue())
                        
                        # Agregar imágenes al ZIP - Obtener todas las URLs de imágenes desde la base de datos
                        cur.execute(
                            """
                            SELECT DISTINCT archivo_url 
                            FROM encuesta_respuestas_detalle 
                            WHERE archivo_url IS NOT NULL AND archivo_url != ''
                            AND respuesta_id IN (
                                SELECT id_respuesta FROM encuesta_respuestas WHERE encuesta_id = %s
                            )
                            """, (encuesta_id,)
                        )
                        image_urls = [row['archivo_url'] for row in cur.fetchall()]
                        logger.info(f"URLs de imágenes encontradas en BD: {len(image_urls)}")
                        logger.info(f"URLs: {image_urls}")
                        
                        # Descargar y agregar cada imagen al ZIP
                        images_added = 0
                        for image_url in image_urls:
                            try:
                                # Obtener solo el nombre del archivo de la URL
                                filename = os.path.basename(image_url)
                                if filename:
                                    # Construir la ruta local del archivo
                                    local_path = os.path.join('static', 'uploads', 'encuestas', str(encuesta_id), 'preguntas', filename)
                                    
                                    if os.path.exists(local_path):
                                        # Si el archivo existe localmente, agregarlo desde el sistema de archivos
                                        arcname = os.path.join('imagenes', filename)
                                        zipf.write(local_path, arcname)
                                        images_added += 1
                                        logger.info(f"Imagen local agregada al ZIP: {filename}")
                                    else:
                                        # Si no existe localmente, usar método más simple sin requests
                                        # Buscar en toda la estructura de uploads
                                        found = False
                                        for root, dirs, files in os.walk('static/uploads'):
                                            if filename in files:
                                                found_path = os.path.join(root, filename)
                                                arcname = os.path.join('imagenes', filename)
                                                zipf.write(found_path, arcname)
                                                images_added += 1
                                                logger.info(f"Imagen encontrada en {root} y agregada al ZIP: {filename}")
                                                found = True
                                                break
                                        
                                        if not found:
                                            logger.warning(f"Imagen no encontrada localmente: {filename}")
                            except Exception as e:
                                logger.error(f"Error procesando imagen {image_url}: {e}")
                        
                        logger.info(f"Total de imágenes agregadas al ZIP: {images_added}/{len(image_urls)}")
                    
                    # Cerrar explícitamente el archivo ZIP antes de obtener el valor
                    zip_output.seek(0)
                    response = make_response(zip_output.getvalue())
                    response.headers['Content-Type'] = 'application/zip'
                    response.headers['Content-Disposition'] = f'attachment; filename=encuesta_{encuesta_id}_respuestas_{timestamp}.zip'
                    return response
                    

                    
                except Exception as e:
                    logger.error(f"Error exportación ZIP encuesta {encuesta_id}: {e}")
                    logger.error(f"Tipo de error: {type(e).__name__}")
                    import traceback
                    logger.error(f"Traceback completo: {traceback.format_exc()}")
                    return jsonify({'success': False, 'message': f'Error en exportación ZIP: {e}'}), 500
            else:
                # Excel
                try:
                    import pandas as pd
                    import io
                    output = io.BytesIO()
                    # Por defecto exportar en wide-form en Excel (una fila por respuesta, columnas por pregunta)
                    wide_param = (request.args.get('wide', '').strip().lower())
                    wide_requested = True if wide_param in ('', '1', 'true', 'yes', 'si', 'sí', 'y') else False
                    if wide_requested:
                        # Construir estructura wide usando id_respuesta como fila
                        # Columnas base
                        base_cols = ['Tecnico', 'Supervisor', 'Carpeta', 'Fecha', 'Estado']
                        # Descubrir preguntas únicas
                        preguntas_unicas = []
                        seen = set()
                        for r in rows:
                            txt = r.get('texto_pregunta')
                            if txt not in seen:
                                seen.add(txt)
                                preguntas_unicas.append(txt)
                        # Mapear respuesta -> fila
                        filas = {}
                        for r in rows:
                            resp_id = r.get('id_respuesta')
                            estado_label = 'OK' if (r.get('estado') == 'enviada') else 'Pendiente'
                            if resp_id not in filas:
                                filas[resp_id] = {
                                    'Tecnico': r.get('tecnico') or str(r.get('usuario_id') or ''),
                                    'Supervisor': r.get('supervisor') or '',
                                    'Carpeta': r.get('carpeta') or '',
                                    'Fecha': r.get('fecha_respuesta'),
                                    'Estado': estado_label,
                                }
                            ans = formatear_respuesta(r, formato)
                            col = r.get('texto_pregunta')
                            if col:
                                if col in filas[resp_id] and filas[resp_id][col]:
                                    # Concatenar múltiples respuestas para la misma pregunta
                                    filas[resp_id][col] = f"{filas[resp_id][col]} | {ans}" if ans else filas[resp_id][col]
                                else:
                                    filas[resp_id][col] = ans
                        # Ordenar columnas: base + preguntas
                        ordered_cols = base_cols + preguntas_unicas
                        df = pd.DataFrame(list(filas.values()))
                        # Asegurar orden de columnas y presencia de todas
                        for c in ordered_cols:
                            if c not in df.columns:
                                df[c] = None
                        df = df[ordered_cols]
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False, sheet_name=f"respuestas_{encuesta_id}")
                    else:
                        # long-form
                        df = pd.DataFrame(export_rows)
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
                    writer = csv.DictWriter(output, fieldnames=list(export_rows[0].keys()))
                    writer.writeheader()
                    writer.writerows(export_rows)
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

    @app.route('/api/encuestas/<int:encuesta_id>/puntajes', methods=['GET'])
    def puntajes_encuesta(encuesta_id):
        """Devuelve los puntajes totales por usuario para una encuesta con puntaje habilitado."""
        user_id = session.get('user_id') or session.get('id_codigo_consumidor')
        if not user_id:
            return jsonify({'success': False, 'message': 'No autorizado'}), 401

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cur = conn.cursor(dictionary=True)
            
            # Verificar si la encuesta tiene puntaje habilitado
            cur.execute("SELECT con_puntaje FROM encuestas WHERE id_encuesta = %s", (encuesta_id,))
            encuesta = cur.fetchone()
            if not encuesta or not encuesta.get('con_puntaje'):
                return jsonify({'success': False, 'message': 'Esta encuesta no tiene puntaje habilitado'}), 400

            # Calcular puntajes totales por usuario
            cur.execute(
                """
                SELECT 
                    r.usuario_id,
                    ro.nombre AS tecnico,
                    ro.super AS supervisor,
                    ro.carpeta,
                    DATE_FORMAT(r.fecha_respuesta, %s) AS fecha_respuesta,
                    r.estado,
                    SUM(CASE WHEN o.puntaje IS NOT NULL THEN o.puntaje ELSE 0 END) AS puntaje_total
                FROM encuesta_respuestas r
                LEFT JOIN recurso_operativo ro ON ro.id_codigo_consumidor = r.usuario_id
                LEFT JOIN encuesta_respuestas_detalle d ON d.respuesta_id = r.id_respuesta
                LEFT JOIN encuesta_opciones o ON o.id_opcion = d.opcion_id
                WHERE r.encuesta_id = %s
                GROUP BY r.usuario_id, ro.nombre, ro.super, ro.carpeta, r.fecha_respuesta, r.estado
                ORDER BY puntaje_total DESC, ro.nombre
                """,
                ('%Y-%m-%d %H:%i:%s', encuesta_id)
            )
            puntajes = cur.fetchall() or []

            return jsonify({
                'success': True,
                'encuesta_id': encuesta_id,
                'puntajes': puntajes
            })
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo puntajes encuesta {encuesta_id}: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            conn.close()

    @app.route('/api/encuestas/<int:encuesta_id>/respuestas/<int:usuario_id>', methods=['GET'])
    def respuestas_usuario_encuesta(encuesta_id, usuario_id):
        """Devuelve las respuestas individuales de un usuario específico para una encuesta."""
        user_id = session.get('user_id') or session.get('id_codigo_consumidor')
        if not user_id:
            return jsonify({'success': False, 'message': 'No autorizado'}), 401

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cur = conn.cursor(dictionary=True)
            
            # Obtener todas las respuestas del usuario para esta encuesta
            cur.execute(
                """
                SELECT 
                    p.id_pregunta,
                    p.texto AS texto_pregunta,
                    p.tipo AS tipo_pregunta,
                    p.imagen_referencia_url,
                    d.valor_texto,
                    d.valor_numero,
                    d.archivo_url,
                    o.texto AS texto_opcion,
                    o.puntaje,
                    r.fecha_respuesta,
                    r.estado
                FROM encuesta_respuestas r
                JOIN encuesta_respuestas_detalle d ON d.respuesta_id = r.id_respuesta
                JOIN encuesta_preguntas p ON p.id_pregunta = d.pregunta_id
                LEFT JOIN encuesta_opciones o ON o.id_opcion = d.opcion_id
                WHERE r.encuesta_id = %s AND r.usuario_id = %s
                ORDER BY p.orden, p.id_pregunta
                """,
                (encuesta_id, usuario_id)
            )
            respuestas = cur.fetchall() or []

            if not respuestas:
                return jsonify({'success': False, 'message': 'No se encontraron respuestas para este usuario'}), 404

            # Formatear las respuestas para mostrar
            respuestas_formateadas = []
            for respuesta in respuestas:
                respuesta_formateada = {
                    'pregunta_id': respuesta['id_pregunta'],
                    'texto_pregunta': respuesta['texto_pregunta'],
                    'tipo_pregunta': respuesta['tipo_pregunta'],
                    'imagen_referencia_url': respuesta.get('imagen_referencia_url'),
                    'respuesta': None,
                    'puntaje': None
                }

                # Determinar el valor de la respuesta según el tipo de pregunta
                if respuesta['tipo_pregunta'] == 'opcion_multiple' or respuesta['tipo_pregunta'] == 'seleccion_unica':
                    respuesta_formateada['respuesta'] = respuesta['texto_opcion']
                    # Incluir puntaje si existe
                    if respuesta.get('puntaje') is not None:
                        respuesta_formateada['puntaje'] = respuesta['puntaje']
                elif respuesta['tipo_pregunta'] == 'texto':
                    respuesta_formateada['respuesta'] = respuesta['valor_texto']
                elif respuesta['tipo_pregunta'] == 'numero':
                    respuesta_formateada['respuesta'] = respuesta['valor_numero']
                elif respuesta['tipo_pregunta'] == 'imagen':
                    respuesta_formateada['respuesta'] = respuesta['archivo_url']
                elif respuesta['tipo_pregunta'] == 'seleccion_multiple':
                    # Para selección múltiple, necesitamos obtener todas las opciones seleccionadas
                    # Primero obtenemos el id_respuesta más reciente para este usuario y encuesta
                    cur.execute(
                        """
                        SELECT id_respuesta 
                        FROM encuesta_respuestas 
                        WHERE encuesta_id = %s AND usuario_id = %s 
                        ORDER BY fecha_respuesta DESC LIMIT 1
                        """,
                        (encuesta_id, usuario_id)
                    )
                    ultima_respuesta = cur.fetchone()
                    
                    if ultima_respuesta:
                        cur.execute(
                            """
                            SELECT o.texto, o.puntaje 
                            FROM encuesta_respuestas_detalle d
                            JOIN encuesta_opciones o ON o.id_opcion = d.opcion_id
                            WHERE d.respuesta_id = %s
                            AND d.pregunta_id = %s
                            """,
                            (ultima_respuesta['id_respuesta'], respuesta['id_pregunta'])
                        )
                        opciones = cur.fetchall()
                        respuesta_formateada['respuesta'] = ', '.join([op['texto'] for op in opciones])
                        # Sumar puntajes si existen
                        puntaje_total = sum([op['puntaje'] or 0 for op in opciones]) if opciones else 0
                        if puntaje_total > 0:
                            respuesta_formateada['puntaje'] = float(puntaje_total)
                    else:
                        respuesta_formateada['respuesta'] = 'Sin respuestas'

                respuestas_formateadas.append(respuesta_formateada)

            return jsonify({
                'success': True,
                'encuesta_id': encuesta_id,
                'usuario_id': usuario_id,
                'respuestas': respuestas_formateadas
            })
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo respuestas usuario {usuario_id} encuesta {encuesta_id}: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            conn.close()

    # ============================================================================
    # ENDPOINTS DE VOTACIONES
    # ============================================================================

    def _validar_encuesta_votacion(encuesta_id, cursor):
        """Valida que la encuesta exista y sea de tipo 'votacion'.
        Devuelve el registro de la encuesta (dict) si es válido, o None en caso contrario.
        """
        try:
            cursor.execute(
                """
                SELECT id_encuesta, titulo, estado, tipo_encuesta, mostrar_resultados,
                       fecha_inicio_votacion, fecha_fin_votacion, creado_por
                FROM encuestas WHERE id_encuesta = %s
                """,
                (encuesta_id,)
            )
            encuesta = cursor.fetchone()
            if not encuesta:
                return None
            if not isinstance(encuesta, dict):
                cols = [d[0] for d in cursor.description]
                encuesta = dict(zip(cols, encuesta))
            if (encuesta.get('tipo_encuesta') or 'encuesta') != 'votacion':
                return None
            return encuesta
        except Exception:
            return None

    @app.route('/api/votaciones/<int:encuesta_id>/candidatos', methods=['POST'])
    def crear_candidato(encuesta_id):
        """Crea un candidato para una encuesta de tipo votación."""
        data = request.get_json(silent=True)
        if not data:
            data = {
                'nombre': request.form.get('nombre'),
                'descripcion': request.form.get('descripcion')
            }
        data = data or {}
        nombre = (data.get('nombre') or '').strip()
        descripcion = data.get('descripcion')

        if not nombre:
            return jsonify({'success': False, 'message': 'El nombre del candidato es obligatorio'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor(dictionary=True)
            encuesta = _validar_encuesta_votacion(encuesta_id, cursor)
            if not encuesta:
                return jsonify({'success': False, 'message': 'Encuesta no encontrada o no es de tipo votación'}), 400

            foto_url = None
            try:
                f = request.files.get('foto')
            except Exception:
                f = None
            if f and getattr(f, 'filename', ''):
                try:
                    base_dir = os.path.join('static', 'uploads', 'votaciones', str(encuesta_id), 'candidatos')
                    os.makedirs(base_dir, exist_ok=True)
                    filename = secure_filename(getattr(f, 'filename', '') or 'foto')
                    name, ext = os.path.splitext(filename)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
                    final_name = f"cand_{encuesta_id}_{timestamp}{ext or '.bin'}"
                    path = os.path.join(base_dir, final_name)
                    f.save(path)
                    foto_url = '/' + path.replace('\\', '/')
                except Exception as e:
                    logger.warning(f"No se pudo guardar la foto del candidato: {e}")
            else:
                foto_url = data.get('foto_url')

            cursor.execute(
                "SELECT COALESCE(MAX(orden), 0) AS max_orden FROM candidatos WHERE id_encuesta = %s",
                (encuesta_id,)
            )
            row = cursor.fetchone() or {}
            next_orden = int(row.get('max_orden') or 0) + 1

            cursor.execute(
                """
                INSERT INTO candidatos (id_encuesta, nombre, descripcion, foto_url, orden)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (encuesta_id, nombre, descripcion, foto_url, next_orden)
            )
            candidato_id = cursor.lastrowid
            connection.commit()
            cursor.execute(
                "SELECT id_candidato, id_encuesta, nombre, descripcion, foto_url, orden, fecha_creacion FROM candidatos WHERE id_candidato = %s",
                (candidato_id,)
            )
            candidato = cursor.fetchone() or {}
            return jsonify({'success': True, 'candidato': candidato}), 201
        except mysql.connector.Error as e:
            logger.error(f"Error creando candidato: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/votaciones/<int:encuesta_id>/candidatos', methods=['GET'])
    def listar_candidatos(encuesta_id):
        """Lista los candidatos de una encuesta de votación."""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        try:
            cursor = connection.cursor(dictionary=True)
            encuesta = _validar_encuesta_votacion(encuesta_id, cursor)
            if not encuesta:
                return jsonify({'success': False, 'message': 'Encuesta no encontrada o no es de tipo votación'}), 400
            cursor.execute(
                """
                SELECT id_candidato, id_encuesta, nombre, descripcion, foto_url, orden, fecha_creacion
                FROM candidatos WHERE id_encuesta = %s ORDER BY orden ASC, id_candidato ASC
                """,
                (encuesta_id,)
            )
            candidatos = cursor.fetchall() or []
            return jsonify({'success': True, 'candidatos': candidatos, 'total': len(candidatos)})
        except mysql.connector.Error as e:
            logger.error(f"Error listando candidatos de encuesta {encuesta_id}: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/votaciones/<int:encuesta_id>/candidatos/<int:candidato_id>', methods=['DELETE'])
    def eliminar_candidato(encuesta_id, candidato_id):
        """Elimina un candidato de una encuesta de votación."""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id_candidato FROM candidatos WHERE id_candidato = %s AND id_encuesta = %s",
                (candidato_id, encuesta_id)
            )
            row = cursor.fetchone()
            if not row:
                return jsonify({'success': False, 'message': 'Candidato no existe o no pertenece a la encuesta'}), 404
            cursor.execute("DELETE FROM candidatos WHERE id_candidato = %s", (candidato_id,))
            connection.commit()
            return jsonify({'success': True})
        except mysql.connector.Error as e:
            logger.error(f"Error eliminando candidato {candidato_id} encuesta {encuesta_id}: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/votaciones/<int:encuesta_id>/votar', methods=['POST'])
    def registrar_voto(encuesta_id):
        """Registra un voto para un candidato en una encuesta de votación."""
        user_id = _get_usuario_id()
        if not user_id:
            return jsonify({'success': False, 'message': 'No autorizado'}), 401

        data = request.get_json(silent=True) or {}
        candidato_id = data.get('id_candidato')
        try:
            candidato_id = int(candidato_id)
        except Exception:
            candidato_id = None
        if not candidato_id:
            return jsonify({'success': False, 'message': 'id_candidato es obligatorio'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor(dictionary=True)
            encuesta = _validar_encuesta_votacion(encuesta_id, cursor)
            if not encuesta:
                return jsonify({'success': False, 'message': 'Encuesta no encontrada o no es de tipo votación'}), 400

            # Validar o garantizar existencia del usuario en tabla usuarios (para cumplir FK de votos)
            cursor.execute("SELECT idusuarios FROM usuarios WHERE idusuarios = %s", (user_id,))
            existe_usuario = cursor.fetchone()
            if not existe_usuario:
                cursor.execute(
                    "SELECT nombre, recurso_operativo_cedula FROM recurso_operativo WHERE id_codigo_consumidor = %s",
                    (user_id,)
                )
                ro = cursor.fetchone() or {}
                nombre = ro.get('nombre') or 'Usuario'
                cedula_raw = ro.get('recurso_operativo_cedula')
                try:
                    cedula = int(str(cedula_raw)) if cedula_raw is not None else 0
                except Exception:
                    cedula = 0
                try:
                    cursor.execute(
                        """
                        INSERT INTO usuarios (idusuarios, usuario_nombre, usuario_cedula, usuario_contraseña)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (user_id, nombre, cedula, 0)
                    )
                    connection.commit()
                except mysql.connector.Error:
                    return jsonify({'success': False, 'message': 'Usuario no válido para emitir voto'}), 401

            # Validar ventana de votación
            def _parse_dt(val):
                if val is None:
                    return None
                if isinstance(val, datetime):
                    return val
                try:
                    return datetime.fromisoformat(str(val))
                except Exception:
                    return None

            ahora = datetime.now()
            ini = _parse_dt(encuesta.get('fecha_inicio_votacion'))
            fin = _parse_dt(encuesta.get('fecha_fin_votacion'))
            if ini and ahora < ini:
                return jsonify({'success': False, 'message': 'La votación aún no ha iniciado'}), 400
            if fin and ahora > fin:
                return jsonify({'success': False, 'message': 'La votación ha finalizado'}), 400

            # Validar candidato pertenece a encuesta
            cursor.execute(
                "SELECT id_candidato FROM candidatos WHERE id_candidato = %s AND id_encuesta = %s",
                (candidato_id, encuesta_id)
            )
            cand = cursor.fetchone()
            if not cand:
                return jsonify({'success': False, 'message': 'Candidato no válido para esta encuesta'}), 400

            # Validar voto único
            cursor.execute(
                "SELECT id_voto FROM votos WHERE id_encuesta = %s AND id_usuario = %s",
                (encuesta_id, user_id)
            )
            if cursor.fetchone():
                return jsonify({'success': False, 'message': 'Ya has votado en esta encuesta'}), 409

            ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
            cursor.execute(
                """
                INSERT INTO votos (id_encuesta, id_candidato, id_usuario, ip_address)
                VALUES (%s, %s, %s, %s)
                """,
                (encuesta_id, candidato_id, user_id, ip_addr)
            )
            connection.commit()
            return jsonify({'success': True, 'message': 'Voto registrado'}), 201
        except mysql.connector.Error as e:
            msg = str(e)
            if 'Duplicate' in msg or 'UNIQUE' in msg:
                return jsonify({'success': False, 'message': 'Ya has votado en esta encuesta'}), 409
            logger.error(f"Error registrando voto: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

    @app.route('/api/votaciones/<int:encuesta_id>/resultados', methods=['GET'])
    def resultados_votacion(encuesta_id):
        """Devuelve el conteo por candidato y porcentajes si se permite mostrar resultados."""
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        try:
            cursor = connection.cursor(dictionary=True)
            encuesta = _validar_encuesta_votacion(encuesta_id, cursor)
            if not encuesta:
                return jsonify({'success': False, 'message': 'Encuesta no encontrada o no es de tipo votación'}), 400
            preview_flag = (str((request.args.get('preview') or '').strip().lower()) in ('1','true','yes'))
            user_id = _get_usuario_id()
            if not encuesta.get('mostrar_resultados'):
                if not (preview_flag and user_id and (str(user_id) == str(encuesta.get('creado_por')) or str(user_id) == '1988914')):
                    return jsonify({'success': False, 'message': 'La encuesta no permite mostrar resultados'}), 403

            cursor.execute(
                """
                SELECT c.id_candidato, c.nombre, c.descripcion, c.foto_url, c.orden,
                       COUNT(v.id_voto) AS votos
                FROM candidatos c
                LEFT JOIN votos v ON v.id_candidato = c.id_candidato AND v.id_encuesta = c.id_encuesta
                WHERE c.id_encuesta = %s
                GROUP BY c.id_candidato, c.nombre, c.descripcion, c.foto_url, c.orden
                ORDER BY c.orden ASC, c.id_candidato ASC
                """,
                (encuesta_id,)
            )
            resultados = cursor.fetchall() or []
            total_votos = sum(int(r.get('votos') or 0) for r in resultados)
            for r in resultados:
                votos = int(r.get('votos') or 0)
                r['porcentaje'] = (round((votos * 100.0 / total_votos), 2) if total_votos > 0 else 0.0)
            cursor.execute(
                """
                SELECT DATE_FORMAT(v.fecha_voto, %s) AS vote_date,
                       COUNT(v.id_voto) AS daily_count
                FROM votos v
                WHERE v.id_encuesta = %s
                GROUP BY DATE_FORMAT(v.fecha_voto, %s)
                ORDER BY vote_date ASC
                """,
                ('%Y-%m-%d', encuesta_id, '%Y-%m-%d')
            )
            daily_votes = cursor.fetchall() or []
            return jsonify({'success': True, 'encuesta_id': encuesta_id, 'total_votos': total_votos, 'resultados': resultados, 'daily_votes': daily_votes})
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo resultados de encuesta {encuesta_id}: {e}")
            return jsonify({'success': False, 'message': f'Error de base de datos: {e}'}), 500
        finally:
            connection.close()

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
    print("- GET /api/encuestas/<id>/puntajes")
