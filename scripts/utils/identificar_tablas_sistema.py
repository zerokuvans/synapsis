#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para identificar las tablas del sistema de dotaciones
"""

import mysql.connector
from mysql.connector import Error

def identificar_tablas_sistema():
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
            
            print("=== IDENTIFICACIÓN DE TABLAS DEL SISTEMA DE DOTACIONES ===")
            
            # Obtener todas las tablas
            cursor.execute("SHOW TABLES")
            todas_tablas = [tabla[0] for tabla in cursor.fetchall()]
            
            print(f"\nTotal de tablas en la base de datos: {len(todas_tablas)}")
            
            # Filtrar tablas relacionadas con dotaciones
            palabras_clave = ['dotacion', 'devolucion', 'cambio', 'historial', 'temporal']
            tablas_relacionadas = []
            
            for tabla in todas_tablas:
                for palabra in palabras_clave:
                    if palabra.lower() in tabla.lower():
                        tablas_relacionadas.append(tabla)
                        break
            
            print(f"\n📋 TABLAS RELACIONADAS CON EL SISTEMA ({len(tablas_relacionadas)}):")
            print("-" * 60)
            
            for tabla in tablas_relacionadas:
                print(f"  ✓ {tabla}")
                
                # Obtener información básica de cada tabla
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"    Registros: {count}")
                
                # Obtener estructura básica
                cursor.execute(f"DESCRIBE {tabla}")
                columnas = cursor.fetchall()
                print(f"    Columnas: {len(columnas)}")
                
                # Mostrar columnas principales
                columnas_principales = [col[0] for col in columnas[:5]]  # Primeras 5 columnas
                print(f"    Principales: {', '.join(columnas_principales)}")
                print()
            
            # Buscar tablas que podrían contener relaciones
            print("\n🔗 ANÁLISIS DE RELACIONES:")
            print("-" * 60)
            
            for tabla in tablas_relacionadas:
                cursor.execute(f"""
                    SELECT 
                        CONSTRAINT_NAME,
                        COLUMN_NAME,
                        REFERENCED_TABLE_NAME,
                        REFERENCED_COLUMN_NAME
                    FROM information_schema.KEY_COLUMN_USAGE 
                    WHERE table_schema = 'capired' 
                    AND table_name = '{tabla}' 
                    AND REFERENCED_TABLE_NAME IS NOT NULL
                """)
                
                relaciones = cursor.fetchall()
                
                if relaciones:
                    print(f"\n  📌 {tabla}:")
                    for rel in relaciones:
                        print(f"    {rel[1]} -> {rel[2]}.{rel[3]}")
                else:
                    print(f"\n  📌 {tabla}: Sin relaciones FK")
            
            # Verificar tablas que referencian a las principales
            print("\n\n📥 TABLAS QUE REFERENCIAN AL SISTEMA:")
            print("-" * 60)
            
            for tabla in tablas_relacionadas:
                cursor.execute(f"""
                    SELECT DISTINCT
                        table_name,
                        COLUMN_NAME,
                        REFERENCED_COLUMN_NAME
                    FROM information_schema.KEY_COLUMN_USAGE 
                    WHERE table_schema = 'capired' 
                    AND REFERENCED_TABLE_NAME = '{tabla}'
                """)
                
                referencias = cursor.fetchall()
                
                if referencias:
                    print(f"\n  📌 Tablas que referencian a {tabla}:")
                    for ref in referencias:
                        print(f"    {ref[0]}.{ref[1]} -> {ref[2]}")
            
            return tablas_relacionadas
            
    except Error as e:
        print(f"Error de base de datos: {e}")
        return []
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n✓ Conexión cerrada")

if __name__ == "__main__":
    tablas = identificar_tablas_sistema()
    
    if tablas:
        print(f"\n\n=== RESUMEN ===")
        print(f"Tablas identificadas para el truncate: {len(tablas)}")
        for i, tabla in enumerate(tablas, 1):
            print(f"{i}. {tabla}")
    else:
        print("\n❌ No se pudieron identificar las tablas del sistema")