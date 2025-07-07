#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file, make_response, Response
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from functools import wraps
import bcrypt
from datetime import datetime, timedelta
import json
import csv
import io
from collections import defaultdict
import calendar
import pytz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.colors import blue
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import jwt
import logging
import base64
import re
import tempfile
from PIL import Image as PILImage
import secrets
import string
import hashlib
import uuid
import pandas as pd
import json
from datetime import datetime, timedelta
import io
import time
import zipfile
import re
import logging
from decimal import Decimal
#from models import Suministro  # Asegúrate de importar el modelo correcto

load_dotenv()

# Configuración de zona horaria
TIMEZONE = pytz.timezone('America/Bogota')

# Remove debug print statements for environment variables
# print(f"MYSQL_HOST: {os.getenv('MYSQL_HOST')}")
# print(f"MYSQL_USER: {os.getenv('MYSQL_USER')}")
# print(f"MYSQL_PASSWORD: {os.getenv('MYSQL_PASSWORD')}")
# print(f"MYSQL_DB: {os.getenv('MYSQL_DB')}")
# print(f"MYSQL_PORT: {os.getenv('MYSQL_PORT')}")

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Configuración de logging
logging.basicConfig(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT')),
    'time_zone': '+00:00'  # Configurar MySQL para usar UTC
}

# Función para obtener conexión a la base de datos
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        return None

# Función para obtener la fecha y hora actual en Bogotá
def get_bogota_datetime():
    return datetime.now(TIMEZONE)

# Función para convertir una fecha UTC a fecha de Bogotá
def convert_to_bogota_time(utc_dt):
    if utc_dt.tzinfo is None:
        utc_dt = pytz.UTC.localize(utc_dt)
    return utc_dt.astimezone(TIMEZONE)

# Probar la conexión a la base de datos
try:
    connection = get_db_connection()
    if connection is None:
        raise Exception('Failed to establish a database connection.')
    connection.close()
except Exception as e:
    pass

# Roles definition
ROLES = {
    '1': 'administrativo',
    '2': 'tecnicos',
    '3': 'operativo',
    '4': 'contabilidad',
    '5': 'logistica'
}

# Decorador para requerir rol específico
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session:
                flash('Por favor inicia sesión para acceder a esta página.', 'warning')
                return redirect(url_for('login'))
            if session.get('user_role') != role and session.get('user_role') != 'administrativo':
                flash('No tienes permisos para acceder a esta página.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Login required decorator
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            if role and session.get('user_role') != role and session.get('user_role') != 'administrativo':
                flash("No tienes permisos para acceder a esta página.", 'danger')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/register', methods=['GET', 'POST'])
@login_required(role='administrativo')  # Solo los administrativos pueden registrar usuarios
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role_id = request.form['role_id']

        # Generar salt y hash
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        try:
            connection = get_db_connection()
            if connection is None:
                flash('Error de conexión a la base de datos.', 'error')
                return redirect(url_for('dashboard'))
                
            cursor = connection.cursor(dictionary=True)
            cursor.execute("INSERT INTO recurso_operativo (recurso_operativo_cedula, recurso_operativo_password, id_roles) VALUES (%s, %s, %s)",
                        (username, hashed_password, role_id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Usuario registrado exitosamente.', 'success')
            return redirect(url_for('dashboard'))
        except Error as e:
            flash(f'Error al registrar usuario: {str(e)}', 'error')
            return redirect(url_for('dashboard'))

    return redirect(url_for('dashboard'))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Añadir logging para depuración
        app.logger.info("Intento de inicio de sesión recibido")
        
        # Obtener credenciales del formulario
        username = request.form.get('username', '')
        password = request.form.get('password', '').encode('utf-8')
        
        # Validación básica
        if not username or not password:
            app.logger.warning("Intento de inicio de sesión con campos vacíos")
            return jsonify({
                'status': 'error', 
                'message': 'Por favor ingrese usuario y contraseña'
            }), 400

        connection = None
        cursor = None
        try:
            # Intentar conexión a la base de datos
            app.logger.info(f"Intentando conectar a la base de datos para usuario: {username}")
            connection = get_db_connection()
            
            if connection is None:
                app.logger.error("Error al conectar con la base de datos")
                return jsonify({
                    'status': 'error', 
                    'message': 'Error de conexión a la base de datos. Por favor intente más tarde.'
                }), 500
                
            cursor = connection.cursor(dictionary=True)
            
            # Buscar usuario
            app.logger.info(f"Consultando usuario con cedula: {username}")
            cursor.execute("SELECT id_codigo_consumidor, id_roles, recurso_operativo_password, nombre FROM recurso_operativo WHERE recurso_operativo_cedula = %s", (username,))
            user = cursor.fetchone()

            # Verificar si el usuario existe
            if not user:
                app.logger.warning(f"Usuario no encontrado: {username}")
                return jsonify({
                    'status': 'error', 
                    'message': 'Usuario o contraseña inválidos'
                }), 401
            
            # Verificar contraseña
            app.logger.info("Verificando contraseña")
            stored_password = user['recurso_operativo_password']
            
            # Asegurar que stored_password es bytes
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            
            # Verificar si el hash está en formato correcto
            if not stored_password.startswith(b'$2b$') and not stored_password.startswith(b'$2a$'):
                app.logger.error(f"Formato de contraseña inválido para usuario: {username}")
                return jsonify({
                    'status': 'error', 
                    'message': 'Error en el formato de la contraseña almacenada. Contacte al administrador.'
                }), 500
            
            try:
                # Verificar contraseña con bcrypt
                if bcrypt.checkpw(password, stored_password):
                    app.logger.info(f"Inicio de sesión exitoso para: {username}")
                    
                    # Establecer variables de sesión
                    session['user_id'] = user['id_codigo_consumidor']
                    session['user_role'] = ROLES.get(str(user['id_roles']))
                    session['user_name'] = user['nombre']
                    
                    app.logger.info(f"Sesión establecida: ID={user['id_codigo_consumidor']}, Rol={ROLES.get(str(user['id_roles']))}")

                    # Verificar vencimientos para el usuario
                    try:
                        cursor.execute("""
                            SELECT 
                                fecha_vencimiento_licencia,
                                fecha_vencimiento_soat,
                                fecha_vencimiento_tecnomecanica
                            FROM preoperacional 
                            WHERE id_codigo_consumidor = %s
                            ORDER BY fecha DESC 
                            LIMIT 1
                        """, (user['id_codigo_consumidor'],))
                        
                        ultimo_registro = cursor.fetchone()
                        if ultimo_registro:
                            fecha_actual = datetime.now().date()
                            mensajes_vencimiento = []
                            
                            if ultimo_registro['fecha_vencimiento_licencia']:
                                dias_licencia = (ultimo_registro['fecha_vencimiento_licencia'] - fecha_actual).days
                                if 0 <= dias_licencia <= 30:
                                    mensajes_vencimiento.append(f'Tu licencia de conducción vence en {dias_licencia} días')
                            
                            if ultimo_registro['fecha_vencimiento_soat']:
                                dias_soat = (ultimo_registro['fecha_vencimiento_soat'] - fecha_actual).days
                                if 0 <= dias_soat <= 30:
                                    mensajes_vencimiento.append(f'El SOAT vence en {dias_soat} días')
                            
                            if ultimo_registro['fecha_vencimiento_tecnomecanica']:
                                dias_tecno = (ultimo_registro['fecha_vencimiento_tecnomecanica'] - fecha_actual).days
                                if 0 <= dias_tecno <= 30:
                                    mensajes_vencimiento.append(f'La tecnomecánica vence en {dias_tecno} días')
                            
                            if mensajes_vencimiento:
                                flash('¡ATENCIÓN! ' + '. '.join(mensajes_vencimiento), 'warning')
                    except Exception as e:
                        app.logger.error(f"Error al verificar vencimientos: {str(e)}")
                        # No bloqueamos el inicio de sesión por este error
                    
                    # Cerrar conexión a la base de datos
                    if cursor:
                        cursor.close()
                    if connection:
                        connection.close()

                    # Si la solicitud espera JSON, devolver respuesta JSON
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            'status': 'success',
                            'message': 'Inicio de sesión exitoso',
                            'user_id': user['id_codigo_consumidor'],
                            'user_role': ROLES.get(str(user['id_roles'])),
                            'user_name': user['nombre'],
                            'redirect_url': url_for('dashboard')
                        })
                    # Si es una solicitud normal, redirigir
                    return redirect(url_for('dashboard'))
                else:
                    app.logger.warning(f"Contraseña incorrecta para usuario: {username}")
                    return jsonify({
                        'status': 'error', 
                        'message': 'Usuario o contraseña inválidos'
                    }), 401
            except Exception as e:
                app.logger.error(f"Error al verificar contraseña: {str(e)}")
                return jsonify({
                    'status': 'error', 
                    'message': 'Error al verificar credenciales. Intente nuevamente.'
                }), 500

        except mysql.connector.Error as e:
            app.logger.error(f"Error de MySQL: {str(e)}")
            return jsonify({
                'status': 'error', 
                'message': f'Error de base de datos: {str(e)}'
            }), 500
        except Exception as e:
            app.logger.error(f"Error inesperado: {str(e)}")
            # Imprimir stack trace para depuración
            import traceback
            app.logger.error(traceback.format_exc())
            return jsonify({
                'status': 'error', 
                'message': 'Error interno del servidor. Por favor contacte al administrador.'
            }), 500
        finally:
            # Asegurarse de cerrar los recursos
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            app.logger.info("Recursos de base de datos liberados")

    # Para solicitudes GET simplemente mostrar la plantilla de login
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # Obtener el rol del usuario antes de cerrar sesión para personalizar el mensaje
    user_role = session.get('user_role', '')
    
    # Limpiar todas las variables de sesión
    session.clear()
    
    # Asegurarse de que la sesión se elimine
    if session.get('user_id'):
        session.pop('user_id')
    if session.get('user_role'):
        session.pop('user_role')
    
    # Mensaje personalizado según el rol
    if user_role:
        flash(f'Has cerrado sesión exitosamente. ¡Hasta pronto, {user_role.title()}!', 'info')
    else:
        flash('Has cerrado sesión exitosamente.', 'info')
    
    # Redirigir al login
    return redirect(url_for('login'))

@app.route('/tecnicos')
@login_required(role='tecnicos')
def tecnicos_dashboard():
    return render_template('modulos/tecnicos/dashboard.html')

@app.route('/operativo')
@login_required(role='operativo')
def operativo_dashboard():
    return render_template('modulos/operativo/dashboard.html')

@app.route('/logistica')
@login_required(role='logistica')
def logistica_dashboard():
    return render_template('modulos/logistica/dashboard.html')

@app.route('/contabilidad')
@login_required(role='contabilidad')
def contabilidad_dashboard():
    return render_template('modulos/contabilidad/dashboard.html')

@app.route('/admin/buscar_usuarios', methods=['POST'])
@login_required(role='administrativo')
def buscar_usuarios():
    search_query = request.form.get('search_query', '')
    search_type = request.form.get('search_type', 'cedula')
    role = request.form.get('role', '')
    sort = request.form.get('sort', 'cedula')
    
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Construir la consulta SQL base
        query = """
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula,
                id_roles,
                estado
            FROM recurso_operativo
            WHERE 1=1
        """
        params = []
        
        # Aplicar filtros de búsqueda
        if search_query:
            if search_type == 'cedula':
                query += " AND recurso_operativo_cedula LIKE %s"
                params.append(f"%{search_query}%")
            elif search_type == 'codigo':
                query += " AND id_codigo_consumidor LIKE %s"
                params.append(f"%{search_query}%")
            elif search_type == 'rol':
                query += " AND id_roles = %s"
                role_id = next((k for k, v in ROLES.items() if v.lower() == search_query.lower()), None)
                if role_id:
                    params.append(role_id)
        
        if role:
            role_id = next((k for k, v in ROLES.items() if v == role), None)
            if role_id:
                query += " AND id_roles = %s"
                params.append(role_id)
        
        # Aplicar ordenamiento
        if sort == 'cedula':
            query += " ORDER BY recurso_operativo_cedula"
        
        cursor.execute(query, params)
        users = cursor.fetchall()
        
        # Formatear resultados
        formatted_users = []
        for user in users:
            formatted_users.append({
                'id_codigo_consumidor': user['id_codigo_consumidor'],
                'recurso_operativo_cedula': user['recurso_operativo_cedula'],
                'role': ROLES.get(str(user['id_roles']), 'Desconocido'),
                'estado': user.get('estado', 'Activo')
            })
        
        return jsonify(formatted_users)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/admin/exportar_usuarios_csv', methods=['POST'])
@login_required(role='administrativo')
def exportar_usuarios_csv():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener todos los usuarios
        cursor.execute("SELECT id_codigo_consumidor, recurso_operativo_cedula, id_roles, estado FROM recurso_operativo")
        users = cursor.fetchall()
        
        # Crear archivo CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Escribir encabezados
        writer.writerow(['Código', 'Cédula', 'Rol', 'Estado'])
        
        # Escribir datos
        for user in users:
            writer.writerow([
                user['id_codigo_consumidor'],
                user['recurso_operativo_cedula'],
                ROLES.get(str(user['id_roles']), 'Desconocido'),
                user.get('estado', 'Activo')
            ])
        
        # Preparar respuesta
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'usuarios_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/admin/estadisticas_usuarios')
@login_required(role='administrativo')
def estadisticas_usuarios():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener estadísticas por rol
        cursor.execute("""
            SELECT id_roles, COUNT(*) as count
            FROM recurso_operativo
            GROUP BY id_roles
        """)
        role_stats = cursor.fetchall()
        
        role_labels = []
        role_data = []
        for stat in role_stats:
            role_labels.append(ROLES.get(str(stat['id_roles']), 'Desconocido'))
            role_data.append(stat['count'])
        
        # Obtener estadísticas de actividad (últimos 30 días)
        activity_dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30)]
        activity_counts = []
        
        for date in activity_dates:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM recurso_operativo
                WHERE DATE(created_at) = %s
            """, (date,))
            result = cursor.fetchone()
            activity_counts.append(result['count'] if result else 0)
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'role_labels': role_labels,
            'role_data': role_data,
            'activity_labels': activity_dates[::-1],
            'activity_data': activity_counts[::-1]
        })
        
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
@login_required()
def dashboard():
    user_role = session.get('user_role')
    if user_role == 'administrativo':
        try:
            connection = get_db_connection()
            if connection is None:
                flash('Error al cargar usuarios. Por favor, inténtelo de nuevo.', 'error')
                return render_template('modulos/administrativo/dashboard.html')
                
            cursor = connection.cursor(dictionary=True)
            
            # Obtener usuarios
            cursor.execute("""
                SELECT 
                    id_codigo_consumidor, 
                    recurso_operativo_cedula, 
                    id_roles,
                    estado,
                    nombre,
                    cargo
                FROM recurso_operativo
            """)
            users = cursor.fetchall()
            
            # Obtener estadísticas
            total_users = len(users)
            total_roles = len(set(user['id_roles'] for user in users))
            active_users = sum(1 for user in users if user.get('estado') == 'Activo')
            
            cursor.close()
            connection.close()
            
            return render_template('modulos/administrativo/dashboard.html',
                                users=users,
                                ROLES=ROLES,
                                total_users=total_users,
                                total_roles=total_roles,
                                active_users=active_users)
                                
        except Error as e:
            flash(f'Error al cargar usuarios: {str(e)}', 'error')
            return render_template('modulos/administrativo/dashboard.html')
    elif user_role in ROLES.values():
        return redirect(url_for(f'{user_role}_dashboard'))
    else:
        flash('No tienes un rol válido asignado.', 'error')
        return redirect(url_for('logout'))

@app.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required(role='administrativo')
def edit_user(user_id):
    try:
        connection = get_db_connection()
        if connection is None:
            flash('Error de conexión a la base de datos.', 'error')
            return redirect(url_for('dashboard'))

        cursor = connection.cursor(dictionary=True)
        
        if request.method == 'POST':
            # Obtener datos del formulario
            new_role = request.form.get('role_id')
            new_password = request.form.get('password')
            
            # Actualizar rol
            if new_role:
                cursor.execute("""
                    UPDATE recurso_operativo 
                    SET id_roles = %s 
                    WHERE id_codigo_consumidor = %s
                """, (new_role, user_id))
            
            # Actualizar contraseña si se proporcionó una nueva
            if new_password:
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute("""
                    UPDATE recurso_operativo 
                    SET recurso_operativo_password = %s 
                    WHERE id_codigo_consumidor = %s
                """, (hashed_password, user_id))
            
            connection.commit()
            flash('Usuario actualizado exitosamente.', 'success')
            return redirect(url_for('dashboard'))
        
        # Obtener datos del usuario para el formulario
        cursor.execute("""
            SELECT id_codigo_consumidor, recurso_operativo_cedula, id_roles 
            FROM recurso_operativo 
            WHERE id_codigo_consumidor = %s
        """, (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('Usuario no encontrado.', 'error')
            return redirect(url_for('dashboard'))
            
        return jsonify({
            'status': 'success',
            'user': user
        })
        
    except Error as e:
        flash(f'Error al editar usuario: {str(e)}', 'error')
        return redirect(url_for('dashboard'))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required(role='administrativo')
def delete_user(user_id):
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'status': 'error', 'message': 'Error de conexión a la base de datos.'})

        cursor = connection.cursor(dictionary=True)
        
        # Verificar que el usuario existe
        cursor.execute("SELECT id_roles FROM recurso_operativo WHERE id_codigo_consumidor = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'status': 'error', 'message': 'Usuario no encontrado.'})
        
        # No permitir eliminar al último usuario administrativo
        if user['id_roles'] == 1:  # rol administrativo
            cursor.execute("SELECT COUNT(*) as admin_count FROM recurso_operativo WHERE id_roles = 1")
            admin_count = cursor.fetchone()['admin_count']
            if (admin_count <= 1):
                return jsonify({
                    'status': 'error',
                    'message': 'No se puede eliminar el último usuario administrativo.'
                })
        
        # Eliminar usuario
        cursor.execute("DELETE FROM recurso_operativo WHERE id_codigo_consumidor = %s", (user_id,))
        connection.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Usuario eliminado exitosamente.'
        })
        
    except Error as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al eliminar usuario: {str(e)}'
        })
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/create_user', methods=['POST'])
@login_required(role='administrativo')
def create_user():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        cursor = connection.cursor()
        
        # Obtener datos del formulario
        cedula = request.form.get('cedula')
        password = request.form.get('password')
        rol = request.form.get('rol')
        estado = request.form.get('estado', 'Activo')  # Por defecto 'Activo'
        nombre = request.form.get('nombre')
        cargo = request.form.get('cargo')

        # Validar datos requeridos
        if not all([cedula, password, rol, nombre, cargo]):
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400

        # Verificar si la cédula ya existe
        cursor.execute("SELECT id_codigo_consumidor FROM recurso_operativo WHERE recurso_operativo_cedula = %s", (cedula,))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'La cédula ya está registrada'}), 400

        # Encriptar contraseña
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insertar nuevo usuario
        cursor.execute("""
            INSERT INTO recurso_operativo 
            (recurso_operativo_cedula, recurso_operativo_password, id_roles, estado, nombre, cargo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (cedula, hashed_password.decode('utf-8'), rol, estado, nombre, cargo))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'success': True, 'message': 'Usuario creado exitosamente'})

    except Error as e:
        return jsonify({'success': False, 'message': f'Error al crear usuario: {str(e)}'}), 500
    
@app.route('/get_user/<int:user_id>')
@login_required(role='administrativo')
def get_user(user_id):
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula,
                id_roles,
                estado
            FROM recurso_operativo 
            WHERE id_codigo_consumidor = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        
        cursor.close()
        connection.close()

        if not user:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

        return jsonify(user)

    except Error as e:
        return jsonify({'success': False, 'message': f'Error al obtener usuario: {str(e)}'})
    
@app.route('/update_user', methods=['POST'])
@login_required(role='administrativo')
def update_user():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        cursor = connection.cursor()
        
        # Obtener datos del formulario
        user_id = request.form.get('id_codigo_consumidor')
        cedula = request.form.get('cedula')
        nombre = request.form.get('nombre')
        password = request.form.get('password')
        rol = request.form.get('rol')
        cargo = request.form.get('cargo')
        estado = request.form.get('estado')

        # Validar datos requeridos
        if not all([user_id, cedula, nombre, rol, cargo, estado]):
            return jsonify({'success': False, 'message': 'Faltan campos requeridos'}), 400

        # Verificar si el usuario existe
        cursor.execute("SELECT id_codigo_consumidor FROM recurso_operativo WHERE id_codigo_consumidor = %s", (user_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

        # Preparar la consulta de actualización
        update_query = """
            UPDATE recurso_operativo 
            SET recurso_operativo_cedula = %s,
                nombre = %s,
                id_roles = %s,
                cargo = %s,
                estado = %s
        """
        params = [cedula, nombre, rol, cargo, estado]

        # Si se proporciona una nueva contraseña, actualizarla
        if password:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            update_query += ", recurso_operativo_password = %s"
            params.append(hashed_password.decode('utf-8'))

        update_query += " WHERE id_codigo_consumidor = %s"
        params.append(user_id)

        # Ejecutar la actualización
        cursor.execute(update_query, params)
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({'success': True, 'message': 'Usuario actualizado exitosamente'})

    except Error as e:
        return jsonify({'success': False, 'message': f'Error al actualizar usuario: {str(e)}'}), 500

@app.route('/preoperacional', methods=['POST'])
@login_required(role='tecnicos')
def registrar_preoperacional():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'status': 'error', 'message': 'Error de conexión a la base de datos.'}), 500

        cursor = connection.cursor(dictionary=True)
        
        # Verificar si ya existe un registro para el día actual
        id_codigo_consumidor = request.form.get('id_codigo_consumidor')
        fecha_actual = get_bogota_datetime().date()
        
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM preoperacional 
            WHERE id_codigo_consumidor = %s 
            AND DATE(CONVERT_TZ(fecha, '+00:00', '-05:00')) = %s
        """, (id_codigo_consumidor, fecha_actual))
        
        resultado = cursor.fetchone()
        if resultado['count'] > 0:
            return jsonify({
                'status': 'error',
                'message': 'Ya has registrado un preoperacional para el día de hoy.'
            }), 400

        # Obtener datos del formulario
        data = {
            'centro_de_trabajo': request.form.get('centro_de_trabajo'),
            'ciudad': request.form.get('ciudad'),
            'supervisor': request.form.get('supervisor'),
            'vehiculo_asistio_operacion': request.form.get('vehiculo_asistio_operacion'),
            'tipo_vehiculo': request.form.get('tipo_vehiculo'),
            'placa_vehiculo': request.form.get('placa_vehiculo'),
            'modelo_vehiculo': request.form.get('modelo_vehiculo'),
            'marca_vehiculo': request.form.get('marca_vehiculo'),
            'licencia_conduccion': request.form.get('licencia_conduccion'),
            'fecha_vencimiento_licencia': request.form.get('fecha_vencimiento_licencia'),
            'fecha_vencimiento_soat': request.form.get('fecha_vencimiento_soat'),
            'fecha_vencimiento_tecnomecanica': request.form.get('fecha_vencimiento_tecnomecanica'),
            'estado_espejos': request.form.get('estado_espejos', 0),
            'bocina_pito': request.form.get('bocina_pito', 0),
            'frenos': request.form.get('frenos', 0),
            'encendido': request.form.get('encendido', 0),
            'estado_bateria': request.form.get('estado_bateria', 0),
            'estado_amortiguadores': request.form.get('estado_amortiguadores', 0),
            'estado_llantas': request.form.get('estado_llantas', 0),
            'kilometraje_actual': request.form.get('kilometraje_actual', 0),
            'luces_altas_bajas': request.form.get('luces_altas_bajas', 0),
            'direccionales_delanteras_traseras': request.form.get('direccionales_delanteras_traseras', 0),
            'elementos_prevencion_seguridad_vial_casco': request.form.get('elementos_prevencion_seguridad_vial_casco', 0),
            'casco_certificado': request.form.get('casco_certificado', 0),
            'casco_identificado': request.form.get('casco_identificado', 0),
            'estado_guantes': request.form.get('estado_guantes', 0),
            'estado_rodilleras': request.form.get('estado_rodilleras', 0),
            'impermeable': request.form.get('impermeable', 0),
            'observaciones': request.form.get('observaciones', '')
        }

        # Verificar que el id_codigo_consumidor existe en la tabla recurso_operativo
        cursor.execute("SELECT id_codigo_consumidor FROM recurso_operativo WHERE id_codigo_consumidor = %s", (id_codigo_consumidor,))
        if cursor.fetchone() is None:
            return jsonify({
                'status': 'error', 
                'message': 'El id_codigo_consumidor no existe en la tabla recurso_operativo.'
            }), 404

        # Construir la consulta SQL dinámicamente
        columns = list(data.keys()) + ['id_codigo_consumidor']
        values = list(data.values()) + [id_codigo_consumidor]
        placeholders = ['%s'] * len(columns)

        sql = f"""
            INSERT INTO preoperacional (
                {', '.join(columns)}, fecha
            ) VALUES (
                {', '.join(placeholders)}, %s
            )
        """
        
        # Agregar la fecha actual de Bogotá a los valores
        values.append(get_bogota_datetime())
        
        cursor.execute(sql, tuple(values))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'message': 'Preoperacional registrado exitosamente'
        }), 201

    except Error as e:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
        return jsonify({
            'status': 'error',
            'message': f'Error al registrar preoperacional: {str(e)}'
        }), 500

@app.route('/check_submission', methods=['GET'])
def check_submission():
    user_id = request.args.get('user_id')
    submission_date = request.args.get('date')
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'submitted': False, 'error': 'Database connection failed.'})

        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT 1 FROM preoperacional 
            WHERE id_codigo_consumidor = %s AND DATE(fecha_creacion) = %s
        """
        cursor.execute(query, (user_id, submission_date))
        submission_exists = cursor.fetchone() is not None

        cursor.close()
        connection.close()

        return jsonify({'submitted': submission_exists})
    except Error as e:
        return jsonify({'submitted': False, 'error': str(e)})

