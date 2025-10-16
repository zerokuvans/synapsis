#!/usr/bin/env python3
"""
Script para probar las APIs del módulo MPA Vehículos
"""

import requests
import json
from datetime import datetime

# Configuración base
BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

def test_login():
    """Probar el login para obtener sesión"""
    print("🔐 Probando login...")
    
    login_data = {
        'username': '80833959',  # Usuario administrativo de ejemplo
        'password': 'admin123'   # Contraseña de ejemplo
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data)
    
    if response.status_code == 200:
        print("✅ Login exitoso")
        return True
    else:
        print(f"❌ Error en login: {response.status_code}")
        print(f"Respuesta: {response.text}")
        return False

def test_get_tecnicos():
    """Probar endpoint para obtener técnicos"""
    print("\n👥 Probando endpoint de técnicos...")
    
    response = session.get(f"{BASE_URL}/api/mpa/tecnicos")
    
    if response.status_code == 200:
        tecnicos = response.json()
        print(f"✅ Técnicos obtenidos: {len(tecnicos)} registros")
        if tecnicos:
            print(f"   Ejemplo: {tecnicos[0]['nombre']} (ID: {tecnicos[0]['id']})")
        return True
    else:
        print(f"❌ Error al obtener técnicos: {response.status_code}")
        print(f"Respuesta: {response.text}")
        return False

def test_get_vehiculos():
    """Probar endpoint para obtener vehículos"""
    print("\n🚗 Probando endpoint de vehículos...")
    
    response = session.get(f"{BASE_URL}/api/mpa/vehiculos")
    
    if response.status_code == 200:
        vehiculos = response.json()
        print(f"✅ Vehículos obtenidos: {len(vehiculos)} registros")
        return vehiculos
    else:
        print(f"❌ Error al obtener vehículos: {response.status_code}")
        print(f"Respuesta: {response.text}")
        return None

def test_create_vehiculo():
    """Probar creación de vehículo"""
    print("\n➕ Probando creación de vehículo...")
    
    vehiculo_data = {
        'cedula_propietario': '12345678',
        'nombre_propietario': 'Juan Pérez Test',
        'placa': 'TEST123',
        'tipo_vehiculo': 'Moto',
        'vin': 'VIN123456789TEST',
        'numero_de_motor': 'MOTOR123TEST',
        'fecha_de_matricula': '2024-01-15',
        'estado': 'Activo',
        'marca': 'Honda',
        'linea': 'CB150',
        'modelo': '2024',
        'color': 'Rojo',
        'kilometraje_actual': '1000',
        'tecnico_asignado': '1',  # ID del técnico
        'observaciones': 'Vehículo de prueba para testing'
    }
    
    response = session.post(f"{BASE_URL}/api/mpa/vehiculos", data=vehiculo_data)
    
    if response.status_code == 201:
        vehiculo = response.json()
        print(f"✅ Vehículo creado exitosamente: ID {vehiculo['id']}")
        return vehiculo['id']
    else:
        print(f"❌ Error al crear vehículo: {response.status_code}")
        print(f"Respuesta: {response.text}")
        return None

def test_get_vehiculo_detail(vehiculo_id):
    """Probar obtener detalle de vehículo"""
    print(f"\n🔍 Probando detalle de vehículo ID {vehiculo_id}...")
    
    response = session.get(f"{BASE_URL}/api/mpa/vehiculos/{vehiculo_id}")
    
    if response.status_code == 200:
        vehiculo = response.json()
        print(f"✅ Detalle obtenido: {vehiculo['placa']} - {vehiculo['marca']}")
        return True
    else:
        print(f"❌ Error al obtener detalle: {response.status_code}")
        return False

def test_update_vehiculo(vehiculo_id):
    """Probar actualización de vehículo"""
    print(f"\n✏️ Probando actualización de vehículo ID {vehiculo_id}...")
    
    update_data = {
        'kilometraje_actual': '2000',
        'observaciones': 'Vehículo actualizado en testing'
    }
    
    response = session.put(f"{BASE_URL}/api/mpa/vehiculos/{vehiculo_id}", data=update_data)
    
    if response.status_code == 200:
        print("✅ Vehículo actualizado exitosamente")
        return True
    else:
        print(f"❌ Error al actualizar vehículo: {response.status_code}")
        print(f"Respuesta: {response.text}")
        return False

def test_delete_vehiculo(vehiculo_id):
    """Probar eliminación de vehículo"""
    print(f"\n🗑️ Probando eliminación de vehículo ID {vehiculo_id}...")
    
    response = session.delete(f"{BASE_URL}/api/mpa/vehiculos/{vehiculo_id}")
    
    if response.status_code == 200:
        print("✅ Vehículo eliminado exitosamente")
        return True
    else:
        print(f"❌ Error al eliminar vehículo: {response.status_code}")
        print(f"Respuesta: {response.text}")
        return False

def main():
    """Función principal para ejecutar todas las pruebas"""
    print("🚀 Iniciando pruebas del módulo MPA Vehículos")
    print("=" * 50)
    
    # Probar login (comentado porque requiere credenciales válidas)
    # if not test_login():
    #     print("❌ No se pudo hacer login. Continuando sin autenticación...")
    
    # Probar endpoints
    test_get_tecnicos()
    vehiculos = test_get_vehiculos()
    
    # Probar CRUD completo
    vehiculo_id = test_create_vehiculo()
    if vehiculo_id:
        test_get_vehiculo_detail(vehiculo_id)
        test_update_vehiculo(vehiculo_id)
        test_delete_vehiculo(vehiculo_id)
    
    print("\n" + "=" * 50)
    print("🏁 Pruebas completadas")

if __name__ == "__main__":
    main()