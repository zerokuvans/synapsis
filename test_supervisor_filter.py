import requests
import json

# Configuración
BASE_URL = "http://localhost:8080"
LOGIN_URL = f"{BASE_URL}/login"
API_URL = f"{BASE_URL}/api/lider/inicio-operacion/datos"

# Credenciales de prueba (ajustar según sea necesario)
USERNAME = "80833959"  # Usuario válido
PASSWORD = "M4r14l4r@"  # Contraseña válida

def test_supervisor_filter():
    """Probar el filtro de supervisor con autenticación"""
    
    # Crear sesión
    session = requests.Session()
    
    try:
        # 1. Hacer login
        print("1. Intentando hacer login...")
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        login_response = session.post(LOGIN_URL, data=login_data)
        print(f"   Status login: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   Error en login: {login_response.text[:200]}")
            return
        
        # 2. Probar endpoint sin filtros
        print("\n2. Probando endpoint sin filtros...")
        from datetime import datetime
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        params = {
            'fecha': fecha_hoy
        }
        
        response = session.get(API_URL, params=params)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ Sin filtros - Datos obtenidos correctamente")
                    print(f"   Total técnicos: {data.get('data', {}).get('tecnicos', {}).get('total', 0)}")
                else:
                    print(f"   ❌ Error en respuesta: {data.get('error')}")
            except json.JSONDecodeError:
                print(f"   ❌ Respuesta no es JSON válido")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
        
        # 3. Probar endpoint con filtro de supervisor
        print("\n3. Probando endpoint con filtro de supervisor...")
        params_with_supervisor = {
            'fecha': fecha_hoy,
            'supervisores[]': 'SILVA CASTRO DANIEL ALBERTO'
        }
        
        response_filtered = session.get(API_URL, params=params_with_supervisor)
        print(f"   Status: {response_filtered.status_code}")
        
        if response_filtered.status_code == 200:
            try:
                data_filtered = response_filtered.json()
                if data_filtered.get('success'):
                    print(f"   ✅ Con filtro - Datos obtenidos correctamente")
                    print(f"   Total técnicos: {data_filtered.get('data', {}).get('tecnicos', {}).get('total', 0)}")
                    print(f"   Con asistencia: {data_filtered.get('data', {}).get('tecnicos', {}).get('con_asistencia', 0)}")
                    print(f"   Sin asistencia: {data_filtered.get('data', {}).get('tecnicos', {}).get('sin_asistencia', 0)}")
                else:
                    print(f"   ❌ Error en respuesta: {data_filtered.get('error')}")
            except json.JSONDecodeError:
                print(f"   ❌ Respuesta no es JSON válido")
                print(f"   Contenido: {response_filtered.text[:200]}")
        else:
            print(f"   ❌ Error HTTP: {response_filtered.status_code}")
            print(f"   Respuesta: {response_filtered.text[:200]}")
        
        # 4. Probar con múltiples supervisores
        print("\n4. Probando endpoint con múltiples supervisores...")
        params_multiple = {
            'fecha': '2025-01-16'
        }
        
        # Agregar múltiples supervisores
        url_with_multiple = f"{API_URL}?fecha={fecha_hoy}&supervisores[]=SILVA%20CASTRO%20DANIEL%20ALBERTO&supervisores[]=CORTES%20CUERVO%20SANDRA%20CECILIA"
        
        response_multiple = session.get(url_with_multiple)
        print(f"   Status: {response_multiple.status_code}")
        
        if response_multiple.status_code == 200:
            try:
                data_multiple = response_multiple.json()
                if data_multiple.get('success'):
                    print(f"   ✅ Con múltiples supervisores - Datos obtenidos correctamente")
                    print(f"   Total técnicos: {data_multiple.get('data', {}).get('tecnicos', {}).get('total', 0)}")
                else:
                    print(f"   ❌ Error en respuesta: {data_multiple.get('error')}")
            except json.JSONDecodeError:
                print(f"   ❌ Respuesta no es JSON válido")
        else:
            print(f"   ❌ Error HTTP: {response_multiple.status_code}")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_supervisor_filter()