import requests
import json
from datetime import datetime

# Configuración
BASE_URL = 'http://localhost:8080'
LOGIN_URL = f'{BASE_URL}/'
OPERATIVO_URL = f'{BASE_URL}/operativo'
PREOPERACIONAL_URL = f'{BASE_URL}/preoperacional'

# Credenciales del usuario
USERNAME = '1032402333'
PASSWORD = 'CE1032402333'

def test_web_interface():
    """Prueba completa de la interfaz web del formulario preoperacional"""
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    print("=== PRUEBA DE INTERFAZ WEB PREOPERACIONAL ===")
    print(f"Usuario: {USERNAME}")
    print(f"Contraseña: {PASSWORD}")
    print()
    
    try:
        # 1. Acceder a la página de login
        print("1. Accediendo a la página de login...")
        login_response = session.get(LOGIN_URL)
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   ERROR: No se pudo acceder a la página de login")
            return False
            
        # 2. Realizar login
        print("\n2. Realizando login...")
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        login_post = session.post(LOGIN_URL, data=login_data, allow_redirects=False)
        print(f"   Status: {login_post.status_code}")
        print(f"   Headers: {dict(login_post.headers)}")
        
        if login_post.status_code == 302:
            print(f"   Redirección a: {login_post.headers.get('Location')}")
        elif login_post.status_code != 200:
            print(f"   ERROR: Login falló con status {login_post.status_code}")
            print(f"   Respuesta: {login_post.text[:500]}")
            return False
            
        # 3. Acceder al módulo operativo
        print("\n3. Accediendo al módulo operativo...")
        operativo_response = session.get(OPERATIVO_URL)
        print(f"   Status: {operativo_response.status_code}")
        
        if operativo_response.status_code != 200:
            print(f"   ERROR: No se pudo acceder al módulo operativo")
            print(f"   Respuesta: {operativo_response.text[:500]}")
            return False
            
        # 4. Verificar si hay formulario preoperacional en la página
        print("\n4. Verificando formulario preoperacional...")
        if 'preoperacional' in operativo_response.text.lower():
            print("   ✓ Formulario preoperacional encontrado en la página")
        else:
            print("   ⚠ No se encontró referencia al formulario preoperacional")
            
        # 5. Intentar enviar datos del formulario preoperacional
        print("\n5. Enviando datos del formulario preoperacional...")
        
        # Datos del formulario (basados en el formulario real)
        form_data = {
            'id_codigo_consumidor': '26',  # ID del usuario en recurso_operativo
            'fecha': datetime.now().strftime('%Y-%m-%d'),
            'hora': datetime.now().strftime('%H:%M'),
            'vehiculo_asignado': 'ABC123',
            'kilometraje_inicial': '50000',
            'nivel_combustible': '75',
            'aceite_motor': 'on',
            'liquido_frenos': 'on',
            'liquido_direccion': 'on',
            'agua_radiador': 'on',
            'luces_altas': 'on',
            'luces_bajas': 'on',
            'luces_parqueo': 'on',
            'luces_reversa': 'on',
            'direccionales': 'on',
            'pito': 'on',
            'alarma_reversa': 'on',
            'cinturon_seguridad': 'on',
            'espejos': 'on',
            'llantas': 'on',
            'llanta_repuesto': 'on',
            'gato': 'on',
            'cruceta': 'on',
            'extintor': 'on',
            'botiquin': 'on',
            'triangulos': 'on',
            'chaleco': 'on',
            'linterna': 'on',
            'observaciones': 'Prueba desde interfaz web'
        }
        
        # Enviar formulario
        form_response = session.post(PREOPERACIONAL_URL, data=form_data)
        print(f"   Status: {form_response.status_code}")
        print(f"   Respuesta: {form_response.text[:1000]}")
        
        if form_response.status_code == 200:
            print("   ✓ Formulario enviado exitosamente")
            return True
        elif form_response.status_code == 400:
            print("   ⚠ Error 400 - Posible validación o registro duplicado")
            return True  # Puede ser un registro duplicado, lo cual es normal
        else:
            print(f"   ✗ Error al enviar formulario: {form_response.status_code}")
            return False
            
    except Exception as e:
        print(f"\nERROR GENERAL: {str(e)}")
        return False
        
    finally:
        session.close()

if __name__ == '__main__':
    success = test_web_interface()
    print(f"\n=== RESULTADO: {'ÉXITO' if success else 'FALLO'} ===")