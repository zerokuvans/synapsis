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

def verificar_password_analista():
    """Verificar la contraseña del analista y probar diferentes opciones"""
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
                estado,
                analista
            FROM recurso_operativo 
            WHERE recurso_operativo_cedula = %s
        """, (cedula,))
        
        user_data = cursor.fetchone()
        
        if not user_data:
            print(f"❌ Usuario con cédula {cedula} no encontrado")
            return
        
        print(f"✅ Usuario encontrado:")
        print(f"   ID: {user_data['id_codigo_consumidor']}")
        print(f"   Cédula: {user_data['recurso_operativo_cedula']}")
        print(f"   Nombre: {user_data['nombre']}")
        print(f"   Estado: {user_data['estado']}")
        print(f"   Analista: {user_data['analista']}")
        
        stored_password = user_data['recurso_operativo_password']
        print(f"   Hash almacenado: {stored_password[:50]}...")
        
        # Probar diferentes contraseñas comunes
        passwords_to_test = [
            "123456",
            "1002407090",  # Su cédula
            "admin",
            "password",
            "ESPITIA",
            "liced",
            "joana",
            "analista"
        ]
        
        print(f"\n🔍 Probando contraseñas comunes:")
        
        # Asegurar que stored_password es bytes
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        
        for password in passwords_to_test:
            password_bytes = password.encode('utf-8')
            try:
                if bcrypt.checkpw(password_bytes, stored_password):
                    print(f"   ✅ CONTRASEÑA ENCONTRADA: '{password}'")
                    return password
                else:
                    print(f"   ❌ '{password}' - No coincide")
            except Exception as e:
                print(f"   ⚠️  Error probando '{password}': {e}")
        
        print(f"\n❌ Ninguna de las contraseñas comunes funcionó")
        print(f"💡 Sugerencia: Puede que necesites resetear la contraseña del usuario")
        
        return None
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return None
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

def resetear_password_analista():
    """Resetear la contraseña del analista a '123456'"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        cedula = "1002407090"
        nueva_password = "123456"
        
        # Generar hash de la nueva contraseña
        password_hash = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt())
        
        # Actualizar la contraseña
        cursor.execute("""
            UPDATE recurso_operativo 
            SET recurso_operativo_password = %s 
            WHERE recurso_operativo_cedula = %s
        """, (password_hash.decode('utf-8'), cedula))
        
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Contraseña actualizada exitosamente para cédula {cedula}")
            print(f"   Nueva contraseña: {nueva_password}")
            return True
        else:
            print(f"❌ No se pudo actualizar la contraseña")
            return False
        
    except mysql.connector.Error as e:
        print(f"❌ Error actualizando contraseña: {e}")
        return False
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    print("🔐 VERIFICACIÓN DE CONTRASEÑA DEL ANALISTA")
    print("=" * 50)
    
    # Primero verificar la contraseña actual
    password_encontrada = verificar_password_analista()
    
    if not password_encontrada:
        print(f"\n🔧 ¿Deseas resetear la contraseña a '123456'? (s/n): ", end="")
        respuesta = input().lower().strip()
        
        if respuesta in ['s', 'si', 'y', 'yes']:
            if resetear_password_analista():
                print(f"\n✅ Ahora puedes usar las credenciales:")
                print(f"   Usuario: 1002407090")
                print(f"   Contraseña: 123456")
        else:
            print(f"❌ Operación cancelada")
    else:
        print(f"\n✅ Puedes usar las credenciales:")
        print(f"   Usuario: 1002407090")
        print(f"   Contraseña: {password_encontrada}")