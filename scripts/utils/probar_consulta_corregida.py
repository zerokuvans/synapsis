#!/usr/bin/env python3
"""
Script para probar la consulta SQL corregida
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

def probar_consulta_corregida():
    connection = get_db_connection()
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    material = 'silicona'
    anio = '2025'
    
    # Consulta corregida
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
        print(f"Probando consulta para {material} en {anio}:")
        cursor.execute(query, (material, anio, material, anio))
        resultados = cursor.fetchall()
        
        if resultados:
            print("✓ Consulta exitosa!")
            for resultado in resultados:
                print(f"  Mes {resultado['mes']}: Entradas={resultado['entradas']}, Salidas={resultado['salidas']}, Stock Final={resultado['stock_final']}")
        else:
            print("✗ No se encontraron resultados")
            
        # Simular respuesta del API
        datos_mensuales = resultados if resultados else []
        
        # Si no hay datos, crear estructura vacía
        if not datos_mensuales:
            datos_mensuales = []
            for mes in range(1, 13):
                datos_mensuales.append({
                    'mes': mes,
                    'entradas': 0,
                    'salidas': 0,
                    'stock_final': 0
                })
            print("\nCreando estructura vacía para todos los meses")
        
        respuesta_api = {
            'status': 'success',
            'datos_mensuales': datos_mensuales,
            'material': material,
            'anio': anio
        }
        
        print("\nRespuesta del API simulada:")
        print(json.dumps(respuesta_api, indent=2, default=str))
        
    except Exception as e:
        print(f"Error en consulta: {e}")
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    probar_consulta_corregida()