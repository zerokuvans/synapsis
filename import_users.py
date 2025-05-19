import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import bcrypt
import csv
from datetime import datetime

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT'))
}

def import_users_from_csv(csv_file):
    try:
        # Crear conexión
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Contadores para estadísticas
        total_users = 0
        successful_imports = 0
        failed_imports = 0
        
        # Leer el archivo CSV con punto y coma como separador
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, delimiter=';')
            
            for row in csv_reader:
                total_users += 1
                try:
                    # Mapear los campos del CSV a los nombres esperados
                    user_data = {
                        'cedula': row['recurso_operativo_cedula'],
                        'password': row['recurso_operativo_password'],
                        'rol': row['id_roles'],
                        'nombre': row['nombre'],
                        'cargo': row['cargo'],
                        'estado': row.get('estado', 'Activo')
                    }
                    
                    # Verificar si el usuario ya existe
                    cursor.execute("SELECT id_codigo_consumidor FROM recurso_operativo WHERE recurso_operativo_cedula = %s", 
                                 (user_data['cedula'],))
                    if cursor.fetchone():
                        print(f"Error: El usuario con cédula {user_data['cedula']} ya existe")
                        failed_imports += 1
                        continue
                    
                    # Generar hash de la contraseña
                    salt = bcrypt.gensalt()
                    hashed_password = bcrypt.hashpw(user_data['password'].encode('utf-8'), salt).decode('utf-8')
                    
                    # Insertar usuario
                    cursor.execute("""
                        INSERT INTO recurso_operativo 
                        (recurso_operativo_cedula, recurso_operativo_password, id_roles, nombre, cargo, estado)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        user_data['cedula'],
                        hashed_password,
                        user_data['rol'],
                        user_data['nombre'],
                        user_data['cargo'],
                        user_data['estado']
                    ))
                    
                    successful_imports += 1
                    print(f"Usuario {user_data['nombre']} importado exitosamente")
                    
                except Error as e:
                    print(f"Error al importar usuario {row.get('nombre', 'desconocido')}: {str(e)}")
                    failed_imports += 1
                    continue
        
        connection.commit()
        
        # Imprimir resumen
        print("\nResumen de la importación:")
        print(f"Total de usuarios en el CSV: {total_users}")
        print(f"Importaciones exitosas: {successful_imports}")
        print(f"Importaciones fallidas: {failed_imports}")
        
        return True
        
    except Error as e:
        print(f"Error de conexión a la base de datos: {e}")
        return False
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    csv_file = "usuarios.csv"
    
    if not os.path.exists(csv_file):
        print(f"Error: El archivo {csv_file} no existe")
        exit(1)
    
    print("Iniciando importación de usuarios...")
    confirm = input("¿Está seguro de continuar con la importación? (s/n): ")
    
    if confirm.lower() == 's':
        if import_users_from_csv(csv_file):
            print("\nProceso de importación completado.")
        else:
            print("\nError durante el proceso de importación.")
    else:
        print("Operación cancelada.") 