#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la estructura de la tabla dotaciones
"""

import mysql.connector

def check_dotaciones_structure():
    """Verificar la estructura de la tabla dotaciones"""
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = connection.cursor()
        
        print("=== ESTRUCTURA DE LA TABLA DOTACIONES ===")
        
        cursor.execute('DESCRIBE dotaciones')
        columns = cursor.fetchall()
        
        print("\nColumnas de la tabla dotaciones:")
        for col in columns:
            print(f"  {col[0]} - {col[1]} - {col[2]} - {col[3]}")
        
        print("\n=== VERIFICANDO REGISTROS EXISTENTES ===")
        
        cursor.execute('SELECT COUNT(*) as total FROM dotaciones')
        total = cursor.fetchone()[0]
        print(f"\nTotal de registros en dotaciones: {total}")
        
        if total > 0:
            cursor.execute('SELECT * FROM dotaciones LIMIT 3')
            sample_records = cursor.fetchall()
            print("\nEjemplos de registros:")
            for record in sample_records:
                print(f"  {record}")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    check_dotaciones_structure()