#!/usr/bin/env python3
"""
Script para probar la nueva lógica de Presupuesto Mes en el módulo de Operaciones
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"
API_URL = f"{BASE_URL}/api/operativo/inicio-operacion/asistencia"

def login():
    """Iniciar sesión con credenciales administrativas"""
    session = requests.Session()
    
    # Datos de login (usando credenciales administrativas que sabemos que funcionan)
    login_data = {
        'username': '80833959',  # Cédula del usuario administrativo
        'password': 'M4r14l4r@'  # Password del usuario
    }
    
    # Realizar login
    response = session.post(LOGIN_URL, data=login_data)
    
    if response.status_code == 200 and ('dashboard' in response.text.lower() or 'administrativo' in response.text.lower()):
        print(f"✅ Login exitoso como administrador")
        return session
    else:
        print(f"❌ Error en login: {response.status_code}")
        print(f"URL de respuesta: {response.url}")
        return None

def test_presupuesto_operativo():
    """Probar la nueva lógica de presupuesto mensual en operativo"""
    print("🔍 Probando nueva lógica de Presupuesto Mes en Operaciones...")
    
    # Iniciar sesión
    session = login()
    if not session:
        return
    
    # Primero, necesitamos acceder al módulo de operativo para establecer la sesión correcta
    # Intentar acceder a la página de operativo
    operativo_url = f"{BASE_URL}/operativo/indicadores/operaciones/inicio-operacion"
    response = session.get(operativo_url)
    
    if response.status_code != 200:
        print(f"❌ No se pudo acceder al módulo de operativo: {response.status_code}")
        print("Nota: Es posible que el usuario administrativo no tenga acceso al módulo operativo")
        return
    
    # Obtener fecha actual
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    
    # Hacer petición a la API
    params = {
        'fecha': fecha_actual,
        '_t': int(datetime.now().timestamp())
    }
    
    response = session.get(API_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('success'):
            stats = data.get('stats', {})
            
            print(f"\n📊 Resultados para {fecha_actual}:")
            print(f"👤 Supervisor: {data.get('supervisor', 'N/A')}")
            print(f"📈 Presupuesto Día: ${stats.get('presupuesto_dia', 0):,.2f}")
            print(f"📅 Presupuesto Mes: ${stats.get('presupuesto_mes', 0):,.2f}")
            
            # Verificar si la nueva lógica está funcionando
            presupuesto_dia = stats.get('presupuesto_dia', 0)
            presupuesto_mes = stats.get('presupuesto_mes', 0)
            presupuesto_mes_viejo = presupuesto_dia * 26
            
            print(f"\n🔍 Verificación de la nueva lógica:")
            print(f"Presupuesto Mes (nuevo): ${presupuesto_mes:,.2f}")
            print(f"Presupuesto Mes (viejo = día * 26): ${presupuesto_mes_viejo:,.2f}")
            
            if presupuesto_mes != presupuesto_mes_viejo:
                print("✅ La nueva lógica está funcionando - Presupuesto mes NO es día * 26")
            else:
                print("⚠️  La nueva lógica podría no estar funcionando o no hay datos del primer día")
            
            # Mostrar otros datos relevantes
            print(f"\n📋 Otros datos:")
            print(f"Total técnicos: {stats.get('total_tecnicos', 0)}")
            print(f"Con asistencia: {stats.get('con_asistencia', 0)}")
            print(f"Sin asistencia: {stats.get('sin_asistencia', 0)}")
            print(f"OK's Día: {stats.get('oks_dia', 0)}")
            
        else:
            print(f"❌ Error en la respuesta de la API: {data.get('message', 'Error desconocido')}")
    else:
        print(f"❌ Error HTTP: {response.status_code}")
        if response.status_code == 403:
            print("Nota: El usuario no tiene permisos para acceder al módulo operativo")
        print(f"Respuesta: {response.text[:500]}")

if __name__ == "__main__":
    test_presupuesto_operativo()