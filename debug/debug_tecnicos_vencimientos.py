#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar por qué no aparecen los nombres de técnicos 
en el módulo de vencimientos.
"""

import mysql.connector
import sys
import os
from datetime import datetime

# Función de conexión a la base de datos (igual que en main.py)
def get_db_connection():
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

def verificar_tablas_vencimientos():
    """Verificar datos en las tablas de vencimientos"""
    print("=" * 80)
    print("🔍 DIAGNÓSTICO DE TÉCNICOS EN VENCIMIENTOS")
    print("=" * 80)
    
    connection = get_db_connection()
    if not connection:
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 1. Verificar tabla recurso_operativo
        print("\n1️⃣ VERIFICANDO TABLA RECURSO_OPERATIVO")
        print("-" * 50)
        
        cursor.execute("SELECT COUNT(*) as total FROM recurso_operativo")
        total_recursos = cursor.fetchone()['total']
        print(f"📊 Total de registros en recurso_operativo: {total_recursos}")
        
        cursor.execute("""
            SELECT id_codigo_consumidor, nombre, id_roles 
            FROM recurso_operativo 
            WHERE nombre IS NOT NULL AND nombre != ''
            LIMIT 10
        """)
        recursos = cursor.fetchall()
        
        print("\n📋 Primeros 10 técnicos en recurso_operativo:")
        for recurso in recursos:
            print(f"  ID: {recurso['id_codigo_consumidor']} | Nombre: {recurso['nombre']} | Rol: {recurso['id_roles']}")
        
        # 2. Verificar tabla mpa_soat
        print("\n\n2️⃣ VERIFICANDO TABLA MPA_SOAT")
        print("-" * 50)
        
        cursor.execute("SELECT COUNT(*) as total FROM mpa_soat")
        total_soat = cursor.fetchone()['total']
        print(f"📊 Total de registros en mpa_soat: {total_soat}")
        
        cursor.execute("""
            SELECT id_mpa_soat, placa, tecnico_asignado, fecha_vencimiento, estado
            FROM mpa_soat 
            WHERE fecha_vencimiento IS NOT NULL
            LIMIT 5
        """)
        soats = cursor.fetchall()
        
        print("\n📋 Primeros 5 registros de SOAT:")
        for soat in soats:
            print(f"  ID: {soat['id_mpa_soat']} | Placa: {soat['placa']} | Técnico: {soat['tecnico_asignado']} | Vencimiento: {soat['fecha_vencimiento']}")
        
        # 3. Verificar tabla mpa_tecnico_mecanica
        print("\n\n3️⃣ VERIFICANDO TABLA MPA_TECNICO_MECANICA")
        print("-" * 50)
        
        cursor.execute("SELECT COUNT(*) as total FROM mpa_tecnico_mecanica")
        total_tm = cursor.fetchone()['total']
        print(f"📊 Total de registros en mpa_tecnico_mecanica: {total_tm}")
        
        cursor.execute("""
            SELECT id_mpa_tecnico_mecanica, placa, tecnico_asignado, fecha_vencimiento, estado
            FROM mpa_tecnico_mecanica 
            WHERE fecha_vencimiento IS NOT NULL
            LIMIT 5
        """)
        tecnicos_mecanica = cursor.fetchall()
        
        print("\n📋 Primeros 5 registros de Técnico Mecánica:")
        for tm in tecnicos_mecanica:
            print(f"  ID: {tm['id_mpa_tecnico_mecanica']} | Placa: {tm['placa']} | Técnico: {tm['tecnico_asignado']} | Vencimiento: {tm['fecha_vencimiento']}")
        
        # 4. Verificar tabla mpa_licencia_conducir
        print("\n\n4️⃣ VERIFICANDO TABLA MPA_LICENCIA_CONDUCIR")
        print("-" * 50)
        
        cursor.execute("SELECT COUNT(*) as total FROM mpa_licencia_conducir")
        total_lc = cursor.fetchone()['total']
        print(f"📊 Total de registros en mpa_licencia_conducir: {total_lc}")
        
        cursor.execute("""
            SELECT id_mpa_licencia_conducir, tecnico, fecha_vencimiento
            FROM mpa_licencia_conducir 
            WHERE fecha_vencimiento IS NOT NULL
            LIMIT 5
        """)
        licencias = cursor.fetchall()
        
        print("\n📋 Primeros 5 registros de Licencias de Conducir:")
        for lc in licencias:
            print(f"  ID: {lc['id_mpa_licencia_conducir']} | Técnico: {lc['tecnico']} | Vencimiento: {lc['fecha_vencimiento']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def probar_consultas_join():
    """Probar las consultas JOIN que usa la API de vencimientos"""
    print("\n\n5️⃣ PROBANDO CONSULTAS JOIN DE LA API")
    print("-" * 50)
    
    connection = get_db_connection()
    if not connection:
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Consulta SOAT con JOIN
        print("\n🔗 CONSULTA SOAT CON JOIN:")
        query_soat = """
        SELECT 
            s.id_mpa_soat as id,
            s.placa,
            s.fecha_vencimiento,
            s.tecnico_asignado,
            ro.nombre as tecnico_nombre,
            'SOAT' as tipo,
            s.estado
        FROM mpa_soat s
        LEFT JOIN recurso_operativo ro ON s.tecnico_asignado = ro.id_codigo_consumidor
        WHERE s.fecha_vencimiento IS NOT NULL
        ORDER BY s.fecha_vencimiento ASC
        LIMIT 5
        """
        
        cursor.execute(query_soat)
        resultados_soat = cursor.fetchall()
        
        for resultado in resultados_soat:
            print(f"  Placa: {resultado['placa']} | Técnico ID: {resultado['tecnico_asignado']} | Nombre: {resultado['tecnico_nombre']} | Tipo: {resultado['tipo']}")
        
        # Consulta Técnico Mecánica con JOIN
        print("\n🔗 CONSULTA TÉCNICO MECÁNICA CON JOIN:")
        query_tm = """
        SELECT 
            tm.id_mpa_tecnico_mecanica as id,
            tm.placa,
            tm.fecha_vencimiento,
            tm.tecnico_asignado,
            ro.nombre as tecnico_nombre,
            'Técnico Mecánica' as tipo,
            tm.estado
        FROM mpa_tecnico_mecanica tm
        LEFT JOIN recurso_operativo ro ON tm.tecnico_asignado = ro.id_codigo_consumidor
        WHERE tm.fecha_vencimiento IS NOT NULL
        ORDER BY tm.fecha_vencimiento ASC
        LIMIT 5
        """
        
        cursor.execute(query_tm)
        resultados_tm = cursor.fetchall()
        
        for resultado in resultados_tm:
            print(f"  Placa: {resultado['placa']} | Técnico ID: {resultado['tecnico_asignado']} | Nombre: {resultado['tecnico_nombre']} | Tipo: {resultado['tipo']}")
        
        # Consulta Licencias de Conducir con JOIN
        print("\n🔗 CONSULTA LICENCIAS DE CONDUCIR CON JOIN:")
        query_lc = """
        SELECT 
            lc.id_mpa_licencia_conducir as id,
            lc.fecha_vencimiento,
            lc.tecnico,
            ro.nombre as tecnico_nombre,
            'Licencia de Conducir' as tipo
        FROM mpa_licencia_conducir lc
        LEFT JOIN recurso_operativo ro ON lc.tecnico = ro.id_codigo_consumidor
        WHERE lc.fecha_vencimiento IS NOT NULL
        ORDER BY lc.fecha_vencimiento ASC
        LIMIT 5
        """
        
        cursor.execute(query_lc)
        resultados_lc = cursor.fetchall()
        
        for resultado in resultados_lc:
            print(f"  Técnico ID: {resultado['tecnico']} | Nombre: {resultado['tecnico_nombre']} | Tipo: {resultado['tipo']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante las consultas JOIN: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def verificar_coincidencias():
    """Verificar coincidencias entre las tablas"""
    print("\n\n6️⃣ VERIFICANDO COINCIDENCIAS ENTRE TABLAS")
    print("-" * 50)
    
    connection = get_db_connection()
    if not connection:
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Verificar técnicos únicos en mpa_soat
        print("\n📊 TÉCNICOS ÚNICOS EN MPA_SOAT:")
        cursor.execute("""
            SELECT DISTINCT tecnico_asignado, COUNT(*) as cantidad
            FROM mpa_soat 
            WHERE tecnico_asignado IS NOT NULL
            GROUP BY tecnico_asignado
            ORDER BY cantidad DESC
            LIMIT 10
        """)
        tecnicos_soat = cursor.fetchall()
        
        for tecnico in tecnicos_soat:
            print(f"  Técnico ID: {tecnico['tecnico_asignado']} | Cantidad de SOATs: {tecnico['cantidad']}")
        
        # Verificar técnicos únicos en mpa_tecnico_mecanica
        print("\n📊 TÉCNICOS ÚNICOS EN MPA_TECNICO_MECANICA:")
        cursor.execute("""
            SELECT DISTINCT tecnico_asignado, COUNT(*) as cantidad
            FROM mpa_tecnico_mecanica 
            WHERE tecnico_asignado IS NOT NULL
            GROUP BY tecnico_asignado
            ORDER BY cantidad DESC
            LIMIT 10
        """)
        tecnicos_tm = cursor.fetchall()
        
        for tecnico in tecnicos_tm:
            print(f"  Técnico ID: {tecnico['tecnico_asignado']} | Cantidad de TMs: {tecnico['cantidad']}")
        
        # Verificar técnicos únicos en mpa_licencia_conducir
        print("\n📊 TÉCNICOS ÚNICOS EN MPA_LICENCIA_CONDUCIR:")
        cursor.execute("""
            SELECT DISTINCT tecnico, COUNT(*) as cantidad
            FROM mpa_licencia_conducir 
            WHERE tecnico IS NOT NULL
            GROUP BY tecnico
            ORDER BY cantidad DESC
            LIMIT 10
        """)
        tecnicos_lc = cursor.fetchall()
        
        for tecnico in tecnicos_lc:
            print(f"  Técnico ID: {tecnico['tecnico']} | Cantidad de Licencias: {tecnico['cantidad']}")
        
        # Verificar registros sin coincidencia
        print("\n❌ REGISTROS SIN COINCIDENCIA EN RECURSO_OPERATIVO:")
        
        # SOAT sin coincidencia
        cursor.execute("""
            SELECT s.tecnico_asignado, COUNT(*) as cantidad
            FROM mpa_soat s
            LEFT JOIN recurso_operativo ro ON s.tecnico_asignado = ro.id_codigo_consumidor
            WHERE s.tecnico_asignado IS NOT NULL AND ro.id_codigo_consumidor IS NULL
            GROUP BY s.tecnico_asignado
        """)
        soat_sin_coincidencia = cursor.fetchall()
        
        if soat_sin_coincidencia:
            print("  SOAT sin técnico en recurso_operativo:")
            for registro in soat_sin_coincidencia:
                print(f"    Técnico ID: {registro['tecnico_asignado']} | Cantidad: {registro['cantidad']}")
        else:
            print("  ✅ Todos los técnicos de SOAT tienen coincidencia en recurso_operativo")
        
        # Técnico Mecánica sin coincidencia
        cursor.execute("""
            SELECT tm.tecnico_asignado, COUNT(*) as cantidad
            FROM mpa_tecnico_mecanica tm
            LEFT JOIN recurso_operativo ro ON tm.tecnico_asignado = ro.id_codigo_consumidor
            WHERE tm.tecnico_asignado IS NOT NULL AND ro.id_codigo_consumidor IS NULL
            GROUP BY tm.tecnico_asignado
        """)
        tm_sin_coincidencia = cursor.fetchall()
        
        if tm_sin_coincidencia:
            print("  TÉCNICO MECÁNICA sin técnico en recurso_operativo:")
            for registro in tm_sin_coincidencia:
                print(f"    Técnico ID: {registro['tecnico_asignado']} | Cantidad: {registro['cantidad']}")
        else:
            print("  ✅ Todos los técnicos de Técnico Mecánica tienen coincidencia en recurso_operativo")
        
        # Licencias sin coincidencia
        cursor.execute("""
            SELECT lc.tecnico, COUNT(*) as cantidad
            FROM mpa_licencia_conducir lc
            LEFT JOIN recurso_operativo ro ON lc.tecnico = ro.id_codigo_consumidor
            WHERE lc.tecnico IS NOT NULL AND ro.id_codigo_consumidor IS NULL
            GROUP BY lc.tecnico
        """)
        lc_sin_coincidencia = cursor.fetchall()
        
        if lc_sin_coincidencia:
            print("  LICENCIAS DE CONDUCIR sin técnico en recurso_operativo:")
            for registro in lc_sin_coincidencia:
                print(f"    Técnico ID: {registro['tecnico']} | Cantidad: {registro['cantidad']}")
        else:
            print("  ✅ Todos los técnicos de Licencias tienen coincidencia en recurso_operativo")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la verificación de coincidencias: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def main():
    """Función principal del diagnóstico"""
    print(f"🚀 Iniciando diagnóstico - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ejecutar todas las verificaciones
    verificar_tablas_vencimientos()
    probar_consultas_join()
    verificar_coincidencias()
    
    print("\n" + "=" * 80)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("=" * 80)
    print("\n💡 RECOMENDACIONES:")
    print("1. Verificar si los campos tecnico_asignado/tecnico tienen valores válidos")
    print("2. Verificar si existen los técnicos en la tabla recurso_operativo")
    print("3. Verificar si los JOIN están funcionando correctamente")
    print("4. Revisar la lógica de la API de vencimientos en main.py")

if __name__ == "__main__":
    main()