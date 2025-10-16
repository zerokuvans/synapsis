#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar la contraseña del usuario 80833959 para pruebas
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

def actualizar_password():
    """Actualizar la contraseña del usuario 80833959"""
    print("🔐 ACTUALIZANDO CONTRASEÑA DEL USUARIO 80833959")
    print("="*60)
    
    # Nueva contraseña para pruebas
    nueva_password = "test123"
    
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if connection is None:
            print("❌ Error de conexión")
            return
        
        cursor = connection.cursor(dictionary=True)
        
        # Verificar que el usuario existe
        cursor.execute("""
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula,
                nombre
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
        
        # Generar hash de la nueva contraseña
        print(f"\n🔒 Generando hash para la nueva contraseña: '{nueva_password}'")
        password_hash = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt())
        password_hash_str = password_hash.decode('utf-8')
        
        print(f"✅ Hash generado: {password_hash_str[:30]}...")
        
        # Actualizar la contraseña en la base de datos
        print(f"\n💾 Actualizando contraseña en la base de datos...")
        cursor.execute("""
            UPDATE recurso_operativo 
            SET recurso_operativo_password = %s 
            WHERE recurso_operativo_cedula = %s
        """, (password_hash_str, '80833959'))
        
        connection.commit()
        
        print(f"✅ Contraseña actualizada exitosamente")
        
        # Verificar que la actualización funcionó
        print(f"\n🧪 Verificando la nueva contraseña...")
        if bcrypt.checkpw(nueva_password.encode('utf-8'), password_hash):
            print(f"✅ Verificación exitosa: La contraseña '{nueva_password}' funciona correctamente")
        else:
            print(f"❌ Error en la verificación")
        
        print(f"\n🎉 PROCESO COMPLETADO")
        print(f"📋 CREDENCIALES PARA PRUEBAS:")
        print(f"   Usuario: 80833959")
        print(f"   Contraseña: {nueva_password}")
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
        if connection:
            connection.rollback()
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
    
    print(f"\n🏁 SCRIPT COMPLETADO")
    print("="*60)

if __name__ == "__main__":
    actualizar_password()