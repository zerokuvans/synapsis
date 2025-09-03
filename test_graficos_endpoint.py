#!/usr/bin/env python3
"""
Script para probar el endpoint /api/vehiculos/graficos
"""

import requests
import json
from requests.sessions import Session

def test_graficos_endpoint():
    print("=== PRUEBA DEL ENDPOINT /api/vehiculos/graficos ===")
    
    # Crear una sesión para mantener las cookies
    session = Session()
    
    # URL base del servidor
    base_url = "http://localhost:8080"
    
    try:
        # Primero intentar hacer login (necesitaremos credenciales válidas)
        login_url = f"{base_url}/"
        
        # Datos de login de prueba (ajustar según sea necesario)
        login_data = {
            'username': 'admin',  # Cambiar por usuario válido
            'password': 'admin'   # Cambiar por contraseña válida
        }
        
        print("1. Intentando hacer login...")
        login_response = session.post(login_url, data=login_data)
        print(f"   Status code del login: {login_response.status_code}")
        
        # Ahora probar el endpoint de gráficos
        graficos_url = f"{base_url}/api/vehiculos/graficos"
        print("\n2. Probando endpoint de gráficos...")
        
        response = session.get(graficos_url)
        print(f"   Status code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("\n✅ RESPUESTA EXITOSA:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Analizar la estructura de los datos
                print("\n📊 ANÁLISIS DE DATOS:")
                if 'tipo_vehiculo' in data:
                    print(f"   - Datos de tipo de vehículo: {len(data['tipo_vehiculo'])} elementos")
                    for item in data['tipo_vehiculo']:
                        print(f"     * {item}")
                        
                if 'estado_documentos' in data:
                    print(f"   - Datos de estado de documentos: {len(data['estado_documentos'])} elementos")
                    for item in data['estado_documentos']:
                        print(f"     * {item}")
                        
            except json.JSONDecodeError:
                print("❌ Error: La respuesta no es JSON válido")
                print(f"Contenido: {response.text[:500]}...")
                
        elif response.status_code == 401:
            print("❌ Error 401: Autenticación requerida")
            print("💡 El endpoint requiere autenticación válida")
            
        elif response.status_code == 403:
            print("❌ Error 403: Sin permisos")
            print("💡 El usuario no tiene permisos para acceder a este endpoint")
            
        else:
            print(f"❌ Código de respuesta inesperado: {response.status_code}")
            print(f"Respuesta: {response.text[:500]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: No se pudo conectar al servidor")
        print("💡 Asegúrate de que el servidor Flask esté ejecutándose en localhost:8080")
        
    except requests.exceptions.Timeout:
        print("❌ Error de timeout: La petición tardó demasiado")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    print("\n=== FIN DE LA PRUEBA ===")

if __name__ == "__main__":
    test_graficos_endpoint()