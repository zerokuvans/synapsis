#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la API con sesión autenticada
"""

import requests
import json

def test_api_with_session():
    """Probar la API con una sesión autenticada"""
    
    # Crear una sesión
    session = requests.Session()
    
    # URL base
    base_url = "http://192.168.80.15:8080"
    
    print("🔐 INICIANDO SESIÓN...")
    print("="*50)
    
    # 1. Hacer login
    login_data = {
        'username': '80833959',  # Cédula del usuario que sabemos que existe
        'password': 'admin'      # Asumiendo que la contraseña es admin
    }
    
    try:
        # Intentar hacer login
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        print(f"Status del login: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login exitoso")
            
            # 2. Probar la API de obtener usuario
            print(f"\n🔍 PROBANDO API /obtener_usuario/1")
            print("="*50)
            
            api_response = session.get(f"{base_url}/obtener_usuario/1")
            
            print(f"Status de la API: {api_response.status_code}")
            
            if api_response.status_code == 200:
                try:
                    data = api_response.json()
                    print("✅ Respuesta JSON recibida:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    
                    # Verificar específicamente las fechas
                    print(f"\n📅 ANÁLISIS DE FECHAS:")
                    print(f"   fecha_ingreso: '{data.get('fecha_ingreso', 'NO ENCONTRADA')}' (tipo: {type(data.get('fecha_ingreso'))})")
                    print(f"   fecha_retiro: '{data.get('fecha_retiro', 'NO ENCONTRADA')}' (tipo: {type(data.get('fecha_retiro'))})")
                    
                    if data.get('fecha_ingreso'):
                        print(f"✅ fecha_ingreso tiene valor: {data['fecha_ingreso']}")
                    else:
                        print(f"❌ fecha_ingreso está vacía o es null")
                        
                    if data.get('fecha_retiro'):
                        print(f"✅ fecha_retiro tiene valor: {data['fecha_retiro']}")
                    else:
                        print(f"ℹ️  fecha_retiro está vacía o es null (esto puede ser normal)")
                    
                except json.JSONDecodeError:
                    print("❌ La respuesta no es JSON válido")
                    print("Contenido de la respuesta:")
                    print(api_response.text[:500])
            else:
                print(f"❌ Error en la API: {api_response.status_code}")
                print("Contenido de la respuesta:")
                print(api_response.text[:500])
        else:
            print(f"❌ Error en el login: {login_response.status_code}")
            print("Contenido de la respuesta:")
            print(login_response.text[:500])
            
            # Intentar con diferentes credenciales
            print(f"\n🔄 INTENTANDO CON CREDENCIALES ALTERNATIVAS...")
            
            # Probar con admin/admin
            login_data_alt = {
                'username': 'admin',
                'password': 'admin'
            }
            
            login_response_alt = session.post(f"{base_url}/login", data=login_data_alt)
            print(f"Status del login alternativo: {login_response_alt.status_code}")
            
            if login_response_alt.status_code == 200:
                print("✅ Login alternativo exitoso")
                
                # Probar la API nuevamente
                api_response = session.get(f"{base_url}/obtener_usuario/1")
                print(f"Status de la API: {api_response.status_code}")
                
                if api_response.status_code == 200:
                    try:
                        data = api_response.json()
                        print("✅ Respuesta JSON recibida:")
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                    except json.JSONDecodeError:
                        print("❌ La respuesta no es JSON válido")
                        print(api_response.text[:500])
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    
    print(f"\n🏁 PRUEBA COMPLETADA")

if __name__ == "__main__":
    test_api_with_session()