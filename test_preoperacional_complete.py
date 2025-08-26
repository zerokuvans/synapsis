import requests
import json
from datetime import datetime

def test_preoperacional_form():
    base_url = 'http://localhost:8080'
    session = requests.Session()
    
    # Datos del usuario operativo
    cedula = '1032402333'  # CACERES MARTINEZ CARLOS
    password = 'password123'  # Password por defecto
    
    print(f"=== INICIANDO PRUEBA DEL FORMULARIO PREOPERACIONAL ===")
    print(f"Usuario: {cedula}")
    print(f"Fecha/Hora: {datetime.now()}")
    
    try:
        # 1. Intentar login
        print("\n1. Intentando login...")
        login_data = {
            'username': cedula,
            'password': password
        }
        
        login_response = session.post(f'{base_url}/', data=login_data)
        print(f"Status login: {login_response.status_code}")
        
        if login_response.status_code == 200:
            if 'operativo' in login_response.text:
                print("✓ Login exitoso - Usuario operativo")
            else:
                print("⚠ Login realizado pero respuesta inesperada")
                print(f"Contenido: {login_response.text[:200]}...")
        else:
            print(f"✗ Error en login: {login_response.status_code}")
            return
        
        # 2. Verificar registro existente
        print("\n2. Verificando registro preoperacional existente...")
        verify_response = session.get(f'{base_url}/verificar_registro_preoperacional')
        print(f"Status verificación: {verify_response.status_code}")
        
        if verify_response.status_code == 200:
            try:
                verify_data = verify_response.json()
                print(f"Respuesta verificación: {verify_data}")
            except json.JSONDecodeError:
                print("⚠ Respuesta de verificación no es JSON válido")
                print(f"Contenido: {verify_response.text[:200]}...")
        
        # 3. Enviar formulario preoperacional
        print("\n3. Enviando formulario preoperacional...")
        
        form_data = {
            'vehiculo_asignado': 'VEH001',
            'kilometraje_inicial': '12500',
            'nivel_combustible': '75',
            'estado_vehiculo': 'Bueno',
            'observaciones_vehiculo': 'Vehículo en buen estado general',
            'equipo_comunicacion': 'Radio portátil',
            'estado_comunicacion': 'Funcional',
            'observaciones_comunicacion': 'Sin novedad',
            'herramientas_trabajo': 'Kit básico de herramientas',
            'estado_herramientas': 'Completo',
            'observaciones_herramientas': 'Todas las herramientas presentes',
            'epp_asignado': 'Casco, chaleco, guantes',
            'estado_epp': 'Bueno',
            'observaciones_epp': 'EPP en buen estado',
            'condiciones_climaticas': 'Despejado',
            'observaciones_clima': 'Condiciones favorables para el trabajo',
            'observaciones_generales': 'Todo en orden para iniciar labores'
        }
        
        preop_response = session.post(f'{base_url}/preoperacional_operativo', data=form_data)
        print(f"Status envío formulario: {preop_response.status_code}")
        
        if preop_response.status_code == 200:
            try:
                response_data = preop_response.json()
                print(f"✓ Respuesta del servidor: {response_data}")
                
                if response_data.get('success'):
                    print("✓ Formulario guardado exitosamente")
                else:
                    print(f"✗ Error al guardar: {response_data.get('message', 'Error desconocido')}")
                    
            except json.JSONDecodeError:
                print("⚠ Respuesta no es JSON válido")
                print(f"Contenido: {preop_response.text[:500]}...")
        else:
            print(f"✗ Error al enviar formulario: {preop_response.status_code}")
            print(f"Contenido: {preop_response.text[:500]}...")
        
        print("\n=== PRUEBA COMPLETADA ===")
        print("Revisa los logs del servidor para ver los mensajes de debug")
        
    except Exception as e:
        print(f"Error durante la prueba: {e}")

if __name__ == '__main__':
    test_preoperacional_form()