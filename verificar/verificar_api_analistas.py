import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"

# Credenciales
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def login_y_verificar_analistas():
    """Inicia sesión y verifica los endpoints de analistas"""
    print("="*50)
    print("VERIFICADOR DE API DE ANALISTAS")
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
    
    # Paso 2: Probar endpoints de analistas
    endpoints = [
        "/api/analistas/causas-cierre",
        "/api/analistas/grupos", 
        "/api/analistas/agrupaciones",
        "/api/analistas/tecnologias"
    ]
    
    print("\n[2] Probando endpoints de analistas...")
    
    for endpoint in endpoints:
        print(f"\n   [2.x] Probando {endpoint}")
        
        try:
            # Probar sin parámetros
            url = f"{BASE_URL}{endpoint}"
            response = session.get(url)
            
            print(f"   Código de estado: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
            
            # Verificar si la respuesta es JSON
            try:
                data = response.json()
                
                if isinstance(data, list):
                    print(f"   ✅ Éxito: {len(data)} elementos encontrados")
                    
                    # Mostrar los primeros elementos
                    for i, item in enumerate(data[:3], 1):
                        if isinstance(item, dict):
                            # Para causas-cierre
                            if 'causa_cierre' in item:
                                print(f"      {i}. Causa: {item.get('causa_cierre', 'N/A')}, Grupo: {item.get('grupo', 'N/A')}, Tecnología: {item.get('tecnologia', 'N/A')}")
                            # Para grupos/agrupaciones/tecnologías
                            elif 'grupo' in item:
                                print(f"      {i}. Grupo: {item.get('grupo', 'N/A')}")
                            elif 'agrupacion' in item:
                                print(f"      {i}. Agrupación: {item.get('agrupacion', 'N/A')}")
                            elif 'tecnologia' in item:
                                print(f"      {i}. Tecnología: {item.get('tecnologia', 'N/A')}")
                            else:
                                print(f"      {i}. {item}")
                        else:
                            print(f"      {i}. {item}")
                elif isinstance(data, dict):
                    if data.get('success', False):
                        print(f"   ✅ Éxito: {data}")
                    else:
                        print(f"   ❌ Error reportado por la API: {data.get('error', 'Sin mensaje específico')}")
                else:
                    print(f"   ⚠️ Respuesta inesperada: {data}")
                    
            except json.JSONDecodeError:
                # No es JSON, podría ser una página HTML (login requerido)
                if "login" in response.text.lower() or "iniciar sesión" in response.text.lower():
                    print("   ❌ La sesión expiró o requiere nuevo login (redirigido a página de login)")
                    print(f"   Contenido: {response.text[:100]}...")
                else:
                    print("   ❌ Respuesta no es JSON válido")
                    print(f"   Primeros 100 caracteres: {response.text[:100]}...")
                    
        except Exception as e:
            print(f"   ❌ Error al consultar {endpoint}: {str(e)}")
    
    # Paso 3: Probar con parámetros de filtro
    print("\n[3] Probando endpoints con parámetros de filtro...")
    
    # Probar causas-cierre con filtros
    test_params = [
        {"texto": "red"},
        {"tecnologia": "FTTH"},
        {"grupo": "CALIDAD"},
        {"agrupacion": "CALIDAD"}
    ]
    
    for params in test_params:
        try:
            print(f"\n   [3.x] Probando /api/analistas/causas-cierre con parámetros: {params}")
            
            url = f"{BASE_URL}/api/analistas/causas-cierre"
            response = session.get(url, params=params)
            
            print(f"   Código de estado: {response.status_code}")
            
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ Éxito: {len(data)} elementos filtrados encontrados")
                    
                    # Mostrar algunos elementos
                    for i, item in enumerate(data[:2], 1):
                        if isinstance(item, dict) and 'causa_cierre' in item:
                            print(f"      {i}. Causa: {item.get('causa_cierre', 'N/A')}, Grupo: {item.get('grupo', 'N/A')}, Tecnología: {item.get('tecnologia', 'N/A')}")
                else:
                    print(f"   ⚠️ Respuesta inesperada: {data}")
            except json.JSONDecodeError:
                print("   ❌ Respuesta no es JSON válido")
                print(f"   Primeros 100 caracteres: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error al probar filtros: {str(e)}")
    
    return True

if __name__ == "__main__":
    login_y_verificar_analistas()