@app.route('/preoperacional/listado')
@login_required(role='administrativo')
def listado_preoperacional():
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        supervisor = request.args.get('supervisor')
        estado_vehiculo = request.args.get('estado_vehiculo')
        
        # Parámetro de paginación
        pagina = request.args.get('pagina', 1, type=int)
        registros_por_pagina = 10

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # Construir la cláusula WHERE dinámica
        where_clauses = []
        params = []

        if fecha_inicio:
            where_clauses.append("fecha >= %s")
            params.append(fecha_inicio)
        if fecha_fin:
            where_clauses.append("fecha <= %s")
            params.append(fecha_fin + " 23:59:59")
        if supervisor:
            where_clauses.append("supervisor = %s")
            params.append(supervisor)
        
        # Agregar filtro por estado del vehículo
        if estado_vehiculo:
            if estado_vehiculo == 'bueno':
                where_clauses.append("(estado_espejos + bocina_pito + frenos + encendido + estado_bateria + estado_amortiguadores + estado_llantas + luces_altas_bajas + direccionales_delanteras_traseras) = 9")
            elif estado_vehiculo == 'regular':
                where_clauses.append("(estado_espejos + bocina_pito + frenos + encendido + estado_bateria + estado_amortiguadores + estado_llantas + luces_altas_bajas + direccionales_delanteras_traseras) >= 5")
                where_clauses.append("(estado_espejos + bocina_pito + frenos + encendido + estado_bateria + estado_amortiguadores + estado_llantas + luces_altas_bajas + direccionales_delanteras_traseras) < 9")
            elif estado_vehiculo == 'malo':
                where_clauses.append("(estado_espejos + bocina_pito + frenos + encendido + estado_bateria + estado_amortiguadores + estado_llantas + luces_altas_bajas + direccionales_delanteras_traseras) < 5")

        # Construir la consulta SQL completa
        query = """
            SELECT p.*, r.nombre as nombre_tecnico, r.cargo as cargo_tecnico,
                   (estado_espejos + bocina_pito + frenos + encendido + estado_bateria + 
                    estado_amortiguadores + estado_llantas + luces_altas_bajas + 
                    direccionales_delanteras_traseras) as estado_total,
                   CASE 
                       WHEN (estado_espejos + bocina_pito + frenos + encendido + estado_bateria + 
                            estado_amortiguadores + estado_llantas + luces_altas_bajas + 
                            direccionales_delanteras_traseras) = 9 THEN 'Bueno'
                       WHEN (estado_espejos + bocina_pito + frenos + encendido + estado_bateria + 
                            estado_amortiguadores + estado_llantas + luces_altas_bajas + 
                            direccionales_delanteras_traseras) >= 5 THEN 'Regular'
                       ELSE 'Malo'
                   END as estado_vehiculo
            FROM preoperacional p
            LEFT JOIN recurso_operativo r ON p.id_codigo_consumidor = r.id_codigo_consumidor
        """
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " ORDER BY p.fecha DESC"
        
        cur.execute(query, params)
        registros = cur.fetchall()

        # Calcular paginación
        total_registros = len(registros)
        total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina
        
        # Ajustar página actual si está fuera de rango
        if pagina < 1:
            pagina = 1
        elif pagina > total_paginas and total_paginas > 0:
            pagina = total_paginas
        
        # Obtener registros de la página actual
        inicio = (pagina - 1) * registros_por_pagina
        fin = inicio + registros_por_pagina
        pagina_actual = registros[inicio:fin]

        # Obtener lista de supervisores únicos
        cur.execute("""
            SELECT DISTINCT supervisor 
            FROM preoperacional 
            WHERE supervisor IS NOT NULL 
            AND supervisor != '' 
            ORDER BY supervisor
        """)
        supervisores = [row['supervisor'] for row in cur.fetchall()]

        # Calcular estadísticas básicas
        registros_hoy = sum(1 for r in registros if r['fecha'].date() == datetime.now().date())
        registros_semana = sum(1 for r in registros if r['fecha'].date() >= (datetime.now() - timedelta(days=7)).date())
        registros_mes = sum(1 for r in registros if r['fecha'].date() >= (datetime.now() - timedelta(days=30)).date())

        # Preparar datos para el gráfico de tendencias
        fechas = []
        registros_por_dia = []
        if registros:
            fecha_actual = datetime.now().date()
            for i in range(7):
                fecha = fecha_actual - timedelta(days=i)
                fechas.append(fecha.strftime('%Y-%m-%d'))
                registros_por_dia.append(sum(1 for r in registros if r['fecha'].date() == fecha))
            fechas.reverse()
            registros_por_dia.reverse()

        # ESTADÍSTICAS ADICIONALES

        # 1. Distribución por tipo de vehículo
        tipos_vehiculo = {}
        for r in registros:
            tipo = r['tipo_vehiculo'] or 'No especificado'
            if tipo in tipos_vehiculo:
                tipos_vehiculo[tipo] += 1
            else:
                tipos_vehiculo[tipo] = 1
        
        # Ordenar por cantidad y tomar los 5 principales
        tipos_vehiculo_top = sorted(tipos_vehiculo.items(), key=lambda x: x[1], reverse=True)[:5]
        labels_tipo_vehiculo = [t[0] for t in tipos_vehiculo_top]
        datos_tipo_vehiculo = [t[1] for t in tipos_vehiculo_top]

        # 2. Top 5 técnicos con más registros
        tecnicos = {}
        for r in registros:
            tecnico = r['nombre_tecnico'] or 'No especificado'
            if tecnico in tecnicos:
                tecnicos[tecnico] += 1
            else:
                tecnicos[tecnico] = 1
        
        tecnicos_top = sorted(tecnicos.items(), key=lambda x: x[1], reverse=True)[:5]
        labels_tecnicos = [t[0] for t in tecnicos_top]
        datos_tecnicos = [t[1] for t in tecnicos_top]

        # 3. Top 5 centros de trabajo con más registros
        centros_trabajo = {}
        for r in registros:
            centro = r['centro_de_trabajo'] or 'No especificado'
            if centro in centros_trabajo:
                centros_trabajo[centro] += 1
            else:
                centros_trabajo[centro] = 1
        
        centros_top = sorted(centros_trabajo.items(), key=lambda x: x[1], reverse=True)[:5]
        labels_centros = [c[0] for c in centros_top]
        datos_centros = [c[1] for c in centros_top]

        # 4. Elementos críticos en mal estado (conteo)
        elementos_mal_estado = {
            'Frenos': sum(1 for r in registros if r.get('frenos') == '0'),
            'Luces': sum(1 for r in registros if r.get('luces_altas_bajas') == '0'),
            'Direccionales': sum(1 for r in registros if r.get('direccionales_delanteras_traseras') == '0'),
            'Espejos': sum(1 for r in registros if r.get('estado_espejos') == '0'),
            'Llantas': sum(1 for r in registros if r.get('estado_llantas') == '0')
        }
        
        labels_elementos = list(elementos_mal_estado.keys())
        datos_elementos = list(elementos_mal_estado.values())

        # 5. Distribución por ciudad
        ciudades = {}
        for r in registros:
            ciudad = r['ciudad'] or 'No especificado'
            if ciudad in ciudades:
                ciudades[ciudad] += 1
            else:
                ciudades[ciudad] = 1
        
        ciudades_top = sorted(ciudades.items(), key=lambda x: x[1], reverse=True)[:5]
        labels_ciudades = [c[0] for c in ciudades_top]
        datos_ciudades = [c[1] for c in ciudades_top]

        # 6. Comparativa mes actual vs mes anterior
        fecha_actual = datetime.now().date()
        primer_dia_mes_actual = fecha_actual.replace(day=1)
        ultimo_dia_mes_anterior = primer_dia_mes_actual - timedelta(days=1)
        primer_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)
        
        registros_mes_actual = sum(1 for r in registros if r['fecha'].date() >= primer_dia_mes_actual)
        registros_mes_anterior = sum(1 for r in registros if r['fecha'].date() >= primer_dia_mes_anterior and r['fecha'].date() < primer_dia_mes_actual)
        
        comparativa_meses = {
            'labels': [primer_dia_mes_anterior.strftime('%B %Y'), primer_dia_mes_actual.strftime('%B %Y')],
            'datos': [registros_mes_anterior, registros_mes_actual]
        }

        cur.close()
        conn.close()

        return render_template('modulos/administrativo/listado_preoperacional.html', 
                            registros=registros,
                            pagina_actual=pagina_actual,
                            pagina_actual_num=pagina,
                            total_paginas=total_paginas,
                            total_registros=total_registros,
                            supervisores=supervisores,
                            fecha_inicio=fecha_inicio,
                            fecha_fin=fecha_fin,
                            supervisor=supervisor,
                            estado_vehiculo=estado_vehiculo,
                            registros_hoy=registros_hoy,
                            registros_semana=registros_semana,
                            registros_mes=registros_mes,
                            fechas=fechas,
                            registros_por_dia=registros_por_dia,
                            # Nuevas estadísticas
                            labels_tipo_vehiculo=labels_tipo_vehiculo,
                            datos_tipo_vehiculo=datos_tipo_vehiculo,
                            labels_tecnicos=labels_tecnicos,
                            datos_tecnicos=datos_tecnicos,
                            labels_centros=labels_centros,
                            datos_centros=datos_centros,
                            labels_elementos=labels_elementos,
                            datos_elementos=datos_elementos,
                            labels_ciudades=labels_ciudades,
                            datos_ciudades=datos_ciudades,
                            comparativa_meses=comparativa_meses)

    except Exception as e:
        flash('Error al cargar el listado preoperacional: ' + str(e), 'error')
        return render_template('modulos/administrativo/listado_preoperacional.html',
                            registros=[],
                            pagina_actual=[],
                            pagina_actual_num=1,
                            total_paginas=0,
                            supervisores=[],
                            fecha_inicio=fecha_inicio,
                            fecha_fin=fecha_fin,
                            supervisor=supervisor,
                            estado_vehiculo=estado_vehiculo,
                            total_registros=0,
                            registros_hoy=0,
                            registros_semana=0,
                            registros_mes=0,
                            fechas=[],
                            registros_por_dia=[],
                            # Valores vacíos para nuevas estadísticas
                            labels_tipo_vehiculo=[],
                            datos_tipo_vehiculo=[],
                            labels_tecnicos=[],
                            datos_tecnicos=[],
                            labels_centros=[],
                            datos_centros=[],
                            labels_elementos=[],
                            datos_elementos=[],
                            labels_ciudades=[],
                            datos_ciudades=[],
                            comparativa_meses={'labels': [], 'datos': []})

@app.route('/preoperacional/exportar_csv')
@login_required(role='administrativo')
def exportar_preoperacional_csv():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener parámetros de filtro
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        supervisor = request.args.get('supervisor')
        
        # Construir la cláusula WHERE base
        where_clauses = []
        params = []
        
        if fecha_inicio:
            where_clauses.append("DATE(p.fecha) >= %s")
            params.append(fecha_inicio)
        if fecha_fin:
            where_clauses.append("DATE(p.fecha) <= %s")
            params.append(fecha_fin)
        if supervisor:
            where_clauses.append("p.supervisor = %s")
            params.append(supervisor)
            
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Obtener registros preoperacionales con información del usuario y filtros aplicados
        query = f"""
            SELECT 
                p.*,
                r.nombre as nombre_tecnico,
                r.cargo as cargo_tecnico,
                r.recurso_operativo_cedula as cedula_tecnico
            FROM preoperacional p
            JOIN recurso_operativo r ON p.id_codigo_consumidor = r.id_codigo_consumidor
            WHERE {where_sql}
            ORDER BY p.fecha DESC
        """
        cursor.execute(query, params)
        registros = cursor.fetchall()
        cursor.close()
        connection.close()
        
        # Crear archivo CSV en memoria con codificación UTF-8-SIG (con BOM)
        output = io.StringIO()
        # Usar csv.excel con delimitador explícito para garantizar correcta separación de columnas
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        
        # Escribir el BOM de UTF-8
        output.write('\ufeff')
        
        # Escribir encabezados
        writer.writerow([
            'Fecha', 'Técnico', 'Cédula', 'Cargo', 'Centro de Trabajo', 'Ciudad', 'Supervisor',
            'Vehículo Asistió', 'Tipo Vehículo', 'Placa', 'Modelo', 'Marca',
            'Licencia Conducción', 'Vencimiento Licencia', 'Vencimiento SOAT',
            'Vencimiento Tecnomecánica', 'Estado Espejos', 'Bocina/Pito',
            'Frenos', 'Encendido', 'Batería', 'Amortiguadores', 'Llantas',
            'Kilometraje', 'Luces Altas/Bajas', 'Direccionales',
            'Elementos Prevención Casco', 'Casco Certificado', 'Casco Identificado',
            'Estado Guantes', 'Estado Rodilleras', 'Impermeable', 'Observaciones'
        ])
        
        # Escribir datos
        for registro in registros:
            # Convertir fechas a cadena o valor nulo para evitar errores
            fecha_lic = registro['fecha_vencimiento_licencia'].strftime('%Y-%m-%d') if registro['fecha_vencimiento_licencia'] else ''
            fecha_soat = registro['fecha_vencimiento_soat'].strftime('%Y-%m-%d') if registro['fecha_vencimiento_soat'] else ''
            fecha_tec = registro['fecha_vencimiento_tecnomecanica'].strftime('%Y-%m-%d') if registro['fecha_vencimiento_tecnomecanica'] else ''
            
            writer.writerow([
                registro['fecha'].strftime('%Y-%m-%d %H:%M:%S'),
                registro['nombre_tecnico'],
                registro['cedula_tecnico'],
                registro['cargo_tecnico'],
                registro['centro_de_trabajo'] or '',
                registro['ciudad'] or '',
                registro['supervisor'] or '',
                registro['vehiculo_asistio_operacion'] or '',
                registro['tipo_vehiculo'] or '',
                registro['placa_vehiculo'] or '',
                registro['modelo_vehiculo'] or '',
                registro['marca_vehiculo'] or '',
                registro['licencia_conduccion'] or '',
                fecha_lic,
                fecha_soat,
                fecha_tec,
                registro['estado_espejos'] or '',
                registro['bocina_pito'] or '',
                registro['frenos'] or '',
                registro['encendido'] or '',
                registro['estado_bateria'] or '',
                registro['estado_amortiguadores'] or '',
                registro['estado_llantas'] or '',
                registro['kilometraje_actual'] or '',
                registro['luces_altas_bajas'] or '',
                registro['direccionales_delanteras_traseras'] or '',
                registro['elementos_prevencion_seguridad_vial_casco'] or '',
                registro['casco_certificado'] or '',
                registro['casco_identificado'] or '',
                registro['estado_guantes'] or '',
                registro['estado_rodilleras'] or '',
                registro['impermeable'] or '',
                registro['observaciones'] or ''
            ])
        
        # Preparar respuesta
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),  # Usar UTF-8 con BOM
            mimetype='text/csv; charset=utf-8-sig',
            as_attachment=True,
            download_name=f'preoperacional_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/reportes')
@login_required(role='administrativo')
def admin_reportes():
    return render_template('modulos/administrativo/reportes/dashboard_reportes.html')

