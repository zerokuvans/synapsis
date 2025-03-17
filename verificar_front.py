import requests
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.parse

# Configuración
BASE_URL = "http://127.0.0.1:8080"
API_URL = f"{BASE_URL}/api/indicadores/cumplimiento"
PAGE_URL = f"{BASE_URL}/indicadores/api"
LOGIN_URL = f"{BASE_URL}/"

# Credenciales
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def login_session():
    """Inicia sesión y devuelve una sesión activa"""
    print(f"Iniciando sesión como {USERNAME}...")
    session = requests.Session()
    
    # Obtener cookies iniciales
    session.get(LOGIN_URL)
    
    # Enviar credenciales
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
    
    if "dashboard" in response.url:
        print("✅ Login exitoso")
        return session
    else:
        print("❌ Error de login")
        return None

def analizar_frontend(session):
    """Analiza la estructura del frontend y cómo carga datos"""
    print("\n1. ANÁLISIS DE LA PÁGINA FRONTEND")
    print("===================================")
    
    response = session.get(PAGE_URL)
    
    if response.status_code != 200:
        print(f"❌ Error al cargar la página: {response.status_code}")
        return False
    
    print(f"✅ Página cargada correctamente ({len(response.text)} bytes)")
    
    # Parsear HTML para analizar
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Analizar el formulario de filtros
    form = soup.find('form', {'id': 'filtrosForm'})
    if form:
        print("✅ Formulario de filtros encontrado")
        inputs = form.find_all(['input', 'select'])
        print(f"   - Campos en el formulario: {len(inputs)}")
        for i in inputs:
            print(f"   - {i.get('name', 'Sin nombre')} ({i.get('type', 'select')})")
    else:
        print("❌ No se encontró el formulario de filtros")
    
    # Analizar el botón de recarga
    reload_button = soup.find('button', {'id': 'recargar-indicadores'})
    if reload_button:
        print("✅ Botón de recarga encontrado")
    else:
        print("❌ No se encontró el botón de recarga")
    
    # Analizar contenedores de resultados
    container = soup.find('div', {'id': 'indicadores-container'})
    if container:
        print("✅ Contenedor de indicadores encontrado")
        content = container.text.strip()
        print(f"   - Contenido inicial: {content[:100]}...")
    else:
        print("❌ No se encontró el contenedor de indicadores")
    
    # Analizar script JS
    scripts = soup.find_all('script')
    js_content = ""
    for script in scripts:
        if not script.get('src') and 'cargarIndicadores' in script.text:
            js_content = script.text
    
    if js_content:
        print("✅ Script para cargar indicadores encontrado")
        
        # Buscar la función de carga de indicadores
        function_match = re.search(r'function\s+cargarIndicadores\s*\([^)]*\)\s*{([^}]+)}', js_content, re.DOTALL)
        if function_match:
            print("✅ Función cargarIndicadores encontrada")
            function_text = function_match.group(1)
            
            # Analizar URL y parámetros
            url_pattern = re.search(r'url\s*=\s*[\'"]([^\'"]+)[\'"]', function_text)
            if url_pattern:
                print(f"   - URL base usada: {url_pattern.group(1)}")
            
            fetch_pattern = re.search(r'fetch\s*\(\s*([^)]+)\s*\)', function_text)
            if fetch_pattern:
                print(f"   - Llamada fetch: {fetch_pattern.group(1)}")
        else:
            print("❌ No se encontró la función cargarIndicadores")
    else:
        print("❌ No se encontró el script para cargar indicadores")
    
    return True

def analizar_api_directa(session):
    """Verifica la API directamente para comparar con lo que ve el frontend"""
    print("\n2. ANÁLISIS DE LA API DIRECTA")
    print("===========================")
    
    fecha = datetime.now().strftime("%Y-%m-%d")
    url = f"{API_URL}?fecha={fecha}"
    
    print(f"Consultando API para fecha {fecha}...")
    response = session.get(url)
    
    if response.status_code != 200:
        print(f"❌ Error al consultar API: {response.status_code}")
        return False
    
    try:
        data = response.json()
        
        if data.get('success', False):
            indicadores = data.get('indicadores', [])
            print(f"✅ API retorna {len(indicadores)} indicadores")
            
            # Mostrar primeros indicadores
            for i, ind in enumerate(indicadores[:3]):
                print(f"   {i+1}. {ind.get('supervisor', 'N/A')}: {ind.get('porcentaje_cumplimiento', 0):.2f}%")
            
            return data
        else:
            print(f"❌ API reporta error: {data.get('error', 'Desconocido')}")
            return False
    except:
        print(f"❌ Error al parsear respuesta JSON")
        return False

