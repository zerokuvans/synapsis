#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector

def check_users():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT recurso_operativo_cedula, nombre, estado FROM recurso_operativo WHERE estado = 'Activo' LIMIT 5")
        users = cursor.fetchall()
        
        print("Usuarios activos en la base de datos:")
        for user in users:
            print(f"  - Cédula: {user['recurso_operativo_cedula']}, Nombre: {user['nombre']}, Estado: {user['estado']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users()