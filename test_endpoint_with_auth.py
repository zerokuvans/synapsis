#!/usr/bin/env python3
"""
Script para probar el endpoint con autenticación simulada
"""

import requests
import json
from datetime import datetime

def test_endpoint_with_session():
    """Probar el endpoint con una sesión autenticada"""
    
    base_url = "http://127.0.0.1:8080"
    
    # Crear una sesión para mantener cookies
    session = requests.Session()
    
    print(f"=== PROBANDO ENDPOINT CON AUTENTICACIÓN ===")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 60)
    
    try:
        # Paso 1: Intentar hacer login
        print("1. Intentando hacer login...")
        login_data = {
            'username': '1234567890',  # Usar una cédula de prueba
            'password': 'password123'  # Usar una contraseña de prueba
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        print(f"Login Status Code: {login_response.status_code}")
        
        if login_response.status_code == 200 and 'login' not in login_response.url:
            print("✅ Login exitoso")
        else:
            print("❌ Login falló, probando sin autenticación...")
        
        # Paso 2: Probar el endpoint
        print("\n2. Probando endpoint /api/indicadores/detalle_tecnicos...")
        params = {
            'fecha': '2025-01-10',
            'supervisor': 'CORTES CUERVO SANDRA CECILIA'
        }
        
        endpoint_url = f"{base_url}/api/indicadores/detalle_tecnicos"
        response = session.get(endpoint_url, params=params, timeout=30)
        
        print(f"Endpoint Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        # Verificar si es HTML (redirect a login) o JSON
        if 'text/html' in response.headers.get('content-type', ''):
            print("❌ Respuesta es HTML - probablemente redirect a login")
            print("Primeros 200 caracteres:")
            print(response.text[:200])
        else:
            try:
                json_data = response.json()
                print("✅ Respuesta JSON:")
                print(json.dumps(json_data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError as e:
                print(f"❌ Error al parsear JSON: {e}")
                print("Contenido raw:")
                print(response.text[:500])
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoint_with_session()