#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar problemas con vencimientos
Versión que replica exactamente la lógica del endpoint real
"""

import mysql.connector
import requests
import json
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def conectar_bd():
    """Conectar a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired',
            sql_mode='ALLOW_INVALID_DATES'
        )
        return connection
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        return None

def verificar_tabla_soat(cursor):
    """Verificar datos en tabla mpa_soat usando la lógica real del endpoint"""
    print("\n" + "="*60)
    print("1️⃣ VERIFICANDO TABLA MPA_SOAT")
    print("="*60)
    
    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM mpa_soat")
    total = cursor.fetchone()[0]
    print(f"📊 Total de registros: {total}")
    
    # Query exacta del endpoint
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
      AND s.fecha_vencimiento != '0000-00-00'
      AND (
          s.tecnico_asignado IS NULL
          OR TRIM(s.tecnico_asignado) = ''
          OR ro.estado = 'Activo'
      )
    ORDER BY s.fecha_vencimiento ASC
    """
    
    cursor.execute(query_soat)
    soats = cursor.fetchall()
    validos = len(soats)
    print(f"✅ Registros que pasan filtros del endpoint: {validos}")
    
    # Registros con fecha inválida
    cursor.execute("""
        SELECT COUNT(*) FROM mpa_soat 
        WHERE fecha_vencimiento IS NULL 
        OR fecha_vencimiento = '0000-00-00'
    """)
    invalidos = cursor.fetchone()[0]
    print(f"❌ Registros con fecha inválida: {invalidos}")
    
    # Ejemplos de registros válidos
    print(f"📋 Ejemplos de registros válidos:")
    for i, soat in enumerate(soats[:5], 1):
        print(f"   {i}. Placa: {soat[1]}, Fecha: {soat[2]}, Técnico: {soat[4]}")
    
    return validos

def verificar_tabla_tecnico(cursor):
    """Verificar datos en tabla mpa_tecnico_mecanica usando la lógica real del endpoint"""
    print("\n" + "="*60)
    print("2️⃣ VERIFICANDO TABLA MPA_TECNICO_MECANICA")
    print("="*60)
    
    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM mpa_tecnico_mecanica")
    total = cursor.fetchone()[0]
    print(f"📊 Total de registros: {total}")
    
    # Query exacta del endpoint
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
      AND tm.fecha_vencimiento != '0000-00-00'
      AND (
          tm.tecnico_asignado IS NULL
          OR TRIM(tm.tecnico_asignado) = ''
          OR ro.estado = 'Activo'
      )
    ORDER BY tm.fecha_vencimiento ASC
    """
    
    cursor.execute(query_tm)
    tecnicos = cursor.fetchall()
    validos = len(tecnicos)
    print(f"✅ Registros que pasan filtros del endpoint: {validos}")
    
    # Registros con fecha inválida
    cursor.execute("""
        SELECT COUNT(*) FROM mpa_tecnico_mecanica 
        WHERE fecha_vencimiento IS NULL 
        OR fecha_vencimiento = '0000-00-00'
    """)
    invalidos = cursor.fetchone()[0]
    print(f"❌ Registros con fecha inválida: {invalidos}")
    
    # Ejemplos de registros válidos
    print(f"📋 Ejemplos de registros válidos:")
    for i, tm in enumerate(tecnicos[:5], 1):
        print(f"   {i}. Placa: {tm[1]}, Fecha: {tm[2]}, Técnico: {tm[4]}")
    
    return validos

