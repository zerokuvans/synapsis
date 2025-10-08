import requests
import json
from datetime import datetime

# Configuración
BASE_URL = 'http://localhost:8080'
USERNAME = '1085176966'  # Usar una cédula de prueba
PASSWORD = 'password'  # Usar la contraseña correspondiente

def test_resumen_endpoint():
    # Crear sesión
    session = requests.Session()
    
    # Datos de login (ajustar según tu sistema)
    login_data = {
        'username': '80833959',  # Cédula del usuario
        'password': 'M4r14l4r@'  # Contraseña del usuario
    }
    
    try:
        # Hacer login (la ruta es la raíz, no /login)
        print("Intentando hacer login...")
        login_response = session.post(f'{BASE_URL}/', data=login_data)
        
        if login_response.status_code == 200 and 'dashboard' in login_response.url:
            print("✓ Login exitoso")
        else:
            print(f"✗ Error en login: {login_response.status_code}")
            print(f"URL de respuesta: {login_response.url}")
            return
    except Exception as e:
        print(f"✗ Error durante login: {e}")
        return
    
    # Probar endpoint de resumen
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    url_resumen = f'{BASE_URL}/api/asistencia/resumen_agrupado?fecha_inicio={fecha_hoy}&fecha_fin={fecha_hoy}'
    
    print(f"\nProbando endpoint: {url_resumen}")
    
    response = session.get(url_resumen)
    
    print(f"Status code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("\n=== RESPUESTA DEL ENDPOINT ===")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('success'):
                print("\n✓ Endpoint funcionando correctamente")
                if data.get('data', {}).get('detallado'):
                    print(f"✓ Se encontraron {len(data['data']['detallado'])} registros")
                else:
                    print("⚠ No hay datos detallados")
            else:
                print(f"✗ Error en respuesta: {data.get('message')}")
                
        except json.JSONDecodeError:
            print("✗ Error: La respuesta no es JSON válido")
            print(f"Contenido: {response.text[:500]}...")
    else:
        print(f"✗ Error HTTP: {response.status_code}")
        print(f"Contenido: {response.text[:500]}...")

if __name__ == '__main__':
    test_resumen_endpoint()