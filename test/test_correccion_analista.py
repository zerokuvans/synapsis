import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time

# Configuración
BASE_URL = "http://127.0.0.1:8080"
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def test_correccion_analista():
    """Probar que la corrección del dropdown de analista funciona"""
    print("="*70)
    print("PRUEBA DE CORRECCIÓN DEL DROPDOWN DE ANALISTA")
    print("="*70)
    
    # Configurar el navegador
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Ejecutar en modo headless
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(BASE_URL)
        
        print("\n[1] Realizando login...")
        
        # Hacer login
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        
        username_field.send_keys(USERNAME)
        password_field.send_keys(PASSWORD)
        
        # Enviar formulario
        login_form = driver.find_element(By.TAG_NAME, "form")
        login_form.submit()
        
        # Esperar a que se cargue el dashboard
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Usuarios"))
        )
        print("   ✅ Login exitoso")
        
        print("\n[2] Navegando a la página de usuarios...")
        
        # Ir a la página de usuarios
        usuarios_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Usuarios")
        usuarios_link.click()
        
        # Esperar a que se cargue la tabla
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "usuariosTable"))
        )
        print("   ✅ Página de usuarios cargada")
        
        print("\n[3] Buscando y editando el técnico ALARCON SALAS LUIS HERNANDO...")
        
        # Buscar el técnico en la tabla
        time.sleep(2)  # Esperar a que se carguen los datos
        
        # Buscar el botón de editar para el técnico con cédula 1019112308
        edit_buttons = driver.find_elements(By.CSS_SELECTOR, "button[onclick*='editarUsuario']")
        
        tecnico_encontrado = False
        for button in edit_buttons:
            onclick_attr = button.get_attribute('onclick')
            if '11' in onclick_attr:  # ID del técnico
                button.click()
                tecnico_encontrado = True
                break
        
        if not tecnico_encontrado:
            print("   ❌ No se encontró el técnico para editar")
            return False
        
        # Esperar a que se abra el modal de edición
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "editModal"))
        )
        
        # Esperar un poco más para que se carguen los datos
        time.sleep(3)
        
        print("   ✅ Modal de edición abierto")
        
        print("\n[4] Verificando el dropdown de analista...")
        
        # Obtener el dropdown de analista
        analista_select = Select(driver.find_element(By.ID, "edit_analista"))
        
        # Verificar las opciones disponibles
        options = analista_select.options
        print(f"   📋 Opciones disponibles en el dropdown ({len(options)}):")
        for i, option in enumerate(options):
            print(f"      {i}. Value: '{option.get_attribute('value')}' | Text: '{option.text}'")
        
        # Verificar cuál está seleccionada
        selected_option = analista_select.first_selected_option
        print(f"\n   🔍 Opción seleccionada:")
        print(f"      Value: '{selected_option.get_attribute('value')}'")
        print(f"      Text: '{selected_option.text}'")
        
        # Verificar si ESPITIA BARON LICED JOANA está seleccionada
        if selected_option.get_attribute('value') == 'ESPITIA BARON LICED JOANA':
            print("   ✅ ¡CORRECCIÓN EXITOSA! ESPITIA BARON LICED JOANA está seleccionada")
            return True
        else:
            print("   ❌ La analista no está seleccionada correctamente")
            return False
        
    except Exception as e:
        print(f"   ❌ Error durante la prueba: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()

def test_api_simple():
    """Prueba simple de los endpoints API"""
    print("\n[5] Prueba simple de endpoints...")
    
    session = requests.Session()
    
    # Login
    session.get(f"{BASE_URL}/")
    login_data = {"username": USERNAME, "password": PASSWORD}
    headers = {"X-Requested-With": "XMLHttpRequest", "Content-Type": "application/x-www-form-urlencoded"}
    session.post(f"{BASE_URL}/", data=login_data, headers=headers, allow_redirects=True)
    
    # Probar /obtener_usuario/11
    response = session.get(f"{BASE_URL}/obtener_usuario/11")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ /obtener_usuario/11 - Analista: '{data.get('analista')}'")
    else:
        print(f"   ❌ /obtener_usuario/11 falló: {response.status_code}")
    
    # Probar /api/analistas
    response = session.get(f"{BASE_URL}/api/analistas")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            analistas = data.get('analistas', [])
            espitia = next((a for a in analistas if 'ESPITIA' in a.get('nombre', '')), None)
            if espitia:
                print(f"   ✅ /api/analistas - ESPITIA encontrada: '{espitia.get('nombre')}'")
            else:
                print(f"   ❌ /api/analistas - ESPITIA no encontrada")
        else:
            print(f"   ❌ /api/analistas - Error: {data.get('message')}")
    else:
        print(f"   ❌ /api/analistas falló: {response.status_code}")

if __name__ == "__main__":
    # Ejecutar prueba simple primero
    test_api_simple()
    
    # Luego la prueba completa con Selenium
    print("\n" + "="*70)
    print("INICIANDO PRUEBA CON SELENIUM...")
    print("="*70)
    
    try:
        resultado = test_correccion_analista()
        
        print("\n" + "="*70)
        print("RESULTADO FINAL")
        print("="*70)
        
        if resultado:
            print("🎉 ¡ÉXITO! La corrección funciona correctamente.")
            print("   El dropdown de analista ahora muestra a ESPITIA BARON LICED JOANA")
            print("   como opción seleccionada para el técnico ALARCON SALAS LUIS HERNANDO.")
        else:
            print("❌ La corrección no funcionó como se esperaba.")
            print("   Revisar manualmente el formulario de edición.")
            
    except Exception as e:
        print(f"❌ Error al ejecutar la prueba con Selenium: {e}")
        print("   Nota: Selenium requiere ChromeDriver instalado.")
        print("   La corrección del código JavaScript debería funcionar de todas formas."