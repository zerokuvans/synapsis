#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar específicamente el endpoint /api/supervisores
"""

import requests
import json

# Configuración del servidor
BASE_URL = "http://localhost:8080"

def test_supervisores_direct():
    """Prueba directa del endpoint de supervisores sin autenticación"""
    print("=== Probando /api/supervisores directamente ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/supervisores")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Respuesta exitosa:")
            print(f"Tipo de datos: {type(data)}")
            print(f"Contenido: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"Error: {response.status_code}")
            print(f"Contenido: {response.text}")
            
    except Exception as e:
        print(f"Error al hacer la petición: {e}")

def test_login_and_supervisores():
    """Prueba el login y luego el endpoint de supervisores"""
    
    # Datos de login - usando cédula real encontrada
    login_data = {
        'username': '80833959',  # VICTOR ALFONSO NARANJO SIERRA (rol 1 - admin)
        'password': 'admin123'   # Intentar con contraseña común
    }
    
    print("=== Probando /api/supervisores ===")
    
    try:
        # Crear sesión para mantener cookies
        session = requests.Session()
        
        print("1. Haciendo login...")
        login_response = session.post(f"{BASE_URL}/login", data=login_data)
        print(f"Login Status Code: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("❌ Error en login")
            return
        
        # Ahora probar el endpoint de supervisores
        print("\n2. Probando endpoint /api/supervisores...")
        response = session.get(f"{BASE_URL}/api/supervisores")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Success: {data.get('success')}")
                supervisores = data.get('supervisores', [])
                print(f"Número de supervisores: {len(supervisores)}")
                print(f"Supervisores: {supervisores}")
                
                if len(supervisores) == 0:
                    print("⚠️  No se encontraron supervisores")
                else:
                    print("✅ Supervisores encontrados correctamente")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error al decodificar JSON: {e}")
                print(f"Contenido de respuesta: {response.text}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Contenido: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en la petición: {str(e)}")

if __name__ == "__main__":
    # Primero probar sin autenticación
    test_supervisores_direct()
    print("\n" + "="*50 + "\n")
    # Luego probar con autenticación
    test_login_and_supervisores()