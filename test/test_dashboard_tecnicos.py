import requests
import json
from datetime import datetime

# URL base del servidor
BASE_URL = 'http://127.0.0.1:8080'

def test_login_and_preoperacional():
    """Prueba el login de un técnico y la verificación preoperacional"""
    
    # Crear una sesión para mantener las cookies
    session = requests.Session()
    
    print("=== Prueba de Login y Verificación Preoperacional ===")
    print(f"Hora actual: {datetime.now()}")
    print()
    
    # 1. Intentar hacer login como técnico
    print("1. Intentando login como técnico...")
    login_data = {
        'username': 'tecnico1',  # Usar un usuario técnico existente
        'password': 'password123'  # Usar la contraseña correcta
    }
    
    try:
        login_response = session.post(f'{BASE_URL}/login', data=login_data)
        print(f"Status code del login: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✓ Login exitoso")
        else:
            print(f"✗ Error en login: {login_response.text}")
            return
            
    except Exception as e:
        print(f"✗ Error al conectar para login: {e}")
        return
    
    # 2. Verificar el registro preoperacional
    print("\n2. Verificando registro preoperacional...")
    
    try:
        preop_response = session.get(f'{BASE_URL}/verificar_registro_preoperacional')
        print(f"Status code: {preop_response.status_code}")
        print(f"Headers: {dict(preop_response.headers)}")
        
        if preop_response.status_code == 200:
            try:
                data = preop_response.json()
                print("✓ Respuesta exitosa del endpoint:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(f"✗ Respuesta no es JSON válido: {preop_response.text}")
        else:
            print(f"✗ Error en endpoint: {preop_response.status_code}")
            print(f"Respuesta: {preop_response.text}")
            
    except Exception as e:
        print(f"✗ Error al verificar preoperacional: {e}")
    
    print("\n=== Fin de la prueba ===")

if __name__ == '__main__':
    test_login_and_preoperacional()