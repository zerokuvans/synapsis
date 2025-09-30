#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar/actualizar el rol SSTT (Seguridad y Salud en el Trabajo)
"""

import mysql.connector
from datetime import datetime

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def actualizar_rol_sstt():
    """Agrega o actualiza el rol SSTT con la descripción correcta"""
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=== CONFIGURACIÓN DEL ROL SSTT ===")
        print("    (Seguridad y Salud en el Trabajo)")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        print("✅ Conectado a la base de datos MySQL")
        
        # Verificar estructura de la tabla roles
        print("\n🔍 Verificando estructura de la tabla 'roles'...")
        cursor.execute("DESCRIBE roles")
        estructura = cursor.fetchall()
        
        print("   Estructura de la tabla 'roles':")
        for campo in estructura:
            print(f"      - {campo[0]}: {campo[1]}")
        
        # Verificar si ya existe el rol SSTT
        print("\n🔍 Verificando si existe el rol SSTT...")
        cursor.execute("SELECT * FROM roles WHERE nombre_rol = 'sstt' OR nombre_rol = 'SSTT'")
        rol_existente = cursor.fetchone()
        
        if rol_existente:
            print(f"   ⚠️  Rol SSTT encontrado: {rol_existente}")
            print("   ℹ️  El rol ya existe, no es necesario actualizar")
        else:
            print("   ℹ️  Rol SSTT no encontrado, creando nuevo...")
            
            # Insertar el nuevo rol (solo nombre_rol ya que no hay descripcion_rol)
            cursor.execute("""
                INSERT INTO roles (nombre_rol) 
                VALUES ('sstt')
            """)
            print("   ✅ Rol SSTT creado exitosamente")
        
        # Confirmar cambios
        conn.commit()
        
        # Mostrar todos los roles actuales
        print("\n📋 Roles disponibles en el sistema:")
        cursor.execute("SELECT id_roles, nombre_rol FROM roles ORDER BY id_roles")
        roles = cursor.fetchall()
        
        for rol in roles:
            print(f"   - ID: {rol[0]} | Nombre: {rol[1]}")
        
        # Verificar el rol SSTT específicamente
        print("\n🎯 Verificación del rol SSTT:")
        cursor.execute("SELECT * FROM roles WHERE nombre_rol IN ('sstt', 'SSTT')")
        rol_sstt = cursor.fetchone()
        
        if rol_sstt:
            print(f"   ✅ Rol SSTT configurado correctamente:")
            print(f"      - ID: {rol_sstt[0]}")
            print(f"      - Nombre: {rol_sstt[1]}")
        else:
            print("   ❌ Error: No se pudo configurar el rol SSTT")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 ¡Configuración del rol SSTT completada exitosamente!")
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    actualizar_rol_sstt()