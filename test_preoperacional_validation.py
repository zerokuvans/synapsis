#!/usr/bin/env python3
"""
Script para probar la validación del preoperacional con TON81E
"""

import requests
import json

def test_preoperacional_validation():
    # URL base - CORREGIDO: puerto 8080
    base_url = 'http://localhost:8080'
    
    # Datos de login - USAR USUARIO ADMIN PARA PROBAR
    login_data = {
        'username': '80833959',
        'password': 'Capired2024*'
    }
    
    # Crear sesión
    session = requests.Session()
    
    print('=== PROBANDO VALIDACIÓN DE PREOPERACIONAL ===')
    
    # 1. Login
    print('1. Realizando login...')
    login_response = session.post(f'{base_url}/login', data=login_data)
    print(f'   Status: {login_response.status_code}')
    
    if login_response.status_code != 200:
        print(f'   Error en login: {login_response.text}')
        return
    
    print(f'   Login exitoso: {login_response.text}')
    
    # 2. Intentar enviar preoperacional con TON81E
    print('2. Enviando preoperacional con vehículo TON81E...')
    
    preoperacional_data = {
        'placa_vehiculo': 'TON81E',
        'vehiculo_asignado': 'MOTO HONDA',
        'kilometraje': '12345',
        'nivel_combustible': 'Bueno',
        'nivel_aceite': 'Bueno',
        'nivel_liquido_frenos': 'Bueno',
        'nivel_refrigerante': 'Bueno',
        'presion_llantas': 'Bueno',
        'luces_funcionando': 'Si',
        'espejos_estado': 'Bueno',
        'cinturon_seguridad': 'Si',
        'extintor_presente': 'Si',
        'botiquin_presente': 'Si',
        'triangulos_seguridad': 'Si',
        'chaleco_reflectivo': 'Si',
        'casco_presente': 'Si',
        'guantes_presente': 'Si',
        'rodilleras_presente': 'Si',
        'impermeable_presente': 'Si',
        'observaciones_generales': 'Prueba de validación'
    }
    
    preop_response = session.post(f'{base_url}/preoperacional', 
                                 data=preoperacional_data,
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
    
    print(f'   Status: {preop_response.status_code}')
    print(f'   Response: {preop_response.text}')
    
    if preop_response.status_code == 400:
        print('   ✅ VALIDACIÓN FUNCIONANDO: El preoperacional fue bloqueado correctamente')
    else:
        print('   ❌ ERROR: El preoperacional NO fue bloqueado')

if __name__ == "__main__":
    test_preoperacional_validation()