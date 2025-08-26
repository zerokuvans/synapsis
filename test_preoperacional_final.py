import requests
import json
from datetime import datetime

def test_preoperacional_form():
    base_url = "http://localhost:8080"
    session = requests.Session()
    
    print("=== PRUEBA FINAL DEL FORMULARIO PREOPERACIONAL ===")
    print(f"Fecha y hora: {datetime.now()}")
    print()
    
    # 1. Login
    print("1. Iniciando sesión...")
    login_data = {
        'username': '1032402333',
        'password': 'CE1032402333'
    }
    
    login_response = session.post(f"{base_url}/login", data=login_data)
    
    if login_response.status_code == 200:
        print("✓ Login exitoso")
    else:
        print(f"✗ Error en login: {login_response.status_code}")
        return False
    
    # 2. Acceder al módulo operativo
    print("\n2. Accediendo al módulo operativo...")
    operativo_response = session.get(f"{base_url}/operativo")
    
    if operativo_response.status_code == 200:
        print("✓ Acceso al módulo operativo exitoso")
        if "preoperacional" in operativo_response.text.lower():
            print("✓ Formulario preoperacional encontrado en la página")
        else:
            print("⚠ No se encontró referencia al formulario preoperacional")
    else:
        print(f"✗ Error accediendo al módulo operativo: {operativo_response.status_code}")
        return False
    
    # 3. Enviar formulario preoperacional
    print("\n3. Enviando formulario preoperacional...")
    
    form_data = {
        'centro_de_trabajo': 'Centro Bogotá',
        'ciudad': 'Bogotá',
        'supervisor': 'Supervisor Test',
        'vehiculo_asistio_operacion': 'Sí',
        'tipo_vehiculo': 'Motocicleta',
        'placa_vehiculo': 'ABC123',
        'modelo_vehiculo': '2020',
        'marca_vehiculo': 'Honda',
        'licencia_conduccion': 'Sí',
        'fecha_vencimiento_licencia': '2025-12-31',
        'fecha_vencimiento_soat': '2025-12-31',
        'fecha_vencimiento_tecnomecanica': '2025-12-31',
        'estado_espejos': 'Bueno',
        'bocina_pito': 'Bueno',
        'frenos': 'Bueno',
        'encendido': 'Bueno',
        'estado_bateria': 'Bueno',
        'estado_amortiguadores': 'Bueno',
        'estado_llantas': 'Bueno',
        'kilometraje_actual': '15000',
        'luces_altas_bajas': 'Bueno',
        'direccionales_delanteras_traseras': 'Bueno',
        'elementos_prevencion_seguridad_vial_casco': 'Sí',
        'casco_certificado': 'Sí',
        'casco_identificado': 'Sí',
        'observaciones': 'Prueba final del formulario desde interfaz web'
    }
    
    submit_response = session.post(f"{base_url}/submit_preoperacional", data=form_data)
    
    print(f"Status code: {submit_response.status_code}")
    print(f"Response text: {submit_response.text[:500]}...")
    
    if submit_response.status_code == 200:
        if "éxito" in submit_response.text.lower() or "exitoso" in submit_response.text.lower():
            print("✓ Formulario enviado exitosamente")
            return True
        else:
            print("⚠ Respuesta recibida pero sin confirmación de éxito")
            return False
    else:
        print(f"✗ Error enviando formulario: {submit_response.status_code}")
        return False

if __name__ == "__main__":
    success = test_preoperacional_form()
    print(f"\n=== RESULTADO FINAL ===")
    if success:
        print("✓ EL FORMULARIO PREOPERACIONAL FUNCIONA CORRECTAMENTE DESDE LA INTERFAZ WEB")
    else:
        print("✗ EL FORMULARIO PREOPERACIONAL AÚN TIENE PROBLEMAS")