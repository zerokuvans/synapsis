#!/usr/bin/env python3
"""
Script para ejecutar las mejoras del módulo MPA
Ejecuta el archivo SQL mpa_mejoras_historial.sql
"""

import mysql.connector
import os
from datetime import datetime

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def ejecutar_sql_archivo(archivo_sql):
    """Ejecutar un archivo SQL completo"""
    try:
        # Leer el archivo SQL
        with open(archivo_sql, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Conectar a la base de datos
        connection = get_db_connection()
        if connection is None:
            return False
        
        cursor = connection.cursor()
        
        # Dividir el contenido en statements individuales
        statements = []
        current_statement = ""
        
        for line in sql_content.split('\n'):
            line = line.strip()
            
            # Ignorar comentarios y líneas vacías
            if line.startswith('--') or not line:
                continue
            
            current_statement += line + " "
            
            # Si la línea termina con ';', es el final de un statement
            if line.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""
        
        # Ejecutar cada statement
        print(f"Ejecutando {len(statements)} statements SQL...")
        
        for i, statement in enumerate(statements, 1):
            if statement.strip():
                try:
                    print(f"Ejecutando statement {i}/{len(statements)}...")
                    cursor.execute(statement)
                    connection.commit()
                    print(f"✓ Statement {i} ejecutado correctamente")
                except mysql.connector.Error as e:
                    print(f"✗ Error en statement {i}: {e}")
                    print(f"Statement: {statement[:100]}...")
                    continue
        
        cursor.close()
        connection.close()
        print("✓ Archivo SQL ejecutado completamente")
        return True
        
    except Exception as e:
        print(f"Error ejecutando archivo SQL: {e}")
        return False

def verificar_tablas_creadas():
    """Verificar que las tablas de historial se crearon correctamente"""
    try:
        connection = get_db_connection()
        if connection is None:
            return False
        
        cursor = connection.cursor()
        
        # Tablas que deberían existir después de ejecutar el script
        tablas_esperadas = [
            'mpa_soat_historial',
            'mpa_tecnico_mecanica_historial',
            'mpa_licencia_conducir_historial',
            'mpa_mantenimiento_historial',
            'mpa_vehiculos_historial'
        ]
        
        print("\nVerificando tablas creadas:")
        tablas_existentes = []
        
        for tabla in tablas_esperadas:
            cursor.execute(f"SHOW TABLES LIKE '{tabla}'")
            result = cursor.fetchone()
            if result:
                print(f"✓ {tabla} - EXISTE")
                tablas_existentes.append(tabla)
            else:
                print(f"✗ {tabla} - NO EXISTE")
        
        cursor.close()
        connection.close()
        
        print(f"\nTablas creadas: {len(tablas_existentes)}/{len(tablas_esperadas)}")
        return len(tablas_existentes) == len(tablas_esperadas)
        
    except Exception as e:
        print(f"Error verificando tablas: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("EJECUTOR DE MEJORAS MPA - SISTEMA DE HISTORIAL")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ruta del archivo SQL
    archivo_sql = os.path.join(os.path.dirname(__file__), 'sql', 'mpa_mejoras_historial.sql')
    
    if not os.path.exists(archivo_sql):
        print(f"✗ Error: No se encontró el archivo {archivo_sql}")
        return
    
    print(f"Archivo SQL: {archivo_sql}")
    print()
    
    # Ejecutar el archivo SQL
    print("1. Ejecutando archivo SQL...")
    if ejecutar_sql_archivo(archivo_sql):
        print("✓ Archivo SQL ejecutado correctamente")
    else:
        print("✗ Error ejecutando archivo SQL")
        return
    
    print()
    
    # Verificar tablas creadas
    print("2. Verificando tablas creadas...")
    if verificar_tablas_creadas():
        print("✓ Todas las tablas se crearon correctamente")
    else:
        print("✗ Algunas tablas no se crearon correctamente")
    
    print()
    print("=" * 60)
    print("PROCESO COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    main()