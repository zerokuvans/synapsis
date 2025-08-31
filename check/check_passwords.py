import mysql.connector
import bcrypt

def check_passwords():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@'
        )
        
        cursor = connection.cursor(dictionary=True)
        
        print("=== VERIFICANDO CONTRASEÑAS DE USUARIOS OPERATIVOS ===")
        cursor.execute("""
            SELECT recurso_operativo_cedula, nombre, recurso_operativo_password 
            FROM recurso_operativo 
            WHERE id_roles = 3 AND estado = 'Activo'
        """)
        
        users = cursor.fetchall()
        
        test_passwords = ['password123', '123456', 'admin', 'capired', '1234']
        
        for user in users:
            print(f"\nUsuario: {user['nombre']} (Cédula: {user['recurso_operativo_cedula']})")
            print(f"Hash almacenado: {user['recurso_operativo_password'][:50]}...")
            
            stored_password = user['recurso_operativo_password']
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            
            print("Probando contraseñas comunes:")
            for test_pass in test_passwords:
                try:
                    if bcrypt.checkpw(test_pass.encode('utf-8'), stored_password):
                        print(f"  ✓ CONTRASEÑA ENCONTRADA: '{test_pass}'")
                        break
                    else:
                        print(f"  ✗ '{test_pass}' - No coincide")
                except Exception as e:
                    print(f"  ⚠ Error probando '{test_pass}': {e}")
        
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_passwords()