@app.route('/api/reportes/usuarios')
@login_required(role='administrativo')
def api_reportes_usuarios():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Estadísticas generales de usuarios
        cursor.execute("""
            SELECT 
                COUNT(*) as total_usuarios,
                SUM(CASE WHEN estado = 'Activo' THEN 1 ELSE 0 END) as usuarios_activos,
                id_roles,
                COUNT(*) as cantidad
            FROM recurso_operativo
            GROUP BY id_roles
        """)
        stats_por_rol = cursor.fetchall()
        
        # Usuarios registrados por mes (últimos 12 meses)
        cursor.execute("""
            SELECT 
                DATE_FORMAT(fecha_creacion, '%Y-%m') as mes,
                COUNT(*) as cantidad
            FROM recurso_operativo
            WHERE fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(fecha_creacion, '%Y-%m')
            ORDER BY mes
        """)
        registros_por_mes = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Formatear datos para gráficos
        roles_labels = [ROLES.get(str(stat['id_roles']), 'Desconocido') for stat in stats_por_rol]
        roles_data = [stat['cantidad'] for stat in stats_por_rol]
        
        meses_labels = []
        meses_data = []
        for registro in registros_por_mes:
            meses_labels.append(registro['mes'])
            meses_data.append(registro['cantidad'])
            
        return jsonify({
            'roles': {
                'labels': roles_labels,
                'data': roles_data
            },
            'registros_mensuales': {
                'labels': meses_labels,
                'data': meses_data
            }
        })
        
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reportes/filtros')
@login_required(role='administrativo')
def api_reportes_filtros():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener supervisores únicos
        cursor.execute("""
            SELECT DISTINCT supervisor 
            FROM preoperacional 
            WHERE supervisor IS NOT NULL AND supervisor != ''
            ORDER BY supervisor
        """)
        supervisores = [row['supervisor'] for row in cursor.fetchall()]
        
        # Obtener centros de trabajo únicos
        cursor.execute("""
            SELECT DISTINCT centro_de_trabajo 
            FROM preoperacional 
            WHERE centro_de_trabajo IS NOT NULL AND centro_de_trabajo != ''
            ORDER BY centro_de_trabajo
        """)
        centros_trabajo = [row['centro_de_trabajo'] for row in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'supervisores': supervisores,
            'centros_trabajo': centros_trabajo
        })
        
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reportes/preoperacional')
@login_required(role='administrativo')
def api_reportes_preoperacional():
    try:
        # Obtener parámetros de filtro
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        supervisor = request.args.get('supervisor')
        centro_trabajo = request.args.get('centro_trabajo')
        
        # Construir la cláusula WHERE base
        where_clauses = []
        params = []
        
        if fecha_inicio:
            where_clauses.append("p.fecha >= %s")
            params.append(fecha_inicio)
        if fecha_fin:
            where_clauses.append("p.fecha <= %s")
            params.append(fecha_fin)
        if supervisor:
            where_clauses.append("p.supervisor = %s")
            params.append(supervisor)
        if centro_trabajo:
            where_clauses.append("p.centro_de_trabajo = %s")
            params.append(centro_trabajo)
            
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Estadísticas generales con filtros
        stats_query = f"""
            SELECT 
                COUNT(*) as total_preoperacionales,
                COUNT(DISTINCT id_codigo_consumidor) as total_tecnicos,
                COUNT(DISTINCT DATE(fecha)) as total_dias
            FROM preoperacional p
            WHERE {where_sql}
        """
        cursor.execute(stats_query, params)
        stats_generales = cursor.fetchone()
        
        # Preoperacionales por día con filtros
        registros_query = f"""
            SELECT 
                DATE(fecha) as fecha,
                COUNT(*) as cantidad
            FROM preoperacional p
            WHERE {where_sql}
            GROUP BY DATE(fecha)
            ORDER BY fecha
        """
        cursor.execute(registros_query, params)
        registros_por_dia = cursor.fetchall()
        
        # Estado de vehículos con filtros
        estado_query = f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE 
                    WHEN (estado_espejos + bocina_pito + frenos + encendido + estado_bateria + 
                         estado_amortiguadores + estado_llantas + luces_altas_bajas + 
                         direccionales_delanteras_traseras) = 9 THEN 1 
                    ELSE 0 
                END) as estado_bueno,
                SUM(CASE 
                    WHEN (estado_espejos + bocina_pito + frenos + encendido + estado_bateria + 
                         estado_amortiguadores + estado_llantas + luces_altas_bajas + 
                         direccionales_delanteras_traseras) >= 5 
                    AND (estado_espejos + bocina_pito + frenos + encendido + estado_bateria + 
                         estado_amortiguadores + estado_llantas + luces_altas_bajas + 
                         direccionales_delanteras_traseras) < 9 THEN 1 
                    ELSE 0 
                END) as estado_regular,
                SUM(CASE 
                    WHEN (estado_espejos + bocina_pito + frenos + encendido + estado_bateria + 
                         estado_amortiguadores + estado_llantas + luces_altas_bajas + 
                         direccionales_delanteras_traseras) < 5 THEN 1 
                    ELSE 0 
                END) as estado_malo
            FROM preoperacional p
            WHERE {where_sql}
        """
        cursor.execute(estado_query, params)
        estado_vehiculos = cursor.fetchone()
        
        # Estadísticas por centro de trabajo con filtros
        centro_trabajo_query = f"""
            SELECT 
                COALESCE(centro_de_trabajo, 'No especificado') as centro_de_trabajo,
                COUNT(*) as cantidad
            FROM preoperacional p
            WHERE {where_sql}
            GROUP BY centro_de_trabajo
            ORDER BY cantidad DESC
            LIMIT 5
        """
        cursor.execute(centro_trabajo_query, params)
        stats_centro_trabajo = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Formatear datos para la respuesta
        dias_labels = [registro['fecha'].strftime('%Y-%m-%d') for registro in registros_por_dia]
        dias_data = [registro['cantidad'] for registro in registros_por_dia]
        
        total = estado_vehiculos['total'] or 1
        estado_labels = ['Bueno', 'Regular', 'Malo']
        estado_data = [
            round((estado_vehiculos['estado_bueno'] or 0) / total * 100, 2),
            round((estado_vehiculos['estado_regular'] or 0) / total * 100, 2),
            round((estado_vehiculos['estado_malo'] or 0) / total * 100, 2)
        ]
        
        return jsonify({
            'stats_generales': stats_generales,
            'registros_diarios': {
                'labels': dias_labels,
                'data': dias_data
            },
            'estado_vehiculos': {
                'labels': estado_labels,
                'data': estado_data,
                'colores': ['#2dce89', '#fb6340', '#f5365c']  # Verde para Bueno, Naranja para Regular, Rojo para Malo
            },
            'centro_trabajo': {
                'labels': [ct['centro_de_trabajo'] for ct in stats_centro_trabajo],
                'data': [ct['cantidad'] for ct in stats_centro_trabajo]
            }
        })
        
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reportes/vencimientos')
@login_required(role='administrativo')
def api_reportes_vencimientos():
    try:
        # Obtener parámetros de filtro
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        supervisor = request.args.get('supervisor')
        centro_trabajo = request.args.get('centro_trabajo')
        
        # Construir la cláusula WHERE base
        where_clauses = []
        params = []
        
        if fecha_inicio:
            where_clauses.append("p.fecha >= %s")
            params.append(fecha_inicio)
        if fecha_fin:
            where_clauses.append("p.fecha <= %s")
            params.append(fecha_fin)
        if supervisor:
            where_clauses.append("p.supervisor = %s")
            params.append(supervisor)
        if centro_trabajo:
            where_clauses.append("p.centro_de_trabajo = %s")
            params.append(centro_trabajo)
            
        # Agregar condiciones de vencimiento
        vencimiento_conditions = [
            "p.fecha_vencimiento_licencia IS NOT NULL AND p.fecha_vencimiento_licencia >= CURDATE() AND p.fecha_vencimiento_licencia <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)",
            "p.fecha_vencimiento_soat IS NOT NULL AND p.fecha_vencimiento_soat >= CURDATE() AND p.fecha_vencimiento_soat <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)",
            "p.fecha_vencimiento_tecnomecanica IS NOT NULL AND p.fecha_vencimiento_tecnomecanica >= CURDATE() AND p.fecha_vencimiento_tecnomecanica <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)"
        ]
        
        where_sql = f"""
            ({" OR ".join(vencimiento_conditions)})
            {" AND " + " AND ".join(where_clauses) if where_clauses else ""}
        """
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        query = f"""
            SELECT 
                p.id_preoperacional,
                p.placa_vehiculo,
                p.fecha_vencimiento_licencia,
                p.fecha_vencimiento_soat,
                p.fecha_vencimiento_tecnomecanica,
                r.nombre as nombre_tecnico,
                DATEDIFF(p.fecha_vencimiento_licencia, CURDATE()) as dias_licencia,
                DATEDIFF(p.fecha_vencimiento_soat, CURDATE()) as dias_soat,
                DATEDIFF(p.fecha_vencimiento_tecnomecanica, CURDATE()) as dias_tecnomecanica
            FROM preoperacional p
            JOIN recurso_operativo r ON p.id_codigo_consumidor = r.id_codigo_consumidor
            WHERE {where_sql}
            ORDER BY 
                LEAST(
                    COALESCE(DATEDIFF(p.fecha_vencimiento_licencia, CURDATE()), 999),
                    COALESCE(DATEDIFF(p.fecha_vencimiento_soat, CURDATE()), 999),
                    COALESCE(DATEDIFF(p.fecha_vencimiento_tecnomecanica, CURDATE()), 999)
                )
        """
        
        cursor.execute(query, params)
        vencimientos = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify({
            'vencimientos': vencimientos
        })
        
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verificar_vencimientos')
@login_required()
def verificar_vencimientos():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener el último registro preoperacional del usuario
        cursor.execute("""
            SELECT 
                fecha_vencimiento_licencia,
                fecha_vencimiento_soat,
                fecha_vencimiento_tecnomecanica
            FROM preoperacional 
            WHERE id_codigo_consumidor = %s
            ORDER BY fecha DESC 
            LIMIT 1
        """, (session.get('user_id'),))
        
        ultimo_registro = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not ultimo_registro:
            return jsonify({'tiene_vencimientos': False})
            
        vencimientos = []
        fecha_actual = datetime.now().date()
        
        # Verificar cada tipo de vencimiento
        if ultimo_registro['fecha_vencimiento_licencia']:
            dias_licencia = (ultimo_registro['fecha_vencimiento_licencia'] - fecha_actual).days
            if 0 <= dias_licencia <= 30:
                vencimientos.append({
                    'tipo': 'Licencia de Conducción',
                    'fecha': ultimo_registro['fecha_vencimiento_licencia'].strftime('%Y-%m-%d'),
                    'dias_restantes': dias_licencia
                })
                
        if ultimo_registro['fecha_vencimiento_soat']:
            dias_soat = (ultimo_registro['fecha_vencimiento_soat'] - fecha_actual).days
            if 0 <= dias_soat <= 30:
                vencimientos.append({
                    'tipo': 'SOAT',
                    'fecha': ultimo_registro['fecha_vencimiento_soat'].strftime('%Y-%m-%d'),
                    'dias_restantes': dias_soat
                })
                
        if ultimo_registro['fecha_vencimiento_tecnomecanica']:
            dias_tecno = (ultimo_registro['fecha_vencimiento_tecnomecanica'] - fecha_actual).days
            if 0 <= dias_tecno <= 30:
                vencimientos.append({
                    'tipo': 'Tecnomecánica',
                    'fecha': ultimo_registro['fecha_vencimiento_tecnomecanica'].strftime('%Y-%m-%d'),
                    'dias_restantes': dias_tecno
                })
        
        return jsonify({
            'tiene_vencimientos': len(vencimientos) > 0,
            'vencimientos': vencimientos
        })
        
    except Error as e:
        print("Error en verificar_vencimientos:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/verificar_registro_preoperacional')
@login_required(role='tecnicos')
def verificar_registro_preoperacional():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Verificar si existe registro para el día actual
        fecha_actual = datetime.now().date()
        cursor.execute("""
            SELECT COUNT(*) as count, 
                   MAX(fecha) as ultimo_registro
            FROM preoperacional 
            WHERE id_codigo_consumidor = %s 
            AND DATE(fecha) = %s
        """, (session.get('user_id'), fecha_actual))
        
        resultado = cursor.fetchone()
        tiene_registro = resultado['count'] > 0
        ultimo_registro = resultado['ultimo_registro'].strftime('%Y-%m-%d %H:%M:%S') if resultado['ultimo_registro'] else None
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'tiene_registro': tiene_registro,
            'ultimo_registro': ultimo_registro,
            'fecha_actual': fecha_actual.strftime('%Y-%m-%d')
        })
        
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logistica/asignaciones')
@login_required()
@role_required('logistica')
def ver_asignaciones():
    try:
        connection = get_db_connection()
        if connection is None:
            return render_template('error.html', 
                               mensaje='Error de conexión a la base de datos',
                               error='No se pudo establecer conexión con la base de datos')
                               
        cursor = connection.cursor(dictionary=True)
        
        # Obtener todas las asignaciones con información del técnico
        cursor.execute("""
            SELECT a.*, r.nombre, r.recurso_operativo_cedula 
            FROM asignacion a 
            LEFT JOIN recurso_operativo r ON a.id_codigo_consumidor = r.id_codigo_consumidor 
            ORDER BY a.asignacion_fecha DESC
        """)
        asignaciones = cursor.fetchall()

        # Obtener lista de técnicos disponibles
        cursor.execute("""
            SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula, cargo 
            FROM recurso_operativo 
            WHERE cargo LIKE '%TECNICO%' OR cargo LIKE '%TÉCNICO%'
            ORDER BY nombre
        """)
        tecnicos = cursor.fetchall()
        
        cursor.close()
        connection.close()

        return render_template('modulos/logistica/asignaciones.html', 
                            asignaciones=asignaciones,
                            tecnicos=tecnicos)

    except Exception as e:
        print(f"Error al obtener asignaciones: {str(e)}")
        return render_template('error.html', 
                           mensaje='Error al cargar las asignaciones',
                           error=str(e))

@app.route('/logistica/registrar_asignacion', methods=['POST'])
@login_required()
@role_required('logistica')
def registrar_asignacion():
    connection = None
    cursor = None
    try:
        # Obtener datos básicos
        id_codigo_consumidor = request.form.get('id_codigo_consumidor')
        fecha = request.form.get('fecha')
        cargo = request.form.get('cargo')

        # Validar campos requeridos
        if not all([id_codigo_consumidor, fecha, cargo]):
            return jsonify({
                'status': 'error',
                'message': 'Los campos ID, fecha y cargo son requeridos'
            }), 400

        connection = get_db_connection()
        if connection is None:
            return jsonify({
                'status': 'error',
                'message': 'Error de conexión a la base de datos'
            }), 500

        cursor = connection.cursor(dictionary=True)

        # Verificar que el técnico existe
        cursor.execute('SELECT nombre FROM recurso_operativo WHERE id_codigo_consumidor = %s', (id_codigo_consumidor,))
        tecnico = cursor.fetchone()
        
        if not tecnico:
            return jsonify({
                'status': 'error',
                'message': 'El técnico seleccionado no existe'
            }), 404

        # Obtener la estructura de la tabla
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'asignacion'
        """)
        columnas_existentes = {row['COLUMN_NAME'].lower() for row in cursor.fetchall()}
        
        print("Columnas existentes:", columnas_existentes)  # Debug log

        # Campos base que siempre deben existir
        campos = ['id_codigo_consumidor', 'asignacion_fecha', 'asignacion_cargo']
        valores = [id_codigo_consumidor, fecha, cargo]

        # Lista de todas las herramientas posibles
        herramientas = [
            'adaptador_mandril', 'alicate', 'barra_45cm', 'bisturi_metalico',
            'broca_3/8', 'broca_3/8/6_ran', 'broca_1/2/6_ran',
            'broca_metal/madera_1/4', 'broca_metal/madera_3/8', 'broca_metal/madera_5/16',
            'caja_de_herramientas', 'cajon_rojo', 'cinta_de_senal', 'cono_retractil',
            'cortafrio', 'destor_de_estrella', 'destor_de_pala', 'destor_tester',
            'espatula', 'exten_de_corr_10_mts', 'llave_locking_male', 'llave_reliance',
            'llave_torque_rg_11', 'llave_torque_rg_6', 'llaves_mandril',
            'mandril_para_taladro', 'martillo_de_una', 'multimetro',
            'pelacable_rg_6y_rg_11', 'pinza_de_punta', 'pistola_de_silicona',
            'planillero', 'ponchadora_rg_6_y_rg_11', 'ponchadora_rj_45_y_rj11',
            'probador_de_tonos', 'probador_de_tonos_utp', 'puntas_para_multimetro',
            'sonda_metalica', 'tacos_de_madera', 'taladro_percutor',
            'telefono_de_pruebas', 'power_miter', 'bfl_laser', 'cortadora',
            'stripper_fibra', 'pelachaqueta'
        ]

        # Procesar cada herramienta
        for herramienta in herramientas:
            nombre_campo = f'asignacion_{herramienta}'
            if nombre_campo.lower() in columnas_existentes:
                campos.append(nombre_campo)
                valor = request.form.get(herramienta, '0')
                valores.append(valor if valor == '1' else '0')
            else:
                print(f"Campo ignorado (no existe en la tabla): {nombre_campo}")

        # Agregar estado por defecto si existe la columna
        if 'asignacion_estado' in columnas_existentes:
            campos.append('asignacion_estado')
            valores.append('1')

        # Construir y ejecutar la consulta SQL
        sql = f"""
            INSERT INTO asignacion ({', '.join(campos)})
            VALUES ({', '.join(['%s'] * len(valores))})
        """
        
        print("SQL Query:", sql)  # Debug log
        print("Valores:", valores)  # Debug log

        cursor.execute(sql, tuple(valores))
        connection.commit()

        return jsonify({
            'status': 'success',
            'message': 'Asignación registrada exitosamente'
        }), 201

    except mysql.connector.Error as e:
        print(f"Error MySQL: {str(e)}")  # Debug log
        return jsonify({
            'status': 'error',
            'message': f'Error en la base de datos: {str(e)}'
        }), 500
    except Exception as e:
        print(f"Error general: {str(e)}")  # Debug log
        return jsonify({
            'status': 'error',
            'message': f'Error al registrar la asignación: {str(e)}'
        }), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/logistica/asignacion/<int:id_asignacion>')
@login_required()
@role_required('logistica')
def ver_detalle_asignacion(id_asignacion):
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({
                'status': 'error',
                'message': 'Error de conexión a la base de datos'
            }), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener los detalles de la asignación
        cursor.execute("""
            SELECT a.*, r.nombre, r.recurso_operativo_cedula, r.cargo
            FROM asignacion a 
            LEFT JOIN recurso_operativo r ON a.id_codigo_consumidor = r.id_codigo_consumidor 
            WHERE a.id_asignacion = %s
        """, (id_asignacion,))
        
        asignacion = cursor.fetchone()
        
        if not asignacion:
            return jsonify({
                'status': 'error',
                'message': 'No se encontró la asignación'
            }), 404

        # Función auxiliar para formatear valores
        def formatear_valor(valor):
            if valor is None:
                return '0'
            return str(valor)

        # Organizar los datos
        detalles = {
            'info_basica': {
                'tecnico': asignacion['nombre'],
                'cedula': asignacion['recurso_operativo_cedula'],
                'cargo': asignacion.get('asignacion_cargo', 'No especificado'),
                'fecha': asignacion['asignacion_fecha'].strftime('%Y-%m-%d %H:%M:%S'),
                'estado': 'Activo' if str(asignacion.get('asignacion_estado', '0')) == '1' else 'Inactivo'
            },
            'herramientas_basicas': {
                'adaptador_mandril': formatear_valor(asignacion.get('asignacion_adaptador_mandril')),
                'alicate': formatear_valor(asignacion.get('asignacion_alicate')),
                'barra_45cm': formatear_valor(asignacion.get('asignacion_barra_45cm')),
                'bisturi_metalico': formatear_valor(asignacion.get('asignacion_bisturi_metalico')),
                'caja_de_herramientas': formatear_valor(asignacion.get('asignacion_caja_de_herramientas')),
                'cortafrio': formatear_valor(asignacion.get('asignacion_cortafrio')),
                'destor_de_estrella': formatear_valor(asignacion.get('asignacion_destor_de_estrella')),
                'destor_de_pala': formatear_valor(asignacion.get('asignacion_destor_de_pala')),
                'destor_tester': formatear_valor(asignacion.get('asignacion_destor_tester')),
                'espatula': formatear_valor(asignacion.get('asignacion_espatula')),
                'martillo_de_una': formatear_valor(asignacion.get('asignacion_martillo_de_una')),
                'pinza_de_punta': formatear_valor(asignacion.get('asignacion_pinza_de_punta'))
            },
            'brocas': {
                'broca_3/8': formatear_valor(asignacion.get('asignacion_broca_3/8')),
                'broca_3/8/6_ran': formatear_valor(asignacion.get('asignacion_broca_3/8/6_ran')),
                'broca_1/2/6_ran': formatear_valor(asignacion.get('asignacion_broca_1/2/6_ran')),
                'broca_metal/madera_1/4': formatear_valor(asignacion.get('asignacion_broca_metal/madera_1/4')),
                'broca_metal/madera_3/8': formatear_valor(asignacion.get('asignacion_broca_metal/madera_3/8')),
                'broca_metal/madera_5/16': formatear_valor(asignacion.get('asignacion_broca_metal/madera_5/16'))
            },
            'herramientas_red': {
                'cajon_rojo': formatear_valor(asignacion.get('asignacion_cajon_rojo')),
                'cinta_de_senal': formatear_valor(asignacion.get('asignacion_cinta_de_senal')),
                'cono_retractil': formatear_valor(asignacion.get('asignacion_cono_retractil')),
                'exten_de_corr_10_mts': formatear_valor(asignacion.get('asignacion_exten_de_corr_10_mts')),
                'llave_locking_male': formatear_valor(asignacion.get('asignacion_llave_locking_male')),
                'llave_reliance': formatear_valor(asignacion.get('asignacion_llave_reliance')),
                'llave_torque_rg_11': formatear_valor(asignacion.get('asignacion_llave_torque_rg_11')),
                'llave_torque_rg_6': formatear_valor(asignacion.get('asignacion_llave_torque_rg_6')),
                'llaves_mandril': formatear_valor(asignacion.get('asignacion_llaves_mandril')),
                'mandril_para_taladro': formatear_valor(asignacion.get('asignacion_mandril_para_taladro')),
                'pelacable_rg_6y_rg_11': formatear_valor(asignacion.get('asignacion_pelacable_rg_6y_rg_11')),
                'pistola_de_silicona': formatear_valor(asignacion.get('asignacion_pistola_de_silicona')),
                'planillero': formatear_valor(asignacion.get('asignacion_planillero')),
                'ponchadora_rg_6_y_rg_11': formatear_valor(asignacion.get('asignacion_ponchadora_rg_6_y_rg_11')),
                'ponchadora_rj_45_y_rj11': formatear_valor(asignacion.get('asignacion_ponchadora_rj_45_y_rj11')),
                'probador_de_tonos': formatear_valor(asignacion.get('asignacion_probador_de_tonos')),
                'probador_de_tonos_utp': formatear_valor(asignacion.get('asignacion_probador_de_tonos_utp')),
                'puntas_para_multimetro': formatear_valor(asignacion.get('asignacion_puntas_para_multimetro')),
                'sonda_metalica': formatear_valor(asignacion.get('asignacion_sonda_metalica')),
                'tacos_de_madera': formatear_valor(asignacion.get('asignacion_tacos_de_madera')),
                'telefono_de_pruebas': formatear_valor(asignacion.get('asignacion_telefono_de_pruebas')),
                'power_miter': formatear_valor(asignacion.get('asignacion_power_miter')),
                'bfl_laser': formatear_valor(asignacion.get('asignacion_bfl_laser')),
                'cortadora': formatear_valor(asignacion.get('asignacion_cortadora')),
                'stripper_fibra': formatear_valor(asignacion.get('asignacion_stripper_fibra')),
                'pelachaqueta': formatear_valor(asignacion.get('asignacion_pelachaqueta'))
            }
        }

        print("Detalles a enviar:", detalles)  # Debug log
        
        return jsonify({
            'status': 'success',
            'data': detalles
        })

    except Exception as e:
        print(f"Error al obtener detalles de asignación: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener detalles de la asignación: {str(e)}'
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/logistica/exportar_asignaciones_csv')
@login_required()
@role_required('logistica')
def exportar_asignaciones_csv():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener todas las asignaciones con información del técnico
        cursor.execute("""
            SELECT 
                a.*,
                r.nombre as nombre_tecnico,
                r.recurso_operativo_cedula as cedula_tecnico,
                r.cargo as cargo_tecnico
            FROM asignacion a 
            LEFT JOIN recurso_operativo r ON a.id_codigo_consumidor = r.id_codigo_consumidor 
            ORDER BY a.asignacion_fecha DESC
        """)
        asignaciones = cursor.fetchall()
        
        # Crear archivo CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Escribir encabezados
        writer.writerow([
            'ID Asignación',
            'Fecha',
            'Técnico',
            'Cédula',
            'Cargo',
            'Estado',
            'Adaptador Mandril',
            'Alicate',
            'Barra 45cm',
            'Bisturí Metálico',
            'Caja de Herramientas',
            'Cortafrío',
            'Destornillador Estrella',
            'Destornillador Pala',
            'Destornillador Tester',
            'Martillo',
            'Pinza de Punta',
            'Multímetro',
            'Taladro Percutor',
            'Ponchadora RG6/RG11',
            'Ponchadora RJ45/RJ11',
            'Power Meter',
            'BFL Laser',
            'Cortadora',
            'Stripper Fibra',
            'Arnés',
            'Eslinga',
            'Casco Tipo II',
            'Araña Casco',
            'Barbuquejo',
            'Guantes de Vaqueta',
            'Gafas',
            'Línea de Vida'
        ])
        
        # Escribir datos
        for asignacion in asignaciones:
            writer.writerow([
                asignacion['id_asignacion'],
                asignacion['asignacion_fecha'].strftime('%Y-%m-%d %H:%M:%S'),
                asignacion.get('nombre_tecnico', 'No asignado'),
                asignacion.get('cedula_tecnico', 'No disponible'),
                asignacion.get('asignacion_cargo', 'No especificado'),
                'Activo' if str(asignacion.get('asignacion_estado', '0')) == '1' else 'Inactivo',
                asignacion.get('asignacion_adaptador_mandril', '0'),
                asignacion.get('asignacion_alicate', '0'),
                asignacion.get('asignacion_barra_45cm', '0'),
                asignacion.get('asignacion_bisturi_metalico', '0'),
                asignacion.get('asignacion_caja_de_herramientas', '0'),
                asignacion.get('asignacion_cortafrio', '0'),
                asignacion.get('asignacion_destor_de_estrella', '0'),
                asignacion.get('asignacion_destor_de_pala', '0'),
                asignacion.get('asignacion_destor_tester', '0'),
                asignacion.get('asignacion_martillo_de_una', '0'),
                asignacion.get('asignacion_pinza_de_punta', '0'),
                asignacion.get('asignacion_multimetro', '0'),
                asignacion.get('asignacion_taladro_percutor', '0'),
                asignacion.get('asignacion_ponchadora_rg_6_y_rg_11', '0'),
                asignacion.get('asignacion_ponchadora_rj_45_y_rj11', '0'),
                asignacion.get('asignacion_power_miter', '0'),
                asignacion.get('asignacion_bfl_laser', '0'),
                asignacion.get('asignacion_cortadora', '0'),
                asignacion.get('asignacion_stripper_fibra', '0'),
                
            ])
        
        # Preparar respuesta
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),  # Usar UTF-8 con BOM para soporte de caracteres especiales
            mimetype='text/csv; charset=utf-8-sig',
            as_attachment=True,
            download_name=f'asignaciones_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/logistica/inventario')
