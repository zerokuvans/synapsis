import requests
import json

def test_endpoint():
    """Prueba el endpoint /api/cambios_dotacion/historial para verificar que funciona"""
    
    # URL del endpoint
    url = "http://localhost:8080/api/cambios_dotacion/historial"
    
    print("Probando el endpoint /api/cambios_dotacion/historial...")
    print(f"URL: {url}")
    
    try:
        # Hacer la petición GET
        response = requests.get(url, timeout=10)
        
        print(f"\nCódigo de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ ¡Éxito! El endpoint responde correctamente.")
            
            # Parsear la respuesta JSON
            try:
                data = response.json()
                print(f"\nRespuesta JSON:")
                print(f"  success: {data.get('success')}")
                
                if 'data' in data:
                    historial = data['data']
                    print(f"  registros encontrados: {len(historial)}")
                    
                    if historial:
                        print(f"\n  Primer registro:")
                        primer_registro = historial[0]
                        for key, value in primer_registro.items():
                            print(f"    {key}: {value}")
                else:
                    print("  No hay datos en la respuesta")
                    
            except json.JSONDecodeError as e:
                print(f"✗ Error al parsear JSON: {e}")
                print(f"Contenido de la respuesta: {response.text[:500]}")
                
        elif response.status_code == 500:
            print("✗ Error HTTP 500 - Error interno del servidor")
            try:
                error_data = response.json()
                print(f"Mensaje de error: {error_data.get('error', 'Sin mensaje específico')}")
            except:
                print(f"Contenido de la respuesta: {response.text[:500]}")
                
        elif response.status_code == 401:
            print("✗ Error HTTP 401 - No autorizado (se requiere autenticación)")
            print("Nota: Este error es esperado ya que no estamos autenticados")
            
        elif response.status_code == 403:
            print("✗ Error HTTP 403 - Prohibido (se requiere rol de logística)")
            print("Nota: Este error es esperado ya que no tenemos el rol correcto")
            
        else:
            print(f"✗ Error HTTP {response.status_code}")
            print(f"Contenido: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Error de conexión: No se puede conectar al servidor")
        print("Verifica que el servidor esté ejecutándose en http://localhost:8080")
        
    except requests.exceptions.Timeout:
        print("✗ Error de timeout: El servidor no respondió a tiempo")
        
    except Exception as e:
        print(f"✗ Error inesperado: {e}")

if __name__ == "__main__":
    test_endpoint()