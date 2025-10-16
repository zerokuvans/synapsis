#!/usr/bin/env python3
"""
Script de prueba para las APIs de vencimientos
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_vencimientos_api():
    """Probar la API de vencimientos"""
    print("🔍 Probando API de vencimientos...")
    
    try:
        # Probar la API de vencimientos
        response = requests.get(f"{BASE_URL}/api/mpa/vencimientos")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API de vencimientos funciona correctamente")
            print(f"Datos recibidos: {len(data.get('data', []))} vencimientos")
        elif response.status_code == 401:
            print("⚠️ API requiere autenticación")
        elif response.status_code == 404:
            print("❌ API no encontrada - verificar rutas")
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - verificar que el servidor esté ejecutándose")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_page_access():
    """Probar acceso a la página de vencimientos"""
    print("\n🔍 Probando acceso a la página de vencimientos...")
    
    try:
        response = requests.get(f"{BASE_URL}/mpa/vencimientos")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Página de vencimientos accesible")
        elif response.status_code == 302:
            print("⚠️ Redirección (probablemente requiere login)")
        elif response.status_code == 404:
            print("❌ Página no encontrada")
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_server_connectivity():
    """Probar conectividad básica del servidor"""
    print("\n🔍 Probando conectividad del servidor...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 302]:
            print("✅ Servidor accesible")
            return True
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - servidor no accesible")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de vencimientos")
    print("=" * 50)
    
    # Probar conectividad básica
    if test_server_connectivity():
        # Probar página
        test_page_access()
        
        # Probar API
        test_vencimientos_api()
    
    print("\n✅ Pruebas completadas")