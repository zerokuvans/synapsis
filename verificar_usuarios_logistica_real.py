#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar usuarios con rol de logística real (ID 5)
y encontrar sus contraseñas
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

def verificar_usuarios_logistica_real():
    """Verificar usuarios con rol de logística real y sus contraseñas"""
    try:
        print("=== VERIFICANDO USUARIOS CON ROL DE LOGÍSTICA (ID 5) ===")
        
        # Conectar a la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Buscar usuarios con rol de logística (ID 5)
        cursor.execute("""
            SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, 
                   recurso_operativo_password, estado
            FROM recurso_operativo 
            WHERE id_roles = 5 AND estado = 'Activo'
            ORDER BY nombre
        """)
        
        usuarios_logistica = cursor.fetchall()
        
        if not usuarios_logistica:
            print("❌ No se encontraron usuarios activos con rol de logística")
            return
        
        print(f"✅ {len(usuarios_logistica)} usuarios activos con rol de logística encontrados:\n")
        
        # Contraseñas comunes a probar
        patrones_password = [
            lambda cedula: f"CE{cedula}",
            lambda cedula: cedula,
            lambda cedula: "123456",
            lambda cedula: "admin",
            lambda cedula: "password",
            lambda cedula: "test123",
            lambda cedula: "logistica",
            lambda cedula: "capired"
        ]
        
        for i, usuario in enumerate(usuarios_logistica, 1):
            print(f"👤 Usuario {i}:")
            print(f"   📋 ID: {usuario['id_codigo_consumidor']}")
            print(f"   🆔 Cédula: {usuario['recurso_operativo_cedula']}")
            print(f"   👨‍💼 Nombre: {usuario['nombre']}")
            print(f"   📊 Estado: {usuario['estado']}")
            
            password_hash = usuario['recurso_operativo_password']
            
            if password_hash and password_hash.startswith('$2b$'):
                print(f"   🔐 Contraseña: Hasheada con bcrypt ✅")
                print(f"   🔍 Probando contraseñas comunes...")
                
                password_encontrada = None
                cedula = usuario['recurso_operativo_cedula']
                
                for patron in patrones_password:
                    password_candidata = patron(cedula)
                    try:
                        if bcrypt.checkpw(password_candidata.encode('utf-8'), password_hash.encode('utf-8')):
                            password_encontrada = password_candidata
                            break
                    except Exception as e:
                        continue
                
                if password_encontrada:
                    print(f"   ✅ Contraseña encontrada: '{password_encontrada}'")
                else:
                    print(f"   ❌ No se pudo determinar la contraseña con los patrones comunes")
            else:
                print(f"   ⚠️ Contraseña no hasheada o formato desconocido: {password_hash[:20]}...")
            
            print()
        
        print("\n" + "="*80)
        print("📋 RESUMEN PARA PRUEBAS")
        print("="*80)
        
        for usuario in usuarios_logistica:
            cedula = usuario['recurso_operativo_cedula']
            nombre = usuario['nombre']
            
            # Intentar determinar la contraseña más probable
            password_hash = usuario['recurso_operativo_password']
            password_probable = None
            
            if password_hash and password_hash.startswith('$2b$'):
                for patron in patrones_password:
                    password_candidata = patron(cedula)
                    try:
                        if bcrypt.checkpw(password_candidata.encode('utf-8'), password_hash.encode('utf-8')):
                            password_probable = password_candidata
                            break
                    except:
                        continue
            
            if password_probable:
                print(f"✅ {nombre}")
                print(f"   Cédula: {cedula}")
                print(f"   Contraseña: {password_probable}")
                print(f"   Rol: logistica (ID 5)")
                print()
        
        cursor.close()
        connection.close()
        print("🔌 Conexión cerrada")
        
    except Error as e:
        print(f"❌ Error de MySQL: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    verificar_usuarios_logistica_real()