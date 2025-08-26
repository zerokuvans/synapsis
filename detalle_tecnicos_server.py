#!/usr/bin/env python3
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import os
import logging
import traceback

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Función para establecer conexión a la base de datos
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASS', ''),
            database=os.environ.get('DB_NAME', 'capired')
        )
        return connection
    except Error as e:
        print(f"Error de conexión a la base de datos: {e}")
        return None

# Decorador simple de login_required para simulación
def login_required(role=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            # En este servidor de prueba, no validamos autenticación
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Endpoint para obtener detalle de técnicos
@app.route('/api/indicadores/detalle_tecnicos')
@login_required(role='administrativo')
def obtener_detalle_tecnicos():
    try:
        # Obtener parámetros
        fecha = request.args.get('fecha')
        supervisor = request.args.get('supervisor')
        
        print(f"Parámetros recibidos - fecha: {fecha}, supervisor: {supervisor}")
        
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
        
        # Registrar resultado para depuración
        print(f"Se encontraron {len(result_tecnicos)} técnicos asignados al supervisor {supervisor}")
        
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

# Ruta raíz para verificar que el servidor está funcionando
@app.route('/')
def index():
    return jsonify({
        'status': 'online',
        'message': 'Servidor de detalle_tecnicos funcionando',
        'endpoints': [
            {
                'path': '/api/indicadores/detalle_tecnicos',
                'method': 'GET',
                'params': ['fecha', 'supervisor'],
                'description': 'Obtiene detalle de técnicos por supervisor y fecha'
            }
        ]
    })

if __name__ == '__main__':
    # Usar un puerto diferente para evitar conflictos
    app.run(debug=True, host='0.0.0.0', port=8081) 