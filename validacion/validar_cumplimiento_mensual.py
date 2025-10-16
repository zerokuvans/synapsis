#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para validar que el cumplimiento mensual se calcula correctamente
con la nueva lógica donde NOVEDAD se considera como CUMPLE
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta, date
from collections import Counter
import requests
import json
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'time_zone': '+00:00'
}

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def obtener_registros_mes_actual():
    """Obtiene registros de asistencia del mes actual para el supervisor específico"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Usar octubre 2025 donde tenemos datos reales
        primer_dia = '2025-10-01'
        ultimo_dia = '2025-10-31'
        supervisor = '1032402333'  # Usar la cédula como identificador
        
        print(f"📅 Consultando registros desde {primer_dia} hasta {ultimo_dia} para supervisor {supervisor}")
        
        cursor.execute("""
            SELECT 
                cedula,
                tecnico,
                fecha_asistencia,
                estado,
                super
            FROM asistencia 
            WHERE fecha_asistencia >= %s 
            AND fecha_asistencia <= %s
            AND super = %s
            ORDER BY fecha_asistencia
        """, (primer_dia, ultimo_dia, supervisor))
        
        registros = cursor.fetchall()
        print(f"📊 Total de registros encontrados: {len(registros)}")
        
        return registros
        
    except mysql.connector.Error as e:
        print(f"❌ Error consultando registros: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def calcular_cumplimiento_manual(registros):
    """Calcular cumplimiento mensual manualmente usando la nueva lógica"""
    print(f"\n🔍 CALCULANDO CUMPLIMIENTO MANUAL")
    print("=" * 50)
    
    # Contar estados
    estados_count = Counter()
    cumple_count = 0
    no_cumple_count = 0
    
    for registro in registros:
        estado = (registro.get('estado') or '').lower().strip()
        estados_count[estado] += 1
        
        # Aplicar nueva lógica: NOVEDAD se considera como CUMPLE
        if estado in ['cumple', 'novedad']:
            cumple_count += 1
        elif estado in ['nocumple', 'no cumple', 'no aplica']:
            no_cumple_count += 1
    
    # Mostrar desglose por estado
    print(f"📋 DESGLOSE POR ESTADO:")
    for estado, count in sorted(estados_count.items()):
        emoji = "✅" if estado in ['cumple', 'novedad'] else "❌" if estado in ['nocumple', 'no cumple', 'no aplica'] else "⚪"
        categoria = "CUMPLE" if estado in ['cumple', 'novedad'] else "NO CUMPLE" if estado in ['nocumple', 'no cumple', 'no aplica'] else "OTRO"
        print(f"   {emoji} {estado.upper()}: {count} registros ({categoria})")
    
    # Calcular porcentajes
    total_cumplimiento = cumple_count + no_cumple_count
    cumplimiento_porcentaje = 0
    cumplimiento_fraccion = f"0/{total_cumplimiento}"
    
    if total_cumplimiento > 0:
        cumplimiento_porcentaje = round((cumple_count / total_cumplimiento) * 100, 1)
        cumplimiento_fraccion = f"{cumple_count}/{total_cumplimiento}"
    
    print(f"\n📊 RESULTADOS MANUALES:")
    print(f"   ✅ Cumple (incluye NOVEDAD): {cumple_count}")
    print(f"   ❌ No Cumple: {no_cumple_count}")
    print(f"   📈 Total considerado: {total_cumplimiento}")
    print(f"   🎯 Cumplimiento: {cumplimiento_porcentaje}% ({cumplimiento_fraccion})")
    
    return {
        'cumple_count': cumple_count,
        'no_cumple_count': no_cumple_count,
        'total_cumplimiento': total_cumplimiento,
        'cumplimiento_porcentaje': cumplimiento_porcentaje,
        'cumplimiento_fraccion': cumplimiento_fraccion,
        'estados_count': dict(estados_count)
    }

def probar_api_endpoint():
    """Prueba el endpoint del API para obtener cumplimiento mensual"""
    base_url = "http://192.168.80.15:8080"
    login_url = f"{base_url}/"
    api_url = f"{base_url}/api/operativo/inicio-operacion/asistencia"
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        print("🔐 Haciendo login...")
        
        # Datos de login - usar credenciales del usuario operativo
        login_data = {
            'username': '1032402333',   # Cédula del usuario operativo Cáceres
            'password': 'CE1032402333'  # Password del usuario operativo
        }
        
        # Hacer login
        login_response = session.post(login_url, data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login falló: {login_response.status_code}")
            return None
            
        # Verificar si el login fue exitoso
        if 'dashboard' not in login_response.text.lower() and 'administrativo' not in login_response.text.lower():
            print("❌ Login falló: credenciales incorrectas")
            return None
            
        print("✅ Login exitoso")
        
        # Ahora hacer la petición al API con la sesión autenticada
        print("📊 Consultando endpoint de asistencia...")
        api_response = session.get(api_url)
        
        if api_response.status_code != 200:
            print(f"❌ Error en API: {api_response.status_code}")
            print(f"Respuesta: {api_response.text[:200]}")
            return None
            
        result = api_response.json()
        print("✅ Datos obtenidos del API exitosamente")
        print(f"📊 Estructura de respuesta del API: {list(result.keys()) if isinstance(result, dict) else 'No es diccionario'}")
        print(f"📊 Primeros datos del API: {str(result)[:500]}...")
        
        # Extraer valores de cumplimiento mensual
        cumple_mes = result.get('cumple_mes', 0)
        no_cumple_mes = result.get('no_cumple_mes', 0)
        cumplimiento_mes_total = result.get('cumplimiento_mes_total', 0)
        cumplimiento_mes_porcentaje = result.get('cumplimiento_mes_porcentaje', 0)
        
        return {
            'cumple_mes': cumple_mes,
            'no_cumple_mes': no_cumple_mes,
            'cumplimiento_mes_total': cumplimiento_mes_total,
            'cumplimiento_mes_porcentaje': cumplimiento_mes_porcentaje
        }
        
    except Exception as e:
        print(f"❌ Error al probar API endpoint: {e}")
        return None

def comparar_resultados(manual, api):
    """Comparar resultados manuales vs API"""
    print(f"\n🔍 COMPARACIÓN DE RESULTADOS")
    print("=" * 50)
    
    if not api:
        print("❌ No se pudieron obtener datos del API para comparar")
        return False
    
    # Comparar valores clave
    comparaciones = [
        ('Cumple', manual['cumple_count'], api['cumple_mes']),
        ('No Cumple', manual['no_cumple_count'], api['no_cumple_mes']),
        ('Total', manual['total_cumplimiento'], api['cumplimiento_mes_total']),
        ('Porcentaje', manual['cumplimiento_porcentaje'], api['cumplimiento_mes_porcentaje'])
    ]
    
    todo_correcto = True
    
    for nombre, valor_manual, valor_api in comparaciones:
        if valor_manual == valor_api:
            print(f"   ✅ {nombre}: {valor_manual} (Manual) = {valor_api} (API)")
        else:
            print(f"   ❌ {nombre}: {valor_manual} (Manual) ≠ {valor_api} (API)")
            todo_correcto = False
    
    # Verificar fracciones
    if manual['cumplimiento_fraccion'] == api['cumplimiento_mes_fraccion']:
        print(f"   ✅ Fracción: {manual['cumplimiento_fraccion']} (Manual) = {api['cumplimiento_mes_fraccion']} (API)")
    else:
        print(f"   ❌ Fracción: {manual['cumplimiento_fraccion']} (Manual) ≠ {api['cumplimiento_mes_fraccion']} (API)")
        todo_correcto = False
    
    return todo_correcto

def validar_logica_novedad(registros):
    """Validar específicamente que NOVEDAD se está contando como cumple"""
    print(f"\n🔍 VALIDACIÓN ESPECÍFICA DE LÓGICA NOVEDAD")
    print("=" * 50)
    
    registros_novedad = [r for r in registros if (r.get('estado') or '').lower().strip() == 'novedad']
    
    print(f"📋 Registros con estado 'NOVEDAD': {len(registros_novedad)}")
    
    if registros_novedad:
        print(f"📝 Ejemplos de registros NOVEDAD:")
        for i, registro in enumerate(registros_novedad[:5]):  # Mostrar máximo 5 ejemplos
            print(f"   {i+1}. {registro['tecnico']} - {registro['fecha_asistencia']} - Estado: {registro['estado']}")
        
        if len(registros_novedad) > 5:
            print(f"   ... y {len(registros_novedad) - 5} más")
    
    print(f"\n✅ Con la nueva lógica, estos {len(registros_novedad)} registros NOVEDAD se cuentan como CUMPLE")
    print(f"📈 Esto mejora el porcentaje de cumplimiento mensual")

def main():
    """Función principal de validación"""
    print("🔍 VALIDACIÓN DE CUMPLIMIENTO MENSUAL")
    print("=" * 60)
    print("Verificando que NOVEDAD se considere como CUMPLE")
    print("=" * 60)
    
    # 1. Obtener registros de la base de datos
    registros = obtener_registros_mes_actual()
    
    if not registros:
        print("❌ No se encontraron registros para validar")
        return
    
    # 2. Calcular cumplimiento manualmente
    resultado_manual = calcular_cumplimiento_manual(registros)
    
    # 3. Validar lógica específica de NOVEDAD
    validar_logica_novedad(registros)
    
    # 4. Probar endpoint del API
    resultado_api = probar_api_endpoint()
    
    # 5. Comparar resultados
    es_correcto = comparar_resultados(resultado_manual, resultado_api)
    
    # 6. Conclusión final
    print(f"\n🎯 CONCLUSIÓN FINAL")
    print("=" * 50)
    
    if es_correcto:
        print("✅ ¡VALIDACIÓN EXITOSA!")
        print("   La nueva lógica está funcionando correctamente")
        print("   NOVEDAD se está contando como CUMPLE en el cálculo mensual")
    else:
        print("❌ ¡VALIDACIÓN FALLIDA!")
        print("   Hay inconsistencias entre el cálculo manual y el API")
        print("   Revisar la implementación del endpoint")
    
    print(f"\n📊 RESUMEN:")
    print(f"   📅 Registros analizados: {len(registros)}")
    print(f"   ✅ Estados que cuentan como CUMPLE: cumple, novedad")
    print(f"   ❌ Estados que cuentan como NO CUMPLE: nocumple, no cumple, no aplica")
    print(f"   🎯 Cumplimiento calculado: {resultado_manual['cumplimiento_porcentaje']}%")

if __name__ == "__main__":
    main()