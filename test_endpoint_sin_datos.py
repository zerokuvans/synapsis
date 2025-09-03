import requests
import json

# Configuración
BASE_URL = 'http://localhost:8080'
LOGIN_URL = f'{BASE_URL}/login'
VENCIMIENTOS_URL = f'{BASE_URL}/api/vehiculos/vencimientos'

# Credenciales de prueba
USERNAME = 'admin'
PASSWORD = 'admin123'

print("=== Prueba del endpoint /api/vehiculos/vencimientos sin datos ===")
print(f"URL base: {BASE_URL}")
print(f"Usuario: {USERNAME}")

try:
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # 1. Verificar conectividad
    print("\n1. Verificando conectividad...")
    response = session.get(BASE_URL, timeout=5)
    print(f"   ✓ Servidor responde: {response.status_code}")
    
    # 2. Intentar login
    print("\n2. Intentando login...")
    login_data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    
    response = session.post(LOGIN_URL, data=login_data, timeout=10)
    print(f"   Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✓ Login exitoso")
        
        # 3. Probar endpoint de vencimientos
        print("\n3. Probando endpoint de vencimientos...")
        response = session.get(VENCIMIENTOS_URL, timeout=10)
        print(f"   Status code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✓ Respuesta JSON válida")
                print(f"   Estructura de respuesta:")
                print(f"     - success: {data.get('success')}")
                print(f"     - message: {data.get('message')}")
                print(f"     - data: {type(data.get('data'))} con {len(data.get('data', []))} elementos")
                
                if data.get('data'):
                    print(f"   Primer elemento de data:")
                    print(f"     {json.dumps(data['data'][0], indent=6, ensure_ascii=False)}")
                else:
                    print(f"   ✓ No hay datos (data está vacío)")
                    
            except json.JSONDecodeError as e:
                print(f"   ✗ Error decodificando JSON: {e}")
                print(f"   Contenido de respuesta: {response.text[:500]}")
        else:
            print(f"   ✗ Error en endpoint: {response.status_code}")
            print(f"   Respuesta: {response.text[:500]}")
    else:
        print(f"   ✗ Error en login: {response.status_code}")
        print(f"   Respuesta: {response.text[:500]}")
        
except requests.exceptions.ConnectionError:
    print("   ✗ Error de conexión. ¿Está el servidor corriendo?")
except requests.exceptions.Timeout:
    print("   ✗ Timeout en la conexión")
except Exception as e:
    print(f"   ✗ Error inesperado: {e}")

print("\n=== Fin de la prueba ===")