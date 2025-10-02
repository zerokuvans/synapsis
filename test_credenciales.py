#!/usr/bin/env python3
"""
Test para verificar el flujo completo de guardar y consultar asistencia
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8080"
LOGIN_URL = f"{BASE_URL}/"
FECHA_HOY = datetime.now().strftime('%Y-%m-%d')

# Credenciales de prueba
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def login():
    """Realizar login y obtener session"""
    session = requests.Session()
    
    print("1. Obteniendo página de login...")
    login_page = session.get(LOGIN_URL)
    print(f"   Status: {login_page.status_code}")
    
    # Datos de login
    login_data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    
    print("2. Realizando login...")
    response = session.post(LOGIN_URL, data=login_data)
    print(f"   Status: {response.status_code}")
    print(f"   URL final: {response.url}")
    
    if response.status_code == 200:
        print("✅ Login exitoso")
        return session
    else:
        print(f"❌ Error en login")
        return None

def test_guardar_asistencia(session, supervisor, tecnico_data):
    """Test para guardar datos de asistencia"""
    print(f"\n🔄 Guardando asistencia para {tecnico_data['tecnico']}...")
    
    # Datos de asistencia a guardar
    asistencia_data = {
        'supervisor': supervisor,
        'fecha': FECHA_HOY,
        'registros': [
            {
                'id_codigo_consumidor': tecnico_data['id_codigo_consumidor'],
                'cedula': tecnico_data['cedula'],
                'tecnico': tecnico_data['tecnico'],
                'carpeta': tecnico_data['carpeta'],
                'carpeta_dia': 'INST',  # Código de ejemplo
                'hora_inicio': '08:30',
                'estado': 'Presente',
                'novedad': 'Prueba de guardado automático'
            }
        ]
    }
    
    try:
        response = session.post(
            f"{BASE_URL}/api/asistencia/guardar",
            json=asistencia_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Asistencia guardada exitosamente")
                return True
            else:
                print(f"   ❌ Error al guardar: {data.get('message')}")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return False

def test_consultar_asistencia(session, supervisor, fecha):
    """Test del endpoint de consulta de asistencia"""
    print(f"\n🔍 Consultando asistencia para {supervisor} en fecha {fecha}...")
    
    try:
        response = session.get(
            f"{BASE_URL}/api/asistencia/consultar",
            params={
                "supervisor": supervisor,
                "fecha": fecha
            }
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                registros = data.get('registros', [])
                registros_con_datos = [r for r in registros if r.get('id_asistencia') is not None]
                
                print(f"   Total registros: {len(registros)}")
                print(f"   Registros con datos: {len(registros_con_datos)}")
                
                if len(registros_con_datos) > 0:
                    print(f"   🎯 ¡DATOS ENCONTRADOS!")
                    
                    # Mostrar los registros con datos
                    for i, registro in enumerate(registros_con_datos):
                        print(f"   Registro {i+1} con datos:")
                        print(f"     - ID: {registro.get('id_asistencia')}")
                        print(f"     - Cédula: {registro.get('cedula')}")
                        print(f"     - Técnico: {registro.get('tecnico')}")
                        print(f"     - Hora Inicio: {registro.get('hora_inicio')}")
                        print(f"     - Estado: {registro.get('estado')}")
                        print(f"     - Novedad: {registro.get('novedad')}")
                        print(f"     - Carpeta Día: {registro.get('carpeta_dia')}")
                    
                    return registros_con_datos
                else:
                    print(f"   Sin datos guardados para esta fecha")
                    return []
            else:
                print(f"   ❌ Error: {data.get('message')}")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return []

def test_supervisores(session):
    """Test del endpoint de supervisores"""
    print("\n3. Obteniendo lista de supervisores...")
    
    try:
        response = session.get(f"{BASE_URL}/api/supervisores")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                supervisores = data.get('supervisores', [])
                print(f"   Total supervisores: {len(supervisores)}")
                return supervisores
            else:
                print(f"❌ Error: {data.get('message')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return []

if __name__ == "__main__":
    print("=== TEST COMPLETO: GUARDAR Y CONSULTAR ASISTENCIA ===")
    print(f"Fecha de prueba: {FECHA_HOY}")
    
    # Realizar login
    session = login()
    
    if session:
        # Obtener supervisores
        supervisores = test_supervisores(session)
        
        if supervisores:
            # Usar el primer supervisor para la prueba
            supervisor_prueba = supervisores[0]
            print(f"\n🎯 Usando supervisor para prueba: {supervisor_prueba}")
            
            # Primero consultar técnicos disponibles
            registros_actuales = test_consultar_asistencia(session, supervisor_prueba, FECHA_HOY)
            
            if len(registros_actuales) == 0:
                print(f"\n📝 No hay datos guardados. Consultando técnicos disponibles...")
                
                # Obtener lista de técnicos para este supervisor
                try:
                    response = session.get(f"{BASE_URL}/api/tecnicos_por_supervisor?supervisor={supervisor_prueba}")
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success') and len(data.get('tecnicos', [])) > 0:
                            primer_tecnico = data['tecnicos'][0]
                            print(f"   Primer técnico disponible: {primer_tecnico['nombre']}")
                            
                            # Preparar datos del técnico para guardar
                            tecnico_data = {
                                'id_codigo_consumidor': primer_tecnico['id_codigo_consumidor'],
                                'cedula': primer_tecnico['cedula'],
                                'tecnico': primer_tecnico['nombre'],
                                'carpeta': primer_tecnico['carpeta']
                            }
                            
                            # Guardar asistencia
                            if test_guardar_asistencia(session, supervisor_prueba, tecnico_data):
                                print(f"\n🔄 Consultando nuevamente después de guardar...")
                                registros_despues = test_consultar_asistencia(session, supervisor_prueba, FECHA_HOY)
                                
                                if len(registros_despues) > 0:
                                    print(f"\n✅ ¡ÉXITO COMPLETO!")
                                    print(f"   - Datos guardados correctamente")
                                    print(f"   - Datos consultados correctamente")
                                    print(f"   - El flujo completo funciona")
                                else:
                                    print(f"\n❌ Los datos se guardaron pero no se pueden consultar")
                            else:
                                print(f"\n❌ Error al guardar datos")
                        else:
                            print(f"   ❌ No se encontraron técnicos para este supervisor")
                    else:
                        print(f"   ❌ Error al obtener técnicos")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            else:
                print(f"\n✅ Ya hay datos guardados para hoy:")
                print(f"   - Supervisor: {supervisor_prueba}")
                print(f"   - Fecha: {FECHA_HOY}")
                print(f"   - Registros: {len(registros_actuales)}")
        else:
            print("\n❌ No se pudieron obtener supervisores")
    else:
        print("\n❌ No se pudo realizar login")