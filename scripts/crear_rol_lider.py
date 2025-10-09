#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar y crear el rol 'lider' en la base de datos
"""

import mysql.connector
from mysql.connector import Error

def crear_rol_lider():
    """Verificar y crear el rol 'lider' en la base de datos"""
    try:
        print("=== VERIFICANDO Y CREANDO ROL LÍDER ===")
        
        # Configuración de conexión a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # 1. Verificar si existe una tabla de roles
            print("1. Verificando estructura de roles...")
            cursor.execute("SHOW TABLES LIKE 'roles'")
            tabla_roles = cursor.fetchone()
            
            if tabla_roles:
                print("   ✅ Tabla 'roles' encontrada")
                
                # Verificar si el rol 'lider' ya existe
                cursor.execute("SELECT * FROM roles WHERE id_roles = 7 OR nombre_rol = 'lider'")
                rol_existente = cursor.fetchone()
                
                if rol_existente:
                    print(f"   ✅ Rol 'lider' ya existe: {rol_existente}")
                else:
                    print("   ⚠️  Rol 'lider' no existe, creándolo...")
                    cursor.execute("""
                        INSERT INTO roles (id_roles, nombre_rol, descripcion) 
                        VALUES (7, 'lider', 'Rol de líder con acceso al módulo de liderazgo')
                    """)
                    connection.commit()
                    print("   ✅ Rol 'lider' creado exitosamente")
                    
            else:
                print("   ⚠️  Tabla 'roles' no encontrada")
                print("   📝 Creando tabla 'roles'...")
                
                # Crear tabla roles
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS roles (
                        id_roles INT PRIMARY KEY,
                        nombre_rol VARCHAR(50) NOT NULL,
                        descripcion TEXT
                    )
                """)
                
                # Insertar roles básicos
                roles_basicos = [
                    (1, 'administrativo', 'Rol administrativo con acceso completo'),
                    (2, 'tecnicos', 'Rol para técnicos'),
                    (3, 'operativo', 'Rol operativo'),
                    (4, 'contabilidad', 'Rol de contabilidad'),
                    (5, 'logistica', 'Rol de logística'),
                    (6, 'analista', 'Rol de analista'),
                    (7, 'lider', 'Rol de líder con acceso al módulo de liderazgo')
                ]
                
                cursor.executemany("""
                    INSERT IGNORE INTO roles (id_roles, nombre_rol, descripcion) 
                    VALUES (%s, %s, %s)
                """, roles_basicos)
                
                connection.commit()
                print("   ✅ Tabla 'roles' y roles básicos creados exitosamente")
            
            # 2. Verificar roles actuales
            print("\n2. Roles disponibles en la base de datos:")
            cursor.execute("SELECT * FROM roles ORDER BY id_roles")
            roles = cursor.fetchall()
            
            for rol in roles:
                print(f"   🎭 ID: {rol['id_roles']} - Nombre: {rol['nombre_rol']} - Descripción: {rol.get('descripcion', 'N/A')}")
            
            # 3. Verificar usuarios con rol de líder
            print("\n3. Verificando usuarios con rol de líder...")
            cursor.execute("""
                SELECT recurso_operativo_cedula, nombre, estado 
                FROM recurso_operativo 
                WHERE id_roles = 7
            """)
            usuarios_lider = cursor.fetchall()
            
            if usuarios_lider:
                print(f"   👥 Encontrados {len(usuarios_lider)} usuarios con rol de líder:")
                for usuario in usuarios_lider:
                    print(f"      - Cédula: {usuario['recurso_operativo_cedula']}, Nombre: {usuario['nombre']}, Estado: {usuario['estado']}")
            else:
                print("   📝 No hay usuarios con rol de líder asignado aún")
                print("   💡 Puedes asignar este