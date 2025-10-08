#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = 'http://localhost:8080'
LOGIN_URL = f'{BASE_URL}/'
ACTUALIZAR_URL = f'{BASE_URL}/api/asistencia/actualizar-campo'

# Credenciales de prueba
USERNAME = '1032402333'
PASSWORD = 'CE1032402333'

def test_actualizar_campo_debug():
    """Test específico para debuggear el problema de actualización"""
    
    print("🧪 Test de Debug - Endpoint actualizar-campo")
    print("=" * 60)
    
    # Crear sesión
    session = requests.Session()
    
    # 1. Login
    print("1️⃣ Realizando login...")
    login_data = {'username': USERNAME, 'password': PASSWORD}
    login_response = session.post(LOGIN_URL, data=login_data)
    
    if login_response.status_code == 200:
        print("✅ Login exitoso")
    else:
        print(f"❌ Error en login: {login_response.status_code}")
        return
    
    # 2. Probar actualización con la cédula que está causando problemas
    cedula_test = "5694500"  # Cédula que aparece en los logs
    
    print(f"\n2️⃣ Probando actualización para cédula: {cedula_test}")
    
    # Test 1: Actualizar novedad (que está causando el error)
    print("\n📝 Test 1: Actualizar novedad...")
    data_novedad = {
        'cedula': cedula_test,
        'campo': 'novedad',
        'valor': 'Test de debug'
    }
    
    response_novedad = session.post(
        ACTUALIZAR_URL,
        headers={'Content-Type': 'application/json'},
        data=json.dumps(data_novedad)
    )
    
    print(f"   Status: {response_novedad.status_code}")
    print(f"   Response: {response_novedad.text}")
    
    # Test 2: Actualizar estado
    print("\n📝 Test 2: Actualizar estado...")
    data_estado = {
        'cedula': cedula_test,
        'campo': 'estado',
        'valor': 'NO CUMPLE'
    }
    
    response_estado = session.post(
        ACTUALIZAR_URL,
        headers={'Content-Type': 'application/json'},
        data=json.dumps(data_estado)
    )
    
    print(f"   Status: {response_estado.status_code}")
    print(f"   Response: {response_estado.text}")
    
    # Test 3: Actualizar hora_inicio
    print("\n📝 Test 3: Actualizar hora_inicio...")
    data_hora = {
        'cedula': cedula_test,
        'campo': 'hora_inicio',
        'valor': '09:15'
    }
    
    response_hora = session.post(
        ACTUALIZAR_URL,
        headers={'Content-Type': 'application/json'},
        data=json.dumps(data_hora)
    )
    
    print(f"   Status: {response_hora.status_code}")
    print(f"   Response: {response_hora.text}")
    
    # Test 4: Probar con otra cédula que sabemos que existe
    print(f"\n3️⃣ Probando con otra cédula...")
    cedula_test2 = "84455827"  # Otra cédula de los registros de hoy
    
    data_test2 = {
        'cedula': cedula_test2,
        'campo': 'novedad',
        'valor': 'Test con otra cédula'
    }
    
    response_test2 = session.post(
        ACTUALIZAR_URL,
        headers={'Content-Type': 'application/json'},
        data=json.dumps(data_test2)
    )
    
    print(f"   Status: {response_test2.status_code}")
    print(f"   Response: {response_test2.text}")
    
    print("\n" + "=" * 60)
    print("🔍 ANÁLISIS COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    test_actualizar_campo_debug()