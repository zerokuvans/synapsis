#!/usr/bin/env python3
"""
Script para probar los endpoints de configuración de hora preoperacional
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_get_hora_preoperacional():
    """Probar endpoint GET para obtener hora límite"""
    print("🔍 Probando GET /api/configuracion/hora-preoperacional")
    try:
        response = requests.get(f"{BASE_URL}/api/configuracion/hora-preoperacional")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_update_hora_preoperacional(nueva_hora):
    """Probar endpoint PUT para actualizar hora límite"""
    print(f"\n📝 Probando PUT /api/configuracion/hora-preoperacional con hora: {nueva_hora}")
    try:
        data = {"hora_limite": nueva_hora}
        response = requests.put(
            f"{BASE_URL}/api/configuracion/hora-preoperacional",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de API de hora preoperacional\n")
    
    # Probar GET
    current_config = test_get_hora_preoperacional()
    
    # Probar UPDATE (solo si GET funcionó)
    if current_config and current_config.get('success'):
        print(f"\n✅ Configuración actual: {current_config['data']['hora_limite_formatted']}")
        
        # Probar actualización a una nueva hora
        test_update_hora_preoperacional("11:30")
        
        # Verificar que se actualizó
        print("\n🔄 Verificando actualización...")
        updated_config = test_get_hora_preoperacional()
        
        if updated_config and updated_config.get('success'):
            print(f"✅ Nueva configuración: {updated_config['data']['hora_limite_formatted']}")
        
        # Restaurar hora original
        if current_config['data']['hora_limite_formatted'] != "11:30":
            print(f"\n🔄 Restaurando hora original: {current_config['data']['hora_limite_formatted']}")
            test_update_hora_preoperacional(current_config['data']['hora_limite_formatted'])
    
    print("\n🏁 Pruebas completadas")