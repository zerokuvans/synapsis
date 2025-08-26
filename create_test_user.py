import mysql.connector
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

def create_test_user():
    try:
        # Crear conexión
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Datos del usuario de prueba
        username = "12345678"  # Cédula numérica
        password = "admin123"
        role_id = 1  # rol administrativo
        
        # Hashear la contraseña
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insertar usuario
        cursor.execute("""
        INSERT INTO recurso_operativo 
        (recurso_operativo_cedula, recurso_operativo_password, id_roles) 
        VALUES (%s, %s, %s)
        """, (username, hashed_password, role_id))
        
        connection.commit()
        print("Usuario de prueba creado exitosamente!")
        print(f"Username (Cédula): {username}")
        print(f"Password: {password}")
        
    except mysql.connector.Error as error:
        print(f"Error: {error}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_test_user() 