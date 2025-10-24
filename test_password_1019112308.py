import mysql.connector
import bcrypt

def test_password_1019112308():
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
            
            print("=== PROBANDO CONTRASEÑAS PARA USUARIO 1019112308 ===")
            
            # Obtener el hash de la contraseña
            cursor.execute("SELECT recurso_operativo_password FROM recurso_operativo WHERE recurso_operativo_cedula = %s", ('1019112308',))
            result = cursor.fetchone()
            
            if result:
                stored_password = result['recurso_operativo_password']
                print(f"Hash almacenado: {stored_password}")
                
                # Lista de contraseñas a probar
                passwords_to_test = [
                    '123456',           # Contraseña común
                    '1019112308',       # Su cédula
                    'admin',            # Admin
                    'password',         # Password
                    'test123',          # Test
                    'CE1019112308',     # CE + cédula
                    'ALARCON',          # Su apellido
                    'LUIS',             # Su nombre
                    'alarcon123',       # Apellido + números
                    'luis123'           # Nombre + números
                ]
                
                print(f"\nProbando {len(passwords_to_test)} contraseñas...")
                
                for password in passwords_to_test:
                    try:
                        # Convertir a bytes si es necesario
                        if isinstance(stored_password, str):
                            stored_password_bytes = stored_password.encode('utf-8')
                        else:
                            stored_password_bytes = stored_password
                        
                        password_bytes = password.encode('utf-8')
                        
                        if bcrypt.checkpw(password_bytes, stored_password_bytes):
                            print(f"✅ ¡CONTRASEÑA CORRECTA ENCONTRADA! '{password}'")
                            return password
                        else:
                            print(f"❌ '{password}' - Incorrecta")
                            
                    except Exception as e:
                        print(f"⚠️ Error probando '{password}': {e}")
                
                print("\n❌ Ninguna de las contraseñas probadas fue correcta")
                return None
                
            else:
                print("❌ Usuario no encontrado")
                return None
                
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    test_password_1019112308()