def verificar_tabla_licencias(cursor):
    """Verificar datos en tabla mpa_licencia_conducir usando la lógica real del endpoint"""
    print("\n" + "="*60)
    print("3️⃣ VERIFICANDO TABLA MPA_LICENCIA_CONDUCIR")
    print("="*60)
    
    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM mpa_licencia_conducir")
    total = cursor.fetchone()[0]
    print(f"📊 Total de registros: {total}")
    
    # Query exacta del endpoint
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
      AND lc.fecha_vencimiento != '0000-00-00'
      AND (
          lc.tecnico IS NULL
          OR TRIM(lc.tecnico) = ''
          OR ro.estado = 'Activo'
      )
    ORDER BY lc.fecha_vencimiento ASC
    """
    
    cursor.execute(query_lc)
    licencias = cursor.fetchall()
    validos = len(licencias)
    print(f"✅ Registros que pasan filtros del endpoint: {validos}")
    
    # Registros con fecha inválida
    cursor.execute("""
        SELECT COUNT(*) FROM mpa_licencia_conducir 
        WHERE fecha_vencimiento IS NULL 
        OR fecha_vencimiento = '0000-00-00'
    """)
    invalidos = cursor.fetchone()[0]
    print(f"❌ Registros con fecha inválida: {invalidos}")
    
    # Ejemplos de registros válidos
    print(f"📋 Ejemplos de registros válidos:")
    for i, lc in enumerate(licencias[:5], 1):
        print(f"   {i}. Fecha: {lc[1]}, Técnico: {lc[3]}")
    
    return validos

def verificar_problemas_joins(cursor):
    """Verificar problemas específicos con JOINs"""
    print("\n" + "="*60)
    print("4️⃣ VERIFICANDO PROBLEMAS CON JOINS")
    print("="*60)
    
    # SOAT - técnicos asignados que no existen en recurso_operativo
    cursor.execute("""
        SELECT COUNT(*) FROM mpa_soat s
        WHERE s.tecnico_asignado IS NOT NULL 
        AND TRIM(s.tecnico_asignado) != ''
        AND s.tecnico_asignado NOT IN (SELECT id_codigo_consumidor FROM recurso_operativo)
    """)
    soat_huerfanos = cursor.fetchone()[0]
    print(f"⚠️ SOAT con técnicos que no existen: {soat_huerfanos}")
    
    # Técnico Mecánica - técnicos asignados que no existen
    cursor.execute("""
        SELECT COUNT(*) FROM mpa_tecnico_mecanica tm
        WHERE tm.tecnico_asignado IS NOT NULL 
        AND TRIM(tm.tecnico_asignado) != ''
        AND tm.tecnico_asignado NOT IN (SELECT id_codigo_consumidor FROM recurso_operativo)
    """)
    tm_huerfanos = cursor.fetchone()[0]
    print(f"⚠️ Técnico Mecánica con técnicos que no existen: {tm_huerfanos}")
    
    # Licencias - técnicos que no existen
    cursor.execute("""
        SELECT COUNT(*) FROM mpa_licencia_conducir lc
        WHERE lc.tecnico IS NOT NULL 
        AND TRIM(lc.tecnico) != ''
        AND lc.tecnico NOT IN (SELECT id_codigo_consumidor FROM recurso_operativo)
    """)
    lc_huerfanos = cursor.fetchone()[0]
    print(f"⚠️ Licencias con técnicos que no existen: {lc_huerfanos}")
    
    # Técnicos inactivos
    cursor.execute("""
        SELECT COUNT(*) FROM mpa_soat s
        INNER JOIN recurso_operativo ro ON s.tecnico_asignado = ro.id_codigo_consumidor
        WHERE ro.estado != 'Activo'
        AND s.fecha_vencimiento IS NOT NULL 
        AND s.fecha_vencimiento != '0000-00-00'
    """)
    soat_inactivos = cursor.fetchone()[0]
    print(f"⚠️ SOAT con técnicos inactivos: {soat_inactivos}")
    
    return soat_huerfanos, tm_huerfanos, lc_huerfanos, soat_inactivos

def probar_api():
    """Probar el endpoint de vencimientos"""
    print("\n" + "="*60)
    print("5️⃣ PROBANDO ENDPOINT /api/mpa/vencimientos")
    print("="*60)
    
    # Login
    print("🔐 Haciendo login...")
    login_data = {
        'numero_documento': '1019112308',
        'password': '123456'
    }
    
    session = requests.Session()
    login_response = session.post('http://localhost:8080/login', data=login_data)
    
    if login_response.status_code == 200:
        print("✅ Login exitoso")
        
        # Llamar API de vencimientos
        print("📡 Llamando a http://localhost:8080/api/mpa/vencimientos...")
        api_response = session.get('http://localhost:8080/api/mpa/vencimientos')
        
        print(f"📊 Status code: {api_response.status_code}")
        
        if api_response.status_code == 200:
            data = api_response.json()
            print(f"📈 Total vencimientos devueltos por API: {len(data)}")
            
            # Contar por tipo
            tipos = {}
            for item in data:
                tipo = item.get('tipo', 'Desconocido')
                tipos[tipo] = tipos.get(tipo, 0) + 1
            
            print("📋 Distribución por tipo:")
            for tipo, count in tipos.items():
                print(f"   {tipo}: {count}")
            
            # Mostrar ejemplos
            print("\n📋 Ejemplos de vencimientos devueltos:")
            for i, item in enumerate(data[:5], 1):
                print(f"   {i}. Tipo: {item.get('tipo')}, Placa: {item.get('placa')}, Fecha: {item.get('fecha_vencimiento')}, Técnico: {item.get('tecnico_nombre')}")
            
            return len(data), tipos
        else:
            print(f"❌ Error en API: {api_response.status_code}")
            print(f"Response: {api_response.text}")
            return 0, {}
    else:
        print(f"❌ Error en login: {login_response.status_code}")
        return 0, {}

def main():
    """Función principal"""
    print("🔍 DIAGNÓSTICO COMPLETO DE VENCIMIENTOS")
    print("="*60)
    
    # Conectar a BD
    connection = conectar_bd()
    if not connection:
        return
    
    cursor = connection.cursor()
    
    try:
        # Verificar cada tabla usando la lógica exacta del endpoint
        soat_validos = verificar_tabla_soat(cursor)
        tecnico_validos = verificar_tabla_tecnico(cursor)
        licencias_validos = verificar_tabla_licencias(cursor)
        
        # Verificar problemas con JOINs
        soat_huerfanos, tm_huerfanos, lc_huerfanos, soat_inactivos = verificar_problemas_joins(cursor)
        
        # Probar API
        api_total, api_tipos = probar_api()
        
        # Resumen final
        print("\n" + "="*60)
        print("📊 RESUMEN FINAL")
        print("="*60)
        
        total_bd_esperado = soat_validos + tecnico_validos + licencias_validos
        
        print(f"📈 Total registros esperados según lógica BD: {total_bd_esperado}")
        print(f"   - SOAT: {soat_validos}")
        print(f"   - Técnico Mecánica: {tecnico_validos}")
        print(f"   - Licencias: {licencias_validos}")
        
        print(f"\n📡 Total devuelto por API: {api_total}")
        
        # Análisis
        if api_total == total_bd_esperado:
            print("\n✅ PERFECTO: La API devuelve exactamente los registros esperados")
        elif api_total > total_bd_esperado:
            print(f"\n⚠️ DISCREPANCIA: La API devuelve {api_total - total_bd_esperado} registros más de los esperados")
        else:
            print(f"\n❌ PROBLEMA: La API devuelve {total_bd_esperado - api_total} registros menos de los esperados")
            
        # Problemas detectados
        print(f"\n🔍 PROBLEMAS DETECTADOS:")
        if soat_huerfanos > 0:
            print(f"   - {soat_huerfanos} registros SOAT con técnicos inexistentes")
        if tm_huerfanos > 0:
            print(f"   - {tm_huerfanos} registros Técnico Mecánica con técnicos inexistentes")
        if lc_huerfanos > 0:
            print(f"   - {lc_huerfanos} registros Licencias con técnicos inexistentes")
        if soat_inactivos > 0:
            print(f"   - {soat_inactivos} registros SOAT con técnicos inactivos")
            
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        if total_bd_esperado == 0:
            print("   - Todas las fechas en BD parecen ser inválidas ('0000-00-00' o NULL)")
            print("   - Verificar proceso de inserción de datos")
        elif api_total != total_bd_esperado:
            print("   - Revisar la lógica del endpoint api_vencimientos_consolidados")
            print("   - Verificar filtros de fechas y estados")
        if soat_huerfanos + tm_huerfanos + lc_huerfanos > 0:
            print("   - Limpiar referencias a técnicos inexistentes")
            print("   - Implementar validación de integridad referencial")
            
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()