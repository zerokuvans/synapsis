#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la nueva lógica de cálculo de Presupuesto Mes
"""

import requests
import json
from datetime import datetime

def test_presupuesto_mes():
    """Probar el nuevo cálculo de Presupuesto Mes"""
    
    # URL del endpoint
    base_url = "http://localhost:8080"
    login_url = f"{base_url}/api/login"
    datos_url = f"{base_url}/api/lider/inicio-operacion/datos"
    
    # Credenciales
    credentials = {
        'username': '80833959',
        'password': 'M4r14l4r@'
    }
    
    print("=" * 60)
    print("PROBANDO NUEVA LÓGICA DE PRESUPUESTO MES")
    print("=" * 60)
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        # 1. Login
        print("🔐 Iniciando sesión...")
        login_response = session.post(login_url, json=credentials)
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            if login_data.get('success'):
                print("✅ Login exitoso")
            else:
                print(f"❌ Error en login: {login_data.get('message', 'Error desconocido')}")
                return
        else:
            print(f"❌ Error HTTP en login: {login_response.status_code}")
            return
        
        # 2. Probar con fecha actual
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        params = {'fecha': fecha_actual}
        
        print(f"\n📊 Consultando datos para fecha: {fecha_actual}")
        response = session.get(datos_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                metricas = data['data']['metricas']
                
                print("✅ Consulta exitosa")
                print(f"\n📈 MÉTRICAS OBTENIDAS:")
                print(f"   Presupuesto día: ${metricas.get('presupuesto_dia', 0):,}")
                print(f"   Presupuesto mes: ${metricas.get('presupuesto_mes', 0):,}")
                
                # Verificar que el presupuesto mes no sea simplemente presupuesto_dia * 26
                presupuesto_dia = metricas.get('presupuesto_dia', 0)
                presupuesto_mes = metricas.get('presupuesto_mes', 0)
                presupuesto_mes_anterior = presupuesto_dia * 26
                
                print(f"\n🔍 VERIFICACIÓN:")
                print(f"   Presupuesto día: ${presupuesto_dia:,}")
                print(f"   Presupuesto mes (nuevo): ${presupuesto_mes:,}")
                print(f"   Presupuesto mes (anterior): ${presupuesto_mes_anterior:,}")
                
                if presupuesto_mes != presupuesto_mes_anterior:
                    print("✅ La nueva lógica está funcionando - el presupuesto mes NO es día * 26")
                else:
                    print("⚠️  El presupuesto mes sigue siendo día * 26 - verificar implementación")
                
                # Mostrar información adicional
                cumplimiento = data['data']['cumplimiento']
                print(f"\n📊 CUMPLIMIENTO:")
                print(f"   Día: {cumplimiento.get('cumplimiento_dia', 0):.1f}%")
                print(f"   Mes: {cumplimiento.get('cumplimiento_mes', 0):.1f}%")
                
            else:
                print(f"❌ Error en respuesta: {data.get('message', 'Error desconocido')}")
        
        elif response.status_code == 403:
            print("❌ Error 403: Permisos insuficientes")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Respuesta: {response.text}")
    
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")

if __name__ == "__main__":
    test_presupuesto_mes()