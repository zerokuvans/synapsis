#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir la estructura de la tabla mpa_mantenimientos
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

def fix_maintenance_table():
    """Corregir la estructura de la tabla mpa_mantenimientos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("=== CORRIGIENDO ESTRUCTURA DE mpa_mantenimientos ===")
        
        # Cambiar el tipo de dato del campo observacion de varchar(45) a TEXT
        print("1. Cambiando observacion de varchar(45) a TEXT...")
        cursor.execute("ALTER TABLE mpa_mantenimientos MODIFY COLUMN observacion TEXT")
        
        # Cambiar soporte_foto_geo de varchar(45) a TEXT para URLs largas
        print("2. Cambiando soporte_foto_geo de varchar(45) a TEXT...")
        cursor.execute("ALTER TABLE mpa_mantenimientos MODIFY COLUMN soporte_foto_geo TEXT")
        
        # Cambiar soporte_foto_factura de varchar(45) a TEXT para URLs largas
        print("3. Cambiando soporte_foto_factura de varchar(45) a TEXT...")
        cursor.execute("ALTER TABLE mpa_mantenimientos MODIFY COLUMN soporte_foto_factura TEXT")
        
        # Cambiar tipo_mantenimiento de varchar(45) a varchar(100) para nombres más largos
        print("4. Cambiando tipo_mantenimiento de varchar(45) a varchar(100)...")
        cursor.execute("ALTER TABLE mpa_mantenimientos MODIFY COLUMN tipo_mantenimiento varchar(100)")
        
        connection.commit()
        print("✅ Estructura de la tabla corregida exitosamente")
        
        # Verificar los cambios
        print("\n=== VERIFICANDO CAMBIOS ===")
        cursor.execute("DESCRIBE mpa_mantenimientos")
        columns = cursor.fetchall()
        
        relevant_fields = ['observacion', 'soporte_foto_geo', 'soporte_foto_factura', 'tipo_mantenimiento']
        for column in columns:
            if column[0] in relevant_fields:
                print(f"✓ {column[0]}: {column[1]}")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    fix_maintenance_table()