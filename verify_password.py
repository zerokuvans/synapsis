#!/usr/bin/env python3
"""
Script para verificar la contraseña del usuario 1019112308
"""

import mysql.connector
import bcrypt

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        return connection
    except mysql.connector.Error as e:
        print(f'Error al conectar a la base de datos: {e}')
        return None

def verify_password():
    """Verificar la contraseña del usuario"""
    
    connection = get_db_connection()
    if not connection:
        print('No se pudo conectar a la base de datos')
        return
    
    cursor = connection.cursor()
    
    print('=== VERIFICANDO CONTRASEÑA DEL USUARIO 1019112308 ===\n')
    
    # Obtener la contraseña hasheada del usuario
    try:
        cursor.execute("SELECT recurso_operativo_password FROM recurso_operativo WHERE recurso_operativo_cedula = %s", ('1019112308',))
        result = cursor.fetchone()
        
        if result:
            stored_password = result[0]
            print(f'Contraseña almacenada (hash): {stored_password}')
            
            # Probar diferentes contraseñas posibles
            test_passwords = ['123456', 'password', '1019112308', 'admin', 'test']
            
            for test_pass in test_passwords:
                try:
                    # Convertir a bytes si es necesario
                    if isinstance(stored_password, str):
                        stored_password_bytes = stored_password.encode('utf-8')
                    else:
                        stored_password_bytes = stored_password
                    
                    test_pass_bytes = test_pass.encode('utf-8')
                    
                    if bcrypt.checkpw(test_pass_bytes, stored_password_bytes):
                        print(f'✅ CONTRASEÑA CORRECTA: "{test_pass}"')
                        return test_pass
                    else:
                        print(f'❌ Contraseña incorrecta: "{test_pass}"')
                        
                except Exception as e:
                    print(f'Error verificando contraseña "{test_pass}": {e}')
            
            print('\n⚠️  Ninguna de las contraseñas de prueba funcionó')
            
        else:
            print('Usuario no encontrado')
    
    except mysql.connector.Error as e:
        print(f'Error: {e}')
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    verify_password()