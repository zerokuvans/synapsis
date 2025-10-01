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

def verificar_stock_real():
    """Verificar el stock en las tablas que realmente existen"""
    connection = conectar_db()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print("=== VERIFICACIÓN DE STOCK REAL ===\n")
        
        # 1. Verificar vista_stock_dotaciones
        print("1. VISTA STOCK DOTACIONES:")
        try:
            cursor.execute("DESCRIBE vista_stock_dotaciones")
            estructura = cursor.fetchall()
            
            print("  Estructura:")
            for campo in estructura:
                print(f"    - {campo['Field']} | {campo['Type']}")
            
            print("\n  Datos de camiseta polo:")
            cursor.execute("SELECT * FROM vista_stock_dotaciones WHERE tipo_elemento LIKE '%camiseta%polo%' OR tipo_elemento LIKE '%camisetapolo%'")
            resultados = cursor.fetchall()
            
            for row in resultados:
                print(f"    - Elemento: {row.get('tipo_elemento', 'N/A')} | Ingresado: {row.get('cantidad_ingresada', 0)} | Entregado: {row.get('cantidad_entregada', 0)} | Disponible: {row.get('saldo_disponible', 0)}")
                
        except Error as e:
            print(f"  Error: {e}")
        
        print("\n" + "="*50)
        
        # 2. Verificar movimientos_inventario
        print("\n2. MOVIMIENTOS INVENTARIO:")
        try:
            cursor.execute("DESCRIBE movimientos_inventario")
            estructura = cursor.fetchall()
            
            print("  Estructura:")
            for campo in estructura:
                print(f"    - {campo['Field']} | {campo['Type']}")
            
            print("\n  Datos de camiseta polo:")
            cursor.execute("SELECT * FROM movimientos_inventario WHERE elemento LIKE '%camiseta%polo%' OR elemento LIKE '%camisetapolo%' LIMIT 10")
            resultados = cursor.fetchall()
            
            if resultados:
                for row in resultados:
                    print(f"    - ID: {row.get('id', 'N/A')} | Elemento: {row.get('elemento', 'N/A')} | Cantidad: {row.get('cantidad', 'N/A')} | Tipo: {row.get('tipo_movimiento', 'N/A')} | Valorado: {row.get('valorado', 'N/A')}")
            else:
                print("    No se encontraron registros")
                
        except Error as e:
            print(f"  Error: {e}")
        
        print("\n" + "="*50)
        
        # 3. Verificar dotaciones (tabla principal)
        print("\n3. TABLA DOTACIONES:")
        try:
            cursor.execute("DESCRIBE dotaciones")
            estructura = cursor.fetchall()
            
            print("  Estructura:")
            for campo in estructura:
                print(f"    - {campo['Field']} | {campo['Type']}")
            
            print("\n  Últimas dotaciones con camiseta polo:")
            cursor.execute("""
                SELECT id, cedula_tecnico, camisetapolo, camisetapolo_talla, camiseta_polo_valorado, fecha_dotacion 
                FROM dotaciones 
                WHERE camisetapolo > 0 
                ORDER BY fecha_dotacion DESC 
                LIMIT 10
            """)
            resultados = cursor.fetchall()
            
            if resultados:
                for row in resultados:
                    print(f"    - ID: {row.get('id', 'N/A')} | Cédula: {row.get('cedula_tecnico', 'N/A')} | Cantidad: {row.get('camisetapolo', 'N/A')} | Talla: {row.get('camisetapolo_talla', 'N/A')} | Valorado: {row.get('camiseta_polo_valorado', 'N/A')} | Fecha: {row.get('fecha_dotacion', 'N/A')}")
            else:
                print("    No se encontraron dotaciones con camiseta polo")
                
        except Error as e:
            print(f"  Error: {e}")
        
        print("\n" + "="*50)
        
        # 4. Verificar cambios_dotacion
        print("\n4. TABLA CAMBIOS DOTACION:")
        try:
            cursor.execute("DESCRIBE cambios_dotacion")
            estructura = cursor.fetchall()
            
            print("  Estructura:")
            for campo in estructura:
                print(f"    - {campo['Field']} | {campo['Type']}")
            
            print("\n  Últimos cambios con camiseta polo:")
            cursor.execute("""
                SELECT id, cedula_tecnico, camisetapolo, camisetapolo_talla, camiseta_polo_valorado, fecha_cambio 
                FROM cambios_dotacion 
                WHERE camisetapolo > 0 
                ORDER BY fecha_cambio DESC 
                LIMIT 10
            """)
            resultados = cursor.fetchall()
            
            if resultados:
                for row in resultados:
                    print(f"    - ID: {row.get('id', 'N/A')} | Cédula: {row.get('cedula_tecnico', 'N/A')} | Cantidad: {row.get('camisetapolo', 'N/A')} | Talla: {row.get('camisetapolo_talla', 'N/A')} | Valorado: {row.get('camiseta_polo_valorado', 'N/A')} | Fecha: {row.get('fecha_cambio', 'N/A')}")
            else:
                print("    No se encontraron cambios con camiseta polo")
                
        except Error as e:
            print(f"  Error: {e}")
        
        print("\n" + "="*50)
        
        # 5. Calcular stock disponible basado en movimientos
        print("\n5. CÁLCULO DE STOCK DISPONIBLE:")
        try:
            # Stock total ingresado
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN tipo_movimiento = 'entrada' THEN cantidad ELSE 0 END) as total_entradas,
                    SUM(CASE WHEN tipo_movimiento = 'salida' THEN cantidad ELSE 0 END) as total_salidas,
                    valorado
                FROM movimientos_inventario 
                WHERE elemento LIKE '%camisetapolo%' 
                GROUP BY valorado
            """)
            stock_calc = cursor.fetchall()
            
            if stock_calc:
                for row in stock_calc:
                    entradas = row.get('total_entradas', 0) or 0
                    salidas = row.get('total_salidas', 0) or 0
                    disponible = entradas - salidas
                    valorado = row.get('valorado', 'N/A')
                    print(f"    - {valorado}: Entradas: {entradas}, Salidas: {salidas}, Disponible: {disponible}")
            else:
                print("    No se encontraron movimientos para calcular stock")
                
        except Error as e:
            print(f"  Error calculando stock: {e}")
        
    except Error as e:
        print(f"Error general: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    verificar_stock_real()