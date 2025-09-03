#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar usuarios con rol logística y crear uno si no existe
"""

import mysql.connector
from mysql.connector import Error
import bcrypt
from dotenv import load_dotenv
import os

load_dotenv()

def conectar_db():
    """Conectar a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            database=os.getenv('MYSQL_DB', 'capired'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )
        return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

def verificar_usuarios_logistica():
    """Verificar usuarios con rol logística"""
    connection = conectar_db()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print("=== VERIFICACIÓN DE USUARIOS LOGÍSTICA ===")
        
        # Verificar estructura de la tabla recurso_operativo
        cursor.execute("DESCRIBE recurso_operativo")
        columns = cursor.fetchall()
        print("\nEstructura de la tabla recurso_operativo:")
        for col in columns:
            print(f"  - {col['Field']}: {col['Type']} ({col['Null']}, {col['Key']})")
        
        # Buscar usuarios con rol logística (id_roles = 5)
        query = """
            SELECT 
                recurso_operativo_cedula,
                nombre,
                id_roles,
                estado
            FROM recurso_operativo 
            WHERE id_roles = 5
        """
        
        cursor.execute(query)
        usuarios_logistica = cursor.fetchall()
        
        print(f"\nUsuarios con rol logística encontrados: {len(usuarios_logistica)}")
        
        if usuarios_logistica:
            for usuario in usuarios_logistica:
                print(f"  - Cédula: {usuario['recurso_operativo_cedula']}")
                print(f"    Nombre: {usuario['nombre']}")
                print(f"    Estado: {usuario['estado']}")
                print()
        else:
            print("\n❌ No se encontraron usuarios con rol logística")
            print("\nCreando usuario de prueba...")
            
            # Crear usuario de prueba
            password_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt())
            
            insert_query = """
                INSERT INTO recurso_operativo 
                (recurso_operativo_cedula, nombre, recurso_operativo_password, id_roles, estado)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                'test_logistica',
                'Usuario Logística Test',
                password_hash,
                5,  # rol logística
                'Activo'
            ))
            
            connection.commit()
            print("✅ Usuario de prueba creado:")
            print("   Cédula: test_logistica")
            print("   Contraseña: 123456")
            print("   Rol: logística (5)")
        
        # Verificar todos los roles disponibles
        print("\n=== DISTRIBUCIÓN DE ROLES ===")
        cursor.execute("""
            SELECT id_roles, COUNT(*) as cantidad
            FROM recurso_operativo 
            GROUP BY id_roles
            ORDER BY id_roles
        """)
        
        roles = cursor.fetchall()
        for rol in roles:
            print(f"  Rol {rol['id_roles']}: {rol['cantidad']} usuarios")
        
    except Error as e:
        print(f"Error en la consulta: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def probar_login_usuario():
    """Probar login con usuario logística"""
    import requests
    import re
    
    print("\n=== PRUEBA DE LOGIN ===")
    
    BASE_URL = 'http://127.0.0.1:8080'
    session = requests.Session()
    
    try:
        # Obtener página de login para extraer CSRF token
        login_page = session.get(BASE_URL)
        csrf_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', login_page.text)
        
        if not csrf_match:
            print("❌ No se pudo obtener el token CSRF")
            return
        
        csrf_token = csrf_match.group(1)
        print(f"✅ Token CSRF obtenido: {csrf_token[:20]}...")
        
        # Intentar login
        login_data = {
            'username': 'test_logistica',
            'password': '123456',
            'csrf_token': csrf_token
        }
        
        response = session.post(BASE_URL, data=login_data)
        
        print(f"Status del login: {response.status_code}")
        print(f"URL final: {response.url}")
        
        if response.status_code == 200:
            if 'dashboard' in response.url.lower():
                print("✅ Login exitoso - Redirigido al dashboard")
                
                # Probar endpoint de vencimientos
                vencimientos_url = f"{BASE_URL}/api/vehiculos/vencimientos"
                api_response = session.get(vencimientos_url)
                
                print(f"\nPrueba del endpoint /api/vehiculos/vencimientos:")
                print(f"Status: {api_response.status_code}")
                print(f"Content-Type: {api_response.headers.get('Content-Type')}")
                
                if api_response.status_code == 200:
                    try:
                        data = api_response.json()
                        print("✅ Respuesta JSON válida")
                        print(f"Success: {data.get('success')}")
                        print(f"Total registros: {data.get('total', 0)}")
                        
                        if data.get('data'):
                            print("\nPrimeros 3 registros:")
                            for i, item in enumerate(data['data'][:3]):
                                print(f"  {i+1}. Placa: {item.get('placa')}, Documento: {item.get('tipo_documento')}, Días: {item.get('dias_restantes')}")
                    except:
                        print("❌ Respuesta no es JSON válido")
                        print(f"Contenido: {api_response.text[:200]}...")
                else:
                    print(f"❌ Error en endpoint: {api_response.status_code}")
            else:
                print("❌ Login fallido - No redirigido al dashboard")
        else:
            print(f"❌ Error en login: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en prueba de login: {e}")

if __name__ == "__main__":
    verificar_usuarios_logistica()
    probar_login_usuario()