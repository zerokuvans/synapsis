#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para identificar problemas con cálculos en servidor MySQL
Este script identifica las posibles causas por las que los cálculos no funcionan
cuando la aplicación se ejecuta en un servidor con base de datos MySQL.
"""

import mysql.connector
import os
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """Obtener conexión a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'capired'),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            autocommit=False
        )
        return connection
    except mysql.connector.Error as e:
        print(f"❌ Error de conexión a MySQL: {e}")
        return None

def diagnosticar_configuracion_mysql():
    """Diagnosticar configuración de MySQL que puede afectar cálculos"""
    print("\n🔍 DIAGNÓSTICO DE CONFIGURACIÓN MYSQL")
    print("=" * 50)
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 1. Verificar zona horaria del servidor MySQL
        print("\n1. ZONA HORARIA DEL SERVIDOR MYSQL:")
        cursor.execute("SELECT @@global.time_zone as global_tz, @@session.time_zone as session_tz")
        tz_info = cursor.fetchone()
        print(f"   - Zona horaria global: {tz_info['global_tz']}")
        print(f"   - Zona horaria de sesión: {tz_info['session_tz']}")
        
        # 2. Verificar fecha y hora actual del servidor MySQL
        cursor.execute("SELECT NOW() as mysql_now, UTC_TIMESTAMP() as mysql_utc")
        time_info = cursor.fetchone()
        print(f"   - Fecha/hora MySQL NOW(): {time_info['mysql_now']}")
        print(f"   - Fecha/hora MySQL UTC: {time_info['mysql_utc']}")
        
        # 3. Comparar con fecha/hora de Python
        python_now = datetime.now()
        python_utc = datetime.utcnow()
        print(f"   - Fecha/hora Python local: {python_now}")
        print(f"   - Fecha/hora Python UTC: {python_utc}")
        
        # 4. Verificar diferencia entre MySQL y Python
        mysql_dt = time_info['mysql_now']
        if isinstance(mysql_dt, datetime):
            diff = abs((python_now - mysql_dt).total_seconds())
            print(f"   - Diferencia MySQL vs Python: {diff} segundos")
            if diff > 60:  # Más de 1 minuto de diferencia
                print("   ⚠️  ADVERTENCIA: Diferencia significativa de tiempo detectada")
        
        # 5. Verificar versión de MySQL
        cursor.execute("SELECT VERSION() as mysql_version")
        version_info = cursor.fetchone()
        print(f"\n2. VERSIÓN DE MYSQL: {version_info['mysql_version']}")
        
        # 6. Verificar configuración de SQL_MODE
        cursor.execute("SELECT @@sql_mode as sql_mode")
        mode_info = cursor.fetchone()
        print(f"\n3. SQL_MODE: {mode_info['sql_mode']}")
        
        # 7. Verificar configuración de caracteres
        cursor.execute("SHOW VARIABLES LIKE 'character_set%'")
        charset_info = cursor.fetchall()
        print("\n4. CONFIGURACIÓN DE CARACTERES:")
        for item in charset_info:
            print(f"   - {item['Variable_name']}: {item['Value']}")
        
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error en diagnóstico MySQL: {e}")
        return False
    finally:
        if connection:
            connection.close()

def diagnosticar_calculos_fechas():
    """Diagnosticar problemas específicos con cálculos de fechas"""
    print("\n🔍 DIAGNÓSTICO DE CÁLCULOS DE FECHAS")
    print("=" * 50)
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 1. Verificar datos de prueba en tabla ferretero
        print("\n1. VERIFICANDO DATOS DE ASIGNACIONES RECIENTES:")
        cursor.execute("""
            SELECT 
                id_codigo_consumidor,
                fecha_asignacion,
                silicona,
                cinta_aislante,
                DATEDIFF(NOW(), fecha_asignacion) as dias_diferencia
            FROM ferretero 
            ORDER BY fecha_asignacion DESC 
            LIMIT 5
        """)
        
        asignaciones = cursor.fetchall()
        if asignaciones:
            for asig in asignaciones:
                print(f"   - ID: {asig['id_codigo_consumidor']}, Fecha: {asig['fecha_asignacion']}, Días: {asig['dias_diferencia']}")
        else:
            print("   - No se encontraron asignaciones recientes")
        
        # 2. Simular cálculo de diferencia de días como en el código
        print("\n2. SIMULANDO CÁLCULO DE DIFERENCIA DE DÍAS:")
        if asignaciones:
            fecha_actual_python = datetime.now()
            primera_asignacion = asignaciones[0]
            fecha_asignacion = primera_asignacion['fecha_asignacion']
            
            # Cálculo como en el código original
            if isinstance(fecha_asignacion, datetime):
                diferencia_python = (fecha_actual_python - fecha_asignacion).days
                diferencia_mysql = primera_asignacion['dias_diferencia']
                
                print(f"   - Diferencia calculada por Python: {diferencia_python} días")
                print(f"   - Diferencia calculada por MySQL: {diferencia_mysql} días")
                
                if diferencia_python != diferencia_mysql:
                    print("   ⚠️  PROBLEMA DETECTADO: Diferencias en cálculo de días")
                    print(f"      Diferencia: {abs(diferencia_python - diferencia_mysql)} días")
                else:
                    print("   ✅ Cálculos de días coinciden")
        
        # 3. Verificar si hay problemas con tipos de datos
        print("\n3. VERIFICANDO TIPOS DE DATOS:")
        cursor.execute("DESCRIBE ferretero")
        estructura = cursor.fetchall()
        
        campos_fecha = [campo for campo in estructura if 'fecha' in campo['Field'].lower()]
        for campo in campos_fecha:
            print(f"   - {campo['Field']}: {campo['Type']} (NULL: {campo['Null']})")
        
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error en diagnóstico de fechas: {e}")
        return False
    finally:
        if connection:
            connection.close()