def simular_llamada_frontend(session):
    """Simula exactamente la misma llamada que haría el frontend"""
    print("\n3. SIMULACIÓN DE LLAMADA DEL FRONTEND")
    print("===================================")
    
    # Obtener la página primero
    response = session.get(PAGE_URL)
    
    if response.status_code != 200:
        print(f"❌ Error al cargar la página: {response.status_code}")
        return
    
    # Parsear HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Obtener valores iniciales de los campos del formulario
    fecha_inicio = None
    fecha_fin = None
    supervisor = None
    
    form = soup.find('form', {'id': 'filtrosForm'})
    if form:
        fecha_inicio_input = form.find('input', {'id': 'fecha_inicio'})
        if fecha_inicio_input:
            fecha_inicio = fecha_inicio_input.get('value')
            
        fecha_fin_input = form.find('input', {'id': 'fecha_fin'})
        if fecha_fin_input:
            fecha_fin = fecha_fin_input.get('value')
            
        supervisor_select = form.find('select', {'id': 'supervisor'})
        if supervisor_select and supervisor_select.find('option', {'selected': True}):
            supervisor = supervisor_select.find('option', {'selected': True}).get('value')
    
    # Construir URL con los mismos parámetros que usaría el frontend
    url = f"{API_URL}?"
    params = []
    
    if fecha_inicio:
        params.append(f"fecha_inicio={fecha_inicio}")
    
    if fecha_fin:
        params.append(f"fecha_fin={fecha_fin}")
    
    if supervisor:
        params.append(f"supervisor={urllib.parse.quote(supervisor)}")
    
    if not params:  # Si no hay parámetros, usar fecha actual
        fecha = datetime.now().strftime("%Y-%m-%d")
        params.append(f"fecha={fecha}")
    
    url += "&".join(params)
    
    print(f"Simulando llamada frontend a: {url}")
    
    # Realizar petición
    response = session.get(url)
    
    if response.status_code != 200:
        print(f"❌ Error al hacer la petición: {response.status_code}")
        return
    
    try:
        data = response.json()
        
        if data.get('success', False):
            indicadores = data.get('indicadores', [])
            print(f"✅ Simulación exitosa: {len(indicadores)} indicadores obtenidos")
            
            # Comparar con llamada directa a la API
            if len(indicadores) > 0:
                print("   Los datos existen y deberían mostrarse en la interfaz")
            else:
                print("   No hay datos para los parámetros seleccionados")
        else:
            print(f"❌ La API reportó error: {data.get('error', 'Desconocido')}")
    except:
        print("❌ Error al parsear la respuesta como JSON")
        print(response.text[:200])

def verificar_headers(session):
    """Verifica si hay problemas con los headers o CORS"""
    print("\n4. VERIFICACIÓN DE HEADERS Y CORS")
    print("===============================")
    
    # Hacer una petición OPTIONS para verificar CORS
    try:
        response = session.options(API_URL)
        print(f"Petición OPTIONS: {response.status_code}")
        
        if 'Access-Control-Allow-Origin' in response.headers:
            print(f"✅ CORS configurado: {response.headers['Access-Control-Allow-Origin']}")
        else:
            print("ℹ️ No se detectaron headers CORS (normal para aplicaciones en mismo dominio)")
    except:
        print("❌ Error al hacer petición OPTIONS")
    
    # Verificar headers de la petición normal
    response = session.get(API_URL)
    print("\nHeaders de respuesta:")
    for key, value in response.headers.items():
        print(f"   {key}: {value}")
    
    # Verificar Content-Type
    if 'Content-Type' in response.headers:
        content_type = response.headers['Content-Type']
        if 'application/json' in content_type:
            print("✅ Content-Type correcto: application/json")
        else:
            print(f"❌ Content-Type incorrecto: {content_type}")
    else:
        print("❌ No se encontró Content-Type en la respuesta")

if __name__ == "__main__":
    session = login_session()
    
    if not session:
        print("No se pudo iniciar sesión. Terminando.")
        exit(1)
    
    # Analizar cómo está estructurado el frontend
    analizar_frontend(session)
    
    # Verificar si la API devuelve datos directamente
    api_data = analizar_api_directa(session)
    
    # Simular la misma llamada que haría el frontend
    simular_llamada_frontend(session)
    
    # Verificar headers y posibles problemas CORS
    verificar_headers(session)
    
    print("\nCONCLUSIÓN")
    print("==========")
    if api_data and isinstance(api_data, dict) and api_data.get('success') and len(api_data.get('indicadores', [])) > 0:
        print("✅ La API funciona correctamente y devuelve datos")
        print("✅ Si los datos no se muestran en la interfaz, el problema probablemente está en el JavaScript")
        print("   Recomendación: Revisar la consola del navegador para ver errores")
    else:
        print("❌ La API no devuelve datos correctamente")
        print("   Recomendación: Verificar implementación en backend") 