@login_required()
@role_required('logistica')
def ver_inventario():
    try:
        connection = get_db_connection()
        if connection is None:
            return render_template('error.html', 
                               mensaje='Error de conexión a la base de datos',
                               error='No se pudo establecer conexión con la base de datos')
                               
        cursor = connection.cursor(dictionary=True)
        
        # Obtener conteo de herramientas básicas asignadas
        herramientas_basicas_query = """
            SELECT 
                SUM(asignacion_adaptador_mandril) as adaptador_mandril,
                SUM(asignacion_alicate) as alicate,
                SUM(asignacion_barra_45cm) as barra_45cm,
                SUM(asignacion_bisturi_metalico) as bisturi_metalico,
                SUM(asignacion_caja_de_herramientas) as caja_herramientas,
                SUM(asignacion_cortafrio) as cortafrio,
                SUM(asignacion_destor_de_estrella) as destornillador_estrella,
                SUM(asignacion_destor_de_pala) as destornillador_pala,
                SUM(asignacion_destor_tester) as destornillador_tester,
                SUM(asignacion_martillo_de_una) as martillo,
                SUM(asignacion_pinza_de_punta) as pinza_punta
            FROM asignacion 
            WHERE asignacion_estado = '1'
        """
        cursor.execute(herramientas_basicas_query)
        herramientas_basicas = cursor.fetchone()
        
        # Obtener conteo de herramientas especializadas asignadas
        herramientas_especializadas_query = """
            SELECT 
                SUM(asignacion_multimetro) as multimetro,
                SUM(asignacion_taladro_percutor) as taladro_percutor,
                SUM(asignacion_ponchadora_rg_6_y_rg_11) as ponchadora_rg6_rg11,
                SUM(asignacion_ponchadora_rj_45_y_rj11) as ponchadora_rj45_rj11,
                SUM(asignacion_power_miter) as power_meter,
                SUM(asignacion_bfl_laser) as bfl_laser,
                SUM(asignacion_cortadora) as cortadora,
                SUM(asignacion_stripper_fibra) as stripper_fibra
            FROM asignacion 
            WHERE asignacion_estado = '1'
        """
        cursor.execute(herramientas_especializadas_query)
        herramientas_especializadas = cursor.fetchone()
        
       

        # Obtener conteo de material ferretero asignado
        material_ferretero_query = """
            SELECT 
                SUM(silicona) as silicona,
                SUM(amarres_negros) as amarres_negros,
                SUM(amarres_blancos) as amarres_blancos,
                SUM(cinta_aislante) as cinta_aislante,
                SUM(grapas_blancas) as grapas_blancas,
                SUM(grapas_negras) as grapas_negras
            FROM ferretero
        """
        cursor.execute(material_ferretero_query)
        material_ferretero = cursor.fetchone()
        
        # Obtener historial de movimientos de inventario (para gráficos de tendencia)
        historial_movimientos_query = """
            SELECT 
                DATE(fecha_movimiento) as fecha,
                tipo_movimiento,
                item_afectado,
                cantidad,
                usuario,
                ubicacion
            FROM movimientos_inventario
            ORDER BY fecha_movimiento DESC
            LIMIT 100
        """
        cursor.execute(historial_movimientos_query)
        historial_movimientos = cursor.fetchall()
        
        # Generar datos para gráficos de tendencias
        ultimos_30_dias = []
        hoy = datetime.now().date()
        for i in range(30, -1, -1):
            fecha = hoy - timedelta(days=i)
            ultimos_30_dias.append(fecha.strftime('%Y-%m-%d'))
        
        # Conteo de movimientos por fecha para gráfico de tendencia
        movimientos_por_dia = {}
        for fecha in ultimos_30_dias:
            movimientos_por_dia[fecha] = 0
            
        for movimiento in historial_movimientos:
            fecha_str = movimiento['fecha'].strftime('%Y-%m-%d')
            if fecha_str in movimientos_por_dia:
                movimientos_por_dia[fecha_str] += 1
                
        # Conteo por categoría para gráficos de distribución
        categorias = {
            'Herramientas Básicas': sum(value for key, value in herramientas_basicas.items() if value is not None),
            'Herramientas Especializadas': sum(value for key, value in herramientas_especializadas.items() if value is not None),
            'Material Ferretero': sum(value for key, value in material_ferretero.items() if value is not None)
        }
        
        # Información para alertas (items con nivel crítico)
        items_criticos = []
        
        # Definir umbrales para cada tipo de elemento
        umbrales_minimos = {
            'adaptador_mandril': 5, 'alicate': 10, 'barra_45cm': 5,
            'bisturi_metalico': 15, 'caja_herramientas': 10, 'cortafrio': 10,
            'destornillador_estrella': 15, 'destornillador_pala': 15,
            'destornillador_tester': 10, 'martillo': 10, 'pinza_punta': 10,
            'multimetro': 5, 'taladro_percutor': 3, 'ponchadora_rg6_rg11': 5,
            'ponchadora_rj45_rj11': 5, 'power_meter': 3, 'bfl_laser': 3,
            'cortadora': 3, 'stripper_fibra': 3, 'arnes': 10, 'eslinga': 10,
            'casco_tipo_ii': 20, 'arana_casco': 20, 'barbuquejo': 20,
            'guantes_vaqueta': 30, 'gafas': 30, 'linea_vida': 5,
            'silicona': 10, 'amarres_negros': 50, 'amarres_blancos': 50,
            'cinta_aislante': 20, 'grapas_blancas': 100, 'grapas_negras': 100
        }
        
        # Verificar herramientas básicas bajo umbral
        for key, value in herramientas_basicas.items():
            if key in umbrales_minimos and value is not None:
                if value <= umbrales_minimos[key]:
                    nombre_item = key.replace('_', ' ').title()
                    items_criticos.append({
                        'item': nombre_item, 
                        'actual': value, 
                        'minimo': umbrales_minimos[key],
                        'categoria': 'Herramientas Básicas'
                    })
        
        # Verificar herramientas especializadas bajo umbral
        for key, value in herramientas_especializadas.items():
            if key in umbrales_minimos and value is not None:
                if value <= umbrales_minimos[key]:
                    nombre_item = key.replace('_', ' ').title()
                    items_criticos.append({
                        'item': nombre_item, 
                        'actual': value, 
                        'minimo': umbrales_minimos[key],
                        'categoria': 'Herramientas Especializadas'
                    })
        
      
        
        # Verificar material ferretero bajo umbral
        for key, value in material_ferretero.items():
            if key in umbrales_minimos and value is not None:
                if value <= umbrales_minimos[key]:
                    nombre_item = key.replace('_', ' ').title()
                    items_criticos.append({
                        'item': nombre_item, 
                        'actual': value, 
                        'minimo': umbrales_minimos[key],
                        'categoria': 'Material Ferretero'
                    })
        
        # Obtener datos para comparativa periódica (mes actual vs mes anterior)
        # Esta es una simulación - en un caso real se obtendría de los registros históricos
        mes_actual = datetime.now().month
        año_actual = datetime.now().year
        
        comparativa_meses = {
            'labels': ['Mes Anterior', 'Mes Actual'],
            'datos': [215, 243]  # Datos de ejemplo
        }
        
        # Simulación de datos para ubicaciones
        ubicaciones = [
            {'nombre': 'Almacén Principal', 'items': 452},
            {'nombre': 'Bodega Norte', 'items': 230},
            {'nombre': 'Bodega Sur', 'items': 195},
            {'nombre': 'Vehículos', 'items': 123},
            {'nombre': 'Personal', 'items': 87}
        ]
        
        cursor.close()
        connection.close()

        return render_template('modulos/logistica/inventario.html',
                           herramientas_basicas=herramientas_basicas,
                           herramientas_especializadas=herramientas_especializadas,
                           
                           material_ferretero=material_ferretero,
                           historial_movimientos=historial_movimientos,
                           movimientos_por_dia=movimientos_por_dia,
                           ultimos_30_dias=ultimos_30_dias,
                           categorias=categorias,
                           items_criticos=items_criticos,
                           comparativa_meses=comparativa_meses,
                           ubicaciones=ubicaciones)

    except Exception as e:
        print(f"Error al obtener inventario: {str(e)}")
        return render_template('error.html',
                           mensaje='Error al cargar el inventario',
                           error=str(e))

@app.route('/logistica/ferretero')
@login_required()
@role_required('logistica')
def ver_asignaciones_ferretero():
    try:
        connection = get_db_connection()
        if connection is None:
            return render_template('error.html', 
                               mensaje='Error de conexión a la base de datos',
                               error='No se pudo establecer conexión con la base de datos')
                               
        cursor = connection.cursor(dictionary=True)
        
        # Obtener todas las asignaciones ferreteras con información del técnico
        cursor.execute("""
            SELECT f.*, r.nombre, r.recurso_operativo_cedula, r.cargo
            FROM ferretero f 
            LEFT JOIN recurso_operativo r ON f.id_codigo_consumidor = r.id_codigo_consumidor 
            ORDER BY f.fecha_asignacion DESC
        """)
        asignaciones = cursor.fetchall()

        # Obtener lista de técnicos disponibles
        cursor.execute("""
            SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula, cargo, carpeta 
            FROM recurso_operativo 
            WHERE cargo LIKE '%TECNICO%' OR cargo LIKE '%TÉCNICO%'
            ORDER BY nombre
        """)
        tecnicos = cursor.fetchall()
        
        # Preparar información de límites para cada técnico
        fecha_actual = datetime.now()
        tecnicos_con_limites = []
        
        # Definir límites según área de trabajo (igual que en registrar_ferretero)
        limites = {
            'FTTH INSTALACIONES': {
                'cinta_aislante': {'cantidad': 3, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 16, 'periodo': 7, 'unidad': 'días'},
                'amarres': {'cantidad': 50, 'periodo': 7, 'unidad': 'días'},
                'grapas': {'cantidad': 100, 'periodo': 7, 'unidad': 'días'}
            },
            'INSTALACIONES DOBLES': {
                'cinta_aislante': {'cantidad': 3, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 16, 'periodo': 7, 'unidad': 'días'},
                'amarres': {'cantidad': 50, 'periodo': 7, 'unidad': 'días'},
                'grapas': {'cantidad': 100, 'periodo': 7, 'unidad': 'días'}
            },
            'POSTVENTA': {
                'cinta_aislante': {'cantidad': 3, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 16, 'periodo': 7, 'unidad': 'días'},
                'amarres': {'cantidad': 50, 'periodo': 7, 'unidad': 'días'},
                'grapas': {'cantidad': 100, 'periodo': 7, 'unidad': 'días'}
            },
            'MANTENIMIENTO FTTH': {
                'cinta_aislante': {'cantidad': 1, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 8, 'periodo': 7, 'unidad': 'días'},
                'amarres': {'cantidad': 50, 'periodo': 15, 'unidad': 'días'},
                'grapas': {'cantidad': 100, 'periodo': 7, 'unidad': 'días'}
            },
            'ARREGLOS HFC': {
                'cinta_aislante': {'cantidad': 1, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 8, 'periodo': 7, 'unidad': 'días'},
                'amarres': {'cantidad': 50, 'periodo': 15, 'unidad': 'días'},
                'grapas': {'cantidad': 100, 'periodo': 7, 'unidad': 'días'}
            },
            'CONDUCTOR': {
                'cinta_aislante': {'cantidad': 100, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 100, 'periodo': 7, 'unidad': 'días'},
                'amarres': {'cantidad': 100, 'periodo': 15, 'unidad': 'días'},
                'grapas': {'cantidad': 100, 'periodo': 7, 'unidad': 'días'}
            }
        }
        
        for tecnico in tecnicos:
            # Determinar área de trabajo basada en la carpeta (prioridad) o el cargo
            carpeta = tecnico.get('carpeta', '').upper() if tecnico.get('carpeta') else ''
            cargo = tecnico.get('cargo', '').upper()
            
            area_trabajo = None
            
            # Primero intentar determinar por carpeta
            if carpeta:
                for area in limites.keys():
                    if area in carpeta:
                        area_trabajo = area
                        break
            
            # Si no se encontró por carpeta, intentar por cargo (como fallback)
            if area_trabajo is None:
                for area in limites.keys():
                    if area in cargo:
                        area_trabajo = area
                        break
            
            # Si no se encuentra un área específica, usar límites por defecto
            if area_trabajo is None:
                area_trabajo = 'POSTVENTA'  # Usar un valor por defecto
            
            # Obtener asignaciones previas para este técnico
            cursor.execute("""
                SELECT 
                    fecha_asignacion,
                    silicona,
                    amarres_negros,
                    amarres_blancos,
                    cinta_aislante,
                    grapas_blancas,
                    grapas_negras
                FROM ferretero 
                WHERE id_codigo_consumidor = %s
                ORDER BY fecha_asignacion DESC
            """, (tecnico['id_codigo_consumidor'],))
            asignaciones_tecnico = cursor.fetchall()
            
            # Inicializar contadores para materiales en los períodos correspondientes
            contadores = {
                'cinta_aislante': 0,
                'silicona': 0,
                'amarres': 0,
                'grapas': 0
            }
            
            # Calcular consumo previo en los periodos correspondientes
            for asignacion in asignaciones_tecnico:
                fecha_asignacion = asignacion['fecha_asignacion']
                diferencia_dias = (fecha_actual - fecha_asignacion).days
                
                # Verificar límite de cintas
                if diferencia_dias <= limites[area_trabajo]['cinta_aislante']['periodo']:
                    contadores['cinta_aislante'] += int(asignacion.get('cinta_aislante', 0) or 0)
                    
                # Verificar límite de siliconas
                if diferencia_dias <= limites[area_trabajo]['silicona']['periodo']:
                    contadores['silicona'] += int(asignacion.get('silicona', 0) or 0)
                    
                # Verificar límite de amarres (sumando negros y blancos)
                if diferencia_dias <= limites[area_trabajo]['amarres']['periodo']:
                    contadores['amarres'] += int(asignacion.get('amarres_negros', 0) or 0)
                    contadores['amarres'] += int(asignacion.get('amarres_blancos', 0) or 0)
                    
                # Verificar límite de grapas (sumando blancas y negras)
                if diferencia_dias <= limites[area_trabajo]['grapas']['periodo']:
                    contadores['grapas'] += int(asignacion.get('grapas_blancas', 0) or 0)
                    contadores['grapas'] += int(asignacion.get('grapas_negras', 0) or 0)
            
            # Calcular límites disponibles
            limites_disponibles = {
                'area': area_trabajo,
                'cinta_aislante': max(0, limites[area_trabajo]['cinta_aislante']['cantidad'] - contadores['cinta_aislante']),
                'silicona': max(0, limites[area_trabajo]['silicona']['cantidad'] - contadores['silicona']),
                'amarres': max(0, limites[area_trabajo]['amarres']['cantidad'] - contadores['amarres']),
                'grapas': max(0, limites[area_trabajo]['grapas']['cantidad'] - contadores['grapas']),
                'periodos': {
                    'cinta_aislante': f"{limites[area_trabajo]['cinta_aislante']['periodo']} {limites[area_trabajo]['cinta_aislante']['unidad']}",
                    'silicona': f"{limites[area_trabajo]['silicona']['periodo']} {limites[area_trabajo]['silicona']['unidad']}",
                    'amarres': f"{limites[area_trabajo]['amarres']['periodo']} {limites[area_trabajo]['amarres']['unidad']}",
                    'grapas': f"{limites[area_trabajo]['grapas']['periodo']} {limites[area_trabajo]['grapas']['unidad']}"
                }
            }
            
            # Agregar información de límites al técnico
            tecnico_con_limites = {**tecnico, 'limites': limites_disponibles}
            tecnicos_con_limites.append(tecnico_con_limites)
        
        cursor.close()
        connection.close()

        return render_template('modulos/logistica/ferretero.html', 
                            asignaciones=asignaciones,
                            tecnicos=tecnicos_con_limites)

    except Exception as e:
        print(f"Error al obtener asignaciones ferretero: {str(e)}")
        return render_template('error.html', 
                           mensaje='Error al cargar las asignaciones de material ferretero',
                           error=str(e))

