import mysql.connector
import os
from mysql.connector import Error
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'synapsis'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'time_zone': '+00:00'
}

def verificar_tablas():
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        print("=== VERIFICACIÓN DE TABLAS EN MYSQL ===")
        print(f"Base de datos: {db_config['database']}")
        print(f"Host: {db_config['host']}")
        print(f"Puerto: {db_config['port']}")
        print()
        
        # Listar todas las tablas
        cursor.execute("SHOW TABLES")
        tablas = cursor.fetchall()
        
        print(f"Total de tablas encontradas: {len(tablas)}")
        print()
        
        # Verificar tablas específicas del sistema de devoluciones
        tablas_importantes = [
            'devoluciones_dotacion',
            'historial_estados_devolucion',
            'permisos_transicion',
            'recurso_operativo',
            'usuarios'
        ]
        
        print("=== VERIFICACIÓN DE TABLAS ESPECÍFICAS ===")
        for tabla in tablas_importantes:
            cursor.execute(f"SHOW TABLES LIKE '{tabla}'")
            resultado = cursor.fetchone()
            if resultado:
                print(f"✓ {tabla} - EXISTE")
                
                # Mostrar estructura de la tabla
                cursor.execute(f"DESCRIBE {tabla}")
                columnas = cursor.fetchall()
                print(f"  Columnas ({len(columnas)}):")
                for columna in columnas:
                    print(f"    - {columna[0]} ({columna[1]})")
                print()
            else:
                print(f"✗ {tabla} - NO EXISTE")
        
        print("\n=== TODAS LAS TABLAS ===")
        for tabla in tablas:
            print(f"- {tabla[0]}")
            
    except Error as e:
        print(f"Error de conexión a MySQL: {e}")
    finally:
        if connection and connection.is_connected():
            if cursor:
                cursor.close()
            connection.close()

if __name__ == "__main__":
    verificar_tablas()