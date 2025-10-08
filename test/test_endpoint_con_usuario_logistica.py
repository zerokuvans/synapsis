import requests
import mysql.connector
from mysql.connector import Error
from bs4 import BeautifulSoup
import json

def test_endpoint_vencimientos():
    """Prueba el endpoint /api/vehiculos/vencimientos con usuario de logística"""
    
    base_url = "http://127.0.0.1:8080"
    session = requests.Session()
    
    print("=== PRUEBA DEL ENDPOINT /api/vehiculos/vencimientos ===")
    print(f"URL base: {base_url}")
    
    try:
        # 1. Obtener la página de login para extraer CSRF token
        print("\n1. Obteniendo página de login...")
        login_page = session.get(base_url)
        
        if login_page.status_code != 200:
            print(f"❌ Error al obtener página de login: {login_page.status_code}")
            return
            
        # Extraer CSRF token si existe
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = None
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if csrf_input:
            csrf_token = csrf_input.get('value')
            print(f"✓ CSRF token encontrado: {csrf_token[:20]}...")
        else:
            print("⚠️ No se encontró CSRF token")
        
        # 2. Intentar login con usuario de logística
        usuarios_logistica = [
            {'username': '1002407101', 'nombre': 'DIANA CAROLINA SOSA'},
            {'username': 'test123', 'nombre': 'Usuario Test'}
        ]
        
        login_exitoso = False
        usuario_actual = None
        
        for usuario in usuarios_logistica:
            print(f"\n2. Intentando login con {usuario['nombre']} ({usuario['username']})...")
            
            # Datos de login
            login_data = {
                'username': usuario['username'],
                'password': '123456'  # Contraseña común de prueba
            }
            
            if csrf_token:
                login_data['csrf_token'] = csrf_token
            
            # Realizar login
            login_response = session.post(base_url, data=login_data)
            
            print(f"   Status: {login_response.status_code}")
            
            # Verificar si el login fue exitoso
            if login_response.status_code == 200:
                try:
                    response_json = login_response.json()
                    if response_json.get('status') == 'success':
                        print(f"   ✓ Login exitoso para {usuario['nombre']}")
                        login_exitoso = True
                        usuario_actual = usuario
                        break
                    else:
                        print(f"   ❌ Login fallido: {response_json.get('message', 'Error desconocido')}")
                except:
                    # Si no es JSON, verificar si hay redirección o contenido HTML
                    if 'dashboard' in login_response.text.lower() or login_response.url != base_url:
                        print(f"   ✓ Login exitoso para {usuario['nombre']} (redirección detectada)")
                        login_exitoso = True
                        usuario_actual = usuario
                        break
                    else:
                        print(f"   ❌ Login fallido para {usuario['nombre']}")
            else:
                print(f"   ❌ Error en login: {login_response.status_code}")
        
        if not login_exitoso:
            print("\n❌ No se pudo hacer login con ningún usuario de logística")
            print("Probando acceso directo al endpoint...")
        else:
            print(f"\n✓ Login exitoso con {usuario_actual['nombre']}")
        
        # 3. Probar el endpoint de vencimientos
        print("\n3. Probando endpoint /api/vehiculos/vencimientos...")
        
        endpoint_url = f"{base_url}/api/vehiculos/vencimientos"
        
        # GET request
        print("\n   GET request:")
        get_response = session.get(endpoint_url)
        print(f"   Status: {get_response.status_code}")
        print(f"   Content-Type: {get_response.headers.get('content-type', 'No especificado')}")
        
        if get_response.status_code == 200:
            try:
                data = get_response.json()
                print(f"   ✓ Respuesta JSON válida")
                print(f"   Número de registros: {len(data) if isinstance(data, list) else 'No es lista'}")
                
                if isinstance(data, list) and len(data) > 0:
                    print("   Ejemplo de registro:")
                    ejemplo = data[0]
                    for key, value in ejemplo.items():
                        print(f"     {key}: {value}")
                else:
                    print("   ⚠️ La respuesta está vacía o no es una lista")
                    print(f"   Contenido: {data}")
                    
            except json.JSONDecodeError:
                print("   ❌ La respuesta no es JSON válido")
                print(f"   Primeros 200 caracteres: {get_response.text[:200]}")
                
                # Verificar si es HTML (página de login)
                if '<html' in get_response.text.lower():
                    print("   ⚠️ La respuesta parece ser HTML (posible redirección a login)")
        else:
            print(f"   ❌ Error en GET: {get_response.status_code}")
            print(f"   Respuesta: {get_response.text[:200]}")
        
        # 4. Verificar datos directamente en la base de datos
        print("\n4. Verificando datos en la base de datos...")
        
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='capired',
                user='root',
                password='732137A031E4b@',
                port=3306,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            
            cursor = connection.cursor(dictionary=True)
            
            # Consulta similar a la del endpoint
            cursor.execute("""
                SELECT 
                    placa,
                    soat_vencimiento,
                    tecnomecanica_vencimiento,
                    DATEDIFF(soat_vencimiento, CURDATE()) as dias_soat,
                    DATEDIFF(tecnomecanica_vencimiento, CURDATE()) as dias_tecnomecanica,
                    CASE 
                        WHEN DATEDIFF(soat_vencimiento, CURDATE()) < 0 THEN 'Vencido'
                        WHEN DATEDIFF(soat_vencimiento, CURDATE()) <= 30 THEN 'Crítico'
                        WHEN DATEDIFF(soat_vencimiento, CURDATE()) <= 60 THEN 'Próximo'
                        ELSE 'Vigente'
                    END as estado_soat,
                    CASE 
                        WHEN DATEDIFF(tecnomecanica_vencimiento, CURDATE()) < 0 THEN 'Vencido'
                        WHEN DATEDIFF(tecnomecanica_vencimiento, CURDATE()) <= 30 THEN 'Crítico'
                        WHEN DATEDIFF(tecnomecanica_vencimiento, CURDATE()) <= 60 THEN 'Próximo'
                        ELSE 'Vigente'
                    END as estado_tecnomecanica
                FROM parque_automotor 
                WHERE estado = 'Activo'
                AND (soat_vencimiento IS NOT NULL OR tecnomecanica_vencimiento IS NOT NULL)
                ORDER BY 
                    LEAST(
                        COALESCE(soat_vencimiento, '9999-12-31'),
                        COALESCE(tecnomecanica_vencimiento, '9999-12-31')
                    ) ASC
                LIMIT 5
            """)
            
            resultados = cursor.fetchall()
            
            if resultados:
                print(f"   ✓ Encontrados {len(resultados)} registros en la base de datos")
                print("   Ejemplos:")
                for i, registro in enumerate(resultados, 1):
                    print(f"   {i}. Placa: {registro['placa']}")
                    print(f"      SOAT: {registro['soat_vencimiento']} ({registro['dias_soat']} días) - {registro['estado_soat']}")
                    print(f"      Tecnomecánica: {registro['tecnomecanica_vencimiento']} ({registro['dias_tecnomecanica']} días) - {registro['estado_tecnomecanica']}")
                    print()
            else:
                print("   ❌ No se encontraron registros en la base de datos")
            
            cursor.close()
            connection.close()
            
        except Error as e:
            print(f"   ❌ Error de base de datos: {e}")
        
        print("\n=== RESUMEN ===")
        print(f"Login exitoso: {'✓' if login_exitoso else '❌'}")
        if login_exitoso:
            print(f"Usuario: {usuario_actual['nombre']} ({usuario_actual['username']})")
        print(f"Endpoint accesible: {'✓' if get_response.status_code == 200 else '❌'}")
        print(f"Respuesta JSON: {'✓' if get_response.status_code == 200 and 'application/json' in get_response.headers.get('content-type', '') else '❌'}")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_endpoint_vencimientos()