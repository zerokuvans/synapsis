#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar datos en la tabla tipificacion_asistencia
"""

import mysql.connector
from mysql.connector import Error

def verificar_tipificacion_asistencia():
    """Verificar datos en tipificacion_asistencia"""
    
    try:
        # Configuración de conexión (usando la misma del main.py)
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@',
            port=3306
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Verificar si la tabla existe
            cursor.execute("SHOW TABLES LIKE 'tipificacion_asistencia'")
            tabla_existe = cursor.fetchone()
            
            if not tabla_existe:
                print("❌ La tabla 'tipificacion_asistencia' no existe")
                return
            
            print("✅ La tabla 'tipificacion_asistencia' existe")
            
            # Contar registros totales
            cursor.execute("SELECT COUNT(*) as total FROM tipificacion_asistencia")
            total = cursor.fetchone()['total']
            print(f"📊 Total de registros: {total}")
            
            # Verificar estructura de la tabla primero
            cursor.execute("DESCRIBE tipificacion_asistencia")
            estructura = cursor.fetchall()
            
            print("\n🏗️  Estructura de la tabla:")
            columnas = []
            for campo in estructura:
                columnas.append(campo['Field'])
                print(f"  - {campo['Field']}: {campo['Type']} {'(NULL)' if campo['Null'] == 'YES' else '(NOT NULL)'}")
            
            if total > 0:
                # Obtener algunos registros de ejemplo usando todas las columnas disponibles
                cursor.execute("SELECT * FROM tipificacion_asistencia LIMIT 10")
                registros = cursor.fetchall()
                
                print(f"\n📋 Registros encontrados ({len(registros)}):")
                for i, registro in enumerate(registros, 1):
                    print(f"  {i}. {registro}")
                
                # Verificar registros con código vacío o nulo si la columna existe
                if 'codigo_tipificacion' in columnas:
                    cursor.execute("""
                        SELECT COUNT(*) as vacios 
                        FROM tipificacion_asistencia 
                        WHERE codigo_tipificacion IS NULL OR codigo_tipificacion = ''
                    """)
                    vacios = cursor.fetchone()['vacios']
                    
                    if vacios > 0:
                        print(f"\n⚠️  Hay {vacios} registros con código_tipificacion vacío o nulo")
                    else:
                        print("\n✅ Todos los registros tienen código_tipificacion válido")
            else:
                print("\n⚠️  No hay registros en la tabla tipificacion_asistencia")
            
    except Error as e:
        print(f"❌ Error de conexión a MySQL: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()
            print("\n🔌 Conexión cerrada")

if __name__ == '__main__':
    print("=== Verificación de tabla tipificacion_asistencia ===")
    verificar_tipificacion_asistencia()