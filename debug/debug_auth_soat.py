#!/usr/bin/env python3
"""
Script para debuggear problemas de autenticación en el módulo SOAT
"""

import requests
import json

def test_auth_and_soat():
    """Probar autenticación y acceso al módulo SOAT"""
    
    base_url = "http://localhost:8080"
    session = requests.Session()
    
    print("=== DEBUG AUTENTICACIÓN Y SOAT ===")
    print()
    
    # 1. Verificar página principal
    print("1. 🏠 Verificando página principal...")
    try:
        response = session.get(base_url)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Servidor funcionando")
        else:
            print("   ❌ Problema con el servidor")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Verificar ruta del módulo SOAT (sin autenticación)
    print("\n2. 🚗 Verificando ruta /mpa/soat sin autenticación...")
    try:
        response = session.get(f"{base_url}/mpa/soat")
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Redirige a login (comportamiento esperado)")
        elif response.status_code == 200:
            print("   ⚠️ Acceso permitido sin autenticación")
        else:
            print(f"   ❌ Respuesta inesperada: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Verificar API SOAT sin autenticación
    print("\n3. 🔌 Verificando API /api/mpa/soat sin autenticación...")
    try:
        response = session.get(f"{base_url}/api/mpa/soat")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'No especificado')}")
        
        if response.status_code == 302:
            print("   ✅ Redirige a login (comportamiento esperado)")
        elif response.status_code == 401:
            print("   ✅ No autorizado (comportamiento esperado)")
        elif response.status_code == 403:
            print("   ✅ Sin permisos (comportamiento esperado)")
        elif response.status_code == 200:
            print("   ⚠️ Acceso permitido sin autenticación")
            try:
                data = response.json()
                print(f"   Datos: {data}")
            except:
                print(f"   Contenido: {response.text[:200]}...")
        else:
            print(f"   ❌ Respuesta inesperada: {response.status_code}")
            print(f"   Contenido: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Intentar login con credenciales de prueba
    print("\n4. 🔐 Intentando login con credenciales de prueba...")
    test_credentials = [
        ("admin", "admin"),
        ("80833959", "M4r14l4r@"),
        ("1234567890", "password123")
    ]
    
    for username, password in test_credentials:
        print(f"   Probando: {username}")
        try:
            login_data = {
                'username': username,
                'password': password
            }
            response = session.post(f"{base_url}/login", data=login_data)
            print(f"     Status: {response.status_code}")
            
            if response.status_code == 200 and 'login' not in response.url:
                print("     ✅ Login exitoso")
                
                # Probar API SOAT con autenticación
                print("     🔌 Probando API SOAT autenticado...")
                api_response = session.get(f"{base_url}/api/mpa/soat")
                print(f"     API Status: {api_response.status_code}")
                
                if api_response.status_code == 200:
                    try:
                        data = api_response.json()
                        print(f"     ✅ API funcionando: {len(data.get('data', []))} registros")
                    except:
                        print("     ❌ Respuesta no es JSON válido")
                elif api_response.status_code == 403:
                    print("     ❌ Usuario sin permisos administrativos")
                else:
                    print(f"     ❌ Error en API: {api_response.status_code}")
                
                break
            else:
                print("     ❌ Login falló")
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    print("\n=== FIN DEBUG ===")

if __name__ == "__main__":
    test_auth_and_soat()