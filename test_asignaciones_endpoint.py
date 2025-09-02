#!/usr/bin/env python3
"""
Script para probar el nuevo endpoint de asignaciones mensuales
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

# Configuración de la base de datos
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'capired'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error de conexión a MySQL: {str(e)}")
        return None

def verificar_datos_ferretero():
    """Verificar datos en la tabla ferretero"""
    print("\n=== VERIFICANDO DATOS EN TABLA FERRETERO ===")
    connection = get_db_connection()
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Verificar estructura de la tabla
        cursor.execute("DESCRIBE ferretero")
        columnas = cursor.fetchall()
        print("\nEstructura de la tabla ferretero:")
        for col in columnas:
            print(f"  - {col['Field']}: {col['Type']}")
        
        # Verificar datos de 2025
        cursor.execute("""
            SELECT 
                YEAR(fecha_asignacion) as anio,
                MONTH(fecha_asignacion) as mes,
                COUNT(*) as total_asignaciones,
                SUM(silicona) as total_silicona,
                SUM(amarres_negros) as total_amarres_negros,
                SUM(amarres_blancos) as total_amarres_blancos,
                SUM(cinta_aislante) as total_cinta,
                SUM(grapas_blancas) as total_grapas_blancas,
                SUM(grapas_negras) as total_grapas_negras
            FROM ferretero 
            WHERE YEAR(fecha_asignacion) = 2025
            GROUP BY YEAR(fecha_asignacion), MONTH(fecha_asignacion)
            ORDER BY mes
        """)
        
        datos_2025 = cursor.fetchall()
        print("\nDatos de asignaciones 2025 por mes:")
        if datos_2025:
            for dato in datos_2025:
                print(f"  Mes {dato['mes']}: {dato['total_asignaciones']} asignaciones")
                print(f"    - Silicona: {dato['total_silicona'] or 0}")
                print(f"    - Amarres negros: {dato['total_amarres_negros'] or 0}")
                print(f"    - Amarres blancos: {dato['total_amarres_blancos'] or 0}")
                print(f"    - Cinta aislante: {dato['total_cinta'] or 0}")
                print(f"    - Grapas blancas: {dato['total_grapas_blancas'] or 0}")
                print(f"    - Grapas negras: {dato['total_grapas_negras'] or 0}")
        else:
            print("  No hay datos de 2025")
            
    except Exception as e:
        print(f"Error verificando tabla ferretero: {e}")
    
    cursor.close()
    connection.close()

def probar_consulta_asignaciones():
    """Probar la consulta SQL del nuevo endpoint"""
    print("\n=== PROBANDO CONSULTA SQL DE ASIGNACIONES ===")
    connection = get_db_connection()
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    material = 'silicona'
    anio = '2025'
    
    # Consulta del nuevo endpoint
    query = """
        SELECT 
            MONTH(fecha_asignacion) as mes,
            SUM(CASE 
                WHEN %s = 'silicona' THEN COALESCE(silicona, 0)
                WHEN %s = 'amarres_negros' THEN COALESCE(amarres_negros, 0)
                WHEN %s = 'amarres_blancos' THEN COALESCE(amarres_blancos, 0)
                WHEN %s = 'cinta_aislante' THEN COALESCE(cinta_aislante, 0)
                WHEN %s = 'grapas_blancas' THEN COALESCE(grapas_blancas, 0)
                WHEN %s = 'grapas_negras' THEN COALESCE(grapas_negras, 0)
                ELSE 0
            END) as cantidad_asignada
        FROM ferretero 
        WHERE YEAR(fecha_asignacion) = %s
        AND (
            (%s = 'silicona' AND silicona > 0) OR
            (%s = 'amarres_negros' AND amarres_negros > 0) OR
            (%s = 'amarres_blancos' AND amarres_blancos > 0) OR
            (%s = 'cinta_aislante' AND cinta_aislante > 0) OR
            (%s = 'grapas_blancas' AND grapas_blancas > 0) OR
            (%s = 'grapas_negras' AND grapas_negras > 0)
        )
        GROUP BY MONTH(fecha_asignacion)
        ORDER BY mes
    """
    
    try:
        cursor.execute(query, (material, material, material, material, material, material, anio, material, material, material, material, material, material))
        resultados = cursor.fetchall()
        
        print(f"\nConsulta para {material} en {anio}:")
        if resultados:
            for resultado in resultados:
                print(f"  Mes {resultado['mes']}: {resultado['cantidad_asignada']} unidades asignadas")
        else:
            print("  ✗ No se encontraron resultados")
            
    except Exception as e:
        print(f"Error en consulta: {e}")
    
    cursor.close()
    connection.close()

def test_api_endpoint():
    """Probar el endpoint API"""
    print("\n=== PROBANDO ENDPOINT API ===")
    base_url = "http://localhost:5000"
    endpoint = "/api/comparacion_mensual_materiales"
    
    materiales = ['silicona', 'amarres_negros', 'amarres_blancos', 'cinta_aislante', 'grapas_blancas', 'grapas_negras']
    
    for material in materiales:
        params = {
            'material': material,
            'anio': '2025'
        }
        
        try:
            response = requests.get(f"{base_url}{endpoint}", params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✓ {material}: {response.status_code}")
                if data.get('status') == 'success':
                    datos_mensuales = data.get('datos_mensuales', [])
                    total_asignado = sum(item.get('cantidad_asignada', 0) for item in datos_mensuales)
                    meses_con_datos = len([item for item in datos_mensuales if item.get('cantidad_asignada', 0) > 0])
                    print(f"  Total asignado: {total_asignado}")
                    print(f"  Meses con datos: {meses_con_datos}")
                else:
                    print(f"  Error en respuesta: {data.get('message', 'Sin mensaje')}")
            else:
                print(f"\n✗ {material}: {response.status_code}")
                print(f"  Error: {response.text}")
                
        except Exception as e:
            print(f"\n✗ {material}: Error de conexión - {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBAS DEL NUEVO ENDPOINT DE ASIGNACIONES MENSUALES")
    print("=" * 60)
    
    verificar_datos_ferretero()
    probar_consulta_asignaciones()
    test_api_endpoint()
    
    print("\n=== PRUEBAS COMPLETADAS ===")