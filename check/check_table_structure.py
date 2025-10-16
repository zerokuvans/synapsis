#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error

def check_table_structures():
    """Verificar la estructura de las tablas MPA"""
    
    try:
        # Configuración de conexión (ajustar según tu configuración)
        connection = mysql.connector.connect(
            host='localhost',
            database='synapsis',
            user='root',
            password='',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar estructura de las tablas
            tables = ['mpa_soat', 'mpa_tecnico_mecanica', 'mpa_licencia_conducir']
            
            for table in tables:
                print(f"\n📋 Estructura de {table}:")
                print("=" * 50)
                
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                
                for column in columns:
                    field, type_info, null, key, default, extra = column
                    print(f"  {field}: {type_info} {'(NULL)' if null == 'YES' else '(NOT NULL)'}")
                
                # Verificar si existe tecnico_asignado
                cursor.execute(f"SHOW COLUMNS FROM {table} LIKE 'tecnico%'")
                tecnico_columns = cursor.fetchall()
                
                if tecnico_columns:
                    print(f"  🔍 Columnas relacionadas con técnico:")
                    for col in tecnico_columns:
                        print(f"    - {col[0]}: {col[1]}")
                else:
                    print(f"  ⚠️ No se encontraron columnas relacionadas con técnico")
            
    except Error as e:
        print(f"❌ Error de conexión a MySQL: {e}")
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n✅ Conexión cerrada")

if __name__ == "__main__":
    check_table_structures()