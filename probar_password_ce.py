#!/usr/bin/env python3
import mysql.connector
import bcrypt

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def probar_password_ce():
    """Probar la contraseña CE1002407090 para la analista"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Buscar el analista ESPITIA BARON LICED JOANA
        cedula = "1002407090"
        cursor.execute("""
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula,
                recurso_operativo_password,
                nombre,
                estado
            FROM recurso_operativo 
            WHERE recurso_operativo_cedula = %s
        """, (cedula,))
        
        user_data = cursor.fetchone()
        
        if not user_data:
            print(f"❌ Usuario con cédula {cedula} no encontrado")
            return False
        
        print(f"✅ Usuario encontrado: {user_data['nombre']}")
        
        stored_password = user_data['recurso_operativo_password']
        
        # Probar la contraseña CE1002407090
        password_to_test = "CE1002407090"
        
        # Asegurar que stored_password es bytes
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        
        password_bytes = password_to_test.encode('utf-8')
        
        try:
            if bcrypt.checkpw(password_bytes, stored_password):
                print(f"✅ ¡CONTRASEÑA CORRECTA! '{password_to_test}'")
                print(f"   Usuario: {cedula}")
                print(f"   Contraseña: {password_to_test}")
                return True
            else:
                print(f"❌ La contraseña '{password_to_test}' no coincide")
                return False
        except Exception as e:
            print(f"⚠️  Error probando la contraseña: {e}")
            return False
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return False
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    print("🔐 PROBANDO CONTRASEÑA CE1002407090")
    print("=" * 40)
    
    if probar_password_ce():
        print(f"\n🎉 ¡Credenciales válidas confirmadas!")
    else:
        print(f"\n❌ La contraseña no es correcta")