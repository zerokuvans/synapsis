import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def test_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB'),
            port=int(os.getenv('MYSQL_PORT'))
        )
        
        if connection.is_connected():
            print("¡Conexión exitosa!")
            cursor = connection.cursor()
            
            # Verificar si la base de datos existe
            cursor.execute("SHOW DATABASES LIKE 'capired'")
            if cursor.fetchone():
                print("Base de datos 'capired' existe")
                
                # Verificar si la tabla existe
                cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
                if cursor.fetchone():
                    print("Tabla 'recurso_operativo' existe")
                else:
                    print("Tabla 'recurso_operativo' NO existe")
                    
                    # Crear la tabla si no existe
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS recurso_operativo (
                        id_codigo_consumidor INT AUTO_INCREMENT PRIMARY KEY,
                        recurso_operativo_cedula VARCHAR(20) NOT NULL UNIQUE,
                        recurso_operativo_password VARCHAR(255) NOT NULL,
                        id_roles INT NOT NULL
                    )
                    """)
                    print("Tabla 'recurso_operativo' creada")
            else:
                print("Base de datos 'capired' NO existe")
                cursor.execute("CREATE DATABASE capired")
                print("Base de datos 'capired' creada")
            
            cursor.close()
            connection.close()
            
    except mysql.connector.Error as error:
        print(f"Error de conexión: {error}")

if __name__ == "__main__":
    test_connection() 