#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la estructura de la tabla roles
"""

import mysql.connector

def verificar_estructura_roles():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = conn.cursor(dictionary=True)
        
        # Verificar estructura de la tabla roles
        cursor.execute("DESCRIBE roles")
        estructura = cursor.fetchall()
        
        print("Estructura de la tabla 'roles':")
        for columna in estructura:
            print(f"  {columna}")
        
        # Obtener todos los roles
        cursor.execute("SELECT * FROM roles")
        roles = cursor.fetchall()
        
        print("\nContenido de la tabla 'roles':")
        for rol in roles:
            print(f"  {rol}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verificar_estructura_roles()