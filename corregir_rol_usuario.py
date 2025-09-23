#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir el rol del usuario de prueba
"""

import mysql.connector

def corregir_rol_usuario():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = conn.cursor(dictionary=True)
        
        # Verificar el usuario actual
        cursor.execute("""
            SELECT 
                ro.recurso_operativo_cedula,
                ro.nombre,
                ro.id_roles,
                r.nombre_rol
            FROM recurso_operativo ro
            LEFT JOIN roles r ON ro.id_roles = r.id_roles
            WHERE ro.recurso_operativo_cedula = '12345678'
        """)
        
        usuario = cursor.fetchone()
        
        if usuario:
            print(f"Usuario actual:")
            print(f"  Cédula: {usuario['recurso_operativo_cedula']}")
            print(f"  Nombre: {usuario['nombre']}")
            print(f"  ID Rol: {usuario['id_roles']}")
            print(f"  Nombre Rol: {usuario['nombre_rol']}")
            
            # Actualizar el usuario para que tenga rol de logística (id=5)
            print(f"\nActualizando rol del usuario de {usuario['id_roles']} ({usuario['nombre_rol']}) a 5 (logística)...")
            cursor.execute(
                "UPDATE recurso_operativo SET id_roles = 5 WHERE recurso_operativo_cedula = '12345678'"
            )
            conn.commit()
            print("✅ Rol actualizado exitosamente")
            
            # Verificar el cambio
            cursor.execute("""
                SELECT 
                    ro.recurso_operativo_cedula,
                    ro.id_roles,
                    r.nombre_rol
                FROM recurso_operativo ro
                LEFT JOIN roles r ON ro.id_roles = r.id_roles
                WHERE ro.recurso_operativo_cedula = '12345678'
            """)
            
            usuario_actualizado = cursor.fetchone()
            print(f"\nUsuario después de la actualización:")
            print(f"  Cédula: {usuario_actualizado['recurso_operativo_cedula']}")
            print(f"  ID Rol: {usuario_actualizado['id_roles']}")
            print(f"  Nombre Rol: {usuario_actualizado['nombre_rol']}")
            
        else:
            print("❌ Usuario de prueba no encontrado")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    corregir_rol_usuario()