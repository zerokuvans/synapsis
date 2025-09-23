#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para ejecutar las migraciones SQL del sistema de gestión de estados
"""

import mysql.connector
import os

def ejecutar_migraciones():
    """Ejecuta todas las migraciones SQL necesarias"""
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        cursor = conn.cursor()
        
        # Lista de archivos SQL a ejecutar
        archivos_sql = [
            'create_estado_management_tables.sql',
            'create_notification_system.sql'
        ]
        
        for archivo in archivos_sql:
            if os.path.exists(archivo):
                print(f"Ejecutando {archivo}...")
                with open(archivo, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # Dividir en statements individuales
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                
                for stmt in statements:
                    try:
                        cursor.execute(stmt)
                        conn.commit()
                    except mysql.connector.Error as e:
                        print(f"Error ejecutando statement: {e}")
                        print(f"Statement: {stmt[:100]}...")
                        continue
                
                print(f"✓ {archivo} ejecutado exitosamente")
            else:
                print(f"⚠ Archivo {archivo} no encontrado")
        
        # Verificar tablas creadas
        cursor.execute("SHOW TABLES LIKE '%estado%' OR SHOW TABLES LIKE '%notificacion%' OR SHOW TABLES LIKE '%auditoria%'")
        tablas = cursor.fetchall()
        
        print("\n=== Tablas del sistema de gestión de estados ===")
        for tabla in tablas:
            print(f"✓ {tabla[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Migraciones ejecutadas exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error ejecutando migraciones: {e}")
        return False

if __name__ == "__main__":
    ejecutar_migraciones()