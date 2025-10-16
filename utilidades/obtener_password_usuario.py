#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para obtener y verificar la contraseña del usuario 80833959
"""

import mysql.connector
import bcrypt
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
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

def obtener_password_usuario():
    """Obtener la contraseña hasheada del usuario 80833959"""
    print("🔐 OBTENIENDO CONTRASEÑA DEL USUARIO 80833959")
    print("="*60)
    
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if connection is None:
            print("❌ Error de conexión")
            return
        
        cursor = connection.cursor(dictionary=True)
        
        # Obtener la contraseña hasheada
        cursor.execute("""
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula,
                nombre,
                recurso_operativo_password,
                estado
            FROM recurso_operativo 
            WHERE recurso_operativo_cedula = %s
        """, ('80833959',))
        
        usuario = cursor.fetchone()
        
        if not usuario:
            print("❌ Usuario no encontrado")
            return
        
        print("✅ Usuario encontrado:")
        print(f"   ID: {usuario['id_codigo_consumidor']}")
        print(f"   Cédula: {usuario['recurso_operativo_cedula']}")
        print(f"   Nombre: {usuario['nombre']}")
        print(f"   Estado: {usuario['estado']}")
        
        password_hash = usuario['recurso_operativo_password']
        print(f"   Password Hash: {password_hash[:50]}...")
        
        # Lista de contraseñas comunes para probar
        contraseñas_comunes = [
            'admin123',
            '123456',
            'password123',
            '80833959',  # Su propia cédula
            'admin',
            'password',
            'victor123',
            'naranjo123',
            'synapsis123',
            'capired123',
            '12345678',
            'qwerty123',
            'abc123',
            'test123'
        ]
        
        print(f"\n🧪 PROBANDO CONTRASEÑAS COMUNES...")
        print("-" * 50)
        
        password_encontrada = None
        
        for password in contraseñas_comunes:
            try:
                # Convertir hash a bytes si es string
                if isinstance(password_hash, str):
                    hash_bytes = password_hash.encode('utf-8')
                else:
                    hash_bytes = password_hash
                
                # Verificar contraseña
                if bcrypt.checkpw(password.encode('utf-8'), hash_bytes):
                    print(f"✅ CONTRASEÑA ENCONTRADA: '{password}'")
                    password_encontrada = password
                    break
                else:
                    print(f"❌ '{password}' - No coincide")
                    
            except Exception as e:
                print(f"❌ Error verificando '{password}': {e}")
        
        if password_encontrada:
            print(f"\n🎉 ÉXITO: La contraseña del usuario 80833959 es: '{password_encontrada}'")
            return password_encontrada
        else:
            print(f"\n❌ No se encontró la contraseña entre las opciones comunes")
            print(f"💡 Puede que necesites crear una nueva contraseña para este usuario")
            
            # Mostrar información del hash para debugging
            print(f"\n🔍 INFORMACIÓN DEL HASH:")
            print(f"   Tipo: {type(password_hash)}")
            print(f"   Longitud: {len(password_hash) if password_hash else 'None'}")
            if password_hash:
                print(f"   Primeros 20 chars: {password_hash[:20]}")
                print(f"   Últimos 20 chars: {password_hash[-20:]}")
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
    
    print(f"\n🏁 PROCESO COMPLETADO")
    print("="*60)

if __name__ == "__main__":
    obtener_password_usuario()