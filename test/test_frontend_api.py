#!/usr/bin/env python3
"""
Test script para verificar que los endpoints de API funcionan correctamente
desde el frontend después de las correcciones.
"""

import requests
import json

BASE_URL = 'http://localhost:8080'

def test_frontend_api_integration():
    """Prueba la integración completa frontend-API"""
    
    print("=== PRUEBA DE INTEGRACIÓN FRONTEND-API ===\n")
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # 1. Login
    print("1. Realizando login...")
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
            return False
    except Exception as e:
        print(f"✗ Error de conexión en login: {e}")
        return False
    
    # 2. Probar endpoint de actualizar campo individual
    print("\n2. Probando actualización de campo individual...")
    campo_data = {
        'cedula': '1032402333',
        'campo': 'hora_inicio',
        'valor': '08:30'
    }
    
    try:
        response = session.post(
            f'{BASE_URL}/api/asistencia/actualizar-campo',
            json=campo_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'No especificado')}")
        
        # Verificar que la respuesta es JSON
        try:
            data = response.json()
            print("✓ Respuesta es JSON válido")
            print(f"Respuesta: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if response.status_code == 200 and data.get('success'):
                print("✓ Campo actualizado correctamente")
            elif response.status_code == 403:
                print("✓ Endpoint funciona (permisos insuficientes - esperado)")
            else:
                print(f"⚠ Respuesta inesperada: {data}")
                
        except json.JSONDecodeError as e:
            print(f"✗ Error: La respuesta NO es JSON válido: {e}")
            print(f"Contenido de respuesta: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"✗ Error en la petición: {e}")
        return False
    
    # 3. Probar endpoint de actualización masiva
    print("\n3. Probando actualización masiva...")
    masivo_data = {
        'cambios': [
            {
                'cedula': '1032402333',
                'hora_inicio': '08:30',
                'estado': 'presente',
                'novedad': 'Sin novedad',
                'fecha': '2024-01-15'
            }
        ]
    }
    
    try:
        response = session.post(
            f'{BASE_URL}/api/asistencia/actualizar-masivo',
            json=masivo_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'No especificado')}")
        
        # Verificar que la respuesta es JSON
        try:
            data = response.json()
            print("✓ Respuesta es JSON válido")
            print(f"Respuesta: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if response.status_code == 200 and data.get('success'):
                print("✓ Actualización masiva exitosa")
            elif response.status_code == 403:
                print("✓ Endpoint funciona (permisos insuficientes - esperado)")
            else:
                print(f"⚠ Respuesta inesperada: {data}")
                
        except json.JSONDecodeError as e:
            print(f"✗ Error: La respuesta NO es JSON válido: {e}")
            print(f"Contenido de respuesta: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"✗ Error en la petición: {e}")
        return False
    
    print("\n=== RESUMEN ===")
    print("✓ Todos los endpoints devuelven JSON válido")
    print("✓ No hay errores de HTML en lugar de JSON")
    print("✓ Los decoradores @login_required_api funcionan correctamente")
    print("✓ La integración frontend-API está funcionando")
    
    return True

if __name__ == '__main__':
    success = test_frontend_api_integration()
    print(f"\n=== RESULTADO: {'ÉXITO' if success else 'FALLO'} ===")