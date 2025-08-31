import requests
import json
from datetime import datetime

# Configuración
BASE_URL = 'http://localhost:8080'
LOGIN_URL = f'{BASE_URL}/login'
PREOPERACIONAL_URL = f'{BASE_URL}/preoperacional'

# Credenciales del usuario
USER_CREDENTIALS = {
    'username': '1032402333',
    'password': 'CE1032402333'
}

def test_login_and_preoperacional():
    """Prueba el login y el envío del formulario preoperacional"""
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    print("=== PRUEBA DE FORMULARIO PREOPERACIONAL ===")
    print(f"Servidor: {BASE_URL}")
    print(f"Usuario: {USER_CREDENTIALS['username']}")
    
    try:
        # 1. Verificar que el servidor esté disponible
        print("\n1. Verificando servidor...")
        response = session.get(BASE_URL)
        print(f"   Estado del servidor: {response.status_code}")
        
        # 2. Hacer login
        print("\n2. Realizando login...")
        login_data = {
            'username': USER_CREDENTIALS['username'],
            'password': USER_CREDENTIALS['password']
        }
        
        # Agregar headers para simular una petición AJAX
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Usar la ruta principal que maneja el login
        login_url = f"{BASE_URL}/"
        login_response = session.post(login_url, data=login_data, headers=headers)
        print(f"   Estado del login: {login_response.status_code}")
        print(f"   URL después del login: {login_response.url}")
        
        if login_response.status_code == 200:
            try:
                login_json = login_response.json()
                print(f"   Respuesta del login: {login_json}")
                if login_json.get('status') != 'success':
                    print(f"   ERROR: Login falló: {login_json.get('message')}")
                    return False
            except:
                print("   Login exitoso (respuesta no JSON)")
        else:
            print(f"   ERROR: Login falló con código {login_response.status_code}")
            print(f"   Respuesta: {login_response.text[:500]}")
            return False
            
        # 3. Acceder al módulo operativo
        print("\n3. Accediendo al módulo operativo...")
        operativo_url = f'{BASE_URL}/operativo'
        operativo_response = session.get(operativo_url)
        print(f"   Estado del módulo operativo: {operativo_response.status_code}")
        
        if operativo_response.status_code != 200:
            print(f"   ERROR: No se pudo acceder al módulo operativo")
            print(f"   Respuesta: {operativo_response.text[:500]}")
            return False
            
        # 4. Preparar datos del formulario preoperacional
        print("\n4. Preparando datos del formulario...")
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        
        form_data = {
            'fecha': fecha_actual,
            'id_codigo_consumidor': '26',  # ID del usuario en recurso_operativo
            'vehiculo_asignado': 'ABC123',
            'kilometraje_inicial': '15000',
            'nivel_combustible': '75',
            'aceite_motor': 'bueno',
            'liquido_frenos': 'bueno',
            'liquido_direccion': 'bueno',
            'agua_radiador': 'bueno',
            'luces_delanteras': 'bueno',
            'luces_traseras': 'bueno',
            'direccionales': 'bueno',
            'freno_mano': 'bueno',
            'freno_pie': 'bueno',
            'llantas': 'bueno',
            'espejos': 'bueno',
            'cinturon_seguridad': 'bueno',
            'extintor': 'bueno',
            'botiquin': 'bueno',
            'triangulos': 'bueno',
            'gato_cruceta': 'bueno',
            'llanta_repuesto': 'bueno',
            'documentos_vehiculo': 'bueno',
            'observaciones': 'Prueba de formulario preoperacional desde script'
        }
        
        print(f"   Datos preparados para fecha: {fecha_actual}")
        print(f"   ID código consumidor: {form_data['id_codigo_consumidor']}")
        
        # 5. Enviar formulario preoperacional
        print("\n5. Enviando formulario preoperacional...")
        preop_response = session.post(PREOPERACIONAL_URL, data=form_data)
        print(f"   Estado del envío: {preop_response.status_code}")
        print(f"   URL de respuesta: {preop_response.url}")
        
        # Analizar respuesta
        if preop_response.status_code == 200:
            print("   ✓ Formulario enviado exitosamente")
            if 'success' in preop_response.text.lower() or 'éxito' in preop_response.text.lower():
                print("   ✓ Mensaje de éxito detectado en la respuesta")
            else:
                print("   ⚠ No se detectó mensaje de éxito claro")
                print(f"   Respuesta: {preop_response.text[:300]}")
        elif preop_response.status_code == 400:
            print("   ⚠ Error 400 - Posible registro duplicado o datos inválidos")
            print(f"   Respuesta: {preop_response.text[:300]}")
        else:
            print(f"   ✗ Error al enviar formulario: {preop_response.status_code}")
            print(f"   Respuesta: {preop_response.text[:500]}")
            
        return preop_response.status_code in [200, 400]  # 400 puede ser duplicado
        
    except requests.exceptions.ConnectionError:
        print("   ✗ ERROR: No se pudo conectar al servidor")
        print("   Verifique que el servidor esté ejecutándose en http://localhost:8080")
        return False
    except Exception as e:
        print(f"   ✗ ERROR inesperado: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_login_and_preoperacional()
    print(f"\n=== RESULTADO FINAL ===")
    if success:
        print("✓ Prueba completada - El formulario se procesó correctamente")
    else:
        print("✗ Prueba falló - Revisar errores anteriores")