#!/usr/bin/env python3
"""
Script para probar la funcionalidad de edición de asistencia
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"
OBTENER_DATOS_URL = f"{BASE_URL}/api/asistencia/obtener-datos"
ACTUALIZAR_CAMPO_URL = f"{BASE_URL}/api/asistencia/actualizar-campo"

# Credenciales de prueba
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"
CEDULA_PRUEBA = "1030545270"

def login():
    """Realizar login y obtener session"""
    session = requests.Session()
    
    # Obtener la página de login para obtener el token CSRF si es necesario
    login_page = session.get(LOGIN_URL)
    
    # Datos de login
    login_data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    
    # Realizar login
    response = session.post(LOGIN_URL, data=login_data)
    
    if response.status_code == 200 and "dashboard" in response.url.lower():
        print("✅ Login exitoso")
        return session
    else:
        print(f"❌ Error en login: {response.status_code}")
        print(f"URL final: {response.url}")
        return None

def obtener_datos_existentes(session, cedula):
    """Obtener datos existentes de asistencia"""
    try:
        response = session.get(f"{OBTENER_DATOS_URL}?cedula={cedula}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Datos obtenidos exitosamente:")
            print(f"   - Hora inicio: {data.get('hora_inicio', 'No definida')}")
            print(f"   - Estado: {data.get('estado', 'No definido')}")
            print(f"   - Novedad: {data.get('novedad', 'No definida')}")
            return data
        else:
            print(f"❌ Error al obtener datos: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en obtener_datos_existentes: {e}")
        return None

def actualizar_campo(session, cedula, campo, valor):
    """Actualizar un campo específico"""
    try:
        data = {
            'cedula': cedula,
            'campo': campo,
            'valor': valor
        }
        
        response = session.post(ACTUALIZAR_CAMPO_URL, 
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Campo '{campo}' actualizado a '{valor}' exitosamente")
                return True
            else:
                print(f"❌ Error al actualizar campo: {result.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP al actualizar campo: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en actualizar_campo: {e}")
        return False

def main():
    print("🧪 Iniciando pruebas de edición de asistencia...")
    print("=" * 50)
    
    # 1. Login
    session = login()
    if not session:
        print("❌ No se pudo realizar login. Terminando pruebas.")
        return
    
    print()
    
    # 2. Obtener datos existentes
    print("📋 Obteniendo datos existentes...")
    datos_iniciales = obtener_datos_existentes(session, CEDULA_PRUEBA)
    
    print()
    
    # 3. Probar actualización de hora_inicio
    print("⏰ Probando actualización de hora_inicio...")
    nueva_hora = "09:30"
    if actualizar_campo(session, CEDULA_PRUEBA, "hora_inicio", nueva_hora):
        # Verificar que se actualizó
        datos_actualizados = obtener_datos_existentes(session, CEDULA_PRUEBA)
        if datos_actualizados and datos_actualizados.get('hora_inicio') == nueva_hora:
            print(f"✅ Verificación exitosa: hora_inicio = {nueva_hora}")
        else:
            print("❌ La verificación falló: el valor no se actualizó correctamente")
    
    print()
    
    # 4. Probar actualización de estado
    print("📊 Probando actualización de estado...")
    nuevo_estado = "NO CUMPLE"
    if actualizar_campo(session, CEDULA_PRUEBA, "estado", nuevo_estado):
        # Verificar que se actualizó
        datos_actualizados = obtener_datos_existentes(session, CEDULA_PRUEBA)
        if datos_actualizados and datos_actualizados.get('estado') == nuevo_estado:
            print(f"✅ Verificación exitosa: estado = {nuevo_estado}")
        else:
            print("❌ La verificación falló: el valor no se actualizó correctamente")
    
    print()
    
    # 5. Probar actualización de novedad
    print("📝 Probando actualización de novedad...")
    nueva_novedad = "Prueba de edición automática"
    if actualizar_campo(session, CEDULA_PRUEBA, "novedad", nueva_novedad):
        # Verificar que se actualizó
        datos_actualizados = obtener_datos_existentes(session, CEDULA_PRUEBA)
        if datos_actualizados and datos_actualizados.get('novedad') == nueva_novedad:
            print(f"✅ Verificación exitosa: novedad = {nueva_novedad}")
        else:
            print("❌ La verificación falló: el valor no se actualizó correctamente")
    
    print()
    
    # 6. Mostrar estado final
    print("📋 Estado final de los datos:")
    datos_finales = obtener_datos_existentes(session, CEDULA_PRUEBA)
    
    print()
    print("=" * 50)
    print("🎉 Pruebas de edición completadas")

if __name__ == "__main__":
    main()