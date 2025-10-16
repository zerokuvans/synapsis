#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la API con login previo
"""

import requests
import json

def test_api_con_login():
    """Probar la API con login previo"""
    print("🔐 PROBANDO API CON LOGIN - USUARIO 80833959")
    print("="*60)
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # URLs
    login_url = "http://192.168.80.15:8080/login"
    api_url = "http://192.168.80.15:8080/obtener_usuario/1"
    
    try:
        # 1. Hacer login
        print("1️⃣ HACIENDO LOGIN...")
        
        # Datos de login (usando las credenciales que sabemos que existen)
        login_data = {
            'username': '80833959',  # El endpoint espera 'username', no 'cedula'
            'password': 'M4r14l4r@'  # Contraseña correcta proporcionada por el usuario
        }
        
        login_response = session.post(login_url, data=login_data)
        print(f"📊 Login Status Code: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login exitoso")
        else:
            print(f"❌ Login falló: {login_response.status_code}")
            print(f"📄 Contenido: {login_response.text[:200]}")
            
            print("❌ Login falló con la contraseña proporcionada")
            return
        
        # 2. Probar la API
        print(f"\n2️⃣ PROBANDO API OBTENER_USUARIO...")
        print(f"📡 Haciendo petición GET a: {api_url}")
        
        api_response = session.get(api_url)
        print(f"📊 API Status Code: {api_response.status_code}")
        print(f"📋 API Headers: {dict(api_response.headers)}")
        
        if api_response.status_code == 200:
            print("✅ API respuesta exitosa")
            
            # Verificar si es JSON
            content_type = api_response.headers.get('content-type', '')
            if 'application/json' in content_type:
                try:
                    data = api_response.json()
                    print("📤 RESPUESTA JSON:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    
                    # Verificar específicamente las fechas
                    print(f"\n📅 ANÁLISIS DE FECHAS:")
                    print(f"   fecha_ingreso: '{data.get('fecha_ingreso')}' (tipo: {type(data.get('fecha_ingreso'))})")
                    print(f"   fecha_retiro: '{data.get('fecha_retiro')}' (tipo: {type(data.get('fecha_retiro'))})")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Error parseando JSON: {e}")
                    print(f"📄 Contenido: {api_response.text[:500]}")
            else:
                print(f"⚠️  Respuesta no es JSON (Content-Type: {content_type})")
                print(f"📄 Contenido: {api_response.text[:500]}")
        else:
            print(f"❌ Error en API: {api_response.status_code}")
            print(f"📄 Contenido: {api_response.text[:500]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    
    print(f"\n🏁 PRUEBA COMPLETADA")
    print("="*60)

if __name__ == "__main__":
    test_api_con_login()