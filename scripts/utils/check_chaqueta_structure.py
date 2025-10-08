#!/usr/bin/env python3
"""
Script para verificar la estructura de la base de datos para el elemento 'chaqueta'
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'synapsis'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            port=int(os.getenv('DB_PORT', 3306))
        )
        return connection
    except Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def check_table_structure(table_name):
    """Verificar la estructura de una tabla específica"""
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        print(f"\n=== ESTRUCTURA DE LA TABLA {table_name.upper()} ===")
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        
        chaqueta_columns = []
        for column in columns:
            column_name = column[0]
            if 'chaqueta' in column_name.lower():
                chaqueta_columns.append(column_name)
                print(f"✓ Columna relacionada con chaqueta: {column_name} - Tipo: {column[1]}")
        
        if not chaqueta_columns:
            print(f"✗ No se encontraron columnas relacionadas con 'chaqueta' en la tabla {table_name}")
        
        return chaqueta_columns
        
    except Error as e:
        print(f"Error verificando estructura de {table_name}: {e}")
        return []
    finally:
        if connection:
            connection.close()

def check_chaqueta_data():
    """Verificar si hay datos de chaqueta en las tablas"""
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # Verificar datos en ingresos_dotaciones
        print(f"\n=== DATOS DE CHAQUETA EN INGRESOS_DOTACIONES ===")
        cursor.execute("SELECT COUNT(*) FROM ingresos_dotaciones WHERE tipo_elemento = 'chaqueta'")
        count = cursor.fetchone()[0]
        print(f"Registros de chaqueta en ingresos_dotaciones: {count}")
        
        if count > 0:
            cursor.execute("SELECT estado, SUM(cantidad) as total FROM ingresos_dotaciones WHERE tipo_elemento = 'chaqueta' GROUP BY estado")
            results = cursor.fetchall()
            for estado, total in results:
                print(f"  - Estado {estado}: {total} unidades")
        
        # Verificar datos en dotaciones
        print(f"\n=== DATOS DE CHAQUETA EN DOTACIONES ===")
        cursor.execute("SELECT COUNT(*) FROM dotaciones WHERE chaqueta IS NOT NULL AND chaqueta > 0")
        count = cursor.fetchone()[0]
        print(f"Registros con chaqueta en dotaciones: {count}")
        
        if count > 0:
            cursor.execute("SELECT estado_chaqueta, SUM(chaqueta) as total FROM dotaciones WHERE chaqueta IS NOT NULL AND chaqueta > 0 GROUP BY estado_chaqueta")
            results = cursor.fetchall()
            for estado, total in results:
                print(f"  - Estado {estado}: {total} unidades")
        
        # Verificar datos en cambios_dotacion
        print(f"\n=== DATOS DE CHAQUETA EN CAMBIOS_DOTACION ===")
        cursor.execute("SELECT COUNT(*) FROM cambios_dotacion WHERE chaqueta IS NOT NULL AND chaqueta > 0")
        count = cursor.fetchone()[0]
        print(f"Registros con chaqueta en cambios_dotacion: {count}")
        
        if count > 0:
            cursor.execute("SELECT estado_chaqueta, SUM(chaqueta) as total FROM cambios_dotacion WHERE chaqueta IS NOT NULL AND chaqueta > 0 GROUP BY estado_chaqueta")
            results = cursor.fetchall()
            for estado, total in results:
                print(f"  - Estado {estado}: {total} unidades")
        
    except Error as e:
        print(f"Error verificando datos de chaqueta: {e}")
    finally:
        if connection:
            connection.close()

def main():
    print("=== VERIFICACIÓN DE ESTRUCTURA Y DATOS PARA CHAQUETA ===")
    
    # Verificar estructura de las tablas principales
    tables = ['dotaciones', 'cambios_dotacion', 'ingresos_dotaciones']
    
    for table in tables:
        check_table_structure(table)
    
    # Verificar datos
    check_chaqueta_data()

if __name__ == "__main__":
    main()