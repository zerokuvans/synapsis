import requests
import json
from datetime import datetime

# Configuración del servidor
BASE_URL = 'http://localhost:8080'
LOGIN_URL = f'{BASE_URL}/'
API_URL = f'{BASE_URL}/api/vehiculos/vencimientos'

def test_vencimientos_endpoint():
    """Probar el endpoint /api/vehiculos/vencimientos con autenticación"""
    
    # Crear una sesión para mantener las cookies
    session = requests.Session()
    
    print("=== PRUEBA DEL ENDPOINT /api/vehiculos/vencimientos ===")
    print(f"URL del endpoint: {API_URL}")
    print()
    
    try:
        # Paso 1: Intentar login
        print("1. Intentando login...")
        login_data = {
            'username': 'test123',
            'password': 'test123'
        }
        
        login_response = session.post(LOGIN_URL, data=login_data, timeout=10)
        print(f"   Status code del login: {login_response.status_code}")
        print(f"   Content-Type: {login_response.headers.get('Content-Type', 'N/A')}")
        
        if login_response.status_code == 200:
            print("   ✓ Login exitoso")
        else:
            print(f"   ✗ Error en login: {login_response.status_code}")
            print(f"   Respuesta: {login_response.text[:200]}...")
            return
        
        print()
        
        # Paso 2: Probar el endpoint sin parámetros
        print("2. Probando endpoint sin parámetros...")
        response = session.get(API_URL, timeout=10)
        print(f"   Status code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✓ Respuesta JSON válida")
                print(f"   Número de registros: {len(data) if isinstance(data, list) else 'N/A'}")
                if isinstance(data, list) and len(data) > 0:
                    print(f"   Primer registro: {json.dumps(data[0], indent=2, default=str)}")
                elif isinstance(data, dict):
                    print(f"   Respuesta: {json.dumps(data, indent=2, default=str)}")
            except json.JSONDecodeError:
                print(f"   ✗ Respuesta no es JSON válido")
                print(f"   Contenido: {response.text[:500]}...")
        else:
            print(f"   ✗ Error: {response.status_code}")
            print(f"   Contenido: {response.text[:500]}...")
        
        print()
        
        # Paso 3: Probar el endpoint con parámetro dias=60
        print("3. Probando endpoint con parámetro dias=60...")
        params = {'dias': 60}
        response = session.get(API_URL, params=params, timeout=10)
        print(f"   Status code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   URL completa: {response.url}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✓ Respuesta JSON válida")
                print(f"   Número de registros: {len(data) if isinstance(data, list) else 'N/A'}")
                if isinstance(data, list) and len(data) > 0:
                    print(f"   Primer registro: {json.dumps(data[0], indent=2, default=str)}")
                elif isinstance(data, dict):
                    print(f"   Respuesta: {json.dumps(data, indent=2, default=str)}")
            except json.JSONDecodeError:
                print(f"   ✗ Respuesta no es JSON válido")
                print(f"   Contenido: {response.text[:500]}...")
        else:
            print(f"   ✗ Error: {response.status_code}")
            print(f"   Contenido: {response.text[:500]}...")
        
        print()
        
        # Paso 4: Probar el endpoint con parámetros adicionales
        print("4. Probando endpoint con múltiples parámetros...")
        params = {
            'dias': 30,
            'documento': 'soat',
            'estado': 'todos'
        }
        response = session.get(API_URL, params=params, timeout=10)
        print(f"   Status code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   URL completa: {response.url}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✓ Respuesta JSON válida")
                print(f"   Número de registros: {len(data) if isinstance(data, list) else 'N/A'}")
                if isinstance(data, list) and len(data) > 0:
                    print(f"   Primer registro: {json.dumps(data[0], indent=2, default=str)}")
                elif isinstance(data, dict):
                    print(f"   Respuesta: {json.dumps(data, indent=2, default=str)}")
            except json.JSONDecodeError:
                print(f"   ✗ Respuesta no es JSON válido")
                print(f"   Contenido: {response.text[:500]}...")
        else:
            print(f"   ✗ Error: {response.status_code}")
            print(f"   Contenido: {response.text[:500]}...")
        
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    test_vencimientos_endpoint()