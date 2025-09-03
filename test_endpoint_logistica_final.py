#!/usr/bin/env python3
import requests
import json
import mysql.connector
from mysql.connector import Error
import bcrypt
from dotenv import load_dotenv
import os

load_dotenv()

# Configuración
BASE_URL = 'http://127.0.0.1:8080'
VENCIMIENTOS_URL = f'{BASE_URL}/api/vehiculos/vencimientos'

# Configuración de base de datos
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT'))
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error de conexión a MySQL: {str(e)}")
        return None

def verificar_usuario_logistica():
    """Verificar si existe un usuario de logística y crearlo si no existe"""
    connection = get_db_connection()
    if not connection:
        return False
        
    cursor = connection.cursor(dictionary=True)
    
    # Buscar usuario de logística
    cursor.execute("""
        SELECT * FROM recurso_operativo 
        WHERE id_roles = 5 
        LIMIT 1
    """)
    
    usuario = cursor.fetchone()
    
    if not usuario:
        print("No se encontró usuario de logística. Creando uno...")
        
        # Crear usuario de logística
        password_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute("""
            INSERT INTO recurso_operativo 
            (recurso_operativo_cedula, recurso_operativo_password, nombre, id_roles, estado)
            VALUES (%s, %s, %s, %s, %s)
        """, ('test_logistica', password_hash, 'Usuario Test Logística', 5, 'Activo'))
        
        connection.commit()
        print("Usuario de logística creado: test_logistica / 123456")
        
        # Obtener el usuario recién creado
        cursor.execute("""
            SELECT * FROM recurso_operativo 
            WHERE recurso_operativo_cedula = 'test_logistica'
        """)
        usuario = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return usuario

def test_endpoint_con_autenticacion():
    """Probar el endpoint con autenticación"""
    print("=== PRUEBA DEL ENDPOINT /api/vehiculos/vencimientos ===\n")
    
    # Verificar usuario de logística
    usuario = verificar_usuario_logistica()
    if not usuario:
        print("❌ No se pudo crear/encontrar usuario de logística")
        return
    
    print(f"✅ Usuario de logística encontrado: {usuario['nombre']} (ID: {usuario['id_codigo_consumidor']})")
    
    # Crear sesión
    session = requests.Session()
    
    try:
        # 1. Obtener CSRF token
        print("\n1. Obteniendo CSRF token...")
        csrf_response = session.get(f"{BASE_URL}/")
        if csrf_response.status_code != 200:
            print(f"❌ Error al obtener página de login: {csrf_response.status_code}")
            return
        
        # Extraer CSRF token del HTML
        csrf_token = None
        for line in csrf_response.text.split('\n'):
            if 'csrf_token' in line and 'value=' in line:
                start = line.find('value="') + 7
                end = line.find('"', start)
                csrf_token = line[start:end]
                break
        
        if not csrf_token:
            print("❌ No se pudo obtener CSRF token")
            return
        
        print(f"✅ CSRF token obtenido: {csrf_token[:20]}...")
        
        # 2. Hacer login
        print("\n2. Realizando login...")
        login_data = {
            'username': 'test_logistica',
            'password': '123456',
            'csrf_token': csrf_token
        }
        
        login_response = session.post(f"{BASE_URL}/", data=login_data)
        
        if login_response.status_code == 200:
            # Verificar si el login fue exitoso
            if 'dashboard' in login_response.url or login_response.json().get('success', False):
                print("✅ Login exitoso")
            else:
                print(f"❌ Login falló: {login_response.text[:200]}")
                return
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            return
        
        # 3. Probar endpoint de vencimientos
        print("\n3. Probando endpoint /api/vehiculos/vencimientos...")
        
        # Sin parámetros
        response = session.get(VENCIMIENTOS_URL)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Respuesta exitosa:")
                print(f"   - Success: {data.get('success')}")
                print(f"   - Total registros: {data.get('total', 0)}")
                
                if data.get('data'):
                    print(f"   - Primeros 3 registros:")
                    for i, item in enumerate(data['data'][:3]):
                        print(f"     {i+1}. Placa: {item.get('placa')}, Documento: {item.get('tipo_documento')}, Días: {item.get('dias_restantes')}")
                else:
                    print("   - No hay datos de vencimientos")
                    
            except json.JSONDecodeError:
                print(f"❌ Error al decodificar JSON: {response.text[:200]}")
        else:
            print(f"❌ Error en endpoint: {response.status_code}")
            print(f"Respuesta: {response.text[:200]}")
        
        # 4. Probar con parámetros
        print("\n4. Probando con parámetros (días=60)...")
        response_params = session.get(f"{VENCIMIENTOS_URL}?dias=60")
        print(f"Status Code: {response_params.status_code}")
        
        if response_params.status_code == 200:
            try:
                data = response_params.json()
                print(f"✅ Respuesta con parámetros:")
                print(f"   - Success: {data.get('success')}")
                print(f"   - Total registros: {data.get('total', 0)}")
            except json.JSONDecodeError:
                print(f"❌ Error al decodificar JSON: {response_params.text[:200]}")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")

if __name__ == "__main__":
    test_endpoint_con_autenticacion()