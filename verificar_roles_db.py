#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar los roles en la base de datos
y encontrar usuarios con rol de logística
"""

import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'port': 3306
}

def verificar_roles():
    """Verificar los roles disponibles en la base de datos"""
    try:
        print("=== VERIFICANDO ROLES EN LA BASE DE DATOS ===")
        
        # Conectar a la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # 1. Verificar si existe tabla de roles
        print("\n1. Verificando tablas relacionadas con roles...")
        cursor.execute("SHOW TABLES LIKE '%rol%'")
        tablas_roles = cursor.fetchall()
        
        if tablas_roles:
            print("✅ Tablas de roles encontradas:")
            for tabla in tablas_roles:
                print(f"   - {list(tabla.values())[0]}")
        else:
            print("❌ No se encontraron tablas específicas de roles")
        
        # 2. Verificar estructura de recurso_operativo
        print("\n2. Verificando estructura de recurso_operativo...")
        cursor.execute("DESCRIBE recurso_operativo")
        columnas = cursor.fetchall()
        
        print("Columnas en recurso_operativo:")
        for columna in columnas:
            if 'rol' in columna['Field'].lower():
                print(f"   🎭 {columna['Field']}: {columna['Type']} - {columna['Extra']}")
            else:
                print(f"   - {columna['Field']}: {columna['Type']}")
        
        # 3. Verificar valores únicos de id_roles
        print("\n3. Verificando valores únicos de id_roles...")
        cursor.execute("""
            SELECT DISTINCT id_roles, COUNT(*) as cantidad
            FROM recurso_operativo 
            GROUP BY id_roles 
            ORDER BY id_roles
        """)
        
        roles_unicos = cursor.fetchall()
        print("Roles encontrados en recurso_operativo:")
        for rol in roles_unicos:
            print(f"   🎭 ID Rol: {rol['id_roles']} - Cantidad de usuarios: {rol['cantidad']}")
        
        # 4. Buscar tabla de roles específica
        print("\n4. Buscando tabla de definición de roles...")
        cursor.execute("SHOW TABLES")
        todas_tablas = cursor.fetchall()
        
        tablas_posibles = ['roles', 'rol', 'tipo_rol', 'tipos_roles', 'user_roles']
        tabla_roles_encontrada = None
        
        for tabla in todas_tablas:
            nombre_tabla = list(tabla.values())[0]
            if nombre_tabla.lower() in tablas_posibles:
                tabla_roles_encontrada = nombre_tabla
                break
        
        if tabla_roles_encontrada:
            print(f"✅ Tabla de roles encontrada: {tabla_roles_encontrada}")
            cursor.execute(f"SELECT * FROM {tabla_roles_encontrada}")
            definiciones_roles = cursor.fetchall()
            
            print("Definiciones de roles:")
            for rol_def in definiciones_roles:
                print(f"   🎭 {rol_def}")
        else:
            print("❌ No se encontró tabla específica de definición de roles")
        
        # 5. Mapeo manual basado en el código
        print("\n5. Mapeo de roles según el código de la aplicación:")
        ROLES = {
            '1': 'administrativo',
            '2': 'tecnicos',
            '3': 'operativo',
            '4': 'contabilidad',
            '5': 'logistica'
        }
        
        for id_rol, nombre_rol in ROLES.items():
            cursor.execute("""
                SELECT COUNT(*) as cantidad, 
                       GROUP_CONCAT(CONCAT(nombre, ' (', recurso_operativo_cedula, ')') SEPARATOR ', ') as usuarios
                FROM recurso_operativo 
                WHERE id_roles = %s AND estado = 'Activo'
            """, (id_rol,))
            
            resultado = cursor.fetchone()
            print(f"   🎭 ID {id_rol} ({nombre_rol}): {resultado['cantidad']} usuarios activos")
            if resultado['cantidad'] > 0 and resultado['usuarios']:
                usuarios_lista = resultado['usuarios'].split(', ')
                for i, usuario in enumerate(usuarios_lista[:3]):  # Mostrar solo los primeros 3
                    print(f"      👤 {usuario}")
                if len(usuarios_lista) > 3:
                    print(f"      ... y {len(usuarios_lista) - 3} más")
        
        # 6. Buscar específicamente usuarios de logística (rol 5)
        print("\n6. Usuarios con rol de logística (ID 5):")
        cursor.execute("""
            SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, estado
            FROM recurso_operativo 
            WHERE id_roles = 5
            ORDER BY estado DESC, nombre
        """)
        
        usuarios_logistica = cursor.fetchall()
        
        if usuarios_logistica:
            print(f"✅ {len(usuarios_logistica)} usuarios con rol de logística encontrados:")
            for usuario in usuarios_logistica:
                estado_emoji = "✅" if usuario['estado'] == 'Activo' else "❌"
                print(f"   {estado_emoji} {usuario['nombre']} (Cédula: {usuario['recurso_operativo_cedula']}) - {usuario['estado']}")
        else:
            print("❌ No se encontraron usuarios con rol de logística (ID 5)")
        
        cursor.close()
        connection.close()
        print("\n✅ Verificación completada")
        
    except Error as e:
        print(f"❌ Error de MySQL: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    verificar_roles()