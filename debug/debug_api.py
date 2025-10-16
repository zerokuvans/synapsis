#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debuggear las APIs de mantenimiento
"""

import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def test_database_connection():
    """Probar conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("✅ Conexión a la base de datos exitosa")
            return connection
    except Error as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return None

def test_mantenimientos_query():
    """Probar la consulta de mantenimientos"""
    connection = test_database_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print("\n=== PROBANDO CONSULTA DE MANTENIMIENTOS ===")
        
        # Verificar si las tablas existen
        print("1. Verificando tablas...")
        cursor.execute("SHOW TABLES LIKE 'mpa_mantenimientos'")
        if cursor.fetchone():
            print("   ✅ Tabla mpa_mantenimientos existe")
        else:
            print("   ❌ Tabla mpa_mantenimientos NO existe")
            return
            
        cursor.execute("SHOW TABLES LIKE 'mpa_vehiculos'")
        if cursor.fetchone():
            print("   ✅ Tabla mpa_vehiculos existe")
        else:
            print("   ❌ Tabla mpa_vehiculos NO existe")
            
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        if cursor.fetchone():
            print("   ✅ Tabla recurso_operativo existe")
        else:
            print("   ❌ Tabla recurso_operativo NO existe")
            
        cursor.execute("SHOW TABLES LIKE 'mpa_categoria_mantenimiento'")
        if cursor.fetchone():
            print("   ✅ Tabla mpa_categoria_mantenimiento existe")
        else:
            print("   ❌ Tabla mpa_categoria_mantenimiento NO existe")
        
        # Probar la consulta exacta de la API
        print("\n2. Probando consulta de mantenimientos...")
        query = """
        SELECT 
            m.id_mpa_mantenimientos,
            m.placa,
            m.fecha_mantenimiento,
            m.kilometraje,
            m.observacion,
            m.soporte_foto_geo as foto_taller,
            m.soporte_foto_factura as foto_factura,
            m.tipo_vehiculo,
            m.tecnico as tecnico_nombre,
            m.tipo_mantenimiento
        FROM mpa_mantenimientos m
        ORDER BY m.fecha_mantenimiento DESC
        """
        
        cursor.execute(query)
        mantenimientos = cursor.fetchall()
        print(f"   ✅ Consulta exitosa. Encontrados {len(mantenimientos)} mantenimientos")
        
        if mantenimientos:
            print("   📋 Primeros 3 registros:")
            for i, m in enumerate(mantenimientos[:3]):
                print(f"      {i+1}. Placa: {m.get('placa', 'N/A')}, Fecha: {m.get('fecha_mantenimiento', 'N/A')}")
        
    except Error as e:
        print(f"❌ Error en consulta de mantenimientos: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def test_placas_query():
    """Probar la consulta de placas"""
    connection = test_database_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print("\n=== PROBANDO CONSULTA DE PLACAS ===")
        
        query = """
        SELECT 
            v.placa,
            v.tipo_vehiculo,
            v.tecnico_asignado as tecnico_nombre
        FROM mpa_vehiculos v
        WHERE v.estado = 'Activo'
        ORDER BY v.placa
        """
        
        cursor.execute(query)
        placas = cursor.fetchall()
        print(f"   ✅ Consulta exitosa. Encontradas {len(placas)} placas activas")
        
        if placas:
            print("   🚗 Primeras 5 placas:")
            for i, p in enumerate(placas[:5]):
                print(f"      {i+1}. Placa: {p.get('placa', 'N/A')}, Tipo: {p.get('tipo_vehiculo', 'N/A')}")
        
    except Error as e:
        print(f"❌ Error en consulta de placas: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    print("🔍 DEBUGGEANDO APIs DE MANTENIMIENTO")
    test_mantenimientos_query()
    test_placas_query()
    print("\n🎉 Debug completado")