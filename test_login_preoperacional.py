import requests
import json
from datetime import datetime

# Configuración
BASE_URL = 'http://localhost:8080'
LOGIN_URL = f'{BASE_URL}/'
PREOPERACIONAL_URL = f'{BASE_URL}/preoperacional_operativo'
VERIFICAR_URL = f'{BASE_URL}/verificar_registro_preoperacional'

# Datos de login del usuario operativo
login_data = {
    'username': '1032402333',
    'password': 'CE1032402333'
}

# Datos del formulario preoperacional
form_data = {
    'id_codigo_consumidor': '19',  # ID del usuario 1032402333
    'centro_de_trabajo': 'Centro Bogotá Norte',
    'ciudad': 'Bogotá',
    'supervisor': 'SUPERVISOR PRUEBA',
    'vehiculo_asistio_operacion': 'ABC123',
    'placa_vehiculo': 'ABC123',
    'kilometraje_inicial': '50000',
    'kilometraje_final': '50100',
    'hora_inicio_labores': '08:00',
    'hora_fin_labores': '17:00',
    'estado_llantas': 'on',
    'luces_altas_bajas': 'on',
    'direccionales_delanteras_traseras': 'on',
    'pito': 'on',
    'alarma_reversa': 'on',
    'arranque_motor': 'on',
    'frenos': 'on',
    'embrague': 'on',
    'caja_cambios': 'on',
    'direccion': 'on',
    'rines': 'on',
    'espejos': 'on',
    'vidrios_panoramicos': 'on',
    'aseo_vehiculo': 'on',
    'casco': 'on',
    'botas': 'on',
    'uniforme': 'on',
    'guantes': 'on',
    'gafas': 'on',
    'protector_auditivo': 'on',
    'arnes_seguridad': 'on',
    'observaciones': 'Prueba de formulario preoperacional - Usuario 1032402333'
}

def test_login_and_preoperacional():
    print("=== PRUEBA DE LOGIN Y FORMULARIO PREOPERACIONAL ===")
    print(f"Usuario: {login_data['username']}")
    print(f"Contraseña: {login_data['password']}")
    print(f"URL Base: {BASE_URL}")
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        # 1. Realizar login
        print("\n1. Intentando login...")
        login_response = session.post(LOGIN_URL, data=login_data)
        
        print(f"Status Code Login: {login_response.status_code}")
        print(f"URL después del login: {login_response.url}")
        
        if login_response.status_code == 200:
            if 'dashboard' in login_response.url or 'operativo' in login_response.url:
                print("✓ Login exitoso")
            else:
                print("⚠ Login posiblemente fallido - revisar redirección")
                print(f"Contenido de respuesta: {login_response.text[:500]}...")
        else:
            print(f"✗ Login fallido - Status: {login_response.status_code}")
            print(f"Respuesta: {login_response.text[:500]}...")
            return
        
        # 2. Verificar acceso al módulo operativo
        print("\n2. Verificando acceso al módulo operativo...")
        operativo_response = session.get(f'{BASE_URL}/operativo')
        
        print(f"Status Code Operativo: {operativo_response.status_code}")
        
        if operativo_response.status_code == 200:
            print("✓ Acceso al módulo operativo exitoso")
        else:
            print(f"✗ No se puede acceder al módulo operativo - Status: {operativo_response.status_code}")
            print(f"Respuesta: {operativo_response.text[:500]}...")
            return
        
        # 3. Verificar registros existentes
        print("\n3. Verificando registros preoperacionales existentes...")
        verificar_data = {
            'id_codigo_consumidor': form_data['id_codigo_consumidor'],
            'fecha': datetime.now().strftime('%Y-%m-%d')
        }
        
        verificar_response = session.get(VERIFICAR_URL, params=verificar_data)
        print(f"Status Code Verificación: {verificar_response.status_code}")
        
        try:
            verificar_json = verificar_response.json()
            print(f"Respuesta verificación: {verificar_json}")
        except:
            print(f"Respuesta verificación (no JSON): {verificar_response.text[:200]}...")
        
        # 4. Enviar formulario preoperacional
        print("\n4. Enviando formulario preoperacional...")
        
        # Agregar fecha actual
        form_data['fecha'] = datetime.now().strftime('%Y-%m-%d')
        
        preop_response = session.post(PREOPERACIONAL_URL, data=form_data)
        
        print(f"Status Code Preoperacional: {preop_response.status_code}")
        print(f"URL después del envío: {preop_response.url}")
        
        if preop_response.status_code == 200:
            print("✓ Formulario enviado exitosamente")
            
            # Verificar si hay mensaje de éxito en la respuesta
            if 'éxito' in preop_response.text.lower() or 'exitoso' in preop_response.text.lower():
                print("✓ Confirmación de guardado encontrada")
            else:
                print("⚠ No se encontró confirmación explícita de guardado")
                
        else:
            print(f"✗ Error al enviar formulario - Status: {preop_response.status_code}")
            print(f"Respuesta: {preop_response.text[:500]}...")
        
        # 5. Verificar si el registro se guardó
        print("\n5. Verificando si el registro se guardó...")
        final_verificar_response = session.get(VERIFICAR_URL, params=verificar_data)
        
        try:
            verificar_json2 = final_verificar_response.json()
            print(f"Verificación final: {verificar_json2}")
            
            if verificar_json2.get('tiene_registro'):
                print("✓ ¡ÉXITO! El registro preoperacional se guardó correctamente")
            else:
                print("✗ El registro no se encontró en la base de datos")
                
        except json.JSONDecodeError:
            print(f"Error en verificación final: {final_verificar_response.text[:500]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    test_login_and_preoperacional()