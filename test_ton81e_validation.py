#!/usr/bin/env python3
"""
Script para probar la validación de mantenimientos abiertos en el endpoint /preoperacional
"""

import requests
import json

def test_preoperacional_validation():
    """Probar la validación de mantenimientos abiertos"""
    
    # URL base del servidor Flask
    base_url = "http://127.0.0.1:8080"
    
    # Crear una sesión para mantener las cookies
    session = requests.Session()
    
    print("=== PRUEBA DE VALIDACIÓN DE MANTENIMIENTOS ABIERTOS ===\n")
    
    # Paso 1: Intentar hacer login
    print("1. Intentando hacer login...")
    login_data = {
        'username': '1019112308',  # Usar 'username' en lugar de 'cedula'
        'password': '123456'       # La contraseña sin hash que se verifica con bcrypt
    }
    
    # Agregar header para recibir respuesta JSON
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    login_response = session.post(f"{base_url}/login", data=login_data, headers=headers)
    print(f"   Status code del login: {login_response.status_code}")
    
    # Verificar si la respuesta es JSON
    try:
        login_json = login_response.json()
        print(f"   Respuesta JSON del login: {json.dumps(login_json, indent=2, ensure_ascii=False)}")
        
        if login_response.status_code == 200 and login_json.get('status') == 'success':
            print("   ✅ Login exitoso")
        else:
            print(f"   ❌ Login falló: {login_json.get('message', 'Error desconocido')}")
            return
            
    except json.JSONDecodeError:
        print("   ❌ La respuesta del login no es JSON válido")
        print(f"   Contenido: {login_response.text[:300]}...")
        return
    
    # Paso 2: Probar el endpoint /preoperacional con TON81E
    print("\n2. Probando endpoint /preoperacional con vehículo TON81E...")
    
    preoperacional_data = {
        'id_codigo_consumidor': '11',  # Usar el ID del usuario (11 según la consulta anterior)
        'placa_vehiculo': 'TON81E',
        'kilometraje_propuesto': '50000',
        'observaciones': 'Prueba de validación de mantenimientos abiertos'
    }
    
    response = session.post(f"{base_url}/preoperacional", data=preoperacional_data)
    
    print(f"   Status code: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
    
    # Verificar si la respuesta es JSON
    try:
        response_json = response.json()
        print(f"   Respuesta JSON: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
        
        # Verificar si la validación está funcionando
        if response.status_code == 400:
            if 'mantenimiento' in response_json.get('error', '').lower():
                print("   ✅ VALIDACIÓN FUNCIONANDO: Se detectó mantenimiento abierto")
            else:
                print("   ⚠️  Error 400 pero no relacionado con mantenimiento")
                print(f"   Error: {response_json.get('error', 'No especificado')}")
        elif response.status_code == 200:
            print("   ❌ VALIDACIÓN NO FUNCIONANDO: El preoperacional fue aceptado a pesar del mantenimiento abierto")
        else:
            print(f"   ⚠️  Status code inesperado: {response.status_code}")
            
    except json.JSONDecodeError:
        print("   ❌ La respuesta no es JSON válido")
        print(f"   Contenido de la respuesta: {response.text[:500]}...")
        
        # Si no es JSON, podría ser una redirección HTML
        if response.status_code == 200 and 'html' in response.headers.get('Content-Type', '').lower():
            print("   ⚠️  Respuesta HTML - posible redirección o página de error")

if __name__ == "__main__":
    test_preoperacional_validation()