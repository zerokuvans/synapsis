#!/usr/bin/env python3
"""
Script para verificar la estructura exacta de la tabla movimientos_stock_ferretero
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

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

def verificar_estructura():
    connection = get_db_connection()
    if not connection:
        return
    
    cursor = connection.cursor()
    
    print("=== ESTRUCTURA DE LA TABLA movimientos_stock_ferretero ===")
    cursor.execute("DESCRIBE movimientos_stock_ferretero")
    columns = cursor.fetchall()
    
    for col in columns:
        print(f"Columna: {col[0]} | Tipo: {col[1]} | Null: {col[2]} | Key: {col[3]} | Default: {col[4]} | Extra: {col[5]}")
    
    print("\n=== DATOS DE EJEMPLO ===")
    cursor.execute("SELECT * FROM movimientos_stock_ferretero LIMIT 3")
    datos = cursor.fetchall()
    
    # Obtener nombres de columnas
    cursor.execute("SHOW COLUMNS FROM movimientos_stock_ferretero")
    column_names = [col[0] for col in cursor.fetchall()]
    
    print(f"Columnas: {column_names}")
    for dato in datos:
        print(f"Registro: {dato}")
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    verificar_estructura()