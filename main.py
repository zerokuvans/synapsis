from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
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
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        try:
            connection = get_db_connection()
            if connection is None:
                return jsonify({'status': 'error', 'message': 'Error de conexión a la base de datos'}), 500
                
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id_codigo_consumidor, id_roles, recurso_operativo_password, nombre FROM recurso_operativo WHERE recurso_operativo_cedula = %s", (username,))
            user = cursor.fetchone()

            if user:
                stored_password = user['recurso_operativo_password']
                if isinstance(stored_password, str):
                    stored_password = stored_password.encode('utf-8')
                if bcrypt.checkpw(password, stored_password):
                    session['user_id'] = user['id_codigo_consumidor']
                    session['user_role'] = ROLES.get(str(user['id_roles']))
                    session['user_name'] = user['nombre']

                    # Verificar vencimientos para el usuario
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

                    cursor.close()
                    connection.close()

                    # Si la solicitud espera JSON, devolver respuesta JSON
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            'status': 'success',
                            'message': 'Login successful',
                            'user_id': user['id_codigo_consumidor'],
                            'user_role': ROLES.get(str(user['id_roles'])),
                            'user_name': user['nombre'],
                            'redirect_url': url_for('dashboard')
                        })
                    # Si es una solicitud normal, redirigir
                    return redirect(url_for('dashboard'))
                else:
                    return jsonify({'status': 'error', 'message': 'Usuario o contraseña inválidos'}), 401
            else:
                return jsonify({'status': 'error', 'message': 'Usuario o contraseña inválidos'}), 401

        except Error as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

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

        # Obtener lista de supervisores únicos
        cur.execute("""
            SELECT DISTINCT supervisor 
            FROM preoperacional 
            WHERE supervisor IS NOT NULL 
            AND supervisor != '' 
            ORDER BY supervisor
        """)
        supervisores = [row['supervisor'] for row in cur.fetchall()]

        # Calcular estadísticas
        total_registros = len(registros)
        registros_hoy = sum(1 for r in registros if r['fecha'].date() == datetime.now().date())
        registros_semana = sum(1 for r in registros if r['fecha'].date() >= (datetime.now() - timedelta(days=7)).date())

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

        cur.close()
        conn.close()

        return render_template('modulos/administrativo/listado_preoperacional.html', 
                            registros=registros,
                            supervisores=supervisores,
                            fecha_inicio=fecha_inicio,
                            fecha_fin=fecha_fin,
                            supervisor=supervisor,
                            estado_vehiculo=estado_vehiculo,
                            total_registros=total_registros,
                            registros_hoy=registros_hoy,
                            registros_semana=registros_semana,
                            fechas=fechas,
                            registros_por_dia=registros_por_dia)

    except Exception as e:
        flash('Error al cargar el listado preoperacional: ' + str(e), 'error')
        return render_template('modulos/administrativo/listado_preoperacional.html',
                            registros=[],
                            supervisores=[],
                            fecha_inicio=fecha_inicio,
                            fecha_fin=fecha_fin,
                            supervisor=supervisor,
                            estado_vehiculo=estado_vehiculo,
                            total_registros=0,
                            registros_hoy=0,
                            registros_semana=0,
                            fechas=[],
                            registros_por_dia=[])

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
        writer = csv.writer(output, dialect='excel')
        
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
            writer.writerow([
                registro['fecha'].strftime('%Y-%m-%d %H:%M:%S'),
                registro['nombre_tecnico'],
                registro['cedula_tecnico'],
                registro['cargo_tecnico'],
                registro['centro_de_trabajo'],
                registro['ciudad'],
                registro['supervisor'],
                registro['vehiculo_asistio_operacion'],
                registro['tipo_vehiculo'],
                registro['placa_vehiculo'],
                registro['modelo_vehiculo'],
                registro['marca_vehiculo'],
                registro['licencia_conduccion'],
                registro['fecha_vencimiento_licencia'],
                registro['fecha_vencimiento_soat'],
                registro['fecha_vencimiento_tecnomecanica'],
                registro['estado_espejos'],
                registro['bocina_pito'],
                registro['frenos'],
                registro['encendido'],
                registro['estado_bateria'],
                registro['estado_amortiguadores'],
                registro['estado_llantas'],
                registro['kilometraje_actual'],
                registro['luces_altas_bajas'],
                registro['direccionales_delanteras_traseras'],
                registro['elementos_prevencion_seguridad_vial_casco'],
                registro['casco_certificado'],
                registro['casco_identificado'],
                registro['estado_guantes'],
                registro['estado_rodilleras'],
                registro['impermeable'],
                registro['observaciones']
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

        # Procesar campos de herramientas y equipo de seguridad
        for campo, valor in request.form.items():
            if campo not in ['id_codigo_consumidor', 'fecha', 'cargo']:
                nombre_campo = f'asignacion_{campo}'
                
                if nombre_campo.lower() in columnas_existentes:
                    campos.append(nombre_campo)
                    valores.append(valor if valor == '1' else '0')
                else:
                    print(f"Campo ignorado (no existe en la tabla): {nombre_campo}")  # Debug log

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
    """
    Obtiene los detalles de una asignación específica.
    
    Args:
        id_asignacion (int): ID de la asignación a consultar
        
    Returns:
        JSON con los detalles de la asignación o mensaje de error
    """
    connection = None
    cursor = None
    
    try:
        # Validar que el ID sea positivo
        if not isinstance(id_asignacion, int) or id_asignacion <= 0:
            return jsonify({
                'status': 'error',
                'message': 'El ID de asignación debe ser un número positivo'
            }), 400

        connection = get_db_connection()
        if connection is None:
            return jsonify({
                'status': 'error',
                'message': 'Error de conexión a la base de datos'
            }), 500
            
        cursor = connection.cursor(dictionary=True)
        
        try:
            # Consulta optimizada con COALESCE para manejar valores nulos
            cursor.execute("""
                SELECT 
                    a.*,
                    COALESCE(r.nombre, 'No asignado') as nombre,
                    COALESCE(r.recurso_operativo_cedula, 'No disponible') as recurso_operativo_cedula,
                    COALESCE(r.cargo, 'No especificado') as cargo
                FROM asignacion a 
                LEFT JOIN recurso_operativo r ON a.id_codigo_consumidor = r.id_codigo_consumidor 
                WHERE a.id_asignacion = %s
            """, (id_asignacion,))
            
            asignacion = cursor.fetchone()
            
            if not asignacion:
                return jsonify({
                    'status': 'error',
                    'message': f'No se encontró la asignación con ID {id_asignacion}'
                }), 404

            # Validar campos requeridos
            campos_requeridos = ['id_asignacion', 'asignacion_fecha', 'id_codigo_consumidor']
            campos_faltantes = [campo for campo in campos_requeridos if campo not in asignacion or asignacion[campo] is None]
            
            if campos_faltantes:
                return jsonify({
                    'status': 'error',
                    'message': f'Datos de asignación incompletos: faltan los campos {", ".join(campos_faltantes)}'
                }), 500
            
            # Definir las categorías de herramientas
            herramientas_basicas = [
                'adaptador_mandril', 'alicate', 'barra_45cm', 'bisturi_metalico',
                'caja_de_herramientas', 'cortafrio', 'destor_de_estrella', 'destor_de_pala',
                'destor_tester', 'martillo_de_una', 'pinza_de_punta'
            ]
            
            herramientas_especializadas = [
                'multimetro', 'taladro_percutor', 'ponchadora_rg_6_y_rg_11', 
                'ponchadora_rj_45_y_rj11', 'power_miter', 'bfl_laser', 'cortadora', 
                'stripper_fibra'
            ]
            
            equipo_seguridad = [
                'arnes', 'eslinga', 'casco_tipo_ii', 'arana_casco', 'barbuquejo',
                'guantes_de_vaqueta', 'gafas', 'linea_de_vida'
            ]
            
            # Organizar las herramientas por categoría
            detalles = {
                'info_basica': {
                    'id_asignacion': asignacion['id_asignacion'],
                    'fecha': asignacion['asignacion_fecha'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(asignacion['asignacion_fecha'], datetime) else str(asignacion['asignacion_fecha']),
                    'tecnico': asignacion['nombre'],
                    'cedula': asignacion['recurso_operativo_cedula'],
                    'cargo': asignacion.get('asignacion_cargo', 'No especificado'),
                    'estado': 'Activo' if str(asignacion.get('asignacion_estado', '0')) == '1' else 'Inactivo'
                },
                'herramientas_basicas': {},
                'herramientas_especializadas': {},
                'equipo_seguridad': {}
            }
            
            def formatear_valor_herramienta(valor):
                """Formatea el valor de una herramienta a '1' o '0'"""
                try:
                    return '1' if str(valor).strip() in ['1', 'True', 'true'] else '0'
                except (ValueError, AttributeError):
                    return '0'
            
            # Llenar herramientas básicas
            for herramienta in herramientas_basicas:
                campo = f'asignacion_{herramienta}'
                detalles['herramientas_basicas'][herramienta] = formatear_valor_herramienta(asignacion.get(campo))
                    
            # Llenar herramientas especializadas
            for herramienta in herramientas_especializadas:
                campo = f'asignacion_{herramienta}'
                detalles['herramientas_especializadas'][herramienta] = formatear_valor_herramienta(asignacion.get(campo))
                    
            # Llenar equipo de seguridad
            for equipo in equipo_seguridad:
                campo = f'asignacion_{equipo}'
                detalles['equipo_seguridad'][equipo] = formatear_valor_herramienta(asignacion.get(campo))
            
            return jsonify({
                'status': 'success',
                'data': detalles
            })
            
        except mysql.connector.Error as e:
            print(f"Error de MySQL: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Error en la base de datos al procesar la asignación'
            }), 500
            
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
                asignacion.get('asignacion_arnes', '0'),
                asignacion.get('asignacion_eslinga', '0'),
                asignacion.get('asignacion_casco_tipo_ii', '0'),
                asignacion.get('asignacion_arana_casco', '0'),
                asignacion.get('asignacion_barbuquejo', '0'),
                asignacion.get('asignacion_guantes_de_vaqueta', '0'),
                asignacion.get('asignacion_gafas', '0'),
                asignacion.get('asignacion_linea_de_vida', '0')
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
        
        # Obtener conteo de equipo de seguridad asignado
        equipo_seguridad_query = """
            SELECT 
                SUM(asignacion_arnes) as arnes,
                SUM(asignacion_eslinga) as eslinga,
                SUM(asignacion_casco_tipo_ii) as casco_tipo_ii,
                SUM(asignacion_arana_casco) as arana_casco,
                SUM(asignacion_barbuquejo) as barbuquejo,
                SUM(asignacion_guantes_de_vaqueta) as guantes_vaqueta,
                SUM(asignacion_gafas) as gafas,
                SUM(asignacion_linea_de_vida) as linea_vida
            FROM asignacion 
            WHERE asignacion_estado = '1'
        """
        cursor.execute(equipo_seguridad_query)
        equipo_seguridad = cursor.fetchone()

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
        
        cursor.close()
        connection.close()

        return render_template('modulos/logistica/inventario.html',
                           herramientas_basicas=herramientas_basicas,
                           herramientas_especializadas=herramientas_especializadas,
                           equipo_seguridad=equipo_seguridad,
                           material_ferretero=material_ferretero)

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
            SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula, cargo 
            FROM recurso_operativo 
            WHERE cargo LIKE '%TECNICO%' OR cargo LIKE '%TÉCNICO%'
            ORDER BY nombre
        """)
        tecnicos = cursor.fetchall()
        
        cursor.close()
        connection.close()

        return render_template('modulos/logistica/ferretero.html', 
                            asignaciones=asignaciones,
                            tecnicos=tecnicos)

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

        # Verificar que el técnico existe
        cursor.execute('SELECT nombre FROM recurso_operativo WHERE id_codigo_consumidor = %s', (id_codigo_consumidor,))
        tecnico = cursor.fetchone()
        
        if not tecnico:
            return jsonify({
                'status': 'error',
                'message': 'El técnico seleccionado no existe'
            }), 404

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
            'message': 'Material ferretero asignado exitosamente'
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

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8080)