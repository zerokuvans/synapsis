#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug específico para problemas en servidor MySQL
Este script identifica diferencias sutiles que pueden causar fallos en producción
"""

import mysql.connector
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import sys
import platform

# Cargar variables de entorno
load_dotenv()

def debug_environment():
    """Debug del entorno de ejecución"""
    print("🔍 INFORMACIÓN DEL ENTORNO")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    print(f"Timezone: {datetime.now().astimezone().tzinfo}")
    
    # Variables de entorno críticas
    env_vars = [
        'MYSQL_HOST', 'MYSQL_PORT', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DB',
        'TZ', 'PYTHONPATH', 'FLASK_ENV'
    ]
    
    print("\nVariables de entorno:")
    for var in env_vars:
        value = os.getenv(var)
        if var in ['MYSQL_PASSWORD']:
            display_value = '***' if value else 'No definida'
        else:
            display_value = value if value else 'No definida'
        print(f"   {var}: {display_value}")

def debug_mysql_connection():
    """Debug detallado de la conexión MySQL"""
    print("\n🔗 DEBUG DE CONEXIÓN MYSQL")
    print("=" * 50)
    
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
        
        cursor = connection.cursor(dictionary=True)
        
        # Información del servidor
        cursor.execute("SELECT VERSION() as version")
        version = cursor.fetchone()
        print(f"✅ MySQL Version: {version['version']}")
        
        # Zona horaria del servidor
        cursor.execute("SELECT @@global.time_zone as global_tz, @@session.time_zone as session_tz")
        timezone_info = cursor.fetchone()
        print(f"✅ MySQL Global Timezone: {timezone_info['global_tz']}")
        print(f"✅ MySQL Session Timezone: {timezone_info['session_tz']}")
        
        # Fecha y hora actual del servidor
        cursor.execute("SELECT NOW() as server_time, UTC_TIMESTAMP() as utc_time")
        time_info = cursor.fetchone()
        print(f"✅ MySQL Server Time: {time_info['server_time']}")
        print(f"✅ MySQL UTC Time: {time_info['utc_time']}")
        
        # Configuración de SQL_MODE
        cursor.execute("SELECT @@sql_mode as sql_mode")
        sql_mode = cursor.fetchone()
        print(f"✅ SQL Mode: {sql_mode['sql_mode']}")
        
        # Verificar si existe la tabla ferretero
        cursor.execute("SHOW TABLES LIKE 'ferretero'")
        table_exists = cursor.fetchone()
        if table_exists:
            print("✅ Tabla 'ferretero' existe")
            
            # Estructura de la tabla
            cursor.execute("DESCRIBE ferretero")
            columns = cursor.fetchall()
            print("   Columnas:")
            for col in columns:
                print(f"      - {col['Field']}: {col['Type']} ({col['Null']})")
        else:
            print("❌ Tabla 'ferretero' no existe")
        
        # Verificar tabla recurso_operativo
        cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
        table_exists = cursor.fetchone()
        if table_exists:
            print("✅ Tabla 'recurso_operativo' existe")
        else:
            print("❌ Tabla 'recurso_operativo' no existe")
        
        connection.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def debug_date_calculations():
    """Debug específico de cálculos de fechas"""
    print("\n📅 DEBUG DE CÁLCULOS DE FECHAS")
    print("=" * 50)
    
    # Fecha actual
    now = datetime.now()
    print(f"Fecha actual Python: {now}")
    print(f"Tipo: {type(now)}")
    
    # Fechas de prueba
    test_dates = [
        now - timedelta(days=1),
        now - timedelta(days=7),
        now - timedelta(days=15),
        now - timedelta(days=30)
    ]
    
    print("\nCálculos de diferencia:")
    for i, test_date in enumerate(test_dates):
        try:
            diff = (now - test_date).days
            print(f"   Fecha {i+1}: {test_date} -> {diff} días")
            
            # Verificar si es datetime naive o aware
            if test_date.tzinfo is None:
                print(f"      - Timezone: naive")
            else:
                print(f"      - Timezone: {test_date.tzinfo}")
                
        except Exception as e:
            print(f"   ❌ Error en cálculo {i+1}: {e}")

def debug_mysql_date_functions():
    """Debug de funciones de fecha en MySQL"""
    print("\n🗓️ DEBUG DE FUNCIONES DE FECHA EN MYSQL")
    print("=" * 50)
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'capired'),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Fecha actual en diferentes formatos
        cursor.execute("""
            SELECT 
                NOW() as now_func,
                CURDATE() as curdate_func,
                CURRENT_TIMESTAMP() as current_timestamp_func,
                UTC_TIMESTAMP() as utc_timestamp_func
        """)
        dates = cursor.fetchone()
        
        print("Funciones de fecha MySQL:")
        for key, value in dates.items():
            print(f"   {key}: {value} (tipo: {type(value)})")
        
        # Probar cálculos de diferencia en MySQL
        test_date = datetime.now() - timedelta(days=7)
        cursor.execute("""
            SELECT 
                %s as test_date,
                NOW() as current_date,
                DATEDIFF(NOW(), %s) as mysql_diff_days,
                TIMESTAMPDIFF(DAY, %s, NOW()) as mysql_timestampdiff
        """, (test_date, test_date, test_date))
        
        result = cursor.fetchone()
        print("\nCálculo de diferencia MySQL vs Python:")
        print(f"   Fecha prueba: {test_date}")
        print(f"   MySQL DATEDIFF: {result['mysql_diff_days']} días")
        print(f"   MySQL TIMESTAMPDIFF: {result['mysql_timestampdiff']} días")
        
        # Cálculo Python
        python_diff = (datetime.now() - test_date).days
        print(f"   Python diff: {python_diff} días")
        
        # Verificar si hay diferencias
        if result['mysql_diff_days'] != python_diff:
            print(f"   ⚠️ DIFERENCIA DETECTADA: MySQL={result['mysql_diff_days']}, Python={python_diff}")
        else:
            print(f"   ✅ Cálculos coinciden")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error en debug de fechas MySQL: {e}")

def debug_specific_ferretero_issue():
    """Debug específico del problema en registrar_ferretero"""
    print("\n🔧 DEBUG ESPECÍFICO DEL PROBLEMA FERRETERO")
    print("=" * 50)
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'capired'),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Verificar si hay datos reales en ferretero
        cursor.execute("SELECT COUNT(*) as total FROM ferretero")
        count = cursor.fetchone()
        print(f"Total registros en ferretero: {count['total']}")
        
        if count['total'] > 0:
            # Obtener algunos registros recientes
            cursor.execute("""
                SELECT 
                    id_codigo_consumidor,
                    fecha_asignacion,
                    silicona,
                    cinta_aislante,
                    DATEDIFF(NOW(), fecha_asignacion) as dias_desde_asignacion
                FROM ferretero 
                ORDER BY fecha_asignacion DESC 
                LIMIT 5
            """)
            
            registros = cursor.fetchall()
            print("\nÚltimos 5 registros:")
            for reg in registros:
                print(f"   - Técnico: {reg['id_codigo_consumidor']}, Fecha: {reg['fecha_asignacion']}, Días: {reg['dias_desde_asignacion']}")
        
        # Verificar trigger actualizar_stock_asignacion
        cursor.execute("SHOW TRIGGERS LIKE 'actualizar_stock_asignacion'")
        trigger = cursor.fetchone()
        if trigger:
            print("✅ Trigger 'actualizar_stock_asignacion' existe")
        else:
            print("❌ Trigger 'actualizar_stock_asignacion' no existe")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error en debug específico: {e}")

def generate_server_recommendations():
    """Generar recomendaciones específicas para el servidor"""
    print("\n💡 RECOMENDACIONES PARA EL SERVIDOR")
    print("=" * 50)
    
    recommendations = [
        "1. VERIFICAR ZONA HORARIA:",
        "   - Servidor: timedatectl status (Linux) o tzutil /g (Windows)",
        "   - MySQL: SELECT @@global.time_zone, @@session.time_zone;",
        "   - Python: import datetime; print(datetime.datetime.now().astimezone().tzinfo)",
        "",
        "2. VERIFICAR VERSIONES:",
        "   - Python: python --version",
        "   - MySQL: SELECT VERSION();",
        "   - mysql-connector-python: pip show mysql-connector-python",
        "",
        "3. VERIFICAR CONFIGURACIÓN MYSQL:",
        "   - SQL_MODE: SELECT @@sql_mode;",
        "   - Charset: SHOW VARIABLES LIKE 'character_set%';",
        "   - Collation: SHOW VARIABLES LIKE 'collation%';",
        "",
        "4. VERIFICAR VARIABLES DE ENTORNO EN SERVIDOR:",
        "   - Archivo .env existe y es accesible",
        "   - Variables MYSQL_* están definidas correctamente",
        "   - Permisos de lectura del archivo .env",
        "",
        "5. AGREGAR LOGGING DETALLADO:",
        "   - Agregar prints en registrar_ferretero antes y después de cálculos",
        "   - Loggear fecha_actual y fecha_asignacion antes del cálculo",
        "   - Loggear resultado de (fecha_actual - fecha_asignacion).days",
        "",
        "6. PROBAR CON FECHAS UTC:",
        "   - Usar datetime.utcnow() en lugar de datetime.now()",
        "   - Convertir fechas de BD a UTC antes de calcular",
        "",
        "7. VERIFICAR PERMISOS DE BASE DE DATOS:",
        "   - Usuario tiene permisos SELECT en ferretero y recurso_operativo",
        "   - Usuario tiene permisos INSERT en ferretero",
        "   - Trigger actualizar_stock_asignacion funciona correctamente"
    ]
    
    for rec in recommendations:
        print(rec)

def main():
    """Función principal de debug"""
    print("🐛 DEBUG COMPLETO PARA SERVIDOR MYSQL")
    print("=" * 60)
    
    # Ejecutar todos los debugs
    debug_environment()
    debug_mysql_connection()
    debug_date_calculations()
    debug_mysql_date_functions()
    debug_specific_ferretero_issue()
    generate_server_recommendations()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE DEBUG COMPLETADO")
    print("=" * 60)
    print("✅ Ejecutar este script en el servidor para comparar resultados")
    print("✅ Revisar las recomendaciones específicas arriba")
    print("✅ Implementar logging detallado en registrar_ferretero")

if __name__ == "__main__":
    main()