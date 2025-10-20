#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el endpoint PUT de actualización de Técnico Mecánica
"""

import requests
import json
from datetime import datetime, timedelta

def test_update_tecnico_mecanica():
    """Probar el endpoint PUT para actualizar técnico mecánica"""
    
    # URL del endpoint
    base_url = "http://localhost:8080"
    
    print("=" * 60)
    print("PROBANDO ACTUALIZACIÓN DE TÉCNICO MECÁNICA")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        # 1. Hacer login primero
        print("1. Realizando login...")
        login_data = {
            'cedula': '1002407090',
            'password': 'CE1002407090'
        }
        
        login_response = session.post(f"{base_url}/", data=login_data)
        print(f"   Status Code Login: {login_response.status_code}")
        
        if login_response.status_code not in [200, 302]:
            print("   ❌ Login fallido")
            return False
        
        print("   ✅ Login exitoso")
        
        # 2. Obtener lista de técnico mecánica para encontrar un ID válido
        print("\n2. Obteniendo lista de técnico mecánica...")
        response = session.get(f"{base_url}/api/mpa/tecnico_mecanica")
        
        if response.status_code != 200:
            print(f"   ❌ Error al obtener lista: {response.status_code}")
            return False
        
        data = response.json()
        if not data.get('success') or not data.get('data'):
            print("   ❌ No hay datos de técnico mecánica")
            return False
        
        # Tomar el primer registro para actualizar
        tm_record = data['data'][0]
        tm_id = tm_record['id_mpa_tecnico_mecanica']
        print(f"   ✅ Usando registro ID: {tm_id}, Placa: {tm_record['placa']}")
        
        # 3. Probar actualización
        print(f"\n3. Probando actualización del registro ID {tm_id}...")
        
        # Datos de prueba para actualizar
        update_data = {
            'observaciones': f'Actualizado por script de prueba - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'estado': 'Activo'
        }
        
        print(f"   Datos a enviar: {json.dumps(update_data, indent=2)}")
        
        # Realizar petición PUT
        update_response = session.put(
            f"{base_url}/api/mpa/tecnico_mecanica/{tm_id}",
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status Code: {update_response.status_code}")
        print(f"   Response Headers: {dict(update_response.headers)}")
        
        try:
            response_data = update_response.json()
            print(f"   Response JSON: {json.dumps(response_data, indent=2)}")
            
            if update_response.status_code == 200 and response_data.get('success'):
                print("   ✅ Actualización exitosa")
                return True
            else:
                print(f"   ❌ Error en actualización: {response_data.get('error', 'Error desconocido')}")
                return False
                
        except json.JSONDecodeError:
            print(f"   ❌ Respuesta no es JSON válido: {update_response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_update_tecnico_mecanica()
    if success:
        print("\n🎉 PRUEBA EXITOSA")
    else:
        print("\n💥 PRUEBA FALLIDA")