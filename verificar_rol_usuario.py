#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar el rol del usuario de prueba
"""

import mysql.connector

def verificar_rol_usuario():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = conn.cursor(dictionary=True)
        
        # Verificar el usuario de prueba
        cursor.execute("""
            SELECT 
                ro.recurso_operativo_cedula,
                ro.nombre,
                ro.id_roles,
                ro.estado
            FROM recurso_operativo ro
            WHERE ro.recurso_operativo_cedula = '12345678'
        """)
        
        usuario = cursor.fetchone()
        
        if usuario:
            print(f"Usuario encontrado:")
            print(f"  Cédula: {usuario['recurso_operativo_cedula']}")
            print(f"  Nombre: {usuario['nombre']}")
            print(f"  ID Rol: {usuario['id_roles']}")
            print(f"  Estado: {usuario['estado']}")
            
            # Verificar qué roles existen
            cursor.execute("SELECT * FROM roles")
            roles = cursor.fetchall()
            
            print("\nRoles disponibles en el sistema:")
            for rol in roles:
                print(f"  ID: {rol['id']}, Nombre: {rol['nombre']}")
            
            # Verificar el mapeo ROLES en el código
            print("\nMapeo ROLES esperado en el código:")
            print("  1: 'administrativo'")
            print("  2: 'logistica'")
            print("  3: 'operativo'")
            
            # Actualizar el usuario para que tenga rol de logística (id=2)
            if usuario['id_roles'] != 2:
                print(f"\nActualizando rol del usuario de {usuario['id_roles']} a 2 (logística)...")
                cursor.execute(
                    "UPDATE recurso_operativo SET id_roles = 2 WHERE recurso_operativo_cedula = '12345678'"
                )
                conn.commit()
                print("✅ Rol actualizado exitosamente")
            else:
                print("\n✅ El usuario ya tiene el rol correcto (logística)")
        else:
            print("❌ Usuario de prueba no encontrado")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verificar_rol_usuario()