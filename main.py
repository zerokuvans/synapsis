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
import psycopg2.extras

load_dotenv()

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
    'port': int(os.getenv('MYSQL_PORT'))
}

# Función para obtener conexión a la base de datos
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Probar la conexión a la base de datos
try:
    connection = get_db_connection()
    if connection is None:
        raise Exception('Failed to establish a database connection.')
    print('Database connection established successfully.')
    connection.close()
except Exception as e:
    print(f'Error: {str(e)}')

# Roles definition
ROLES = {
    '1': 'administrativo',
    '2': 'tecnicos',
    '3': 'operativo',
    '4': 'contabilidad',
    '5': 'logistica'
}

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
                flash('Database connection failed. Please check your configuration.', 'error')
                return render_template('login.html')
                
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
                    return redirect(url_for('dashboard'))
                else:
                    flash('Usuario o contraseña inválidos', 'error')
            else:
                flash('Usuario o contraseña inválidos', 'error')

        except Error as e:
            flash(f'Ocurrió un error: {str(e)}', 'error')
            return render_template('login.html')

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
        cursor.close()
        connection.close()
        
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
        
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/exportar_usuarios_csv', methods=['POST'])
@login_required(role='administrativo')
def exportar_usuarios_csv():
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener todos los usuarios
        cursor.execute("SELECT id_codigo_consumidor, recurso_operativo_cedula, id_roles, estado FROM recurso_operativo")
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        
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
            return jsonify({'status': 'error', 'message': 'Error de conexión a la base de datos.'})

        cursor = connection.cursor(dictionary=True)
        
        # Verificar si ya existe un registro para el día actual
        id_codigo_consumidor = request.form.get('id_codigo_consumidor')
        fecha_actual = datetime.now().date()
        
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM preoperacional 
            WHERE id_codigo_consumidor = %s 
            AND DATE(fecha) = %s
        """, (id_codigo_consumidor, fecha_actual))
        
        resultado = cursor.fetchone()
        if resultado['count'] > 0:
            return jsonify({
                'status': 'error',
                'message': 'Ya has registrado un preoperacional para el día de hoy.'
            })

        # Obtener datos del formulario
        centro_de_trabajo = request.form.get('centro_de_trabajo')
        ciudad = request.form.get('ciudad')
        supervisor = request.form.get('supervisor')
        vehiculo_asistio_operacion = request.form.get('vehiculo_asistio_operacion')
        tipo_vehiculo = request.form.get('tipo_vehiculo')
        placa_vehiculo = request.form.get('placa_vehiculo')
        modelo_vehiculo = request.form.get('modelo_vehiculo')
        marca_vehiculo = request.form.get('marca_vehiculo')
        licencia_conduccion = request.form.get('licencia_conduccion')
        fecha_vencimiento_licencia = request.form.get('fecha_vencimiento_licencia')
        fecha_vencimiento_soat = request.form.get('fecha_vencimiento_soat')
        fecha_vencimiento_tecnomecanica = request.form.get('fecha_vencimiento_tecnomecanica')
        estado_espejos = request.form.get('estado_espejos', 0)
        bocina_pito = request.form.get('bocina_pito', 0)
        frenos = request.form.get('frenos', 0)
        encendido = request.form.get('encendido', 0)
        estado_bateria = request.form.get('estado_bateria', 0)
        estado_amortiguadores = request.form.get('estado_amortiguadores', 0)
        estado_llantas = request.form.get('estado_llantas', 0)
        kilometraje_actual = request.form.get('kilometraje_actual', 0)
        luces_altas_bajas = request.form.get('luces_altas_bajas', 0)
        direccionales_delanteras_traseras = request.form.get('direccionales_delanteras_traseras', 0)
        elementos_prevencion_seguridad_vial_casco = request.form.get('elementos_prevencion_seguridad_vial_casco', 0)
        casco_certificado = request.form.get('casco_certificado', 0)
        casco_identificado = request.form.get('casco_identificado', 0)
        estado_guantes = request.form.get('estado_guantes', 0)
        estado_rodilleras = request.form.get('estado_rodilleras', 0)
        impermeable = request.form.get('impermeable', 0)
        observaciones = request.form.get('observaciones', '')
        estado_fisico_vehiculo_espejos = request.form.get('estado_fisico_vehiculo_espejos', 0)
        estado_fisico_vehiculo_bocina_pito = request.form.get('estado_fisico_vehiculo_bocina_pito', 0)
        estado_fisico_vehiculo_frenos = request.form.get('estado_fisico_vehiculo_frenos', 0)
        estado_fisico_vehiculo_encendido = request.form.get('estado_fisico_vehiculo_encendido', 0)
        estado_fisico_vehiculo_bateria = request.form.get('estado_fisico_vehiculo_bateria', 0)
        estado_fisico_vehiculo_amortiguadores = request.form.get('estado_fisico_vehiculo_amortiguadores', 0)
        estado_fisico_vehiculo_llantas = request.form.get('estado_fisico_vehiculo_llantas', 0)
        estado_fisico_vehiculo_luces_altas = request.form.get('estado_fisico_vehiculo_luces_altas', 0)
        estado_fisico_vehiculo_luces_bajas = request.form.get('estado_fisico_vehiculo_luces_bajas', 0)
        estado_fisico_vehiculo_direccionales_delanteras = request.form.get('estado_fisico_vehiculo_direccionales_delanteras', 0)
        estado_fisico_vehiculo_direccionales_traseras = request.form.get('estado_fisico_vehiculo_direccionales_traseras', 0)
        elementos_prevencion_seguridad_vial_guantes = request.form.get('elementos_prevencion_seguridad_vial_guantes', 0)
        elementos_prevencion_seguridad_vial_rodilleras = request.form.get('elementos_prevencion_seguridad_vial_rodilleras', 0)
        elementos_prevencion_seguridad_vial_coderas = request.form.get('elementos_prevencion_seguridad_vial_coderas', 0)
        elementos_prevencion_seguridad_vial_impermeable = request.form.get('elementos_prevencion_seguridad_vial_impermeable', 0)
        casco_identificado_placa = request.form.get('casco_identificado_placa', 0)

        # Verificar que el id_codigo_consumidor existe en la tabla recurso_operativo
        cursor.execute("SELECT id_codigo_consumidor FROM recurso_operativo WHERE id_codigo_consumidor = %s", (id_codigo_consumidor,))
        if cursor.fetchone() is None:
            return jsonify({'status': 'error', 'message': 'El id_codigo_consumidor no existe en la tabla recurso_operativo.'})

        # Mensajes de depuración
        # print(f"Datos recibidos: {request.form}")
        # print(f"ID de usuario en sesión: {session.get('user_id')}")

        sql = """
            INSERT INTO preoperacional (
                centro_de_trabajo, ciudad, supervisor, vehiculo_asistio_operacion, tipo_vehiculo, placa_vehiculo, modelo_vehiculo, marca_vehiculo, licencia_conduccion, fecha_vencimiento_licencia, fecha_vencimiento_soat, fecha_vencimiento_tecnomecanica, estado_espejos, bocina_pito, frenos, encendido, estado_bateria, estado_amortiguadores, estado_llantas, kilometraje_actual, luces_altas_bajas, direccionales_delanteras_traseras, elementos_prevencion_seguridad_vial_casco, casco_certificado, casco_identificado, estado_guantes, estado_rodilleras, impermeable, observaciones, estado_fisico_vehiculo_espejos, estado_fisico_vehiculo_bocina_pito, estado_fisico_vehiculo_frenos, estado_fisico_vehiculo_encendido, estado_fisico_vehiculo_bateria, estado_fisico_vehiculo_amortiguadores, estado_fisico_vehiculo_llantas, estado_fisico_vehiculo_luces_altas, estado_fisico_vehiculo_luces_bajas, estado_fisico_vehiculo_direccionales_delanteras, estado_fisico_vehiculo_direccionales_traseras, elementos_prevencion_seguridad_vial_guantes, elementos_prevencion_seguridad_vial_rodilleras, elementos_prevencion_seguridad_vial_coderas, elementos_prevencion_seguridad_vial_impermeable, casco_identificado_placa, id_codigo_consumidor
            ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            centro_de_trabajo, ciudad, supervisor, vehiculo_asistio_operacion, tipo_vehiculo, placa_vehiculo, modelo_vehiculo, marca_vehiculo, licencia_conduccion, fecha_vencimiento_licencia, fecha_vencimiento_soat, fecha_vencimiento_tecnomecanica, estado_espejos, bocina_pito, frenos, encendido, estado_bateria, estado_amortiguadores, estado_llantas, kilometraje_actual, luces_altas_bajas, direccionales_delanteras_traseras, elementos_prevencion_seguridad_vial_casco, casco_certificado, casco_identificado, estado_guantes, estado_rodilleras, impermeable, observaciones, estado_fisico_vehiculo_espejos, estado_fisico_vehiculo_bocina_pito, estado_fisico_vehiculo_frenos, estado_fisico_vehiculo_encendido, estado_fisico_vehiculo_bateria, estado_fisico_vehiculo_amortiguadores, estado_fisico_vehiculo_llantas, estado_fisico_vehiculo_luces_altas, estado_fisico_vehiculo_luces_bajas, estado_fisico_vehiculo_direccionales_delanteras, estado_fisico_vehiculo_direccionales_traseras, elementos_prevencion_seguridad_vial_guantes, elementos_prevencion_seguridad_vial_rodilleras, elementos_prevencion_seguridad_vial_coderas, elementos_prevencion_seguridad_vial_impermeable, casco_identificado_placa, id_codigo_consumidor
        ))
        connection.commit()
        flash('Inspección preoperacional registrada exitosamente.', 'success')
        return redirect(url_for('dashboard'))
    except Error as e:
        # print(f'Error al registrar inspección: {str(e)}')  # Mensaje de depuración
        return jsonify({'status': 'error', 'message': f'Error al registrar inspección: {str(e)}'})
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

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
                r.cargo as cargo_tecnico
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
            'Fecha', 'Técnico', 'Cargo', 'Centro de Trabajo', 'Ciudad', 'Supervisor',
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

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8080)