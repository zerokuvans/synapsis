import requests
import json

def test_tipificacion_endpoint():
    """Probar el endpoint /api/asistencia/tipificacion con autenticación simulada"""
    
    print("=== Prueba del endpoint /api/asistencia/tipificacion con autenticación ===")
    
    # URL del endpoint
    url = "http://localhost:8080/api/asistencia/tipificacion"
    
    # Crear una sesión para mantener cookies
    session = requests.Session()
    
    try:
        # Primero intentar hacer login (simulado)
        login_url = "http://localhost:8080/login"
        login_data = {
            'username': 'admin',  # Usuario de prueba
            'password': 'admin'   # Contraseña de prueba
        }
        
        print("🔐 Intentando hacer login...")
        login_response = session.post(login_url, data=login_data)
        print(f"Status del login: {login_response.status_code}")
        
        # Ahora probar el endpoint de tipificación
        print("📡 Probando endpoint de tipificación...")
        response = session.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Respuesta exitosa:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                if 'tipificaciones' in data:
                    print(f"\n📊 Total de tipificaciones encontradas: {len(data['tipificaciones'])}")
                    for i, tip in enumerate(data['tipificaciones'][:5]):  # Mostrar solo las primeras 5
                        print(f"  {i+1}. {tip['codigo']} - {tip['descripcion']}")
                        
            except json.JSONDecodeError as e:
                print(f"❌ Error al decodificar JSON: {e}")
                print(f"Contenido de la respuesta: {response.text[:500]}")
        else:
            print(f"❌ Error en la respuesta: {response.status_code}")
            print(f"Contenido: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está el servidor ejecutándose en localhost:8080?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_tipificacion_endpoint()