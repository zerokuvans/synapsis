#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
import os

def ejecutar_script_sql():
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        cursor = conn.cursor()
        
        # Leer el archivo SQL
        with open('sql/crear_tabla_ingresos_dotaciones.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Dividir y ejecutar cada statement
        statements = sql_script.split(';')
        for statement in statements:
            if statement.strip() and not statement.strip().startswith('--'):
                try:
                    cursor.execute(statement)
                    # Si es una consulta SELECT, leer los resultados
                    if statement.strip().upper().startswith('SELECT'):
                        results = cursor.fetchall()
                        for row in results:
                            print(row)
                    else:
                        conn.commit()
                    print(f"Ejecutado: {statement[:50]}...")
                except Exception as e:
                    print(f"Error en statement: {e}")
                    print(f"Statement: {statement[:100]}...")
        
        cursor.close()
        conn.close()
        print('Script SQL ejecutado exitosamente')
        
    except Exception as e:
        print(f"Error al ejecutar script SQL: {e}")

if __name__ == "__main__":
    ejecutar_script_sql()