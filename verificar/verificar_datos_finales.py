#!/usr/bin/env python3
"""
Script final para verificar que los datos se están devolviendo correctamente
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import json

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

def simular_endpoint_api():
    """Simular exactamente lo que hace el endpoint API"""
    connection = get_db_connection()
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    material = 'silicona'
    anio = '2025'
    
    print(f"=== SIMULANDO ENDPOINT API ===")
    print(f"Material: {material}, Año: {anio}")
    
    # Consulta exacta del endpoint
    query = """
        SELECT 
            mes,
            SUM(entradas) as entradas,
            SUM(salidas) as salidas,
            (
                SELECT cantidad_nueva 
                FROM movimientos_stock_ferretero m2 
                WHERE m2.material_tipo = %s 
                AND YEAR(m2.fecha_movimiento) = %s 
                AND MONTH(m2.fecha_movimiento) = mes
                ORDER BY m2.fecha_movimiento DESC 
                LIMIT 1
            ) as stock_final
        FROM (
            SELECT 
                MONTH(fecha_movimiento) as mes,
                CASE WHEN tipo_movimiento = 'entrada' THEN cantidad ELSE 0 END as entradas,
                CASE WHEN tipo_movimiento = 'salida' THEN cantidad ELSE 0 END as salidas
            FROM movimientos_stock_ferretero 
            WHERE material_tipo = %s 
            AND YEAR(fecha_movimiento) = %s
        ) as movimientos_mes
        GROUP BY mes
        ORDER BY mes
    """
    
    try:
        cursor.execute(query, (material, anio, material, anio))
        datos_mensuales = cursor.fetchall()
        
        print(f"\nDatos obtenidos de la consulta: {len(datos_mensuales)} registros")
        
        # Si no hay datos, crear estructura vacía
        if not datos_mensuales:
            print("No hay datos, creando estructura vacía...")
            datos_mensuales = []
            for mes in range(1, 13):
                datos_mensuales.append({
                    'mes': mes,
                    'entradas': 0,
                    'salidas': 0,
                    'stock_final': 0
                })
        
        # Simular respuesta del API
        respuesta = {
            'status': 'success',
            'datos_mensuales': datos_mensuales,
            'material': material,
            'anio': anio
        }
        
        print("\n=== RESPUESTA DEL API ===")
        print(json.dumps(respuesta, indent=2, default=str))
        
        # Verificar si hay datos reales
        datos_reales = [d for d in datos_mensuales if d['entradas'] > 0 or d['salidas'] > 0]
        if datos_reales:
            print(f"\n✓ Se encontraron {len(datos_reales)} meses con datos reales")
            for dato in datos_reales:
                print(f"  Mes {dato['mes']}: Entradas={dato['entradas']}, Salidas={dato['salidas']}, Stock={dato['stock_final']}")
        else:
            print("\n⚠ No se encontraron datos reales, el gráfico mostrará valores en cero")
        
    except Exception as e:
        print(f"Error en consulta: {e}")
    
    cursor.close()
    connection.close()

def verificar_datos_disponibles():
    """Verificar qué datos hay disponibles en la base de datos"""
    connection = get_db_connection()
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    print("\n=== VERIFICANDO DATOS DISPONIBLES ===")
    
    # Verificar datos por material y año
    cursor.execute("""
        SELECT 
            material_tipo,
            YEAR(fecha_movimiento) as anio,
            COUNT(*) as total_movimientos,
            SUM(CASE WHEN tipo_movimiento = 'entrada' THEN cantidad ELSE 0 END) as total_entradas,
            SUM(CASE WHEN tipo_movimiento = 'salida' THEN cantidad ELSE 0 END) as total_salidas
        FROM movimientos_stock_ferretero 
        GROUP BY material_tipo, YEAR(fecha_movimiento)
        ORDER BY material_tipo, anio
    """)
    
    datos_disponibles = cursor.fetchall()
    
    if datos_disponibles:
        print("Datos disponibles por material y año:")
        for dato in datos_disponibles:
            print(f"  {dato['material_tipo']} ({dato['anio']}): {dato['total_movimientos']} movimientos, {dato['total_entradas']} entradas, {dato['total_salidas']} salidas")
    else:
        print("No hay datos disponibles en movimientos_stock_ferretero")
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    print("VERIFICACIÓN FINAL DE DATOS PARA EL GRÁFICO")
    print("=" * 50)
    
    verificar_datos_disponibles()
    simular_endpoint_api()
    
    print("\n=== CONCLUSIÓN ===")
    print("Si el endpoint devuelve datos con entradas/salidas > 0, el gráfico debería mostrar información.")
    print("Si todos los valores son 0, el gráfico aparecerá vacío como se observa actualmente.")
    print("\n=== VERIFICACIÓN COMPLETADA ===")