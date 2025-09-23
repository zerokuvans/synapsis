import mysql.connector
import bcrypt
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT')),
    'time_zone': '+00:00'
}

def verificar_password_usuario():
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Buscar el usuario de prueba
        cedula = '12345678'
        cursor.execute("""
            SELECT id_codigo_consumidor, recurso_operativo_cedula, 
                   recurso_operativo_password, nombre, estado, id_roles
            FROM recurso_operativo 
            WHERE recurso_operativo_cedula = %s
        """, (cedula,))
        
        usuario = cursor.fetchone()
        
        if usuario:
            print(f"Usuario encontrado:")
            print(f"  ID: {usuario['id_codigo_consumidor']}")
            print(f"  Cédula: {usuario['recurso_operativo_cedula']}")
            print(f"  Nombre: {usuario['nombre']}")
            print(f"  Estado: {usuario['estado']}")
            print(f"  Rol ID: {usuario['id_roles']}")
            
            # Verificar el hash de la contraseña
            stored_password = usuario['recurso_operativo_password']
            print(f"\nHash almacenado: {stored_password[:50]}...")
            
            # Probar la contraseña 'password123'
            test_password = 'password123'.encode('utf-8')
            
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            
            try:
                if bcrypt.checkpw(test_password, stored_password):
                    print("✅ La contraseña 'password123' es correcta")
                else:
                    print("❌ La contraseña 'password123' NO es correcta")
                    
                    # Intentar generar un nuevo hash para 'password123'
                    print("\nGenerando nuevo hash para 'password123'...")
                    new_hash = bcrypt.hashpw(test_password, bcrypt.gensalt())
                    
                    # Actualizar la contraseña en la base de datos
                    cursor.execute("""
                        UPDATE recurso_operativo 
                        SET recurso_operativo_password = %s 
                        WHERE recurso_operativo_cedula = %s
                    """, (new_hash.decode('utf-8'), cedula))
                    
                    connection.commit()
                    print("✅ Contraseña actualizada correctamente")
                    
            except Exception as e:
                print(f"❌ Error al verificar contraseña: {e}")
        else:
            print(f"❌ Usuario con cédula {cedula} no encontrado")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verificar_password_usuario()