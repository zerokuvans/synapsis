#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar usuarios de logística y sus contraseñas
"""

import mysql.connector
from mysql.connector import Error
import bcrypt

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'port': 3306
}

def verificar_usuarios_logistica():
    """
    Verifica los usuarios de logística disponibles
    """
    connection = None
    cursor = None
    
    try:
        print("🔍 Conectando a la base de datos...")
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        print("✅ Conexión exitosa")
        print("\n" + "="*80)
        print("👥 VERIFICACIÓN DE USUARIOS DE LOGÍSTICA")
        print("="*80)
        
        # Buscar usuarios con rol de logística (id_roles = 3)
        print("\n1️⃣ Buscando usuarios con rol de logística...")
        cursor.execute("""
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula,
                nombre,
                id_roles,
                estado,
                recurso_operativo_password
            FROM recurso_operativo 
            WHERE id_roles = 3
            ORDER BY nombre
        """)
        
        usuarios_logistica = cursor.fetchall()
        
        if not usuarios_logistica:
            print("❌ No se encontraron usuarios con rol de logística")
            return
        
        print(f"✅ Se encontraron {len(usuarios_logistica)} usuarios con rol de logística:")
        print()
        
        for i, usuario in enumerate(usuarios_logistica, 1):
            print(f"👤 Usuario {i}:")
            print(f"   📋 ID: {usuario['id_codigo_consumidor']}")
            print(f"   🆔 Cédula: {usuario['recurso_operativo_cedula']}")
            print(f"   👨‍💼 Nombre: {usuario['nombre']}")
            print(f"   🎭 Rol ID: {usuario['id_roles']}")
            print(f"   📊 Estado: {usuario['estado']}")
            
            # Verificar si la contraseña está hasheada
            password_hash = usuario['recurso_operativo_password']
            if password_hash:
                if isinstance(password_hash, str):
                    password_hash = password_hash.encode('utf-8')
                
                if password_hash.startswith(b'$2b$') or password_hash.startswith(b'$2a$'):
                    print(f"   🔐 Contraseña: Hasheada con bcrypt ✅")
                    
                    # Probar contraseñas comunes
                    contraseñas_comunes = [
                        f"CE{usuario['recurso_operativo_cedula']}",  # Patrón CE + cédula
                        usuario['recurso_operativo_cedula'],  # Solo la cédula
                        "123456",
                        "admin",
                        "password"
                    ]
                    
                    print(f"   🔍 Probando contraseñas comunes...")
                    for contraseña in contraseñas_comunes:
                        try:
                            if bcrypt.checkpw(contraseña.encode('utf-8'), password_hash):
                                print(f"   ✅ Contraseña encontrada: '{contraseña}'")
                                break
                        except Exception as e:
                            continue
                    else:
                        print(f"   ❌ No se encontró la contraseña entre las opciones comunes")
                else:
                    print(f"   🔐 Contraseña: Texto plano - '{password_hash.decode('utf-8') if isinstance(password_hash, bytes) else password_hash}'")
            else:
                print(f"   🔐 Contraseña: No definida")
            
            print()
        
        # Mostrar usuarios activos específicamente
        print("\n2️⃣ Usuarios de logística ACTIVOS:")
        usuarios_activos = [u for u in usuarios_logistica if u['estado'] == 'Activo']
        
        if usuarios_activos:
            print(f"✅ {len(usuarios_activos)} usuarios activos encontrados:")
            for usuario in usuarios_activos:
                print(f"   👤 {usuario['nombre']} (Cédula: {usuario['recurso_operativo_cedula']})")
        else:
            print("❌ No hay usuarios de logística activos")
        
        print("\n" + "="*80)
        print("📋 RESUMEN")
        print("="*80)
        print(f"Total usuarios logística: {len(usuarios_logistica)}")
        print(f"Usuarios activos: {len(usuarios_activos)}")
        print(f"Usuarios inactivos: {len(usuarios_logistica) - len(usuarios_activos)}")
        
        if usuarios_activos:
            print("\n💡 Para las pruebas, puedes usar cualquiera de estos usuarios activos:")
            for usuario in usuarios_activos[:3]:  # Mostrar máximo 3
                print(f"   - Cédula: {usuario['recurso_operativo_cedula']} | Nombre: {usuario['nombre']}")
        
        print("\n✅ Verificación completada")
        
    except Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    verificar_usuarios_logistica()