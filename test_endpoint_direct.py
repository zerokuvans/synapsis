#!/usr/bin/env python3
"""
Script para probar directamente el endpoint /preoperacional sin autenticación
"""

import requests
import json

def test_preoperacional_endpoint():
    print('=== PROBANDO ENDPOINT /preoperacional DIRECTAMENTE ===')
    
    base_url = 'http://localhost:8080'
    
    # Datos de prueba que deberían fallar por mantenimiento abierto
    test_data = {
        'placa_vehiculo': 'TON81E',
        'codigo_consumidor': '1019112308',
        'fecha': '2025-01-20',
        'hora': '08:00',
        'kilometraje': '50000',
        'nivel_combustible': '75',
        'observaciones': 'Prueba de validación'
    }
    
    print(f'1. Enviando datos al endpoint /preoperacional...')
    print(f'   Datos: {json.dumps(test_data, indent=2)}')
    
    try:
        # Intentar con Content-Type: application/json
        print(f'\n2. Probando con Content-Type: application/json')
        response = requests.post(
            f'{base_url}/preoperacional',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f'   Status Code: {response.status_code}')
        print(f'   Headers: {dict(response.headers)}')
        
        # Verificar si es JSON o HTML
        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type:
            print(f'   Response JSON: {response.json()}')
        else:
            print(f'   Response HTML (primeros 200 chars): {response.text[:200]}...')
        
        if response.status_code == 400:
            print(f'   ✅ CORRECTO: El endpoint está bloqueando correctamente')
        elif response.status_code == 401:
            print(f'   🔒 AUTENTICACIÓN: Se requiere login (esperado)')
        elif response.status_code == 200:
            print(f'   ❌ ERROR CRÍTICO: El endpoint está permitiendo el acceso sin autenticación')
        else:
            print(f'   ❓ INESPERADO: Status code no esperado')
            
    except requests.exceptions.ConnectionError:
        print(f'   ❌ ERROR: No se pudo conectar al servidor en {base_url}')
        print(f'   Asegúrate de que el servidor Flask esté ejecutándose')
    except Exception as e:
        print(f'   ❌ ERROR: {e}')

if __name__ == "__main__":
    test_preoperacional_endpoint()