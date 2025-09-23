#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar las tablas relacionadas con auditoría
"""

import mysql.connector

def verificar_tablas_auditoria():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = conn.cursor()
        
        # Buscar todas las tablas que contengan 'auditoria' o 'estado'
        cursor.execute("SHOW TABLES")
        todas_tablas = cursor.fetchall()
        
        print("Todas las tablas en la base de datos:")
        tablas_auditoria = []
        tablas_estado = []
        
        for tabla in todas_tablas:
            tabla_nombre = tabla[0]
            print(f"  {tabla_nombre}")
            
            if 'auditoria' in tabla_nombre.lower():
                tablas_auditoria.append(tabla_nombre)
            if 'estado' in tabla_nombre.lower():
                tablas_estado.append(tabla_nombre)
        
        print(f"\nTablas relacionadas con 'auditoria':")
        for tabla in tablas_auditoria:
            print(f"  {tabla}")
            
        print(f"\nTablas relacionadas con 'estado':")
        for tabla in tablas_estado:
            print(f"  {tabla}")
        
        # Verificar si existe alguna tabla similar
        if tablas_auditoria:
            print(f"\nEstructura de las tablas de auditoría encontradas:")
            for tabla in tablas_auditoria:
                print(f"\n--- Estructura de {tabla} ---")
                cursor.execute(f"DESCRIBE {tabla}")
                estructura = cursor.fetchall()
                for columna in estructura:
                    print(f"  {columna}")
        
        if tablas_estado:
            print(f"\nEstructura de las tablas de estado encontradas:")
            for tabla in tablas_estado:
                print(f"\n--- Estructura de {tabla} ---")
                cursor.execute(f"DESCRIBE {tabla}")
                estructura = cursor.fetchall()
                for columna in estructura:
                    print(f"  {columna}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verificar_tablas_auditoria()