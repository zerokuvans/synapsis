from flask import jsonify, request
from datetime import datetime
import traceback

def register_endpoint(app, get_db_connection, login_required):
    """
    Registra el endpoint /api/indicadores/detalle_tecnicos en la aplicación Flask.
    """
    @app.route('/api/indicadores/detalle_tecnicos', methods=['GET'])
    @login_required
    def obtener_detalle_tecnicos():
        try:
            # Obtener parámetros
            fecha = request.args.get('fecha')
            supervisor = request.args.get('supervisor')
            
            # Validar parámetros
            if not fecha or not supervisor:
                return jsonify({
                    'success': False,
                    'error': 'Parámetros fecha y supervisor son requeridos'
                }), 400
                
            print(f"Consultando detalle de técnicos para supervisor {supervisor} en fecha {fecha}")
            
            # Conectar a la base de datos
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Consultar técnicos activos asignados al supervisor
            query_tecnicos = """
            SELECT id, nombre, apellido
            FROM tecnicos
            WHERE supervisor = %s AND estado = 1
            ORDER BY nombre, apellido
            """
            cursor.execute(query_tecnicos, (supervisor,))
            tecnicos = cursor.fetchall()
            
            resultado = []
            
            for tecnico in tecnicos:
                # Consultar asistencia para el técnico en la fecha
                query_asistencia = """
                SELECT COUNT(*) as tiene_asistencia
                FROM asistencia
                WHERE id_tecnico = %s AND DATE(fecha_registro) = %s
                """
                cursor.execute(query_asistencia, (tecnico['id'], fecha))
                asistencia = cursor.fetchone()
                
                # Consultar preoperacional para el técnico en la fecha
                query_preoperacional = """
                SELECT COUNT(*) as tiene_preoperacional
                FROM preoperacional
                WHERE id_tecnico = %s AND DATE(fecha_registro) = %s
                """
                cursor.execute(query_preoperacional, (tecnico['id'], fecha))
                preoperacional = cursor.fetchone()
                
                # Añadir a resultados
                resultado.append({
                    'id': tecnico['id'],
                    'nombre': f"{tecnico['nombre']} {tecnico['apellido']}",
                    'asistencia': True if asistencia and asistencia['tiene_asistencia'] > 0 else False,
                    'preoperacional': True if preoperacional and preoperacional['tiene_preoperacional'] > 0 else False
                })
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'fecha': fecha,
                'supervisor': supervisor,
                'tecnicos': resultado
            })
            
        except Exception as e:
            print(f"Error en obtener_detalle_tecnicos: {str(e)}")
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return obtener_detalle_tecnicos 