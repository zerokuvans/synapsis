import mysql.connector
from mysql.connector import Error
import bcrypt

def verificar_credenciales():
    try:
        # Configuración de conexión a MySQL
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("=== Verificación de Credenciales de Usuarios Logística ===")
            print()
            
            # Consultar usuarios con rol logística (ID 5)
            query = """
            SELECT 
                id_codigo_consumidor,
                nombre,
                recurso_operativo_cedula,
                recurso_operativo_password,
                estado
            FROM recurso_operativo 
            WHERE id_roles = 5 AND estado = 'Activo'
            ORDER BY id_codigo_consumidor
            """
            
            cursor.execute(query)
            usuarios = cursor.fetchall()
            
            if usuarios:
                print(f"Usuarios activos con rol logística encontrados: {len(usuarios)}")
                print()
                
                for usuario in usuarios:
                    id_codigo, nombre, cedula, password_hash, estado = usuario
                    print(f"ID: {id_codigo}")
                    print(f"Nombre: {nombre}")
                    print(f"Cédula: {cedula}")
                    print(f"Estado: {estado}")
                    print(f"Password Hash: {password_hash[:50] if password_hash else 'N/A'}...")
                    print("-" * 50)
                    
                    # Intentar verificar si la contraseña es simple
                    if password_hash:
                        # Probar contraseñas comunes
                        contraseñas_test = ['123456', 'admin', 'password', cedula, nombre.lower()]
                        for pwd in contraseñas_test:
                            try:
                                if bcrypt.checkpw(pwd.encode('utf-8'), password_hash.encode('utf-8')):
                                    print(f"✓ Contraseña encontrada para {nombre}: {pwd}")
                                    break
                            except:
                                # Si no es bcrypt, podría ser texto plano
                                if password_hash == pwd:
                                    print(f"✓ Contraseña en texto plano para {nombre}: {pwd}")
                                    break
                        else:
                            print(f"✗ No se pudo determinar la contraseña para {nombre}")
                    print()
                    
            else:
                print("No se encontraron usuarios activos con rol logística")
                
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a MySQL cerrada")

if __name__ == "__main__":
    verificar_credenciales()