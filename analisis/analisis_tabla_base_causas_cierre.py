#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis detallado de la tabla base_causas_cierre existente
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from collections import Counter

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

def analizar_estructura_tabla():
    """Analizar la estructura completa de la tabla base_causas_cierre"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        print("=== ANÁLISIS DETALLADO DE LA TABLA base_causas_cierre ===")
        
        # 1. Estructura de la tabla
        print("\n1. ESTRUCTURA DE LA TABLA:")
        cursor.execute("DESCRIBE base_causas_cierre")
        columnas = cursor.fetchall()
        
        for columna in columnas:
            print(f"   {columna[0]:35} | {columna[1]:20} | Key: {columna[3]:3} | Null: {columna[2]:3} | Default: {columna[4]}")
        
        # 2. Estadísticas generales
        print("\n2. ESTADÍSTICAS GENERALES:")
        cursor.execute("SELECT COUNT(*) FROM base_causas_cierre")
        total = cursor.fetchone()[0]
        print(f"   Total de registros: {total}")
        
        # 3. Análisis de tecnologías
        print("\n3. ANÁLISIS DE TECNOLOGÍAS:")
        cursor.execute("SELECT tecnologia_causas_cierre, COUNT(*) as cantidad FROM base_causas_cierre GROUP BY tecnologia_causas_cierre ORDER BY cantidad DESC")
        tecnologias = cursor.fetchall()
        print("   Tecnologías disponibles:")
        for tech in tecnologias:
            print(f"     - {tech[0]:20} : {tech[1]:3} registros")
        
        # 4. Análisis de agrupaciones
        print("\n4. ANÁLISIS DE AGRUPACIONES:")
        cursor.execute("SELECT agrupaciones_causas_cierre, COUNT(*) as cantidad FROM base_causas_cierre GROUP BY agrupaciones_causas_cierre ORDER BY cantidad DESC")
        agrupaciones = cursor.fetchall()
        print("   Agrupaciones disponibles:")
        for agrup in agrupaciones:
            print(f"     - {agrup[0]:25} : {agrup[1]:3} registros")
        
        # 5. Análisis de grupos
        print("\n5. ANÁLISIS DE GRUPOS:")
        cursor.execute("SELECT todos_los_grupos_causas_cierre, COUNT(*) as cantidad FROM base_causas_cierre GROUP BY todos_los_grupos_causas_cierre ORDER BY cantidad DESC")
        grupos = cursor.fetchall()
        print("   Grupos disponibles:")
        for grupo in grupos:
            print(f"     - {grupo[0]:25} : {grupo[1]:3} registros")
        
        # 6. Análisis de códigos más comunes
        print("\n6. CÓDIGOS MÁS COMUNES:")
        cursor.execute("SELECT codigo_causas_cierre, nombre_causas_cierre, COUNT(*) as cantidad FROM base_causas_cierre GROUP BY codigo_causas_cierre, nombre_causas_cierre ORDER BY cantidad DESC LIMIT 10")
        codigos = cursor.fetchall()
        print("   Top 10 códigos:")
        for codigo in codigos:
            print(f"     - {codigo[0]:8} | {codigo[1]:40} | {codigo[2]} registros")
        
        # 7. Muestra de datos completos
        print("\n7. MUESTRA DE DATOS COMPLETOS:")
        cursor.execute("SELECT * FROM base_causas_cierre LIMIT 3")
        datos = cursor.fetchall()
        
        columnas_nombres = [desc[0] for desc in cursor.description]
        print("   Columnas:", columnas_nombres)
        
        for i, registro in enumerate(datos, 1):
            print(f"\n   Registro {i}:")
            for j, valor in enumerate(registro):
                print(f"     {columnas_nombres[j]:35} : {valor}")
        
        # 8. Análisis de búsqueda de texto
        print("\n8. ANÁLISIS PARA BÚSQUEDA:")
        cursor.execute("SELECT COUNT(*) FROM base_causas_cierre WHERE nombre_causas_cierre LIKE '%TECNICA%'")
        tecnica_count = cursor.fetchone()[0]
        print(f"   Registros con 'TECNICA' en nombre: {tecnica_count}")
        
        cursor.execute("SELECT COUNT(*) FROM base_causas_cierre WHERE nombre_causas_cierre LIKE '%VISITA%'")
        visita_count = cursor.fetchone()[0]
        print(f"   Registros con 'VISITA' en nombre: {visita_count}")
        
        cursor.execute("SELECT COUNT(*) FROM base_causas_cierre WHERE instrucciones_de_uso_causas_cierre LIKE '%COMPLETAR%'")
        completar_count = cursor.fetchone()[0]
        print(f"   Registros con 'COMPLETAR' en instrucciones: {completar_count}")
        
        # 9. Recomendaciones para el módulo analistas
        print("\n9. RECOMENDACIONES PARA EL MÓDULO ANALISTAS:")
        print("   ✓ La tabla ya existe con 178 registros")
        print("   ✓ Estructura actual usa campos de texto en lugar de IDs para relaciones")
        print("   ✓ Campos principales para búsqueda:")
        print("     - codigo_causas_cierre (código único)")
        print("     - nombre_causas_cierre (descripción principal)")
        print("     - instrucciones_de_uso_causas_cierre (texto detallado)")
        print("   ✓ Campos para filtros:")
        print("     - tecnologia_causas_cierre (filtro de tecnología)")
        print("     - agrupaciones_causas_cierre (filtro de agrupación)")
        print("     - todos_los_grupos_causas_cierre (filtro de grupo)")
        print("   ✓ No es necesario crear tablas adicionales")
        print("   ✓ Se puede implementar búsqueda FULLTEXT en campos de texto")
        
        return {
            'total_registros': total,
            'tecnologias': [t[0] for t in tecnologias],
            'agrupaciones': [a[0] for a in agrupaciones],
            'grupos': [g[0] for g in grupos],
            'estructura_columnas': columnas_nombres
        }
        
    except Error as e:
        print(f"Error de MySQL: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def generar_consultas_ejemplo():
    """Generar consultas SQL de ejemplo para el módulo analistas"""
    print("\n=== CONSULTAS SQL DE EJEMPLO PARA EL MÓDULO ANALISTAS ===")
    
    consultas = {
        "Búsqueda por texto": """
            SELECT codigo_causas_cierre, nombre_causas_cierre, tecnologia_causas_cierre, 
                   agrupaciones_causas_cierre, todos_los_grupos_causas_cierre
            FROM base_causas_cierre 
            WHERE nombre_causas_cierre LIKE '%{texto_busqueda}%' 
               OR codigo_causas_cierre LIKE '%{texto_busqueda}%'
               OR instrucciones_de_uso_causas_cierre LIKE '%{texto_busqueda}%'
            ORDER BY codigo_causas_cierre
        """,
        
        "Filtro por tecnología": """
            SELECT codigo_causas_cierre, nombre_causas_cierre, agrupaciones_causas_cierre, todos_los_grupos_causas_cierre
            FROM base_causas_cierre 
            WHERE tecnologia_causas_cierre = '{tecnologia_seleccionada}'
            ORDER BY codigo_causas_cierre
        """,
        
        "Filtro por agrupación": """
            SELECT codigo_causas_cierre, nombre_causas_cierre, tecnologia_causas_cierre, todos_los_grupos_causas_cierre
            FROM base_causas_cierre 
            WHERE agrupaciones_causas_cierre = '{agrupacion_seleccionada}'
            ORDER BY codigo_causas_cierre
        """,
        
        "Filtro por grupo": """
            SELECT codigo_causas_cierre, nombre_causas_cierre, tecnologia_causas_cierre, agrupaciones_causas_cierre
            FROM base_causas_cierre 
            WHERE todos_los_grupos_causas_cierre = '{grupo_seleccionado}'
            ORDER BY codigo_causas_cierre
        """,
        
        "Búsqueda combinada": """
            SELECT codigo_causas_cierre, nombre_causas_cierre, tecnologia_causas_cierre, 
                   agrupaciones_causas_cierre, todos_los_grupos_causas_cierre
            FROM base_causas_cierre 
            WHERE (nombre_causas_cierre LIKE '%{texto_busqueda}%' 
                   OR codigo_causas_cierre LIKE '%{texto_busqueda}%'
                   OR instrucciones_de_uso_causas_cierre LIKE '%{texto_busqueda}%')
              AND tecnologia_causas_cierre = '{tecnologia_seleccionada}'
              AND agrupaciones_causas_cierre = '{agrupacion_seleccionada}'
              AND todos_los_grupos_causas_cierre = '{grupo_seleccionado}'
            ORDER BY codigo_causas_cierre
        """,
        
        "Obtener opciones para filtros": """
            -- Para dropdown de tecnologías
            SELECT DISTINCT tecnologia_causas_cierre 
            FROM base_causas_cierre 
            WHERE tecnologia_causas_cierre IS NOT NULL 
            ORDER BY tecnologia_causas_cierre;
            
            -- Para dropdown de agrupaciones
            SELECT DISTINCT agrupaciones_causas_cierre 
            FROM base_causas_cierre 
            WHERE agrupaciones_causas_cierre IS NOT NULL 
            ORDER BY agrupaciones_causas_cierre;
            
            -- Para dropdown de grupos
            SELECT DISTINCT todos_los_grupos_causas_cierre 
            FROM base_causas_cierre 
            WHERE todos_los_grupos_causas_cierre IS NOT NULL 
            ORDER BY todos_los_grupos_causas_cierre;
        """
    }
    
    for nombre, consulta in consultas.items():
        print(f"\n{nombre}:")
        print(consulta)

def main():
    """Función principal"""
    datos = analizar_estructura_tabla()
    if datos:
        generar_consultas_ejemplo()
        
        print("\n=== RESUMEN PARA DESARROLLO ===")
        print(f"✓ Tabla base_causas_cierre analizada exitosamente")
        print(f"✓ {datos['total_registros']} registros disponibles")
        print(f"✓ {len(datos['tecnologias'])} tecnologías diferentes")
        print(f"✓ {len(datos['agrupaciones'])} agrupaciones diferentes")
        print(f"✓ {len(datos['grupos'])} grupos diferentes")
        print(f"✓ Estructura de datos lista para implementar el módulo analistas")

if __name__ == "__main__":
    main()