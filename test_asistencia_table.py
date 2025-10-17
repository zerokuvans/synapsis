#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para examinar la estructura y datos de la tabla asistencia
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd

def connect_to_database():
    """Conectar a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            database='capired',
            user='root',
            password='732137A031E4b@',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def examine_table_structure(connection):
    """Examinar la estructura de la tabla asistencia"""
    print("=" * 60)
    print("ESTRUCTURA DE LA TABLA ASISTENCIA")
    print("=" * 60)
    
    cursor = connection.cursor()
    cursor.execute("DESCRIBE asistencia")
    columns = cursor.fetchall()
    
    print(f"{'Campo':<20} {'Tipo':<25} {'Null':<5} {'Key':<5} {'Default':<10}")
    print("-" * 70)
    for column in columns:
        print(f"{column[0]:<20} {column[1]:<25} {column[2]:<5} {column[3]:<5} {str(column[4]):<10}")
    
    cursor.close()
    print()

def examine_carpeta_values(connection):
    """Examinar valores distintos en la columna carpeta"""
    print("=" * 60)
    print("VALORES DISTINTOS EN COLUMNA 'carpeta'")
    print("=" * 60)
    
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT carpeta, COUNT(*) as cantidad FROM asistencia GROUP BY carpeta ORDER BY cantidad DESC")
    carpeta_values = cursor.fetchall()
    
    print(f"{'Carpeta':<30} {'Cantidad':<10}")
    print("-" * 45)
    for value in carpeta_values:
        carpeta = value[0] if value[0] is not None else "NULL"
        print(f"{carpeta:<30} {value[1]:<10}")
    
    cursor.close()
    print()

def examine_carpeta_dia_values(connection):
    """Examinar valores distintos en la columna carpeta_dia"""
    print("=" * 60)
    print("VALORES DISTINTOS EN COLUMNA 'carpeta_dia'")
    print("=" * 60)
    
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT carpeta_dia, COUNT(*) as cantidad FROM asistencia GROUP BY carpeta_dia ORDER BY cantidad DESC")
    carpeta_dia_values = cursor.fetchall()
    
    print(f"{'Carpeta Día':<30} {'Cantidad':<10}")
    print("-" * 45)
    for value in carpeta_dia_values:
        carpeta_dia = value[0] if value[0] is not None else "NULL"
        print(f"{carpeta_dia:<30} {value[1]:<10}")
    
    cursor.close()
    print()

def examine_technician_classification(connection):
    """Examinar clasificación de técnicos"""
    print("=" * 60)
    print("CLASIFICACIÓN DE TÉCNICOS")
    print("=" * 60)
    
    cursor = connection.cursor()
    
    # Buscar patrones que indiquen técnicos
    queries = [
        ("Registros con 'tecnico' en carpeta", "SELECT COUNT(*) FROM asistencia WHERE LOWER(carpeta) LIKE '%tecnico%'"),
        ("Registros con 'técnico' en carpeta", "SELECT COUNT(*) FROM asistencia WHERE LOWER(carpeta) LIKE '%técnico%'"),
        ("Registros con 'tec' en carpeta", "SELECT COUNT(*) FROM asistencia WHERE LOWER(carpeta) LIKE '%tec%'"),
        ("Registros con 'tecnico' en carpeta_dia", "SELECT COUNT(*) FROM asistencia WHERE LOWER(carpeta_dia) LIKE '%tecnico%'"),
        ("Registros con 'técnico' en carpeta_dia", "SELECT COUNT(*) FROM asistencia WHERE LOWER(carpeta_dia) LIKE '%técnico%'"),
        ("Registros con 'tec' en carpeta_dia", "SELECT COUNT(*) FROM asistencia WHERE LOWER(carpeta_dia) LIKE '%tec%'"),
    ]
    
    for description, query in queries:
        cursor.execute(query)
        count = cursor.fetchone()[0]
        print(f"{description:<40}: {count}")
    
    cursor.close()
    print()

def examine_sample_data(connection):
    """Examinar datos de muestra"""
    print("=" * 60)
    print("DATOS DE MUESTRA (primeros 10 registros)")
    print("=" * 60)
    
    cursor = connection.cursor()
    cursor.execute("""
        SELECT cedula, tecnico, carpeta, carpeta_dia, super, eventos 
        FROM asistencia 
        LIMIT 10
    """)
    sample_data = cursor.fetchall()
    
    print(f"{'Cédula':<12} {'Técnico':<25} {'Carpeta':<20} {'Carpeta Día':<20} {'Super':<15} {'Eventos':<10}")
    print("-" * 110)
    for row in sample_data:
        cedula = str(row[0]) if row[0] is not None else "NULL"
        tecnico = str(row[1])[:24] if row[1] is not None else "NULL"
        carpeta = str(row[2])[:19] if row[2] is not None else "NULL"
        carpeta_dia = str(row[3])[:19] if row[3] is not None else "NULL"
        super_val = str(row[4])[:14] if row[4] is not None else "NULL"
        eventos = str(row[5]) if row[5] is not None else "NULL"
        
        print(f"{cedula:<12} {tecnico:<25} {carpeta:<20} {carpeta_dia:<20} {super_val:<15} {eventos:<10}")
    
    cursor.close()
    print()

def examine_attendance_logic(connection):
    """Examinar lógica de asistencia"""
    print("=" * 60)
    print("ANÁLISIS DE LÓGICA DE ASISTENCIA")
    print("=" * 60)
    
    cursor = connection.cursor()
    
    # Analizar relación entre carpeta y carpeta_dia
    queries = [
        ("Total registros", "SELECT COUNT(*) FROM asistencia"),
        ("Registros con carpeta_dia no NULL", "SELECT COUNT(*) FROM asistencia WHERE carpeta_dia IS NOT NULL AND carpeta_dia != ''"),
        ("Registros con carpeta no NULL", "SELECT COUNT(*) FROM asistencia WHERE carpeta IS NOT NULL AND carpeta != ''"),
        ("Registros donde carpeta = carpeta_dia", "SELECT COUNT(*) FROM asistencia WHERE carpeta = carpeta_dia"),
        ("Registros donde carpeta != carpeta_dia", "SELECT COUNT(*) FROM asistencia WHERE carpeta != carpeta_dia AND carpeta IS NOT NULL AND carpeta_dia IS NOT NULL"),
    ]
    
    for description, query in queries:
        cursor.execute(query)
        count = cursor.fetchone()[0]
        print(f"{description:<40}: {count}")
    
    cursor.close()
    print()

def main():
    """Función principal"""
    print("EXAMINANDO TABLA ASISTENCIA")
    print("=" * 60)
    
    connection = connect_to_database()
    if not connection:
        print("No se pudo conectar a la base de datos")
        return
    
    try:
        examine_table_structure(connection)
        examine_carpeta_values(connection)
        examine_carpeta_dia_values(connection)
        examine_technician_classification(connection)
        examine_sample_data(connection)
        examine_attendance_logic(connection)
        
        print("ANÁLISIS COMPLETADO")
        print("=" * 60)
        
    except Error as e:
        print(f"Error durante el análisis: {e}")
    
    finally:
        if connection.is_connected():
            connection.close()
            print("Conexión a la base de datos cerrada.")

if __name__ == "__main__":
    main()