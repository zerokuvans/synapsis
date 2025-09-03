import mysql.connector
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'capired'),
            port=int(os.getenv('MYSQL_PORT', 3306))
        )
        return connection
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def verificar_usuarios():
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Obtener algunos usuarios activos
        cursor.execute("""
            SELECT 
                recurso_operativo_cedula,
                nombre,
                id_roles,
                estado
            FROM recurso_operativo 
            WHERE estado = 'Activo'
            LIMIT 5
        """)
        
        usuarios = cursor.fetchall()
        
        print("=== USUARIOS ACTIVOS EN LA BASE DE DATOS ===")
        for usuario in usuarios:
            print(f"Cédula: {usuario['recurso_operativo_cedula']}")
            print(f"Nombre: {usuario['nombre']}")
            print(f"Rol ID: {usuario['id_roles']}")
            print(f"Estado: {usuario['estado']}")
            print("-" * 40)
            
    except Exception as e:
        print(f"Error consultando usuarios: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    verificar_usuarios()