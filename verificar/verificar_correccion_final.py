#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar que la corrección del formato de fechas está funcionando
para el usuario 80833959 (cédula 80833959)
"""

import requests
import json
from datetime import datetime

def verificar_correccion():
    """Verificar que la API devuelve fechas en formato YYYY-MM-DD"""
    
    print("🔍 VERIFICACIÓN FINAL - CORRECCIÓN DE FECHAS")
    print("=" * 60)
    
    # Configuración
    base_url = "http://192.168.80.15:8080"
    login_url = f"{base_url}/login"
    api_url = f"{base_url}/obtener_usuario/1"  # Usuario con cédula 80833959
    
    # Datos de login
    login_data = {
        'username': '80833959',
        'password': 'M4r14l4r@'
    }
    
    session = requests.Session()
    
    try:
        # 1. Login
        print("1️⃣ Haciendo login...")
        login_response = session.post(login_url, data=login_data)
        
        if login_response.status_code == 200:
            print("   ✅ Login exitoso")
        else:
            print(f"   ❌ Login falló: {login_response.status_code}")
            return
        
        # 2. Probar API
        print("\n2️⃣ Probando API obtener_usuario...")
        api_response = session.get(api_url)
        
        if api_response.status_code == 200:
            print("   ✅ API respuesta exitosa")
            
            # 3. Analizar respuesta
            data = api_response.json()
            print(f"\n3️⃣ DATOS DEL USUARIO:")
            print(f"   📋 Cédula: {data.get('recurso_operativo_cedula')}")
            print(f"   👤 Nombre: {data.get('nombre')}")
            print(f"   📅 Fecha Ingreso: '{data.get('fecha_ingreso')}' (tipo: {type(data.get('fecha_ingreso'))})")
            print(f"   📅 Fecha Retiro: '{data.get('fecha_retiro')}' (tipo: {type(data.get('fecha_retiro'))})")
            
            # 4. Verificar formato de fecha
            fecha_ingreso = data.get('fecha_ingreso')
            if fecha_ingreso:
                print(f"\n4️⃣ VERIFICACIÓN DE FORMATO:")
                print(f"   📅 Fecha recibida: '{fecha_ingreso}'")
                
                # Verificar que es string
                if isinstance(fecha_ingreso, str):
                    print("   ✅ Es string (correcto)")
                    
                    # Verificar formato YYYY-MM-DD
                    try:
                        parsed_date = datetime.strptime(fecha_ingreso, '%Y-%m-%d')
                        print(f"   ✅ Formato YYYY-MM-DD válido")
                        print(f"   📅 Fecha parseada: {parsed_date.date()}")
                        
                        # Verificar que es compatible con input type="date"
                        print(f"   ✅ Compatible con input type='date'")
                        
                        print(f"\n🎉 CORRECCIÓN EXITOSA!")
                        print(f"   La fecha ahora se devuelve en formato '{fecha_ingreso}' en lugar del formato GMT anterior")
                        
                    except ValueError as e:
                        print(f"   ❌ Formato inválido: {e}")
                else:
                    print(f"   ❌ No es string: {type(fecha_ingreso)}")
            else:
                print("   ⚠️ No hay fecha_ingreso")
                
        else:
            print(f"   ❌ API falló: {api_response.status_code}")
            print(f"   📄 Respuesta: {api_response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    verificar_correccion()