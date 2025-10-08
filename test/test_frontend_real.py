#!/usr/bin/env python3
"""
Script para simular exactamente lo que hace el frontend
"""
import requests
import json

# Configuración
BASE_URL = "http://192.168.80.39:8080"
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def test_frontend_simulation():
    """Simular exactamente el comportamiento del frontend"""
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        print("🔍 1. Accediendo a la página principal...")
        
        # Primero acceder a la página principal
        main_page = session.get(BASE_URL)
        print(f"   Status: {main_page.status_code}")
        
        print("🔍 2. Haciendo login...")
        
        # Hacer login con headers que simula el navegador
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': BASE_URL,
            'Referer': BASE_URL
        }
        
        login_response = session.post(f"{BASE_URL}/", data=login_data, headers=headers)
        print(f"   Status: {login_response.status_code}")
        print(f"   URL final: {login_response.url}")
        
        if 'dashboard' not in login_response.url:
            print("❌ Login falló")
            return
            
        print("✅ Login exitoso")
        
        print("🔍 3. Accediendo al módulo de indicadores...")
        
        # Acceder al módulo de indicadores
        indicadores_url = f"{BASE_URL}/administrativo/indicadores"
        indicadores_response = session.get(indicadores_url, headers=headers)
        print(f"   Status: {indicadores_response.status_code}")
        
        print("🔍 4. Llamando al endpoint de detalle técnicos...")
        
        # Simular la llamada AJAX del frontend
        ajax_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'es-ES,es;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': indicadores_url
        }
        
        params = {
            'fecha': '2025-01-10',
            'supervisor': 'CORTES CUERVO SANDRA CECILIA'
        }
        
        endpoint_url = f"{BASE_URL}/api/indicadores/detalle_tecnicos"
        response = session.get(endpoint_url, params=params, headers=ajax_headers)
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Respuesta JSON válida:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Simular exactamente la lógica del frontend
                print("\n🔍 5. Simulando lógica del frontend...")
                print(f"   data.success === true: {data.get('success') is True}")
                print(f"   data.tecnicos existe: {data.get('tecnicos') is not None}")
                print(f"   data.tecnicos.length > 0: {len(data.get('tecnicos', [])) > 0}")
                
                # Condición exacta del frontend
                if data.get('success') is True and data.get('tecnicos') and len(data.get('tecnicos', [])) > 0:
                    print("✅ FRONTEND: Condición cumplida - Mostraría datos reales")
                    tecnicos = data.get('tecnicos', [])
                    print(f"   Técnicos a mostrar: {len(tecnicos)}")
                    for i, tecnico in enumerate(tecnicos[:3]):  # Mostrar solo los primeros 3
                        print(f"   {i+1}. {tecnico.get('nombre', 'N/A')} - {tecnico.get('estado', 'N/A')}")
                else:
                    print("❌ FRONTEND: Condición NO cumplida - Mostraría mensaje sin datos")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"   Respuesta raw: {response.text[:500]}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_frontend_simulation()