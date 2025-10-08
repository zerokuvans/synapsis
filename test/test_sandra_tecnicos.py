#!/usr/bin/env python3
"""
Script para probar la consulta SQL que busca técnicos para CORTES CUERVO SANDRA CECILIA
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            database=os.getenv('MYSQL_DB', 'capired'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            port=int(os.getenv('MYSQL_PORT', 3306))
        )
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def test_sandra_tecnicos():
    """Probar consultas para CORTES CUERVO SANDRA CECILIA"""
    supervisor = "CORTES CUERVO SANDRA CECILIA"
    
    print(f"=== PROBANDO CONSULTAS PARA: {supervisor} ===\n")
    
    connection = get_db_connection()
    if connection is None:
        print("❌ No se pudo conectar a la base de datos")
        return
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # 1. Consulta exacta como en el endpoint
        print("1. Consulta exacta del endpoint:")
        query1 = """
            SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula as documento
            FROM recurso_operativo
            WHERE super = %s AND estado = 'Activo'
        """
        print(f"Query: {query1}")
        print(f"Parámetro: '{supervisor}'")
        
        cursor.execute(query1, (supervisor,))
        tecnicos = cursor.fetchall()
        
        print(f"Resultados encontrados: {len(tecnicos)}")
        for tecnico in tecnicos:
            print(f"  - {tecnico['nombre']} (ID: {tecnico['id_codigo_consumidor']}, Doc: {tecnico['documento']})")
        
        print("\n" + "="*60 + "\n")
        
        # 2. Verificar si existe el supervisor en la tabla
        print("2. Verificando si existe el supervisor en recurso_operativo:")
        query2 = "SELECT DISTINCT super FROM recurso_operativo WHERE super LIKE %s"
        cursor.execute(query2, (f"%{supervisor}%",))
        supervisores = cursor.fetchall()
        
        print(f"Supervisores que contienen '{supervisor}':")
        for sup in supervisores:
            print(f"  - '{sup['super']}'")
        
        print("\n" + "="*60 + "\n")
        
        # 3. Consulta más amplia para ver todos los supervisores
        print("3. Todos los supervisores únicos:")
        query3 = "SELECT DISTINCT super FROM recurso_operativo WHERE super IS NOT NULL AND super != '' ORDER BY super"
        cursor.execute(query3)
        todos_supervisores = cursor.fetchall()
        
        print(f"Total de supervisores únicos: {len(todos_supervisores)}")
        for sup in todos_supervisores:
            print(f"  - '{sup['super']}'")
        
        print("\n" + "="*60 + "\n")
        
        # 4. Buscar técnicos sin filtro de estado
        print("4. Técnicos de Sandra sin filtro de estado:")
        query4 = """
            SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula as documento, estado
            FROM recurso_operativo
            WHERE super = %s
        """
        cursor.execute(query4, (supervisor,))
        tecnicos_sin_filtro = cursor.fetchall()
        
        print(f"Técnicos encontrados (sin filtro de estado): {len(tecnicos_sin_filtro)}")
        for tecnico in tecnicos_sin_filtro:
            print(f"  - {tecnico['nombre']} (Estado: {tecnico['estado']}, ID: {tecnico['id_codigo_consumidor']})")
        
    except Error as e:
        print(f"❌ Error en la consulta: {e}")
    
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    test_sandra_tecnicos()