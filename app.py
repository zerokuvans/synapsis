from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
import logging
import pytz
import os
from datetime import date

app = Flask(__name__)
db = SQLAlchemy()

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

class Asignacion(db.Model):
    id_asignacion = db.Column(db.Integer, primary_key=True)
    id_codigo_consumidor = db.Column(db.String(50))
    fecha = db.Column(db.DateTime)
    cargo = db.Column(db.String(100))
    asignacion_firma = db.Column(db.Text)
    id_asignador = db.Column(db.Integer)