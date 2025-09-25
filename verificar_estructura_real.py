import mysql.connector
import os
from mysql.connector import Error
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT')),
    'time_zone': '+00:00'
}

def verificar_estructura_tablas():
    """Verifica la estructura real de las tablas importantes"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        tablas_importantes = [
            'devoluciones_dotacion',
            'permisos_transicion', 
            'recurso_operativo',
            'usuarios'
        ]
        
        for tabla in tablas_importantes:
            print(f"\n=== ESTRUCTURA DE {tabla.upper()} ===")
            cursor.execute(f"DESCRIBE {tabla}")
            columnas = cursor.fetchall()
            
            for columna in columnas:
                field, type_, null, key, default, extra = columna
                print(f"  {field:<20} {type_:<15} {null:<5} {key:<5} {str(default):<10} {extra}")
        
        # Verificar datos de permisos_transicion
        print(f"\n=== DATOS EN PERMISOS_TRANSICION ===")
        cursor.execute("SELECT * FROM permisos_transicion LIMIT 5")
        permisos = cursor.fetchall()
        
        # Obtener nombres de columnas
        cursor.execute("DESCRIBE permisos_transicion")
        columnas_info = cursor.fetchall()
        nombres_columnas = [col[0] for col in columnas_info]
        
        print("Columnas:", nombres_columnas)
        print("Primeros 5 registros:")
        for permiso in permisos:
            print("  ", permiso)
        
        connection.close()
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verificar_estructura_tablas()