import requests
from bs4 import BeautifulSoup
import re
import json

# Configuración
BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"
API_URL = f"{BASE_URL}/api/indicadores/cumplimiento"
PAGE_URL = f"{BASE_URL}/indicadores/api"

# Credenciales
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def verificar_html():
    """Verifica la estructura HTML y la carga de datos en la interfaz"""
    print("="*60)
    print("VERIFICADOR DE HTML Y CARGA DE DATOS")
    print("="*60)
    
    # Crear sesión
    session = requests.Session()
    
    # 1. Iniciar sesión
    print("\n[1] Iniciando sesión...")
    
    # Obtener cookies iniciales
    session.get(LOGIN_URL)
    
    # Enviar credenciales
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
        
        # Verificar login exitoso
        login_success = "dashboard" in login_response.url or session.cookies.get('session')
        
        if login_success:
            print(f"✅ Login exitoso como {USERNAME}")
        else:
            print(f"❌ Login fallido. URL: {login_response.url}")
            return False
            
    except Exception as e:
        print(f"❌ Error en el login: {str(e)}")
        return False
    
    # 2. Analizar la estructura HTML de la página
    print("\n[2] Analizando estructura HTML...")
    
    try:
        html_response = session.get(PAGE_URL)
        soup = BeautifulSoup(html_response.text, 'html.parser')
        
        # Verificar elementos clave
        elementos = [
            ('Formulario de filtros', soup.find('form', {'id': 'filtrosForm'})),
            ('Contenedor de indicadores', soup.find('div', {'id': 'indicadores-container'})),
            ('Botón de recarga', soup.find('button', {'id': 'recargar-indicadores'})),
            ('Tabla de indicadores', soup.find('table', {'id': 'tabla-indicadores'}))
        ]
        
        print("Elementos HTML encontrados:")
        for nombre, elemento in elementos:
            if elemento:
                print(f"   ✅ {nombre}: Presente")
            else:
                print(f"   ❌ {nombre}: No encontrado")
        
        # Buscar scripts en la página
        scripts = soup.find_all('script')
        print(f"\nScripts encontrados: {len(scripts)}")
        
        # Buscar funciones JavaScript importantes
        js_functions = []
        for script in scripts:
            if script.string:
                js_text = script.string
                functions = re.findall(r'function\s+(\w+)', js_text)
                js_functions.extend(functions)
                
                # Buscar específicamente cargarIndicadores
                if 'cargarIndicadores' in js_text:
                    print("   ✅ Función cargarIndicadores encontrada en scripts")
                
                # Buscar window.cargarIndicadores
                if 'window.cargarIndicadores' in js_text:
                    print("   ✅ Definición global window.cargarIndicadores encontrada")
                    
        if not any('cargarIndicadores' in func for func in js_functions):
            print("   ❌ No se encontró la función cargarIndicadores")
            
        # Analizar el contenido actual del contenedor de indicadores
        container = soup.find('div', {'id': 'indicadores-container'})
        if container:
            content = container.text.strip()
            print(f"\nContenido actual del contenedor de indicadores:")
            if content:
                print(f"   {content[:100]}..." if len(content) > 100 else f"   {content}")
            else:
                print("   (Contenedor vacío)")
                
            # Verificar si ya hay una tabla de datos
            tabla = container.find('table')
            if tabla:
                filas = tabla.find_all('tr')
                print(f"   Tabla con {len(filas)-1} filas de datos encontrada")
            
    except Exception as e:
        print(f"❌ Error al analizar HTML: {str(e)}")
    
    # 3. Verificar la respuesta de la API
    print("\n[3] Verificando respuesta de la API...")
    
    try:
        api_response = session.get(f"{API_URL}?fecha_inicio=2025-03-17&fecha_fin=2025-03-17")
        
        if api_response.status_code == 200:
            try:
                data = api_response.json()
                if data.get('success'):
                    indicadores = data.get('indicadores', [])
                    print(f"✅ API responde correctamente: {len(indicadores)} indicadores")
                    
                    # Guardar JSON para referencia
                    with open('api_output.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    print("   JSON guardado en api_output.json")
                    
                else:
                    print(f"❌ API reporta error: {data.get('error', 'Sin mensaje')}")
            except:
                print("❌ La respuesta de la API no es JSON válido")
        else:
            print(f"❌ Error en la API: Código {api_response.status_code}")
    except Exception as e:
        print(f"❌ Error al verificar API: {str(e)}")
    
    # 4. Sugerencias para arreglar el problema
    print("\n[4] DIAGNÓSTICO Y SUGERENCIAS")
    print("="*30)
    print("Si la API funciona pero los datos no se muestran en la interfaz, el problema podría ser:")
    print("1. La función cargarIndicadores no se está ejecutando al cargar la página")
    print("2. Hay errores JavaScript que impiden la ejecución correcta")
    print("3. La función no está actualizando correctamente el DOM")
    
    print("\nSUGERENCIAS DE CORRECCIÓN:")
    print("1. Agregar console.log para verificar la ejecución en la consola del navegador")
    print("2. Añadir try/catch alrededor de la llamada inicial a cargarIndicadores")
    print("3. Revisar en el navegador (F12) si hay errores en la consola JavaScript")
    print("4. Verificar que la respuesta JSON se está procesando correctamente")
    
    return True

if __name__ == "__main__":
    verificar_html() 