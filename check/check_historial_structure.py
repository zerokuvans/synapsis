#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla historial_vencimientos
y encontrar el error en la consulta WHERE
"""

import mysql.connector
import os
from dotenv import load_dotenv

def get_db_connection():
    """Obtener conexión a la base de datos"""
    load_dotenv()
    
    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DB'),
        'autocommit': True
    }
    
    return mysql.connector.connect(**config)

def main():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("=== ESTRUCTURA DE TABLA historial_vencimientos ===")
        cursor.execute("DESCRIBE historial_vencimientos")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"  {col[0]} - {col[1]} - {col[2]} - {col[3]} - {col[4]} - {col[5]}")
        
        print("\n=== CONTENIDO ACTUAL DE historial_vencimientos ===")
        cursor.execute("SELECT * FROM historial_vencimientos LIMIT 5")
        rows = cursor.fetchall()
        
        if rows:
            for row in rows:
                print(f"  {row}")
        else:
            print("  (Tabla vacía)")
        
        print("\n=== VERIFICAR SI EXISTE COLUMNA id_parque_automotor ===")
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'historial_vencimientos' 
            AND COLUMN_NAME = 'id_parque_automotor'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"  ✓ Columna id_parque_automotor existe")
        else:
            print(f"  ❌ Columna id_parque_automotor NO existe")
        
        print("\n=== VERIFICAR RELACIÓN CON parque_automotor ===")
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'historial_vencimientos' 
            AND COLUMN_NAME LIKE '%vehiculo%' OR COLUMN_NAME LIKE '%parque%'
        """)
        
        related_columns = cursor.fetchall()
        if related_columns:
            print("  Columnas relacionadas con vehículos:")
            for col in related_columns:
                print(f"    - {col[0]}")
        else:
            print("  No se encontraron columnas relacionadas")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()