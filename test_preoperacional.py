import requests
import json
from datetime import datetime, timedelta

# Crear una sesión para mantener las cookies
session = requests.Session()

# URL base
base_url = 'http://127.0.0.1:8080'

# Datos del usuario administrador/técnico
username = '80833959'
password = 'M4r14l4r@'

try:
    # Login como administrador/técnico
    print('1. Login como administrador/técnico...')
    login_data = {
        'username': username,
        'password': password
    }

    login_response = session.post(f'{base_url}/', data=login_data)
    print('Estado:', login_response.status_code)
    try:
        print('Respuesta:', json.dumps(login_response.json(), indent=2))
    except:
        print('Respuesta:', login_response.text)
    
    if login_response.status_code != 200:
        print('Error en el login')
        exit(1)

    # Datos de prueba para el preoperacional
    print('\n2. Registrando preoperacional...')
    data = {
        'id_codigo_consumidor': login_response.json().get('user_id'),  # Usar el ID del usuario logueado
        'centro_de_trabajo': 'Centro Prueba',
        'ciudad': 'Ciudad Prueba',
        'supervisor': 'Supervisor Prueba',
        'vehiculo_asistio_operacion': 'Si',
        'tipo_vehiculo': 'Moto',
        'placa_vehiculo': 'ABC123',
        'modelo_vehiculo': '2023',
        'marca_vehiculo': 'Honda',
        'licencia_conduccion': '12345',
        'fecha_vencimiento_licencia': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'fecha_vencimiento_soat': (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
        'fecha_vencimiento_tecnomecanica': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'),
        'estado_espejos': '1',
        'bocina_pito': '1',
        'frenos': '1',
        'encendido': '1',
        'estado_bateria': '1',
        'estado_amortiguadores': '1',
        'estado_llantas': '1',
        'kilometraje_actual': '1000',
        'luces_altas_bajas': '1',
        'direccionales_delanteras_traseras': '1',
        'elementos_prevencion_seguridad_vial_casco': '1',
        'casco_certificado': '1',
        'casco_identificado': '1',
        'estado_guantes': '1',
        'estado_rodilleras': '1',
        'impermeable': '1',
        'observaciones': 'Prueba de registro preoperacional'
    }

    # Realizar la solicitud POST para registrar el preoperacional
    response = session.post(f'{base_url}/preoperacional', data=data)
    print('Estado:', response.status_code)
    try:
        print('Respuesta:', json.dumps(response.json(), indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print('Respuesta:', response.text)

except requests.exceptions.ConnectionError as e:
    print('Error de conexión:', str(e))
except Exception as e:
    print('Error:', str(e)) 