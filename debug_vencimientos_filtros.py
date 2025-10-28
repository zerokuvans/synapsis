#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debuggear los filtros en la función api_vencimientos_consolidados
"""

import mysql.connector
from datetime import datetime, date
import pytz

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

def main():
    print("=== DEBUG: Analizando filtros en vencimientos ===\n")
    
    connection = get_db_connection()
    if not connection:
        print("No se pudo conectar a la base de datos")
        return
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # 1. Verificar SOAT sin filtros
        print("1. SOAT - Todos los registros:")
        query_soat_all = """
        SELECT COUNT(*) as total
        FROM mpa_soat s
        WHERE s.fecha_vencimiento IS NOT NULL
          AND s.fecha_vencimiento != '0000-00-00'
        """
        cursor.execute(query_soat_all)
        result = cursor.fetchone()
        print(f"   Total SOAT con fecha válida: {result['total']}")
        
        # 2. Verificar SOAT con filtros de técnico
        print("\n2. SOAT - Con filtros de técnico activo:")
        query_soat_filtered = """
        SELECT COUNT(*) as total
        FROM mpa_soat s
        LEFT JOIN recurso_operativo ro ON s.tecnico_asignado = ro.id_codigo_consumidor
        WHERE s.fecha_vencimiento IS NOT NULL
          AND s.fecha_vencimiento != '0000-00-00'
          AND (
              s.tecnico_asignado IS NULL
              OR TRIM(s.tecnico_asignado) = ''
              OR ro.estado = 'Activo'
          )
        """
        cursor.execute(query_soat_filtered)
        result = cursor.fetchone()
        print(f"   Total SOAT con filtros: {result['total']}")
        
        # 3. Verificar qué técnicos están inactivos
        print("\n3. SOAT - Técnicos inactivos que están siendo filtrados:")
        query_soat_inactive = """
        SELECT s.tecnico_asignado, ro.nombre, ro.estado, COUNT(*) as cantidad
        FROM mpa_soat s
        LEFT JOIN recurso_operativo ro ON s.tecnico_asignado = ro.id_codigo_consumidor
        WHERE s.fecha_vencimiento IS NOT NULL
          AND s.fecha_vencimiento != '0000-00-00'
          AND s.tecnico_asignado IS NOT NULL
          AND TRIM(s.tecnico_asignado) != ''
          AND (ro.estado IS NULL OR ro.estado != 'Activo')
        GROUP BY s.tecnico_asignado, ro.nombre, ro.estado
        """
        cursor.execute(query_soat_inactive)
        inactive_soat = cursor.fetchall()
        if inactive_soat:
            for row in inactive_soat:
                print(f"   Técnico: {row['tecnico_asignado']} - {row['nombre']} - Estado: {row['estado']} - Cantidad: {row['cantidad']}")
        else:
            print("   No hay SOAT con técnicos inactivos")
        
        # 4. Verificar Técnico Mecánica sin filtros
        print("\n4. Técnico Mecánica - Todos los registros:")
        query_tm_all = """
        SELECT COUNT(*) as total
        FROM mpa_tecnico_mecanica tm
        WHERE tm.fecha_vencimiento IS NOT NULL
          AND tm.fecha_vencimiento NOT IN ('0000-00-00', '1900-01-01')
          AND tm.fecha_vencimiento > '1900-01-01'
        """
        cursor.execute(query_tm_all)
        result = cursor.fetchone()
        print(f"   Total TM con fecha válida: {result['total']}")
        
        # 5. Verificar Técnico Mecánica con filtros
        print("\n5. Técnico Mecánica - Con filtros de técnico activo:")
        query_tm_filtered = """
        SELECT COUNT(*) as total
        FROM mpa_tecnico_mecanica tm
        LEFT JOIN recurso_operativo ro ON tm.tecnico_asignado = ro.id_codigo_consumidor
        WHERE tm.fecha_vencimiento IS NOT NULL
          AND tm.fecha_vencimiento NOT IN ('0000-00-00', '1900-01-01')
          AND tm.fecha_vencimiento > '1900-01-01'
          AND (
              tm.tecnico_asignado IS NULL
              OR TRIM(tm.tecnico_asignado) = ''
              OR ro.estado = 'Activo'
          )
        """
        cursor.execute(query_tm_filtered)
        result = cursor.fetchone()
        print(f"   Total TM con filtros: {result['total']}")
        
        # 6. Verificar Licencias sin filtros
        print("\n6. Licencias de Conducir - Todos los registros:")
        query_lc_all = """
        SELECT COUNT(*) as total
        FROM mpa_licencia_conducir lc
        WHERE lc.fecha_vencimiento IS NOT NULL
          AND lc.fecha_vencimiento NOT IN ('0000-00-00', '1900-01-01')
          AND lc.fecha_vencimiento > '1900-01-01'
        """
        cursor.execute(query_lc_all)
        result = cursor.fetchone()
        print(f"   Total Licencias con fecha válida: {result['total']}")
        
        # 7. Verificar Licencias con filtros
        print("\n7. Licencias de Conducir - Con filtros de técnico activo:")
        query_lc_filtered = """
        SELECT COUNT(*) as total
        FROM mpa_licencia_conducir lc
        LEFT JOIN recurso_operativo ro ON lc.tecnico = ro.id_codigo_consumidor
        WHERE lc.fecha_vencimiento IS NOT NULL
          AND lc.fecha_vencimiento NOT IN ('0000-00-00', '1900-01-01')
          AND lc.fecha_vencimiento > '1900-01-01'
          AND (
              lc.tecnico IS NULL
              OR TRIM(lc.tecnico) = ''
              OR ro.estado = 'Activo'
          )
        """
        cursor.execute(query_lc_filtered)
        result = cursor.fetchone()
        print(f"   Total Licencias con filtros: {result['total']}")
        
        # 8. Verificar estados de técnicos en recurso_operativo
        print("\n8. Estados de técnicos en recurso_operativo:")
        query_estados = """
        SELECT estado, COUNT(*) as cantidad
        FROM recurso_operativo
        GROUP BY estado
        ORDER BY cantidad DESC
        """
        cursor.execute(query_estados)
        estados = cursor.fetchall()
        for estado in estados:
            print(f"   Estado: {estado['estado']} - Cantidad: {estado['cantidad']}")
        
        print("\n=== Resumen ===")
        print("Si los números 'Con filtros' son menores que 'Todos los registros',")
        print("significa que el filtro de técnicos activos está ocultando vencimientos.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()