@app.route('/logistica/registrar_ferretero', methods=['POST'])
@login_required()
@role_required('logistica')
def registrar_ferretero():
    connection = None
    cursor = None
    try:
        # Obtener datos básicos
        id_codigo_consumidor = request.form.get('id_codigo_consumidor')
        fecha = request.form.get('fecha')
        
        # Obtener cantidades de materiales
        silicona = request.form.get('silicona', '0')
        amarres_negros = request.form.get('amarres_negros', '0')
        amarres_blancos = request.form.get('amarres_blancos', '0')
        cinta_aislante = request.form.get('cinta_aislante', '0')
        grapas_blancas = request.form.get('grapas_blancas', '0')
        grapas_negras = request.form.get('grapas_negras', '0')

        # Validar campos requeridos
        if not all([id_codigo_consumidor, fecha]):
            return jsonify({
                'status': 'error',
                'message': 'El ID del técnico y la fecha son requeridos'
            }), 400

        connection = get_db_connection()
        if connection is None:
            return jsonify({
                'status': 'error',
                'message': 'Error de conexión a la base de datos'
            }), 500

        cursor = connection.cursor(dictionary=True)

        # Verificar que el técnico existe y obtener su área de trabajo (carpeta)
        cursor.execute('SELECT nombre, cargo, carpeta FROM recurso_operativo WHERE id_codigo_consumidor = %s', (id_codigo_consumidor,))
        tecnico = cursor.fetchone()
        
        if not tecnico:
            return jsonify({
                'status': 'error',
                'message': 'El técnico seleccionado no existe'
            }), 404
            
        # Obtener la fecha actual para cálculos
        fecha_actual = datetime.now()
        
        # Verificar asignaciones previas del técnico para controlar los límites
        cursor.execute("""
            SELECT 
                fecha_asignacion,
                silicona,
                amarres_negros,
                amarres_blancos,
                cinta_aislante,
                grapas_blancas,
                grapas_negras
            FROM ferretero 
            WHERE id_codigo_consumidor = %s
            ORDER BY fecha_asignacion DESC
        """, (id_codigo_consumidor,))
        asignaciones_previas = cursor.fetchall()
        
        # Determinar la carpeta/área del técnico
        carpeta = tecnico.get('carpeta', '').upper() if tecnico.get('carpeta') else ''
        cargo = tecnico.get('cargo', '').upper()
        
        # Definir límites según área de trabajo
        limites = {
            'FTTH INSTALACIONES': {
                'cinta_aislante': {'cantidad': 3, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 16, 'periodo': 7, 'unidad': 'días'},
                'amarres': {'cantidad': 50, 'periodo': 7, 'unidad': 'días'},
                'grapas': {'cantidad': 100, 'periodo': 7, 'unidad': 'días'}
            },
            'INSTALACIONES DOBLES': {
                'cinta_aislante': {'cantidad': 3, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 16, 'periodo': 7, 'unidad': 'días'},
                'amarres': {'cantidad': 50, 'periodo': 7, 'unidad': 'días'},
                'grapas': {'cantidad': 100, 'periodo': 7, 'unidad': 'días'}
            },
            'POSTVENTA': {
                'cinta_aislante': {'cantidad': 3, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 16, 'periodo': 7, 'unidad': 'días'},
                'amarres': {'cantidad': 50, 'periodo': 7, 'unidad': 'días'},
                'grapas': {'cantidad': 100, 'periodo': 7, 'unidad': 'días'}
            },
            'MANTENIMIENTO FTTH': {
                'cinta_aislante': {'cantidad': 1, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 8, 'periodo': 7, 'unidad': 'días'},
                'amarres': {'cantidad': 50, 'periodo': 15, 'unidad': 'días'},
                'grapas': {'cantidad': 100, 'periodo': 7, 'unidad': 'días'}
            },
            'ARREGLOS HFC': {
                'cinta_aislante': {'cantidad': 1, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 8, 'periodo': 7, 'unidad': 'días'},
                'amarres': {'cantidad': 50, 'periodo': 15, 'unidad': 'días'},
                'grapas': {'cantidad': 100, 'periodo': 7, 'unidad': 'días'}
            },
            'CONDUCTOR': {
                'cinta_aislante': {'cantidad': 100, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 100, 'periodo': 7, 'unidad': 'días'},
                'amarres': {'cantidad': 100, 'periodo': 15, 'unidad': 'días'},
                'grapas': {'cantidad': 100, 'periodo': 7, 'unidad': 'días'}
            }
        }
        
        # Determinar área de trabajo basada en la carpeta (prioridad) o el cargo
        area_trabajo = None
        
        # Primero intentar determinar por carpeta
        if carpeta:
            for area in limites.keys():
                if area in carpeta:
                    area_trabajo = area
                    break
        
        # Si no se encontró por carpeta, intentar por cargo (como fallback)
        if area_trabajo is None:
            for area in limites.keys():
                if area in cargo:
                    area_trabajo = area
                    break
        
        # Si no se encuentra un área específica, usar límites por defecto
        if area_trabajo is None:
            # Mensajes de advertencia en caso de que no se encuentre un área específica
            print(f"ADVERTENCIA: No se identificó área específica para la carpeta '{carpeta}' o cargo '{cargo}'. Usando límites por defecto.")
            area_trabajo = 'POSTVENTA'  # Usar un valor por defecto
        
        # Inicializar contadores para materiales en los períodos correspondientes
        contadores = {
            'cinta_aislante': 0,
            'silicona': 0,
            'amarres': 0,
            'grapas': 0
        }
        
        # Calcular consumo previo en los periodos correspondientes
        for asignacion in asignaciones_previas:
            fecha_asignacion = asignacion['fecha_asignacion']
            diferencia_dias = (fecha_actual - fecha_asignacion).days
            
            # Verificar límite de cintas
            if diferencia_dias <= limites[area_trabajo]['cinta_aislante']['periodo']:
                contadores['cinta_aislante'] += int(asignacion.get('cinta_aislante', 0) or 0)
                
            # Verificar límite de siliconas
            if diferencia_dias <= limites[area_trabajo]['silicona']['periodo']:
                contadores['silicona'] += int(asignacion.get('silicona', 0) or 0)
                
            # Verificar límite de amarres (sumando negros y blancos)
            if diferencia_dias <= limites[area_trabajo]['amarres']['periodo']:
                contadores['amarres'] += int(asignacion.get('amarres_negros', 0) or 0)
                contadores['amarres'] += int(asignacion.get('amarres_blancos', 0) or 0)
                
            # Verificar límite de grapas (sumando blancas y negras)
            if diferencia_dias <= limites[area_trabajo]['grapas']['periodo']:
                contadores['grapas'] += int(asignacion.get('grapas_blancas', 0) or 0)
                contadores['grapas'] += int(asignacion.get('grapas_negras', 0) or 0)
        
        # Calcular cantidades de la asignación actual
        cintas_solicitadas = int(cinta_aislante or 0)
        siliconas_solicitadas = int(silicona or 0)
        amarres_solicitados = int(amarres_negros or 0) + int(amarres_blancos or 0)
        grapas_solicitadas = int(grapas_blancas or 0) + int(grapas_negras or 0)
        
        # Validaciones de límites
        errores = []
        
        # Validar cintas
        if contadores['cinta_aislante'] + cintas_solicitadas > limites[area_trabajo]['cinta_aislante']['cantidad']:
            limite = limites[area_trabajo]['cinta_aislante']
            errores.append(f"Excede el límite de {limite['cantidad']} cintas cada {limite['periodo']} {limite['unidad']} para {area_trabajo}. Ya se han asignado {contadores['cinta_aislante']}.")
        
        # Validar siliconas
        if contadores['silicona'] + siliconas_solicitadas > limites[area_trabajo]['silicona']['cantidad']:
            limite = limites[area_trabajo]['silicona']
            errores.append(f"Excede el límite de {limite['cantidad']} siliconas cada {limite['periodo']} {limite['unidad']} para {area_trabajo}. Ya se han asignado {contadores['silicona']}.")
        
        # Validar amarres
        if contadores['amarres'] + amarres_solicitados > limites[area_trabajo]['amarres']['cantidad']:
            limite = limites[area_trabajo]['amarres']
            errores.append(f"Excede el límite de {limite['cantidad']} amarres cada {limite['periodo']} {limite['unidad']} para {area_trabajo}. Ya se han asignado {contadores['amarres']}.")
        
        # Validar grapas
        if contadores['grapas'] + grapas_solicitadas > limites[area_trabajo]['grapas']['cantidad']:
            limite = limites[area_trabajo]['grapas']
            errores.append(f"Excede el límite de {limite['cantidad']} grapas cada {limite['periodo']} {limite['unidad']} para {area_trabajo}. Ya se han asignado {contadores['grapas']}.")
        
        # Si hay errores, rechazar la asignación
        if errores:
            return jsonify({
                'status': 'error',
                'message': 'La asignación excede los límites permitidos',
                'detalles': errores
            }), 400
        
        # Insertar la asignación
        cursor.execute("""
            INSERT INTO ferretero (
                id_codigo_consumidor, 
                fecha_asignacion,
                silicona,
                amarres_negros,
                amarres_blancos,
                cinta_aislante,
                grapas_blancas,
                grapas_negras
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            id_codigo_consumidor,
            fecha,
            silicona,
            amarres_negros,
            amarres_blancos,
            cinta_aislante,
            grapas_blancas,
            grapas_negras
        ))
        
        connection.commit()

        return jsonify({
            'status': 'success',
            'message': f'Material ferretero asignado exitosamente para {area_trabajo}'
        }), 201

    except mysql.connector.Error as e:
        print(f"Error MySQL: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error en la base de datos: {str(e)}'
        }), 500
    except Exception as e:
        print(f"Error general: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error al registrar la asignación: {str(e)}'
        }), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/logistica/exportar_ferretero_csv')
@login_required()
@role_required('logistica')
def exportar_ferretero_csv():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener todas las asignaciones con información del técnico
        cursor.execute("""
            SELECT 
                f.*,
                r.nombre as nombre_tecnico,
                r.recurso_operativo_cedula as cedula_tecnico,
                r.cargo as cargo_tecnico
            FROM ferretero f 
            LEFT JOIN recurso_operativo r ON f.id_codigo_consumidor = r.id_codigo_consumidor 
            ORDER BY f.fecha_asignacion DESC
        """)
        asignaciones = cursor.fetchall()
        
        # Crear archivo CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Escribir encabezados
        writer.writerow([
            'ID Asignación',
            'Fecha',
            'Técnico',
            'Cédula',
            'Cargo',
            'Silicona',
            'Amarres Negros',
            'Amarres Blancos',
            'Cinta Aislante',
            'Grapas Blancas',
            'Grapas Negras'
        ])
        
        # Escribir datos
        for asignacion in asignaciones:
            writer.writerow([
                asignacion['id_ferretero'],
                asignacion['fecha_asignacion'].strftime('%Y-%m-%d %H:%M:%S'),
                asignacion.get('nombre_tecnico', 'No asignado'),
                asignacion.get('cedula_tecnico', 'No disponible'),
                asignacion.get('cargo_tecnico', 'No especificado'),
                asignacion.get('silicona', '0'),
                asignacion.get('amarres_negros', '0'),
                asignacion.get('amarres_blancos', '0'),
                asignacion.get('cinta_aislante', '0'),
                asignacion.get('grapas_blancas', '0'),
                asignacion.get('grapas_negras', '0')
            ])
        
        # Preparar respuesta
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv; charset=utf-8-sig',
            as_attachment=True,
            download_name=f'material_ferretero_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/logistica/automotor')
@login_required()
@role_required('logistica')
def ver_parque_automotor():
    try:
        connection = get_db_connection()
        if connection is None:
            return render_template('error.html', 
                               mensaje='Error de conexión a la base de datos',
                               error='No se pudo establecer conexión con la base de datos')
                               
        cursor = connection.cursor(dictionary=True)
        
        # Obtener todos los vehículos con información del técnico asignado
        cursor.execute("""
            SELECT pa.*, r.nombre, r.recurso_operativo_cedula, r.cargo
            FROM parque_automotor pa 
            LEFT JOIN recurso_operativo r ON pa.id_codigo_consumidor = r.id_codigo_consumidor 
            ORDER BY pa.fecha_asignacion DESC
        """)
        vehiculos = cursor.fetchall()

        # Convertir fechas de vencimiento a objetos datetime.date
        for vehiculo in vehiculos:
            if isinstance(vehiculo['soat_vencimiento'], datetime):
                vehiculo['soat_vencimiento'] = vehiculo['soat_vencimiento'].date()
            if isinstance(vehiculo['tecnomecanica_vencimiento'], datetime):
                vehiculo['tecnomecanica_vencimiento'] = vehiculo['tecnomecanica_vencimiento'].date()

        # Obtener lista de técnicos disponibles
        cursor.execute("""
            SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula, cargo 
            FROM recurso_operativo 
            WHERE cargo LIKE '%TECNICO%' OR cargo LIKE '%TÉCNICO%'
            ORDER BY nombre
        """)
        tecnicos = cursor.fetchall()
        
        cursor.close()
        connection.close()

        return render_template('modulos/logistica/automotor.html', 
                            vehiculos=vehiculos,
                            tecnicos=tecnicos,
                            fecha_actual=datetime.now().date())

    except Exception as e:
        print(f"Error al obtener parque automotor: {str(e)}")
        return render_template('error.html', 
                           mensaje='Error al cargar el parque automotor',
                           error=str(e))

@app.route('/logistica/registrar_vehiculo', methods=['POST'])
@login_required()
@role_required('logistica')
def registrar_vehiculo():
    connection = None
    cursor = None
    try:
        # Obtener datos del formulario
        placa = request.form.get('placa')
        tipo_vehiculo = request.form.get('tipo_vehiculo')
        marca = request.form.get('marca')
        modelo = request.form.get('modelo')
        color = request.form.get('color')
        id_codigo_consumidor = request.form.get('id_codigo_consumidor')
        fecha_asignacion = request.form.get('fecha_asignacion')
        soat_vencimiento = request.form.get('soat_vencimiento')
        tecnomecanica_vencimiento = request.form.get('tecnomecanica_vencimiento')
        observaciones = request.form.get('observaciones')

        # Validar campos requeridos
        if not all([placa, tipo_vehiculo, marca, modelo, color, fecha_asignacion]):
            return jsonify({
                'status': 'error',
                'message': 'Todos los campos marcados con * son requeridos'
            }), 400

        connection = get_db_connection()
        if connection is None:
            return jsonify({
                'status': 'error',
                'message': 'Error de conexión a la base de datos'
            }), 500

        cursor = connection.cursor(dictionary=True)

        # Verificar si la placa ya existe
        cursor.execute('SELECT placa FROM parque_automotor WHERE placa = %s', (placa,))
        if cursor.fetchone():
            return jsonify({
                'status': 'error',
                'message': 'Ya existe un vehículo registrado con esta placa'
            }), 400

        # Insertar el nuevo vehículo
        cursor.execute("""
            INSERT INTO parque_automotor (
                placa, tipo_vehiculo, marca, modelo, color, 
                id_codigo_consumidor, fecha_asignacion,
                soat_vencimiento, tecnomecanica_vencimiento, observaciones
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            placa, tipo_vehiculo, marca, modelo, color,
            id_codigo_consumidor, fecha_asignacion,
            soat_vencimiento, tecnomecanica_vencimiento, observaciones
        ))
        
        connection.commit()

        return jsonify({
            'status': 'success',
            'message': 'Vehículo registrado exitosamente'
        }), 201

    except mysql.connector.Error as e:
        print(f"Error MySQL: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error en la base de datos: {str(e)}'
        }), 500
    except Exception as e:
        print(f"Error general: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error al registrar el vehículo: {str(e)}'
        }), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/logistica/actualizar_vehiculo/<int:id_parque_automotor>', methods=['POST'])
@login_required()
@role_required('logistica')
def actualizar_vehiculo(id_parque_automotor):
    connection = None
    cursor = None
    try:
        # Obtener datos del formulario
        placa = request.form.get('placa')
        tipo_vehiculo = request.form.get('tipo_vehiculo')
        marca = request.form.get('marca')
        modelo = request.form.get('modelo')
        color = request.form.get('color')
        id_codigo_consumidor = request.form.get('id_codigo_consumidor')
        fecha_asignacion = request.form.get('fecha_asignacion')
        estado = request.form.get('estado', 'Activo')
        soat_vencimiento = request.form.get('soat_vencimiento')
        tecnomecanica_vencimiento = request.form.get('tecnomecanica_vencimiento')
        observaciones = request.form.get('observaciones', '')

        # Validar campos requeridos
        if not all([placa, tipo_vehiculo, marca, modelo, color, fecha_asignacion]):
            return jsonify({
                'status': 'error',
                'message': 'Todos los campos marcados con * son requeridos'
            }), 400

        # Convertir id_codigo_consumidor a None si está vacío
        id_codigo_consumidor = None if not id_codigo_consumidor else id_codigo_consumidor

        # Convertir fechas vacías a None
        soat_vencimiento = None if not soat_vencimiento else soat_vencimiento
        tecnomecanica_vencimiento = None if not tecnomecanica_vencimiento else tecnomecanica_vencimiento

        connection = get_db_connection()
        if connection is None:
            return jsonify({
                'status': 'error',
                'message': 'Error de conexión a la base de datos'
            }), 500

        cursor = connection.cursor(dictionary=True)

        # Verificar si el vehículo existe
        cursor.execute('SELECT id_parque_automotor FROM parque_automotor WHERE id_parque_automotor = %s', (id_parque_automotor,))
        if not cursor.fetchone():
            return jsonify({
                'status': 'error',
                'message': 'El vehículo no existe'
            }), 404

        # Verificar si la placa ya existe para otro vehículo
        cursor.execute('SELECT id_parque_automotor FROM parque_automotor WHERE placa = %s AND id_parque_automotor != %s', (placa, id_parque_automotor))
        if cursor.fetchone():
            return jsonify({
                'status': 'error',
                'message': 'Ya existe otro vehículo registrado con esta placa'
            }), 400

        # Actualizar el vehículo
        cursor.execute("""
            UPDATE parque_automotor SET
                placa = %s,
                tipo_vehiculo = %s,
                marca = %s,
                modelo = %s,
                color = %s,
                id_codigo_consumidor = %s,
                fecha_asignacion = %s,
                estado = %s,
                soat_vencimiento = %s,
                tecnomecanica_vencimiento = %s,
                observaciones = %s
            WHERE id_parque_automotor = %s
        """, (
            placa, tipo_vehiculo, marca, modelo, color,
            id_codigo_consumidor, fecha_asignacion, estado,
            soat_vencimiento, tecnomecanica_vencimiento,
            observaciones, id_parque_automotor
        ))
        
        connection.commit()

        return jsonify({
            'status': 'success',
            'message': 'Vehículo actualizado exitosamente'
        })

    except mysql.connector.Error as e:
        print(f"Error MySQL en actualización: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error al actualizar en la base de datos: {str(e)}'
        }), 500
    except Exception as e:
        print(f"Error general en actualizar_vehiculo: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error al actualizar el vehículo: {str(e)}'
        }), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/logistica/exportar_automotor_csv')
@login_required()
@role_required('logistica')
def exportar_automotor_csv():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener todos los vehículos con información del técnico
        cursor.execute("""
            SELECT 
                pa.placa,
                pa.tipo_vehiculo,
                pa.marca,
                pa.modelo,
                pa.color,
                r.nombre as nombre_tecnico,
                r.recurso_operativo_cedula as cedula_tecnico,
                r.cargo as cargo_tecnico,
                pa.fecha_asignacion,
                pa.estado,
                pa.soat_vencimiento,
                pa.tecnomecanica_vencimiento,
                pa.observaciones
            FROM parque_automotor pa 
            LEFT JOIN recurso_operativo r ON pa.id_codigo_consumidor = r.id_codigo_consumidor 
            ORDER BY pa.fecha_asignacion DESC
        """)
        vehiculos = cursor.fetchall()
        
        # Crear archivo CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Escribir encabezados
        writer.writerow([
            'Placa',
            'Tipo Vehículo',
            'Marca',
            'Modelo',
            'Color',
            'Técnico Asignado',
            'Cédula Técnico',
            'Cargo Técnico',
            'Fecha Asignación',
            'Estado',
            'Vencimiento SOAT',
            'Vencimiento Tecnomecánica',
            'Observaciones'
        ])
        
        # Escribir datos
        for vehiculo in vehiculos:
            writer.writerow([
                vehiculo['placa'],
                vehiculo['tipo_vehiculo'],
                vehiculo['marca'],
                vehiculo['modelo'],
                vehiculo['color'],
                vehiculo.get('nombre_tecnico', 'No asignado'),
                vehiculo.get('cedula_tecnico', 'No disponible'),
                vehiculo.get('cargo_tecnico', 'No especificado'),
                vehiculo['fecha_asignacion'].strftime('%Y-%m-%d') if vehiculo['fecha_asignacion'] else '',
                vehiculo.get('estado', 'Activo'),
                vehiculo['soat_vencimiento'].strftime('%Y-%m-%d') if vehiculo['soat_vencimiento'] else '',
                vehiculo['tecnomecanica_vencimiento'].strftime('%Y-%m-%d') if vehiculo['tecnomecanica_vencimiento'] else '',
                vehiculo.get('observaciones', '')
            ])
        
        # Preparar respuesta
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv; charset=utf-8-sig',
            as_attachment=True,
            download_name=f'parque_automotor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/logistica/ultima_asignacion')
@login_required()
@role_required('logistica')
def obtener_ultima_asignacion():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({
                'status': 'error',
                'message': 'Error de conexión a la base de datos'
            }), 500

        cursor = connection.cursor(dictionary=True)
        
        # Obtener la última asignación creada (por ID, asumiendo que es autoincremental)
        cursor.execute("""
            SELECT id_asignacion 
            FROM asignacion 
            ORDER BY id_asignacion DESC 
            LIMIT 1
        """)
        
        resultado = cursor.fetchone()
        
        if resultado:
            return jsonify({
                'status': 'success',
                'id_asignacion': resultado['id_asignacion'],
                'message': 'Última asignación encontrada'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'No se encontraron asignaciones'
            }), 404

    except mysql.connector.Error as e:
        print(f"Error MySQL: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error en la base de datos: {str(e)}'
        }), 500
    except Exception as e:
        print(f"Error general: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener la última asignación: {str(e)}'
        }), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/logistica/registrar_asignacion_con_firma', methods=['POST'])
