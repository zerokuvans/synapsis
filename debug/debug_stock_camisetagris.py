#!/usr/bin/env python3
"""
Script para debuggear el problema específico de stock de camisetagris
"""

import mysql.connector
import json

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
    'autocommit': True
}

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def debug_stock_camisetagris():
    """Debuggear específicamente el stock de camisetagris"""
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        elemento = 'camisetagris'
        
        print(f"=== DEBUG STOCK PARA {elemento.upper()} ===\n")
        
        # Mapeo de columnas
        estado_column_dotaciones = 'estado_camisetagris'
        estado_column_cambios = 'estado_camiseta_gris'
        
        print(f"Columna en dotaciones: {estado_column_dotaciones}")
        print(f"Columna en cambios_dotacion: {estado_column_cambios}\n")
        
        for estado in ['VALORADO', 'NO VALORADO']:
            print(f"--- ESTADO: {estado} ---")
            
            # 1. Ingresos
            cursor.execute("""
                SELECT COALESCE(SUM(cantidad), 0) as total_ingresos
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = %s AND estado = %s
            """, (elemento, estado))
            
            ingresos_result = cursor.fetchone()
            total_ingresos = ingresos_result['total_ingresos'] if ingresos_result else 0
            print(f"Ingresos: {total_ingresos}")
            
            # 2. Salidas de dotaciones
            query_dotaciones = f"""
                SELECT COALESCE(SUM(
                    CASE WHEN {estado_column_dotaciones} = %s THEN {elemento} ELSE 0 END
                ), 0) as total_dotaciones
                FROM dotaciones
                WHERE {elemento} IS NOT NULL AND {elemento} > 0
            """
            print(f"Query dotaciones: {query_dotaciones}")
            
            cursor.execute(query_dotaciones, (estado,))
            dotaciones_result = cursor.fetchone()
            total_dotaciones = dotaciones_result['total_dotaciones'] if dotaciones_result else 0
            print(f"Salidas dotaciones: {total_dotaciones}")
            
            # 3. Salidas de cambios
            query_cambios = f"""
                SELECT COALESCE(SUM(
                    CASE WHEN {estado_column_cambios} = %s THEN {elemento} ELSE 0 END
                ), 0) as total_cambios
                FROM cambios_dotacion
                WHERE {elemento} IS NOT NULL AND {elemento} > 0
            """
            print(f"Query cambios: {query_cambios}")
            
            cursor.execute(query_cambios, (estado,))
            cambios_result = cursor.fetchone()
            total_cambios = cambios_result['total_cambios'] if cambios_result else 0
            print(f"Salidas cambios: {total_cambios}")
            
            # 4. Stock disponible
            stock_disponible = total_ingresos - total_dotaciones - total_cambios
            stock_final = max(0, stock_disponible)
            print(f"Stock calculado: {total_ingresos} - {total_dotaciones} - {total_cambios} = {stock_disponible}")
            print(f"Stock final: {stock_final}\n")
        
        # Verificar datos reales en las tablas
        print("=== VERIFICACIÓN DE DATOS REALES ===\n")
        
        # Verificar ingresos
        cursor.execute("""
            SELECT estado, SUM(cantidad) as total
            FROM ingresos_dotaciones 
            WHERE tipo_elemento = %s
            GROUP BY estado
        """, (elemento,))
        
        ingresos = cursor.fetchall()
        print("Ingresos por estado:")
        for ingreso in ingresos:
            print(f"  {ingreso['estado']}: {ingreso['total']}")
        
        # Verificar dotaciones
        cursor.execute(f"""
            SELECT {estado_column_dotaciones} as estado, SUM({elemento}) as total
            FROM dotaciones 
            WHERE {elemento} IS NOT NULL AND {elemento} > 0
            GROUP BY {estado_column_dotaciones}
        """)
        
        dotaciones = cursor.fetchall()
        print("\nDotaciones por estado:")
        for dotacion in dotaciones:
            print(f"  {dotacion['estado']}: {dotacion['total']}")
        
        # Verificar cambios
        cursor.execute(f"""
            SELECT {estado_column_cambios} as estado, SUM({elemento}) as total
            FROM cambios_dotacion 
            WHERE {elemento} IS NOT NULL AND {elemento} > 0
            GROUP BY {estado_column_cambios}
        """)
        
        cambios = cursor.fetchall()
        print("\nCambios por estado:")
        for cambio in cambios:
            print(f"  {cambio['estado']}: {cambio['total']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    debug_stock_camisetagris()