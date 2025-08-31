#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el login del usuario 1019112308
"""

import os
import mysql.connector
from mysql.connector import Error
import bcrypt
import requests
import json

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        # Usar la misma configuración que main.py
        db_config = {
            'host': os.getenv('MYSQL_HOST'),
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DB'),
            'port': int(os.getenv('MYSQL_PORT')),
            'time_zone': '+00:00'
        }
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def verificar_login_directo(username, password):
    """Verificar login directamente en la base de datos"""
    print(f"\n=== VERIFICACIÓN DIRECTA DE LOGIN PARA {username} ===")
    
    connection = get_db_connection()
    if not connection:
        print("Error: No se pudo conectar a la base de datos")
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Buscar usuario
        print(f"1. Buscando usuario con cedula: {username}")
        cursor.execute(
            "SELECT id_codigo_consumidor, id_roles, recurso_operativo_password, nombre, estado FROM recurso_operativo WHERE recurso_operativo_cedula = %s", 
            (username,)
        )
        user_data = cursor.fetchone()
        
        if not user_data:
            print("   ❌ Usuario no encontrado")
            return False
        
        print(f"   ✅ Usuario encontrado: {user_data['nombre']}")
        print(f"   📊 Estado: '{user_data['estado']}'")
        print(f"   🔑 ID Rol: {user_data['id_roles']}")
        
        # Verificar estado
        print(f"\n2. Verificando estado del usuario")
        if user_data['estado'] != 'Activo':
            print(f"   ❌ Usuario inactivo - Estado: '{user_data['estado']}'")
            print(f"   🚫 El login debería ser rechazado")
            return False
        else:
            print(f"   ✅ Usuario activo - Estado: '{user_data['estado']}'")
        
        # Verificar contraseña
        print(f"\n3. Verificando contraseña")
        stored_password = user_data['recurso_operativo_password']
        
        # Asegurar que stored_password es bytes
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        
        # Verificar formato del hash
        if not stored_password.startswith(b'$2b$') and not stored_password.startswith(b'$2a$'):
            print(f"   ❌ Formato de contraseña inválido")
            return False
        
        # Verificar contraseña
        password_bytes = password.encode('utf-8')
        if bcrypt.checkpw(password_bytes, stored_password):
            print(f"   ✅ Contraseña correcta")
            print(f"\n🎉 LOGIN EXITOSO - El usuario debería poder acceder")
            return True
        else:
            print(f"   ❌ Contraseña incorrecta")
            return False
            
    except Error as e:
        print(f"Error en la consulta: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def test_login_endpoint(username, password):
    """Probar el endpoint de login via HTTP"""
    print(f"\n=== PRUEBA DEL ENDPOINT DE LOGIN ===")
    
    try:
        # Datos del formulario
        data = {
            'username': username,
            'password': password
        }
        
        # Hacer la petición POST al endpoint de login
        response = requests.post('http://localhost:5000/', data=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        # Intentar parsear como JSON
        try:
            json_response = response.json()
            print(f"JSON Response: {json.dumps(json_response, indent=2)}")
        except:
            print(f"HTML/Text Response: {response.text[:500]}...")
            
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. ¿Está ejecutándose main.py?")
        return False
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return False

def main():
    username = "1019112308"
    password = "CE1019112308"  # Contraseña por defecto según el CSV
    
    print("=" * 60)
    print("PRUEBA DE LOGIN PARA USUARIO 1019112308")
    print("=" * 60)
    
    # Verificación directa en base de datos
    db_result = verificar_login_directo(username, password)
    
    # Prueba del endpoint HTTP
    http_result = test_login_endpoint(username, password)
    
    print("\n" + "=" * 60)
    print("RESUMEN DE RESULTADOS")
    print("=" * 60)
    print(f"Verificación directa en BD: {'✅ EXITOSA' if db_result else '❌ FALLIDA'}")
    print(f"Prueba endpoint HTTP: {'✅ EXITOSA' if http_result else '❌ FALLIDA'}")
    
    if db_result and not http_result:
        print("\n🔍 DISCREPANCIA DETECTADA:")
        print("   - La verificación directa en BD es exitosa")
        print("   - Pero el endpoint HTTP falla")
        print("   - Esto indica un problema en el código del endpoint")
    elif not db_result and http_result:
        print("\n🔍 DISCREPANCIA DETECTADA:")
        print("   - La verificación directa en BD falla")
        print("   - Pero el endpoint HTTP es exitoso")
        print("   - Esto indica un problema en la validación de estado")
    elif db_result and http_result:
        print("\n✅ AMBAS PRUEBAS EXITOSAS:")
        print("   - El usuario puede hacer login correctamente")
        print("   - Si el usuario reporta que no puede, revisar otros factores")
    else:
        print("\n❌ AMBAS PRUEBAS FALLIDAS:")
        print("   - Confirma que el usuario no puede hacer login")

if __name__ == "__main__":
    main()