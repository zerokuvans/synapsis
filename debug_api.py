import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8080"
API_ENDPOINT = "/api/indicadores/cumplimiento"
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def iniciar_sesion():
    """Inicia sesión y obtiene una sesión autenticada"""
    print(f"Iniciando sesión con usuario: {USERNAME}")
    session = requests.Session()
    
    try:
        # Obtener cookies iniciales
        session.get(BASE_URL)
        
        # Realizar login
        response = session.post(
            BASE_URL + "/", 
            data={
                "username": USERNAME,
                "password": PASSWORD
            }
        )
        
        if response.status_code == 200 and "dashboard" in response.url:
            print("✅ Login exitoso!")
            print(f"Cookies: {session.cookies}")
            return session
        else:
            print("❌ Error en login")
            print(f"Status: {response.status_code}")
            print(f"URL después de login: {response.url}")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def probar_api(session, fecha_inicio="2025-03-17", fecha_fin="2025-03-17", supervisor=None):
    """Prueba el endpoint de API con diferentes parámetros"""
    if not session:
        print("No hay sesión autenticada")
        return
    
    # Construir URL con parámetros
    url = f"{BASE_URL}{API_ENDPOINT}?fecha_inicio={fecha_inicio}&fecha_fin={fecha_fin}"
    if supervisor:
        url += f"&supervisor={supervisor}"
    
    print(f"\nConsultando API: {url}")
    
    # Configurar cabeceras para petición AJAX
    headers = {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        response = session.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Cabeceras de respuesta: {dict(response.headers)}")
        
        # Verificar status code
        if response.status_code != 200:
            print(f"❌ Error HTTP: {response.status_code}")
            print(response.text)
            return
        
        # Intentar procesar como JSON
        try:
            data = response.json()
            print("\n📊 Respuesta JSON:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar si hay datos
            if "indicadores" in data:
                print(f"\n✅ Se encontraron {len(data['indicadores'])} indicadores")
                if data['indicadores']:
                    print("\nPrimeros 3 indicadores:")
                    for i, indicador in enumerate(data['indicadores'][:3]):
                        print(f"{i+1}. {indicador['supervisor']}: {indicador['porcentaje_cumplimiento']}%")
            
            # Verificar campos esperados
            if "success" in data and data["success"]:
                print("\n✅ La respuesta indica éxito")
            else:
                print("\n❌ La respuesta indica error")
                if "error" in data:
                    print(f"Error: {data['error']}")
            
            return data
            
        except json.JSONDecodeError:
            print("❌ Error al decodificar JSON")
            print(f"Contenido: {response.text[:500]}...")
    
    except Exception as e:
        print(f"❌ Error al consultar API: {str(e)}")

def main():
    print("=== DEPURACIÓN DE API DE INDICADORES ===")
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("======================================")
    
    # Iniciar sesión
    session = iniciar_sesion()
    if not session:
        print("No se pudo iniciar sesión. Terminando.")
        return
    
    # Probar con diferentes escenarios
    print("\n--- Escenario 1: Fecha única (mismo día) ---")
    probar_api(session, "2025-03-17", "2025-03-17")
    
    print("\n--- Escenario 2: Rango de fechas ---")
    probar_api(session, "2025-03-15", "2025-03-17")
    
    print("\n--- Escenario 3: Con filtro de supervisor ---")
    probar_api(session, "2025-03-17", "2025-03-17", "NELSON DIAZ")
    
    print("\n--- Escenario 4: Compatibilidad con parámetro 'fecha' ---")
    # Consulta antigua con parámetro 'fecha'
    url = f"{BASE_URL}{API_ENDPOINT}?fecha=2025-03-17"
    print(f"\nConsultando API: {url}")
    
    headers = {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        response = session.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("\n📊 Respuesta JSON:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                print(f"\nSe encontraron {len(data.get('indicadores', []))} indicadores")
            except:
                print("Error al decodificar JSON")
                print(response.text[:500])
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 