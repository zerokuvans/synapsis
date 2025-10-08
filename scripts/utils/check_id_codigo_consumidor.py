#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_id_codigo_consumidor():
    """Verificar la estructura del campo id_codigo_consumidor"""
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
            database='capired'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            print("=" * 80)
            print("ANÁLISIS DEL CAMPO 'id_codigo_consumidor'")
            print("=" * 80)
            
            # 1. Verificar estructura del campo id_codigo_consumidor
            print("\n1. ESTRUCTURA DEL CAMPO 'id_codigo_consumidor':")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, 
                       CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'capired' 
                AND TABLE_NAME = 'cambios_dotacion' 
                AND COLUMN_NAME = 'id_codigo_consumidor'
            """)
            
            campo_info = cursor.fetchone()
            if campo_info:
                print(f"  Nombre: {campo_info['COLUMN_NAME']}")
                print(f"  Tipo: {campo_info['DATA_TYPE']}")
                print(f"  Permite NULL: {campo_info['IS_NULLABLE']}")
                print(f"  Valor por defecto: {campo_info['COLUMN_DEFAULT']}")
                print(f"  Longitud máxima: {campo_info['CHARACTER_MAXIMUM_LENGTH']}")
                print(f"  Precisión numérica: {campo_info['NUMERIC_PRECISION']}")
                print(f"  Escala numérica: {campo_info['NUMERIC_SCALE']}")
            
            # 2. Verificar datos existentes en id_codigo_consumidor
            print("\n2. DATOS EXISTENTES EN 'id_codigo_consumidor':")
            cursor.execute("""
                SELECT id_codigo_consumidor, COUNT(*) as cantidad
                FROM cambios_dotacion 
                GROUP BY id_codigo_consumidor
                ORDER BY id_codigo_consumidor
                LIMIT 10
            """)
            
            datos_existentes = cursor.fetchall()
            if datos_existentes:
                print("  Valores encontrados (primeros 10):")
                for dato in datos_existentes:
                    print(f"    {dato['id_codigo_consumidor']} (aparece {dato['cantidad']} veces)")
            
            # 3. Verificar estructura en tabla recurso_operativo
            print("\n3. ESTRUCTURA EN TABLA 'recurso_operativo':")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, 
                       CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'capired' 
                AND TABLE_NAME = 'recurso_operativo' 
                AND COLUMN_NAME = 'id_codigo_consumidor'
            """)
            
            campo_ro = cursor.fetchone()
            if campo_ro:
                print(f"  Nombre: {campo_ro['COLUMN_NAME']}")
                print(f"  Tipo: {campo_ro['DATA_TYPE']}")
                print(f"  Permite NULL: {campo_ro['IS_NULLABLE']}")
                print(f"  Valor por defecto: {campo_ro['COLUMN_DEFAULT']}")
                print(f"  Longitud máxima: {campo_ro['CHARACTER_MAXIMUM_LENGTH']}")
                print(f"  Precisión numérica: {campo_ro['NUMERIC_PRECISION']}")
                print(f"  Escala numérica: {campo_ro['NUMERIC_SCALE']}")
            
            # 4. Verificar algunos valores de recurso_operativo
            print("\n4. VALORES EN 'recurso_operativo' (primeros 5):")
            cursor.execute("""
                SELECT id_codigo_consumidor, nombre
                FROM recurso_operativo 
                ORDER BY id_codigo_consumidor
                LIMIT 5
            """)
            
            datos_ro = cursor.fetchall()
            if datos_ro:
                for dato in datos_ro:
                    print(f"    {dato['id_codigo_consumidor']} - {dato['nombre']}")
            
            # 5. Verificar foreign key constraint
            print("\n5. FOREIGN KEY CONSTRAINT:")
            cursor.execute("""
                SELECT 
                    CONSTRAINT_NAME,
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = 'capired' 
                AND TABLE_NAME = 'cambios_dotacion'
                AND COLUMN_NAME = 'id_codigo_consumidor'
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            
            fk_info = cursor.fetchone()
            if fk_info:
                print(f"  Constraint: {fk_info['CONSTRAINT_NAME']}")
                print(f"  Columna: {fk_info['COLUMN_NAME']}")
                print(f"  Tabla referenciada: {fk_info['REFERENCED_TABLE_NAME']}")
                print(f"  Columna referenciada: {fk_info['REFERENCED_COLUMN_NAME']}")
            
            print("\n" + "=" * 80)
            print("ANÁLISIS COMPLETADO")
            print("=" * 80)
            
    except Error as e:
        print(f"Error de base de datos: {e}")
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada.")

if __name__ == "__main__":
    check_id_codigo_consumidor()