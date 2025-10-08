import mysql.connector
import sys
import os

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotaciones_api import get_db_connection

def obtener_ids_validos():
    """Obtener IDs válidos de recurso_operativo"""
    connection = get_db_connection()
    if not connection:
        print("❌ Error de conexión a la base de datos")
        return []
    
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT id_codigo_consumidor, nombre FROM recurso_operativo LIMIT 5')
        resultados = cursor.fetchall()
        
        print("IDs disponibles en recurso_operativo:")
        for id_codigo, nombre in resultados:
            print(f"  ID: {id_codigo}, Nombre: {nombre}")
        
        return [row[0] for row in resultados]
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        connection.close()

if __name__ == "__main__":
    ids = obtener_ids_validos()
    if ids:
        print(f"\nPrimer ID válido para usar en pruebas: {ids[0]}")