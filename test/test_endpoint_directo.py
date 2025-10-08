#!/usr/bin/env python3
"""
Script para probar directamente el endpoint de detalle de técnicos
"""
import requests
import json

# Configuración
BASE_URL = "http://192.168.80.39:8080"
LOGIN_URL = f"{BASE_URL}/login"
ENDPOINT_URL = f"{BASE_URL}/api/indicadores/detalle_tecnicos"

# Credenciales de administrador
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def test_endpoint():
    """Probar el endpoint directamente"""
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        print("🔍 Iniciando sesión...")
        
        # Hacer login
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        login_response = session.post(LOGIN_URL, data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.status_code}")
            return
            
        print("✅ Login exitoso")
        
        # Probar el endpoint
        params = {
            'fecha': '2025-01-10',
            'supervisor': 'CORTES CUERVO SANDRA CECILIA'
        }
        
        print(f"🔍 Llamando endpoint: {ENDPOINT_URL}")
        print(f"📋 Parámetros: {params}")
        
        response = session.get(ENDPOINT_URL, params=params)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Respuesta JSON válida:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Analizar la respuesta
                if data.get('success'):
                    tecnicos = data.get('tecnicos', [])
                    print(f"\n📊 Análisis:")
                    print(f"   - success: {data.get('success')}")
                    print(f"   - tecnicos count: {len(tecnicos)}")
                    
                    if tecnicos:
                        print(f"   - Primer técnico: {tecnicos[0]}")
                    else:
                        print("   - No hay técnicos en la respuesta")
                else:
                    print(f"❌ success = False")
                    print(f"   - message: {data.get('message', 'No message')}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"📄 Respuesta raw: {response.text[:500]}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Respuesta: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_endpoint()