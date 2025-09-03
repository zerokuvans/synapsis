import requests
import json
from datetime import datetime

def test_endpoint_vencimientos():
    """Probar el endpoint de vencimientos después de limpiar los datos"""
    print("=== PRUEBA FINAL DEL ENDPOINT DE VENCIMIENTOS ===")
    
    base_url = "http://localhost:8080"
    endpoint = f"{base_url}/api/vehiculos/vencimientos"
    
    try:
        print("\n1. PROBANDO ACCESO DIRECTO AL ENDPOINT:")
        
        # Probar acceso directo
        response = requests.get(endpoint, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'No especificado')}")
        
        if response.status_code == 200:
            try:
                # Intentar parsear como JSON
                data = response.json()
                print(f"   ✓ Respuesta JSON válida")
                print(f"   ✓ Número de registros: {len(data) if isinstance(data, list) else 'No es lista'}")
                
                if isinstance(data, list) and len(data) > 0:
                    print("\n   Primeros 3 registros:")
                    for i, registro in enumerate(data[:3]):
                        print(f"     {i+1}. {json.dumps(registro, indent=6, ensure_ascii=False)}")
                        
                    # Contar por estado
                    estados = {}
                    for registro in data:
                        if 'soat_estado' in registro:
                            estado = registro['soat_estado']
                            estados[f'SOAT_{estado}'] = estados.get(f'SOAT_{estado}', 0) + 1
                        if 'tecnomecanica_estado' in registro:
                            estado = registro['tecnomecanica_estado']
                            estados[f'TECNO_{estado}'] = estados.get(f'TECNO_{estado}', 0) + 1
                    
                    print("\n   Resumen por estados:")
                    for estado, count in estados.items():
                        print(f"     - {estado}: {count}")
                        
                elif isinstance(data, list) and len(data) == 0:
                    print("   ⚠️  Lista vacía - No hay datos de vencimientos")
                else:
                    print(f"   ⚠️  Respuesta inesperada: {type(data)}")
                    print(f"   Contenido: {str(data)[:200]}...")
                    
            except json.JSONDecodeError:
                print("   ❌ La respuesta no es JSON válido")
                content = response.text[:500]
                print(f"   Contenido (primeros 500 chars): {content}")
                
                # Verificar si es HTML de login
                if "login" in content.lower() or "password" in content.lower():
                    print("   ⚠️  Parece ser una página de login - se requiere autenticación")
                    
        elif response.status_code == 401:
            print("   ⚠️  Error 401: No autorizado - se requiere autenticación")
        elif response.status_code == 403:
            print("   ⚠️  Error 403: Prohibido - se requiere rol específico")
        else:
            print(f"   ❌ Error {response.status_code}: {response.text[:200]}")
            
        print("\n2. PROBANDO CON SESIÓN SIMULADA:")
        
        # Crear una sesión para mantener cookies
        session = requests.Session()
        
        # Intentar acceder a la página principal primero
        main_response = session.get(base_url, timeout=10)
        print(f"   Página principal: {main_response.status_code}")
        
        # Intentar el endpoint con la sesión
        session_response = session.get(endpoint, timeout=10)
        print(f"   Endpoint con sesión: {session_response.status_code}")
        
        if session_response.status_code == 200:
            try:
                session_data = session_response.json()
                print(f"   ✓ Datos obtenidos con sesión: {len(session_data) if isinstance(session_data, list) else 'No es lista'}")
            except:
                print("   ❌ Respuesta no es JSON válido con sesión")
                
        print("\n3. VERIFICANDO CONFIGURACIÓN DEL SERVIDOR:")
        
        # Verificar si el servidor está corriendo
        try:
            health_response = requests.get(f"{base_url}/", timeout=5)
            print(f"   Servidor activo: {health_response.status_code == 200}")
        except:
            print("   ❌ Servidor no responde")
            
        print("\n✅ PRUEBA COMPLETADA")
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Error de conexión - Verificar que el servidor esté ejecutándose")
    except requests.exceptions.Timeout:
        print("   ❌ Timeout - El servidor no responde a tiempo")
    except Exception as e:
        print(f"   ❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_endpoint_vencimientos()