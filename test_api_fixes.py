#!/usr/bin/env python3
"""
Script para probar las correcciones de los endpoints de API de asistencia
"""

import requests
import json

BASE_URL = 'http://localhost:8080'

def test_api_endpoints():
    """Probar los endpoints de API corregidos"""
    
    # Crear una sesión para mantener las cookies
    session = requests.Session()
    
    print("=== PRUEBA DE CORRECCIONES DE API ===\n")
    
    # 1. Hacer login primero
    print("1. Intentando hacer login...")
    login_data = {
        'username': '1032402333',
        'password': 'CE1032402333'
    }
    
    try:
        login_response = session.post(f'{BASE_URL}/', data=login_data)
        if login_response.status_code == 200:
            print("✓ Login exitoso")
        else:
            print(f"✗ Error en login: {login_response.status_code}")
            return
    except Exception as e:
        print(f"✗ Error de conexión en login: {e}")
        return
    
    # 2. Probar endpoint de actualizar campo
    print("\n2. Probando endpoint /api/asistencia/actualizar-campo...")
    
    test_data = {
        'cedula': '1019112308',  # Usar una cédula de prueba
        'campo': 'estado',
        'valor': 'CUMPLE'
    }
    
    try:
        response = session.post(
            f'{BASE_URL}/api/asistencia/actualizar-campo',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
        
        # Verificar si la respuesta es JSON
        try:
            json_response = response.json()
            print("✓ Respuesta es JSON válido:")
            print(json.dumps(json_response, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("✗ Respuesta NO es JSON válido:")
            print(f"Contenido: {response.text[:200]}...")
            
    except Exception as e:
        print(f"✗ Error en la petición: {e}")
    
    # 3. Probar endpoint de actualizar masivo
    print("\n3. Probando endpoint /api/asistencia/actualizar-masivo...")
    
    test_data_masivo = {
        'cambios': [
            {
                'cedula': '1019112308',
                'hora_inicio': '08:00',
                'estado': 'CUMPLE',
                'novedad': '',
                'fecha': '2025-01-17'
            }
        ]
    }
    
    try:
        response = session.post(
            f'{BASE_URL}/api/asistencia/actualizar-masivo',
            json=test_data_masivo,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
        
        # Verificar si la respuesta es JSON
        try:
            json_response = response.json()
            print("✓ Respuesta es JSON válido:")
            print(json.dumps(json_response, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("✗ Respuesta NO es JSON válido:")
            print(f"Contenido: {response.text[:200]}...")
            
    except Exception as e:
        print(f"✗ Error en la petición: {e}")

if __name__ == "__main__":
    test_api_endpoints()