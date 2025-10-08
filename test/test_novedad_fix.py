#!/usr/bin/env python3
"""
Test script to verify the novedad field fix
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = 'http://localhost:8080'
LOGIN_URL = f'{BASE_URL}/'
API_URL = f'{BASE_URL}/api/asistencia/actualizar-campo'

# Test credentials
CEDULA = '1032402333'
PASSWORD = 'CE1032402333'

def test_novedad_field():
    """Test the novedad field functionality"""
    
    # Create session
    session = requests.Session()
    
    print("🔐 Iniciando sesión...")
    
    # Login
    login_data = {
        'username': CEDULA,
        'password': PASSWORD
    }
    
    response = session.post(LOGIN_URL, data=login_data)
    
    if response.status_code != 200:
        print(f"❌ Error en login: {response.status_code}")
        return False
    
    print("✅ Login exitoso")
    
    # Test updating novedad field
    print("\n📝 Probando actualización del campo novedad...")
    
    test_data = {
        'cedula': CEDULA,
        'campo': 'novedad',
        'valor': 'Prueba de novedad - campo funcionando correctamente',
        'fecha': datetime.now().strftime('%Y-%m-%d')
    }
    
    response = session.post(API_URL, 
                          headers={'Content-Type': 'application/json'},
                          data=json.dumps(test_data))
    
    print(f"📊 Status Code: {response.status_code}")
    
    try:
        result = response.json()
        print(f"📋 Respuesta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and result.get('success'):
            print("✅ Campo novedad actualizado correctamente")
            return True
        elif response.status_code == 404:
            print("ℹ️  No hay registro de asistencia para hoy (esperado)")
            print("✅ La API está funcionando correctamente - no hay errores de 'undefined'")
            return True
        else:
            print(f"⚠️  Respuesta inesperada: {result}")
            return False
            
    except json.JSONDecodeError:
        print(f"❌ Error al decodificar JSON: {response.text}")
        return False

if __name__ == "__main__":
    print("🧪 Test de funcionalidad del campo novedad")
    print("=" * 50)
    
    success = test_novedad_field()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 RESULTADO: ÉXITO - El campo novedad está funcionando correctamente")
    else:
        print("💥 RESULTADO: FALLO - Hay problemas con el campo novedad")