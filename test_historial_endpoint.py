import requests
import json

def test_historial_endpoint():
    """Prueba el endpoint del historial de cambios de dotación"""
    
    url = "http://localhost:8080/api/cambios_dotacion/historial"
    
    print("Probando el endpoint del historial de cambios de dotación...")
    print(f"URL: {url}")
    
    try:
        # Hacer la petición GET
        response = requests.get(url, timeout=10)
        
        print(f"\nCódigo de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ ¡Éxito! El endpoint responde correctamente.")
            print(f"Contenido de la respuesta: {response.text[:500]}...")
            
            # Parsear la respuesta JSON
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                print(f"✗ Error al parsear JSON: {e}")
                print(f"Respuesta completa: {response.text}")
                return
            
            if data.get('success'):
                print(f"✓ Respuesta exitosa con {len(data.get('data', []))} registros")
                
                # Mostrar algunos datos de ejemplo
                if data.get('data'):
                    print("\nPrimer registro:")
                    primer_registro = data['data'][0]
                    print(f"  ID: {primer_registro.get('id')}")
                    print(f"  Técnico: {primer_registro.get('tecnico')}")
                    print(f"  Elementos: {primer_registro.get('elementos_modificados')}")
                    print(f"  Fecha cambio: {primer_registro.get('fecha_cambio')}")
                else:
                    print("  No hay registros en el historial")
            else:
                print(f"✗ Error en la respuesta: {data.get('error', 'Error desconocido')}")
                
        elif response.status_code == 401:
            print("✗ Error de autenticación (401). Necesitas estar logueado.")
        elif response.status_code == 403:
            print("✗ Error de permisos (403). Necesitas rol de logística.")
        elif response.status_code == 500:
            print("✗ Error interno del servidor (500).")
            try:
                error_data = response.json()
                print(f"  Detalle del error: {error_data.get('error', 'Error desconocido')}")
            except:
                print(f"  Respuesta del servidor: {response.text[:200]}...")
        else:
            print(f"✗ Error inesperado: {response.status_code}")
            print(f"  Respuesta: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("✗ Error de conexión. ¿Está el servidor ejecutándose en localhost:8080?")
    except requests.exceptions.Timeout:
        print("✗ Timeout. El servidor tardó demasiado en responder.")
    except Exception as e:
        print(f"✗ Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_historial_endpoint()