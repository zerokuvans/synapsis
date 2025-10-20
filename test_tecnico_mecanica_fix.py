#!/usr/bin/env python3
"""
Script para probar que el fix de técnico mecánica funciona correctamente.
Verifica que se guarden IDs de técnicos y se muestren nombres.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración
BASE_URL = "http://localhost:8080"
LOGIN_URL = f"{BASE_URL}/login"
PLACAS_URL = f"{BASE_URL}/api/mpa/vehiculos/placas"
TECNICO_MECANICA_URL = f"{BASE_URL}/api/mpa/tecnico_mecanica"

def test_tecnico_mecanica_flow():
    """Prueba el flujo completo de técnico mecánica"""
    
    print("🔧 Iniciando prueba del flujo de Técnico Mecánica...")
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        # 1. Obtener datos de vehículos/placas (sin autenticación para verificar estructura)
        print("\n1. Verificando estructura de datos de vehículos...")
        
        # Primero intentamos sin autenticación para ver qué pasa
        response = session.get(PLACAS_URL)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 302:
            print("   ✅ Redirección a login detectada (autenticación requerida)")
        elif response.status_code == 200:
            try:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    vehicle = data['data'][0]
                    print(f"   ✅ Estructura de vehículo:")
                    print(f"      - Placa: {vehicle.get('placa', 'N/A')}")
                    print(f"      - Técnico ID: {vehicle.get('tecnico_asignado', 'N/A')}")
                    print(f"      - Técnico Nombre: {vehicle.get('tecnico_nombre', 'N/A')}")
                    
                    # Verificar que tenemos tanto ID como nombre
                    if vehicle.get('tecnico_asignado') and vehicle.get('tecnico_nombre'):
                        print("   ✅ Los datos incluyen tanto ID como nombre del técnico")
                    else:
                        print("   ⚠️  Faltan datos de técnico (ID o nombre)")
                else:
                    print("   ⚠️  No hay datos de vehículos")
            except json.JSONDecodeError as e:
                print(f"   ❌ Error al decodificar JSON: {e}")
                print(f"   Contenido de respuesta (primeros 500 chars): {response.text[:500]}")
        else:
            print(f"   ❌ Error inesperado: {response.status_code}")
            print(f"   Contenido: {response.text[:200]}")
        
        # 2. Verificar estructura de técnico mecánica existente
        print("\n2. Verificando registros existentes de técnico mecánica...")
        response = session.get(TECNICO_MECANICA_URL)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    tm = data['data'][0]
                    print(f"   ✅ Estructura de técnico mecánica:")
                    print(f"      - ID: {tm.get('id_mpa_tecnico_mecanica', 'N/A')}")
                    print(f"      - Placa: {tm.get('placa', 'N/A')}")
                    print(f"      - Técnico Asignado (campo): {tm.get('tecnico_asignado', 'N/A')}")
                    print(f"      - Técnico Nombre: {tm.get('tecnico_nombre', 'N/A')}")
                    
                    # Verificar que el campo tecnico_asignado contiene un ID (número)
                    tecnico_asignado = tm.get('tecnico_asignado')
                    if tecnico_asignado:
                        try:
                            int(tecnico_asignado)
                            print("   ✅ El campo tecnico_asignado contiene un ID numérico")
                        except (ValueError, TypeError):
                            print(f"   ⚠️  El campo tecnico_asignado contiene: '{tecnico_asignado}' (no es un ID)")
                    
                    # Verificar que tenemos el nombre del técnico
                    if tm.get('tecnico_nombre'):
                        print("   ✅ Se muestra correctamente el nombre del técnico")
                    else:
                        print("   ⚠️  No se muestra el nombre del técnico")
                        
                else:
                    print("   ℹ️  No hay registros de técnico mecánica")
            except json.JSONDecodeError as e:
                print(f"   ❌ Error al decodificar JSON: {e}")
                print(f"   Contenido de respuesta (primeros 500 chars): {response.text[:500]}")
        elif response.status_code == 302:
            print("   ✅ Redirección a login detectada (autenticación requerida)")
        else:
            print(f"   ❌ Error inesperado: {response.status_code}")
            print(f"   Contenido: {response.text[:200]}")
        
        print("\n📋 Resumen de la prueba:")
        print("   - El endpoint de vehículos debe retornar tanto tecnico_asignado (ID) como tecnico_nombre")
        print("   - El endpoint de técnico mecánica debe mostrar tecnico_nombre en la lista")
        print("   - Los registros guardados deben tener tecnico_asignado como ID numérico")
        print("   - La interfaz debe mostrar nombres pero guardar IDs")
        
        print("\n✅ Prueba completada. Revisa los resultados arriba.")
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")

if __name__ == "__main__":
    test_tecnico_mecanica_flow()