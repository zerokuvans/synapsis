#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para investigar duplicados en la tabla asistencia
"""

import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def investigar_duplicados():
    """Investigar duplicados en la tabla asistencia"""
    connection = get_db_connection()
    if not connection:
        print("❌ No se pudo conectar a la base de datos")
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print("🔍 INVESTIGANDO DUPLICADOS EN TABLA ASISTENCIA")
        print("=" * 60)
        
        # 1. Buscar duplicados específicos para ARNACHE ARIAS JUAN CARLOS
        print("\n1. DUPLICADOS PARA ARNACHE ARIAS JUAN CARLOS:")
        query1 = """
        SELECT id_asistencia, cedula, tecnico, super, fecha_asistencia, 
               carpeta, carpeta_dia, oks, valor
        FROM asistencia 
        WHERE tecnico = 'ARNACHE ARIAS JUAN CARLOS' 
        AND super = 'SILVA CASTRO DANIEL ALBERTO' 
        AND fecha_asistencia = '2025-01-08'
        ORDER BY id_asistencia
        """
        cursor.execute(query1)
        resultados1 = cursor.fetchall()
        
        if resultados1:
            print(f"   Encontrados {len(resultados1)} registros:")
            for registro in resultados1:
                print(f"   ID: {registro['id_asistencia']}, Cédula: {registro['cedula']}, "
                      f"Carpeta: {registro['carpeta']}, OK's: {registro['oks']}, Valor: {registro['valor']}")
        else:
            print("   No se encontraron registros")
        
        # 2. Buscar duplicados específicos para RAMON SANTOS CHOLES
        print("\n2. DUPLICADOS PARA RAMON SANTOS CHOLES:")
        query2 = """
        SELECT id_asistencia, cedula, tecnico, super, fecha_asistencia, 
               carpeta, carpeta_dia, oks, valor
        FROM asistencia 
        WHERE tecnico = 'RAMON SANTOS CHOLES' 
        AND super = 'SILVA CASTRO DANIEL ALBERTO' 
        AND fecha_asistencia = '2025-01-08'
        ORDER BY id_asistencia
        """
        cursor.execute(query2)
        resultados2 = cursor.fetchall()
        
        if resultados2:
            print(f"   Encontrados {len(resultados2)} registros:")
            for registro in resultados2:
                print(f"   ID: {registro['id_asistencia']}, Cédula: {registro['cedula']}, "
                      f"Carpeta: {registro['carpeta']}, OK's: {registro['oks']}, Valor: {registro['valor']}")
        else:
            print("   No se encontraron registros")
        
        # 3. Buscar todos los técnicos con duplicados para la fecha y supervisor
        print("\n3. TODOS LOS TÉCNICOS CON DUPLICADOS:")
        query3 = """
        SELECT cedula, tecnico, COUNT(*) as cantidad_registros
        FROM asistencia 
        WHERE super = 'SILVA CASTRO DANIEL ALBERTO' 
        AND fecha_asistencia = '2025-01-08'
        GROUP BY cedula, tecnico
        HAVING COUNT(*) > 1
        ORDER BY cantidad_registros DESC, tecnico
        """
        cursor.execute(query3)
        resultados3 = cursor.fetchall()
        
        if resultados3:
            print(f"   Técnicos con duplicados: {len(resultados3)}")
            for registro in resultados3:
                print(f"   Cédula: {registro['cedula']}, Técnico: {registro['tecnico']}, "
                      f"Cantidad: {registro['cantidad_registros']}")
        else:
            print("   No se encontraron técnicos con duplicados")
        
        # 4. Estadísticas generales
        print("\n4. ESTADÍSTICAS GENERALES:")
        
        # Total de registros únicos por cédula
        query4a = """
        SELECT COUNT(DISTINCT cedula) as tecnicos_unicos
        FROM asistencia 
        WHERE super = 'SILVA CASTRO DANIEL ALBERTO' 
        AND fecha_asistencia = '2025-01-08'
        """
        cursor.execute(query4a)
        tecnicos_unicos = cursor.fetchone()['tecnicos_unicos']
        
        # Total de registros en la tabla
        query4b = """
        SELECT COUNT(*) as total_registros
        FROM asistencia 
        WHERE super = 'SILVA CASTRO DANIEL ALBERTO' 
        AND fecha_asistencia = '2025-01-08'
        """
        cursor.execute(query4b)
        total_registros = cursor.fetchone()['total_registros']
        
        print(f"   Técnicos únicos (por cédula): {tecnicos_unicos}")
        print(f"   Total de registros: {total_registros}")
        print(f"   Registros duplicados: {total_registros - tecnicos_unicos}")
        
        # 5. Mostrar todos los registros para análisis
        print("\n5. TODOS LOS REGISTROS PARA ANÁLISIS:")
        query5 = """
        SELECT id_asistencia, cedula, tecnico, carpeta, carpeta_dia, oks, valor
        FROM asistencia 
        WHERE super = 'SILVA CASTRO DANIEL ALBERTO' 
        AND fecha_asistencia = '2025-01-08'
        ORDER BY tecnico, id_asistencia
        """
        cursor.execute(query5)
        todos_registros = cursor.fetchall()
        
        print(f"   Total de registros encontrados: {len(todos_registros)}")
        for registro in todos_registros:
            print(f"   ID: {registro['id_asistencia']:>6} | Cédula: {registro['cedula']:>12} | "
                  f"Técnico: {registro['tecnico']:<30} | Carpeta: {registro['carpeta']:<20} | "
                  f"OK's: {registro['oks']:>3} | Valor: {registro['valor']:>10}")
        
    except Error as e:
        print(f"❌ Error ejecutando consultas: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    investigar_duplicados()