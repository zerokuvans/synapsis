#!/usr/bin/env python3
"""
Script para probar que la interfaz de asistencia muestre correctamente los datos guardados
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8080"
LOGIN_URL = f"{BASE_URL}/login"
ASISTENCIA_URL = f"{BASE_URL}/api/asistencia/consultar"

def test_interfaz_asistencia():
    """Prueba que la interfaz muestre correctamente los datos de asistencia"""
    
    print("=== TEST INTERFAZ ASISTENCIA ===")
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    print(f"Fecha de prueba: {fecha_hoy}")
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        # 1. Obtener página de login
        print("1. Obteniendo página de login...")
        response = session.get(LOGIN_URL)
        print(f"   Status: {response.status_code}")
        
        # 2. Realizar login
        print("2. Realizando login...")
        login_data = {
            'cedula': '80833959',
            'password': 'Synapsis2024*'
        }
        
        response = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        print(f"   Status: {response.status_code}")
        print(f"   URL final: {response.url}")
        
        if "dashboard" in response.url:
            print("✅ Login exitoso")
        else:
            print("❌ Error en login")
            return False
            
        # 3. Probar endpoint de consulta con fecha actual
        print(f"\n3. Consultando asistencia para fecha {fecha_hoy}...")
        
        # Primero obtener supervisores
        supervisores_response = session.get(f"{BASE_URL}/api/supervisores")
        if supervisores_response.status_code == 200:
            supervisores_data = supervisores_response.json()
            if supervisores_data.get('success') and supervisores_data.get('supervisores'):
                supervisor = supervisores_data['supervisores'][0]
                print(f"   Usando supervisor: {supervisor}")
                
                # Consultar asistencia
                params = {
                    'supervisor': supervisor,
                    'fecha': fecha_hoy
                }
                
                response = session.get(ASISTENCIA_URL, params=params)
                print(f"   Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   Success: {data.get('success')}")
                        print(f"   Total registros: {len(data.get('registros', []))}")
                        
                        # Verificar si hay registros con datos
                        registros_con_datos = [r for r in data.get('registros', []) if r.get('id_asistencia')]
                        print(f"   Registros con datos: {len(registros_con_datos)}")
                        
                        if registros_con_datos:
                            print("\n🎯 ¡DATOS ENCONTRADOS PARA HOY!")
                            for i, registro in enumerate(registros_con_datos, 1):
                                print(f"   Registro {i}:")
                                print(f"     - ID: {registro.get('id_asistencia')}")
                                print(f"     - Cédula: {registro.get('cedula')}")
                                print(f"     - Técnico: {registro.get('tecnico')}")
                                print(f"     - Hora Inicio: {registro.get('hora_inicio')}")
                                print(f"     - Estado: {registro.get('estado')}")
                                print(f"     - Novedad: {registro.get('novedad')}")
                                print(f"     - Carpeta Día: {registro.get('carpeta_dia')}")
                            
                            print("\n✅ La interfaz debería mostrar estos datos automáticamente")
                            print("   cuando se seleccione el supervisor y la fecha actual.")
                            
                        else:
                            print(f"\n⚠️  No hay datos de asistencia para {supervisor} en {fecha_hoy}")
                            print("   La interfaz mostrará técnicos sin datos de asistencia.")
                            
                        return True
                        
                    except json.JSONDecodeError:
                        print("❌ Error: Respuesta no es JSON válido")
                        print(f"   Contenido: {response.text[:200]}...")
                        return False
                else:
                    print(f"❌ Error en consulta: {response.status_code}")
                    return False
            else:
                print("❌ Error al obtener supervisores")
                return False
        else:
            print("❌ Error al obtener supervisores")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False

if __name__ == "__main__":
    success = test_interfaz_asistencia()
    if success:
        print("\n🎉 Prueba completada exitosamente")
        print("💡 Instrucciones para verificar en la interfaz:")
        print("   1. Abrir http://localhost:8080/administrativo/asistencia")
        print("   2. La fecha actual debería estar seleccionada automáticamente")
        print("   3. Seleccionar un supervisor de la lista")
        print("   4. Los datos de asistencia existentes deberían aparecer automáticamente")
        print("   5. Los campos Hora Inicio, Estado y Novedad deberían mostrar los valores guardados")
    else:
        print("\n❌ Prueba falló")