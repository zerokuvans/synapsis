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
        return None

def verificar_inventario_dotaciones():
    """Verificar el stock en inventario_dotaciones"""
    connection = conectar_db()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print("=== VERIFICACIÓN DE INVENTARIO DOTACIONES ===\n")
        
        # 1. Verificar estructura de la tabla
        print("1. ESTRUCTURA DE LA TABLA inventario_dotaciones:")
        cursor.execute("DESCRIBE inventario_dotaciones")
        estructura = cursor.fetchall()
        
        for campo in estructura:
            print(f"  - {campo['Field']} | {campo['Type']} | {campo['Null']} | {campo['Key']} | {campo['Default']}")
        
        print("\n" + "="*50)
        
        # 2. Verificar todos los registros de camiseta polo
        print("\n2. TODOS LOS REGISTROS DE CAMISETA POLO:")
        query_camiseta = """
        SELECT * FROM inventario_dotaciones 
        WHERE elemento LIKE '%camiseta%polo%' 
        OR elemento LIKE '%camisetapolo%'
        ORDER BY elemento, talla, valorado
        """
        
        cursor.execute(query_camiseta)
        resultados = cursor.fetchall()
        
        if resultados:
            print(f"  Encontrados {len(resultados)} registros:")
            for row in resultados:
                print(f"    ID: {row.get('id', 'N/A')} | Elemento: {row.get('elemento', 'N/A')} | Talla: {row.get('talla', 'N/A')} | Valorado: {row.get('valorado', 'N/A')} | Cantidad: {row.get('cantidad', 'N/A')}")
        else:
            print("  ❌ NO SE ENCONTRARON REGISTROS DE CAMISETA POLO")
        
        print("\n" + "="*50)
        
        # 3. Verificar específicamente stock NO VALORADO
        print("\n3. STOCK ESPECÍFICO NO VALORADO:")
        query_no_valorado = """
        SELECT * FROM inventario_dotaciones 
        WHERE (elemento LIKE '%camiseta%polo%' OR elemento LIKE '%camisetapolo%')
        AND valorado = 'NO VALORADO'
        ORDER BY talla
        """
        
        cursor.execute(query_no_valorado)
        no_valorado = cursor.fetchall()
        
        if no_valorado:
            total_no_valorado = 0
            print(f"  Encontrados {len(no_valorado)} registros NO VALORADO:")
            for row in no_valorado:
                cantidad = row.get('cantidad', 0)
                total_no_valorado += cantidad
                print(f"    - {row.get('elemento', 'N/A')} | Talla: {row.get('talla', 'N/A')} | Cantidad: {cantidad}")
            print(f"\n  ✅ TOTAL STOCK NO VALORADO: {total_no_valorado}")
        else:
            print("  ❌ NO SE ENCONTRÓ STOCK NO VALORADO")
        
        print("\n" + "="*50)
        
        # 4. Verificar stock VALORADO para comparar
        print("\n4. STOCK ESPECÍFICO VALORADO:")
        query_valorado = """
        SELECT * FROM inventario_dotaciones 
        WHERE (elemento LIKE '%camiseta%polo%' OR elemento LIKE '%camisetapolo%')
        AND valorado = 'VALORADO'
        ORDER BY talla
        """
        
        cursor.execute(query_valorado)
        valorado = cursor.fetchall()
        
        if valorado:
            total_valorado = 0
            print(f"  Encontrados {len(valorado)} registros VALORADO:")
            for row in valorado:
                cantidad = row.get('cantidad', 0)
                total_valorado += cantidad
                print(f"    - {row.get('elemento', 'N/A')} | Talla: {row.get('talla', 'N/A')} | Cantidad: {cantidad}")
            print(f"\n  ✅ TOTAL STOCK VALORADO: {total_valorado}")
        else:
            print("  ❌ NO SE ENCONTRÓ STOCK VALORADO")
        
        print("\n" + "="*50)
        
        # 5. Verificar todos los elementos únicos para ver variaciones de nombre
        print("\n5. TODOS LOS ELEMENTOS ÚNICOS QUE CONTIENEN 'CAMISETA' O 'POLO':")
        query_elementos = """
        SELECT DISTINCT elemento FROM inventario_dotaciones 
        WHERE elemento LIKE '%camiseta%' 
        OR elemento LIKE '%polo%'
        ORDER BY elemento
        """
        
        cursor.execute(query_elementos)
        elementos = cursor.fetchall()
        
        if elementos:
            for elem in elementos:
                print(f"    - {elem['elemento']}")
        else:
            print("  No se encontraron elementos con 'camiseta' o 'polo'")
        
        print("\n" + "="*50)
        
        # 6. Verificar resumen por valorado
        print("\n6. RESUMEN POR ESTADO VALORADO:")
        query_resumen = """
        SELECT 
            valorado,
            COUNT(*) as registros,
            SUM(cantidad) as total_cantidad
        FROM inventario_dotaciones 
        WHERE (elemento LIKE '%camiseta%polo%' OR elemento LIKE '%camisetapolo%')
        GROUP BY valorado
        ORDER BY valorado
        """
        
        cursor.execute(query_resumen)
        resumen = cursor.fetchall()
        
        if resumen:
            for row in resumen:
                print(f"    - {row['valorado']}: {row['registros']} registros, {row['total_cantidad']} unidades")
        else:
            print("  No hay datos para el resumen")
        
    except Error as e:
        print(f"Error al ejecutar consulta: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    verificar_inventario_dotaciones()