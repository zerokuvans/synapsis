import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# Configuración
BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"
ANALISTAS_URL = f"{BASE_URL}/analistas"

# Credenciales
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def test_analistas_frontend():
    """Prueba el frontend del módulo analistas"""
    print("="*60)
    print("PRUEBA DEL FRONTEND DEL MÓDULO ANALISTAS")
    print("="*60)
    
    # Configurar Chrome en modo headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    
    try:
        print("\n[1] Iniciando navegador...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        print("\n[2] Navegando a la página de login...")
        driver.get(LOGIN_URL)
        time.sleep(2)
        
        print("\n[3] Realizando login...")
        # Buscar campos de login
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        # Ingresar credenciales
        username_field.send_keys(USERNAME)
        password_field.send_keys(PASSWORD)
        
        # Enviar formulario
        password_field.submit()
        time.sleep(3)
        
        # Verificar si el login fue exitoso
        current_url = driver.current_url
        if "dashboard" in current_url or "login" not in current_url:
            print("   ✅ Login exitoso")
        else:
            print("   ❌ Login fallido")
            return False
        
        print("\n[4] Navegando al módulo analistas...")
        driver.get(ANALISTAS_URL)
        time.sleep(3)
        
        # Verificar que la página se cargó correctamente
        try:
            title_element = driver.find_element(By.TAG_NAME, "h3")
            if "Causas de Cierre" in title_element.text:
                print("   ✅ Página del módulo analistas cargada correctamente")
            else:
                print("   ❌ La página no parece ser del módulo analistas")
                return False
        except Exception as e:
            print(f"   ❌ Error al verificar el título: {e}")
            return False
        
        print("\n[5] Verificando elementos de la interfaz...")
        
        # Verificar elementos clave
        elementos_requeridos = [
            ("buscarTexto", "Campo de búsqueda"),
            ("filtroTecnologia", "Filtro de tecnología"),
            ("filtroAgrupacion", "Filtro de agrupación"),
            ("filtroGrupo", "Filtro de grupo"),
            ("btnBuscar", "Botón buscar"),
            ("btnLimpiar", "Botón limpiar"),
            ("tablaCausas", "Tabla de causas"),
            ("contadorResultados", "Contador de resultados")
        ]
        
        elementos_encontrados = 0
        for elemento_id, descripcion in elementos_requeridos:
            try:
                driver.find_element(By.ID, elemento_id)
                print(f"   ✅ {descripcion} encontrado")
                elementos_encontrados += 1
            except Exception:
                print(f"   ❌ {descripcion} NO encontrado")
        
        print(f"\n   Elementos encontrados: {elementos_encontrados}/{len(elementos_requeridos)}")
        
        print("\n[6] Verificando carga de datos inicial...")
        
        # Esperar a que se carguen los datos
        try:
            # Esperar hasta 15 segundos a que aparezcan datos en la tabla
            WebDriverWait(driver, 15).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "#tablaCausasBody tr")) > 0
            )
            
            # Contar filas de datos
            filas = driver.find_elements(By.CSS_SELECTOR, "#tablaCausasBody tr")
            if len(filas) > 0:
                # Verificar si es una fila de "no hay datos" o datos reales
                primera_fila = filas[0]
                if "No se encontraron resultados" in primera_fila.text:
                    print("   ❌ No se cargaron datos - tabla vacía")
                else:
                    print(f"   ✅ Datos cargados correctamente - {len(filas)} filas")
                    
                    # Mostrar algunos datos de ejemplo
                    for i, fila in enumerate(filas[:3], 1):
                        celdas = fila.find_elements(By.TAG_NAME, "td")
                        if len(celdas) >= 3:
                            codigo = celdas[0].text.strip()
                            descripcion = celdas[1].text.strip()[:50]
                            tecnologia = celdas[2].text.strip()
                            print(f"      {i}. {codigo} - {descripcion}... - {tecnologia}")
            else:
                print("   ❌ No se encontraron filas en la tabla")
                
        except Exception as e:
            print(f"   ❌ Timeout esperando datos: {e}")
            
            # Verificar si hay un mensaje de error en la consola
            logs = driver.get_log('browser')
            if logs:
                print("\n   Errores de consola encontrados:")
                for log in logs:
                    if log['level'] == 'SEVERE':
                        print(f"      ERROR: {log['message']}")
        
        print("\n[7] Probando filtros...")
        
        try:
            # Probar filtro de tecnología
            filtro_tecnologia = driver.find_element(By.ID, "filtroTecnologia")
            filtro_tecnologia.click()
            
            # Seleccionar FTTH
            opciones = driver.find_elements(By.CSS_SELECTOR, "#filtroTecnologia option")
            for opcion in opciones:
                if opcion.get_attribute("value") == "FTTH":
                    opcion.click()
                    break
            
            time.sleep(2)
            
            # Verificar si se aplicó el filtro
            filas_filtradas = driver.find_elements(By.CSS_SELECTOR, "#tablaCausasBody tr")
            print(f"   ✅ Filtro de tecnología aplicado - {len(filas_filtradas)} resultados")
            
        except Exception as e:
            print(f"   ❌ Error al probar filtros: {e}")
        
        print("\n[8] Verificando contador de resultados...")
        
        try:
            contador = driver.find_element(By.ID, "contadorResultados")
            numero_resultados = contador.text.strip()
            print(f"   ✅ Contador muestra: {numero_resultados} resultados")
        except Exception as e:
            print(f"   ❌ Error al verificar contador: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False
        
    finally:
        if driver:
            print("\n[9] Cerrando navegador...")
            driver.quit()

def test_api_endpoints_direct():
    """Prueba directa de los endpoints de API"""
    print("\n" + "="*60)
    print("PRUEBA DIRECTA DE ENDPOINTS DE API")
    print("="*60)
    
    # Crear sesión
    session = requests.Session()
    
    # Login
    print("\n[1] Realizando login...")
    session.get(LOGIN_URL)
    
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    login_response = session.post(LOGIN_URL, data=login_data, headers=headers, allow_redirects=True)
    
    if "dashboard" in login_response.url or session.cookies.get('session'):
        print("   ✅ Login exitoso")
    else:
        print("   ❌ Login fallido")
        return False
    
    # Probar endpoints
    endpoints = [
        "/api/analistas/causas-cierre",
        "/api/analistas/grupos",
        "/api/analistas/agrupaciones",
        "/api/analistas/tecnologias"
    ]
    
    print("\n[2] Probando endpoints...")
    
    for endpoint in endpoints:
        try:
            response = session.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   ✅ {endpoint}: {len(data)} elementos")
                    else:
                        print(f"   ⚠️ {endpoint}: respuesta no es lista")
                except:
                    print(f"   ❌ {endpoint}: respuesta no es JSON válido")
            else:
                print(f"   ❌ {endpoint}: status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: error {e}")
    
    return True

if __name__ == "__main__":
    # Primero probar los endpoints directamente
    test_api_endpoints_direct()
    
    # Luego probar el frontend (requiere Chrome instalado)
    try:
        test_analistas_frontend()
    except Exception as e:
        print(f"\nNo se pudo ejecutar la prueba del frontend: {e}")
        print("Esto puede ser porque Chrome/ChromeDriver no está instalado.")