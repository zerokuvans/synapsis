#!/usr/bin/env python3
"""
Script para probar la API de vencimientos con autenticación real
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_with_auth():
    """Probar la API con autenticación"""
    session = requests.Session()
    
    print("🔍 Probando login...")
    
    # Intentar login con credenciales de prueba
    login_data = {
        'username': 'admin',  # Cambiar por credenciales válidas
        'password': 'admin'   # Cambiar por credenciales válidas
    }
    
    try:
        # Primero obtener la página de login para obtener el token CSRF si es necesario
        login_page = session.get(f"{BASE_URL}/login")
        print(f"Login page status: {login_page.status_code}")
        
        # Intentar login
        login_response = session.post(f"{BASE_URL}/login", data=login_data)
        print(f"Login response status: {login_response.status_code}")
        print(f"Login response URL: {login_response.url}")
        
        # Verificar si el login fue exitoso (redirección o cambio de URL)
        if login_response.status_code == 200 and '/dashboard' in login_response.url:
            print("✅ Login exitoso")
            
            # Ahora probar la API de vencimientos
            print("\n🔍 Probando API de vencimientos con autenticación...")
            api_response = session.get(f"{BASE_URL}/api/mpa/vencimientos")
            print(f"API status: {api_response.status_code}")
            print(f"API headers: {dict(api_response.headers)}")
            
            if api_response.status_code == 200:
                try:
                    data = api_response.json()
                    print(f"✅ API funcionando - {len(data.get('data', []))} vencimientos encontrados")
                except:
                    print(f"✅ API respondió pero no es JSON válido: {api_response.text[:200]}")
            else:
                print(f"❌ API falló: {api_response.text[:200]}")
                
        else:
            print("❌ Login falló")
            print(f"Response text: {login_response.text[:500]}")
            
            # Probar la API sin autenticación para ver qué error da
            print("\n🔍 Probando API sin autenticación...")
            api_response = requests.get(f"{BASE_URL}/api/mpa/vencimientos")
            print(f"API sin auth status: {api_response.status_code}")
            print(f"API sin auth response: {api_response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. ¿Está ejecutándose en el puerto 8080?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_other_apis():
    """Probar otras APIs para comparar"""
    print("\n🔍 Probando otras APIs sin autenticación...")
    
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
    print("🚀 Iniciando pruebas de autenticación para vencimientos")
    print("=" * 60)
    
    test_with_auth()
    test_other_apis()
    
    print("\n✅ Pruebas completadas")