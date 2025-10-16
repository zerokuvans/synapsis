#!/usr/bin/env python3
"""
Script para probar que los nombres de técnicos se muestren correctamente
en la tabla de vehículos después de corregir el JOIN
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_technician_display():
    """Prueba que los nombres de técnicos se muestren en la tabla"""
    
    # Crear una sesión para mantener las cookies
    session = requests.Session()
    
    print("🔧 Probando visualización de técnicos asignados...")
    print("=" * 60)
    
    try:
        # 1. Obtener la lista de vehículos
        print("1. Obteniendo lista de vehículos...")
        response = session.get(f"{BASE_URL}/api/mpa/vehiculos")
        
        if response.status_code == 200:
            vehicles_data = response.json()
            if vehicles_data.get('success'):
                vehicles = vehicles_data.get('data', [])
                print(f"   ✅ {len(vehicles)} vehículos encontrados")
                
                # Verificar cada vehículo
                vehicles_with_technician = 0
                vehicles_without_technician = 0
                
                for vehicle in vehicles:
                    placa = vehicle.get('placa', 'N/A')
                    tecnico_asignado = vehicle.get('tecnico_asignado')
                    tecnico_nombre = vehicle.get('tecnico_nombre')
                    
                    print(f"\n   📋 Vehículo: {placa}")
                    print(f"      - ID Técnico asignado: {tecnico_asignado}")
                    print(f"      - Nombre técnico: {tecnico_nombre}")
                    
                    if tecnico_asignado and tecnico_asignado != 'undefined':
                        if tecnico_nombre:
                            print(f"      ✅ CORRECTO: Técnico '{tecnico_nombre}' asignado")
                            vehicles_with_technician += 1
                        else:
                            print(f"      ❌ ERROR: ID técnico presente pero nombre faltante")
                            print(f"      ❌ Esto causará que se muestre 'Sin asignar'")
                    else:
                        print(f"      ⚪ Sin técnico asignado (normal)")
                        vehicles_without_technician += 1
                
                print(f"\n📊 Resumen:")
                print(f"   - Vehículos con técnico asignado: {vehicles_with_technician}")
                print(f"   - Vehículos sin técnico asignado: {vehicles_without_technician}")
                
                if vehicles_with_technician > 0:
                    print(f"\n✅ ¡ÉXITO! Los nombres de técnicos se están devolviendo correctamente")
                    print(f"✅ La tabla debería mostrar los nombres en lugar de 'Sin asignar'")
                else:
                    print(f"\n⚠️  No hay vehículos con técnicos asignados para probar")
                    
            else:
                print("   ❌ Error en la respuesta de la API")
                print(f"   ❌ Mensaje: {vehicles_data.get('error', 'Error desconocido')}")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   ❌ Detalle: {error_data}")
            except:
                print(f"   ❌ Respuesta: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. ¿Está ejecutándose en el puerto 8080?")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 Prueba completada")

if __name__ == "__main__":
    test_technician_display()