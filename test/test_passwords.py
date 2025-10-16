import mysql.connector
import bcrypt

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def test_passwords():
    """Probar diferentes contraseñas para el usuario 80833959"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Obtener el hash de la contraseña del usuario
        cursor.execute("""
            SELECT recurso_operativo_cedula, nombre, recurso_operativo_password 
            FROM recurso_operativo 
            WHERE recurso_operativo_cedula = '80833959'
        """)
        
        user = cursor.fetchone()
        if not user:
            print("❌ Usuario no encontrado")
            return
        
        print(f"✅ Usuario encontrado: {user['nombre']}")
        print(f"📋 Cédula: {user['recurso_operativo_cedula']}")
        
        stored_password = user['recurso_operativo_password']
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        
        print(f"🔑 Hash almacenado: {stored_password[:50]}...")
        
        # Lista de contraseñas a probar
        passwords_to_test = [
            '80833959',           # La cédula
            '123456',             # Contraseña común
            'admin',              # Admin
            'password',           # Password
            'test123',            # Test
            'CE80833959',         # CE + cédula
            'M4r14l4r@',          # Contraseña vista en otros scripts
            '732137A031E4b@',     # Contraseña de la DB
            'victor',             # Nombre
            'naranjo',            # Apellido
            'VICTOR',             # Nombre en mayúsculas
            'capired',            # Nombre del sistema
            'synapsis',           # Nombre del proyecto
        ]
        
        print(f"\n🔍 Probando {len(passwords_to_test)} contraseñas...")
        
        for i, password in enumerate(passwords_to_test, 1):
            try:
                password_bytes = password.encode('utf-8')
                if bcrypt.checkpw(password_bytes, stored_password):
                    print(f"✅ ¡CONTRASEÑA ENCONTRADA! #{i}: '{password}'")
                    return password
                else:
                    print(f"❌ #{i}: '{password}' - No coincide")
            except Exception as e:
                print(f"⚠️ #{i}: '{password}' - Error: {e}")
        
        print("\n❌ Ninguna contraseña funcionó")
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    password = test_passwords()
    if password:
        print(f"\n🎉 Contraseña válida encontrada: '{password}'")
    else:
        print("\n😞 No se encontró una contraseña válida")