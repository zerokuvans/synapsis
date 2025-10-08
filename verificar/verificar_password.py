#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error
import bcrypt

def verificar_password_usuario(cedula):
    """Verificar si un usuario tiene contraseña configurada"""
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
            
            print(f"=== VERIFICANDO CONTRASEÑA PARA CÉDULA: {cedula} ===")
            cursor.execute("""
                SELECT 
                    id_codigo_consumidor,
                    recurso_operativo_cedula,
                    nombre,
                    recurso_operativo_password,
                    estado,
                    id_roles
                FROM recurso_operativo 
                WHERE recurso_operativo_cedula = %s
            """, (cedula,))
            
            usuario = cursor.fetchone()
            
            if usuario:
                print(f"\nUsuario encontrado:")
                print(f"ID: {usuario['id_codigo_consumidor']}")
                print(f"Cédula: {usuario['recurso_operativo_cedula']}")
                print(f"Nombre: {usuario['nombre']}")
                print(f"Estado: {usuario['estado']}")
                print(f"Rol ID: {usuario['id_roles']}")
                
                password = usuario['recurso_operativo_password']
                if password:
                    print(f"\nTiene contraseña configurada: SÍ")
                    print(f"Longitud del hash: {len(password)}")
                    
                    # Verificar si es un hash bcrypt válido
                    if isinstance(password, str):
                        password_bytes = password.encode('utf-8')
                    else:
                        password_bytes = password
                        
                    if password_bytes.startswith(b'$2b$') or password_bytes.startswith(b'$2a$'):
                        print("Formato de hash: bcrypt válido")
                        
                        # Probar algunas contraseñas comunes
                        passwords_to_test = ['admin', '123456', '12345', 'password', cedula, 'capired']
                        
                        print("\nProbando contraseñas comunes...")
                        for test_password in passwords_to_test:
                            try:
                                if bcrypt.checkpw(test_password.encode('utf-8'), password_bytes):
                                    print(f"✓ CONTRASEÑA ENCONTRADA: '{test_password}'")
                                    return test_password
                                else:
                                    print(f"✗ '{test_password}' - No coincide")
                            except Exception as e:
                                print(f"✗ '{test_password}' - Error: {e}")
                    else:
                        print("Formato de hash: NO es bcrypt válido")
                        print(f"Primeros 20 caracteres: {password[:20]}")
                else:
                    print(f"\nTiene contraseña configurada: NO")
            else:
                print("Usuario no encontrado")
                
    except Error as e:
        print(f"Error de MySQL: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada")
    
    return None

if __name__ == "__main__":
    # Verificar el usuario administrativo
    verificar_password_usuario('80833959')