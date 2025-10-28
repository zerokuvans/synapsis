#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar problemas con vencimientos
Versión corregida con nombres de columnas correctos
"""

import mysql.connector
import requests
import json
from datetime import datetime
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
    """Verificar datos en tabla mpa_soat"""
    print("\n" + "="*60)
    print("1️⃣ VERIFICANDO TABLA MPA_SOAT")
    print("="*60)
    
    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM mpa_soat")
    total = cursor.fetchone()[0]
    print(f"📊 Total de registros: {total}")
    
    # Registros con fecha válida usando STRING comparison
    cursor.execute("""
        SELECT COUNT(*) FROM mpa_soat 
        WHERE fecha_vencimiento IS NOT NULL 
        AND CAST(fecha_vencimiento AS CHAR) != '0000-00-00'
        AND CAST(fecha_vencimiento AS CHAR) != '0000-00-00 00:00:00'
        AND CAST(fecha_vencimiento AS CHAR) != ''
    """)
    validos = cursor.fetchone()[0]
    print(f"✅ Registros con fecha válida: {validos}")
    
    # Registros con fecha inválida
    cursor.execute("""
        SELECT COUNT(*) FROM mpa_soat 
        WHERE fecha_vencimiento IS NULL 
        OR CAST(fecha_vencimiento AS CHAR) = '0000-00-00'
        OR CAST(fecha_vencimiento AS CHAR) = '0000-00-00 00:00:00'
        OR CAST(fecha_vencimiento AS CHAR) = ''
    """)
    invalidos = cursor.fetchone()[0]
    print(f"❌ Registros con fecha inválida: {invalidos}")
    
    # Ejemplos de registros válidos
    cursor.execute("""
        SELECT s.placa, CAST(s.fecha_vencimiento AS CHAR) as fecha_str, r.nombre
        FROM mpa_soat s
        LEFT JOIN recurso_operativo r ON s.id_codigo_consumidor = r.id_codigo_consumidor
        WHERE s.fecha_vencimiento IS NOT NULL 
        AND CAST(s.fecha_vencimiento AS CHAR) != '0000-00-00'
        AND CAST(s.fecha_vencimiento AS CHAR) != '0000-00-00 00:00:00'
        AND CAST(s.fecha_vencimiento AS CHAR) != ''
        LIMIT 5
    """)
    ejemplos = cursor.fetchall()
    print(f"📋 Ejemplos de registros válidos:")
    for i, (placa, fecha, tecnico) in enumerate(ejemplos, 1):
        print(f"   {i}. Placa: {placa}, Fecha: {fecha}, Técnico: {tecnico}")
    
    return validos

def verificar_tabla_tecnico(cursor):
    """Verificar datos en tabla mpa_tecnico_mecanica"""
    print("\n" + "="*60)
    print("2️⃣ VERIFICANDO TABLA MPA_TECNICO_MECANICA")
    print("="*60)
    
    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM mpa_tecnico_mecanica")
    total = cursor.fetchone()[0]
    print(f"📊 Total de registros: {total}")
    
    # Registros con fecha válida
    cursor.execute("""
        SELECT COUNT(*) FROM mpa_tecnico_mecanica 
        WHERE fecha_vencimiento IS NOT NULL 
        AND CAST(fecha_vencimiento AS CHAR) != '0000-00-00'
        AND CAST(fecha_vencimiento AS CHAR) != '0000-00-00 00:00:00'
        AND CAST(fecha_vencimiento AS CHAR) != ''
    """)
    validos = cursor.fetchone()[0]
    print(f"✅ Registros con fecha válida: {validos}")
    
    # Registros con fecha inválida
    cursor.execute("""
        SELECT COUNT(*) FROM mpa_tecnico_mecanica 
        WHERE fecha_vencimiento IS NULL 
        OR CAST(fecha_vencimiento AS CHAR) = '0000-00-00'
        OR CAST(fecha_vencimiento AS CHAR) = '0000-00-00 00:00:00'
        OR CAST(fecha_vencimiento AS CHAR) = ''
    """)
    invalidos = cursor.fetchone()[0]
    print(f"❌ Registros con fecha inválida: {invalidos}")
    
    # Ejemplos de registros válidos
    cursor.execute("""
        SELECT t.placa, CAST(t.fecha_vencimiento AS CHAR) as fecha_str, r.nombre
        FROM mpa_tecnico_mecanica t
        LEFT JOIN recurso_operativo r ON t.id_codigo_consumidor = r.id_codigo_consumidor
        WHERE t.fecha_vencimiento IS NOT NULL 
        AND CAST(t.fecha_vencimiento AS CHAR) != '0000-00-00'
        AND CAST(t.fecha_vencimiento AS CHAR) != '0000-00-00 00:00:00'
        AND CAST(t.fecha_vencimiento AS CHAR) != ''
        LIMIT 5
    """)
    ejemplos = cursor.fetchall()
    print(f"📋 Ejemplos de registros válidos:")
    for i, (placa, fecha, tecnico) in enumerate(ejemplos, 1):
        print(f"   {i}. Placa: {placa}, Fecha: {fecha}, Técnico: {tecnico}")
    
    return validos

def verificar_tabla_licencias(cursor):
    """Verificar datos en tabla mpa_licencia_conducir"""
    print("\n" + "="*60)
    print("3️⃣ VERIFICANDO TABLA MPA_LICENCIA_CONDUCIR")
    print("="*60)
    
    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM mpa_licencia_conducir")
    total = cursor.fetchone()[0]
    print(f"📊 Total de registros: {total}")
    
    # Registros con fecha válida
    cursor.execute("""
        SELECT COUNT(*) FROM mpa_licencia_conducir 
        WHERE fecha_vencimiento IS NOT NULL 
        AND CAST(fecha_vencimiento AS CHAR) != '0000-00-00'
        AND CAST(fecha_vencimiento AS CHAR) != '0000-00-00 00:00:00'
        AND CAST(fecha_vencimiento AS CHAR) != ''
    """)
    validos = cursor.fetchone()[0]
    print(f"✅ Registros con fecha válida: {validos}")
    
    # Registros con fecha inválida
    cursor.execute("""
        SELECT COUNT(*) FROM mpa_licencia_conducir 
        WHERE fecha_vencimiento IS NULL 
        OR CAST(fecha_vencimiento AS CHAR) = '0000-00-00'
        OR CAST(fecha_vencimiento AS CHAR) = '0000-00-00 00:00:00'
        OR CAST(fecha_vencimiento AS CHAR) = ''
    """)
    invalidos = cursor.fetchone()[0]
    print(f"❌ Registros con fecha inválida: {invalidos}")
    
    # Verificar si hay id_codigo_consumidor en la tabla
    cursor.execute("SHOW COLUMNS FROM mpa_licencia_conducir LIKE 'id_codigo_consumidor'")
    tiene_id_consumidor = cursor.fetchone() is not None
    print(f"🔍 Tiene id_codigo_consumidor: {tiene_id_consumidor}")
    
    if tiene_id_consumidor:
        # Ejemplos de registros válidos con JOIN
        cursor.execute("""
            SELECT CAST(l.fecha_vencimiento AS CHAR) as fecha_str, r.nombre, l.tecnico
            FROM mpa_licencia_conducir l
            LEFT JOIN recurso_operativo r ON l.id_codigo_consumidor = r.id_codigo_consumidor
            WHERE l.fecha_vencimiento IS NOT NULL 
            AND CAST(l.fecha_vencimiento AS CHAR) != '0000-00-00'
            AND CAST(l.fecha_vencimiento AS CHAR) != '0000-00-00 00:00:00'
            AND CAST(l.fecha_vencimiento AS CHAR) != ''
            LIMIT 5
        """)
        ejemplos = cursor.fetchall()
        print(f"📋 Ejemplos de registros válidos:")
        for i, (fecha, nombre_recurso, tecnico_campo) in enumerate(ejemplos, 1):
            print(f"   {i}. Fecha: {fecha}, Recurso: {nombre_recurso}, Técnico Campo: {tecnico_campo}")
    else:
        # Solo mostrar registros sin JOIN
        cursor.execute("""
            SELECT CAST(fecha_vencimiento AS CHAR) as fecha_str, tecnico
            FROM mpa_licencia_conducir
            WHERE fecha_vencimiento IS NOT NULL 
            AND CAST(fecha_vencimiento AS CHAR) != '0000-00-00'
            AND CAST(fecha_vencimiento AS CHAR) != '0000-00-00 00:00:00'
            AND CAST(fecha_vencimiento AS CHAR) != ''
            LIMIT 5
        """)
        ejemplos = cursor.fetchall()
        print(f"📋 Ejemplos de registros válidos:")
        for i, (fecha, tecnico) in enumerate(ejemplos, 1):
            print(f"   {i}. Fecha: {fecha}, Técnico: {tecnico}")
    
    return validos

def verificar_joins(cursor):
    """Verificar problemas con JOINs a recurso_operativo"""
    print("\n" + "="*60)
    print("4️⃣ VERIFICANDO JOINS CON RECURSO_OPERATIVO")
    print("="*60)
    
    # SOAT con JOIN exitoso
    cursor.execute("""
        SELECT COUNT(*) FROM mpa_soat s
        INNER JOIN recurso_operativo r ON s.id_codigo_consumidor = r.id_codigo_consumidor
        WHERE s.fecha_vencimiento IS NOT NULL 
        AND CAST(s.fecha_vencimiento AS CHAR) != '0000-00-00'
        AND CAST(s.fecha_vencimiento AS CHAR) != '0000-00-00 00:00:00'
        AND CAST(s.fecha_vencimiento AS CHAR) != ''
    """)
    soat_join = cursor.fetchone()[0]
    print(f"✅ SOAT con JOIN exitoso: {soat_join}")
    
    # Técnico Mecánica con JOIN exitoso
    cursor.execute("""
        SELECT COUNT(*) FROM mpa_tecnico_mecanica t
        INNER JOIN recurso_operativo r ON t.id_codigo_consumidor = r.id_codigo_consumidor
        WHERE t.fecha_vencimiento IS NOT NULL 
        AND CAST(t.fecha_vencimiento AS CHAR) != '0000-00-00'
        AND CAST(t.fecha_vencimiento AS CHAR) != '0000-00-00 00:00:00'
        AND CAST(t.fecha_vencimiento AS CHAR) != ''
    """)
    tecnico_join = cursor.fetchone()[0]
    print(f"✅ Técnico Mecánica con JOIN exitoso: {tecnico_join}")
    
    # Verificar si licencias tiene id_codigo_consumidor
    cursor.execute("SHOW COLUMNS FROM mpa_licencia_conducir LIKE 'id_codigo_consumidor'")
    tiene_id_consumidor = cursor.fetchone() is not None
    
    if tiene_id_consumidor:
        # Licencias con JOIN exitoso
        cursor.execute("""
            SELECT COUNT(*) FROM mpa_licencia_conducir l
            INNER JOIN recurso_operativo r ON l.id_codigo_consumidor = r.id_codigo_consumidor
            WHERE l.fecha_vencimiento IS NOT NULL 
            AND CAST(l.fecha_vencimiento AS CHAR) != '0000-00-00'
            AND CAST(l.fecha_vencimiento AS CHAR) != '0000-00-00 00:00:00'
            AND CAST(l.fecha_vencimiento AS CHAR) != ''
        """)
        licencias_join = cursor.fetchone()[0]
        print(f"✅ Licencias con JOIN exitoso: {licencias_join}")
    else:
        print("⚠️ Licencias NO tiene id_codigo_consumidor - no se puede hacer JOIN")
        licencias_join = 0
    
    return soat_join, tecnico_join, licencias_join

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
                print(f"   {i}. Tipo: {item.get('tipo')}, Placa: {item.get('placa_vehiculo')}, Fecha: {item.get('fecha_vencimiento')}, Técnico: {item.get('tecnico')}")
            
            return len(data), tipos
        else:
            print(f"❌ Error en API: {api_response.status_code}")
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
        # Verificar cada tabla
        soat_validos = verificar_tabla_soat(cursor)
        tecnico_validos = verificar_tabla_tecnico(cursor)
        licencias_validos = verificar_tabla_licencias(cursor)
        
        # Verificar JOINs
        soat_join, tecnico_join, licencias_join = verificar_joins(cursor)
        
        # Probar API
        api_total, api_tipos = probar_api()
        
        # Resumen final
        print("\n" + "="*60)
        print("📊 RESUMEN FINAL")
        print("="*60)
        
        total_bd_validos = soat_validos + tecnico_validos + licencias_validos
        total_joins = soat_join + tecnico_join + licencias_join
        
        print(f"📈 Total registros con fecha válida en BD: {total_bd_validos}")
        print(f"   - SOAT: {soat_validos}")
        print(f"   - Técnico Mecánica: {tecnico_validos}")
        print(f"   - Licencias: {licencias_validos}")
        
        print(f"\n🔗 Total que pasa filtros JOIN: {total_joins}")
        print(f"   - SOAT: {soat_join}")
        print(f"   - Técnico Mecánica: {tecnico_join}")
        print(f"   - Licencias: {licencias_join}")
        
        print(f"\n📡 Total devuelto por API: {api_total}")
        
        # Análisis
        if api_total == total_joins:
            print("\n✅ PERFECTO: La API devuelve exactamente los registros esperados")
        elif api_total > total_joins:
            print(f"\n⚠️ DISCREPANCIA: La API devuelve {api_total - total_joins} registros más de los esperados")
            print("   Esto podría indicar que la API está usando una lógica diferente")
        else:
            print(f"\n❌ PROBLEMA: La API devuelve {total_joins - api_total} registros menos de los esperados")
            
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        if soat_validos == 0 and tecnico_validos == 0 and licencias_validos == 0:
            print("   - Todas las fechas en BD parecen ser inválidas ('0000-00-00' o NULL)")
            print("   - Verificar proceso de inserción de datos")
        elif api_total > total_joins:
            print("   - La API podría estar usando datos de otras fuentes")
            print("   - Revisar la lógica del endpoint api_vencimientos_consolidados")
            
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()