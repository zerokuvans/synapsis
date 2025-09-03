#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analizar la estructura de la tabla recurso_operativo
"""

import mysql.connector
from mysql.connector import Error
import sys

def conectar_bd():
    """Conecta a la base de datos capired"""
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return conexion
    except Error as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return None

def analizar_estructura_tabla(cursor, tabla):
    """Analiza la estructura de una tabla específica"""
    print(f"\n=== ESTRUCTURA DE LA TABLA '{tabla}' ===")
    print("\n📋 DESCRIPCIÓN DE CAMPOS:")
    print("-" * 100)
    print(f"{'Campo':<25} {'Tipo':<20} {'Nulo':<8} {'Clave':<8} {'Extra':<15} {'Comentario'}")
    print("-" * 100)
    
    cursor.execute(f"DESCRIBE {tabla}")
    campos = cursor.fetchall()
    
    for campo in campos:
        field, type_, null, key, default, extra = campo
        print(f"{field:<25} {type_:<20} {null:<8} {key:<8} {extra:<15}")
    
    return campos

def obtener_datos_ejemplo(cursor, tabla, limite=10):
    """Obtiene datos de ejemplo de la tabla"""
    print(f"\n=== DATOS DE EJEMPLO (primeros {limite} registros) ===")
    
    # Contar registros totales
    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
    total = cursor.fetchone()[0]
    print(f"\n📊 Total de registros en la tabla: {total}")
    
    if total == 0:
        print("ℹ️ La tabla está vacía")
        return
    
    # Obtener datos de ejemplo
    cursor.execute(f"SELECT * FROM {tabla} LIMIT {limite}")
    registros = cursor.fetchall()
    
    if registros:
        # Obtener nombres de columnas
        cursor.execute(f"DESCRIBE {tabla}")
        columnas = [desc[0] for desc in cursor.fetchall()]
        
        print(f"\n📋 Primeros {len(registros)} registros:")
        print("-" * 120)
        
        # Imprimir encabezados
        header = " | ".join([f"{col[:15]:<15}" for col in columnas[:8]])  # Limitar a 8 columnas
        print(header)
        print("-" * 120)
        
        # Imprimir datos
        for registro in registros:
            row = " | ".join([f"{str(val)[:15]:<15}" if val is not None else f"{'NULL':<15}" for val in registro[:8]])
            print(row)

def analizar_usuarios_activos(cursor):
    """Analiza específicamente los usuarios activos"""
    print("\n=== ANÁLISIS DE USUARIOS ACTIVOS ===")
    
    # Verificar valores únicos en campo estado
    cursor.execute("SELECT DISTINCT estado FROM recurso_operativo ORDER BY estado")
    estados = cursor.fetchall()
    print(f"\n📊 Estados encontrados: {[estado[0] for estado in estados]}")
    
    # Contar usuarios por estado
    cursor.execute("SELECT estado, COUNT(*) as cantidad FROM recurso_operativo GROUP BY estado ORDER BY cantidad DESC")
    conteos = cursor.fetchall()
    print("\n📈 Distribución por estado:")
    for estado, cantidad in conteos:
        print(f"  - {estado}: {cantidad} usuarios")
    
    # Obtener usuarios activos
    cursor.execute("SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula, cargo, estado FROM recurso_operativo WHERE estado = 'Activo' LIMIT 10")
    activos = cursor.fetchall()
    
    if activos:
        print("\n👥 Primeros 10 usuarios activos:")
        print("-" * 100)
        print(f"{'ID':<10} {'Nombre':<25} {'Cédula':<15} {'Cargo':<20} {'Estado':<10}")
        print("-" * 100)
        for usuario in activos:
            id_cod, nombre, cedula, cargo, estado = usuario
            print(f"{id_cod:<10} {nombre[:24]:<25} {cedula:<15} {cargo[:19]:<20} {estado:<10}")

def main():
    """Función principal"""
    print("🔍 ANALIZADOR DE TABLA RECURSO_OPERATIVO")
    print("=" * 50)
    
    # Conectar a la base de datos
    conexion = conectar_bd()
    if not conexion:
        sys.exit(1)
    
    try:
        cursor = conexion.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        if not cursor.fetchone():
            print("❌ La tabla 'recurso_operativo' no existe")
            return
        
        # Analizar estructura
        campos = analizar_estructura_tabla(cursor, 'recurso_operativo')
        
        # Obtener datos de ejemplo
        obtener_datos_ejemplo(cursor, 'recurso_operativo', 5)
        
        # Análisis específico de usuarios activos
        analizar_usuarios_activos(cursor)
        
        print("\n✅ Análisis completado exitosamente")
        
    except Error as e:
        print(f"❌ Error durante el análisis: {e}")
    
    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()
            print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    main()