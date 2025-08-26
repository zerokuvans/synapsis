#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la validación de estado de usuario en el login
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8080"
LOGIN_URL = f"{BASE_URL}/"

def test_login_usuario_activo():
    """Probar login con usuario activo"""
    print("\n=== Probando login con usuario ACTIVO ===")
    
    session = requests.Session()
    
    # Datos de login para usuario activo (ajustar según tu BD)
    login_data = {
        'username': '1019112308',  # ALARCON SALAS LUIS HERNANDO - Estado: Activo
        'password': 'CE1019112308'   # Contraseña por defecto
    }
    
    try:
        response = session.post(LOGIN_URL, data=login_data, headers={
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print("✓ Login exitoso para usuario activo")
                return True
            else:
                print(f"✗ Login falló: {data.get('message')}")
                return False
        else:
            print(f"✗ Error en login: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error al probar login: {e}")
        return False

def test_login_usuario_inactivo():
    """Probar login con usuario inactivo"""
    print("\n=== Probando login con usuario INACTIVO ===")
    
    session = requests.Session()
    
    # Datos de login para usuario inactivo (ajustar según tu BD)
    login_data = {
        'username': '1000954206',  # FELIPE SANCHEZ - Estado: Inactivo
        'password': 'CE1000954206'   # Contraseña por defecto
    }
    
    try:
        response = session.post(LOGIN_URL, data=login_data, headers={
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 403:
            data = response.json()
            if 'inactiva' in data.get('message', '').lower():
                print("✓ Validación de usuario inactivo funcionando correctamente")
                print(f"Mensaje: {data.get('message')}")
                return True
            else:
                print(f"✗ Mensaje inesperado: {data.get('message')}")
                return False
        else:
            print(f"✗ Status code inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error al probar login: {e}")
        return False

def main():
    """Función principal para ejecutar todas las pruebas"""
    print("=" * 60)
    print("PRUEBAS DE VALIDACIÓN DE ESTADO DE USUARIO")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Probar usuario activo
    resultado_activo = test_login_usuario_activo()
    
    # Probar usuario inactivo
    resultado_inactivo = test_login_usuario_inactivo()
    
    print("\n=== RESUMEN DE PRUEBAS ===")
    print(f"Usuario activo: {'✓ PASS' if resultado_activo else '✗ FAIL'}")
    print(f"Usuario inactivo: {'✓ PASS' if resultado_inactivo else '✗ FAIL'}")
    
    if resultado_activo and resultado_inactivo:
        print("\n🎉 Todas las pruebas pasaron exitosamente")
        print("La validación de estado de usuario está funcionando correctamente")
    else:
        print("\n⚠️ Algunas pruebas fallaron")
        print("Revisar la implementación o los datos de prueba")

if __name__ == "__main__":
    main()