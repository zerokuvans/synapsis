#!/usr/bin/env python3
"""
Script para verificar y corregir los roles MPA en la base de datos
"""

import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def get_db_connection():
    """Establece conexión con la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("✅ Conexión exitosa a la base de datos")
            return connection
    except Error as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return None

def check_roles_table(cursor):
    """Verifica la estructura de la tabla de roles"""
    try:
        cursor.execute("SHOW TABLES LIKE 'roles'")
        if cursor.fetchone():
            print("✅ Tabla 'roles' encontrada")
            cursor.execute("DESCRIBE roles")
            columns = cursor.fetchall()
            print("📋 Estructura de la tabla roles:")
            for column in columns:
                print(f"   - {column[0]}: {column[1]}")
            return True
        else:
            print("❌ Tabla 'roles' no encontrada")
            return False
    except Error as e:
        print(f"❌ Error al verificar tabla roles: {e}")
        return False

def check_user_roles_table(cursor):
    """Verifica la estructura de la tabla de user_roles"""
    try:
        cursor.execute("SHOW TABLES LIKE 'user_roles'")
        if cursor.fetchone():
            print("✅ Tabla 'user_roles' encontrada")
            cursor.execute("DESCRIBE user_roles")
            columns = cursor.fetchall()
            print("📋 Estructura de la tabla user_roles:")
            for column in columns:
                print(f"   - {column[0]}: {column[1]}")
            return True
        else:
            print("❌ Tabla 'user_roles' no encontrada")
            return False
    except Error as e:
        print(f"❌ Error al verificar tabla user_roles: {e}")
        return False

def check_mpa_role_exists(cursor):
    """Verifica si el rol 'mpa' existe"""
    try:
        cursor.execute("SELECT id, name FROM roles WHERE name = 'mpa'")
        role = cursor.fetchone()
        if role:
            print(f"✅ Rol 'mpa' encontrado con ID: {role[0]}")
            return role[0]
        else:
            print("❌ Rol 'mpa' no encontrado")
            return None
    except Error as e:
        print(f"❌ Error al verificar rol mpa: {e}")
        return None

def create_mpa_role(cursor, connection):
    """Crea el rol 'mpa' si no existe"""
    try:
        cursor.execute("INSERT INTO roles (name, description) VALUES ('mpa', 'Módulo de Parque Automotor')")
        connection.commit()
        role_id = cursor.lastrowid
        print(f"✅ Rol 'mpa' creado exitosamente con ID: {role_id}")
        return role_id
    except Error as e:
        print(f"❌ Error al crear rol mpa: {e}")
        return None

def check_administrativo_role(cursor):
    """Verifica si el rol 'administrativo' existe"""
    try:
        cursor.execute("SELECT id, name FROM roles WHERE name = 'administrativo'")
        role = cursor.fetchone()
        if role:
            print(f"✅ Rol 'administrativo' encontrado con ID: {role[0]}")
            return role[0]
        else:
            print("❌ Rol 'administrativo' no encontrado")
            return None
    except Error as e:
        print(f"❌ Error al verificar rol administrativo: {e}")
        return None

def get_current_user_info(cursor):
    """Obtiene información del usuario actual (asumiendo que hay un usuario logueado)"""
    try:
        # Primero verificamos qué usuarios existen
        cursor.execute("SELECT id, username, email FROM users LIMIT 5")
        users = cursor.fetchall()
        print("👥 Usuarios disponibles:")
        for user in users:
            print(f"   - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
        
        if users:
            # Tomamos el primer usuario para testing
            return users[0][0], users[0][1]
        return None, None
    except Error as e:
        print(f"❌ Error al obtener usuarios: {e}")
        return None, None

def check_user_roles(cursor, user_id):
    """Verifica los roles asignados a un usuario"""
    try:
        cursor.execute("""
            SELECT r.id, r.name 
            FROM roles r 
            JOIN user_roles ur ON r.id = ur.role_id 
            WHERE ur.user_id = %s
        """, (user_id,))
        roles = cursor.fetchall()
        if roles:
            print(f"✅ Roles del usuario {user_id}:")
            for role in roles:
                print(f"   - {role[1]} (ID: {role[0]})")
            return [role[1] for role in roles]
        else:
            print(f"❌ Usuario {user_id} no tiene roles asignados")
            return []
    except Error as e:
        print(f"❌ Error al verificar roles del usuario: {e}")
        return []

def assign_role_to_user(cursor, connection, user_id, role_id, role_name):
    """Asigna un rol a un usuario"""
    try:
        # Verificar si ya tiene el rol
        cursor.execute("SELECT 1 FROM user_roles WHERE user_id = %s AND role_id = %s", (user_id, role_id))
        if cursor.fetchone():
            print(f"ℹ️ Usuario {user_id} ya tiene el rol '{role_name}'")
            return True
        
        # Asignar el rol
        cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)", (user_id, role_id))
        connection.commit()
        print(f"✅ Rol '{role_name}' asignado exitosamente al usuario {user_id}")
        return True
    except Error as e:
        print(f"❌ Error al asignar rol: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 Verificando configuración de roles MPA...")
    print("=" * 50)
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # 1. Verificar estructura de tablas
        print("\n1️⃣ Verificando estructura de tablas...")
        if not check_roles_table(cursor):
            print("❌ No se puede continuar sin la tabla roles")
            return
        
        if not check_user_roles_table(cursor):
            print("❌ No se puede continuar sin la tabla user_roles")
            return
        
        # 2. Verificar rol MPA
        print("\n2️⃣ Verificando rol MPA...")
        mpa_role_id = check_mpa_role_exists(cursor)
        if not mpa_role_id:
            print("🔧 Creando rol MPA...")
            mpa_role_id = create_mpa_role(cursor, connection)
            if not mpa_role_id:
                print("❌ No se pudo crear el rol MPA")
                return
        
        # 3. Verificar rol administrativo
        print("\n3️⃣ Verificando rol administrativo...")
        admin_role_id = check_administrativo_role(cursor)
        
        # 4. Obtener usuario para testing
        print("\n4️⃣ Obteniendo usuario para testing...")
        user_id, username = get_current_user_info(cursor)
        if not user_id:
            print("❌ No se encontraron usuarios en la base de datos")
            return
        
        print(f"👤 Usuario seleccionado para testing: {username} (ID: {user_id})")
        
        # 5. Verificar roles del usuario
        print("\n5️⃣ Verificando roles del usuario...")
        user_roles = check_user_roles(cursor, user_id)
        
        # 6. Asignar rol MPA si no lo tiene
        if 'mpa' not in user_roles and 'administrativo' not in user_roles:
            print("\n6️⃣ Asignando rol MPA al usuario...")
            if assign_role_to_user(cursor, connection, user_id, mpa_role_id, 'mpa'):
                print("✅ Rol MPA asignado correctamente")
            else:
                print("❌ Error al asignar rol MPA")
        else:
            print("\n✅ Usuario ya tiene permisos para acceder al módulo MPA")
        
        print("\n" + "=" * 50)
        print("🎉 Verificación completada!")
        print("💡 Ahora deberías poder acceder a http://127.0.0.1:8080/mpa")
        
    except Error as e:
        print(f"❌ Error durante la ejecución: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("🔌 Conexión a la base de datos cerrada")

if __name__ == "__main__":
    main()