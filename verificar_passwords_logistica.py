#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar las contraseñas de los usuarios de logística
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import bcrypt

# Cargar variables de entorno
load_dotenv()

def conectar_db():
    """Conectar a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            database=os.getenv('MYSQL_DB', 'synapsis'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )
        return connection
    except Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None

def verificar_passwords():
    """Verificar las contraseñas de los usuarios de logística"""
    connection = conectar_db()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Obtener usuarios de logística con sus contraseñas
        cursor.execute("""
            SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, 
                   recurso_operativo_password, estado
            FROM recurso_operativo 
            WHERE id_roles = 5 AND estado = 'Activo'
            LIMIT 5
        """)
        
        usuarios = cursor.fetchall()
        
        print("=== VERIFICACIÓN DE CONTRASEÑAS DE USUARIOS LOGÍSTICA ===")
        print(f"Encontrados {len(usuarios)} usuarios:\n")
        
        for usuario in usuarios:
            print(f"Usuario: {usuario['nombre']}")
            print(f"Cédula: {usuario['recurso_operativo_cedula']}")
            print(f"ID: {usuario['id_codigo_consumidor']}")
            print(f"Estado: {usuario['estado']}")
            
            password_hash = usuario['recurso_operativo_password']
            print(f"Hash de contraseña: {password_hash[:50]}...")
            
            # Probar contraseñas comunes
            contraseñas_prueba = ['123456', '123', 'admin', 'password', usuario['recurso_operativo_cedula']]
            
            for pwd in contraseñas_prueba:
                try:
                    if bcrypt.checkpw(pwd.encode('utf-8'), password_hash.encode('utf-8')):
                        print(f"✅ Contraseña encontrada: '{pwd}'")
                        break
                except Exception as e:
                    continue
            else:
                print("❌ No se encontró la contraseña entre las opciones comunes")
                
                # Intentar verificar si es un hash bcrypt válido
                if password_hash.startswith('$2b$') or password_hash.startswith('$2a$'):
                    print("   Hash parece ser bcrypt válido")
                else:
                    print(f"   Hash no parece ser bcrypt: {password_hash}")
            
            print("-" * 50)
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"❌ Error consultando usuarios: {e}")

if __name__ == "__main__":
    verificar_passwords()