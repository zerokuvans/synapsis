#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar credenciales de usuarios en la base de datos
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

def verificar_estructura_tabla():
    """Verificar estructura de la tabla recurso_operativo"""
    print("🔍 VERIFICANDO ESTRUCTURA DE LA TABLA")
    print("="*60)
    
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if connection is None:
            print("❌ Error de conexión")
            return
        
        cursor = connection.cursor()
        
        # Obtener estructura de la tabla
        cursor.execute("DESCRIBE recurso_operativo")
        
        columnas = cursor.fetchall()
        
        print("✅ Columnas de la tabla recurso_operativo:")
        print()
        
        for columna in columnas:
            print(f"   {columna[0]} | {columna[1]} | {columna[2]} | {columna[3]} | {columna[4]} | {columna[5]}")
        
        print()
        print("🔑 BUSCANDO COLUMNAS RELACIONADAS CON PASSWORD:")
        
        columnas_password = [col[0] for col in columnas if 'password' in col[0].lower() or 'pass' in col[0].lower() or 'clave' in col[0].lower()]
        
        if columnas_password:
            print(f"   Encontradas: {', '.join(columnas_password)}")
            
            # Obtener algunos usuarios con esas columnas
            cursor = connection.cursor(dictionary=True)
            
            columnas_str = ', '.join(columnas_password)
            query = f"""
                SELECT 
                    id_codigo_consumidor,
                    recurso_operativo_cedula,
                    nombre,
                    {columnas_str}
                FROM recurso_operativo 
                LIMIT 5
            """
            
            cursor.execute(query)
            usuarios = cursor.fetchall()
            
            print(f"\n📋 PRIMEROS 5 USUARIOS:")
            for usuario in usuarios:
                print(f"   ID: {usuario['id_codigo_consumidor']} | Cédula: {usuario['recurso_operativo_cedula']}")
                for col in columnas_password:
                    print(f"      {col}: {usuario.get(col, 'N/A')}")
                print()
        else:
            print("   No se encontraron columnas relacionadas con password")
            
            # Mostrar todas las columnas para identificar la correcta
            print(f"\n📋 TODAS LAS COLUMNAS DISPONIBLES:")
            for columna in columnas:
                print(f"   - {columna[0]}")
        
    except mysql.connector.Error as e:
        print(f"❌ Error: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    verificar_estructura_tabla()