import requests
import json

# Configuración del servidor
BASE_URL = "http://localhost:8080"

def test_vencimientos_endpoint():
    """Probar el endpoint de vencimientos"""
    
    print("=== PRUEBA DEL ENDPOINT /api/vehiculos/vencimientos ===")
    
    # Crear una sesión para mantener las cookies
    session = requests.Session()
    
    try:
        # Primero intentar acceder directamente al endpoint
        print("\n1. Probando acceso directo al endpoint...")
        response = session.get(f"{BASE_URL}/api/vehiculos/vencimientos")
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✓ Respuesta JSON exitosa")
                print(f"Tipo de datos: {type(data)}")
                
                if isinstance(data, list):
                    print(f"Total de registros: {len(data)}")
                    if data:
                        print("\nPrimeros 3 registros:")
                        for i, item in enumerate(data[:3]):
                            print(f"  {i+1}. {json.dumps(item, indent=2, ensure_ascii=False)}")
                elif isinstance(data, dict):
                    print(f"Respuesta tipo diccionario:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                else:
                    print(f"Respuesta: {data}")
                    
            except json.JSONDecodeError:
                print("❌ La respuesta no es JSON válido")
                print(f"Contenido: {response.text[:500]}...")
        
        elif response.status_code == 302 or 'login' in response.text.lower():
            print("❌ El endpoint requiere autenticación")
            print("Redirigiendo al login...")
            
        else:
            print(f"❌ Error en la respuesta: {response.status_code}")
            print(f"Contenido: {response.text[:500]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está el servidor ejecutándose en localhost:8080?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_vencimientos_endpoint()