import requests
import json
from datetime import datetime

# Configuración del servidor
BASE_URL = 'http://localhost:8080'

def test_login_and_preoperacional():
    print("=== Prueba de Login y Verificación Preoperacional ===")
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # 1. Intentar hacer login
    print("\n1. Intentando hacer login...")
    login_data = {
        'username': '1234567890',  # Usar una cédula que exista en la BD
        'password': 'password123'  # Usar la contraseña correcta
    }
    
    # Hacer login con headers para simular AJAX
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        login_response = session.post(f'{BASE_URL}/', data=login_data, headers=headers)
        print(f"Status Code Login: {login_response.status_code}")
        print(f"Response Login: {login_response.text}")
        
        if login_response.status_code == 200:
            login_json = login_response.json()
            if login_json.get('status') == 'success':
                print("✓ Login exitoso")
                print(f"User ID: {login_json.get('user_id')}")
                print(f"User Role: {login_json.get('user_role')}")
                print(f"User Name: {login_json.get('user_name')}")
                
                # 2. Probar endpoint de verificación preoperacional
                print("\n2. Probando endpoint de verificación preoperacional...")
                preop_response = session.get(f'{BASE_URL}/verificar_registro_preoperacional')
                print(f"Status Code Preoperacional: {preop_response.status_code}")
                print(f"Response Preoperacional: {preop_response.text}")
                
                if preop_response.status_code == 200:
                    try:
                        preop_json = preop_response.json()
                        print("✓ Endpoint preoperacional funcionando")
                        print(f"Datos: {json.dumps(preop_json, indent=2)}")
                    except json.JSONDecodeError:
                        print("✗ Respuesta no es JSON válido")
                else:
                    print(f"✗ Error en endpoint preoperacional: {preop_response.status_code}")
            else:
                print(f"✗ Login falló: {login_json.get('message')}")
        else:
            print(f"✗ Error en login: {login_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Error: No se puede conectar al servidor. ¿Está ejecutándose en localhost:5000?")
    except Exception as e:
        print(f"✗ Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_login_and_preoperacional()