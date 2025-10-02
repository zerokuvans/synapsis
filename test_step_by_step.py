#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import mysql.connector
from datetime import datetime
import pytz

# Configuración
BASE_URL = "http://localhost:8080"
LOGIN_DATA = {
    'username': '80833959',
    'password': 'M4r14l4r@'
}

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def verificar_db_estado(cedula):
    """Verificar el estado actual en la base de datos"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Obtener fecha actual
        bogota_tz = pytz.timezone('America/Bogota')
        fecha_actual = datetime.now(bogota_tz).date()
        
        cursor.execute("""
            SELECT id_asistencia, cedula, tecnico, fecha_asistencia, hora_inicio, estado, novedad
            FROM asistencia 
            WHERE cedula = %s AND DATE(fecha_asistencia) = %s
            ORDER BY fecha_asistencia DESC
            LIMIT 1
        """, (cedula, fecha_actual))
        
        registro = cursor.fetchone()
        
        if registro:
            print(f"📋 Estado en DB:")
            print(f"   ID: {registro['id_asistencia']}")
            print(f"   Hora inicio: {registro['hora_inicio']}")
            print(f"   Estado: {registro['estado']}")
            print(f"   Novedad: {registro['novedad']}")
        else:
            print("❌ No se encontró registro en DB")
            
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error verificando DB: {str(e)}")

def test_step_by_step():
    print("🧪 Prueba paso a paso de actualización de asistencia")
    print("=" * 60)
    
    # Crear sesión
    session = requests.Session()
    
    # 1. Login
    print("1️⃣ Realizando login...")
    response = session.post(f"{BASE_URL}/", data=LOGIN_DATA)
    if response.status_code == 200:
        print("✅ Login exitoso")
    else:
        print(f"❌ Error en login: {response.status_code}")
        return
    
    cedula_test = "1030545270"
    
    # 2. Verificar estado inicial en DB
    print("\n2️⃣ Estado inicial en base de datos:")
    verificar_db_estado(cedula_test)
    
    # 3. Obtener datos via API
    print("\n3️⃣ Obteniendo datos via API...")
    response = session.get(f"{BASE_URL}/api/asistencia/obtener-datos", params={'cedula': cedula_test})
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API Response:")
        print(f"   Hora inicio: {data.get('hora_inicio', 'No definida')}")
        print(f"   Estado: {data.get('estado', 'No definido')}")
        print(f"   Novedad: {data.get('novedad', 'No definida')}")
    else:
        print(f"❌ Error obteniendo datos: {response.status_code}")
    
    # 4. Actualizar hora_inicio
    print("\n4️⃣ Actualizando hora_inicio...")
    update_data = {
        'cedula': cedula_test,
        'campo': 'hora_inicio',
        'valor': '11:45'
    }
    headers = {'Content-Type': 'application/json'}
    response = session.post(f"{BASE_URL}/api/asistencia/actualizar-campo", json=update_data, headers=headers)
    print(f"📤 Response: {response.status_code}")
    if response.status_code == 200:
        print("✅ Actualización exitosa")
    else:
        print(f"❌ Error: {response.text}")
    
    # 5. Verificar en DB después de primera actualización
    print("\n5️⃣ Estado en DB después de actualizar hora_inicio:")
    verificar_db_estado(cedula_test)
    
    # 6. Verificar via API después de primera actualización
    print("\n6️⃣ Estado via API después de actualizar hora_inicio:")
    response = session.get(f"{BASE_URL}/api/asistencia/obtener-datos", params={'cedula': cedula_test})
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API Response:")
        print(f"   Hora inicio: {data.get('hora_inicio', 'No definida')}")
        print(f"   Estado: {data.get('estado', 'No definido')}")
        print(f"   Novedad: {data.get('novedad', 'No definida')}")
    
    # 7. Actualizar estado
    print("\n7️⃣ Actualizando estado...")
    update_data = {
        'cedula': cedula_test,
        'campo': 'estado',
        'valor': 'CUMPLE'
    }
    headers = {'Content-Type': 'application/json'}
    response = session.post(f"{BASE_URL}/api/asistencia/actualizar-campo", json=update_data, headers=headers)
    print(f"📤 Response: {response.status_code}")
    if response.status_code == 200:
        print("✅ Actualización exitosa")
    else:
        print(f"❌ Error: {response.text}")
    
    # 8. Verificar en DB después de segunda actualización
    print("\n8️⃣ Estado final en DB:")
    verificar_db_estado(cedula_test)
    
    # 9. Verificar via API final
    print("\n9️⃣ Estado final via API:")
    response = session.get(f"{BASE_URL}/api/asistencia/obtener-datos", params={'cedula': cedula_test})
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API Response:")
        print(f"   Hora inicio: {data.get('hora_inicio', 'No definida')}")
        print(f"   Estado: {data.get('estado', 'No definido')}")
        print(f"   Novedad: {data.get('novedad', 'No definida')}")

if __name__ == "__main__":
    test_step_by_step()