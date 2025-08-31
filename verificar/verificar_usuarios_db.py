#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar usuarios existentes en la base de datos
"""

import mysql.connector
from datetime import datetime

def verificar_usuarios():
    """Verificar usuarios existentes en la base de datos"""
    
    print("=== VERIFICACIÓN DE USUARIOS EN LA BASE DE DATOS ===")
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
        
        # Verificar si existe la tabla usuarios
        cursor.execute("SHOW TABLES LIKE 'usuarios'")
        tabla_usuarios = cursor.fetchone()
        
        if tabla_usuarios:
            print("✅ Tabla 'usuarios' encontrada")
            
            # Obtener estructura de la tabla usuarios
            cursor.execute("DESCRIBE usuarios")
            estructura = cursor.fetchall()
            
            print("\n=== ESTRUCTURA DE LA TABLA USUARIOS ===")
            for campo in estructura:
                print(f"- {campo['Field']}: {campo['Type']} {'(NULL)' if campo['Null'] == 'YES' else '(NOT NULL)'}")
            
            # Contar total de usuarios
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            total_usuarios = cursor.fetchone()['total']
            print(f"\n📊 Total de usuarios: {total_usuarios}")
            
            if total_usuarios > 0:
                # Obtener usuarios con rol administrativo
                cursor.execute("""
                    SELECT username, rol, activo 
                    FROM usuarios 
                    WHERE rol = 'administrativo' 
                    ORDER BY username
                """)
                admins = cursor.fetchall()
                
                print(f"\n=== USUARIOS ADMINISTRATIVOS ({len(admins)}) ===")
                if admins:
                    for admin in admins:
                        estado = "✅ Activo" if admin['activo'] else "❌ Inactivo"
                        print(f"- {admin['username']} ({estado})")
                else:
                    print("⚠️  No se encontraron usuarios administrativos")
                
                # Obtener todos los roles disponibles
                cursor.execute("SELECT DISTINCT rol FROM usuarios ORDER BY rol")
                roles = cursor.fetchall()
                
                print(f"\n=== ROLES DISPONIBLES ({len(roles)}) ===")
                for rol in roles:
                    cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE rol = %s", (rol['rol'],))
                    total_rol = cursor.fetchone()['total']
                    print(f"- {rol['rol']}: {total_rol} usuarios")
                
                # Mostrar algunos usuarios de ejemplo
                cursor.execute("""
                    SELECT username, rol, activo 
                    FROM usuarios 
                    WHERE activo = 1
                    ORDER BY username 
                    LIMIT 10
                """)
                usuarios_activos = cursor.fetchall()
                
                print(f"\n=== PRIMEROS 10 USUARIOS ACTIVOS ===")
                for usuario in usuarios_activos:
                    print(f"- {usuario['username']} (rol: {usuario['rol']})")
                    
        else:
            print("❌ Tabla 'usuarios' no encontrada")
            
            # Buscar otras tablas que puedan contener usuarios
            cursor.execute("SHOW TABLES")
            tablas = cursor.fetchall()
            
            print("\n=== TABLAS DISPONIBLES ===")
            tablas_usuario = []
            for tabla in tablas:
                nombre_tabla = list(tabla.values())[0]
                print(f"- {nombre_tabla}")
                if 'user' in nombre_tabla.lower() or 'usuario' in nombre_tabla.lower():
                    tablas_usuario.append(nombre_tabla)
            
            if tablas_usuario:
                print(f"\n=== TABLAS RELACIONADAS CON USUARIOS ===")
                for tabla in tablas_usuario:
                    print(f"\n--- Estructura de {tabla} ---")
                    cursor.execute(f"DESCRIBE {tabla}")
                    estructura = cursor.fetchall()
                    for campo in estructura:
                        print(f"  - {campo['Field']}: {campo['Type']}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error al verificar usuarios: {e}")
        import traceback
        traceback.print_exc()

def crear_usuario_admin_temporal():
    """Crear un usuario administrativo temporal para pruebas"""
    
    print("\n=== CREACIÓN DE USUARIO ADMINISTRATIVO TEMPORAL ===")
    
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
        
        # Verificar si ya existe el usuario test_admin
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'test_admin'")
        existe = cursor.fetchone()[0]
        
        if existe > 0:
            print("✅ Usuario 'test_admin' ya existe")
        else:
            # Crear hash de la contraseña
            password = "admin123"
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Insertar usuario temporal
            cursor.execute("""
                INSERT INTO usuarios (username, password, rol, activo, fecha_creacion)
                VALUES (%s, %s, %s, %s, NOW())
            """, ('test_admin', password_hash.decode('utf-8'), 'administrativo', 1))
            
            connection.commit()
            print("✅ Usuario 'test_admin' creado exitosamente")
            print("   Username: test_admin")
            print("   Password: admin123")
            print("   Rol: administrativo")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_usuarios()
    crear_usuario_admin_temporal()