@login_required()
@role_required('logistica')
def registrar_asignacion_con_firma():
    connection = None
    cursor = None
    try:
        # Obtener datos básicos
        id_codigo_consumidor = request.form.get('id_codigo_consumidor')
        fecha = request.form.get('fecha')
        cargo = request.form.get('cargo')
        firma = request.form.get('firma')
        id_asignador = request.form.get('id_asignador')

        # Validar campos requeridos
        if not all([id_codigo_consumidor, fecha, cargo, firma, id_asignador]):
            return jsonify({
                'status': 'error',
                'message': 'Faltan campos requeridos para la asignación con firma'
            }), 400

        connection = get_db_connection()
        if connection is None:
            return jsonify({
                'status': 'error',
                'message': 'Error de conexión a la base de datos'
            }), 500

        cursor = connection.cursor(dictionary=True)

        # Verificar que el técnico existe
        cursor.execute('SELECT nombre FROM recurso_operativo WHERE id_codigo_consumidor = %s', (id_codigo_consumidor,))
        tecnico = cursor.fetchone()
        
        if not tecnico:
            return jsonify({
                'status': 'error',
                'message': 'El técnico seleccionado no existe'
            }), 404

        # Obtener la estructura de la tabla
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'asignacion'
        """)
        columnas_existentes = {row['COLUMN_NAME'].lower() for row in cursor.fetchall()}
        
        print("Columnas existentes:", columnas_existentes)  # Debug log

        # Campos base que siempre deben existir
        campos = ['id_codigo_consumidor', 'asignacion_fecha', 'asignacion_cargo']
        valores = [id_codigo_consumidor, fecha, cargo]

        # Lista de todas las herramientas posibles
        herramientas = [
            'adaptador_mandril', 'alicate', 'barra_45cm', 'bisturi_metalico',
            'broca_3_8', 'broca_386_ran', 'broca_126_ran',
            'broca_metalmadera_14', 'broca_metalmadera_38', 'broca_metalmadera_516',
            'caja_de_herramientas', 'cajon_rojo', 'cinta_de_senal', 'cono_retractil',
            'cortafrio', 'destor_de_estrella', 'destor_de_pala', 'destor_tester',
            'espatula', 'exten_de_corr_10_mts', 'llave_locking_male', 'llave_reliance',
            'llave_torque_rg_11', 'llave_torque_rg_6', 'llaves_mandril',
            'mandril_para_taladro', 'martillo_de_una', 'multimetro',
            'pelacable_rg_6y_rg_11', 'pinza_de_punta', 'pistola_de_silicona',
            'planillero', 'ponchadora_rg_6_y_rg_11', 'ponchadora_rj_45_y_rj11',
            'probador_de_tonos', 'probador_de_tonos_utp', 'puntas_para_multimetro',
            'sonda_metalica', 'tacos_de_madera', 'taladro_percutor',
            'telefono_de_pruebas', 'power_miter', 'bfl_laser', 'cortadora',
            'stripper_fibra', 'pelachaqueta'
        ]

        # Procesar cada herramienta
        for herramienta in herramientas:
            nombre_campo = f'asignacion_{herramienta}'
            if nombre_campo.lower() in columnas_existentes:
                campos.append(nombre_campo)
                valor = request.form.get(herramienta, '0')
                valores.append(valor if valor == '1' else '0')
            else:
                print(f"Campo ignorado (no existe en la tabla): {nombre_campo}")

        # Agregar estado por defecto si existe la columna
        if 'asignacion_estado' in columnas_existentes:
            campos.append('asignacion_estado')
            valores.append('1')
            
        # Agregar campos de firma y asignador
        if 'asignacion_firma' in columnas_existentes:
            campos.append('asignacion_firma')
            valores.append(firma)
            
        if 'id_asignador' in columnas_existentes:
            campos.append('id_asignador')
            valores.append(id_asignador)

        # Construir y ejecutar la consulta SQL
        sql = f"""
            INSERT INTO asignacion ({', '.join(campos)})
            VALUES ({', '.join(['%s'] * len(valores))})
        """
        
        print("SQL Query:", sql)  # Debug log
        print("Valores:", valores)  # Debug log

        cursor.execute(sql, tuple(valores))
        connection.commit()
        
        # Obtener el ID de la asignación recién creada
        cursor.execute("SELECT LAST_INSERT_ID() as id_asignacion")
        id_asignacion = cursor.fetchone()['id_asignacion']

        return jsonify({
            'status': 'success',
            'message': 'Asignación con firma registrada exitosamente',
            'id_asignacion': id_asignacion
        }), 201

    except mysql.connector.Error as e:
        print(f"Error MySQL: {str(e)}")  # Debug log
        return jsonify({
            'status': 'error',
            'message': f'Error en la base de datos: {str(e)}'
        }), 500
    except Exception as e:
        print(f"Error general: {str(e)}")  # Debug log
        return jsonify({
            'status': 'error',
            'message': f'Error al registrar la asignación con firma: {str(e)}'
        }), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/logistica/guardar_firma', methods=['POST'])
@login_required()
@role_required('logistica')
def guardar_firma():
    connection = None
    cursor = None
    try:
        # Obtener datos del JSON
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No se recibieron datos JSON'
            }), 400
            
        id_asignacion = data.get('id_asignacion')
        firma = data.get('firma')
        id_asignador = data.get('id_asignador')

        # Validar campos requeridos
        if not all([id_asignacion, firma, id_asignador]):
            return jsonify({
                'status': 'error',
                'message': 'Faltan campos requeridos (id_asignacion, firma, id_asignador)'
            }), 400

        connection = get_db_connection()
        if connection is None:
            return jsonify({
                'status': 'error',
                'message': 'Error de conexión a la base de datos'
            }), 500

        cursor = connection.cursor(dictionary=True)

        # Verificar que la asignación existe
        cursor.execute('SELECT id_asignacion FROM asignacion WHERE id_asignacion = %s', (id_asignacion,))
        asignacion = cursor.fetchone()
        
        if not asignacion:
            return jsonify({
                'status': 'error',
                'message': 'La asignación no existe'
            }), 404

        # Actualizar la asignación con la firma
        cursor.execute("""
            UPDATE asignacion 
            SET asignacion_firma = %s, id_asignador = %s 
            WHERE id_asignacion = %s
        """, (firma, id_asignador, id_asignacion))
        
        connection.commit()

        return jsonify({
            'status': 'success',
            'message': 'Firma guardada exitosamente'
        })

    except mysql.connector.Error as e:
        print(f"Error MySQL: {str(e)}")  # Debug log
        return jsonify({
            'status': 'error',
            'message': f'Error en la base de datos: {str(e)}'
        }), 500
    except Exception as e:
        print(f"Error general: {str(e)}")  # Debug log
        return jsonify({
            'status': 'error',
            'message': f'Error al guardar la firma: {str(e)}'
        }), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/logistica/guardar_asignacion', methods=['POST'])
def guardar_asignacion():
    connection = None
    cursor = None
    try:
        # Obtener datos básicos del formulario
        id_codigo_consumidor = request.form.get('id_codigo_consumidor')
        fecha = request.form.get('fecha')
        cargo = request.form.get('cargo')
        
        # Validar datos requeridos
        if not id_codigo_consumidor or not fecha or not cargo:
            return jsonify({
                'status': 'error',
                'message': 'Faltan campos obligatorios'
            }), 400
            
        # Obtener conexión a la base de datos
        connection = get_db_connection()
        if not connection:
            return jsonify({
                'status': 'error',
                'message': 'Error al conectar con la base de datos'
            }), 500
            
        # Obtener información del técnico desde la base de datos
        query_tecnico = """
            SELECT nombre, recurso_operativo_cedula 
            FROM recurso_operativo
            WHERE id_codigo_consumidor = %s
        """
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query_tecnico, (id_codigo_consumidor,))
        tecnico = cursor.fetchone()
        
        if not tecnico:
            return jsonify({
                'status': 'error',
                'message': 'Técnico no encontrado'
            }), 404
        
        # Convertir fecha a formato datetime
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%dT%H:%M')
            fecha_formateada = fecha_obj.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Formato de fecha inválido'
            }), 400
            
        # Mapeo entre nombres de campos del formulario y nombres de campos en la base de datos (sin prefijo)
        mapeo_herramientas = {
            'adaptador_mandril': 'adaptador_mandril',
            'alicate': 'alicate',
            'barra_45cm': 'barra_45cm',
            'bisturi_metalico': 'bisturi_metalico',
            # Para las brocas, usamos nombres sin caracteres especiales
            'broca_3_8': 'broca_38',
            'broca_386_ran': 'broca_386_ran',
            'broca_126_ran': 'broca_126_ran',
            'broca_metalmadera_14': 'broca_metalmadera_14',
            'broca_metalmadera_38': 'broca_metalmadera_38',
            'broca_metalmadera_516': 'broca_metalmadera_516',
            'caja_de_herramientas': 'caja_de_herramientas',
            'cajon_rojo': 'cajon_rojo',
            'cinta_de_senal': 'cinta_de_senal',
            'cono_retractil': 'cono_retractil',
            'cortafrio': 'cortafrio',
            'destor_de_estrella': 'destor_de_estrella',
            'destor_de_pala': 'destor_de_pala',
            'destor_tester': 'destor_tester',
            'espatula': 'espatula',
            'exten_de_corr_10_mts': 'exten_de_corr_10_mts',
            'llave_locking_male': 'llave_locking_male',
            'llave_reliance': 'llave_reliance',
            'llave_torque_rg_11': 'llave_torque_rg_11',
            'llave_torque_rg_6': 'llave_torque_rg_6',
            'llaves_mandril': 'llaves_mandril',
            'mandril_para_taladro': 'mandril_para_taladro',
            'martillo_de_una': 'martillo_de_una',
            'multimetro': 'multimetro',
            'pelacable_rg_6y_rg_11': 'pelacable_rg_6y_rg_11',
            'pinza_de_punta': 'pinza_de_punta',
            'pistola_de_silicona': 'pistola_de_silicona',
            'planillero': 'planillero',
            'ponchadora_rg_6_y_rg_11': 'ponchadora_rg_6_y_rg_11',
            'ponchadora_rj_45_y_rj11': 'ponchadora_rj_45_y_rj11',
            'probador_de_tonos': 'probador_de_tonos',
            'probador_de_tonos_utp': 'probador_de_tonos_utp',
            'puntas_para_multimetro': 'puntas_para_multimetro',
            'sonda_metalica': 'sonda_metalica',
            'tacos_de_madera': 'tacos_de_madera',
            'taladro_percutor': 'taladro_percutor',
            'telefono_de_pruebas': 'telefono_de_pruebas',
            'power_miter': 'power_miter',
            'bfl_laser': 'bfl_laser',
            'cortadora': 'cortadora',
            'stripper_fibra': 'stripper_fibra',
            'pelachaqueta': 'pelachaqueta'
        }
            
        # Construir los valores para la consulta
        valores = {
            'id_codigo_consumidor': id_codigo_consumidor,
            'cedula': tecnico['recurso_operativo_cedula'],
            'nombre': tecnico['nombre'],
            'fecha': fecha_formateada,
            'cargo': cargo,
            'estado': '1'  # Activo por defecto
        }
        
        # Agregar herramientas con valor '0' por defecto
        for clave_form, clave_db in mapeo_herramientas.items():
            valores[clave_db] = '0'
        
        # Actualizar valores según lo seleccionado en el formulario
        for nombre_campo, valor in request.form.items():
            if nombre_campo in mapeo_herramientas and valor == '1':
                clave_db = mapeo_herramientas[nombre_campo]
                valores[clave_db] = '1'
        
        # Construir la consulta SQL
        nombres_columnas = []
        placeholders = []
        valores_lista = []
        
        # Campo id_codigo_consumidor (sin prefijo)
        nombres_columnas.append('id_codigo_consumidor')
        placeholders.append('%s')
        valores_lista.append(valores['id_codigo_consumidor'])
        
        # Campos con prefijo 'asignacion_'
        for campo, valor in valores.items():
            if campo != 'id_codigo_consumidor':
                # Usar prefijo asignacion_ para todos los demás campos
                nombre_columna = f"asignacion_{campo}"
                nombres_columnas.append(nombre_columna)
                placeholders.append('%s')
                valores_lista.append(valor)
        
        query = f"""
            INSERT INTO asignacion (
                {', '.join(nombres_columnas)}
            ) VALUES (
                {', '.join(placeholders)}
            )
        """
        
        # Ejecutar la consulta
        cursor.execute(query, valores_lista)
        id_asignacion = cursor.lastrowid
        connection.commit()
        
        # Registrar acción en log
        app.logger.info(
            f"Asignación {id_asignacion} creada para técnico "
            f"{tecnico['nombre']} ({tecnico['recurso_operativo_cedula']})"
        )
        
        # Responder con éxito y el ID de la asignación
        return jsonify({
            'status': 'success',
            'message': 'Asignación guardada correctamente',
            'id_asignacion': id_asignacion
        }), 200
         
    except mysql.connector.Error as e:
        print(f"Error MySQL en guardar_asignacion: {str(e)}")  # Debug log
        
        # En caso de error, hacer rollback
        if connection:
            try:
                connection.rollback()
            except:
                pass
                
        return jsonify({
            'status': 'error',
            'message': f'Error en la base de datos: {str(e)}'
        }), 500
    except Exception as e:
        print(f"Error general en guardar_asignacion: {str(e)}")  # Debug log
        
        # En caso de error, hacer rollback
        if connection:
            try:
                connection.rollback()
            except:
                pass
                
        # Log detallado para diagnóstico
        import traceback
        app.logger.error(traceback.format_exc())
        
        return jsonify({
            'status': 'error',
            'message': f'Error al guardar la asignación: {str(e)}'
        }), 500
    finally:
        # Asegurarse de cerrar cursor y conexión
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# Endpoint para guardar asignaciones simplificado
@app.route('/logistica/guardar_asignacion_simple', methods=['POST'])
def guardar_asignacion_simple():
    connection = None
    cursor = None
    try:
        # Obtener datos básicos del formulario
        id_codigo_consumidor = request.form.get('id_codigo_consumidor')
        fecha = request.form.get('fecha')
        cargo = request.form.get('cargo')
        
        # Validar datos requeridos
        if not id_codigo_consumidor or not fecha or not cargo:
            return jsonify({
                'status': 'error',
                'message': 'Faltan campos obligatorios'
            }), 400
            
        # Obtener conexión a la base de datos
        connection = get_db_connection()
        if not connection:
            return jsonify({
                'status': 'error',
                'message': 'Error al conectar con la base de datos'
            }), 500
            
        # Obtener información del técnico
        cursor = connection.cursor(dictionary=True)
        
        query_tecnico = """
            SELECT nombre, recurso_operativo_cedula 
            FROM recurso_operativo 
            WHERE id_codigo_consumidor = %s
        """
        cursor.execute(query_tecnico, (id_codigo_consumidor,))
        tecnico = cursor.fetchone()
        
        if not tecnico:
            return jsonify({
                'status': 'error',
                'message': 'Técnico no encontrado'
            }), 404
            
        # Convertir fecha a formato datetime
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%dT%H:%M')
            fecha_formateada = fecha_obj.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Formato de fecha inválido'
            }), 400
        
        # Construir la consulta SQL solo con información básica
        query = """
            INSERT INTO asignacion (
                id_codigo_consumidor, 
                asignacion_cedula, 
                asignacion_nombre, 
                asignacion_fecha, 
                asignacion_cargo, 
                asignacion_estado
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        # Ejecutar consulta
        try:
            cursor.execute(query, [
                id_codigo_consumidor,
                tecnico['recurso_operativo_cedula'],  # cedula
                tecnico['nombre'],  # nombre
                fecha_formateada,
                cargo,
                '1'  # Estado activo
            ])
            
            # Obtener ID y hacer commit
            id_asignacion = cursor.lastrowid
            connection.commit()
                
            return jsonify({
                'status': 'success',
                'message': 'Asignación básica guardada correctamente',
                'id_asignacion': id_asignacion
            }), 200
            
        except Exception as e:
            app.logger.error(f"Error al guardar asignación simple: {str(e)}")
            
            if connection:
                connection.rollback()
                    
            return jsonify({
                'status': 'error',
                'message': f'Error al guardar la asignación simple: {str(e)}'
            }), 500
        
    except Exception as e:
        app.logger.error(f"Error general en guardar_asignacion_simple: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error al procesar la solicitud: {str(e)}'
        }), 500
    finally:
        # Asegurarse de cerrar cursor y conexión
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/logistica/asignacion/<int:id_asignacion>/pdf', methods=['GET'])
@login_required()
@role_required('logistica')
def generar_pdf_asignacion(id_asignacion):
    try:
        # Verificar si se solicitó el PDF firmado
        mostrar_firma = request.args.get('firmado', 'false').lower() == 'true'
        app.logger.info(f"Generando PDF para asignación {id_asignacion} - Con firma: {mostrar_firma}")

        # Obtener la conexión a la base de datos
        connection = get_db_connection()
        if not connection:
            app.logger.error("Error al conectar con la base de datos para generar PDF")
            return jsonify({'status': 'error', 'message': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)

        # Consultar información de la asignación
        query = """
            SELECT a.*, 
                r.nombre AS recurso_nombre, 
                r.recurso_operativo_cedula
            FROM asignacion a
            JOIN recurso_operativo r ON a.id_codigo_consumidor = r.id_codigo_consumidor
            WHERE a.id_asignacion = %s
        """
        cursor.execute(query, (id_asignacion,))
        asignacion = cursor.fetchone()

        if not asignacion:
            cursor.close()
            connection.close()
            app.logger.warning(f"Asignación no encontrada para PDF: {id_asignacion}")
            return jsonify({'status': 'error', 'message': 'Asignación no encontrada'}), 404

        # En lugar de consultar una tabla inexistente, procesamos las herramientas desde la misma tabla de asignación
        # Las herramientas están almacenadas como columnas en la tabla asignacion con prefijo asignacion_
        herramientas_basicas = []
        brocas = []
        herramientas_red = []
        
        # Prefijos para identificar los tipos de herramientas (definidos aquí para usarlos en todo el método)
        prefijos_brocas = ['broca']
        prefijos_red = ['cajon', 'cinta', 'cono', 'exten', 'llave', 'mandril', 
                        'pelacable', 'ponchadora', 'probador', 'sonda', 'telefono',
                        'power', 'laser', 'cortadora', 'stripper']
        
        # Recorremos los campos de la asignación y extraemos las herramientas
        for key, value in asignacion.items():
            if (key.startswith('asignacion_') and 
                value == '1' and 
                not key in ['asignacion_fecha', 'asignacion_estado', 'asignacion_cargo',
                           'asignacion_cedula', 'asignacion_nombre']):
                # Quitar el prefijo asignacion_
                nombre_campo = key[11:]
                nombre_herramienta = nombre_campo.replace('_', ' ').title()
                
                # Clasificar por tipo
                es_broca = any(prefijo in nombre_campo.lower() for prefijo in prefijos_brocas)
                es_red = any(prefijo in nombre_campo.lower() for prefijo in prefijos_red)
                
                item_herramienta = {
                    'id_codigo_herramienta': nombre_campo,
                    'referencia': nombre_herramienta,
                    'herramienta_cedula': '',
                    'marca': '',
                    'modelo': '',
                    'serial': ''
                }
                
                if es_broca:
                    brocas.append(item_herramienta)
                elif es_red:
                    herramientas_red.append(item_herramienta)
                else:
                    herramientas_basicas.append(item_herramienta)
        
        # Combinamos todas las herramientas para mostrarlas en el PDF
        herramientas = herramientas_basicas + brocas + herramientas_red

        # Si se solicitó firmado, buscar firma en la base de datos
        firma_imagen = None
        if mostrar_firma:
            try:
                query_firma = """
                    SELECT firma_imagen, fecha_firma 
                    FROM firmas_asignaciones 
                    WHERE id_asignacion = %s 
                    ORDER BY fecha_firma DESC LIMIT 1
                """
                cursor.execute(query_firma, (id_asignacion,))
                resultado_firma = cursor.fetchone()
                
                if resultado_firma and resultado_firma['firma_imagen']:
                    app.logger.info(f"Firma encontrada para asignación {id_asignacion}")
                    firma_imagen = resultado_firma['firma_imagen']
                else:
                    app.logger.warning(f"No se encontró firma para la asignación {id_asignacion}")
            except Exception as e:
                app.logger.error(f"Error al buscar firma: {str(e)}")
                # Continuamos sin firma

        cursor.close()
        connection.close()

        # Crear buffer para el PDF
        buffer = BytesIO()
        
        # Crear PDF con ReportLab
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Contenido del PDF
        contenido = []
        
        # Añadir logo si existe
        try:
            logo_path = os.path.join(app.root_path, 'static', 'img', 'logo.png')
            if os.path.exists(logo_path):
                logo = RLImage(logo_path, width=150, height=50)
                contenido.append(logo)
                contenido.append(Spacer(1, 20))
            else:
                app.logger.warning("Logo no encontrado en: " + logo_path)
        except Exception as e:
            app.logger.error(f"Error al cargar logo: {str(e)}")
            # Continuar sin logo
            
        # Título
        estilos = getSampleStyleSheet()
        estilo_titulo = estilos['Heading1']
        estilo_titulo.alignment = 1  # Centrado
        titulo = Paragraph("DETALLE DE ASIGNACIÓN", estilo_titulo)
        contenido.append(titulo)
        contenido.append(Spacer(1, 20))
        
        # Información de la asignación
        estilo_normal = estilos['Normal']
        estilo_heading = estilos['Heading2']
        
        # Datos del recurso operativo
        contenido.append(Paragraph("Información de la Asignación", estilo_heading))
        contenido.append(Spacer(1, 10))
        
        datos_recurso = [
            ["Nombre", asignacion['recurso_nombre'] or ""],
            ["Cédula", asignacion['recurso_operativo_cedula'] or ""]
        ]
        
        tabla_recurso = Table(datos_recurso, colWidths=[100, 350])
        tabla_recurso.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        contenido.append(tabla_recurso)
        contenido.append(Spacer(1, 20))
        
        # Detalles de la asignación
        contenido.append(Paragraph("Detalles de la Asignación", estilo_heading))
        contenido.append(Spacer(1, 10))
        
        # Formatear la fecha
        fecha_asignacion = asignacion.get('asignacion_fecha')
        if fecha_asignacion:
            fecha_str = fecha_asignacion.strftime("%d/%m/%Y %H:%M") if isinstance(fecha_asignacion, datetime) else str(fecha_asignacion)
        else:
            fecha_str = "No especificada"
            
        datos_asignacion = [
            ["ID Asignación", str(asignacion['id_asignacion']) or ""],
            ["Fecha", fecha_str],
            ["Proyecto", asignacion.get('proyecto', "") or ""],
            ["Ubicación", asignacion.get('ubicacion', "") or ""],
            ["Observaciones", asignacion.get('observaciones', "") or ""]
        ]
        
        tabla_asignacion = Table(datos_asignacion, colWidths=[100, 350])
        tabla_asignacion.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        contenido.append(tabla_asignacion)
        contenido.append(Spacer(1, 20))
        
        # Lista de herramientas
        contenido.append(Paragraph("Herramientas Asignadas", estilo_heading))
        contenido.append(Spacer(1, 10))
        
        if herramientas:
            # Agrupar herramientas por tipo
            herramientas_por_tipo = {}
            for h in herramientas:
                tipo = 'Herramientas Básicas'
                if any(prefijo in h['id_codigo_herramienta'].lower() for prefijo in prefijos_brocas):
                    tipo = 'Brocas'
                elif any(prefijo in h['id_codigo_herramienta'].lower() for prefijo in prefijos_red):
                    tipo = 'Herramientas de Red'
                
                if tipo not in herramientas_por_tipo:
                    herramientas_por_tipo[tipo] = []
                herramientas_por_tipo[tipo].append(h)
            
            # Mostrar cada tipo de herramienta
            for tipo, items in herramientas_por_tipo.items():
                if items:
                    # Título del tipo
                    contenido.append(Paragraph(tipo, estilos['Heading3']))
                    contenido.append(Spacer(1, 5))
                    
                    # Tablas con hasta 3 columnas
                    filas = []
                    fila_actual = []
                    
                    for item in items:
                        fila_actual.append(item['referencia'])
                        if len(fila_actual) == 3:
                            filas.append(fila_actual)
                            fila_actual = []
                    
                    # Añadir la última fila si quedaron elementos
                    if fila_actual:
                        # Rellenar con espacios vacíos si es necesario
                        while len(fila_actual) < 3:
                            fila_actual.append("")
                        filas.append(fila_actual)
                    
                    # Crear tabla para este tipo
                    tabla = Table(filas, colWidths=[150, 150, 150])
                    tabla.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('PADDING', (0, 0), (-1, -1), 4),
                    ]))
                    contenido.append(tabla)
                    contenido.append(Spacer(1, 10))
        else:
            contenido.append(Paragraph("No hay herramientas asignadas", estilo_normal))
        
        contenido.append(Spacer(1, 30))
        
        # Sección de firma si se solicitó
        if mostrar_firma and firma_imagen:
            try:
                contenido.append(Paragraph("Firma de Aceptación", estilo_heading))
                contenido.append(Spacer(1, 10))
                
                # Manejamos la imagen en memoria, evitando archivos temporales
                if firma_imagen.startswith('data:image'):
                    # Extraer la parte base64
                    firma_base64 = re.sub(r'^data:image/[^;]+;base64,', '', firma_imagen)
                    
                    # Decodificar a bytes
                    firma_bytes = base64.b64decode(firma_base64)
                    
                    # Crear buffer de memoria para la imagen
                    firma_buffer = BytesIO(firma_bytes)
                    
                    # Crear imagen para ReportLab
                    firma_img = RLImage(firma_buffer, width=200, height=100)
                    
                    # Añadir al contenido
                    contenido.append(firma_img)
                    app.logger.info("Firma añadida al PDF correctamente")
                else:
                    contenido.append(Paragraph("(Formato de firma no válido)", estilo_normal))
                    app.logger.warning("Formato de firma no válido para incluir en PDF")
            except Exception as e:
                app.logger.error(f"Error al procesar firma para PDF: {str(e)}")
                contenido.append(Paragraph("(Error al cargar firma)", estilo_normal))
                import traceback
                app.logger.error(traceback.format_exc())
        
        contenido.append(Spacer(1, 20))
        
        # Pie de página con fecha de generación
        fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        pie = Paragraph(f"Documento generado el {fecha_generacion}", estilo_normal)
        contenido.append(pie)
        
        # Construir el PDF
        doc.build(contenido)
        
        # Obtener los datos del buffer
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Crear respuesta
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=asignacion_{id_asignacion}.pdf'
        
        app.logger.info(f"PDF generado correctamente para asignación {id_asignacion}")
        return response
        
    except Exception as e:
        app.logger.error(f"Error al generar PDF: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Error al generar el PDF: {str(e)}'
        }), 500

