import requests
import json
from collections import Counter

# Configuración
base_url = "http://127.0.0.1:8080"
login_url = f"{base_url}/login"
endpoint_url = f"{base_url}/api/operativo/inicio-operacion/asistencia"

# Crear sesión para mantener cookies
session = requests.Session()

# Datos de login (ajusta según tu sistema)
login_data = {
    'username': '80833959',  # Usuario válido encontrado
    'password': 'M4r14l4r@'  # Contraseña correcta encontrada
}

try:
    # Intentar login
    print("🔐 Intentando login...")
    login_response = session.post(login_url, data=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        # Intentar acceder al endpoint con fecha de hoy
        print("📊 Accediendo al endpoint...")
        from datetime import datetime
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        params = {'fecha': fecha_hoy}
        response = session.get(endpoint_url, params=params)
        print(f"Endpoint status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'No especificado')}")
        print(f"Parámetros enviados: {params}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            data = response.json()
            print(f"✅ Respuesta JSON recibida")
            print(f"Status: {data.get('status')}")
            
            if 'registros' in data:
                registros = data['registros']
                print(f"📋 Total registros: {len(registros)}")
                
                # Verificar duplicados por cédula
                cedulas = [reg.get('cedula') for reg in registros if reg.get('cedula')]
                cedulas_unicas = set(cedulas)
                print(f"🔍 Cédulas únicas: {len(cedulas_unicas)}")
                
                if len(cedulas) != len(cedulas_unicas):
                    print("🔴 ¡DUPLICADOS ENCONTRADOS!")
                    # Mostrar duplicados
                    contador = Counter(cedulas)
                    duplicados = {k: v for k, v in contador.items() if v > 1}
                    for cedula, count in duplicados.items():
                        print(f"   Cédula {cedula}: {count} veces")
                        
                        # Mostrar detalles de los registros duplicados
                        registros_duplicados = [reg for reg in registros if reg.get('cedula') == cedula]
                        for i, reg in enumerate(registros_duplicados, 1):
                            print(f"     Registro {i}: {reg}")
                else:
                    print("✅ No hay duplicados")
                    
                # Mostrar muestra de los primeros registros
                print("\n📋 Muestra de registros (primeros 3):")
                for i, reg in enumerate(registros[:3], 1):
                    print(f"   {i}. {reg}")
                    
            else:
                print("⚠️ No se encontró 'registros' en la respuesta")
                print(f"Claves disponibles: {list(data.keys())}")
        else:
            print("❌ La respuesta no es JSON")
            print("Primeros 500 caracteres de la respuesta:")
            print(response.text[:500])
    else:
        print("❌ Error en login")
        print(f"Respuesta: {login_response.text[:200]}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()