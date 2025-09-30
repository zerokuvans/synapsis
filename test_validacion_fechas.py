#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar las validaciones de fecha en el endpoint de resumen de asistencia
"""

import requests
import json
from datetime import datetime, date, timedelta

# Configuración
BASE_URL = 'http://localhost:8080'
USERNAME = '80833959'  # Usuario proporcionado
PASSWORD = 'M4r14l4r@'  # Contraseña proporcionada

def test_validaciones_fecha():
    """Probar las validaciones de fecha implementadas"""
    
    print("=" * 60)
    print("PRUEBA: VALIDACIONES DE FECHA EN RESUMEN DE ASISTENCIA")
    print("=" * 60)
    
    # Crear sesión
    session = requests.Session()
    
    # 1. Login
    print("\n1. Realizando login...")
    login_data = {
        'cedula': USERNAME,
        'password': PASSWORD
    }
    
    login_response = session.post(f'{BASE_URL}/', data=login_data)
    
    if login_response.status_code == 200:
        print("✓ Login exitoso")
    else:
        print(f"✗ Error en login: {login_response.status_code}")
        return
    
    # Fechas para pruebas
    hoy = date.today()
    ayer = hoy - timedelta(days=1)
    manana = hoy + timedelta(days=1)
    hace_un_ano = hoy - timedelta(days=365)
    hace_dos_anos = hoy - timedelta(days=730)
    
    # 2. Prueba: Fecha inicio mayor que fecha fin
    print("\n2. Probando fecha inicio mayor que fecha fin...")
    url = f'{BASE_URL}/api/asistencia/resumen_agrupado?fecha_inicio={hoy}&fecha_fin={ayer}'
    response = session.get(url)
    
    if response.status_code == 400:
        data = response.json()
        if 'fecha de inicio no puede ser mayor' in data.get('message', '').lower():
            print("✓ Validación correcta: fecha inicio > fecha fin")
        else:
            print(f"✗ Mensaje incorrecto: {data.get('message')}")
    else:
        print(f"✗ Debería devolver error 400, pero devolvió: {response.status_code}")
    
    # 3. Prueba: Fechas futuras
    print("\n3. Probando fechas futuras...")
    url = f'{BASE_URL}/api/asistencia/resumen_agrupado?fecha_inicio={manana}&fecha_fin={manana}'
    response = session.get(url)
    
    if response.status_code == 400:
        data = response.json()
        if 'futuras' in data.get('message', '').lower():
            print("✓ Validación correcta: fechas futuras")
        else:
            print(f"✗ Mensaje incorrecto: {data.get('message')}")
    else:
        print(f"✗ Debería devolver error 400, pero devolvió: {response.status_code}")
    
    # 4. Prueba: Rango mayor a 1 año
    print("\n4. Probando rango mayor a 1 año...")
    url = f'{BASE_URL}/api/asistencia/resumen_agrupado?fecha_inicio={hace_dos_anos}&fecha_fin={hoy}'
    response = session.get(url)
    
    if response.status_code == 400:
        data = response.json()
        if 'mayor a 1 año' in data.get('message', '').lower():
            print("✓ Validación correcta: rango mayor a 1 año")
        else:
            print(f"✗ Mensaje incorrecto: {data.get('message')}")
    else:
        print(f"✗ Debería devolver error 400, pero devolvió: {response.status_code}")
    
    # 5. Prueba: Rango válido
    print("\n5. Probando rango válido...")
    url = f'{BASE_URL}/api/asistencia/resumen_agrupado?fecha_inicio={ayer}&fecha_fin={hoy}'
    response = session.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✓ Rango válido procesado correctamente")
            print(f"  - Total general: {data['data'].get('total_general', 0)}")
            print(f"  - Grupos encontrados: {len(data['data'].get('resumen_grupos', []))}")
        else:
            print(f"✗ Respuesta no exitosa: {data.get('message')}")
    else:
        print(f"✗ Error en rango válido: {response.status_code}")
    
    # 6. Prueba: Formato de fecha inválido
    print("\n6. Probando formato de fecha inválido...")
    url = f'{BASE_URL}/api/asistencia/resumen_agrupado?fecha_inicio=2025-13-45&fecha_fin=2025-01-01'
    response = session.get(url)
    
    if response.status_code == 400:
        data = response.json()
        if 'formato' in data.get('message', '').lower():
            print("✓ Validación correcta: formato inválido")
        else:
            print(f"✗ Mensaje incorrecto: {data.get('message')}")
    else:
        print(f"✗ Debería devolver error 400, pero devolvió: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("PRUEBAS COMPLETADAS")
    print("=" * 60)

if __name__ == '__main__':
    test_validaciones_fecha()