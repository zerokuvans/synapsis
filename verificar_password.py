import mysql.connector
from mysql.connector import Error
import bcrypt

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def verificar_password():
    """Verificar la contraseña del usuario test123"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        print("=== VERIFICACIÓN DE CONTRASEÑA PARA test123 ===")
        print()
        
        # Buscar el usuario test123
        cursor.execute("""
            SELECT recurso_operativo_cedula, recurso_operativo_password, nombre, id_roles, estado 
            FROM recurso_operativo 
            WHERE recurso_operativo_cedula = 'test123'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"Usuario encontrado: {result['nombre']}")
            print(f"Rol: {result['id_roles']}")
            print(f"Estado: {result['estado']}")
            
            # Probar contraseñas comunes
            passwords_to_test = ['test123', 'admin', '123456', 'password', 'test']
            stored_password = result['recurso_operativo_password']
            
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            
            print(f"Hash almacenado: {stored_password[:50]}...")
            print()
            print("Probando contraseñas comunes:")
            
            for password in passwords_to_test:
                try:
                    if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                        print(f"   ✓ Contraseña correcta: {password}")
                        break
                    else:
                        print(f"   ✗ Contraseña incorrecta: {password}")
                except Exception as e:
                    print(f"   ✗ Error al verificar {password}: {e}")
            
        else:
            print("Usuario test123 no encontrado")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")

if __name__ == "__main__":
    verificar_password()