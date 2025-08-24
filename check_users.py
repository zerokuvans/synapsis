import mysql.connector
from mysql.connector import Error
import bcrypt

def check_users():
    print("=== Verificando usuarios en la base de datos ===")
    
    try:
        # Configuración de la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Obtener todos los usuarios
            cursor.execute("""
                SELECT 
                    id_codigo_consumidor,
                    recurso_operativo_cedula,
                    nombre,
                    id_roles,
                    recurso_operativo_password
                FROM recurso_operativo 
                LIMIT 5
            """)
            
            users = cursor.fetchall()
            
            print(f"\nTotal de usuarios encontrados: {len(users)}")
            print("\nPrimeros 5 usuarios:")
            
            for user in users:
                print(f"ID: {user['id_codigo_consumidor']}")
                print(f"Cédula: {user['recurso_operativo_cedula']}")
                print(f"Nombre: {user['nombre']}")
                print(f"Rol ID: {user['id_roles']}")
                print(f"Password Hash: {user['recurso_operativo_password'][:50]}...")
                print("-" * 50)
            
            # Crear un usuario de prueba si no existe
            test_cedula = '1234567890'
            cursor.execute("SELECT * FROM recurso_operativo WHERE recurso_operativo_cedula = %s", (test_cedula,))
            existing_user = cursor.fetchone()
            
            if not existing_user:
                print(f"\nCreando usuario de prueba con cédula: {test_cedula}")
                
                # Generar hash de contraseña
                password = 'password123'
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
                
                cursor.execute("""
                    INSERT INTO recurso_operativo 
                    (recurso_operativo_cedula, recurso_operativo_password, nombre, id_roles) 
                    VALUES (%s, %s, %s, %s)
                """, (test_cedula, hashed_password, 'Usuario Prueba', 2))
                
                connection.commit()
                print("✓ Usuario de prueba creado exitosamente")
                print(f"Cédula: {test_cedula}")
                print(f"Contraseña: {password}")
            else:
                print(f"\nUsuario de prueba ya existe:")
                print(f"Cédula: {existing_user['recurso_operativo_cedula']}")
                print(f"Nombre: {existing_user['nombre']}")
                
                # Verificar si la contraseña 'password123' funciona
                stored_password = existing_user['recurso_operativo_password']
                if isinstance(stored_password, str):
                    stored_password = stored_password.encode('utf-8')
                
                test_password = 'password123'.encode('utf-8')
                if bcrypt.checkpw(test_password, stored_password):
                    print("✓ La contraseña 'password123' es válida para este usuario")
                else:
                    print("✗ La contraseña 'password123' NO es válida para este usuario")
                    print("Actualizando contraseña...")
                    
                    # Actualizar contraseña
                    salt = bcrypt.gensalt()
                    new_hashed = bcrypt.hashpw(test_password, salt).decode('utf-8')
                    
                    cursor.execute(
                        "UPDATE recurso_operativo SET recurso_operativo_password = %s WHERE recurso_operativo_cedula = %s",
                        (new_hashed, test_cedula)
                    )
                    connection.commit()
                    print("✓ Contraseña actualizada a 'password123'")
            
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"Error de MySQL: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users()