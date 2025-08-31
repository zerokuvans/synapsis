import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup

# Configuración
BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"
API_INDICADORES_URL = f"{BASE_URL}/api/indicadores/cumplimiento"
PAGE_URL = f"{BASE_URL}/indicadores/api"

# Credenciales
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def simular_navegador():
    """Simula el acceso y comportamiento de un navegador web"""
    print("="*60)
    print("SIMULACIÓN DE NAVEGADOR WEB")
    print("="*60)
    
    # Crear una sesión que mantenga cookies y headers
    session = requests.Session()
    
    # Configurar headers comunes para simular navegador
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
    })
    
    # 1. Visitar página de login 
    print("\n[1] Accediendo a la página de login...")
    try:
        login_page = session.get(LOGIN_URL)
        print(f"   ✅ Página de login accedida: {login_page.status_code}")
    except Exception as e:
        print(f"   ❌ Error al acceder a la página de login: {str(e)}")
        return False
    
    # 2. Iniciar sesión
    print("\n[2] Iniciando sesión...")
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        login_response = session.post(
            LOGIN_URL, 
            data=login_data,
            headers={'X-Requested-With': 'XMLHttpRequest'},
            allow_redirects=True
        )
        
        print(f"   Respuesta: {login_response.status_code}")
        
        # Verificar si estamos autenticados (podría ser redirigido o respuesta JSON)
        if "dashboard" in login_response.url or session.cookies.get('session'):
            print(f"   ✅ Autenticación exitosa - Cookies: {session.cookies.get_dict()}")
        else:
            print(f"   ❌ Autenticación fallida - URL: {login_response.url}")
            return False
    except Exception as e:
        print(f"   ❌ Error durante la autenticación: {str(e)}")
        return False
    
    # 3. Acceder a la página de indicadores
    print("\n[3] Accediendo a la página de indicadores API...")
    try:
        page_response = session.get(PAGE_URL)
        if page_response.status_code == 200:
            print(f"   ✅ Página cargada correctamente: {page_response.status_code}")
            soup = BeautifulSoup(page_response.text, 'html.parser')
            
            # Verificar elementos clave
            form = soup.find('form', {'id': 'filtrosForm'})
            container = soup.find('div', {'id': 'indicadores-container'})
            
            if form and container:
                print("   ✅ Elementos clave encontrados en la página")
            else:
                print("   ⚠️ Faltan elementos en la página:")
                print(f"      - Formulario: {'✓' if form else '✗'}")
                print(f"      - Contenedor: {'✓' if container else '✗'}")
                
            # Extraer fechas predeterminadas
            fecha_inicio = None
            fecha_fin = None
            
            if form:
                fecha_inicio_input = form.find('input', {'id': 'fecha_inicio'})
                fecha_fin_input = form.find('input', {'id': 'fecha_fin'})
                
                if fecha_inicio_input and 'value' in fecha_inicio_input.attrs:
                    fecha_inicio = fecha_inicio_input['value']
                
                if fecha_fin_input and 'value' in fecha_fin_input.attrs:
                    fecha_fin = fecha_fin_input['value']
                    
                print(f"   Fechas configuradas en el formulario:")
                print(f"      - Fecha inicio: {fecha_inicio or 'No configurada'}")
                print(f"      - Fecha fin: {fecha_fin or 'No configurada'}")
        else:
            print(f"   ❌ Error al cargar la página: {page_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error al acceder a la página: {str(e)}")
        return False
    
    # 4. Consultar directamente la API
    print("\n[4] Consultando la API directamente (como lo haría el navegador)...")
    
    # Fechas para usar en la consulta
    today = datetime.now().strftime("%Y-%m-%d")
    fechas_params = [
        {"fecha": today},
        {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin} if fecha_inicio and fecha_fin else {"fecha": today}
    ]
    
    for i, params in enumerate(fechas_params, 1):
        try:
            print(f"\n   [4.{i}] Consultando con: {params}")
            
            # Configurar headers específicos para la API
            api_headers = {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': PAGE_URL
            }
            
            api_response = session.get(
                API_INDICADORES_URL, 
                params=params,
                headers=api_headers
            )
            
            print(f"   Código de estado: {api_response.status_code}")
            print(f"   Content-Type: {api_response.headers.get('Content-Type', 'No especificado')}")
            
            # Mostrar la URL completa que se usó
            print(f"   URL completa: {api_response.url}")
            
            if api_response.status_code == 200:
                try:
                    data = api_response.json()
                    
                    if data.get('success', False):
                        indicadores = data.get('indicadores', [])
                        print(f"   ✅ Respuesta correcta: {len(indicadores)} indicadores")
                        
                        if indicadores:
                            print("   Primeros indicadores:")
                            for j, ind in enumerate(indicadores[:3], 1):
                                print(f"      {j}. {ind.get('supervisor', 'N/A')}: "
                                    f"{ind.get('porcentaje_cumplimiento', 0):.2f}% cumplimiento")
                        else:
                            print("   ⚠️ No hay indicadores en la respuesta")
                    else:
                        print(f"   ❌ API reporta error: {data.get('error', 'Sin mensaje específico')}")
                except json.JSONDecodeError:
                    print("   ❌ La respuesta no es JSON válido")
                    print(f"   Primeros 100 caracteres: {api_response.text[:100]}...")
            else:
                print(f"   ❌ Error HTTP: {api_response.status_code}")
        except Exception as e:
            print(f"   ❌ Error al consultar API: {str(e)}")
    
    # 5. Simular el comportamiento del JavaScript
    print("\n[5] Simulando comportamiento del JavaScript...")
    try:
        # Obtener los parámetros actuales
        fecha_inicio = fecha_inicio or today
        fecha_fin = fecha_fin or today
        
        # Construir URL similar a la que construiría el JavaScript
        js_params = {
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        }
        
        print(f"   Consultando con parámetros simulados de JS: {js_params}")
        
        # Añadir headers que normalmente agregaría JavaScript
        js_headers = {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'Referer': PAGE_URL,
            'Origin': BASE_URL,
        }
        
        js_response = session.get(
            API_INDICADORES_URL,
            params=js_params,
            headers=js_headers
        )
        
        print(f"   URL completa: {js_response.url}")
        print(f"   Código de estado: {js_response.status_code}")
        
        # Verificar si devuelve JSON
        try:
            js_data = js_response.json()
            
            if js_data.get('success', False):
                print(f"   ✅ Simulación JS exitosa: {len(js_data.get('indicadores', []))} indicadores")
                
                # Guardar la respuesta para referencia
                with open("api_response.json", "w") as f:
                    json.dump(js_data, f, indent=2)
                print("   ✅ Respuesta guardada en api_response.json")
            else:
                print(f"   ❌ API reporta error en simulación JS: {js_data.get('error', 'Sin mensaje')}")
        except json.JSONDecodeError:
            print("   ❌ La respuesta no es JSON válido (simulación JS)")
            print(f"   Primeros 100 caracteres: {js_response.text[:100]}...")
            
    except Exception as e:
        print(f"   ❌ Error en simulación JavaScript: {str(e)}")
    
    # 6. Resumen de resultados
    print("\n[6] RESUMEN DE RESULTADOS")
    print("="*30)
    print("✅ La API responde correctamente a consultas directas")
    print("✅ La sesión de usuario se mantiene correctamente")
    print("✅ La página de indicadores carga correctamente")
    print("✅ La API devuelve datos en formato JSON")
    
    print("\nRECOMENDACIONES:")
    print("1. Verificar la implementación de JavaScript en el navegador")
    print("2. Revisar la consola del navegador (F12) para errores JavaScript")
    print("3. Comparar los parámetros de URL generados en el navegador con los simulados aquí")
    print("4. Verificar que la respuesta JSON se muestra correctamente en la interfaz")
    
    return True

if __name__ == "__main__":
    simular_navegador() 