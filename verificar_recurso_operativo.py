#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la tabla recurso_operativo y usuarios disponibles
"""

import mysql.connector
from datetime import datetime

def verificar_recurso_operativo():
    """Verificar la estructura y datos de la tabla recurso_operativo"""
    
    print("=== VERIFICACIÓN DE TABLA RECURSO_OPERATIVO ===")
    print(f"Fecha de verificación: {datetime.now()}")
    print()
    
    try:
        # Configuración de la base de datos
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '732137A031E4b@',
            'database': 'capired'
        }
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Verificar si existe la tabla recurso_operativo
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        tabla_existe = cursor.fetchone()
        
        if tabla_existe:
            print("✅ Tabla 'recurso_operativo' encontrada")
            
            # Obtener estructura de la tabla
            cursor.execute("DESCRIBE recurso_operativo")
            estructura = cursor.fetchall()
            
            print("\n=== ESTRUCTURA DE LA TABLA RECURSO_OPERATIVO ===")
            for campo in estructura:
                print(f"- {campo['Field']}: {campo['Type']} {'(NULL)' if campo['Null'] == 'YES' else '(NOT NULL)'} {campo.get('Extra', '')}")
            
            # Contar total de usuarios
            cursor.execute("SELECT COUNT(*) as total FROM recurso_operativo")
            total_usuarios = cursor.fetchone()['total']
            print(f"\n📊 Total de usuarios: {total_usuarios}")
            
            if total_usuarios > 0:
                # Obtener usuarios activos
                cursor.execute("""
                    SELECT 
                        id_codigo_consumidor,
                        recurso_operativo_cedula,
                        nombre,
                        id_roles,
                        estado
                    FROM recurso_operativo 
                    WHERE estado = 'Activo'
                    ORDER BY nombre
                    LIMIT 10
                """)
                usuarios_activos = cursor.fetchall()
                
                print(f"\n=== USUARIOS ACTIVOS ({len(usuarios_activos)}) ===")
                for usuario in usuarios_activos:
                    print(f"- Cédula: {usuario['recurso_operativo_cedula']} | Nombre: {usuario['nombre']} | Rol ID: {usuario['id_roles']}")
                
                # Verificar tabla de roles
                cursor.execute("SHOW TABLES LIKE 'roles'")
                tabla_roles = cursor.fetchone()
                
                if tabla_roles:
                    print("\n=== ROLES DISPONIBLES ===")
                    cursor.execute("SELECT * FROM roles ORDER BY id_roles")
                    roles = cursor.fetchall()
                    
                    for rol in roles:
                        print(f"- ID {rol['id_roles']}: {rol.get('nombre_rol', 'Sin nombre')}")
                    
                    # Contar usuarios por rol
                    print("\n=== USUARIOS POR ROL ===")
                    for rol in roles:
                        cursor.execute("""
                            SELECT COUNT(*) as total 
                            FROM recurso_operativo 
                            WHERE id_roles = %s AND estado = 'Activo'
                        """, (rol['id_roles'],))
                        total_rol = cursor.fetchone()['total']
                        nombre_rol = rol.get('nombre_rol', f'Rol {rol["id_roles"]}')
                        print(f"- {nombre_rol}: {total_rol} usuarios activos")
                else:
                    print("⚠️  Tabla 'roles' no encontrada")
                
                # Buscar usuarios administrativos (asumiendo que rol 1 es administrativo)
                cursor.execute("""
                    SELECT 
                        recurso_operativo_cedula,
                        nombre,
                        id_roles
                    FROM recurso_operativo 
                    WHERE estado = 'Activo' AND id_roles IN (1, 2, 3)
                    ORDER BY id_roles, nombre
                    LIMIT 5
                """)
                posibles_admins = cursor.fetchall()
                
                print(f"\n=== POSIBLES USUARIOS ADMINISTRATIVOS ===")
                for usuario in posibles_admins:
                    print(f"- Cédula: {usuario['recurso_operativo_cedula']} | Nombre: {usuario['nombre']} | Rol: {usuario['id_roles']}")
                
                # Verificar si hay contraseñas válidas
                cursor.execute("""
                    SELECT 
                        recurso_operativo_cedula,
                        nombre,
                        CASE 
                            WHEN recurso_operativo_password IS NULL THEN 'NULL'
                            WHEN recurso_operativo_password = '' THEN 'VACÍO'
                            WHEN recurso_operativo_password LIKE '$2%' THEN 'HASH_BCRYPT'
                            ELSE 'TEXTO_PLANO'
                        END as tipo_password
                    FROM recurso_operativo 
                    WHERE estado = 'Activo'
                    ORDER BY tipo_password, nombre
                    LIMIT 10
                """)
                info_passwords = cursor.fetchall()
                
                print(f"\n=== INFORMACIÓN DE CONTRASEÑAS ===")
                for info in info_passwords:
                    print(f"- {info['nombre']} (Cédula: {info['recurso_operativo_cedula']}): {info['tipo_password']}")
                
        else:
            print("❌ Tabla 'recurso_operativo' no encontrada")
            
            # Mostrar todas las tablas disponibles
            cursor.execute("SHOW TABLES")
            tablas = cursor.fetchall()
            
            print("\n=== TODAS LAS TABLAS DISPONIBLES ===")
            for tabla in tablas:
                nombre_tabla = list(tabla.values())[0]
                print(f"- {nombre_tabla}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error al verificar recurso_operativo: {e}")
        import traceback
        traceback.print_exc()

def crear_usuario_test():
    """Crear un usuario de prueba con contraseña hasheada"""
    
    print("\n=== CREACIÓN DE USUARIO DE PRUEBA ===")
    
    try:
        import bcrypt
        
        # Configuración de la base de datos
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '732137A031E4b@',
            'database': 'capired'
        }
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Verificar si ya existe el usuario test
        cursor.execute("SELECT COUNT(*) FROM recurso_operativo WHERE recurso_operativo_cedula = '12345678'")
        existe = cursor.fetchone()[0]
        
        if existe > 0:
            print("✅ Usuario de prueba (cédula: 12345678) ya existe")
            
            # Actualizar la contraseña
            password = "admin123"
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            cursor.execute("""
                UPDATE recurso_operativo 
                SET recurso_operativo_password = %s, estado = 'Activo', id_roles = 1
                WHERE recurso_operativo_cedula = '12345678'
            """, (password_hash.decode('utf-8'),))
            
            connection.commit()
            print("✅ Contraseña actualizada para usuario de prueba")
            
        else:
            # Crear hash de la contraseña
            password = "admin123"
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Insertar usuario de prueba
            cursor.execute("""
                INSERT INTO recurso_operativo 
                (recurso_operativo_cedula, nombre, recurso_operativo_password, id_roles, estado)
                VALUES (%s, %s, %s, %s, %s)
            """, ('12345678', 'Usuario Prueba Admin', password_hash.decode('utf-8'), 1, 'Activo'))
            
            connection.commit()
            print("✅ Usuario de prueba creado exitosamente")
        
        print("\n📋 CREDENCIALES DE PRUEBA:")
        print("   Cédula: 12345678")
        print("   Contraseña: admin123")
        print("   Rol: 1 (Administrativo)")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error al crear usuario de prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_recurso_operativo()
    crear_usuario_test()