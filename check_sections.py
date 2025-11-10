#!/usr/bin/env python3
"""
Script para verificar el estado de las secciones y preguntas en la base de datos
"""

import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos - usando la misma configuración que encuestas_api.py
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
    'autocommit': True
}

def check_database():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Obtener encuestas recientes
            cursor.execute('SELECT id_encuesta, titulo FROM encuestas ORDER BY id_encuesta DESC LIMIT 5')
            encuestas = cursor.fetchall()
            
            print('=== ENCUESTAS ENCONTRADAS ===')
            for enc in encuestas:
                print(f'ID: {enc["id_encuesta"]}, Título: {enc["titulo"]}')
                
                # Verificar secciones
                cursor.execute('SELECT id_seccion, titulo, orden FROM encuesta_secciones WHERE encuesta_id = %s ORDER BY orden', 
                             (enc['id_encuesta'],))
                secciones = cursor.fetchall()
                
                print(f'  Secciones encontradas: {len(secciones)}')
                for sec in secciones:
                    print(f'    - ID: {sec["id_seccion"]}, Título: {sec["titulo"]}, Orden: {sec["orden"]}')
                
                # Verificar preguntas
                cursor.execute('SELECT id_pregunta, texto, seccion_id FROM encuesta_preguntas WHERE encuesta_id = %s ORDER BY orden', 
                             (enc['id_encuesta'],))
                preguntas = cursor.fetchall()
                
                preguntas_con_seccion = [p for p in preguntas if p['seccion_id']]
                print(f'  Preguntas totales: {len(preguntas)}, Con sección: {len(preguntas_con_seccion)}')
                
                for p in preguntas:
                    seccion_info = f"Sección ID: {p['seccion_id']}" if p['seccion_id'] else "Sin sección"
                    print(f'    - Pregunta ID: {p["id_pregunta"]}, {seccion_info}')
                
                print('-' * 50)
            
    except Error as e:
        print(f'Error de conexión a la base de datos: {e}')
    finally:
        if connection and connection.is_connected():
            connection.close()

if __name__ == '__main__':
    check_database()