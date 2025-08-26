import requests
import json

# Configuración
BASE_URL = 'http://localhost:8080'
LOGIN_URL = f'{BASE_URL}/'
PREOPERACIONAL_URL = f'{BASE_URL}/preoperacional_operativo'
VERIFICAR_URL = f'{BASE_URL}/verificar_registro_preoperacional'

# Datos de login - Usuario operativo real
login_data = {
    'username': '52912112',
    'password': 'CE52912112'
}

# Datos del formulario preoperacional
form_data = {
    'centro_de_trabajo': 'Centro Test',
    'ciudad': 'Bogotá',
    'supervisor': 'Supervisor Test',
    'vehiculo_asistio_operacion': '1',
    'tipo_vehiculo': 'Motocicleta',
    'placa_vehiculo': 'ABC123',
    'modelo_vehiculo': '2020',
    'marca_vehiculo': 'Honda',
    'licencia_conduccion': 'A1',
    'fecha_vencimiento_licencia': '2025-12-31',
    'fecha_vencimiento_soat': '2025-12-31',
    'fecha_vencimiento_tecnomecanica': '2025-12-31',
    'estado_espejos': '1',
    'bocina_pito': '1',
    'frenos': '1',
    'encendido': '1',
    'estado_bateria': '1',
    'estado_amortiguadores': '1',
    'estado_llantas': '1',
    'kilometraje_actual': '15000',
    'luces_altas_bajas': '1',
    'direccionales_delanteras_traseras': '1',
    'elementos_prevencion_seguridad_vial_casco': '1',
    'casco_certificado': '1',
    'casco_identificado': '1',
    'estado_guantes': '1',
    'estado_rodilleras': '1',
    'impermeable': '1',
    'observaciones': 'Prueba de formulario preoperacional',
    'id_codigo_consumidor': '26'  # ID del usuario operativo (CORTES CUERVO SANDRA CECILIA)
}

def test_preoperacional_form():
    print("\n=== INICIANDO PRUEBA DEL FORMULARIO PREOPERACIONAL ===")
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # Paso 1: Login del usuario operativo
    print("\n1. Realizando login del usuario operativo...")
    try:
        login_response = session.post(LOGIN_URL, data=login_data)
        print(f"Status login: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("Login exitoso")
            # Verificar si hay redirección o mensaje de éxito
            if 'dashboard' in login_response.url or 'operativo' in login_response.url:
                print(f"Redirigido a: {login_response.url}")
            else:
                print(f"Respuesta login: {login_response.text[:200]}...")
        else:
            print(f"Error en login: {login_response.text}")
            return
    except Exception as e:
        print(f"Error al hacer login: {e}")
        return
    
    # Paso 2: Verificar si ya existe un registro preoperacional para hoy
    print("\n2. Verificando registros existentes...")
    try:
        verificar_response = session.get(VERIFICAR_URL)
        print(f"Status verificación: {verificar_response.status_code}")
        
        if verificar_response.status_code == 200:
            try:
                verificar_data = verificar_response.json()
                print(f"Respuesta verificación: {verificar_data}")
            except:
                print(f"Respuesta verificación (texto): {verificar_response.text[:200]}...")
        else:
            print(f"Error en verificación: {verificar_response.text}")
    except Exception as e:
        print(f"Error al verificar registros: {e}")
    
    # Paso 3: Enviar formulario preoperacional
    print("\n3. Enviando formulario preoperacional...")
    try:
        response = session.post(PREOPERACIONAL_URL, data=form_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Respuesta JSON: {json.dumps(data, indent=2)}")
                if data.get('success'):
                    print("✓ Formulario enviado exitosamente")
                else:
                    print(f"⚠ Advertencia: {data.get('message', 'Respuesta inesperada')}")
            except:
                print(f"Respuesta texto: {response.text[:500]}...")
                if 'success' in response.text.lower() or 'exitoso' in response.text.lower():
                    print("✓ Posible envío exitoso (respuesta en texto)")
        else:
            print(f"✗ Error HTTP {response.status_code}: {response.text[:300]}...")
    except Exception as e:
        print(f"✗ Error al enviar formulario: {e}")
    
    print("\n=== FIN DE LA PRUEBA ===")

if __name__ == '__main__':
    test_preoperacional_form()