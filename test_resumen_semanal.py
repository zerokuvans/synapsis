#!/usr/bin/env python3
"""
Script para probar el nuevo endpoint /api/resumen-semanal
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8080"
USERNAME = "80833959"  # Usuario administrativo
PASSWORD = "732137A031E4b@"

def test_resumen_semanal():
    """Probar el endpoint /api/resumen-semanal"""
    print("=== PRUEBA DEL ENDPOINT /api/resumen-semanal ===")
    
    # Crear sesión
    session = requests.Session()
    
    # 1. Login
    print("[1] Realizando login...")
    try:
        # Obtener página de login
        session.get(f"{BASE_URL}/")
        
        # Realizar login
        login_data = {
            "username": USERNAME,
            "password": PASSWORD
        }
        
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        login_response = session.post(f"{BASE_URL}/", data=login_data, headers=headers, allow_redirects=True)
        
        if "dashboard" in login_response.url or session.cookies.get('session'):
            print("   ✅ Login exitoso")
        else:
            print("   ❌ Login fallido")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False
    
    # 2. Probar endpoint
    print("\n[2] Probando endpoint /api/resumen-semanal...")
    try:
        params = {
            'fecha_inicio': '2025-10-06',
            'fecha_fin': '2025-10-12'
        }
        
        response = session.get(f"{BASE_URL}/api/resumen-semanal", params=params)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Respuesta exitosa")
            print(f"   Success: {data.get('success')}")
            
            if data.get('success') and 'resumen' in data:
                resumen = data['resumen']
                print(f"   Cantidad de analistas: {len(resumen)}")
                
                if len(resumen) > 0:
                    print(f"\n   Primer analista:")
                    primer_analista = resumen[0]
                    print(json.dumps(primer_analista, indent=4, ensure_ascii=False))
                    
                    print(f"\n   Campos disponibles:")
                    for key, value in primer_analista.items():
                        print(f"     - {key}: {value} ({type(value).__name__})")
                else:
                    print("   ⚠️  No hay datos de analistas para esta semana")
            else:
                print(f"   ❌ Error en respuesta: {data.get('error', 'Error desconocido')}")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error en petición: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_resumen_semanal()