#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar el stock de dotaciones y entender
el problema de validación con elementos "NO VALORADO"
"""

import mysql.connector
from mysql.connector import Error

def conectar_db():
    """Conectar a la base de datos"""
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        return conexion
    except Error as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def verificar_stock_por_estado():
    """Verificar stock disponible por estado para todos los elementos"""
    conexion = conectar_db()
    if not conexion:
        return
    
    try:
        print("=== DIAGNÓSTICO DE STOCK POR ESTADO ===\n")
        
        # Elementos a verificar
        elementos = ['pantalon', 'camisetagris', 'guerrera', 'camisetapolo', 
                    'guantes_nitrilo', 'guantes_carnaza', 'gafas', 'gorra', 'casco', 'botas']
        
        for elemento in elementos:
            verificar_stock_elemento(conexion, elemento)
        
        conexion.close()
        
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")

def verificar_stock_elemento(conn, elemento):
    """Verificar stock disponible por estado para un elemento específico"""
    cursor = conn.cursor()
    
    try:
        print(f"📦 {elemento.upper()}:")
        
        # Obtener campos de estado para cada tabla
        campo_estado_dotaciones = obtener_campo_estado(elemento, 'dotaciones')
        campo_estado_cambios = obtener_campo_estado(elemento, 'cambios_dotacion')
        
        stock_valorado = {'ingresos': 0, 'dotaciones': 0, 'cambios': 0}
        stock_no_valorado = {'ingresos': 0, 'dotaciones': 0, 'cambios': 0}
        
        for estado in ['VALORADO', 'NO VALORADO']:
            stock_dict = stock_valorado if estado == 'VALORADO' else stock_no_valorado
            
            # 1. Ingresos
            cursor.execute("""
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = %s AND estado = %s
            """, (elemento, estado))
            stock_dict['ingresos'] = cursor.fetchone()[0]
            
            # 2. Salidas por dotaciones
            cursor.execute(f"""
                SELECT COALESCE(SUM({elemento}), 0) 
                FROM dotaciones 
                WHERE {campo_estado_dotaciones} = %s
            """, (estado,))
            stock_dict['dotaciones'] = cursor.fetchone()[0]
            
            # 3. Salidas por cambios
            cursor.execute(f"""
                SELECT COALESCE(SUM({elemento}), 0) 
                FROM cambios_dotacion 
                WHERE {campo_estado_cambios} = %s
            """, (estado,))
            stock_dict['cambios'] = cursor.fetchone()[0]
        
        # Mostrar resultados
        print(f"  📥 Ingresos:")
        print(f"    VALORADO: {stock_valorado['ingresos']}")
        print(f"    NO VALORADO: {stock_no_valorado['ingresos']}")
        print(f"  📤 Salidas (Dotaciones):")
        print(f"    VALORADO: {stock_valorado['dotaciones']}")
        print(f"    NO VALORADO: {stock_no_valorado['dotaciones']}")
        print(f"  🔄 Salidas (Cambios):")
        print(f"    VALORADO: {stock_valorado['cambios']}")
        print(f"    NO VALORADO: {stock_no_valorado['cambios']}")
        print(f"  💰 STOCK DISPONIBLE:")
        
        valorado_disponible = max(0, stock_valorado['ingresos'] - stock_valorado['dotaciones'] - stock_valorado['cambios'])
        no_valorado_disponible = max(0, stock_no_valorado['ingresos'] - stock_no_valorado['dotaciones'] - stock_no_valorado['cambios'])
        
        print(f"    VALORADO: {valorado_disponible}")
        print(f"    NO VALORADO: {no_valorado_disponible}")
        print()
        
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
    finally:
        cursor.close()

def obtener_campo_estado(elemento, tabla='dotaciones'):
    """Obtener el nombre del campo de estado para un elemento"""
    # Mapeo para tabla dotaciones
    mapeo_dotaciones = {
        'pantalon': 'estado_pantalon',
        'camisetagris': 'estado_camisetagris',
        'camiseta_gris': 'estado_camisetagris',
        'guerrera': 'estado_guerrera',
        'camisetapolo': 'estado_camiseta_polo',
        'camiseta_polo': 'estado_camiseta_polo',
        'guantes_nitrilo': 'estado_guantes_nitrilo',
        'guantes_carnaza': 'estado_guantes_carnaza',
        'gafas': 'estado_gafas',
        'gorra': 'estado_gorra',
        'casco': 'estado_casco',
        'botas': 'estado_botas'
    }
    
    # Mapeo para tabla cambios_dotacion (tiene nombres diferentes)
    mapeo_cambios = {
        'pantalon': 'estado_pantalon',
        'camisetagris': 'estado_camiseta_gris',  # Diferente en cambios_dotacion
        'camiseta_gris': 'estado_camiseta_gris',
        'guerrera': 'estado_guerrera',
        'camisetapolo': 'estado_camiseta_polo',
        'camiseta_polo': 'estado_camiseta_polo',
        'guantes_nitrilo': 'estado_guantes_nitrilo',
        'guantes_carnaza': 'estado_guantes_carnaza',
        'gafas': 'estado_gafas',
        'gorra': 'estado_gorra',
        'casco': 'estado_casco',
        'botas': 'estado_botas'
    }
    
    if tabla == 'cambios_dotacion':
        return mapeo_cambios.get(elemento, f'estado_{elemento}')
    else:
        return mapeo_dotaciones.get(elemento, f'estado_{elemento}')

def verificar_estructura_tablas():
    """Verificar la estructura de las tablas relacionadas"""
    conexion = conectar_db()
    if not conexion:
        return
    
    try:
        cursor = conexion.cursor(dictionary=True)
        
        print("=== VERIFICACIÓN DE ESTRUCTURA DE TABLAS ===\n")
        
        # Verificar tabla ingresos_dotaciones
        print("📋 Tabla: ingresos_dotaciones")
        cursor.execute("DESCRIBE ingresos_dotaciones")
        columnas = cursor.fetchall()
        for col in columnas:
            print(f"  - {col['Field']}: {col['Type']}")
        
        # Verificar algunos registros
        cursor.execute("SELECT * FROM ingresos_dotaciones LIMIT 5")
        registros = cursor.fetchall()
        print(f"  📊 Registros de ejemplo: {len(registros)} encontrados")
        for reg in registros[:2]:
            print(f"    {reg}")
        print()
        
        # Verificar tabla dotaciones (campos de estado)
        print("📋 Tabla: dotaciones (campos de estado)")
        cursor.execute("DESCRIBE dotaciones")
        columnas = cursor.fetchall()
        campos_estado = [col['Field'] for col in columnas if 'estado_' in col['Field']]
        print(f"  📝 Campos de estado encontrados: {campos_estado}")
        print()
        
        cursor.close()
        conexion.close()
        
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")

if __name__ == "__main__":
    verificar_estructura_tablas()
    print("\n" + "="*50 + "\n")
    verificar_stock_por_estado()