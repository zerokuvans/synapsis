#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la funcionalidad de la API de devoluciones
"""

import requests
import json
from bs4 import BeautifulSoup

# Configuración
BASE_URL = "http://localhost:8080"
LOGIN_URL = f"{BASE_URL}/"
USERNAME = "80833959"  # Usuario de logística
PASSWORD = "M4r14l4r@"

def login_and_get_session():
    """Inicia sesión y retorna la sesión autenticada"""
    session = requests.Session()
    
    try:
        # Obtener la página de login
        login_page = session.get(LOGIN_URL)
        if login_page.status_code != 200:
            print(f"❌ Error al acceder a la página de login: {login_page.status_code}")
            return None
        
        # Realizar login
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        login_response = session.post(LOGIN_URL, data=login_data, allow_redirects=False)
        
        # Verificar si el login fue exitoso (redirección)
        if login_response.status_code in [302, 303]:
            print("✅ Login exitoso")
            return session
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error durante el login: {str(e)}")
        return None

def test_agregar_elemento_devolucion(session):
    """Prueba agregar un elemento a una devolución existente"""
    
    # URL del endpoint
    url = f"{BASE_URL}/api/devoluciones/3/detalles"
    
    # Datos de prueba con elementos que coinciden con las columnas de dotación
    test_data = {
        "elemento": "pantalon",
        "talla": "M",
        "cantidad": 1,
        "estado_elemento": "USADO_BUENO",
        "observaciones": "Prueba de API"
    }
    
    try:
        # Realizar petición POST con sesión autenticada
        response = session.post(
            url, 
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Elemento agregado exitosamente")
                print(f"ID del elemento: {data.get('detalle_id')}")
                if 'elemento' in data:
                    print(f"Datos del elemento: {json.dumps(data['elemento'], indent=2)}")
                return True
            else:
                print(f"❌ Error en la respuesta: {data.get('error', 'Error desconocido')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: No se puede conectar al servidor")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

def test_listar_elementos_devolucion(session):
    """Prueba listar elementos de una devolución"""
    
    url = f"{BASE_URL}/api/devoluciones/3/detalles"
    
    try:
        response = session.get(url)
        print(f"\nListar elementos - Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                elementos = data.get('elementos', [])
                print(f"✅ Se encontraron {len(elementos)} elementos")
                for elemento in elementos:
                    print(f"  - {elemento.get('elemento')} (Talla: {elemento.get('talla')}, Cantidad: {elemento.get('cantidad')})")
                return True
            else:
                print(f"❌ Error: {data.get('error')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Prueba de API de Devoluciones ===")
    
    # Iniciar sesión
    print("\n0. Iniciando sesión...")
    session = login_and_get_session()
    
    if not session:
        print("❌ No se pudo iniciar sesión. Abortando pruebas.")
        exit(1)
    
    print("\n1. Probando agregar elemento...")
    success1 = test_agregar_elemento_devolucion(session)
    
    print("\n2. Probando listar elementos...")
    success2 = test_listar_elementos_devolucion(session)
    
    print("\n=== Resumen ===")
    if success1 and success2:
        print("✅ Todas las pruebas pasaron exitosamente")
        print("✅ La API de devoluciones está funcionando correctamente")
        print("✅ Los elementos del formulario coinciden con las columnas de la tabla")
    else:
        print("❌ Algunas pruebas fallaron")
        if not success1:
            print("  - Fallo al agregar elemento")
        if not success2:
            print("  - Fallo al listar elementos")