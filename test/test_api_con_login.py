#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la API con login previo
"""

import requests
import json
import time

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
    try:
        session = requests.Session()
        base_url = "http://localhost:8080"
        login_data = {'username': 'admin', 'password': 'admin'}
        session.post(f"{base_url}/login", data=login_data)
        fecha = time.strftime('%Y-%m-%d')
        url_ind = f"{base_url}/api/indicadores/cumplimiento?fecha={fecha}"
        t0 = time.perf_counter(); r1 = session.get(url_ind); t1 = time.perf_counter()
        t2 = time.perf_counter(); r2 = session.get(url_ind); t3 = time.perf_counter()
        print("\nMEDICIÓN INDICADORES")
        print(f"Primera carga: {round((t1-t0)*1000)} ms, Status {r1.status_code}")
        print(f"Carga con cache: {round((t3-t2)*1000)} ms, Status {r2.status_code}")
        sup = None
        try:
            d = r1.json()
            arr = d.get('indicadores') or []
            if arr:
                sup = arr[0].get('supervisor')
        except Exception:
            sup = None
        if sup:
            url_det = f"{base_url}/api/indicadores/detalle_tecnicos?fecha={fecha}&supervisor={sup}"
            s0 = time.perf_counter(); k1 = session.get(url_det); s1 = time.perf_counter()
            s2 = time.perf_counter(); k2 = session.get(url_det); s3 = time.perf_counter()
            print("\nMEDICIÓN DETALLE TÉCNICOS")
            print(f"Primera carga: {round((s1-s0)*1000)} ms, Status {k1.status_code}")
            print(f"Carga con cache: {round((s3-s2)*1000)} ms, Status {k2.status_code}")
    except Exception as e:
        print(f"\n❌ Error en medición de rendimiento: {e}")
