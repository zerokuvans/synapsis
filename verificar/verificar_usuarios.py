#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar qué usuarios existen en la base de datos
"""

import mysql.connector
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

def verificar_usuarios():
    """Verificar usuarios existentes"""
    print("="*60)
    print("VERIFICACIÓN DE USUARIOS EN LA BASE DE DATOS")
    print("="*60)
    
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if connection is None:
            print("❌ Error: No se pudo conectar a la base de datos")
            return
        
        cursor = connection.cursor(dictionary=True)
        print("✅ Conexión a la base de datos exitosa")
        
        # Verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        tabla_existe = cursor.fetchone()
        
        if not tabla_existe:
            print("❌ La tabla 'recurso_operativo' no existe")
            return
        
        print("✅ Tabla 'recurso_operativo' encontrada")
        
        # Obtener todos los usuarios
        cursor.execute("""
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula,
                nombre,
                fecha_ingreso,
                fecha_retiro
            FROM recurso_operativo 
            ORDER BY id_codigo_consumidor
            LIMIT 10
        """)
        
        usuarios = cursor.fetchall()
        
        if not usuarios:
            print("❌ No se encontraron usuarios en la tabla")
            return
        
        print(f"\n📋 USUARIOS ENCONTRADOS (primeros 10):")
        print("-" * 80)
        print(f"{'ID':<5} {'Cédula':<15} {'Nombre':<25} {'F.Ingreso':<12} {'F.Retiro':<12}")
        print("-" * 80)
        
        for usuario in usuarios:
            fecha_ing = usuario['fecha_ingreso'].strftime('%Y-%m-%d') if usuario['fecha_ingreso'] else 'NULL'
            fecha_ret = usuario['fecha_retiro'].strftime('%Y-%m-%d') if usuario['fecha_retiro'] else 'NULL'
            
            print(f"{usuario['id_codigo_consumidor']:<5} {usuario['recurso_operativo_cedula']:<15} {usuario['nombre'][:24]:<25} {fecha_ing:<12} {fecha_ret:<12}")
        
        # Estadísticas
        cursor.execute("SELECT COUNT(*) as total FROM recurso_operativo")
        total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as con_fecha_ing FROM recurso_operativo WHERE fecha_ingreso IS NOT NULL")
        con_fecha_ing = cursor.fetchone()['con_fecha_ing']
        
        cursor.execute("SELECT COUNT(*) as con_fecha_ret FROM recurso_operativo WHERE fecha_retiro IS NOT NULL")
        con_fecha_ret = cursor.fetchone()['con_fecha_ret']
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"Total de usuarios: {total}")
        print(f"Con fecha de ingreso: {con_fecha_ing}")
        print(f"Con fecha de retiro: {con_fecha_ret}")
        
        # Buscar usuarios con fechas
        if con_fecha_ing > 0:
            cursor.execute("""
                SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, fecha_ingreso
                FROM recurso_operativo 
                WHERE fecha_ingreso IS NOT NULL
                LIMIT 3
            """)
            usuarios_con_fecha = cursor.fetchall()
            
            print(f"\n✅ USUARIOS CON FECHA DE INGRESO:")
            for u in usuarios_con_fecha:
                print(f"  ID: {u['id_codigo_consumidor']}, Cédula: {u['recurso_operativo_cedula']}, Nombre: {u['nombre']}")
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("\n✅ Conexión cerrada")

if __name__ == "__main__":
    verificar_usuarios()