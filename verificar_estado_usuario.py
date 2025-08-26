#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar el estado exacto del usuario 1019112308 en la base de datos
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
        # Usar la misma configuración que main.py
        db_config = {
            'host': os.getenv('MYSQL_HOST'),
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DB'),
            'port': int(os.getenv('MYSQL_PORT')),
            'time_zone': '+00:00'
        }
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def verificar_estado_usuario(cedula):
    """Verificar el estado exacto del usuario en la base de datos"""
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if connection is None:
            print("No se pudo conectar a la base de datos")
            return
            
        cursor = connection.cursor(dictionary=True)
        
        # Consultar información del usuario
        query = """
        SELECT 
            recurso_operativo_cedula,
            nombre,
            estado,
            LENGTH(estado) as longitud_estado,
            ASCII(SUBSTRING(estado, 1, 1)) as ascii_primer_caracter,
            HEX(estado) as hex_estado
        FROM recurso_operativo 
        WHERE recurso_operativo_cedula = %s
        """
        
        cursor.execute(query, (cedula,))
        resultado = cursor.fetchone()
        
        if resultado:
            print(f"\n=== INFORMACIÓN DEL USUARIO {cedula} ===")
            print(f"Nombre: {resultado['nombre']}")
            print(f"Estado: '{resultado['estado']}'")
            print(f"Longitud del estado: {resultado['longitud_estado']}")
            print(f"ASCII primer carácter: {resultado['ascii_primer_caracter']}")
            print(f"Valor hexadecimal: {resultado['hex_estado']}")
            
            # Verificar si hay espacios o caracteres especiales
            estado = resultado['estado']
            if estado != estado.strip():
                print(f"⚠️  ADVERTENCIA: El estado tiene espacios al inicio o final")
                print(f"Estado sin espacios: '{estado.strip()}'")
            
            # Verificar diferentes variaciones
            print(f"\n=== COMPARACIONES ===")
            print(f"estado == 'Activo': {estado == 'Activo'}")
            print(f"estado == 'activo': {estado == 'activo'}")
            print(f"estado == 'ACTIVO': {estado == 'ACTIVO'}")
            print(f"estado == 'Inactivo': {estado == 'Inactivo'}")
            print(f"estado == 'inactivo': {estado == 'inactivo'}")
            print(f"estado == 'INACTIVO': {estado == 'INACTIVO'}")
            print(f"estado.lower() == 'activo': {estado.lower() == 'activo'}")
            print(f"estado.lower() == 'inactivo': {estado.lower() == 'inactivo'}")
            
        else:
            print(f"\n❌ Usuario {cedula} no encontrado en la base de datos")
            
    except Error as e:
        print(f"Error de MySQL: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    print("Verificando estado del usuario 1019112308...")
    verificar_estado_usuario("1019112308")