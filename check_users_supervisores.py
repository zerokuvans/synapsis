#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar usuarios y supervisores en la base de datos
"""

import mysql.connector
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'capired'),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def check_users():
    """Verificar usuarios en la base de datos"""
    print("=== VERIFICANDO USUARIOS ===")
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Verificar qué tablas existen
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Tablas disponibles:")
        for table in tables:
            print(f"  - {list(table.values())[0]}")
        
        # Obtener usuarios de la tabla recurso_operativo (que es la que usa el login)
        print("\n=== USUARIOS DE RECURSO_OPERATIVO ===")
        cursor.execute("SELECT recurso_operativo_cedula, nombre, id_roles, estado FROM recurso_operativo WHERE estado = 'Activo' LIMIT 5")
        users = cursor.fetchall()
        print(f"Usuarios activos encontrados: {len(users)}")
        for user in users:
            print(f"  Cédula: {user['recurso_operativo_cedula']}, Nombre: {user['nombre']}, Rol: {user['id_roles']}, Estado: {user['estado']}")
        
        # También verificar si hay contraseñas
        cursor.execute("SELECT recurso_operativo_cedula, recurso_operativo_password FROM recurso_operativo WHERE estado = 'Activo' AND recurso_operativo_password IS NOT NULL LIMIT 3")
        users_with_pass = cursor.fetchall()
        print(f"\nUsuarios con contraseña: {len(users_with_pass)}")
        for user in users_with_pass:
            print(f"  Cédula: {user['recurso_operativo_cedula']}, Contraseña (hash): {user['recurso_operativo_password'][:20]}...")
            
    except mysql.connector.Error as e:
        print(f"Error consultando usuarios: {e}")
    finally:
        cursor.close()
        connection.close()

def check_supervisores():
    """Verificar supervisores en la tabla recurso_operativo"""
    print("\n=== VERIFICANDO SUPERVISORES ===")
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Verificar supervisores únicos
        cursor.execute("""
            SELECT DISTINCT super
            FROM recurso_operativo
            WHERE super IS NOT NULL AND super != '' AND estado = 'Activo'
            ORDER BY super
        """)
        supervisores = cursor.fetchall()
        
        print(f"Total supervisores encontrados: {len(supervisores)}")
        for supervisor in supervisores:
            print(f"  - Supervisor: {supervisor['super']}")
            
        # Verificar algunos registros de recurso_operativo
        print("\n=== MUESTRA DE RECURSO_OPERATIVO ===")
        cursor.execute("""
            SELECT id_codigo_consumidor, nombre, super, estado
            FROM recurso_operativo
            WHERE super IS NOT NULL AND super != ''
            LIMIT 5
        """)
        recursos = cursor.fetchall()
        
        for recurso in recursos:
            print(f"  - ID: {recurso['id_codigo_consumidor']}, Nombre: {recurso['nombre']}, Supervisor: {recurso['super']}, Estado: {recurso['estado']}")
            
    except mysql.connector.Error as e:
        print(f"Error consultando supervisores: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    check_users()
    check_supervisores()