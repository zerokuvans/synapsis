import requests
import json

# Configuración
BASE_URL = "http://localhost:8080"
LOGIN_URL = f"{BASE_URL}/"
PREOP_URL = f"{BASE_URL}/preoperacional"

# Datos del usuario específico
USER_CEDULA = "1019112308"
USER_PASSWORD = "123456"  # Contraseña confirmada
VEHICLE_PLATE = "TON81E"

def test_specific_user_validation():
    print("=== PRUEBA CON USUARIO ESPECÍFICO 1019112308 ===")
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # 1. Intentar hacer login con el usuario específico
    print(f"\n1. Intentando hacer login con usuario {USER_CEDULA}...")
    login_data = {
        'username': USER_CEDULA,
        'password': USER_PASSWORD
    }
    
    try:
        login_response = session.post(LOGIN_URL, data=login_data)
        print(f"   Status code del login: {login_response.status_code}")
        
        if login_response.status_code == 200:
            try:
                login_json = login_response.json()
                print(f"   Respuesta JSON del login: {json.dumps(login_json, indent=2, ensure_ascii=False)}")
                print("   ✅ Login exitoso")
            except:
                print("   ⚠️ Login exitoso pero respuesta no es JSON")
        else:
            print(f"   ❌ Error en login: {login_response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return
    
    # 2. Probar endpoint /preoperacional
    print(f"\n2. Probando endpoint /preoperacional con vehículo {VEHICLE_PLATE}...")
    # Datos de prueba para el preoperacional (sin id_codigo_consumidor ya que se obtiene de la sesión)
    preoperacional_data = {
        'centro_de_trabajo': 'CENTRO_PRUEBA',
        'ciudad': 'BOGOTA',
        'supervisor': 'SUPERVISOR_PRUEBA',
        'vehiculo_asistio_operacion': 'Si',
        'tipo_vehiculo': 'CAMIONETA',
        'placa_vehiculo': 'TON81E',  # Vehículo con mantenimiento abierto
        'modelo_vehiculo': '2020',
        'marca_vehiculo': 'TOYOTA',
        'licencia_conduccion': '12345678',
        'fecha_vencimiento_licencia': '2025-12-31',
        'fecha_vencimiento_soat': '2025-12-31',
        'fecha_vencimiento_tecnomecanica': '2025-12-31',
        'kilometraje_actual': '50000',
        'observaciones': 'Prueba de validación de mantenimientos abiertos'
    }
    
    try:
        preop_response = session.post(PREOP_URL, data=preoperacional_data)
        print(f"   Status code: {preop_response.status_code}")
        print(f"   Content-Type: {preop_response.headers.get('Content-Type', 'No especificado')}")
        
        if 'application/json' in preop_response.headers.get('Content-Type', ''):
            try:
                response_json = preop_response.json()
                print(f"   ✅ Respuesta JSON: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
                
                # Verificar si la validación está funcionando
                if preop_response.status_code == 400 and response_json.get('tiene_mantenimientos_abiertos'):
                    print("   🎯 ¡VALIDACIÓN EXITOSA! El sistema está bloqueando correctamente el preoperacional por mantenimientos abiertos")
                elif preop_response.status_code == 200:
                    print("   ⚠️ PROBLEMA: El preoperacional fue aceptado a pesar de tener mantenimientos abiertos")
                else:
                    print(f"   ℹ️ Respuesta inesperada: {preop_response.status_code}")
                    
            except json.JSONDecodeError:
                print(f"   ❌ Respuesta no es JSON válido: {preop_response.text[:500]}")
        else:
            print(f"   ❌ Respuesta no es JSON: {preop_response.text[:500]}")
            
    except Exception as e:
        print(f"   ❌ Error en preoperacional: {e}")

if __name__ == "__main__":
    test_specific_user_validation()