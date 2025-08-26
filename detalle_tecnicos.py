from flask import jsonify, request
from datetime import datetime
import traceback

def obtener_detalle_tecnicos(app, get_db_connection, login_required):
    """
    Crea y registra el endpoint para obtener detalles de técnicos por supervisor y fecha.
    """
    @app.route('/api/indicadores/detalle_tecnicos')
    @login_required(role='administrativo')
    def endpoint_detalle_tecnicos():
        try:
            # Obtener parámetros
            fecha = request.args.get('fecha')
            supervisor = request.args.get('supervisor')
            
            if not fecha or not supervisor:
                return jsonify({
                    'success': False,
                    'error': 'Se requieren los parámetros fecha y supervisor'
                }), 400
                
            # Validar fecha
            try:
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }), 400
                
            print(f"Consultando detalle de técnicos para supervisor {supervisor} en fecha {fecha}")
            
            connection = get_db_connection()
            if connection is None:
                print("Error: No se pudo establecer conexión a la base de datos")
                return jsonify({
                    'success': False,
                    'error': 'Error de conexión a la base de datos'
                }), 500
                
            cursor = connection.cursor(dictionary=True)
            
            # Obtener lista de técnicos asignados al supervisor
            query_tecnicos = """
                SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula as documento
                FROM recurso_operativo
                WHERE super = %s AND estado = 'Activo'
            """
            
            cursor.execute(query_tecnicos, (supervisor,))
            tecnicos = cursor.fetchall()
            
            if not tecnicos:
                return jsonify({
                    'success': True,
                    'tecnicos': [],
                    'mensaje': f'No se encontraron técnicos asignados al supervisor {supervisor}'
                })
                
            # Para cada técnico, verificar si tiene asistencia y preoperacional en la fecha indicada
            result_tecnicos = []
            for tecnico in tecnicos:
                id_tecnico = tecnico['id_codigo_consumidor']
                
                # Verificar asistencia
                cursor.execute("""
                    SELECT a.id_asistencia, a.fecha_asistencia 
                    FROM asistencia a
                    JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
                    WHERE a.id_codigo_consumidor = %s 
                    AND DATE(a.fecha_asistencia) = %s 
                    AND t.valor = '1'
                """, (id_tecnico, fecha_obj))
                
                asistencia = cursor.fetchone()
                tiene_asistencia = asistencia is not None
                
                # Verificar preoperacional
                cursor.execute("""
                    SELECT id_preoperacional, fecha
                    FROM preoperacional
                    WHERE id_codigo_consumidor = %s AND DATE(fecha) = %s
                """, (id_tecnico, fecha_obj))
                
                preoperacional = cursor.fetchone()
                tiene_preoperacional = preoperacional is not None
                
                # Formatear hora de registro
                hora_registro = None
                if asistencia:
                    hora_asistencia = asistencia['fecha_asistencia']
                    if hora_asistencia:
                        hora_registro = hora_asistencia.strftime('%H:%M:%S')
                
                # Agregar a los resultados
                result_tecnicos.append({
                    'id': id_tecnico,
                    'nombre': tecnico['nombre'],
                    'documento': tecnico['documento'],
                    'asistencia': tiene_asistencia,
                    'preoperacional': tiene_preoperacional,
                    'hora_registro': hora_registro
                })
                
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'tecnicos': result_tecnicos,
                'fecha': fecha,
                'supervisor': supervisor,
                'total': len(result_tecnicos)
            })
            
        except Exception as e:
            print(f"Error al obtener detalle de técnicos: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    return endpoint_detalle_tecnicos
