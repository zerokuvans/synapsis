#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def conectar_db():
    """Conectar a la base de datos MySQL"""
    try:
        # Usar la misma configuración que main.py
        db_config = {
            'host': os.getenv('MYSQL_HOST'),
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DB'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'time_zone': '+00:00'
        }
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        print(f"Configuración utilizada:")
        print(f"  Host: {os.getenv('MYSQL_HOST')}")
        print(f"  User: {os.getenv('MYSQL_USER')}")
        print(f"  Database: {os.getenv('MYSQL_DB')}")
        print(f"  Port: {os.getenv('MYSQL_PORT', 3306)}")
        return None

def verificar_stock_camiseta_polo():
    """Verificar el stock actual de camiseta polo NO VALORADO"""
    connection = conectar_db()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print("=== VERIFICACIÓN DE STOCK CAMISETA POLO ===\n")
        
        # 1. Verificar stock total de camiseta polo
        print("1. STOCK TOTAL DE CAMISETA POLO:")
        query_total = """
        SELECT 
            elemento,
            talla,
            valorado,
            SUM(cantidad) as stock_total
        FROM stock_dotaciones 
        WHERE elemento LIKE '%camiseta%polo%' 
        GROUP BY elemento, talla, valorado
        ORDER BY elemento, talla, valorado
        """
        
        cursor.execute(query_total)
        resultados_total = cursor.fetchall()
        
        if resultados_total:
            for row in resultados_total:
                print(f"  - {row['elemento']} | Talla: {row['talla']} | Valorado: {row['valorado']} | Stock: {row['stock_total']}")
        else:
            print("  No se encontró stock de camiseta polo")
        
        print("\n" + "="*50)
        
        # 2. Verificar específicamente stock NO VALORADO
        print("\n2. STOCK ESPECÍFICO NO VALORADO:")
        query_no_valorado = """
        SELECT 
            elemento,
            talla,
            valorado,
            cantidad,
            fecha_actualizacion
        FROM stock_dotaciones 
        WHERE elemento LIKE '%camiseta%polo%' 
        AND valorado = 'NO VALORADO'
        ORDER BY talla, fecha_actualizacion DESC
        """
        
        cursor.execute(query_no_valorado)
        resultados_no_valorado = cursor.fetchall()
        
        if resultados_no_valorado:
            total_no_valorado = 0
            for row in resultados_no_valorado:
                print(f"  - {row['elemento']} | Talla: {row['talla']} | Cantidad: {row['cantidad']} | Fecha: {row['fecha_actualizacion']}")
                total_no_valorado += row['cantidad']
            print(f"\n  TOTAL STOCK NO VALORADO: {total_no_valorado}")
        else:
            print("  ❌ NO SE ENCONTRÓ STOCK NO VALORADO DE CAMISETA POLO")
        
        print("\n" + "="*50)
        
        # 3. Verificar todas las variaciones de nombre
        print("\n3. VERIFICAR TODAS LAS VARIACIONES DE NOMBRE:")
        query_variaciones = """
        SELECT DISTINCT elemento 
        FROM stock_dotaciones 
        WHERE elemento LIKE '%camiseta%' 
        OR elemento LIKE '%polo%'
        ORDER BY elemento
        """
        
        cursor.execute(query_variaciones)
        variaciones = cursor.fetchall()
        
        print("  Elementos encontrados que contienen 'camiseta' o 'polo':")
        for var in variaciones:
            print(f"    - {var['elemento']}")
        
        print("\n" + "="*50)
        
        # 4. Verificar stock por talla específica (ejemplo: M)
        print("\n4. STOCK DETALLADO TALLA M:")
        query_talla_m = """
        SELECT 
            elemento,
            valorado,
            cantidad,
            fecha_actualizacion
        FROM stock_dotaciones 
        WHERE elemento LIKE '%camiseta%polo%' 
        AND talla = 'M'
        ORDER BY valorado, fecha_actualizacion DESC
        """
        
        cursor.execute(query_talla_m)
        resultados_m = cursor.fetchall()
        
        if resultados_m:
            for row in resultados_m:
                print(f"  - {row['elemento']} | Valorado: {row['valorado']} | Cantidad: {row['cantidad']} | Fecha: {row['fecha_actualizacion']}")
        else:
            print("  No se encontró stock talla M")
        
        print("\n" + "="*50)
        
        # 5. Verificar entradas recientes
        print("\n5. ENTRADAS RECIENTES (ÚLTIMOS 7 DÍAS):")
        query_recientes = """
        SELECT 
            elemento,
            talla,
            valorado,
            cantidad,
            fecha_actualizacion,
            tipo_movimiento
        FROM stock_dotaciones 
        WHERE elemento LIKE '%camiseta%polo%' 
        AND fecha_actualizacion >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        ORDER BY fecha_actualizacion DESC
        """
        
        cursor.execute(query_recientes)
        resultados_recientes = cursor.fetchall()
        
        if resultados_recientes:
            for row in resultados_recientes:
                print(f"  - {row['elemento']} | Talla: {row['talla']} | Valorado: {row['valorado']} | Cantidad: {row['cantidad']} | Fecha: {row['fecha_actualizacion']}")
        else:
            print("  No hay movimientos recientes")
        
    except Error as e:
        print(f"Error al ejecutar consulta: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    verificar_stock_camiseta_polo()