@app.route('/logistica/asignacion/<int:id_asignacion>/firmar', methods=['POST'])
@login_required()
@role_required('logistica')
def firmar_asignacion(id_asignacion):
    try:
        # Verificar que el usuario tiene derechos para firmar
        usuario_id = session.get('user_id')
        app.logger.info(f"Intento de firma para asignación {id_asignacion} por usuario {usuario_id}")
        
        # Obtener la conexión a la base de datos
        connection = get_db_connection()
        if not connection:
            app.logger.error("Error al conectar con la base de datos al intentar firmar")
            return jsonify({
                'status': 'error',
                'message': 'Error al conectar con la base de datos'
            }), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener información de la asignación para verificar permisos
        query = """
            SELECT a.*, r.nombre, r.recurso_operativo_cedula
            FROM asignacion a
            JOIN recurso_operativo r ON a.id_codigo_consumidor = r.id_codigo_consumidor
            WHERE a.id_asignacion = %s
        """
        cursor.execute(query, (id_asignacion,))
        asignacion = cursor.fetchone()
        
        if not asignacion:
            cursor.close()
            connection.close()
            app.logger.warning(f"Intento de firma para asignación inexistente: {id_asignacion}")
            return jsonify({
                'status': 'error',
                'message': 'Asignación no encontrada'
            }), 404
        
        # Obtener los datos de la firma manuscrita
        data = request.json
        if not data or 'signature' not in data:
            app.logger.warning("Datos de firma incompletos o inválidos")
            return jsonify({
                'status': 'error',
                'message': 'No se recibieron datos de firma'
            }), 400
        
        # Validar formato de la firma
        firma_imagen = data['signature']
        if not firma_imagen.startswith('data:image/'):
            app.logger.warning("Formato de imagen de firma inválido")
            return jsonify({
                'status': 'error',
                'message': 'Formato de imagen de firma inválido'
            }), 400
        
        # Verificar el tamaño de la firma (para evitar datos demasiado grandes)
        if len(firma_imagen) > 500000:  # Limitar a ~500KB
            app.logger.warning("Imagen de firma demasiado grande")
            return jsonify({
                'status': 'error',
                'message': 'La imagen de firma es demasiado grande'
            }), 400
            
        fecha_firma = datetime.now()
        app.logger.info(f"Firma recibida correctamente para asignación {id_asignacion}")
        
        # Verificar que la firma se puede procesar correctamente
        try:
            # Extraer la parte base64 de la firma
            if 'data:image' in firma_imagen:
                imagen_base64 = re.sub(r'^data:image/[^;]+;base64,', '', firma_imagen)
            
            # Verificar que la decodificación funciona
            imagen_bytes = base64.b64decode(imagen_base64)
            
            # Verificar que la imagen es válida creando un objeto Image con ella
            with PILImage.open(BytesIO(imagen_bytes)) as img:
                formato = img.format
                width, height = img.size
                app.logger.info(f"Imagen de firma validada: formato={formato}, dimensiones={width}x{height}")
        except Exception as e:
            app.logger.error(f"Error al validar la imagen de firma: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Error al procesar la imagen de firma: {str(e)}'
            }), 400
        
        # Primero verificar si existe la tabla para firmas
        try:
            check_table_query = """
                CREATE TABLE IF NOT EXISTS firmas_asignaciones (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_asignacion INT NOT NULL,
                    id_usuario INT NOT NULL,
                    firma_imagen LONGTEXT,
                    fecha_firma DATETIME,
                    FOREIGN KEY (id_asignacion) REFERENCES asignacion(id_asignacion)
                )
            """
            cursor.execute(check_table_query)
            connection.commit()
            app.logger.info("Tabla firmas_asignaciones verificada/creada correctamente")
        except Exception as e:
            app.logger.error(f"Error al verificar tabla de firmas: {str(e)}")
            # Continuar aún si falla la verificación, ya que podría existir
        
        # Guardar la firma en la base de datos
        firma_guardada = False
        try:
            # Verificar si ya existe una firma para esta asignación
            cursor.execute("SELECT id FROM firmas_asignaciones WHERE id_asignacion = %s", (id_asignacion,))
            firma_existente = cursor.fetchone()
            
            if firma_existente:
                # Actualizar firma existente
                update_query = """
                    UPDATE firmas_asignaciones 
                    SET firma_imagen = %s, fecha_firma = %s, id_usuario = %s
                    WHERE id_asignacion = %s
                """
                cursor.execute(update_query, (firma_imagen, fecha_firma, usuario_id, id_asignacion))
                app.logger.info(f"Firma actualizada para asignación {id_asignacion}")
            else:
                # Insertar nueva firma
                insert_query = """
                    INSERT INTO firmas_asignaciones 
                    (id_asignacion, id_usuario, firma_imagen, fecha_firma) 
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_query, (id_asignacion, usuario_id, firma_imagen, fecha_firma))
                app.logger.info(f"Nueva firma guardada para asignación {id_asignacion}")
            
            connection.commit()
            firma_guardada = True
        except Exception as e:
            app.logger.error(f"Error al guardar firma en base de datos: {str(e)}")
            connection.rollback()
            # Si falla, seguimos para intentar generar el PDF igualmente
            import traceback
            app.logger.error(traceback.format_exc())
            
        # Generar un token JWT como respaldo o para verificación alternativa
        payload = {
            'asignacion_id': id_asignacion,
            'usuario_id': usuario_id,
            'fecha': fecha_firma.strftime('%Y-%m-%d %H:%M:%S'),
            'firma_guardada': firma_guardada,
            'iat': fecha_firma.timestamp(),
            'exp': (fecha_firma + timedelta(days=365)).timestamp()
        }
        
        # En un entorno real, este secreto estaría almacenado de manera segura
        clave_secreta = os.getenv('JWT_SECRET_KEY', 'clave_secreta_para_firmas')
        token = jwt.encode(payload, clave_secreta, algorithm='HS256')
        
        # Cerrar cursor y conexión
        cursor.close()
        connection.close()
        
        # Devolver URL al PDF firmado
        url_pdf_firmado = url_for('generar_pdf_asignacion', id_asignacion=id_asignacion, firmado='true', _external=True)
        
        app.logger.info(f"Proceso de firma completado exitosamente para asignación {id_asignacion}")
        return jsonify({
            'status': 'success',
            'message': 'Documento firmado correctamente',
            'token': token,
            'url_pdf': url_pdf_firmado,
            'firma_guardada': firma_guardada
        })
        
    except Exception as e:
        app.logger.error(f"Error inesperado al firmar documento: {str(e)}")
        
        # Log detallado para diagnóstico
        import traceback
        app.logger.error(traceback.format_exc())
        
        return jsonify({
            'status': 'error',
            'message': f'Error al firmar el documento: {str(e)}'
        }), 500

@app.route('/api/inventario/filtrar', methods=['POST'])
@login_required()
@role_required('logistica')
def filtrar_inventario():
    try:
        # Obtener parámetros del filtro
        filtros = request.json
        categoria = filtros.get('categoria', 'todos')
        ubicacion = filtros.get('ubicacion', 'todos')
        fecha_inicio = filtros.get('fecha_inicio')
        fecha_fin = filtros.get('fecha_fin')
        estado = filtros.get('estado', 'todos')
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Construir consultas según filtros
        params = []
        where_clauses = []
        
        # Base de la consulta para movimientos
        movimientos_query = """
            SELECT 
                DATE(fecha_movimiento) as fecha,
                tipo_movimiento,
                item_afectado,
                cantidad,
                usuario,
                ubicacion
            FROM movimientos_inventario
            WHERE 1=1
        """
        
        # Aplicar filtros de fecha
        if fecha_inicio:
            where_clauses.append("fecha_movimiento >= %s")
            params.append(fecha_inicio)
        
        if fecha_fin:
            where_clauses.append("fecha_movimiento <= %s")
            params.append(fecha_fin)
        
        # Aplicar filtro de categoría
        if categoria != 'todos':
            # Mapeo de categorías a items
            categoria_items = {
                'herramientas_basicas': ['Adaptador Mandril', 'Alicate', 'Barra 45cm', 'Bisturí Metálico', 
                                         'Caja de Herramientas', 'Cortafrío', 'Destornillador Estrella', 
                                         'Destornillador Pala', 'Destornillador Tester', 'Martillo', 'Pinza de Punta'],
                'herramientas_especializadas': ['Multímetro', 'Taladro Percutor', 'Ponchadora RG6/RG11', 
                                               'Ponchadora RJ45/RJ11', 'Power Meter', 'BFL Laser', 
                                               'Cortadora', 'Stripper Fibra'],
               'material_ferretero': ['Silicona', 'Amarres Negros', 'Amarres Blancos', 
                                      'Cinta Aislante', 'Grapas Blancas', 'Grapas Negras']
            }
            
            if categoria in categoria_items:
                item_placeholders = ', '.join(['%s'] * len(categoria_items[categoria]))
                where_clauses.append(f"item_afectado IN ({item_placeholders})")
                params.extend(categoria_items[categoria])
        
        # Aplicar filtro de ubicación
        if ubicacion != 'todos':
            where_clauses.append("ubicacion = %s")
            params.append(ubicacion)
        
        # Construir consulta final
        if where_clauses:
            movimientos_query += " AND " + " AND ".join(where_clauses)
        
        movimientos_query += " ORDER BY fecha_movimiento DESC LIMIT 100"
        
        # Ejecutar consulta
        cursor.execute(movimientos_query, params)
        movimientos = cursor.fetchall()
        
        # Procesar datos para el gráfico de tendencia
        ultimos_30_dias = []
        hoy = datetime.now().date()
        for i in range(30, -1, -1):
            fecha = hoy - timedelta(days=i)
            ultimos_30_dias.append(fecha.strftime('%Y-%m-%d'))
        
        movimientos_por_dia = {}
        for fecha in ultimos_30_dias:
            movimientos_por_dia[fecha] = 0
            
        for movimiento in movimientos:
            fecha_str = movimiento['fecha'].strftime('%Y-%m-%d')
            if fecha_str in movimientos_por_dia:
                movimientos_por_dia[fecha_str] += 1
        
        # Preparar datos del gráfico de tendencia
        datos_tendencia = {
            'labels': ultimos_30_dias,
            'datos': [movimientos_por_dia.get(fecha, 0) for fecha in ultimos_30_dias]
        }
        
        # Simular estadísticas según los filtros
        # En una implementación real, estos datos se obtendrían de la base de datos
        estadisticas = {
            'total_items': len(movimientos),
            'entradas': sum(1 for m in movimientos if m['tipo_movimiento'] == 'entrada'),
            'salidas': sum(1 for m in movimientos if m['tipo_movimiento'] == 'salida'),
            'transferencias': sum(1 for m in movimientos if m['tipo_movimiento'] == 'transferencia'),
            'ajustes': sum(1 for m in movimientos if m['tipo_movimiento'] == 'ajuste')
        }
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'movimientos': movimientos,
            'tendencia': datos_tendencia,
            'estadisticas': estadisticas
        })
        
    except Exception as e:
        print(f"Error al filtrar inventario: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventario/exportar-csv', methods=['POST'])
@login_required()
@role_required('logistica')
def exportar_inventario_csv():
    try:
        # Obtener parámetros del filtro (similar a filtrar_inventario)
        filtros = request.json
        
        # Obtener datos según filtros...
        # (Código similar a filtrar_inventario para obtener los datos)
        
        # Para este ejemplo, usaremos datos simulados
        datos = []
        
        # Herramientas básicas
        for item in ['Adaptador Mandril', 'Alicate', 'Barra 45cm', 'Bisturí Metálico', 
                    'Caja de Herramientas', 'Cortafrío', 'Destornillador Estrella']:
            datos.append({
                'categoria': 'Herramientas Básicas',
                'item': item,
                'cantidad': 15,
                'ubicacion': 'Almacén Principal',
                'estado': 'Disponible'
            })
        
        # Herramientas especializadas
        for item in ['Multímetro', 'Taladro Percutor', 'Ponchadora RG6/RG11']:
            datos.append({
                'categoria': 'Herramientas Especializadas',
                'item': item,
                'cantidad': 8,
                'ubicacion': 'Bodega Norte',
                'estado': 'Disponible'
            })
        
        # Material ferretero
        for item in ['Silicona', 'Amarres Negros', 'Amarres Blancos']:
            datos.append({
                'categoria': 'Material Ferretero',
                'item': item,
                'cantidad': 50,
                'ubicacion': 'Bodega Sur',
                'estado': 'Disponible'
            })
        
        # Crear DataFrame y exportar a CSV
        df = pd.DataFrame(datos)
        csv_data = df.to_csv(index=False, sep=';')
        
        # Crear un objeto de archivo en memoria
        output = io.StringIO()
        output.write(csv_data)
        output.seek(0)
        
        # Devolver el archivo CSV
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=inventario.csv"}
        )
        
    except Exception as e:
        print(f"Error al exportar inventario a CSV: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/suministros', methods=['GET', 'POST'])
def suministros():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            flash('Error de conexión a la base de datos.', 'error')
            return redirect(url_for('dashboard'))
        
        cursor = connection.cursor(dictionary=True)
        
        # Obtener todos los suministros
        cursor.execute("SELECT * FROM suministros")
        suministros_data = cursor.fetchall()
        
        return render_template('modulos/administrativo/suministros.html', suministros=suministros_data)
    
    except mysql.connector.Error as e:
        flash(f'Error de base de datos: {str(e)}', 'error')
        return redirect(url_for('dashboard'))
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/guardar_suministro', methods=['POST'])
@login_required()
def guardar_suministro():
    connection = None
    cursor = None
    try:
        # Obtener datos del formulario
        suministros_codigo = request.form.get('suministros_codigo')
        suministros_descripcion = request.form.get('suministros_descripcion')
        suministros_unidad_medida = request.form.get('suministros_unidad_medida')
        suministros_familia = request.form.get('suministros_familia')
        suministros_cliente = request.form.get('suministros_cliente')
        suministros_tipo = request.form.get('suministros_tipo')
        suministros_estado = request.form.get('suministros_estado', 'Activo')
        suministros_requiere_serial = request.form.get('suministros_requiere_serial', 'no')
        suministros_serial = request.form.get('suministros_serial', '')
        suministros_costo_unitario = request.form.get('suministros_costo_unitario')
        suministros_cantidad = request.form.get('suministros_cantidad')
        fecha_registro = request.form.get('fecha_registro')
        id_codigo_consumidor = request.form.get('id_codigo_consumidor', session.get('user_id'))
        
        # Validar datos requeridos
        if not all([suministros_codigo, suministros_descripcion, suministros_unidad_medida, 
                    suministros_familia, suministros_costo_unitario, suministros_cantidad]):
            flash('Por favor complete todos los campos requeridos.', 'error')
            return redirect(url_for('suministros'))
        
        # Conectar a la base de datos
        connection = get_db_connection()
        if connection is None:
            flash('Error de conexión a la base de datos.', 'error')
            return redirect(url_for('suministros'))
        
        cursor = connection.cursor()
        
        # Insertar nuevo suministro
        query = """
        INSERT INTO suministros (
            suministros_codigo, suministros_descripcion, suministros_unidad_medida,
            suministros_familia, suministros_cliente, suministros_tipo, suministros_estado,
            suministros_requiere_serial, suministros_serial, suministros_costo_unitario,
            suministros_cantidad, fecha_registro, id_codigo_consumidor
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            suministros_codigo, suministros_descripcion, suministros_unidad_medida,
            suministros_familia, suministros_cliente, suministros_tipo, suministros_estado,
            suministros_requiere_serial, suministros_serial, suministros_costo_unitario,
            suministros_cantidad, fecha_registro, id_codigo_consumidor
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        flash('Suministro guardado exitosamente.', 'success')
        return redirect(url_for('suministros'))
        
    except mysql.connector.Error as e:
        flash(f'Error al guardar suministro: {str(e)}', 'error')
        return redirect(url_for('suministros'))
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/obtener_suministro/<int:id>', methods=['GET'])
@login_required()
def obtener_suministro(id):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Obtener suministro por ID
        cursor.execute("SELECT * FROM suministros WHERE id_suministros = %s", (id,))
        suministro = cursor.fetchone()
        
        if not suministro:
            return jsonify({'error': 'Suministro no encontrado'}), 404
        
        return jsonify(suministro)
        
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/actualizar_suministro', methods=['POST'])
@login_required()
def actualizar_suministro():
    connection = None
    cursor = None
    try:
        # Obtener datos del formulario
        id_suministros = request.form.get('id_suministros')
        suministros_codigo = request.form.get('suministros_codigo')
        suministros_descripcion = request.form.get('suministros_descripcion')
        suministros_unidad_medida = request.form.get('suministros_unidad_medida')
        suministros_familia = request.form.get('suministros_familia')
        suministros_cliente = request.form.get('suministros_cliente')
        suministros_tipo = request.form.get('suministros_tipo')
        suministros_estado = request.form.get('suministros_estado', 'Activo')
        suministros_requiere_serial = request.form.get('suministros_requiere_serial', 'no')
        suministros_serial = request.form.get('suministros_serial', '')
        suministros_costo_unitario = request.form.get('suministros_costo_unitario')
        suministros_cantidad = request.form.get('suministros_cantidad')
        
        # Validar datos requeridos
        if not all([id_suministros, suministros_codigo, suministros_descripcion, suministros_unidad_medida, 
                    suministros_familia, suministros_costo_unitario, suministros_cantidad]):
            flash('Por favor complete todos los campos requeridos.', 'error')
            return redirect(url_for('suministros'))
        
        # Conectar a la base de datos
        connection = get_db_connection()
        if connection is None:
            flash('Error de conexión a la base de datos.', 'error')
            return redirect(url_for('suministros'))
        
        cursor = connection.cursor()
        
        # Actualizar suministro
        query = """
        UPDATE suministros SET 
            suministros_codigo = %s, 
            suministros_descripcion = %s, 
            suministros_unidad_medida = %s,
            suministros_familia = %s, 
            suministros_cliente = %s, 
            suministros_tipo = %s, 
            suministros_estado = %s,
            suministros_requiere_serial = %s, 
            suministros_serial = %s, 
            suministros_costo_unitario = %s,
            suministros_cantidad = %s
        WHERE id_suministros = %s
        """
        values = (
            suministros_codigo, suministros_descripcion, suministros_unidad_medida,
            suministros_familia, suministros_cliente, suministros_tipo, suministros_estado,
            suministros_requiere_serial, suministros_serial, suministros_costo_unitario,
            suministros_cantidad, id_suministros
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        flash('Suministro actualizado exitosamente.', 'success')
        return redirect(url_for('suministros'))
        
    except mysql.connector.Error as e:
        flash(f'Error al actualizar suministro: {str(e)}', 'error')
        return redirect(url_for('suministros'))
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/eliminar_suministro/<int:id>', methods=['POST'])
@login_required()
def eliminar_suministro(id):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        cursor = connection.cursor()
        
        # Eliminar suministro
        cursor.execute("DELETE FROM suministros WHERE id_suministros = %s", (id,))
        connection.commit()
        
        return jsonify({'success': True, 'message': 'Suministro eliminado correctamente'})
        
    except mysql.connector.Error as e:
        return jsonify({'success': False, 'message': f'Error al eliminar suministro: {str(e)}'}), 500
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/admin/usuarios', methods=['GET'])
@login_required(role='administrativo')
def usuarios():
    connection = None
    cursor = None
    try:
        page = request.args.get('page', 1, type=int)
        items_per_page = 10  # Número de usuarios por página
        offset = (page - 1) * items_per_page
        
        connection = get_db_connection()
        if connection is None:
            flash('Error de conexión a la base de datos.', 'error')
            return redirect(url_for('dashboard'))
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener total de usuarios para calcular el número de páginas
        cursor.execute("SELECT COUNT(*) as total FROM recurso_operativo")
        total_users = cursor.fetchone()['total']
        total_pages = (total_users + items_per_page - 1) // items_per_page  # Redondeo hacia arriba
        
        # Obtener usuarios con paginación
        query = """
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula,
                nombre,
                id_roles,
                estado
            FROM recurso_operativo
            ORDER BY id_codigo_consumidor
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (items_per_page, offset))
        usuarios = cursor.fetchall()
        
        # Convertir id_roles a nombres legibles
        for usuario in usuarios:
            usuario['role'] = ROLES.get(str(usuario['id_roles']), 'Desconocido')
        
        return render_template('modulos/administrativo/usuarios.html', 
                              usuarios=usuarios, 
                              current_page=page, 
                              total_pages=total_pages,
                              ROLES=ROLES)  # Pasar el diccionario ROLES al contexto
        
    except mysql.connector.Error as e:
        flash(f'Error de base de datos: {str(e)}', 'error')
        return redirect(url_for('dashboard'))
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/obtener_usuario/<int:id>', methods=['GET'])
@login_required(role='administrativo')
def obtener_usuario(id):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Obtener usuario por ID
        cursor.execute("""
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula,
                nombre,
                id_roles,
                estado
            FROM recurso_operativo 
            WHERE id_codigo_consumidor = %s
        """, (id,))
        
        usuario = cursor.fetchone()
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify(usuario)
        
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/actualizar_usuario', methods=['POST'])
@login_required(role='administrativo')
def actualizar_usuario():
    connection = None
    cursor = None
    try:
        # Obtener datos del formulario
        id_codigo_consumidor = request.form.get('id_codigo_consumidor')
        recurso_operativo_cedula = request.form.get('recurso_operativo_cedula')
        nombre = request.form.get('nombre')
        id_roles = request.form.get('id_roles')
        estado = request.form.get('estado', 'Activo')
        
        # Validar datos requeridos
        if not all([id_codigo_consumidor, recurso_operativo_cedula, nombre, id_roles]):
            flash('Por favor complete todos los campos requeridos.', 'error')
            return redirect(url_for('usuarios'))
        
        # Conectar a la base de datos
        connection = get_db_connection()
        if connection is None:
            flash('Error de conexión a la base de datos.', 'error')
            return redirect(url_for('usuarios'))
        
        cursor = connection.cursor()
        
        # Actualizar usuario
        query = """
        UPDATE recurso_operativo SET 
            recurso_operativo_cedula = %s, 
            nombre = %s, 
            id_roles = %s,
            estado = %s
        WHERE id_codigo_consumidor = %s
        """
        values = (
            recurso_operativo_cedula, 
            nombre, 
            id_roles,
            estado,
            id_codigo_consumidor
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        flash('Usuario actualizado exitosamente.', 'success')
        return redirect(url_for('usuarios'))
        
    except mysql.connector.Error as e:
        flash(f'Error al actualizar usuario: {str(e)}', 'error')
        return redirect(url_for('usuarios'))
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/eliminar_usuario/<int:id>', methods=['POST'])
@login_required(role='administrativo')
def eliminar_usuario(id):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'})
            
        cursor = connection.cursor()
        
        # Verificar si el usuario existe
        cursor.execute("SELECT id_codigo_consumidor FROM recurso_operativo WHERE id_codigo_consumidor = %s", (id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Usuario no encontrado'})
        
        # Eliminar el usuario
        cursor.execute("DELETE FROM recurso_operativo WHERE id_codigo_consumidor = %s", (id,))
        connection.commit()
        
        return jsonify({'success': True, 'message': 'Usuario eliminado correctamente'})
        
    except mysql.connector.Error as e:
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': f'Error al eliminar usuario: {str(e)}'})
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/estadisticas_inventario')
@login_required(role='administrativo')
def estadisticas_inventario():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            flash('Error de conexión a la base de datos', 'danger')
            return redirect(url_for('dashboard'))
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener usuarios para el filtro
        cursor.execute("""
            SELECT id_codigo_consumidor, nombre
            FROM recurso_operativo
            WHERE estado = 'Activo'
            ORDER BY nombre
        """)
        usuarios = cursor.fetchall()
        
        # Obtener datos iniciales para los contadores usando las tablas existentes
        # Usaremos asignacion para herramientas y ferretero para materiales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_elementos,
                SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as elementos_asignados,
                SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as elementos_disponibles,
                0 as elementos_mantenimiento
            FROM asignacion
        """)
        contadores_asignacion = cursor.fetchone()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_elementos
            FROM ferretero
        """)
        contadores_ferretero = cursor.fetchone()
        
        # Combinar contadores
        contadores = {
            'total_elementos': (contadores_asignacion['total_elementos'] or 0) + (contadores_ferretero['total_elementos'] or 0),
            'elementos_asignados': contadores_asignacion['elementos_asignados'] or 0,
            'elementos_disponibles': contadores_asignacion['elementos_disponibles'] or 0,
            'elementos_mantenimiento': 0  # No hay datos de mantenimiento en las tablas actuales
        }
        
        # Obtener top 10 de herramientas (usando asignacion para herramientas básicas)
        cursor.execute("""
            SELECT 
                'Adaptador Mandril' as descripcion,
                'HD-001' as codigo,
                COUNT(*) as cantidad_total,
                SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as asignados,
                SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as disponibles,
                ROUND((SUM(asignacion_adaptador_mandril) / COUNT(*)) * 100) as frecuencia_uso
            FROM asignacion 
            WHERE asignacion_adaptador_mandril > 0
            UNION ALL
            SELECT 
                'Alicate' as descripcion,
                'HD-002' as codigo,
                COUNT(*) as cantidad_total,
                SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as asignados,
                SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as disponibles,
                ROUND((SUM(asignacion_alicate) / COUNT(*)) * 100) as frecuencia_uso
            FROM asignacion 
            WHERE asignacion_alicate > 0
            UNION ALL
            SELECT 
                'Barra 45cm' as descripcion,
                'HD-003' as codigo,
                COUNT(*) as cantidad_total,
                SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as asignados,
                SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as disponibles,
                ROUND((SUM(asignacion_barra_45cm) / COUNT(*)) * 100) as frecuencia_uso
            FROM asignacion 
            WHERE asignacion_barra_45cm > 0
            ORDER BY frecuencia_uso DESC
            LIMIT 10
        """)
        top_herramientas = cursor.fetchall()
        
        # Obtener top 10 de herramientas especializadas
        cursor.execute("""
            SELECT 
                'Multímetro' as descripcion,
                'HE-001' as codigo,
                COUNT(*) as cantidad_total,
                SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as asignados,
                SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as disponibles,
                ROUND((SUM(asignacion_multimetro) / COUNT(*)) * 100) as frecuencia_uso
            FROM asignacion 
            WHERE asignacion_multimetro > 0
            UNION ALL
            SELECT 
                'Taladro Percutor' as descripcion,
                'HE-002' as codigo,
                COUNT(*) as cantidad_total,
                SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as asignados,
                SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as disponibles,
                ROUND((SUM(asignacion_taladro_percutor) / COUNT(*)) * 100) as frecuencia_uso
            FROM asignacion 
            WHERE asignacion_taladro_percutor > 0
            ORDER BY frecuencia_uso DESC
            LIMIT 10
        """)
        top_dotaciones = cursor.fetchall()
        
        # Obtener top 10 de EPPs (Elementos de Protección Personal)
        cursor.execute("""
            SELECT 
                'Arnés' as descripcion,
                'EPP-001' as codigo,
                COUNT(*) as cantidad_total,
                SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as asignados,
                SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as disponibles,
                ROUND((SUM(asignacion_arnes) / COUNT(*)) * 100) as frecuencia_uso
            FROM asignacion 
            WHERE asignacion_arnes > 0
            UNION ALL
            SELECT 
                'Eslinga' as descripcion,
                'EPP-002' as codigo,
                COUNT(*) as cantidad_total,
                SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as asignados,
                SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as disponibles,
                ROUND((SUM(asignacion_eslinga) / COUNT(*)) * 100) as frecuencia_uso
            FROM asignacion 
            WHERE asignacion_eslinga > 0
            ORDER BY frecuencia_uso DESC
            LIMIT 10
        """)
        top_epps = cursor.fetchall()
        
        # Obtener top 10 de ferretero
        cursor.execute("""
            SELECT 
                'Silicona' as descripcion,
                'F-001' as codigo,
                COUNT(*) as cantidad_total,
                SUM(silicona) as asignados,
                0 as disponibles,
                ROUND((SUM(silicona) / COUNT(*)) * 100) as frecuencia_uso
            FROM ferretero 
            WHERE silicona > 0
            UNION ALL
            SELECT 
                'Amarres Negros' as descripcion,
                'F-002' as codigo,
                COUNT(*) as cantidad_total,
                SUM(amarres_negros) as asignados,
                0 as disponibles,
                ROUND((SUM(amarres_negros) / COUNT(*)) * 100) as frecuencia_uso
            FROM ferretero 
            WHERE amarres_negros > 0
            UNION ALL
            SELECT 
                'Amarres Blancos' as descripcion,
                'F-003' as codigo,
                COUNT(*) as cantidad_total,
                SUM(amarres_blancos) as asignados,
                0 as disponibles,
                ROUND((SUM(amarres_blancos) / COUNT(*)) * 100) as frecuencia_uso
            FROM ferretero 
            WHERE amarres_blancos > 0
            UNION ALL
            SELECT 
                'Cinta Aislante' as descripcion,
                'F-004' as codigo,
                COUNT(*) as cantidad_total,
                SUM(cinta_aislante) as asignados,
                0 as disponibles,
                ROUND((SUM(cinta_aislante) / COUNT(*)) * 100) as frecuencia_uso
            FROM ferretero 
            WHERE cinta_aislante > 0
            ORDER BY frecuencia_uso DESC
            LIMIT 10
        """)
        top_ferretero = cursor.fetchall()
        
        # Obtener datos para el gráfico de distribución por categorías
        cursor.execute("""
            SELECT 
                SUM(CASE 
                    WHEN asignacion_adaptador_mandril > 0 OR 
                         asignacion_alicate > 0 OR 
                         asignacion_barra_45cm > 0 OR 
                         asignacion_bisturi_metalico > 0 OR 
                         asignacion_caja_de_herramientas > 0 OR 
                         asignacion_cortafrio > 0 OR 
                         asignacion_destor_de_estrella > 0 OR 
                         asignacion_destor_de_pala > 0 OR 
                         asignacion_destor_tester > 0 OR 
                         asignacion_martillo_de_una > 0 OR 
                         asignacion_pinza_de_punta > 0 
                    THEN 1 ELSE 0 END) as herramientas,
                SUM(CASE 
                    WHEN asignacion_multimetro > 0 OR 
                         asignacion_taladro_percutor > 0 OR 
                         asignacion_ponchadora_rg_6_y_rg_11 > 0 OR 
                         asignacion_ponchadora_rj_45_y_rj11 > 0 OR 
                         asignacion_power_miter > 0 OR 
                         asignacion_bfl_laser > 0 OR 
                         asignacion_cortadora > 0 OR 
                         asignacion_stripper_fibra > 0 
                    THEN 1 ELSE 0 END) as dotaciones,
                SUM(CASE 
                    WHEN asignacion_arnes > 0 OR 
                         asignacion_eslinga > 0 OR 
                         asignacion_casco_tipo_ii > 0 OR 
                         asignacion_arana_casco > 0 OR 
                         asignacion_barbuquejo > 0 OR 
                         asignacion_guantes_vaqueta > 0 OR 
                         asignacion_gafas > 0 OR 
                         asignacion_linea_vida > 0 
                    THEN 1 ELSE 0 END) as epps
            FROM asignacion
        """)
        categorias_asignacion = cursor.fetchone()
        
        cursor.execute("""
            SELECT COUNT(*) as ferretero
            FROM ferretero
        """)
        categorias_ferretero = cursor.fetchone()
        
        # Formatear datos para gráficos
        categorias = {
            'herramientas': categorias_asignacion['herramientas'] or 0,
            'dotaciones': categorias_asignacion['dotaciones'] or 0,
            'epps': categorias_asignacion['epps'] or 0,
            'ferretero': categorias_ferretero['ferretero'] or 0
        }
        
        datos_categorias = json.dumps([
            categorias['herramientas'], 
            categorias['dotaciones'], 
            categorias['epps'], 
            categorias['ferretero']
        ])
        
        # Obtener datos para el gráfico de distribución por estado
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as asignados,
                SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as disponibles,
                0 as en_mantenimiento,
                0 as de_baja
            FROM asignacion
        """)
        estados = cursor.fetchone()
        
        datos_estados = json.dumps([
            estados['disponibles'] or 0, 
            estados['asignados'] or 0, 
            estados['en_mantenimiento'] or 0, 
            estados['de_baja'] or 0
        ])
        
        # Obtener datos para el gráfico de elementos más asignados
        cursor.execute("""
            SELECT 
                'Adaptador Mandril' as descripcion,
                SUM(asignacion_adaptador_mandril) as total_asignaciones
            FROM asignacion 
            WHERE asignacion_adaptador_mandril > 0
            UNION ALL
            SELECT 
                'Alicate' as descripcion,
                SUM(asignacion_alicate) as total_asignaciones
            FROM asignacion 
            WHERE asignacion_alicate > 0
            UNION ALL
            SELECT 
                'Barra 45cm' as descripcion,
                SUM(asignacion_barra_45cm) as total_asignaciones
            FROM asignacion 
            WHERE asignacion_barra_45cm > 0
            UNION ALL
            SELECT 
                'Silicona' as descripcion,
                SUM(silicona) as total_asignaciones
            FROM ferretero 
            WHERE silicona > 0
            UNION ALL
            SELECT 
                'Amarres Negros' as descripcion,
                SUM(amarres_negros) as total_asignaciones
            FROM ferretero 
            WHERE amarres_negros > 0
            UNION ALL
            SELECT 
                'Cinta Aislante' as descripcion,
                SUM(cinta_aislante) as total_asignaciones
            FROM ferretero 
            WHERE cinta_aislante > 0
            ORDER BY total_asignaciones DESC
            LIMIT 6
        """)
        mas_asignados = cursor.fetchall()
        
        
        if mas_asignados:
            labels_mas_asignados = json.dumps([item['descripcion'] for item in mas_asignados])
            datos_mas_asignados = json.dumps([item['total_asignaciones'] for item in mas_asignados])
        else:
            labels_mas_asignados = json.dumps(["Taladro", "Guantes", "Martillo", "Pulidora", "Destornillador", "Llaves"])
            datos_mas_asignados = json.dumps([120, 98, 85, 74, 65, 60])
        
        # Obtener datos para el gráfico de tendencia de asignaciones
        cursor.execute("""
            SELECT 
                DATE_FORMAT(asignacion_fecha, '%b') as mes,
                MIN(asignacion_fecha) as fecha_referencia,
                COUNT(*) as total
            FROM asignacion
            WHERE asignacion_fecha >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(asignacion_fecha, '%Y-%m')
            ORDER BY MIN(asignacion_fecha)
        """)
        tendencia_asignacion = cursor.fetchall()
        
        cursor.execute("""
            SELECT 
                DATE_FORMAT(fecha_asignacion, '%b') as mes,
                MIN(fecha_asignacion) as fecha_referencia,
                COUNT(*) as total
            FROM ferretero
            WHERE fecha_asignacion >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(fecha_asignacion, '%Y-%m')
            ORDER BY MIN(fecha_asignacion)
        """)
        tendencia_ferretero = cursor.fetchall()
        
        # Combinar tendencias
        tendencia_meses = {}
        
        # Agregar datos de asignación
        for item in tendencia_asignacion:
            mes = item['mes']
            if mes not in tendencia_meses:
                tendencia_meses[mes] = 0
            tendencia_meses[mes] += item['total']
        
        # Agregar datos de ferretero
        for item in tendencia_ferretero:
            mes = item['mes']
            if mes not in tendencia_meses:
                tendencia_meses[mes] = 0
            tendencia_meses[mes] += item['total']
        
        # Convertir a lista ordenada por mes
        tendencia = [{'mes': k, 'total': v} for k, v in tendencia_meses.items()]
        tendencia.sort(key=lambda x: {'Ene': 1, 'Feb': 2, 'Mar': 3, 'Abr': 4, 'May': 5, 'Jun': 6, 
                                  'Jul': 7, 'Ago': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dic': 12}.get(x['mes'], 0))
        
        if tendencia:
            labels_tendencia = json.dumps([item['mes'] for item in tendencia])
            datos_tendencia = json.dumps([item['total'] for item in tendencia])
        else:
            labels_tendencia = json.dumps(["Ene", "Feb", "Mar", "Abr", "May", "Jun"])
            datos_tendencia = json.dumps([65, 72, 78, 90, 85, 95])
        
        return render_template('modulos/administrativo/estadisticas_inventario.html',
                               usuarios=usuarios,
                               total_elementos=contadores['total_elementos'],
                               elementos_disponibles=contadores['elementos_disponibles'],
                               elementos_asignados=contadores['elementos_asignados'],
                               elementos_mantenimiento=contadores['elementos_mantenimiento'],
                               top_herramientas=top_herramientas,
                               top_dotaciones=top_dotaciones,
                               top_epps=top_epps,
                               top_ferretero=top_ferretero,
                               datos_categorias=datos_categorias,
                               datos_estados=datos_estados,
                               labels_mas_asignados=labels_mas_asignados,
                               datos_mas_asignados=datos_mas_asignados,
                               labels_tendencia=labels_tendencia,
                               datos_tendencia=datos_tendencia)
        
    except mysql.connector.Error as e:
        flash(f'Error al cargar datos: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/api/estadisticas/inventario', methods=['GET'])
@login_required(role='administrativo')
def api_estadisticas_inventario():
    from decimal import Decimal
    
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({
                'success': False,
                'message': 'Error de conexión a la base de datos'
            })
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener parámetros de filtro
        dias = request.args.get('dias', default='30', type=str)
        categoria = request.args.get('categoria', default='todos', type=str)
        estado = request.args.get('estado', default='todos', type=str)
        usuario = request.args.get('usuario', default='todos', type=str)
        
        # Construir condiciones de filtro
        condicion_fecha = "1=1"
        if dias != 'todos':
            condicion_fecha = f"asignacion_fecha >= DATE_SUB(NOW(), INTERVAL {dias} DAY)"
            
        condicion_categoria = "1=1"
        if categoria != 'todos':
            if categoria == 'herramientas':
                condicion_categoria = """(
                    asignacion_adaptador_mandril > 0 OR 
                    asignacion_alicate > 0 OR 
                    asignacion_barra_45cm > 0 OR 
                    asignacion_bisturi_metalico > 0 OR 
                    asignacion_caja_de_herramientas > 0 OR 
                    asignacion_cortafrio > 0 OR 
                    asignacion_destor_de_estrella > 0 OR 
                    asignacion_destor_de_pala > 0 OR 
                    asignacion_destor_tester > 0 OR 
                    asignacion_martillo_de_una > 0 OR 
                    asignacion_pinza_de_punta > 0
                )"""
            elif categoria == 'dotaciones':
                condicion_categoria = """(
                    asignacion_multimetro > 0 OR 
                    asignacion_taladro_percutor > 0 OR 
                    asignacion_ponchadora_rg_6_y_rg_11 > 0 OR 
                    asignacion_ponchadora_rj_45_y_rj11 > 0 OR 
                    asignacion_power_miter > 0 OR 
                    asignacion_bfl_laser > 0 OR 
                    asignacion_cortadora > 0 OR 
                    asignacion_stripper_fibra > 0
                )"""
            elif categoria == 'epps':
                condicion_categoria = """(
                    asignacion_arnes > 0 OR 
                    asignacion_eslinga > 0 OR 
                    asignacion_casco_tipo_ii > 0 OR 
                    asignacion_arana_casco > 0 OR 
                    asignacion_barbuquejo > 0 OR 
                    asignacion_guantes_vaqueta > 0 OR 
                    asignacion_gafas > 0 OR 
                    asignacion_linea_vida > 0
                )"""
            
        condicion_estado = "1=1"
        if estado != 'todos':
            condicion_estado = f"asignacion_estado = '{estado}'"
            
        condicion_usuario = "1=1"
        if usuario != 'todos':
            condicion_usuario = f"recurso_id = '{usuario}'"
        
        # Obtener datos para los contadores 
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_elementos,
                SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as elementos_asignados,
                SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as elementos_disponibles,
                0 as elementos_mantenimiento
            FROM asignacion
            WHERE {condicion_fecha} AND {condicion_categoria} AND {condicion_estado} AND {condicion_usuario}
        """)
        contadores_asignacion = cursor.fetchone()
        
        # Si la categoría no es ferretero, incluir contadores de ferretero
        contadores_ferretero = {'total_elementos': 0}
        if categoria == 'todos' or categoria == 'ferretero':
            condicion_fecha_ferretero = "1=1"
            if dias != 'todos':
                condicion_fecha_ferretero = f"fecha_asignacion >= DATE_SUB(NOW(), INTERVAL {dias} DAY)"
                
            condicion_usuario_ferretero = "1=1"
            if usuario != 'todos':
                condicion_usuario_ferretero = f"id_tecnico = '{usuario}'"
                
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_elementos
                FROM ferretero
                WHERE {condicion_fecha_ferretero} AND {condicion_usuario_ferretero}
            """)
            contadores_ferretero = cursor.fetchone()
        
        # Combinar contadores
        contadores = {
            'total_elementos': (contadores_asignacion['total_elementos'] or 0) + (contadores_ferretero['total_elementos'] or 0),
            'elementos_asignados': contadores_asignacion['elementos_asignados'] or 0,
            'elementos_disponibles': contadores_asignacion['elementos_disponibles'] or 0,
            'elementos_mantenimiento': 0
        }
        
        # Obtener Top 10 según la categoría seleccionada
        resultados = {}
        
        if categoria == 'todos' or categoria == 'herramientas':
            cursor.execute(f"""
                SELECT 
                    'Adaptador Mandril' as descripcion,
                    'HD-001' as codigo,
                    COUNT(*) as cantidad_total,
                    SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as asignados,
                    SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as disponibles,
                    ROUND((SUM(asignacion_adaptador_mandril) / COUNT(*)) * 100) as frecuencia_uso
                FROM asignacion 
                WHERE asignacion_adaptador_mandril > 0 AND {condicion_fecha} AND {condicion_estado} AND {condicion_usuario}
                UNION ALL
                SELECT 
                    'Alicate' as descripcion,
                    'HD-002' as codigo,
                    COUNT(*) as cantidad_total,
                    SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as asignados,
                    SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as disponibles,
                    ROUND((SUM(asignacion_alicate) / COUNT(*)) * 100) as frecuencia_uso
                FROM asignacion 
                WHERE asignacion_alicate > 0 AND {condicion_fecha} AND {condicion_estado} AND {condicion_usuario}
                UNION ALL
                SELECT 
                    'Barra 45cm' as descripcion,
                    'HD-003' as codigo,
                    COUNT(*) as cantidad_total,
                    SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as asignados,
                    SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as disponibles,
                    ROUND((SUM(asignacion_barra_45cm) / COUNT(*)) * 100) as frecuencia_uso
                FROM asignacion 
                WHERE asignacion_barra_45cm > 0 AND {condicion_fecha} AND {condicion_estado} AND {condicion_usuario}
                ORDER BY frecuencia_uso DESC
                LIMIT 10
            """)
            top_herramientas = cursor.fetchall()
            # Formatear los valores para JSON
            for item in top_herramientas:
                for k, v in item.items():
                    if v is None:
                        item[k] = 0
                    elif isinstance(v, Decimal):
                        item[k] = float(v)
            resultados['top_herramientas'] = top_herramientas
        
        if categoria == 'todos' or categoria == 'dotaciones':
            cursor.execute(f"""
                SELECT 
                    'Multímetro' as descripcion,
                    'HE-001' as codigo,
                    COUNT(*) as cantidad_total,
                    SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as asignados,
                    SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as disponibles,
                    ROUND((SUM(asignacion_multimetro) / COUNT(*)) * 100) as frecuencia_uso
                FROM asignacion 
                WHERE asignacion_multimetro > 0 AND {condicion_fecha} AND {condicion_estado} AND {condicion_usuario}
                UNION ALL
                SELECT 
                    'Taladro Percutor' as descripcion,
                    'HE-002' as codigo,
                    COUNT(*) as cantidad_total,
                    SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as asignados,
                    SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as disponibles,
                    ROUND((SUM(asignacion_taladro_percutor) / COUNT(*)) * 100) as frecuencia_uso
                FROM asignacion 
                WHERE asignacion_taladro_percutor > 0 AND {condicion_fecha} AND {condicion_estado} AND {condicion_usuario}
                ORDER BY frecuencia_uso DESC
                LIMIT 10
            """)
            top_dotaciones = cursor.fetchall()
            # Formatear los valores para JSON
            for item in top_dotaciones:
                for k, v in item.items():
                    if v is None:
                        item[k] = 0
                    elif isinstance(v, Decimal):
                        item[k] = float(v)
            resultados['top_dotaciones'] = top_dotaciones
        
        if categoria == 'todos' or categoria == 'epps':
            cursor.execute(f"""
                SELECT 
                    'Arnés' as descripcion,
                    'EPP-001' as codigo,
                    COUNT(*) as cantidad_total,
                    SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as asignados,
                    SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as disponibles,
                    ROUND((SUM(asignacion_arnes) / COUNT(*)) * 100) as frecuencia_uso
                FROM asignacion 
                WHERE asignacion_arnes > 0 AND {condicion_fecha} AND {condicion_estado} AND {condicion_usuario}
                UNION ALL
                SELECT 
                    'Eslinga' as descripcion,
                    'EPP-002' as codigo,
                    COUNT(*) as cantidad_total,
                    SUM(CASE WHEN asignacion_estado = '1' THEN 1 ELSE 0 END) as asignados,
                    SUM(CASE WHEN asignacion_estado = '0' THEN 1 ELSE 0 END) as disponibles,
                    ROUND((SUM(asignacion_eslinga) / COUNT(*)) * 100) as frecuencia_uso
                FROM asignacion 
                WHERE asignacion_eslinga > 0 AND {condicion_fecha} AND {condicion_estado} AND {condicion_usuario}
                ORDER BY frecuencia_uso DESC
                LIMIT 10
            """)
            top_epps = cursor.fetchall()
            # Formatear los valores para JSON
            for item in top_epps:
                for k, v in item.items():
                    if v is None:
                        item[k] = 0
                    elif isinstance(v, Decimal):
                        item[k] = float(v)
            resultados['top_epps'] = top_epps
        
        if categoria == 'todos' or categoria == 'ferretero':
            cursor.execute(f"""
                SELECT 
                    'Silicona' as descripcion,
                    'F-001' as codigo,
                    COUNT(*) as cantidad_total,
                    SUM(silicona) as asignados,
                    0 as disponibles,
                    ROUND((SUM(silicona) / COUNT(*)) * 100) as frecuencia_uso
                FROM ferretero 
                WHERE silicona > 0 AND {condicion_fecha} AND {condicion_estado} AND {condicion_usuario}
                UNION ALL
                SELECT 
                    'Amarres Negros' as descripcion,
                    'F-002' as codigo,
                    COUNT(*) as cantidad_total,
                    SUM(amarres_negros) as asignados,
                    0 as disponibles,
                    ROUND((SUM(amarres_negros) / COUNT(*)) * 100) as frecuencia_uso
                FROM ferretero 
                WHERE amarres_negros > 0 AND {condicion_fecha} AND {condicion_estado} AND {condicion_usuario}
                UNION ALL
                SELECT 
                    'Amarres Blancos' as descripcion,
                    'F-003' as codigo,
                    COUNT(*) as cantidad_total,
                    SUM(amarres_blancos) as asignados,
                    0 as disponibles,
                    ROUND((SUM(amarres_blancos) / COUNT(*)) * 100) as frecuencia_uso
                FROM ferretero 
                WHERE amarres_blancos > 0 AND {condicion_fecha} AND {condicion_estado} AND {condicion_usuario}
                UNION ALL
                SELECT 
                    'Cinta Aislante' as descripcion,
                    'F-004' as codigo,
                    COUNT(*) as cantidad_total,
                    SUM(cinta_aislante) as asignados,
                    0 as disponibles,
                    ROUND((SUM(cinta_aislante) / COUNT(*)) * 100) as frecuencia_uso
                FROM ferretero 
                WHERE cinta_aislante > 0 AND {condicion_fecha} AND {condicion_estado} AND {condicion_usuario}
                ORDER BY frecuencia_uso DESC
                LIMIT 10
            """)
            top_ferretero = cursor.fetchall()
            # Formatear los valores para JSON
            for item in top_ferretero:
                for k, v in item.items():
                    if v is None:
                        item[k] = 0
                    elif isinstance(v, Decimal):
                        item[k] = float(v)
            resultados['top_ferretero'] = top_ferretero
        
        return jsonify({
            'total_elementos': contadores['total_elementos'],
            'elementos_asignados': contadores['elementos_asignados'],
            'elementos_disponibles': contadores['elementos_disponibles'],
            'elementos_mantenimiento': contadores['elementos_mantenimiento'],
            'top_herramientas': resultados.get('top_herramientas', []),
            'top_dotaciones': resultados.get('top_dotaciones', []),
            'top_epps': resultados.get('top_epps', []),
            'top_ferretero': resultados.get('top_ferretero', []),
            'herramientas': categorias['herramientas'],
            'dotaciones': categorias['dotaciones'],
            'epps': categorias['epps'],
            'ferretero': categorias['ferretero'],
            'estadisticas': estadisticas,
            'tendencia': datos_tendencia,
            'mas_asignados': {
                'labels': labels_mas_asignados,
                'datos': datos_mas_asignados
            },
            'tendencia_asignacion': tendencia_asignacion,
            'tendencia_ferretero': tendencia_ferretero
        })
        
    except mysql.connector.Error as e:
        flash(f'Error al cargar datos: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8080)