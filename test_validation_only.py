#!/usr/bin/env python3
"""
Script para probar solo la validación de mantenimientos abiertos
"""

import requests
import json

def test_validation_only():
    """Probar solo la validación de mantenimientos abiertos"""
    
    print('=== PRUEBA DE VALIDACIÓN DE MANTENIMIENTOS ABIERTOS (SOLO VALIDACIÓN) ===\n')
    
    # Configuración
    BASE_URL = 'http://localhost:8080'
    LOGIN_URL = f'{BASE_URL}/login'
    PREOP_URL = f'{BASE_URL}/preoperacional'
    
    # Crear sesión
    session = requests.Session()
    
    # 1. Login
    print('1. Intentando hacer login...')
    login_data = {
        'username': '1019112308',
        'password': '123456'
    }
    
    login_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    login_response = session.post(LOGIN_URL, data=login_data, headers=login_headers)
    
    print(f'   Status code del login: {login_response.status_code}')
    
    if login_response.status_code == 200:
        try:
            login_json = login_response.json()
            print(f'   Respuesta JSON del login: {json.dumps(login_json, indent=2, ensure_ascii=False)}')
            
            if login_json.get('status') == 'success':
                print('   ✅ Login exitoso')
            else:
                print('   ❌ Login fallido')
                return
        except json.JSONDecodeError:
            print('   ❌ La respuesta del login no es JSON válido')
            return
    else:
        print('   ❌ Error en el login')
        return
    
    # 2. Probar endpoint con datos mínimos
    print('\n2. Probando endpoint /preoperacional con datos mínimos...')
    
    # Datos mínimos para activar solo la validación
    preop_data = {
        'id_codigo_consumidor': '11',  # ID del usuario logueado
        'placa_vehiculo': 'TON81E',
        'kilometraje_actual': '100000'  # Un valor que no cause problemas de kilometraje
    }
    
    preop_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    preop_response = session.post(PREOP_URL, data=preop_data, headers=preop_headers)
    
    print(f'   Status code: {preop_response.status_code}')
    print(f'   Content-Type: {preop_response.headers.get("Content-Type", "No especificado")}')
    
    if preop_response.status_code == 400:
        try:
            response_json = preop_response.json()
            print(f'   ✅ Respuesta JSON (validación funcionando): {json.dumps(response_json, indent=2, ensure_ascii=False)}')
            
            if response_json.get('tiene_mantenimientos_abiertos'):
                print('   🎯 ¡VALIDACIÓN EXITOSA! El sistema está bloqueando correctamente el preoperacional por mantenimientos abiertos')
            else:
                print('   ⚠️ La validación no detectó mantenimientos abiertos')
                
        except json.JSONDecodeError:
            print('   ❌ La respuesta no es JSON válido')
            print(f'   Contenido de la respuesta: {preop_response.text[:500]}...')
    
    elif preop_response.status_code == 500:
        print('   ❌ Error 500 - hay un problema en el código')
        print(f'   Contenido de la respuesta: {preop_response.text[:500]}...')
    
    else:
        print(f'   ⚠️ Status code inesperado: {preop_response.status_code}')
        try:
            response_json = preop_response.json()
            print(f'   Respuesta JSON: {json.dumps(response_json, indent=2, ensure_ascii=False)}')
        except json.JSONDecodeError:
            print(f'   Contenido de la respuesta: {preop_response.text[:500]}...')

if __name__ == "__main__":
    test_validation_only()