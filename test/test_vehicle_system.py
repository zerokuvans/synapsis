#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el sistema de gestión de vehículos
Verifica que las tablas, triggers y funcionalidades estén funcionando correctamente
"""

import mysql.connector
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def get_db_connection():
    """Establece conexión con la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def test_tables_exist():
    """Verifica que todas las tablas necesarias existan"""
    print("\n🔍 Verificando existencia de tablas...")
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        required_tables = [
            'parque_automotor',
            'historial_vencimientos', 
            'alertas_vencimiento',
            'kilometraje_vehiculos'
        ]
        
        for table in required_tables:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            result = cursor.fetchone()
            if result:
                print(f"  ✓ Tabla {table} existe")
            else:
                print(f"  ❌ Tabla {table} NO existe")
                return False
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"Error verificando tablas: {e}")
        return False

def test_triggers_exist():
    """Verifica que los triggers estén creados"""
    print("\n🔍 Verificando triggers...")
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE 
            FROM information_schema.TRIGGERS 
            WHERE TRIGGER_SCHEMA = %s
            AND TRIGGER_NAME LIKE 'tr_%'
        """, (DB_CONFIG['database'],))
        
        triggers = cursor.fetchall()
        
        expected_triggers = [
        'tr_parque_automotor_historial_insert_v2',
        'tr_parque_automotor_historial_update_v2'
    ]
        
        found_triggers = [t['TRIGGER_NAME'] for t in triggers]
        
        for trigger in expected_triggers:
            if trigger in found_triggers:
                print(f"  ✓ Trigger {trigger} existe")
            else:
                print(f"  ❌ Trigger {trigger} NO existe")
        
        print(f"\n📊 Total triggers encontrados: {len(triggers)}")
        
        cursor.close()
        connection.close()
        return len([t for t in expected_triggers if t in found_triggers]) >= 2
        
    except Exception as e:
        print(f"Error verificando triggers: {e}")
        return False

def test_vehicle_insertion():
    """Prueba insertar un vehículo y verificar que los triggers funcionen"""
    print("\n🚗 Probando inserción de vehículo...")
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Datos de prueba
        test_vehicle = {
            'placa': 'TEST123',
            'tipo_vehiculo': 'Automóvil',
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'color': 'Blanco',
            'supervisor': 'Técnico Test',
            'fecha_asignacion': datetime.now(),
            'estado': 'Activo',
            'soat_vencimiento': (datetime.now() + timedelta(days=15)).date(),
            'tecnomecanica_vencimiento': (datetime.now() + timedelta(days=25)).date(),
            'observaciones': 'Vehículo de prueba'
        }
        
        # Verificar si ya existe el vehículo de prueba
        cursor.execute("SELECT id_parque_automotor FROM parque_automotor WHERE placa = %s", (test_vehicle['placa'],))
        existing = cursor.fetchone()
        
        if existing:
            print(f"  ⚠ Vehículo de prueba ya existe (ID: {existing[0]}), eliminando...")
            cursor.execute("DELETE FROM parque_automotor WHERE id_parque_automotor = %s", (existing[0],))
        
        # Insertar vehículo de prueba
        insert_query = """
            INSERT INTO parque_automotor 
            (placa, tipo_vehiculo, marca, modelo, color, supervisor, 
             fecha_asignacion, estado, soat_vencimiento, tecnomecanica_vencimiento, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            test_vehicle['placa'], test_vehicle['tipo_vehiculo'], test_vehicle['marca'],
            test_vehicle['modelo'], test_vehicle['color'], test_vehicle['supervisor'],
            test_vehicle['fecha_asignacion'], test_vehicle['estado'],
            test_vehicle['soat_vencimiento'], test_vehicle['tecnomecanica_vencimiento'],
            test_vehicle['observaciones']
        ))
        
        vehicle_id = cursor.lastrowid
        print(f"  ✓ Vehículo insertado con ID: {vehicle_id}")
        
        # Verificar que se crearon registros en historial_vencimientos
        cursor.execute("""
            SELECT COUNT(*) FROM historial_vencimientos 
            WHERE id_vehiculo = %s
        """, (vehicle_id,))
        
        historial_count = cursor.fetchone()[0]
        print(f"  📝 Registros en historial_vencimientos: {historial_count}")
        
        # Verificar alertas generadas (a través de historial_vencimientos)
        cursor.execute("""
            SELECT COUNT(*) FROM alertas_vencimiento av
            INNER JOIN historial_vencimientos hv ON av.id_historial = hv.id_historial
            WHERE hv.id_vehiculo = %s
        """, (vehicle_id,))
        
        alertas_count = cursor.fetchone()[0]
        print(f"  🚨 Alertas activas generadas: {alertas_count}")
        
        connection.commit()
        
        # Limpiar datos de prueba
        cursor.execute("DELETE FROM parque_automotor WHERE id_parque_automotor = %s", (vehicle_id,))
        connection.commit()
        print(f"  🧹 Datos de prueba eliminados")
        
        cursor.close()
        connection.close()
        
        return historial_count > 0 and alertas_count > 0
        
    except Exception as e:
        print(f"Error en prueba de inserción: {e}")
        return False

def test_api_structure():
    """Verifica que las rutas API estén definidas en main.py"""
    print("\n🌐 Verificando estructura de API...")
    
    try:
        with open('main.py', 'r', encoding='utf-8') as file:
            content = file.read()
        
        api_routes = [
            '/api/vehiculos',
            '/api/vehiculos/<int:vehiculo_id>',
            '/api/vehiculos/dashboard',
            '/api/vehiculos/importar',
            '/api/vehiculos/alertas',
            '/api/vehiculos/reportes'
        ]
        
        found_routes = 0
        for route in api_routes:
            if route.replace('<int:vehiculo_id>', '') in content:
                print(f"  ✓ Ruta {route} encontrada")
                found_routes += 1
            else:
                print(f"  ❌ Ruta {route} NO encontrada")
        
        print(f"\n📊 Rutas API encontradas: {found_routes}/{len(api_routes)}")
        return found_routes >= len(api_routes) - 1  # Permitir una ruta faltante
        
    except Exception as e:
        print(f"Error verificando API: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("=" * 60)
    print("PRUEBAS DEL SISTEMA DE GESTIÓN DE VEHÍCULOS")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Existencia de tablas", test_tables_exist),
        ("Existencia de triggers", test_triggers_exist),
        ("Inserción de vehículo y triggers", test_vehicle_insertion),
        ("Estructura de API", test_api_structure)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Ejecutando: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASÓ")
                passed_tests += 1
            else:
                print(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESUMEN DE PRUEBAS: {passed_tests}/{total_tests} pasaron")
    
    if passed_tests == total_tests:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está funcionando correctamente.")
    elif passed_tests >= total_tests * 0.75:
        print("⚠ La mayoría de pruebas pasaron. Revisar fallos menores.")
    else:
        print("❌ Múltiples pruebas fallaron. Revisar configuración del sistema.")
    
    print("=" * 60)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Pruebas interrumpidas por el usuario")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        exit(1)