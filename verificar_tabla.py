#!/usr/bin/env python3
import mysql.connector
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

def verificar_estructura_tabla():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Verificar estructura de la tabla tipificacion_asistencia
        cursor.execute("DESCRIBE tipificacion_asistencia")
        columnas = cursor.fetchall()
        
        print("\n=== Estructura de la tabla tipificacion_asistencia ===")
        for columna in columnas:
            print(f"Columna: {columna['Field']} - Tipo: {columna['Type']} - Null: {columna['Null']} - Default: {columna['Default']}")
        
        # Verificar si existe la columna zona
        columnas_nombres = [col['Field'] for col in columnas]
        zona_existe = 'zona' in columnas_nombres
        
        print(f"\n¿Existe la columna 'zona'? {zona_existe}")
        
        # Mostrar algunos registros de ejemplo
        cursor.execute("SELECT * FROM tipificacion_asistencia LIMIT 5")
        registros = cursor.fetchall()
        
        print("\n=== Registros de ejemplo ===")
        for registro in registros:
            print(registro)
            
        return zona_existe
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    verificar_estructura_tabla()