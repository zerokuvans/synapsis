#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def apply_migration():
    """Aplicar migración para agregar columna estado"""
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB')
        )
        
        cursor = conn.cursor()
        
        # Leer el archivo de migración
        with open('migrations/add_estado_column_to_ingresos_dotaciones.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Ejecutar cada statement SQL
        statements = sql_content.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--') and statement != '':
                print(f"Ejecutando: {statement[:50]}...")
                cursor.execute(statement)
        
        conn.commit()
        print("✓ Migración aplicada exitosamente")
        
    except mysql.connector.Error as e:
        print(f"✗ Error de MySQL: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Conexión cerrada")

if __name__ == "__main__":
    apply_migration()