#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error

def check_recurso_operativo_table():
    """Verificar la estructura de la tabla recurso_operativo"""
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar estructura de la tabla
            cursor.execute("DESCRIBE recurso_operativo")
            estructura = cursor.fetchall()
            
            print("Estructura de la tabla 'recurso_operativo':")
            for campo in estructura:
                print(f"  {campo[0]} - {campo[1]} - {campo[2]} - {campo[3]}")
            
            # Verificar algunos registros de ejemplo
            cursor.execute("SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula FROM recurso_operativo LIMIT 3")
            registros = cursor.fetchall()
            
            print("\nEjemplos de registros:")
            for registro in registros:
                print(f"  ID: {registro[0]}, Nombre: {registro[1]}, Cédula: {registro[2]}")
                
    except Error as e:
        print(f"Error de base de datos: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    check_recurso_operativo_table()