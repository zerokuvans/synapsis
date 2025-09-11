import requests
import json
from bs4 import BeautifulSoup

# Configuración
BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"  # La ruta de login es la raíz
DEVOLUCIONES_URL = f"{BASE_URL}/logistica/devoluciones_dotacion"
REGISTRAR_URL = f"{BASE_URL}/logistica/registrar_devolucion_dotacion"

def test_devoluciones_form():
    session = requests.Session()
    
    try:
        print("=== INICIANDO PRUEBA DE FORMULARIO DEVOLUCIONES ===")
        
        # 1. Obtener página de login
        print("\n1. Obteniendo página de login...")
        login_page = session.get(LOGIN_URL)
        print(f"Status: {login_page.status_code}")
        
        # 2. Hacer login con usuario de logística
        print("\n2. Haciendo login con usuario de logística...")
        login_data = {
            'username': 'test_logistica',
            'password': '123456'
        }
        
        login_response = session.post(LOGIN_URL, data=login_data)
        print(f"Login status: {login_response.status_code}")
        print(f"Login URL final: {login_response.url}")
        
        # 3. Acceder al formulario de devoluciones
        print("\n3. Accediendo al formulario de devoluciones...")
        form_response = session.get(DEVOLUCIONES_URL)
        print(f"Formulario status: {form_response.status_code}")
        print(f"Formulario URL: {form_response.url}")
        
        if form_response.status_code == 200:
            print("✓ Formulario cargado exitosamente")
            
            # Parsear HTML para verificar datos
            soup = BeautifulSoup(form_response.text, 'html.parser')
            
            # Verificar clientes
            cliente_select = soup.find('select', {'name': 'cliente_id'})
            if cliente_select:
                options = cliente_select.find_all('option')
                print(f"\n📋 Clientes disponibles: {len(options)-1}")  # -1 por la opción vacía
                for i, option in enumerate(options[1:6]):  # Mostrar primeros 5
                    print(f"  {i+1}. ID: {option.get('value')}, Nombre: {option.text.strip()}")
            
            # Verificar técnicos
            tecnico_select = soup.find('select', {'name': 'tecnico_id'})
            if tecnico_select:
                options = tecnico_select.find_all('option')
                print(f"\n👷 Técnicos disponibles: {len(options)-1}")
                for i, option in enumerate(options[1:4]):  # Mostrar primeros 3
                    print(f"  {i+1}. ID: {option.get('value')}, Nombre: {option.text.strip()}")
            
            # 4. Probar envío del formulario
            print("\n4. Probando envío del formulario...")
            
            # Datos de prueba
            form_data = {
                'tecnico_id': '1',  # Primer técnico
                'cliente_id': '1',  # Primer cliente
                'fecha_devolucion': '2024-01-15',
                'motivo': 'RENUNCIA',
                'observaciones': 'Prueba de formulario - usuario renunció',
                'estado': 'REGISTRADA'
            }
            
            submit_response = session.post(REGISTRAR_URL, data=form_data)
            print(f"Envío status: {submit_response.status_code}")
            print(f"Envío URL final: {submit_response.url}")
            
            if submit_response.status_code == 200:
                print("✓ Formulario enviado exitosamente")
                
                # Verificar si hay mensajes de éxito o error
                soup_result = BeautifulSoup(submit_response.text, 'html.parser')
                alerts = soup_result.find_all('div', class_=['alert', 'flash-message'])
                
                if alerts:
                    for alert in alerts:
                        print(f"📢 Mensaje: {alert.text.strip()}")
                else:
                    print("ℹ️ No se encontraron mensajes de respuesta")
            else:
                print(f"❌ Error al enviar formulario: {submit_response.status_code}")
                print(f"Contenido: {submit_response.text[:500]}...")
        
        else:
            print(f"❌ Error al cargar formulario: {form_response.status_code}")
            print(f"Contenido: {form_response.text[:500]}...")
    
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")

if __name__ == "__main__":
    test_devoluciones_form()