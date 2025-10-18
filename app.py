from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
import logging
import pytz
import os
from datetime import date, datetime
import bcrypt

app = Flask(__name__)
app.secret_key = 'synapsis-secret-key-2024-production-secure-key-12345'
db = SQLAlchemy()

# Configuración de zona horaria
TIMEZONE = pytz.timezone('America/Bogota')

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirigir al login cuando se requiera autenticación

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
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Función para obtener la fecha y hora actual en Bogotá
def get_bogota_datetime():
    return datetime.now(TIMEZONE)

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
        
        # Insertar cada asistencia
        asistencias_guardadas = 0
        for asistencia in data['asistencias']:
            try:
                cursor.execute("""
                    INSERT INTO asistencia (
                        cedula, tecnico, carpeta_dia, carpeta, super, 
                        id_codigo_consumidor, fecha_asistencia
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (
                    asistencia['cedula'],
                    asistencia['tecnico'],
                    asistencia['carpeta_dia'],
                    asistencia.get('carpeta', ''),
                    asistencia['super'],
                    asistencia['id_codigo_consumidor']
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
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()


            connection.close()

@app.route('/preoperacional', methods=['POST'])
@login_required
def preoperacional():
    try:
        # Obtener datos del formulario
        data = request.get_json()
        
        # Obtener la fecha actual en zona horaria de Bogotá
        bogota_tz = pytz.timezone('America/Bogota')
        fecha_actual = datetime.now(bogota_tz).date()
        
        # Verificar si ya existe un registro para este usuario en la fecha actual
        cursor = get_db_connection().cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM preoperacional 
            WHERE id_codigo_consumidor = %s AND DATE(fecha_registro) = %s
        """, (session['id_codigo_consumidor'], fecha_actual))
        
        if cursor.fetchone()[0] > 0:
            cursor.close()
            return jsonify({
                'success': False, 
                'message': 'Ya existe un registro preoperacional para hoy'
            }), 400
        
        # Verificar que el id_codigo_consumidor existe en la tabla usuarios
        cursor.execute("SELECT id_codigo_consumidor FROM usuarios WHERE id_codigo_consumidor = %s", 
                      (session['id_codigo_consumidor'],))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({
                'success': False, 
                'message': 'Usuario no encontrado'
            }), 400
        
        # Insertar el nuevo registro
        insert_query = """
            INSERT INTO preoperacional (
                id_codigo_consumidor, fecha_registro, vehiculo_asignado, placa_vehiculo,
                kilometraje, nivel_combustible, nivel_aceite, nivel_liquido_frenos,
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
        
        get_db_connection().commit()
        cursor.close()
        
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
        cursor = get_db_connection().cursor()
        cursor.execute("""
            SELECT fecha_registro FROM preoperacional 
            WHERE id_codigo_consumidor = %s AND DATE(fecha_registro) = %s
            ORDER BY fecha_registro DESC LIMIT 1
        """, (session['id_codigo_consumidor'], fecha_actual))
        
        resultado = cursor.fetchone()
        cursor.close()
        
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

# ============================================================================
# MÓDULO ANALISTAS - API ENDPOINTS
# ============================================================================

@app.route('/analistas')
@login_required
def analistas_index():
    """Renderizar el dashboard del módulo analistas"""
    return render_template('modulos/analistas/dashboard.html')

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
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
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
        logging.error(f"Error en API causas-cierre: {str(e)}")
        return jsonify({'error': 'Error al consultar la base de datos'}), 500
    except Exception as e:
        logging.error(f"Error inesperado en API causas-cierre: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
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
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
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
        logging.error(f"Error en API grupos: {str(e)}")
        return jsonify({'error': 'Error al consultar la base de datos'}), 500
    except Exception as e:
        logging.error(f"Error inesperado en API grupos: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
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
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
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
        logging.error(f"Error en API tecnologías: {str(e)}")
        return jsonify({'error': 'Error al consultar la base de datos'}), 500
    except Exception as e:
        logging.error(f"Error inesperado en API tecnologías: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
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
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
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
        logging.error(f"Error en API agrupaciones: {str(e)}")
        return jsonify({'error': 'Error al consultar la base de datos'}), 500
    except Exception as e:
        logging.error(f"Error inesperado en API agrupaciones: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
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
                }
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
        
        # Consulta para obtener vehículos con información del técnico asignado
        query = """
        SELECT 
            v.id_mpa_vehiculos,
            v.cedula_propietario,
            v.nombre_propietario,
            v.placa,
            v.tipo_vehiculo,
            v.vin,
            v.numero_de_motor,
            v.fecha_de_matricula,
            v.estado,
            v.marca,
            v.linea,
            v.modelo,
            v.color,
            v.kilometraje_actual,
            v.fecha_creacion,
            v.tecnico_asignado,
            v.observaciones,
            ro.nombre as tecnico_nombre
        FROM mpa_vehiculos v
        LEFT JOIN recurso_operativo ro ON v.tecnico_asignado = ro.id_codigo_consumidor
        ORDER BY v.fecha_creacion DESC
        """
        
        cursor.execute(query)
        vehiculos = cursor.fetchall()
        
        # Formatear fechas para el frontend
        for vehiculo in vehiculos:
            if vehiculo['fecha_de_matricula']:
                vehiculo['fecha_de_matricula'] = vehiculo['fecha_de_matricula'].strftime('%Y-%m-%d')
            if vehiculo['fecha_creacion']:
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
        
        # Insertar nuevo vehículo
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
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vehículo creado exitosamente',
            'id': cursor.lastrowid
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
    """API para actualizar un vehículo"""
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
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vehículo actualizado exitosamente'
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
def mpa_vencimientos():
    """Módulo de gestión de vencimientos consolidados"""
    # Temporalmente sin autenticación para pruebas
    # if not current_user.has_role('administrativo'):
    #     flash('No tienes permisos para acceder a este módulo.', 'error')
    #     return redirect(url_for('mpa_dashboard'))
    
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

@app.route('/mpa/inspecciones')
@login_required
def mpa_inspecciones():
    """Módulo de gestión de inspecciones vehiculares"""
    if not current_user.has_role('administrativo'):
        flash('No tienes permisos para acceder a este módulo.', 'error')
        return redirect(url_for('mpa_dashboard'))
    
    # TODO: Implementar página de inspecciones
    flash('Módulo en desarrollo', 'info')
    return redirect(url_for('mpa_dashboard'))

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
        
        # Obtener mantenimientos con información del vehículo
        query = """
        SELECT 
            m.id_mpa_mantenimientos,
            m.placa,
            m.fecha_mantenimiento,
            m.kilometraje,
            m.observacion,
            m.soporte_foto_geo as foto_taller,
            m.soporte_foto_factura as foto_factura,
            m.tipo_vehiculo,
            m.tecnico as tecnico_nombre,
            m.tipo_mantenimiento
        FROM mpa_mantenimientos m
        ORDER BY m.fecha_mantenimiento DESC
        """
        
        cursor.execute(query)
        mantenimientos = cursor.fetchall()
        
        # Formatear fechas para el frontend
        for mantenimiento in mantenimientos:
            if mantenimiento['fecha_mantenimiento']:
                mantenimiento['fecha_mantenimiento'] = mantenimiento['fecha_mantenimiento'].strftime('%Y-%m-%d %H:%M:%S')
        
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
        
        query = """
        SELECT 
            m.id_mpa_mantenimientos,
            m.placa,
            m.fecha_mantenimiento,
            m.kilometraje,
            m.observacion,
            m.soporte_foto_geo as foto_taller,
            m.soporte_foto_factura as foto_factura,
            m.tipo_vehiculo,
            m.tecnico as tecnico_nombre,
            m.tipo_mantenimiento
        FROM mpa_mantenimientos m
        WHERE m.id_mpa_mantenimientos = %s
        """
        
        cursor.execute(query, (mantenimiento_id,))
        mantenimiento = cursor.fetchone()
        
        if not mantenimiento:
            return jsonify({'success': False, 'error': 'Mantenimiento no encontrado'}), 404
        
        # Formatear fecha
        if mantenimiento['fecha_mantenimiento']:
            mantenimiento['fecha_mantenimiento'] = mantenimiento['fecha_mantenimiento'].strftime('%Y-%m-%d %H:%M:%S')
        
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
        
        # Insertar nuevo mantenimiento
        insert_query = """
        INSERT INTO mpa_mantenimientos 
        (placa, fecha_mantenimiento, kilometraje, tipo_vehiculo, tipo_mantenimiento, observacion, soporte_foto_geo, soporte_foto_factura, tecnico)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            data['placa'],
            fecha_mantenimiento,
            data['kilometraje'],
            tipo_vehiculo,
            data['tipo_mantenimiento'],
            data['observacion'],
            data.get('foto_taller', ''),
            data.get('foto_factura', ''),
            data.get('tecnico', '')
        ))
        
        connection.commit()
        mantenimiento_id = cursor.lastrowid
        
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
        
        if 'tecnico' in data:
            update_fields.append("tecnico = %s")
            values.append(data['tecnico'])
        
        if 'observacion' in data:
            update_fields.append("observacion = %s")
            values.append(data['observacion'])
        
        if 'foto_taller' in data:
            update_fields.append("soporte_foto_geo = %s")
            values.append(data['foto_taller'])
        
        if 'foto_factura' in data:
            update_fields.append("soporte_foto_factura = %s")
            values.append(data['foto_factura'])
        
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
        LEFT JOIN recurso_operativo ro ON v.tecnico_asignado = ro.id_codigo_consumidor
        WHERE v.estado = 'Activo'
        ORDER BY v.placa
        """
        
        cursor.execute(query)
        placas = cursor.fetchall()
        
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
    """API para obtener lista de SOATs"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        # Obtener fecha actual de Bogotá
        fecha_bogota = get_bogota_datetime().date()
        
        query = """
        SELECT 
            s.id_mpa_soat,
            s.placa,
            s.numero_poliza,
            s.aseguradora,
            s.fecha_inicio,
            s.fecha_vencimiento,
            s.valor_prima,
            s.tecnico_asignado,
            s.estado,
            s.observaciones,
            s.fecha_creacion,
            s.fecha_actualizacion,
            v.tipo_vehiculo,
            COALESCE(ro.nombre, CAST(s.tecnico_asignado AS CHAR)) as tecnico_nombre,
            DATEDIFF(s.fecha_vencimiento, %s) as dias_vencimiento
        FROM mpa_soat s
        LEFT JOIN mpa_vehiculos v ON s.placa = v.placa
        LEFT JOIN recurso_operativo ro ON s.tecnico_asignado = ro.id_codigo_consumidor
        ORDER BY s.fecha_vencimiento ASC
        """
        
        cursor.execute(query, (fecha_bogota,))
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
        
        query = """
        SELECT 
            s.id_mpa_soat,
            s.placa,
            s.numero_poliza,
            s.aseguradora,
            s.fecha_inicio,
            s.fecha_vencimiento,
            s.valor_prima,
            s.tecnico_asignado,
            s.estado,
            s.observaciones,
            s.fecha_creacion,
            s.fecha_actualizacion,
            v.tipo_vehiculo,
            COALESCE(ro.nombre, CAST(s.tecnico_asignado AS CHAR)) as tecnico_nombre,
            DATEDIFF(s.fecha_vencimiento, %s) as dias_vencimiento
        FROM mpa_soat s
        LEFT JOIN mpa_vehiculos v ON s.placa = v.placa
        LEFT JOIN recurso_operativo ro ON s.tecnico_asignado = ro.id_codigo_consumidor
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
        
        # Verificar si ya existe un SOAT activo para esta placa
        cursor.execute("""
            SELECT id_mpa_soat FROM mpa_soat 
            WHERE placa = %s AND estado = 'Activo'
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
def api_vencimientos_consolidados():
    """API consolidada para obtener vencimientos de SOAT, Técnico Mecánica y Licencias de Conducir"""
    # Temporalmente sin autenticación para pruebas
    # if not current_user.has_role('administrativo'):
    #     return jsonify({'error': 'Sin permisos'}), 403
    
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
        WHERE s.fecha_vencimiento IS NOT NULL AND (ro.estado = 'Activo' OR s.tecnico_asignado IS NULL)
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
        WHERE tm.fecha_vencimiento IS NOT NULL AND (ro.estado = 'Activo' OR tm.tecnico_asignado IS NULL)
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
        WHERE lc.fecha_vencimiento IS NOT NULL AND (ro.estado = 'Activo' OR lc.tecnico IS NULL)
        ORDER BY lc.fecha_vencimiento ASC
        """
        
        cursor.execute(query_lc)
        licencias = cursor.fetchall()
        
        for lc in licencias:
            vencimientos_consolidados.append({
                'id': lc['id'],
                'tipo': 'Licencia de Conducir',
                'placa': None,  # Las licencias no tienen placa
                'fecha_vencimiento': lc['fecha_vencimiento'].strftime('%Y-%m-%d') if lc['fecha_vencimiento'] else None,
                'tecnico_nombre': lc['tecnico_nombre'] or 'Sin asignar',
                'estado_original': None  # Las licencias no tienen campo estado
            })
        
        # 4. Calcular días restantes y estado para todos los vencimientos
        from datetime import datetime
        import pytz
        
        colombia_tz = pytz.timezone('America/Bogota')
        fecha_actual = datetime.now(colombia_tz).date()
        
        for vencimiento in vencimientos_consolidados:
            if vencimiento['fecha_vencimiento']:
                fecha_venc = datetime.strptime(vencimiento['fecha_vencimiento'], '%Y-%m-%d').date()
                dias_restantes = (fecha_venc - fecha_actual).days
                
                vencimiento['dias_restantes'] = dias_restantes
                
                # Determinar estado basado en días restantes
                if dias_restantes < 0:
                    vencimiento['estado'] = 'Vencido'
                elif dias_restantes <= 30:
                    vencimiento['estado'] = 'Próximo a vencer'
                else:
                    vencimiento['estado'] = 'Vigente'
            else:
                vencimiento['dias_restantes'] = None
                vencimiento['estado'] = 'Sin fecha'
        
        # 5. Ordenar por fecha de vencimiento (más próximos primero)
        vencimientos_consolidados.sort(key=lambda x: (
            x['fecha_vencimiento'] if x['fecha_vencimiento'] else '9999-12-31'
        ))
        
        return jsonify({
            'success': True,
            'data': vencimientos_consolidados,
            'total': len(vencimientos_consolidados)
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
def api_get_vencimiento_detalle(tipo, documento_id):
    """API para obtener detalles de un vencimiento específico"""
    # Temporalmente sin autenticación para pruebas
    # if not current_user.has_role('administrativo'):
    #     return jsonify({'error': 'Sin permisos'}), 403
    
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
    """API para obtener todas las técnico mecánicas"""
    if not current_user.has_role('administrativo'):
        return jsonify({'error': 'Sin permisos'}), 403
    
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT 
            tm.id_mpa_tecnico_mecanica,
            tm.placa,
            tm.fecha_inicio,
            tm.fecha_vencimiento,
            tm.tecnico_asignado,
            tm.estado,
            tm.observaciones,
            tm.fecha_creacion,
            tm.fecha_actualizacion,
            tm.tipo_vehiculo,
            v.tipo_vehiculo as vehiculo_tipo,
            v.tecnico_asignado as vehiculo_tecnico,
            ro.nombre as tecnico_nombre
        FROM mpa_tecnico_mecanica tm
        LEFT JOIN mpa_vehiculos v ON tm.placa = v.placa
        LEFT JOIN recurso_operativo ro ON tm.tecnico_asignado = ro.id_codigo_consumidor
        ORDER BY tm.fecha_creacion DESC
        """
        
        cursor.execute(query)
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
        
        query = """
        SELECT 
            tm.id_mpa_tecnico_mecanica,
            tm.placa,
            tm.fecha_inicio,
            tm.fecha_vencimiento,
            tm.tecnico_asignado,
            tm.estado,
            tm.observaciones,
            tm.fecha_creacion,
            tm.fecha_actualizacion,
            tm.tipo_vehiculo,
            v.tipo_vehiculo as vehiculo_tipo,
            v.tecnico_asignado as vehiculo_tecnico,
            ro.nombre as tecnico_nombre
        FROM mpa_tecnico_mecanica tm
        LEFT JOIN mpa_vehiculos v ON tm.placa = v.placa
        LEFT JOIN recurso_operativo ro ON tm.tecnico_asignado = ro.id_codigo_consumidor
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
    """API para obtener todas las licencias de conducir"""
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
        
        query = """
        SELECT 
            lc.id_mpa_licencia_conducir as id,
            lc.tecnico as tecnico_id,
            lc.tipo_licencia,
            lc.fecha_inicio as fecha_inicial,
            lc.fecha_vencimiento,
            lc.observacion as observaciones,
            lc.fecha_creacion as created_at,
            lc.fecha_actualizacion as updated_at,
            COALESCE(ro.nombre, lc.tecnico) as tecnico_nombre,
            DATEDIFF(lc.fecha_vencimiento, %s) as dias_vencimiento
        FROM mpa_licencia_conducir lc
        LEFT JOIN recurso_operativo ro ON lc.tecnico = ro.id_codigo_consumidor
        ORDER BY lc.fecha_vencimiento ASC
        """
        
        cursor.execute(query, (fecha_bogota,))
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
        
        query = """
        SELECT 
            lc.id_mpa_licencia_conducir as id,
            lc.tecnico as tecnico_id,
            lc.tipo_licencia,
            lc.fecha_inicio as fecha_inicial,
            lc.fecha_vencimiento,
            lc.observacion as observaciones,
            lc.fecha_creacion as created_at,
            lc.fecha_actualizacion as updated_at,
            COALESCE(ro.nombre, lc.tecnico) as tecnico_nombre,
            DATEDIFF(lc.fecha_vencimiento, %s) as dias_vencimiento
        FROM mpa_licencia_conducir lc
        LEFT JOIN recurso_operativo ro ON lc.tecnico = ro.id_codigo_consumidor
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



class Asignacion(db.Model):
    id_asignacion = db.Column(db.Integer, primary_key=True)
    id_codigo_consumidor = db.Column(db.String(50))
    fecha = db.Column(db.DateTime)
    cargo = db.Column(db.String(100))
    asignacion_firma = db.Column(db.Text)
    id_asignador = db.Column(db.Integer)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
