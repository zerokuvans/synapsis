import requests
import json
from datetime import datetime

# Configuración del servidor
BASE_URL = "http://localhost:8080"

def test_vencimientos_with_auth():
    """Probar el endpoint de vencimientos con autenticación"""
    
    print("=== PRUEBA DEL ENDPOINT /api/vehiculos/vencimientos CON AUTENTICACIÓN ===")
    print(f"Fecha de prueba: {datetime.now()}")
    
    # Crear una sesión para mantener las cookies
    session = requests.Session()
    
    try:
        # Paso 1: Intentar hacer login
        print("\n1. Intentando hacer login...")
        login_data = {
            'username': 'admin',  # Usuario por defecto
            'password': 'admin'   # Contraseña por defecto
        }
        
        login_response = session.post(f"{BASE_URL}/login", data=login_data)
        print(f"Status Code Login: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login exitoso")
        else:
            print("❌ Error en login")
            return
        
        # Paso 2: Probar el endpoint de vencimientos
        print("\n2. Probando endpoint de vencimientos...")
        response = session.get(f"{BASE_URL}/api/vehiculos/vencimientos")
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'No especificado')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Respuesta JSON válida")
                print(f"Success: {data.get('success', 'No especificado')}")
                print(f"Total registros: {data.get('total', 0)}")
                
                if data.get('success') and data.get('data'):
                    print(f"\n📊 DATOS DE VENCIMIENTOS:")
                    for i, item in enumerate(data['data'][:5]):  # Mostrar solo los primeros 5
                        print(f"  {i+1}. Placa: {item.get('placa')}, Tipo: {item.get('tipo_documento')}, Días: {item.get('dias_restantes')}")
                    
                    if len(data['data']) > 5:
                        print(f"  ... y {len(data['data']) - 5} registros más")
                else:
                    print("⚠️ No hay datos de vencimientos o la respuesta no es exitosa")
                    if not data.get('success'):
                        print(f"Mensaje de error: {data.get('message', 'No especificado')}")
                        
            except json.JSONDecodeError:
                print("❌ La respuesta no es JSON válido")
                print(f"Contenido: {response.text[:200]}...")
        else:
            print(f"❌ Error en la petición: {response.status_code}")
            print(f"Contenido: {response.text[:200]}...")
        
        # Paso 3: Probar con parámetros
        print("\n3. Probando con parámetros (días=60)...")
        response_params = session.get(f"{BASE_URL}/api/vehiculos/vencimientos?dias=60")
        
        if response_params.status_code == 200:
            try:
                data_params = response_params.json()
                print(f"✅ Con parámetros - Total: {data_params.get('total', 0)}")
            except:
                print("❌ Error al procesar respuesta con parámetros")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. Asegúrate de que el servidor esté ejecutándose en http://localhost:8080")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_vencimientos_with_auth()