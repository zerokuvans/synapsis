import os
import mysql.connector
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos usando las mismas variables que main.py
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT')),
    'time_zone': '+00:00'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return None

def verificar_estructura():
    print("=== VERIFICACIÓN DE ESTRUCTURA DE TABLAS ===\n")
    
    connection = get_db_connection()
    if not connection:
        print("No se pudo conectar a la base de datos")
        return
    
    cursor = connection.cursor()
    
    try:
        # Verificar si las tablas existen
        print("1. Verificando si las tablas existen:")
        cursor.execute("SHOW TABLES LIKE 'presupuesto_%'")
        tablas_presupuesto = cursor.fetchall()
        
        if tablas_presupuesto:
            print("   Tablas de presupuesto encontradas:")
            for tabla in tablas_presupuesto:
                print(f"     - {tabla[0]}")
        else:
            print("   ✗ No se encontraron tablas de presupuesto")
            
        # Verificar estructura de presupuesto_carpeta
        print("\n2. Estructura de presupuesto_carpeta:")
        try:
            cursor.execute("DESCRIBE presupuesto_carpeta")
            estructura_carpeta = cursor.fetchall()
            if estructura_carpeta:
                print("   Columnas:")
                for col in estructura_carpeta:
                    print(f"     - {col[0]} ({col[1]})")
            else:
                print("   ✗ No se pudo obtener la estructura")
        except mysql.connector.Error as err:
            print(f"   ✗ Error: {err}")
            
        # Verificar estructura de presupuesto_cargo
        print("\n3. Estructura de presupuesto_cargo:")
        try:
            cursor.execute("DESCRIBE presupuesto_cargo")
            estructura_cargo = cursor.fetchall()
            if estructura_cargo:
                print("   Columnas:")
                for col in estructura_cargo:
                    print(f"     - {col[0]} ({col[1]})")
            else:
                print("   ✗ No se pudo obtener la estructura")
        except mysql.connector.Error as err:
            print(f"   ✗ Error: {err}")
            
        # Mostrar contenido de presupuesto_carpeta si existe
        print("\n4. Contenido de presupuesto_carpeta:")
        try:
            cursor.execute("SELECT * FROM presupuesto_carpeta LIMIT 10")
            contenido_carpeta = cursor.fetchall()
            if contenido_carpeta:
                for row in contenido_carpeta:
                    print(f"     - {row}")
            else:
                print("   ✗ Tabla vacía")
        except mysql.connector.Error as err:
            print(f"   ✗ Error: {err}")
            
        # Mostrar contenido de presupuesto_cargo si existe
        print("\n5. Contenido de presupuesto_cargo:")
        try:
            cursor.execute("SELECT * FROM presupuesto_cargo LIMIT 10")
            contenido_cargo = cursor.fetchall()
            if contenido_cargo:
                for row in contenido_cargo:
                    print(f"     - {row}")
            else:
                print("   ✗ Tabla vacía")
        except mysql.connector.Error as err:
            print(f"   ✗ Error: {err}")
        
    except mysql.connector.Error as err:
        print(f"Error general: {err}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    verificar_estructura()