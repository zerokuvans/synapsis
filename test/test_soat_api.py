#!/usr/bin/env python3
"""
Script para probar las APIs de SOAT
"""

import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8080"
API_URL = f"{BASE_URL}/api/mpa/soat"

def test_soat_api():
    """Probar la API de SOAT"""
    try:
        print("Probando API de SOAT...")
        
        # Probar GET /api/mpa/soat
        print(f"GET {API_URL}")
        response = requests.get(API_URL)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ API de SOAT funcionando correctamente")
        else:
            print("❌ Error en API de SOAT")
            
    except Exception as e:
        print(f"❌ Error al probar API: {e}")

def test_vehiculos_api():
    """Probar la API de vehículos para comparar"""
    try:
        print("\nProbando API de vehículos (para comparar)...")
        
        # Probar GET /api/mpa/vehiculos/placas
        url = f"{BASE_URL}/api/mpa/vehiculos/placas"
        print(f"GET {url}")
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ API de vehículos funcionando correctamente")
        else:
            print("❌ Error en API de vehículos")
            
    except Exception as e:
        print(f"❌ Error al probar API: {e}")

if __name__ == "__main__":
    test_soat_api()
    test_vehiculos_api()