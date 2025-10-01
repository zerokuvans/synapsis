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

def verificar_tablas_stock():
    """Verificar qué tablas de stock existen"""
    connection = conectar_db()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print("=== VERIFICACIÓN DE TABLAS DE STOCK ===\n")
        
        # 1. Listar todas las tablas que contienen 'stock'
        print("1. TABLAS QUE CONTIENEN 'STOCK':")
        query_tablas = "SHOW TABLES LIKE '%stock%'"
        cursor.execute(query_tablas)
        tablas_stock = cursor.fetchall()
        
        if tablas_stock:
            for tabla in tablas_stock:
                tabla_nombre = list(tabla.values())[0]
                print(f"  - {tabla_nombre}")
        else:
            print("  No se encontraron tablas que contengan 'stock'")
        
        print("\n" + "="*50)
        
        # 2. Listar todas las tablas que contienen 'dotacion'
        print("\n2. TABLAS QUE CONTIENEN 'DOTACION':")
        query_dotacion = "SHOW TABLES LIKE '%dotacion%'"
        cursor.execute(query_dotacion)
        tablas_dotacion = cursor.fetchall()
        
        if tablas_dotacion:
            for tabla in tablas_dotacion:
                tabla_nombre = list(tabla.values())[0]
                print(f"  - {tabla_nombre}")
        else:
            print("  No se encontraron tablas que contengan 'dotacion'")
        
        print("\n" + "="*50)
        
        # 3. Listar todas las tablas
        print("\n3. TODAS LAS TABLAS EN LA BASE DE DATOS:")
        query_todas = "SHOW TABLES"
        cursor.execute(query_todas)
        todas_tablas = cursor.fetchall()
        
        if todas_tablas:
            for tabla in todas_tablas:
                tabla_nombre = list(tabla.values())[0]
                print(f"  - {tabla_nombre}")
        
        print("\n" + "="*50)
        
        # 4. Si existe una tabla de stock, verificar su estructura
        if tablas_stock:
            primera_tabla = list(tablas_stock[0].values())[0]
            print(f"\n4. ESTRUCTURA DE LA TABLA '{primera_tabla}':")
            query_estructura = f"DESCRIBE {primera_tabla}"
            cursor.execute(query_estructura)
            estructura = cursor.fetchall()
            
            for campo in estructura:
                print(f"  - {campo['Field']} | {campo['Type']} | {campo['Null']} | {campo['Key']} | {campo['Default']}")
        
        # 5. Buscar datos de camiseta polo en cualquier tabla que pueda contenerlos
        print("\n" + "="*50)
        print("\n5. BUSCANDO DATOS DE CAMISETA POLO EN TABLAS RELEVANTES:")
        
        tablas_relevantes = []
        for tabla in todas_tablas:
            tabla_nombre = list(tabla.values())[0]
            if any(keyword in tabla_nombre.lower() for keyword in ['stock', 'dotacion', 'elemento', 'inventario']):
                tablas_relevantes.append(tabla_nombre)
        
        for tabla_nombre in tablas_relevantes:
            try:
                print(f"\n  Verificando tabla: {tabla_nombre}")
                # Primero verificar la estructura
                cursor.execute(f"DESCRIBE {tabla_nombre}")
                campos = cursor.fetchall()
                campos_nombres = [campo['Field'] for campo in campos]
                
                # Buscar campos que puedan contener información de elementos
                campos_elemento = [campo for campo in campos_nombres if any(keyword in campo.lower() for keyword in ['elemento', 'item', 'producto', 'nombre'])]
                
                if campos_elemento:
                    campo_elemento = campos_elemento[0]
                    query_buscar = f"SELECT * FROM {tabla_nombre} WHERE {campo_elemento} LIKE '%camiseta%polo%' LIMIT 5"
                    cursor.execute(query_buscar)
                    resultados = cursor.fetchall()
                    
                    if resultados:
                        print(f"    ✓ Encontrados {len(resultados)} registros con 'camiseta polo'")
                        for resultado in resultados:
                            print(f"      {resultado}")
                    else:
                        print(f"    - No se encontraron registros con 'camiseta polo'")
                else:
                    print(f"    - No se encontraron campos de elemento en esta tabla")
                    
            except Error as e:
                print(f"    Error al consultar {tabla_nombre}: {e}")
        
    except Error as e:
        print(f"Error al ejecutar consulta: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    verificar_tablas_stock()