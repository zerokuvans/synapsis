import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"

# Credenciales
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def test_api_endpoints():
    """Prueba los endpoints de API del módulo analistas"""
    print("="*60)
    print("PRUEBA DE ENDPOINTS DE API - MÓDULO ANALISTAS")
    print("="*60)
    
    # Crear sesión
    session = requests.Session()
    
    print("\n[1] Realizando login...")
    try:
        # Obtener página de login primero
        session.get(LOGIN_URL)
        
        # Datos de login
        login_data = {
            "username": USERNAME,
            "password": PASSWORD
        }
        
        # Headers para simular una petición AJAX
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Realizar login
        login_response = session.post(LOGIN_URL, data=login_data, headers=headers, allow_redirects=True)
        
        # Verificar login
        if "dashboard" in login_response.url or session.cookies.get('session'):
            print("   ✅ Login exitoso")
        else:
            print("   ❌ Login fallido")
            print(f"   URL actual: {login_response.url}")
            print(f"   Status: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False
    
    # Endpoints a probar
    endpoints_info = [
        ("/api/analistas/causas-cierre", "Causas de cierre"),
        ("/api/analistas/grupos", "Grupos"),
        ("/api/analistas/agrupaciones", "Agrupaciones"),
        ("/api/analistas/tecnologias", "Tecnologías")
    ]
    
    print("\n[2] Probando endpoints de API...")
    
    resultados = {}
    
    for endpoint, descripcion in endpoints_info:
        try:
            print(f"\n   Probando {descripcion} ({endpoint})...")
            
            # Hacer petición
            response = session.get(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if isinstance(data, list):
                        print(f"      ✅ Status: 200 - {len(data)} elementos")
                        resultados[endpoint] = len(data)
                        
                        # Mostrar algunos ejemplos si hay datos
                        if len(data) > 0 and len(data) <= 5:
                            print("      Datos de ejemplo:")
                            for i, item in enumerate(data[:3], 1):
                                if isinstance(item, dict):
                                    # Mostrar las primeras claves del diccionario
                                    keys = list(item.keys())[:3]
                                    values = [str(item.get(k, ''))[:30] for k in keys]
                                    print(f"         {i}. {dict(zip(keys, values))}")
                                else:
                                    print(f"         {i}. {str(item)[:50]}")
                        elif len(data) > 5:
                            print(f"      (Mostrando primeros 3 de {len(data)} elementos)")
                            for i, item in enumerate(data[:3], 1):
                                if isinstance(item, dict):
                                    keys = list(item.keys())[:3]
                                    values = [str(item.get(k, ''))[:30] for k in keys]
                                    print(f"         {i}. {dict(zip(keys, values))}")
                                else:
                                    print(f"         {i}. {str(item)[:50]}")
                    else:
                        print(f"      ⚠️ Status: 200 - Respuesta no es una lista")
                        print(f"      Tipo de respuesta: {type(data)}")
                        resultados[endpoint] = "No es lista"
                        
                except json.JSONDecodeError:
                    print(f"      ❌ Status: 200 - Respuesta no es JSON válido")
                    print(f"      Contenido: {response.text[:200]}...")
                    resultados[endpoint] = "No JSON"
                    
            elif response.status_code == 302:
                print(f"      ❌ Status: 302 - Redirección (posible problema de autenticación)")
                print(f"      Location: {response.headers.get('Location', 'No especificado')}")
                resultados[endpoint] = "Redirección"
                
            elif response.status_code == 404:
                print(f"      ❌ Status: 404 - Endpoint no encontrado")
                resultados[endpoint] = "No encontrado"
                
            elif response.status_code == 500:
                print(f"      ❌ Status: 500 - Error interno del servidor")
                print(f"      Contenido: {response.text[:200]}...")
                resultados[endpoint] = "Error servidor"
                
            else:
                print(f"      ❌ Status: {response.status_code}")
                print(f"      Contenido: {response.text[:200]}...")
                resultados[endpoint] = f"Status {response.status_code}"
                
        except Exception as e:
            print(f"      ❌ Error de conexión: {e}")
            resultados[endpoint] = f"Error: {e}"
    
    # Probar endpoint con filtros
    print("\n[3] Probando endpoint con filtros...")
    
    try:
        # Probar causas-cierre con filtro de tecnología
        filtro_url = f"{BASE_URL}/api/analistas/causas-cierre?tecnologia=FTTH"
        print(f"   Probando: {filtro_url}")
        
        response = session.get(filtro_url)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"      ✅ Filtro FTTH: {len(data)} resultados")
                    
                    # Verificar que todos los resultados tienen tecnología FTTH
                    if len(data) > 0:
                        ftth_count = sum(1 for item in data if isinstance(item, dict) and item.get('tecnologia') == 'FTTH')
                        print(f"      Verificación: {ftth_count}/{len(data)} elementos con tecnología FTTH")
                else:
                    print(f"      ⚠️ Respuesta no es lista")
            except:
                print(f"      ❌ Respuesta no es JSON válido")
        else:
            print(f"      ❌ Status: {response.status_code}")
            
    except Exception as e:
        print(f"      ❌ Error: {e}")
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE RESULTADOS")
    print("="*60)
    
    for endpoint, resultado in resultados.items():
        print(f"{endpoint}: {resultado}")
    
    # Verificar si el servidor está funcionando
    print("\n[4] Verificando estado del servidor...")
    try:
        response = session.get(f"{BASE_URL}/dashboard")
        if response.status_code == 200:
            print("   ✅ Servidor funcionando correctamente")
        else:
            print(f"   ⚠️ Dashboard status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error al verificar servidor: {e}")
    
    return True

if __name__ == "__main__":
    test_api_endpoints()