#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import sys

def check_user():
    try:
        # Usar la misma configuración que main.py
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = connection.cursor()
        
        # Verificar si el usuario 80833959 existe
        cursor.execute("""
            SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, cargo, carpeta 
            FROM recurso_operativo 
            WHERE recurso_operativo_cedula = %s
        """, ('80833959',))
        
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Usuario encontrado:")
            print(f"   ID: {result['id_codigo_consumidor']}")
            print(f"   Cédula: {result['recurso_operativo_cedula']}")
            print(f"   Nombre: {result['nombre']}")
            print(f"   Cargo: {result['cargo']}")
            print(f"   Carpeta: {result['carpeta']}")
        else:
            print("❌ Usuario 80833959 NO encontrado en recurso_operativo")
            
            # Mostrar algunos usuarios existentes para referencia
            print("\n📋 Usuarios existentes (primeros 10):")
            cursor.execute("""
                SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, cargo 
                FROM recurso_operativo 
                ORDER BY id_codigo_consumidor 
                LIMIT 10
            """)
            
            users = cursor.fetchall()
            for user in users:
                cedula = user['recurso_operativo_cedula'] or 'N/A'
                print(f"   ID:{user['id_codigo_consumidor']} Cédula:{cedula} - {user['nombre']} ({user['cargo']})")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_user()