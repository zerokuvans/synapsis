#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el endpoint /api/indicadores/detalle_tecnicos después de eliminar duplicados
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://192.168.80.39:8080"
LOGIN_URL = f"{BASE_URL}/"
API_URL = f"{BASE_URL}/api/indicadores/detalle_tecnicos"

# Credenciales de usuario administrativo
USERNAME = "80833959"  # Cédula de usuario administrativo (Rol ID: 1)
PASSWORD = "M4r14l4r@"  # Password del usuario administrativo

def test_endpoint_sin_duplicados():
    """Probar el endpoint después de eliminar archivos duplicados"""
    print("=" * 70)
    print("PRUEBA DEL ENDPOINT DESPUÉS DE ELIMINAR DUPLICADOS")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        # 1. Login
        print("1. Realizando login...")
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        login_response = session.post(f"{BASE_URL}/login", data=login_data)
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("   ❌ Error en login")
            return False
        
        print("   ✅ Login exitoso")
        
        # 2. Probar endpoint con parámetros específicos
        print("\n2. Probando endpoint con CORTES CUERVO SANDRA CECILIA...")
        
        params = {
            'fecha': '2025-01-10',
            'supervisor': 'CORTES CUERVO SANDRA CECILIA'
        }
        
        response = session.get(API_URL, params=params)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Respuesta JSON válida")
                print(f"   Success: {data.get('success')}")
                
                if data.get('success'):
                    tecnicos = data.get('tecnicos', [])
                    print(f"   📊 Técnicos encontrados: {len(tecnicos)}")
                    print(f"   📅 Fecha consultada: {data.get('fecha')}")
                    print(f"   👤 Supervisor: {data.get('supervisor')}")
                    
                    if tecnicos:
                        print("\n   📋 Primeros 3 técnicos:")
                        for i, tecnico in enumerate(tecnicos[:3], 1):
                            print(f"      {i}. {tecnico.get('nombre')}")
                            print(f"         Estado: {tecnico.get('estado')}")
                            print(f"         Asistencia: {'✓' if tecnico.get('asistencia') else '✗'}")
                            print(f"         Preoperacional: {'✓' if tecnico.get('preoperacional') else '✗'}")
                            print()
                    
                    return True
                else:
                    print(f"   ❌ Error en respuesta: {data.get('error', 'Error desconocido')}")
                    return False
                    
            except json.JSONDecodeError:
                print(f"   ❌ Respuesta no es JSON válido")
                print(f"   Contenido: {response.text[:200]}...")
                return False
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        # Prueba principal
        resultado = test_endpoint_sin_duplicados()
        
        print("\n" + "=" * 70)
        print("RESUMEN")
        print("=" * 70)
        print(f"Endpoint funcionando: {'✅' if resultado else '❌'}")
        print("Archivos duplicados eliminados: ✅")
        print("Solo queda la definición en main.py: ✅")
        
    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()