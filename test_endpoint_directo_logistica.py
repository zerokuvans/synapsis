#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el endpoint /api/vehiculos/vencimientos con usuario logística
"""

import requests
import json
import re
from datetime import datetime

def test_endpoint_vencimientos():
    """Probar el endpoint con autenticación"""
    print("=== PRUEBA DEL ENDPOINT /api/vehiculos/vencimientos ===")
    print(f"Fecha: {datetime.now()}")
    
    BASE_URL = 'http://127.0.0.1:8080'
    session = requests.Session()
    
    # Usuarios logística disponibles
    usuarios = [
        {'username': 'test123', 'password': '123456'},
        {'username': '1002407101', 'password': '123456'},  # Probar con contraseña común
    ]
    
    for i, usuario in enumerate(usuarios, 1):
        print(f"\n{i}. Probando con usuario: {usuario['username']}")
        
        try:
            # Obtener página principal para extraer CSRF token
            print("   Obteniendo página de login...")
            response = session.get(BASE_URL)
            
            if response.status_code != 200:
                print(f"   ❌ Error obteniendo página: {response.status_code}")
                continue
            
            # Buscar token CSRF en diferentes formatos
            csrf_patterns = [
                r'name="csrf_token"\s+value="([^"]+)"',
                r'<input[^>]*name=["\']csrf_token["\'][^>]*value=["\']([^"\'>]+)["\']',
                r'csrf_token["\']\s*:\s*["\']([^"\'>]+)["\']'
            ]
            
            csrf_token = None
            for pattern in csrf_patterns:
                match = re.search(pattern, response.text)
                if match:
                    csrf_token = match.group(1)
                    break
            
            if not csrf_token:
                print("   ❌ No se encontró token CSRF")
                print(f"   Contenido de respuesta (primeros 500 chars): {response.text[:500]}")
                continue
            
            print(f"   ✅ Token CSRF obtenido: {csrf_token[:20]}...")
            
            # Intentar login
            login_data = {
                'username': usuario['username'],
                'password': usuario['password'],
                'csrf_token': csrf_token
            }
            
            print("   Intentando login...")
            login_response = session.post(BASE_URL, data=login_data, allow_redirects=False)
            
            print(f"   Status login: {login_response.status_code}")
            print(f"   Headers: {dict(login_response.headers)}")
            
            # Verificar si el login fue exitoso
            login_exitoso = False
            
            if login_response.status_code == 302:
                location = login_response.headers.get('Location', '')
                print(f"   Redirección a: {location}")
                if 'dashboard' in location.lower():
                    print("   ✅ Login exitoso - Redirigido al dashboard")
                    login_exitoso = True
                else:
                    print("   ❌ Login fallido - Redirigido a login")
            elif login_response.status_code == 200:
                # Verificar contenido de respuesta
                if 'dashboard' in login_response.text.lower():
                    print("   ✅ Login exitoso - Contenido dashboard")
                    login_exitoso = True
                else:
                    print("   ❌ Login fallido - Aún en página de login")
            
            if login_exitoso:
                # Probar endpoint de vencimientos
                print("\n   === PROBANDO ENDPOINT VENCIMIENTOS ===")
                vencimientos_url = f"{BASE_URL}/api/vehiculos/vencimientos"
                
                # Probar con diferentes parámetros
                params_tests = [
                    {},  # Sin parámetros
                    {'dias': 30},  # 30 días
                    {'dias': 90, 'tipo': 'all'},  # 90 días, todos los tipos
                ]
                
                for j, params in enumerate(params_tests, 1):
                    print(f"\n   Prueba {j} - Parámetros: {params}")
                    
                    api_response = session.get(vencimientos_url, params=params)
                    print(f"   Status: {api_response.status_code}")
                    print(f"   Content-Type: {api_response.headers.get('Content-Type')}")
                    
                    if api_response.status_code == 200:
                        content_type = api_response.headers.get('Content-Type', '')
                        
                        if 'application/json' in content_type:
                            try:
                                data = api_response.json()
                                print("   ✅ Respuesta JSON válida")
                                print(f"   Success: {data.get('success')}")
                                print(f"   Total: {data.get('total', 0)}")
                                
                                if data.get('data') and len(data['data']) > 0:
                                    print(f"   Registros encontrados: {len(data['data'])}")
                                    print("   Primeros 3 registros:")
                                    for k, item in enumerate(data['data'][:3]):
                                        print(f"     {k+1}. Placa: {item.get('placa')}, Tipo: {item.get('tipo_documento')}, Días: {item.get('dias_restantes')}")
                                else:
                                    print("   ⚠️  No hay datos de vencimientos")
                                    
                                # Mostrar estructura completa del primer registro
                                if data.get('data'):
                                    print("\n   Estructura del primer registro:")
                                    first_record = data['data'][0]
                                    for key, value in first_record.items():
                                        print(f"     {key}: {value}")
                                        
                                return True  # Éxito, no necesitamos probar más usuarios
                                
                            except json.JSONDecodeError as e:
                                print(f"   ❌ Error decodificando JSON: {e}")
                                print(f"   Contenido: {api_response.text[:200]}...")
                        else:
                            print(f"   ❌ Respuesta no es JSON: {content_type}")
                            print(f"   Contenido: {api_response.text[:200]}...")
                    else:
                        print(f"   ❌ Error en endpoint: {api_response.status_code}")
                        print(f"   Contenido: {api_response.text[:200]}...")
                
                return True  # Login exitoso, no probar más usuarios
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n❌ No se pudo autenticar con ningún usuario")
    return False

if __name__ == "__main__":
    test_endpoint_vencimientos()