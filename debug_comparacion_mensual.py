#!/usr/bin/env python3
"""
Script para debuggear el problema de datos en la comparación mensual de materiales
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT')),
    'time_zone': '+00:00'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error de conexión a MySQL: {str(e)}")
        return None

def verificar_tablas_existentes():
    """Verificar qué tablas relacionadas con stock existen"""
    print("=== VERIFICANDO TABLAS EXISTENTES ===")
    connection = get_db_connection()
    if not connection:
        return
    
    cursor = connection.cursor()
    
    # Verificar tablas relacionadas con stock
    tablas_a_verificar = [
        'movimientos_stock_ferretero',
        'stock_ferretero', 
        'entradas_ferretero',
        'asignaciones_ferretero',
        'stock_general'
    ]
    
    for tabla in tablas_a_verificar:
        try:
            cursor.execute(f"SHOW TABLES LIKE '{tabla}'")
            result = cursor.fetchone()
            if result:
                print(f"✓ Tabla {tabla} existe")
                
                # Contar registros
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"  - Registros: {count}")
                
                # Mostrar estructura
                cursor.execute(f"DESCRIBE {tabla}")
                columns = cursor.fetchall()
                print(f"  - Columnas: {[col[0] for col in columns]}")
                
            else:
                print(f"✗ Tabla {tabla} NO existe")
        except Exception as e:
            print(f"✗ Error verificando tabla {tabla}: {e}")
    
    cursor.close()
    connection.close()

def verificar_datos_movimientos():
    """Verificar datos en la tabla movimientos_stock_ferretero"""
    print("\n=== VERIFICANDO DATOS EN MOVIMIENTOS_STOCK_FERRETERO ===")
    connection = get_db_connection()
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'movimientos_stock_ferretero'")
        if not cursor.fetchone():
            print("✗ La tabla movimientos_stock_ferretero NO existe")
            return
        
        # Contar total de registros
        cursor.execute("SELECT COUNT(*) as total FROM movimientos_stock_ferretero")
        total = cursor.fetchone()['total']
        print(f"Total de registros: {total}")
        
        if total == 0:
            print("✗ No hay datos en la tabla movimientos_stock_ferretero")
            return
        
        # Verificar datos por material
        cursor.execute("""
            SELECT 
                material_tipo,
                COUNT(*) as registros,
                MIN(fecha_movimiento) as fecha_min,
                MAX(fecha_movimiento) as fecha_max
            FROM movimientos_stock_ferretero 
            GROUP BY material_tipo
        """)
        
        datos_por_material = cursor.fetchall()
        print("\nDatos por material:")
        for dato in datos_por_material:
            print(f"  - {dato['material_tipo']}: {dato['registros']} registros ({dato['fecha_min']} a {dato['fecha_max']})")
        
        # Verificar datos de 2025
        cursor.execute("""
            SELECT 
                material_tipo,
                YEAR(fecha_movimiento) as anio,
                MONTH(fecha_movimiento) as mes,
                COUNT(*) as registros
            FROM movimientos_stock_ferretero 
            WHERE YEAR(fecha_movimiento) = 2025
            GROUP BY material_tipo, YEAR(fecha_movimiento), MONTH(fecha_movimiento)
            ORDER BY material_tipo, mes
        """)
        
        datos_2025 = cursor.fetchall()
        print("\nDatos de 2025 por mes:")
        if datos_2025:
            for dato in datos_2025:
                print(f"  - {dato['material_tipo']} - {dato['anio']}/{dato['mes']:02d}: {dato['registros']} registros")
        else:
            print("  ✗ No hay datos para el año 2025")
        
        # Mostrar algunos registros de ejemplo
        cursor.execute("""
            SELECT * FROM movimientos_stock_ferretero 
            ORDER BY fecha_movimiento DESC 
            LIMIT 5
        """)
        
        ejemplos = cursor.fetchall()
        print("\nÚltimos 5 registros:")
        for ejemplo in ejemplos:
            print(f"  - {ejemplo}")
            
    except Exception as e:
        print(f"Error verificando datos: {e}")
    
    cursor.close()
    connection.close()

def probar_consulta_api():
    """Probar la consulta SQL del endpoint API"""
    print("\n=== PROBANDO CONSULTA SQL DEL API ===")
    connection = get_db_connection()
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    material = 'silicona'
    anio = '2025'
    
    # Consulta original del API
    query = """
        SELECT 
            MONTH(fecha_movimiento) as mes,
            SUM(CASE WHEN tipo_movimiento = 'entrada' THEN cantidad ELSE 0 END) as entradas,
            SUM(CASE WHEN tipo_movimiento = 'salida' THEN cantidad ELSE 0 END) as salidas,
            (
                SELECT stock_actual 
                FROM movimientos_stock_ferretero m2 
                WHERE m2.material_tipo = %s 
                AND YEAR(m2.fecha_movimiento) = %s 
                AND MONTH(m2.fecha_movimiento) = MONTH(m1.fecha_movimiento)
                ORDER BY m2.fecha_movimiento DESC 
                LIMIT 1
            ) as stock_final
        FROM movimientos_stock_ferretero m1
        WHERE material_tipo = %s 
        AND YEAR(fecha_movimiento) = %s
        GROUP BY MONTH(fecha_movimiento)
        ORDER BY mes
    """
    
    try:
        cursor.execute(query, (material, anio, material, anio))
        resultados = cursor.fetchall()
        
        print(f"Consulta para {material} en {anio}:")
        if resultados:
            for resultado in resultados:
                print(f"  Mes {resultado['mes']}: Entradas={resultado['entradas']}, Salidas={resultado['salidas']}, Stock={resultado['stock_final']}")
        else:
            print("  ✗ No se encontraron resultados")
            
        # Probar consulta simplificada
        print("\nConsulta simplificada:")
        cursor.execute("""
            SELECT 
                MONTH(fecha_movimiento) as mes,
                tipo_movimiento,
                SUM(cantidad) as total_cantidad
            FROM movimientos_stock_ferretero 
            WHERE material_tipo = %s 
            AND YEAR(fecha_movimiento) = %s
            GROUP BY MONTH(fecha_movimiento), tipo_movimiento
            ORDER BY mes, tipo_movimiento
        """, (material, anio))
        
        resultados_simple = cursor.fetchall()
        for resultado in resultados_simple:
            print(f"  Mes {resultado['mes']} - {resultado['tipo_movimiento']}: {resultado['total_cantidad']}")
            
    except Exception as e:
        print(f"Error en consulta: {e}")
    
    cursor.close()
    connection.close()

def verificar_otras_tablas():
    """Verificar datos en otras tablas relacionadas"""
    print("\n=== VERIFICANDO OTRAS TABLAS RELACIONADAS ===")
    connection = get_db_connection()
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    # Verificar entradas_ferretero
    try:
        cursor.execute("SELECT COUNT(*) as total FROM entradas_ferretero")
        total_entradas = cursor.fetchone()['total']
        print(f"Entradas ferretero: {total_entradas} registros")
        
        if total_entradas > 0:
            cursor.execute("""
                SELECT material_tipo, COUNT(*) as cantidad, SUM(cantidad_entrada) as total_cantidad
                FROM entradas_ferretero 
                GROUP BY material_tipo
            """)
            entradas_por_material = cursor.fetchall()
            for entrada in entradas_por_material:
                print(f"  - {entrada['material_tipo']}: {entrada['cantidad']} entradas, total: {entrada['total_cantidad']}")
    except Exception as e:
        print(f"Error verificando entradas_ferretero: {e}")
    
    # Verificar asignaciones_ferretero
    try:
        cursor.execute("SELECT COUNT(*) as total FROM asignaciones_ferretero")
        total_asignaciones = cursor.fetchone()['total']
        print(f"Asignaciones ferretero: {total_asignaciones} registros")
        
        if total_asignaciones > 0:
            cursor.execute("""
                SELECT 
                    SUM(silicona) as total_silicona,
                    SUM(amarres_negros) as total_amarres_negros,
                    SUM(amarres_blancos) as total_amarres_blancos,
                    SUM(cinta_aislante) as total_cinta,
                    SUM(grapas_blancas) as total_grapas_blancas,
                    SUM(grapas_negras) as total_grapas_negras
                FROM asignaciones_ferretero
            """)
            totales = cursor.fetchone()
            print(f"  Totales asignados: {totales}")
    except Exception as e:
        print(f"Error verificando asignaciones_ferretero: {e}")
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    print("DIAGNÓSTICO DE COMPARACIÓN MENSUAL DE MATERIALES")
    print("=" * 50)
    
    verificar_tablas_existentes()
    verificar_datos_movimientos()
    probar_consulta_api()
    verificar_otras_tablas()
    
    print("\n=== DIAGNÓSTICO COMPLETADO ===")