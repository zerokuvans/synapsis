#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import sys

def check_table_structure():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = connection.cursor()
        
        print("📋 Estructura de la tabla recurso_operativo:")
        print("=" * 50)
        
        # Describir la tabla
        cursor.execute("DESCRIBE recurso_operativo")
        columns = cursor.fetchall()
        
        for column in columns:
            print(f"Columna: {column['Field']}")
            print(f"  Tipo: {column['Type']}")
            print(f"  Null: {column['Null']}")
            print(f"  Key: {column['Key']}")
            print(f"  Default: {column['Default']}")
            print(f"  Extra: {column['Extra']}")
            print("-" * 30)
        
        print("\n📊 Primeros 3 registros:")
        print("=" * 50)
        
        cursor.execute("SELECT * FROM recurso_operativo LIMIT 3")
        records = cursor.fetchall()
        
        for i, record in enumerate(records, 1):
            print(f"\nRegistro {i}:")
            for key, value in record.items():
                print(f"  {key}: {value}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar la estructura: {e}")
        return False

if __name__ == "__main__":
    check_table_structure()