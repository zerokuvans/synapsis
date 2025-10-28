#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para verificar los vencimientos
"""

import mysql.connector

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            sql_mode=''  # Desactivar modo estricto
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def main():
    print("=== Verificación simple de vencimientos ===\n")
    
    connection = get_db_connection()
    if not connection:
        print("No se pudo conectar a la base de datos")
        return
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # 1. Total de registros en cada tabla
        print("1. Total de registros por tabla:")
        
        cursor.execute("SELECT COUNT(*) as total FROM mpa_soat")
        soat_total = cursor.fetchone()['total']
        print(f"   mpa_soat: {soat_total}")
        
        cursor.execute("SELECT COUNT(*) as total FROM mpa_tecnico_mecanica")
        tm_total = cursor.fetchone()['total']
        print(f"   mpa_tecnico_mecanica: {tm_total}")
        
        cursor.execute("SELECT COUNT(*) as total FROM mpa_licencia_conducir")
        lc_total = cursor.fetchone()['total']
        print(f"   mpa_licencia_conducir: {lc_total}")
        
        # 2. Registros con fechas válidas (no nulas y no 0000-00-00)
        print("\n2. Registros con fechas de vencimiento válidas:")
        
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM mpa_soat 
            WHERE fecha_vencimiento IS NOT NULL 
            AND fecha_vencimiento NOT LIKE '0000-00-00%'
            AND fecha_vencimiento > '1900-01-01'
        """)
        soat_validas = cursor.fetchone()['total']
        print(f"   mpa_soat con fechas válidas: {soat_validas}")
        
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM mpa_tecnico_mecanica 
            WHERE fecha_vencimiento IS NOT NULL 
            AND fecha_vencimiento NOT LIKE '0000-00-00%'
            AND fecha_vencimiento > '1900-01-01'
        """)
        tm_validas = cursor.fetchone()['total']
        print(f"   mpa_tecnico_mecanica con fechas válidas: {tm_validas}")
        
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM mpa_licencia_conducir 
            WHERE fecha_vencimiento IS NOT NULL 
            AND fecha_vencimiento NOT LIKE '0000-00-00%'
            AND fecha_vencimiento > '1900-01-01'
        """)
        lc_validas = cursor.fetchone()['total']
        print(f"   mpa_licencia_conducir con fechas válidas: {lc_validas}")
        
        total_esperado = soat_validas + tm_validas + lc_validas
        print(f"\n   TOTAL ESPERADO: {total_esperado}")
        
        # 3. Verificar estados de técnicos
        print("\n3. Estados en recurso_operativo:")
        cursor.execute("""
            SELECT estado, COUNT(*) as cantidad 
            FROM recurso_operativo 
            GROUP BY estado 
            ORDER BY cantidad DESC
        """)
        estados = cursor.fetchall()
        for estado in estados:
            print(f"   {estado['estado']}: {estado['cantidad']}")
        
        # 4. Verificar técnicos asignados en SOAT
        print("\n4. Técnicos en SOAT:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total_con_tecnico,
                COUNT(CASE WHEN tecnico_asignado IS NULL OR TRIM(tecnico_asignado) = '' THEN 1 END) as sin_tecnico
            FROM mpa_soat 
            WHERE fecha_vencimiento IS NOT NULL 
            AND fecha_vencimiento NOT LIKE '0000-00-00%'
            AND fecha_vencimiento > '1900-01-01'
        """)
        soat_tecnicos = cursor.fetchone()
        print(f"   Con técnico asignado: {soat_tecnicos['total_con_tecnico'] - soat_tecnicos['sin_tecnico']}")
        print(f"   Sin técnico asignado: {soat_tecnicos['sin_tecnico']}")
        
        # 5. Verificar técnicos inactivos que podrían estar siendo filtrados
        print("\n5. SOAT con técnicos inactivos:")
        cursor.execute("""
            SELECT COUNT(*) as cantidad
            FROM mpa_soat s
            LEFT JOIN recurso_operativo ro ON s.tecnico_asignado = ro.id_codigo_consumidor
            WHERE s.fecha_vencimiento IS NOT NULL 
            AND s.fecha_vencimiento NOT LIKE '0000-00-00%'
            AND s.fecha_vencimiento > '1900-01-01'
            AND s.tecnico_asignado IS NOT NULL
            AND TRIM(s.tecnico_asignado) != ''
            AND (ro.estado IS NULL OR ro.estado != 'Activo')
        """)
        soat_inactivos = cursor.fetchone()['cantidad']
        print(f"   SOAT con técnicos inactivos: {soat_inactivos}")
        
        print("\n6. Técnico Mecánica con técnicos inactivos:")
        cursor.execute("""
            SELECT COUNT(*) as cantidad
            FROM mpa_tecnico_mecanica tm
            LEFT JOIN recurso_operativo ro ON tm.tecnico_asignado = ro.id_codigo_consumidor
            WHERE tm.fecha_vencimiento IS NOT NULL 
            AND tm.fecha_vencimiento NOT LIKE '0000-00-00%'
            AND tm.fecha_vencimiento > '1900-01-01'
            AND tm.tecnico_asignado IS NOT NULL
            AND TRIM(tm.tecnico_asignado) != ''
            AND (ro.estado IS NULL OR ro.estado != 'Activo')
        """)
        tm_inactivos = cursor.fetchone()['cantidad']
        print(f"   TM con técnicos inactivos: {tm_inactivos}")
        
        print("\n7. Licencias con técnicos inactivos:")
        cursor.execute("""
            SELECT COUNT(*) as cantidad
            FROM mpa_licencia_conducir lc
            LEFT JOIN recurso_operativo ro ON lc.tecnico = ro.id_codigo_consumidor
            WHERE lc.fecha_vencimiento IS NOT NULL 
            AND lc.fecha_vencimiento NOT LIKE '0000-00-00%'
            AND lc.fecha_vencimiento > '1900-01-01'
            AND lc.tecnico IS NOT NULL
            AND TRIM(lc.tecnico) != ''
            AND (ro.estado IS NULL OR ro.estado != 'Activo')
        """)
        lc_inactivos = cursor.fetchone()['cantidad']
        print(f"   Licencias con técnicos inactivos: {lc_inactivos}")
        
        total_filtrados = soat_inactivos + tm_inactivos + lc_inactivos
        total_que_deberia_mostrar = total_esperado - total_filtrados
        
        print(f"\n=== RESUMEN ===")
        print(f"Total de vencimientos con fechas válidas: {total_esperado}")
        print(f"Vencimientos con técnicos inactivos (filtrados): {total_filtrados}")
        print(f"Vencimientos que DEBERÍA mostrar el API: {total_que_deberia_mostrar}")
        print(f"Vencimientos que ESTÁ mostrando el API: 3")
        
        if total_que_deberia_mostrar != 3:
            print(f"\n❌ HAY UN PROBLEMA: Se esperan {total_que_deberia_mostrar} pero solo se muestran 3")
        else:
            print(f"\n✅ Los números coinciden")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()