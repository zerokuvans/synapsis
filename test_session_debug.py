#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar los datos de sesión del usuario
"""

import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"

# Credenciales
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def test_session_data():
    """Verificar los datos de sesión del usuario"""
    print("=" * 60)
    print("VERIFICACIÓN DE DATOS DE SESIÓN")
    print("=" * 60)
    
    session = requests.Session()
    
    # 1. Login
    print("\n[1] Realizando login...")
    try:
        login_data = {
            "username": USERNAME,
            "password": PASSWORD
        }
        
        login_response = session.post(LOGIN_URL, data=login_data)
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("   ❌ Login fallido")
            return False
            
        print("   ✅ Login exitoso")
        
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False
    
    # 2. Verificar datos de sesión accediendo a una página que muestre info del usuario
    print("\n[2] Verificando datos de sesión...")
    try:
        # Intentar acceder a la página de inicio de operación
        page_response = session.get(f"{BASE_URL}/operativo/indicadores/operaciones/inicio")
        print(f"   Status página: {page_response.status_code}")
        
        if page_response.status_code == 200:
            # Buscar información del usuario en la página
            content = page_response.text
            
            # Buscar patrones comunes de información de usuario
            if "supervisor" in content.lower():
                print("   ✅ Página cargada correctamente")
                print("   📄 Contenido contiene referencias a supervisor")
            else:
                print("   ⚠️ Página cargada pero no se encontraron referencias a supervisor")
                
        else:
            print(f"   ❌ Error al cargar página: {page_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error al verificar sesión: {e}")
    
    # 3. Intentar acceder a un endpoint que devuelva información del usuario
    print("\n[3] Intentando obtener información del usuario...")
    try:
        # Probar diferentes endpoints que podrían devolver info del usuario
        endpoints_test = [
            "/api/operativo/inicio-operacion/asistencia",  # Sin parámetros
            "/api/user/info",  # Posible endpoint de info de usuario
            "/api/session/info",  # Posible endpoint de sesión
        ]
        
        for endpoint in endpoints_test:
            try:
                response = session.get(f"{BASE_URL}{endpoint}")
                print(f"   Endpoint {endpoint}: Status {response.status_code}")
                
                if response.status_code == 200 and 'application/json' in response.headers.get('content-type', ''):
                    data = response.json()
                    print(f"      Respuesta JSON: {json.dumps(data, indent=2)[:200]}...")
                    
            except Exception as e:
                print(f"   Error en {endpoint}: {e}")
                
    except Exception as e:
        print(f"   ❌ Error general: {e}")