import requests
import json
from bs4 import BeautifulSoup

def test_vencimientos_con_login():
    """Prueba completa del endpoint de vencimientos con login"""
    
    base_url = "http://127.0.0.1:8080"
    session = requests.Session()
    
    print("=== PRUEBA COMPLETA DEL ENDPOINT DE VENCIMIENTOS ===")
    print(f"URL base: {base_url}")
    
    try:
        # 1. Obtener la página de login para el token CSRF
        print("\n1. Obteniendo página de login...")
        login_page = session.get(f"{base_url}/")
        print(f"Status de página de login: {login_page.status_code}")
        
        if login_page.status_code != 200:
            print(f"Error: No se pudo obtener la página de login. Status: {login_page.status_code}")
            return
        
        # 2. Extraer token CSRF si existe
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = None
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if csrf_input:
            csrf_token = csrf_input.get('value')
            print(f"Token CSRF encontrado: {csrf_token[:20]}...")
        else:
            print("No se encontró token CSRF")
        
        # 3. Intentar login con diferentes usuarios
        usuarios_prueba = [
            {'username': 'admin', 'password': 'admin123'},
            {'username': '1234567890', 'password': 'password123'},
            {'username': 'test', 'password': 'test123'}
        ]
        
        login_exitoso = False
        
        for usuario in usuarios_prueba:
            print(f"\n2. Intentando login con usuario: {usuario['username']}")
            
            # Preparar datos de login
            login_data = {
                'username': usuario['username'],
                'password': usuario['password']
            }
            
            if csrf_token:
                login_data['csrf_token'] = csrf_token
            
            # Realizar login
            login_response = session.post(
                f"{base_url}/",
                data=login_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                allow_redirects=False
            )
            
            print(f"Status de login: {login_response.status_code}")
            print(f"Headers de respuesta: {dict(login_response.headers)}")
            
            # Verificar si el login fue exitoso
            if login_response.status_code == 200:
                try:
                    response_json = login_response.json()
                    if response_json.get('status') == 'success':
                        print(f"✓ Login exitoso con usuario: {usuario['username']}")
                        print(f"Datos del usuario: {response_json}")
                        login_exitoso = True
                        break
                    else:
                        print(f"✗ Login fallido: {response_json.get('message', 'Error desconocido')}")
                except json.JSONDecodeError:
                    print("✗ Respuesta no es JSON válido")
                    print(f"Contenido de respuesta: {login_response.text[:200]}...")
            elif login_response.status_code == 302:
                print("✓ Login exitoso (redirección detectada)")
                login_exitoso = True
                break
            else:
                print(f"✗ Login fallido con status: {login_response.status_code}")
        
        if not login_exitoso:
            print("\n❌ No se pudo hacer login con ningún usuario. Probando acceso directo al endpoint...")
        
        # 4. Probar el endpoint de vencimientos
        print("\n3. Probando endpoint de vencimientos...")
        vencimientos_url = f"{base_url}/api/vehiculos/vencimientos"
        
        # Probar con diferentes métodos
        for metodo in ['GET', 'POST']:
            print(f"\n   Probando método {metodo}:")
            
            if metodo == 'GET':
                response = session.get(vencimientos_url)
            else:
                response = session.post(vencimientos_url, json={})
            
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✓ Respuesta JSON válida")
                    print(f"   Estructura de datos: {type(data)}")
                    
                    if isinstance(data, dict):
                        print(f"   Claves en respuesta: {list(data.keys())}")
                        if 'vencimientos' in data:
                            vencimientos = data['vencimientos']
                            print(f"   Número de vencimientos: {len(vencimientos)}")
                            if vencimientos:
                                print(f"   Primer vencimiento: {vencimientos[0]}")
                        elif 'data' in data:
                            print(f"   Datos encontrados: {len(data['data'])} registros")
                    elif isinstance(data, list):
                        print(f"   Lista con {len(data)} elementos")
                        if data:
                            print(f"   Primer elemento: {data[0]}")
                    
                except json.JSONDecodeError:
                    print(f"   ✗ Respuesta no es JSON válido")
                    print(f"   Contenido: {response.text[:200]}...")
            else:
                print(f"   ✗ Error en endpoint: {response.status_code}")
                print(f"   Contenido: {response.text[:200]}...")
        
        # 5. Verificar cookies de sesión
        print("\n4. Verificando cookies de sesión:")
        cookies = session.cookies.get_dict()
        print(f"Cookies activas: {list(cookies.keys())}")
        
        # 6. Probar acceso a dashboard para verificar autenticación
        print("\n5. Verificando acceso al dashboard:")
        dashboard_response = session.get(f"{base_url}/dashboard")
        print(f"Status dashboard: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            print("✓ Acceso al dashboard exitoso - Usuario autenticado")
        else:
            print("✗ No se pudo acceder al dashboard - Posible problema de autenticación")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. Verifique que esté ejecutándose en el puerto 8080")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vencimientos_con_login()