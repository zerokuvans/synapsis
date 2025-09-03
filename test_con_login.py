import requests
import json
from bs4 import BeautifulSoup

def test_con_login():
    """Probar el endpoint de vencimientos con login completo"""
    print("=== PRUEBA CON LOGIN COMPLETO ===")
    
    base_url = "http://localhost:8080"
    login_url = f"{base_url}/login"
    endpoint = f"{base_url}/api/vehiculos/vencimientos"
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        print("\n1. OBTENIENDO PÁGINA DE LOGIN:")
        
        # Obtener la página de login
        login_page = session.get(login_url)
        print(f"   Status: {login_page.status_code}")
        
        if login_page.status_code == 200:
            # Parsear el HTML para obtener el token CSRF si existe
            soup = BeautifulSoup(login_page.content, 'html.parser')
            csrf_token = None
            
            # Buscar token CSRF
            csrf_input = soup.find('input', {'name': 'csrf_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
                print(f"   ✓ Token CSRF encontrado: {csrf_token[:20]}...")
            else:
                print("   ⚠️  No se encontró token CSRF")
            
            print("\n2. INTENTANDO LOGIN:")
            
            # Datos de login (usando credenciales de prueba)
            login_data = {
                'username': 'admin',
                'password': 'admin'
            }
            
            if csrf_token:
                login_data['csrf_token'] = csrf_token
            
            # Intentar login
            login_response = session.post(login_url, data=login_data)
            print(f"   Status después del login: {login_response.status_code}")
            
            # Verificar si el login fue exitoso
            if login_response.status_code == 200 and 'login' not in login_response.url.lower():
                print("   ✓ Login exitoso")
            elif login_response.status_code == 302:
                print(f"   ✓ Redirección después del login: {login_response.headers.get('Location', 'No especificada')}")
            else:
                print("   ⚠️  Login posiblemente fallido")
            
            print("\n3. PROBANDO ENDPOINT DESPUÉS DEL LOGIN:")
            
            # Probar el endpoint después del login
            endpoint_response = session.get(endpoint)
            print(f"   Status: {endpoint_response.status_code}")
            print(f"   Content-Type: {endpoint_response.headers.get('content-type', 'No especificado')}")
            
            if endpoint_response.status_code == 200:
                try:
                    data = endpoint_response.json()
                    print(f"   ✓ Respuesta JSON válida")
                    print(f"   ✓ Número de registros: {len(data) if isinstance(data, list) else 'No es lista'}")
                    
                    if isinstance(data, list):
                        if len(data) > 0:
                            print("\n   Primeros 2 registros:")
                            for i, registro in enumerate(data[:2]):
                                print(f"     {i+1}. {json.dumps(registro, indent=8, ensure_ascii=False)}")
                                
                            # Contar estados
                            estados = {}
                            for registro in data:
                                if 'soat_estado' in registro:
                                    estado = registro['soat_estado']
                                    estados[f'SOAT_{estado}'] = estados.get(f'SOAT_{estado}', 0) + 1
                                if 'tecnomecanica_estado' in registro:
                                    estado = registro['tecnomecanica_estado']
                                    estados[f'TECNO_{estado}'] = estados.get(f'TECNO_{estado}', 0) + 1
                            
                            print("\n   📊 RESUMEN DE ESTADOS:")
                            for estado, count in estados.items():
                                print(f"     - {estado}: {count}")
                                
                            # Mostrar vencimientos críticos
                            criticos = [r for r in data if 
                                       (r.get('soat_estado') in ['vencido', 'critico']) or 
                                       (r.get('tecnomecanica_estado') in ['vencido', 'critico'])]
                            
                            if criticos:
                                print(f"\n   🚨 VENCIMIENTOS CRÍTICOS: {len(criticos)}")
                                for critico in criticos[:3]:
                                    placa = critico.get('placa', 'N/A')
                                    soat_estado = critico.get('soat_estado', 'N/A')
                                    tecno_estado = critico.get('tecnomecanica_estado', 'N/A')
                                    print(f"     - {placa}: SOAT={soat_estado}, TECNO={tecno_estado}")
                            else:
                                print("\n   ✅ No hay vencimientos críticos")
                                
                        else:
                            print("   ⚠️  Lista vacía - No hay datos de vencimientos")
                    else:
                        print(f"   ⚠️  Respuesta no es una lista: {type(data)}")
                        
                except json.JSONDecodeError:
                    print("   ❌ La respuesta no es JSON válido")
                    content = endpoint_response.text[:300]
                    print(f"   Contenido: {content}")
                    
            elif endpoint_response.status_code == 401:
                print("   ❌ Error 401: Aún no autorizado")
            elif endpoint_response.status_code == 403:
                print("   ❌ Error 403: Sin permisos (rol requerido)")
            else:
                print(f"   ❌ Error {endpoint_response.status_code}")
                
        else:
            print(f"   ❌ No se pudo obtener la página de login: {login_page.status_code}")
            
        print("\n4. PROBANDO OTROS USUARIOS:")
        
        # Probar con otros usuarios comunes
        usuarios_prueba = [
            ('1019112308', '1019112308'),
            ('admin', '123456'),
            ('logistica', 'logistica')
        ]
        
        for username, password in usuarios_prueba:
            print(f"\n   Probando {username}:")
            
            # Nueva sesión para cada usuario
            test_session = requests.Session()
            
            # Obtener página de login
            test_login_page = test_session.get(login_url)
            if test_login_page.status_code == 200:
                test_soup = BeautifulSoup(test_login_page.content, 'html.parser')
                test_csrf = None
                test_csrf_input = test_soup.find('input', {'name': 'csrf_token'})
                if test_csrf_input:
                    test_csrf = test_csrf_input.get('value')
                
                test_login_data = {
                    'username': username,
                    'password': password
                }
                if test_csrf:
                    test_login_data['csrf_token'] = test_csrf
                
                test_login_response = test_session.post(login_url, data=test_login_data)
                
                if test_login_response.status_code in [200, 302]:
                    test_endpoint_response = test_session.get(endpoint)
                    if test_endpoint_response.status_code == 200:
                        try:
                            test_data = test_endpoint_response.json()
                            print(f"     ✅ Login exitoso - {len(test_data) if isinstance(test_data, list) else 'No lista'} registros")
                            break
                        except:
                            print(f"     ⚠️  Login posible pero respuesta no JSON")
                    else:
                        print(f"     ❌ Endpoint: {test_endpoint_response.status_code}")
                else:
                    print(f"     ❌ Login falló: {test_login_response.status_code}")
            
        print("\n✅ PRUEBA COMPLETADA")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")

if __name__ == "__main__":
    test_con_login()