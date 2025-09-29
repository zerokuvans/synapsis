#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error
import bcrypt

def verificar_todos_usuarios():
    """Verificar contraseñas de todos los usuarios"""
    try:
        # Configuración de la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@',
            port=3306
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            print("=== VERIFICANDO CONTRASEÑAS DE TODOS LOS USUARIOS ===")
            cursor.execute("""
                SELECT 
                    id_codigo_consumidor,
                    recurso_operativo_cedula,
                    nombre,
                    recurso_operativo_password,
                    estado,
                    id_roles
                FROM recurso_operativo 
                WHERE estado = 'Activo'
                LIMIT 5
            """)
            
            usuarios = cursor.fetchall()
            
            passwords_to_test = ['admin', '123456', '12345', 'password', 'capired', '1234']
            
            for usuario in usuarios:
                print(f"\n{'='*60}")
                print(f"Usuario: {usuario['nombre']}")
                print(f"Cédula: {usuario['recurso_operativo_cedula']}")
                print(f"Rol ID: {usuario['id_roles']}")
                
                password = usuario['recurso_operativo_password']
                if password:
                    print("Tiene contraseña: SÍ")
                    
                    # Verificar si es un hash bcrypt válido
                    if isinstance(password, str):
                        password_bytes = password.encode('utf-8')
                    else:
                        password_bytes = password
                        
                    if password_bytes.startswith(b'$2b$') or password_bytes.startswith(b'$2a$'):
                        print("Formato: bcrypt válido")
                        
                        # Probar contraseñas comunes
                        for test_password in passwords_to_test:
                            try:
                                if bcrypt.checkpw(test_password.encode('utf-8'), password_bytes):
                                    print(f"\n🎉 CONTRASEÑA ENCONTRADA para {usuario['recurso_operativo_cedula']}: '{test_password}'")
                                    print(f"Usuario: {usuario['nombre']}")
                                    print(f"Rol: {usuario['id_roles']}")
                                    return usuario['recurso_operativo_cedula'], test_password
                            except Exception as e:
                                continue
                        print("No se encontró contraseña común")
                    else:
                        print("Formato: NO es bcrypt válido")
                else:
                    print("Tiene contraseña: NO")
                
    except Error as e:
        print(f"Error de MySQL: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada")
    
    return None, None

if __name__ == "__main__":
    cedula, password = verificar_todos_usuarios()
    if cedula and password:
        print(f"\n✅ CREDENCIALES ENCONTRADAS:")
        print(f"Usuario: {cedula}")
        print(f"Contraseña: {password}")
    else:
        print("\n❌ No se encontraron credenciales válidas")