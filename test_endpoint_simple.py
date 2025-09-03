#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el endpoint /api/vehiculos/vencimientos
con autenticación de usuario logística
"""

import requests
import json
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Configuración
BASE_URL = 'http://127.0.0.1:8080'
VENCIMIENTOS_URL = f'{BASE_URL}/api/vehiculos/vencimientos'

def conectar_db():
    """Conectar a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def verificar_usuario_logistica():
    """Verificar que existe un usuario con rol de logística"""
    connection = conectar_db()
    if not connection:
        return None
        
    cursor = connection.cursor(dictionary=True)
    
    # Buscar usuario con rol logística (id_roles = 3)
    cursor.execute("""
        SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula, id_roles
        FROM recurso_operativo 
        WHERE id_roles = 3 AND estado = 'Activo'
        LIMIT 1
    """)
    
    usuario = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if usuario:
        print(f"✅ Usuario de logística encontrado: {usuario['nombre']} (ID: {usuario['id_codigo_consumidor']})")
        return usuario
    else:
        print("❌ No se encontró usuario con rol de logística")
        return None

def hacer_login(session, cedula, password):
    """Hacer login y obtener sesión"""
    login_url = f"{BASE_URL}/"
    
    # Headers para simular petición AJAX
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Datos del login
    login_data = {
        'username': cedula,
        'password': password
    }
    
    print(f"Intentando login con usuario: {cedula}")
    print(f"Contraseña: {password}")
    
    try:
        response = session.post(login_url, data=login_data, headers=headers)
        print(f"Status de login: {response.status_code}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                print(f"Respuesta JSON: {json_response}")
                
                if json_response.get('status') == 'success':
                    return True, json_response
                else:
                    print(f"❌ Login falló: {json_response.get('message', 'Error desconocido')}")
                    return False, None
            except json.JSONDecodeError:
                print(f"❌ Respuesta no es JSON válido: {response.text[:200]}")
                return False, None
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return False, None

def probar_endpoint(session):
    """Probar el endpoint de vencimientos"""
    print("\n=== PROBANDO ENDPOINT /api/vehiculos/vencimientos ===")
    
    # Prueba 1: Sin parámetros
    print("\n1. Probando sin parámetros...")
    response = session.get(VENCIMIENTOS_URL)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"✅ Respuesta exitosa:")
            print(f"   - Total vencimientos: {len(data.get('vencimientos', []))}")
            if data.get('vencimientos'):
                print(f"   - Primer vencimiento: {data['vencimientos'][0]}")
        except json.JSONDecodeError:
            print(f"❌ Respuesta no es JSON válido: {response.text[:200]}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text[:200]}")
    
    # Prueba 2: Con parámetros
    print("\n2. Probando con parámetros (30 días, SOAT)...")
    params = {
        'dias_anticipacion': 30,
        'tipo_documento': 'SOAT'
    }
    response = session.get(VENCIMIENTOS_URL, params=params)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"✅ Respuesta exitosa:")
            print(f"   - Total vencimientos SOAT: {len(data.get('vencimientos', []))}")
            if data.get('vencimientos'):
                print(f"   - Primer vencimiento: {data['vencimientos'][0]}")
        except json.JSONDecodeError:
            print(f"❌ Respuesta no es JSON válido: {response.text[:200]}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text[:200]}")

def probar_endpoint_vencimientos(session, dias_anticipacion=None, tipo_documento=None):
    """Probar el endpoint de vencimientos"""
    url = f"{BASE_URL}/api/vehiculos/vencimientos"
    
    # Preparar parámetros
    params = {}
    if dias_anticipacion is not None:
        params['dias_anticipacion'] = dias_anticipacion
    if tipo_documento is not None:
        params['tipo_documento'] = tipo_documento
    
    try:
        response = session.get(url, params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Respuesta JSON válida")
                print(f"Número de registros: {len(data) if isinstance(data, list) else 'No es lista'}")
                
                if isinstance(data, list) and len(data) > 0:
                    print(f"Primer registro: {data[0]}")
                elif isinstance(data, list):
                    print("Lista vacía")
                else:
                    print(f"Respuesta: {data}")
                    
            except json.JSONDecodeError:
                print(f"❌ Respuesta no es JSON válido: {response.text[:200]}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error en petición: {e}")

def test_endpoint():
    """Función principal para probar el endpoint"""
    print("=== INICIANDO PRUEBA DEL ENDPOINT /api/vehiculos/vencimientos ===")
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # Verificar conexión a base de datos
    print("Verificando conexión a base de datos...")
    usuario_logistica = verificar_usuario_logistica()
    
    if not usuario_logistica:
        print("❌ No se pudo conectar a la base de datos o no hay usuarios de logística")
        return
    
    print(f"✅ Usuario de logística encontrado: {usuario_logistica['nombre']} (ID: {usuario_logistica['id_codigo_consumidor']})")
    
    # Credenciales específicas para la prueba (usuario con rol de logística)
    cedula = '1002407101'
    password = 'CE1002407101'
    
    # Hacer login
    print("\n1. Haciendo login...")
    login_success, session_data = hacer_login(session, cedula, password)
    
    if not login_success:
        print("❌ Login falló")
        return
    
    print("✅ Login exitoso")
    
    # Probar endpoint
    print("\n=== PROBANDO ENDPOINT /api/vehiculos/vencimientos ===")
    
    # Test 1: Sin parámetros
    print("\n1. Probando sin parámetros...")
    probar_endpoint_vencimientos(session)
    
    # Test 2: Con parámetros
    print("\n2. Probando con parámetros (30 días, SOAT)...")
    probar_endpoint_vencimientos(session, dias_anticipacion=30, tipo_documento='SOAT')
    
    print("\n=== FIN DE LA PRUEBA ===")

if __name__ == "__main__":
    try:
        test_endpoint()
    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()