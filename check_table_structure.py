#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la estructura de las tablas de vencimientos
"""

import mysql.connector

def conectar_bd():
    """Conectar a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        return connection
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        return None

def mostrar_estructura_tabla(cursor, tabla):
    """Mostrar la estructura de una tabla"""
    print(f"\n📋 ESTRUCTURA DE TABLA: {tabla}")
    print("="*50)
    
    cursor.execute(f"DESCRIBE {tabla}")
    columnas = cursor.fetchall()
    
    for columna in columnas:
        field, type_, null, key, default, extra = columna
        print(f"   {field} - {type_} - NULL: {null} - KEY: {key}")

def main():
    """Función principal"""
    print("🔍 VERIFICANDO ESTRUCTURA DE TABLAS")
    print("="*50)
    
    # Conectar a BD
    connection = conectar_bd()
    if not connection:
        return
    
    cursor = connection.cursor()
    
    try:
        # Verificar estructura de cada tabla
        mostrar_estructura_tabla(cursor, "mpa_soat")
        mostrar_estructura_tabla(cursor, "mpa_tecnico_mecanica")
        mostrar_estructura_tabla(cursor, "mpa_licencia_conducir")
        mostrar_estructura_tabla(cursor, "recurso_operativo")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()