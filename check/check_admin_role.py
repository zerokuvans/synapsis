#!/usr/bin/env python3
"""
Script para verificar y configurar el rol administrativo
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

def main():
    """Función principal"""
    print("🔍 Verificando configuración de roles...")
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # 1. Mostrar roles existentes
        print("\n🏷️ Roles existentes:")
        cursor.execute("SELECT * FROM roles")
        roles = cursor.fetchall()
        for role in roles:
            print(f"   - ID: {role[0]}, Nombre: {role[1]}")
        
        # 2. Verificar si existe el rol administrativo
        cursor.execute("SELECT * FROM roles WHERE nombre_rol = 'administrativo'")
        admin_role = cursor.fetchone()
        if admin_role:
            admin_role_id = admin_role[0]
            print(f"\n✅ Rol 'administrativo' encontrado: ID {admin_role_id}")
        else:
            print(f"\n❌ Rol 'administrativo' no encontrado")
            return
        
        # 3. Mostrar algunos usuarios con sus roles
        print("\n👥 Usuarios existentes (primeros 5):")
        cursor.execute("""
            SELECT ro.id_codigo_consumidor, ro.nombre, ro.recurso_operativo_cedula, ro.id_roles, r.nombre_rol 
            FROM recurso_operativo ro 
            LEFT JOIN roles r ON ro.id_roles = r.id_roles 
            LIMIT 5
        """)
        users = cursor.fetchall()
        for user in users:
            print(f"   - ID: {user[0]}, Nombre: {user[1]}, Cédula: {user[2]}, Rol ID: {user[3]}, Rol: {user[4] or 'Sin rol'}")
        
        # 4. Verificar si hay algún usuario con rol administrativo
        cursor.execute("""
            SELECT ro.id_codigo_consumidor, ro.nombre, ro.recurso_operativo_cedula 
            FROM recurso_operativo ro 
            WHERE ro.id_roles = %s
        """, (admin_role_id,))
        admin_users = cursor.fetchall()
        
        if admin_users:
            print(f"\n✅ Usuarios con rol administrativo:")
            for user in admin_users:
                print(f"   - {user[1]} (Cédula: {user[2]})")
        else:
            print(f"\n❌ No hay usuarios con rol administrativo")
            if users:
                first_user = users[0]
                print(f"🔧 Asignando rol administrativo al usuario {first_user[1]}...")
                cursor.execute("UPDATE recurso_operativo SET id_roles = %s WHERE id_codigo_consumidor = %s", 
                             (admin_role_id, first_user[0]))
                connection.commit()
                print(f"✅ Rol administrativo asignado a {first_user[1]}")
        
        print("\n🎉 ¡Configuración completada! Ahora deberías poder acceder a /mpa")
        
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    main()