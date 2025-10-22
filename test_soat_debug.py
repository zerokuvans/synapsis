#!/usr/bin/env python3
"""
Script para debuggear problemas específicos del módulo SOAT
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

def test_database_connection():
    """Probar conexión a la base de datos"""
    print("=== PROBANDO CONEXIÓN A BASE DE DATOS ===")
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("✅ Conexión a base de datos exitosa")
            
            cursor = connection.cursor(dictionary=True)
            
            # Verificar tabla mpa_soat
            print("\n--- Verificando tabla mpa_soat ---")
            cursor.execute("SHOW TABLES LIKE 'mpa_soat'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                print("✅ Tabla mpa_soat existe")
                
                # Verificar estructura
                cursor.execute("DESCRIBE mpa_soat")
                columns = cursor.fetchall()
                print("Columnas de la tabla:")
                for col in columns:
                    print(f"  - {col['Field']} ({col['Type']}) {'NOT NULL' if col['Null'] == 'NO' else 'NULL'}")
                
                # Verificar registros
                cursor.execute("SELECT COUNT(*) as total FROM mpa_soat")
                count = cursor.fetchone()
                print(f"Total de registros: {count['total']}")
                
                # Verificar algunos registros
                if count['total'] > 0:
                    cursor.execute("SELECT * FROM mpa_soat LIMIT 3")
                    registros = cursor.fetchall()
                    print("Primeros registros:")
                    for i, reg in enumerate(registros, 1):
                        print(f"  {i}. ID: {reg.get('id_mpa_soat')}, Placa: {reg.get('placa')}, Estado: {reg.get('estado')}")
            else:
                print("❌ Tabla mpa_soat NO existe")
                
            # Verificar tabla mpa_vehiculos
            print("\n--- Verificando tabla mpa_vehiculos ---")
            cursor.execute("SHOW TABLES LIKE 'mpa_vehiculos'")
            vehiculos_exists = cursor.fetchone()
            
            if vehiculos_exists:
                print("✅ Tabla mpa_vehiculos existe")
                cursor.execute("SELECT COUNT(*) as total FROM mpa_vehiculos WHERE estado = 'Activo'")
                count_vehiculos = cursor.fetchone()
                print(f"Vehículos activos: {count_vehiculos['total']}")
                
                if count_vehiculos['total'] > 0:
                    cursor.execute("SELECT placa, tecnico_asignado FROM mpa_vehiculos WHERE estado = 'Activo' LIMIT 3")
                    vehiculos = cursor.fetchall()
                    print("Vehículos de ejemplo:")
                    for v in vehiculos:
                        print(f"  - Placa: {v['placa']}, Técnico: {v['tecnico_asignado']}")
            else:
                print("❌ Tabla mpa_vehiculos NO existe")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_soat_endpoints():
    """Probar endpoints de SOAT con autenticación"""
    print("\n=== PROBANDO ENDPOINTS DE SOAT ===")
    
    session = requests.Session()
    
    # Credenciales de prueba (usuario administrativo)
    test_credentials = [
        ("80833959", "M4r14l4r@"),  # Usuario administrativo conocido
        ("admin", "admin"),
        ("1002407101", "CE1002407101")
    ]
    
    login_success = False
    
    for username, password in test_credentials:
        print(f"\n--- Probando login con: {username} ---")
        try:
            login_data = {
                'username': username,
                'password': password
            }
            response = session.post(f"{BASE_URL}/login", data=login_data)
            
            if response.status_code == 200 and 'login' not in response.url:
                print(f"✅ Login exitoso con {username}")
                login_success = True
                break
            else:
                print(f"❌ Login falló con {username}")
        except Exception as e:
            print(f"❌ Error en login: {e}")
    
    if not login_success:
        print("❌ No se pudo hacer login con ninguna credencial")
        return False
    
    # Probar GET /api/mpa/soat
    print("\n--- Probando GET /api/mpa/soat ---")
    try:
        response = session.get(f"{BASE_URL}/api/mpa/soat")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ GET exitoso: {len(data.get('data', []))} registros")
                if data.get('data'):
                    print("Primer registro:")
                    print(json.dumps(data['data'][0], indent=2, default=str))
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
                print(f"Contenido: {response.text[:500]}")
        else:
            print(f"❌ Error en GET: {response.status_code}")
            print(f"Contenido: {response.text[:500]}")
    except Exception as e:
        print(f"❌ Error en GET: {e}")
    
    # Probar POST /api/mpa/soat (crear)
    print("\n--- Probando POST /api/mpa/soat (crear) ---")
    try:
        # Datos de prueba para crear SOAT
        test_soat_data = {
            "placa": "TEST123",
            "numero_poliza": "POL-TEST-001",
            "aseguradora": "Aseguradora Test",
            "fecha_inicio": "2024-01-01",
            "fecha_vencimiento": "2024-12-31",
            "valor_prima": 150000,
            "estado": "Activo",
            "observaciones": "SOAT de prueba"
        }
        
        response = session.post(
            f"{BASE_URL}/api/mpa/soat",
            json=test_soat_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        try:
            result = response.json()
            print(f"Respuesta: {json.dumps(result, indent=2, default=str)}")
            
            if response.status_code == 200 and result.get('success'):
                print("✅ POST exitoso")
                created_id = result.get('data', {}).get('id_mpa_soat')
                
                # Probar PUT (actualizar)
                if created_id:
                    print(f"\n--- Probando PUT /api/mpa/soat/{created_id} (actualizar) ---")
                    update_data = {
                        "valor_prima": 200000,
                        "observaciones": "SOAT actualizado en prueba"
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
                            print("✅ PUT exitoso")
                        else:
                            print("❌ Error en PUT")
                    except json.JSONDecodeError:
                        print("❌ Respuesta PUT no es JSON válido")
                        print(f"Contenido: {update_response.text[:500]}")
                    
                    # Limpiar: eliminar registro de prueba
                    print(f"\n--- Limpiando: DELETE /api/mpa/soat/{created_id} ---")
                    delete_response = session.delete(f"{BASE_URL}/api/mpa/soat/{created_id}")
                    if delete_response.status_code == 200:
                        print("✅ Registro de prueba eliminado")
                    else:
                        print("⚠️ No se pudo eliminar el registro de prueba")
            else:
                print("❌ Error en POST")
        except json.JSONDecodeError:
            print("❌ Respuesta POST no es JSON válido")
            print(f"Contenido: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error en POST: {e}")
    
    return True

def main():
    """Función principal"""
    print("DIAGNÓSTICO COMPLETO DEL MÓDULO SOAT")
    print("=" * 50)
    
    # 1. Probar base de datos
    db_ok = test_database_connection()
    
    # 2. Probar endpoints
    if db_ok:
        test_soat_endpoints()
    else:
        print("\n❌ No se pueden probar endpoints sin conexión a BD")
    
    print("\n" + "=" * 50)
    print("DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    main()