def diagnosticar_variables_entorno():
    """Diagnosticar variables de entorno"""
    print("\n🔍 DIAGNÓSTICO DE VARIABLES DE ENTORNO")
    print("=" * 50)
    
    variables_criticas = [
        'MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DB', 'MYSQL_PORT',
        'TZ', 'PYTHONPATH', 'FLASK_ENV'
    ]
    
    print("\nVARIABLES DE ENTORNO CRÍTICAS:")
    for var in variables_criticas:
        valor = os.getenv(var, 'NO DEFINIDA')
        if var == 'MYSQL_PASSWORD' and valor != 'NO DEFINIDA':
            valor = '*' * len(valor)  # Ocultar contraseña
        print(f"   - {var}: {valor}")
    
    # Verificar zona horaria del sistema
    print(f"\nZONA HORARIA DEL SISTEMA:")
    print(f"   - TZ variable: {os.getenv('TZ', 'NO DEFINIDA')}")
    print(f"   - Zona horaria local detectada: {datetime.now().astimezone().tzinfo}")

def diagnosticar_permisos_mysql():
    """Diagnosticar permisos de MySQL"""
    print("\n🔍 DIAGNÓSTICO DE PERMISOS MYSQL")
    print("=" * 50)
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Verificar usuario actual y permisos
        cursor.execute("SELECT USER() as current_user, DATABASE() as current_db")
        user_info = cursor.fetchone()
        print(f"\nUSUARIO ACTUAL: {user_info['current_user']}")
        print(f"BASE DE DATOS ACTUAL: {user_info['current_db']}")
        
        # Verificar permisos en tablas críticas
        tablas_criticas = ['ferretero', 'stock_ferretero', 'movimientos_stock']
        
        print("\nPERMISOS EN TABLAS CRÍTICAS:")
        for tabla in tablas_criticas:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {tabla} LIMIT 1")
                print(f"   - {tabla}: ✅ Lectura OK")
                
                # Intentar inserción de prueba (sin commit)
                cursor.execute(f"SHOW COLUMNS FROM {tabla}")
                print(f"   - {tabla}: ✅ Estructura accesible")
                
            except mysql.connector.Error as e:
                print(f"   - {tabla}: ❌ Error - {e}")
        
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error en diagnóstico de permisos: {e}")
        return False
    finally:
        if connection:
            connection.close()

def main():
    """Función principal de diagnóstico"""
    print("🚀 DIAGNÓSTICO COMPLETO - PROBLEMAS CON MYSQL")
    print("=" * 60)
    print("Este script identifica problemas que pueden causar fallos")
    print("en los cálculos cuando la aplicación se ejecuta en MySQL.")
    
    # Ejecutar todos los diagnósticos
    diagnosticos = [
        ("Configuración MySQL", diagnosticar_configuracion_mysql),
        ("Cálculos de fechas", diagnosticar_calculos_fechas),
        ("Variables de entorno", diagnosticar_variables_entorno),
        ("Permisos MySQL", diagnosticar_permisos_mysql)
    ]
    
    resultados = {}
    
    for nombre, funcion in diagnosticos:
        print(f"\n{'='*20} {nombre.upper()} {'='*20}")
        try:
            if funcion == diagnosticar_variables_entorno:
                funcion()  # Esta función no retorna valor
                resultados[nombre] = True
            else:
                resultados[nombre] = funcion()
        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")
            resultados[nombre] = False
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE DIAGNÓSTICO")
    print("=" * 60)
    
    problemas_encontrados = []
    
    for nombre, resultado in resultados.items():
        estado = "✅ OK" if resultado else "❌ PROBLEMAS"
        print(f"   - {nombre}: {estado}")
        if not resultado:
            problemas_encontrados.append(nombre)
    
    if problemas_encontrados:
        print("\n⚠️  PROBLEMAS DETECTADOS EN:")
        for problema in problemas_encontrados:
            print(f"   - {problema}")
        
        print("\n💡 RECOMENDACIONES:")
        print("   1. Verificar configuración de zona horaria en MySQL")
        print("   2. Sincronizar tiempo entre servidor Python y MySQL")
        print("   3. Revisar variables de entorno en el servidor")
        print("   4. Verificar permisos de base de datos")
        print("   5. Considerar usar UTC para todos los cálculos de fecha")
    else:
        print("\n✅ No se detectaron problemas obvios")
        print("   El problema puede estar en la lógica de negocio específica")

if __name__ == "__main__":
    main()