#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar el estado de la base de datos en producción
y comparar con el entorno local
"""

import mysql.connector
import os
from datetime import datetime
import json
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def conectar_bd_local():
    """Conectar a la base de datos local"""
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='synapsis_db'
        )
        return conexion
    except Exception as e:
        print(f"❌ Error conectando a BD local: {e}")
        return None

def conectar_bd_produccion():
    """Conectar a la base de datos de producción"""
    try:
        # Intentar obtener configuración de producción desde variables de entorno
        host_prod = os.getenv('DB_HOST_PROD', 'localhost')
        user_prod = os.getenv('DB_USER_PROD', 'root')
        pass_prod = os.getenv('DB_PASS_PROD', '')
        db_prod = os.getenv('DB_NAME_PROD', 'synapsis_db')
        
        print(f"🔗 Intentando conectar a producción:")
        print(f"   Host: {host_prod}")
        print(f"   Usuario: {user_prod}")
        print(f"   Base de datos: {db_prod}")
        
        conexion = mysql.connector.connect(
            host=host_prod,
            user=user_prod,
            password=pass_prod,
            database=db_prod
        )
        return conexion
    except Exception as e:
        print(f"❌ Error conectando a BD producción: {e}")
        return None

def analizar_tabla(cursor, nombre_tabla):
    """Analizar una tabla específica"""
    resultado = {
        'existe': False,
        'registros': 0,
        'estructura': [],
        'muestra_datos': []
    }
    
    try:
        # Verificar si la tabla existe
        cursor.execute(f"SHOW TABLES LIKE '{nombre_tabla}'")
        if cursor.fetchone():
            resultado['existe'] = True
            
            # Obtener estructura
            cursor.execute(f"DESCRIBE {nombre_tabla}")
            resultado['estructura'] = cursor.fetchall()
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
            resultado['registros'] = cursor.fetchone()[0]
            
            # Obtener muestra de datos (máximo 3 registros)
            cursor.execute(f"SELECT * FROM {nombre_tabla} LIMIT 3")
            resultado['muestra_datos'] = cursor.fetchall()
            
    except Exception as e:
        print(f"❌ Error analizando tabla {nombre_tabla}: {e}")
    
    return resultado

def verificar_vista(cursor, nombre_vista):
    """Verificar si existe una vista específica"""
    try:
        cursor.execute(f"SHOW CREATE VIEW {nombre_vista}")
        return True, cursor.fetchone()
    except Exception as e:
        return False, str(e)

def comparar_entornos():
    """Comparar el estado entre local y producción"""
    print("\n" + "="*80)
    print("🔍 COMPARACIÓN ENTRE ENTORNOS LOCAL Y PRODUCCIÓN")
    print("="*80)
    
    # Conectar a ambas bases de datos
    conn_local = conectar_bd_local()
    conn_prod = conectar_bd_produccion()
    
    if not conn_local:
        print("❌ No se pudo conectar a la base de datos local")
        return
    
    if not conn_prod:
        print("❌ No se pudo conectar a la base de datos de producción")
        print("💡 Verifica las variables de entorno para producción:")
        print("   - DB_HOST_PROD")
        print("   - DB_USER_PROD")
        print("   - DB_PASS_PROD")
        print("   - DB_NAME_PROD")
        return
    
    cursor_local = conn_local.cursor()
    cursor_prod = conn_prod.cursor()
    
    tablas_importantes = ['usuarios', 'stock_ferretero', 'dotaciones', 'cambios_dotacion', 'ingresos_dotaciones']
    
    print(f"\n📊 ANÁLISIS DE TABLAS IMPORTANTES:")
    print("-" * 80)
    
    for tabla in tablas_importantes:
        print(f"\n🔍 TABLA: {tabla.upper()}")
        print("-" * 40)
        
        # Analizar en local
        local_data = analizar_tabla(cursor_local, tabla)
        print(f"LOCAL:      Existe: {local_data['existe']}, Registros: {local_data['registros']}")
        
        # Analizar en producción
        prod_data = analizar_tabla(cursor_prod, tabla)
        print(f"PRODUCCIÓN: Existe: {prod_data['existe']}, Registros: {prod_data['registros']}")
        
        # Comparar
        if local_data['existe'] != prod_data['existe']:
            print(f"⚠️  DIFERENCIA: Tabla existe en local pero no en producción")
        elif local_data['registros'] != prod_data['registros']:
            print(f"⚠️  DIFERENCIA: Diferentes cantidades de registros")
        else:
            print(f"✅ COINCIDE: Misma estructura y cantidad de registros")
    
    # Verificar vista específica
    print(f"\n🔍 VERIFICANDO VISTA: vista_stock_dotaciones")
    print("-" * 50)
    
    local_vista_existe, local_vista_def = verificar_vista(cursor_local, 'vista_stock_dotaciones')
    prod_vista_existe, prod_vista_def = verificar_vista(cursor_prod, 'vista_stock_dotaciones')
    
    print(f"LOCAL:      Vista existe: {local_vista_existe}")
    print(f"PRODUCCIÓN: Vista existe: {prod_vista_existe}")
    
    if local_vista_existe != prod_vista_existe:
        print(f"⚠️  DIFERENCIA: Vista no existe en ambos entornos")
    
    # Cerrar conexiones
    cursor_local.close()
    cursor_prod.close()
    conn_local.close()
    conn_prod.close()

def probar_endpoint_produccion():
    """Probar el endpoint en producción"""
    print("\n" + "="*80)
    print("🌐 PROBANDO ENDPOINT EN PRODUCCIÓN")
    print("="*80)
    
    # Obtener URL de producción desde variables de entorno
    url_prod = os.getenv('API_URL_PROD', 'https://tu-servidor-produccion.com')
    endpoint = f"{url_prod}/api/refresh-stock-dotaciones"
    
    print(f"🔗 URL de producción: {endpoint}")
    
    try:
        response = requests.post(endpoint, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ RESPUESTA EXITOSA:")
            print(f"   Mensaje: {data.get('message', 'N/A')}")
            print(f"   Success: {data.get('success', 'N/A')}")
            
            if 'stock_actualizado' in data:
                print(f"   Materiales procesados: {len(data['stock_actualizado'])}")
                for item in data['stock_actualizado'][:3]:  # Mostrar solo los primeros 3
                    print(f"     - {item.get('material', 'N/A')}: Stock actual {item.get('stock_actual', 'N/A')}")
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        print("💡 Verifica:")
        print("   - La variable API_URL_PROD está configurada")
        print("   - El servidor de producción está funcionando")
        print("   - La conectividad de red")

def generar_reporte_diagnostico():
    """Generar un reporte completo de diagnóstico"""
    print("\n" + "="*80)
    print("📋 REPORTE DE DIAGNÓSTICO COMPLETO")
    print("="*80)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🕐 Fecha y hora: {timestamp}")
    
    print("\n🔧 VARIABLES DE ENTORNO CONFIGURADAS:")
    variables_importantes = ['DB_HOST_PROD', 'DB_USER_PROD', 'DB_NAME_PROD', 'API_URL_PROD']
    
    for var in variables_importantes:
        valor = os.getenv(var, 'NO CONFIGURADA')
        if 'PASS' in var:
            valor = '***' if valor != 'NO CONFIGURADA' else 'NO CONFIGURADA'
        print(f"   {var}: {valor}")
    
    print("\n💡 RECOMENDACIONES:")
    print("   1. Verificar que todas las variables de entorno estén configuradas")
    print("   2. Confirmar que la tabla 'dotaciones' tenga datos en producción")
    print("   3. Verificar que la vista 'vista_stock_dotaciones' exista en producción")
    print("   4. Revisar logs del servidor de producción")
    print("   5. Verificar permisos de base de datos en producción")

def main():
    """Función principal"""
    print("🚀 INICIANDO VERIFICACIÓN DE PRODUCCIÓN")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ejecutar todas las verificaciones
    comparar_entornos()
    probar_endpoint_produccion()
    generar_reporte_diagnostico()
    
    print("\n" + "="*80)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("="*80)

if __name__ == "__main__":
    main()