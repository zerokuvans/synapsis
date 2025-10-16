#!/usr/bin/env python3
"""
Script para probar que el campo 'Técnico asignado' se guarde correctamente
después de la corrección del bug tech.id -> tech.cedula
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8080"

def test_technician_assignment():
    """Prueba la asignación de técnicos en vehículos"""
    
    # Crear una sesión para mantener las cookies
    session = requests.Session()
    
    print("🔧 Probando corrección del bug 'Técnico asignado'...")
    print("=" * 60)
    
    try:
        # 1. Primero obtener la lista de técnicos disponibles
        print("1. Obteniendo lista de técnicos...")
        response = session.get(f"{BASE_URL}/api/mpa/tecnicos")
        
        if response.status_code == 200:
            tecnicos_data = response.json()
            if tecnicos_data.get('success') and tecnicos_data.get('data'):
                tecnicos = tecnicos_data['data']
                print(f"   ✅ {len(tecnicos)} técnicos encontrados")
                
                # Mostrar algunos técnicos disponibles
                for i, tech in enumerate(tecnicos[:3]):
                    print(f"   - {tech['nombre']} (Cédula: {tech['cedula']})")
                
                # Seleccionar el primer técnico para la prueba
                if tecnicos:
                    tecnico_test = tecnicos[0]
                    print(f"\n2. Usando técnico de prueba: {tecnico_test['nombre']} (Cédula: {tecnico_test['cedula']})")
                    
                    # 3. Crear un vehículo de prueba con técnico asignado
                    print("\n3. Creando vehículo de prueba con técnico asignado...")
                    
                    vehicle_data = {
                        "cedula_propietario": "12345678",
                        "nombre_propietario": "Propietario Test",
                        "placa": f"TEST{datetime.now().strftime('%H%M%S')}",  # Placa única
                        "tipo_vehiculo": "Automóvil",
                        "marca": "Toyota",
                        "modelo": "2023",
                        "color": "Blanco",
                        "estado": "Activo",
                        "tecnico_asignado": tecnico_test['cedula'],  # Aquí está la clave del test
                        "observaciones": "Vehículo de prueba para validar técnico asignado"
                    }
                    
                    response = session.post(
                        f"{BASE_URL}/api/mpa/vehiculos",
                        json=vehicle_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            vehicle_id = result.get('id')
                            print(f"   ✅ Vehículo creado exitosamente (ID: {vehicle_id})")
                            
                            # 4. Verificar que el técnico se guardó correctamente
                            print("\n4. Verificando que el técnico se guardó correctamente...")
                            
                            # Obtener la lista de vehículos para verificar
                            response = session.get(f"{BASE_URL}/api/mpa/vehiculos")
                            if response.status_code == 200:
                                vehicles_data = response.json()
                                if vehicles_data.get('success'):
                                    vehicles = vehicles_data.get('data', [])
                                    
                                    # Buscar nuestro vehículo de prueba
                                    test_vehicle = None
                                    for vehicle in vehicles:
                                        if vehicle.get('id_mpa_vehiculos') == vehicle_id:
                                            test_vehicle = vehicle
                                            break
                                    
                                    if test_vehicle:
                                        saved_tecnico = test_vehicle.get('tecnico_asignado')
                                        print(f"   📋 Técnico asignado guardado: '{saved_tecnico}'")
                                        print(f"   📋 Técnico esperado: '{tecnico_test['cedula']}'")
                                        
                                        if saved_tecnico == tecnico_test['cedula']:
                                            print("   ✅ ¡ÉXITO! El técnico se guardó correctamente")
                                            print("   ✅ Bug corregido: ya no se guarda como 'undefined'")
                                        elif saved_tecnico == 'undefined' or saved_tecnico is None:
                                            print("   ❌ ERROR: El técnico aún se guarda como 'undefined' o NULL")
                                            print("   ❌ El bug NO ha sido corregido")
                                        else:
                                            print(f"   ⚠️  ADVERTENCIA: Valor inesperado: '{saved_tecnico}'")
                                    else:
                                        print("   ❌ No se pudo encontrar el vehículo creado")
                                else:
                                    print("   ❌ Error al obtener lista de vehículos")
                            else:
                                print(f"   ❌ Error al verificar vehículos: {response.status_code}")
                        else:
                            print(f"   ❌ Error al crear vehículo: {result.get('error', 'Error desconocido')}")
                    else:
                        print(f"   ❌ Error HTTP al crear vehículo: {response.status_code}")
                        try:
                            error_data = response.json()
                            print(f"   ❌ Detalle: {error_data}")
                        except:
                            print(f"   ❌ Respuesta: {response.text}")
                else:
                    print("   ❌ No hay técnicos disponibles para la prueba")
            else:
                print("   ❌ No se pudieron obtener técnicos")
        else:
            print(f"   ❌ Error al obtener técnicos: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. ¿Está ejecutándose en el puerto 8080?")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 Prueba completada")

if __name__ == "__main__":
    test_technician_assignment()