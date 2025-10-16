#!/usr/bin/env python3
"""
Script para verificar las rutas registradas en el servidor Flask
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_routes():
    """Probar diferentes rutas para verificar cuáles están disponibles"""
    
    routes_to_test = [
        "/api/mpa/vencimientos",
        "/api/mpa/test-vencimientos", 
        "/api/mpa/soat",
        "/api/mpa/tecnico_mecanica",
        "/api/mpa/licencias-conducir",
        "/mpa/vencimientos",
        "/mpa/dashboard"
    ]
    
    print("🔍 Probando rutas en el servidor Flask...")
    print("=" * 60)
    
    for route in routes_to_test:
        try:
            url = f"{BASE_URL}{route}"
            response = requests.get(url, timeout=5)
            
            print(f"✅ {route}: Status {response.status_code}")
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    try:
                        data = response.json()
                        print(f"   📄 JSON Response: {json.dumps(data, indent=2)[:200]}...")
                    except:
                        print(f"   📄 Response length: {len(response.text)} chars")
                else:
                    print(f"   📄 HTML Response length: {len(response.text)} chars")
            elif response.status_code == 404:
                print(f"   ❌ Ruta no encontrada")
            elif response.status_code == 302:
                print(f"   🔄 Redirección a: {response.headers.get('Location', 'Unknown')}")
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {route}: Error de conexión - {e}")
    
    print("\n" + "=" * 60)
    print("✅ Prueba de rutas completada")

if __name__ == "__main__":
    test_routes()