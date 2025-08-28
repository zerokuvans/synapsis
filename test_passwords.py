import bcrypt
import mysql.connector
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB')
}

def test_password(username, password):
    """Probar si una contraseña es válida para un usuario"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Obtener el hash de la contraseña del usuario
        cursor.execute("SELECT password_hash FROM recurso_operativo WHERE cedula = %s", (username,))
        result = cursor.fetchone()
        
        if result:
            stored_hash = result[0]
            # Verificar la contraseña
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                return True
        
        cursor.close()
        conn.close()
        return False
        
    except Exception as e:
        print(f"Error al verificar contraseña: {e}")
        return False

# Lista de contraseñas comunes para probar
passwords_to_test = [
    'password123',
    'admin123',
    '123456',
    'capired',
    '80833959',  # Mismo que el username
    'CE80833959',  # Patrón CE + cedula
    '732137A031E4b@',  # La contraseña del .env
    'admin',
    '1234',
    'test123'
]

username = '80833959'
print(f"Probando contraseñas para el usuario {username}:")
print("=" * 50)

for password in passwords_to_test:
    if test_password(username, password):
        print(f"✅ CONTRASEÑA ENCONTRADA: '{password}'")
        break
    else:
        print(f"❌ '{password}' - No válida")
else:
    print("\n❌ Ninguna de las contraseñas probadas es válida")
    print("\nVerificando el hash almacenado...")
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM recurso_operativo WHERE cedula = %s", (username,))
        result = cursor.fetchone()
        if result:
            print(f"Hash almacenado: {result[0][:50]}...")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")