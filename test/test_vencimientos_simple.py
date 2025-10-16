#!/usr/bin/env python3
"""
Script simple para probar las APIs de vencimientos con autenticación
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_with_session():
    """Probar con una sesión autenticada"""
    print("🔍 Probando con sesión autenticada...")
    
    session = requests.Session()
    
    try:
        # Primero intentar hacer login
        login_data = {
            'username': 'admin',  # Cambiar por credenciales válidas
            'password': 'admin'   # Cambiar por credenciales válidas
        }
        
        login_response = session.post(f"{BASE_URL}/login", data=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login exitoso")
            
            # Ahora probar la API de vencimientos
            api_response = session.get(f"{BASE_URL}/api/mpa/vencimientos")
            print(f"API Status: {api_response.status_code}")
            print(f"API Response: {api_response.text[:500]}...")
            
            if api_response.status_code == 200:
                data = api_response.json()
                print("✅ API de vencimientos funciona correctamente")
                print(f"Datos recibidos: {len(data.get('data', []))} vencimientos")
            else:
                print(f"❌ Error en API: {api_response.status_code}")
        else:
            print("❌ Error en login")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_direct_api():
    """Probar API directamente sin autenticación para ver el error específico"""
    print("\n🔍 Probando API directamente...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/mpa/vencimientos")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_other_apis():
    """Probar otras APIs para comparar"""
    print("\n🔍 Probando otras APIs para comparar...")
    
    apis_to_test = [
        "/api/mpa/soat",
        "/api/mpa/tecnico_mecanica", 
        "/api/mpa/licencias-conducir"
    ]
    
    for api in apis_to_test:
        try:
            response = requests.get(f"{BASE_URL}{api}")
            print(f"{api}: Status {response.status_code}")
        except Exception as e:
            print(f"{api}: Error {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas detalladas de vencimientos")
    print("=" * 60)
    
    test_direct_api()
    test_other_apis()
    test_with_session()
    
    print("\n✅ Pruebas completadas")