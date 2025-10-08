import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT'))
}

def reset_password(username, new_password):
    try:
        # Crear conexión
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Verificar si el usuario existe
        cursor.execute("SELECT id_codigo_consumidor FROM recurso_operativo WHERE recurso_operativo_cedula = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"Error: El usuario {username} no existe en la base de datos.")
            return False
            
        # Generar nuevo hash de contraseña
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
        
        # Actualizar la contraseña
        cursor.execute("""
            UPDATE recurso_operativo 
            SET recurso_operativo_password = %s 
            WHERE recurso_operativo_cedula = %s
        """, (hashed_password, username))
        
        connection.commit()
        print(f"Contraseña actualizada exitosamente para el usuario {username}")
        return True
        
    except Error as e:
        print(f"Error al restablecer la contraseña: {e}")
        return False
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    # Solicitar datos al usuario
    username = input("Ingrese el número de cédula del usuario: ")
    new_password = input("Ingrese la nueva contraseña: ")
    
    # Confirmar la acción
    confirm = input(f"¿Está seguro de restablecer la contraseña para el usuario {username}? (s/n): ")
    
    if confirm.lower() == 's':
        if reset_password(username, new_password):
            print("Proceso completado exitosamente.")
        else:
            print("No se pudo completar el proceso.")
    else:
        print("Operación cancelada.") 