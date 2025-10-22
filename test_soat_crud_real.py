#!/usr/bin/env python3
"""
Script para probar CRUD de SOAT con placas reales
"""

import requests
import json
import mysql.connector
from mysql.connector import Error

# Configuración
BASE_URL = "http://localhost:8080"
DB_CONFIG = {
    'host': 'localhost',
    'database': 'capired',
    'user': 'root',
    'password': '732137A031E4b@'
}

def get_available_vehicle():
    """Obtener un vehículo que no tenga SOAT activo"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Buscar vehículos sin SOAT activo
        query = """
        SELECT v.placa, v.tecnico_asignado, v.tipo_vehiculo
        FROM mpa_vehiculos v
        LEFT JOIN mpa_soat s ON v.placa = s.placa AND s.estado = 'Activo'
        WHERE v.estado = 'Activo' AND s.id_mpa_soat IS NULL
        LIMIT 1
        """
        
        cursor.execute(query)
        vehicle = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return vehicle
        
    except Error as e:
        print(f"Error obteniendo vehículo: {e}")
        return None

def test_soat_crud():
    """Probar operaciones CRUD de SOAT"""
    print("=== PROBANDO CRUD DE SOAT CON PLACA REAL ===")
    
    # 1. Obtener vehículo disponible
    vehicle = get_available_vehicle()
    if not vehicle:
        print("❌ No hay vehículos disponibles sin SOAT activo")
        return False
    
    print(f"✅ Vehículo encontrado: {vehicle['placa']} - {vehicle['tipo_vehiculo']}")
    
    # 2. Login
    session = requests.Session()
    login_data = {
        'username': '80833959',
        'password': 'M4r14l4r@'
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data)
    if response.status_code != 200 or 'login' in response.url:
        print("❌ Error en login")
        return False
    
    print("✅ Login exitoso")
    
    # 3. Crear SOAT
    print(f"\n--- Creando SOAT para {vehicle['placa']} ---")
    soat_data = {
        "placa": vehicle['placa'],
        "numero_poliza": "POL-TEST-001",
        "aseguradora": "Aseguradora Test",
        "fecha_inicio": "2024-01-01",
        "fecha_vencimiento": "2024-12-31",
        "valor_prima": 150000,
        "estado": "Activo",
        "observaciones": "SOAT de prueba para diagnóstico"
    }
    
    response = session.post(
        f"{BASE_URL}/api/mpa/soat",
        json=soat_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    
    try:
        result = response.json()
        print(f"Respuesta: {json.dumps(result, indent=2, default=str)}")
        
        if response.status_code == 200 and result.get('success'):
            print("✅ SOAT creado exitosamente")
            created_id = result.get('data', {}).get('id_mpa_soat')
            
            # 4. Actualizar SOAT
            if created_id:
                print(f"\n--- Actualizando SOAT ID: {created_id} ---")
                update_data = {
                    "valor_prima": 200000,
                    "observaciones": "SOAT actualizado - diagnóstico completado",
                    "aseguradora": "Aseguradora Actualizada"
                }
                
                update_response = session.put(
                    f"{BASE_URL}/api/mpa/soat/{created_id}",
                    json=update_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"Status: {update_response.status_code}")
                
                try:
                    update_result = update_response.json()
                    print(f"Respuesta: {json.dumps(update_result, indent=2, default=str)}")
                    
                    if update_response.status_code == 200 and update_result.get('success'):
                        print("✅ SOAT actualizado exitosamente")
                        
                        # 5. Verificar actualización
                        print(f"\n--- Verificando actualización ---")
                        get_response = session.get(f"{BASE_URL}/api/mpa/soat")
                        if get_response.status_code == 200:
                            data = get_response.json()
                            updated_soat = None
                            for soat in data.get('data', []):
                                if soat.get('id_mpa_soat') == created_id:
                                    updated_soat = soat
                                    break
                            
                            if updated_soat:
                                print("✅ Verificación exitosa:")
                                print(f"  - Valor prima: {updated_soat.get('valor_prima')}")
                                print(f"  - Aseguradora: {updated_soat.get('aseguradora')}")
                                print(f"  - Observaciones: {updated_soat.get('observaciones')}")
                            else:
                                print("❌ No se encontró el SOAT actualizado")
                        
                        # 6. Limpiar (eliminar registro de prueba)
                        print(f"\n--- Eliminando SOAT de prueba ---")
                        delete_response = session.delete(f"{BASE_URL}/api/mpa/soat/{created_id}")
                        if delete_response.status_code == 200:
                            delete_result = delete_response.json()
                            if delete_result.get('success'):
                                print("✅ SOAT de prueba eliminado exitosamente")
                            else:
                                print(f"⚠️ Error eliminando: {delete_result.get('error')}")
                        else:
                            print(f"⚠️ Error en DELETE: {delete_response.status_code}")
                    else:
                        print("❌ Error actualizando SOAT")
                        print(f"Error: {update_result.get('error', 'Error desconocido')}")
                        
                except json.JSONDecodeError:
                    print("❌ Respuesta de actualización no es JSON válido")
                    print(f"Contenido: {update_response.text[:500]}")
            else:
                print("❌ No se obtuvo ID del SOAT creado")
        else:
            print("❌ Error creando SOAT")
            print(f"Error: {result.get('error', 'Error desconocido')}")
            
    except json.JSONDecodeError:
        print("❌ Respuesta de creación no es JSON válido")
        print(f"Contenido: {response.text[:500]}")
    
    return True

def main():
    """Función principal"""
    print("PRUEBA COMPLETA DE CRUD SOAT")
    print("=" * 50)
    
    test_soat_crud()
    
    print("\n" + "=" * 50)
    print("PRUEBA COMPLETADA")

if __name__ == "__main__":
    main()