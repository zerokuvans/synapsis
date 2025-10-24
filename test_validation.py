#!/usr/bin/env python3
"""
Script para probar la validación de mantenimientos en el preoperacional
"""

import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/login"
PREOPERACIONAL_URL = f"{BASE_URL}/preoperacional"

# Datos de prueba
TEST_USER = "1019112308"
TEST_PASSWORD = "123456"  # Asumiendo que esta es la contraseña
TEST_VEHICLE = "TON81E"

def test_preoperacional_validation():
    """Prueba la validación de mantenimientos en el preoperacional"""
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    print("=== PRUEBA DE VALIDACIÓN DE MANTENIMIENTOS ===")
    print(f"Usuario: {TEST_USER}")
    print(f"Vehículo: {TEST_VEHICLE}")
    
    # 1. Login
    print("\n1. Intentando login...")
    login_data = {
        'username': TEST_USER,
        'password': TEST_PASSWORD
    }
    
    login_response = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
    
    # Verificar si el login fue exitoso (redirección a /tecnicos, /dashboard o /verificar_registro_preoperacional)
    if login_response.status_code == 200 and (
        '/tecnicos' in login_response.url or 
        '/dashboard' in login_response.url or
        '/verificar_registro_preoperacional' in login_response.url
    ):
        print("✓ Login exitoso")
        print(f"Redirigido a: {login_response.url}")
    else:
        print("✗ Error en login")
        print(f"Status: {login_response.status_code}")
        print(f"URL: {login_response.url}")
        return
    
    # 2. Intentar enviar preoperacional
    print("\n2. Intentando enviar preoperacional...")
    
    preoperacional_data = {
        'placa_vehiculo': TEST_VEHICLE,
        'kilometraje': '50000',
        'nivel_combustible': '75',
        'observaciones': 'Prueba de validación de mantenimientos',
        'firma_tecnico': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
    }
    
    preoperacional_response = session.post(PREOPERACIONAL_URL, json=preoperacional_data)
    
    print(f"Status Code: {preoperacional_response.status_code}")
    
    try:
        response_json = preoperacional_response.json()
        print(f"Response: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
        
        # Verificar si la validación funcionó
        if not response_json.get('success', True) and 'mantenimiento' in response_json.get('message', '').lower():
            print("\n✓ VALIDACIÓN FUNCIONANDO CORRECTAMENTE")
            print("✓ El sistema está bloqueando el preoperacional por mantenimientos abiertos")
        else:
            print("\n✗ VALIDACIÓN NO FUNCIONANDO")
            print("✗ El sistema permitió el preoperacional a pesar de tener mantenimientos abiertos")
            
    except json.JSONDecodeError:
        print(f"Response text: {preoperacional_response.text}")
    
    print("\n=== FIN DE LA PRUEBA ===")

if __name__ == "__main__":
    test_preoperacional_validation()