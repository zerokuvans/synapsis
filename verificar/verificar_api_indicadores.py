import requests
import json
from datetime import datetime
import re

# Configuración
BASE_URL = "http://127.0.0.1:8080"  
LOGIN_URL = f"{BASE_URL}/"
API_URL = f"{BASE_URL}/api/indicadores/cumplimiento"

# Credenciales
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def login_y_verificar_api():
    """Inicia sesión y verifica la API de indicadores"""
    print("="*50)
    print("VERIFICADOR DE API DE INDICADORES")
    print("="*50)
    
    # Crear sesión
    session = requests.Session()
    
    # Paso 1: Iniciar sesión
    print("\n[1] Intentando iniciar sesión...")
    
    # Realizar solicitud GET inicial para obtener cookies/CSRF
    session.get(LOGIN_URL)
    
    # Preparar datos de login
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Intentar login
    try:
        login_response = session.post(
            LOGIN_URL, 
            data=login_data,
            headers=headers,
            allow_redirects=True
        )
        
        print(f"   Respuesta de login (status: {login_response.status_code})")
        
        # Verificar si la respuesta contiene indicadores de éxito
        login_success = False
        
        # Verificar URL (podría ser redirigido a dashboard)
        if "dashboard" in login_response.url:
            login_success = True
        
        # O la respuesta podría ser un JSON de éxito 
        try:
            json_data = login_response.json()
            if json_data.get('status') == 'success' or json_data.get('message') == 'Inicio de sesión exitoso':
                login_success = True
        except:
            pass
        
        # Si nada de lo anterior funciona, verificar en el contenido HTML
        if not login_success and "dashboard" in login_response.text:
            login_success = True
            
        # Finalmente, verificar la existencia de cookies de sesión
        if not login_success and session.cookies.get('session'):
            login_success = True
        
        if login_success:
            print(f"✅ Login exitoso como {USERNAME}")
            print(f"   Cookies: {session.cookies.get_dict()}")
        else:
            print(f"❌ Login fallido. URL final: {login_response.url}")
            print(f"   Código de estado: {login_response.status_code}")
            print(f"   Primeros 200 caracteres de respuesta: {login_response.text[:200]}...")
            return False
    except Exception as e:
        print(f"❌ Error durante el login: {str(e)}")
        return False
    
    # Paso 2: Verificar si el usuario está autenticado haciendo una solicitud a una página protegida
    try:
        dashboard_response = session.get(f"{BASE_URL}/dashboard")
        if dashboard_response.status_code == 200 and "login" not in dashboard_response.url.lower():
            print("✅ Verificación de sesión exitosa: Acceso al dashboard confirmado")
        else:
            print("❌ No se pudo acceder al dashboard, posible problema de sesión")
            print(f"   URL final: {dashboard_response.url}")
    except Exception as e:
        print(f"❌ Error al verificar sesión: {str(e)}")
    
    # Paso 3: Consultar la API
    print("\n[2] Consultando API de indicadores...")
    
    # Fechas para probar
    fechas_prueba = [
        {"fecha": "2025-03-17"},
        {"fecha_inicio": "2025-03-17", "fecha_fin": "2025-03-17"},
        {"fecha_inicio": "2025-03-01", "fecha_fin": "2025-03-30"},
    ]
    
    for i, params in enumerate(fechas_prueba, 1):
        try:
            print(f"\n   [2.{i}] Consultando con parámetros: {params}")
            
            # Realizar la solicitud a la API
            api_response = session.get(API_URL, params=params)
            
            # Mostrar información básica
            print(f"   Código de estado: {api_response.status_code}")
            print(f"   Content-Type: {api_response.headers.get('Content-Type', 'No especificado')}")
            
            # Verificar si la respuesta es JSON
            try:
                data = api_response.json()
                
                # Verificar si es una respuesta de éxito
                if data.get('success', False):
                    indicadores = data.get('indicadores', [])
                    print(f"   ✅ Éxito: {len(indicadores)} indicadores encontrados")
                    
                    # Mostrar los primeros indicadores
                    for j, ind in enumerate(indicadores[:3], 1):
                        print(f"      {j}. {ind.get('supervisor', 'N/A')}: "
                              f"{ind.get('total_asistencia', 0)} asistencias, "
                              f"{ind.get('total_preoperacional', 0)} preoperacionales, "
                              f"{ind.get('porcentaje_cumplimiento', 0):.2f}% cumplimiento")
                else:
                    print(f"   ❌ Error reportado por la API: {data.get('error', 'Sin mensaje específico')}")
            except json.JSONDecodeError:
                # No es JSON, podría ser una página HTML (login requerido)
                if "login" in api_response.text.lower() or "iniciar sesión" in api_response.text.lower():
                    print("   ❌ La sesión expiró o requiere nuevo login (redirigido a página de login)")
                    print(f"   Contenido: {api_response.text[:100]}...")
                else:
                    print("   ❌ Respuesta no es JSON válido")
                    print(f"   Primeros 100 caracteres: {api_response.text[:100]}...")
        except Exception as e:
            print(f"   ❌ Error al consultar API: {str(e)}")
    
    # Paso 4: Verificar la URL del problema específico
    problem_url = "http://127.0.0.1:8080/indicadores/api?fecha_inicio=2025-03-17&fecha_fin=2025-03-17&supervisor="
    print(f"\n[3] Verificando URL del problema: {problem_url}")
    
    try:
        page_response = session.get(problem_url)
        print(f"   Código de estado: {page_response.status_code}")
        print(f"   Content-Type: {page_response.headers.get('Content-Type', 'No especificado')}")
        
        # Verificar si contiene elementos clave de la página
        contains_form = "filtrosForm" in page_response.text
        contains_indicators = "indicadores-container" in page_response.text
        contains_reload_button = "recargar-indicadores" in page_response.text
        
        if contains_form and contains_indicators and contains_reload_button:
            print("   ✅ La página se cargó correctamente con todos los elementos necesarios")
        else:
            print("   ⚠️ La página se cargó pero faltan algunos elementos:")
            print(f"      - Formulario de filtros: {'✓' if contains_form else '✗'}")
            print(f"      - Contenedor de indicadores: {'✓' if contains_indicators else '✗'}")
            print(f"      - Botón de recarga: {'✓' if contains_reload_button else '✗'}")
        
        # Buscar scripts que podrían contener la función cargarIndicadores
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', page_response.text, re.DOTALL)
        has_cargar_indicadores = any('cargarIndicadores' in script for script in scripts)
        
        if has_cargar_indicadores:
            print("   ✅ Se encontró la función cargarIndicadores en los scripts")
        else:
            print("   ❌ No se encontró la función cargarIndicadores en los scripts")
        
    except Exception as e:
        print(f"   ❌ Error al verificar la URL del problema: {str(e)}")
    
    return True

if __name__ == "__main__":
    login_y_verificar_api() 