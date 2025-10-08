#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para probar que el sistema de validación de stock 
ahora maneja correctamente ambas variantes: 'camisetapolo' y 'camiseta_polo'
"""

import mysql.connector
from mysql.connector import Error
from validacion_stock_por_estado import ValidadorStockPorEstado

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'capired'
}

def conectar_db():
    """Conectar a la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def verificar_datos_existentes():
    """Verificar qué datos existen actualmente en la base de datos"""
    connection = conectar_db()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print("=== VERIFICACIÓN DE DATOS EXISTENTES ===\n")
        
        # 1. Verificar registros en ingresos_dotaciones
        print("1. REGISTROS EN ingresos_dotaciones:")
        cursor.execute("""
            SELECT tipo_elemento, estado, COUNT(*) as cantidad_registros, SUM(cantidad) as total_unidades
            FROM ingresos_dotaciones 
            WHERE tipo_elemento IN ('camisetapolo', 'camiseta_polo')
            GROUP BY tipo_elemento, estado
            ORDER BY tipo_elemento, estado
        """)
        
        registros = cursor.fetchall()
        if registros:
            for reg in registros:
                print(f"   - {reg['tipo_elemento']} ({reg['estado']}): {reg['cantidad_registros']} registros, {reg['total_unidades']} unidades")
        else:
            print("   ❌ No se encontraron registros")
        
        print("\n" + "="*50)
        
        # 2. Verificar total combinado
        print("\n2. TOTAL COMBINADO (ambas variantes):")
        cursor.execute("""
            SELECT estado, COUNT(*) as cantidad_registros, SUM(cantidad) as total_unidades
            FROM ingresos_dotaciones 
            WHERE tipo_elemento IN ('camisetapolo', 'camiseta_polo')
            GROUP BY estado
            ORDER BY estado
        """)
        
        totales = cursor.fetchall()
        if totales:
            for total in totales:
                print(f"   - {total['estado']}: {total['cantidad_registros']} registros, {total['total_unidades']} unidades")
        else:
            print("   ❌ No se encontraron registros")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error verificando datos: {e}")

def probar_validacion_con_ambas_variantes():
    """Probar la validación de stock con ambas variantes"""
    print("\n=== PRUEBA DE VALIDACIÓN CON AMBAS VARIANTES ===\n")
    
    validador = ValidadorStockPorEstado()
    
    # Prueba 1: Validar con 'camisetapolo'
    print("1. PRUEBA CON 'camisetapolo':")
    items_dict_1 = {'camisetapolo': 2}
    estados_dict_1 = {'camisetapolo': 'VALORADO'}
    
    es_valido_1, mensaje_1, stock_1 = validador.validar_stock_por_estado(items_dict_1, estados_dict_1)
    print(f"   Resultado: {'✅ VÁLIDO' if es_valido_1 else '❌ INVÁLIDO'}")
    print(f"   Mensaje: {mensaje_1}")
    print(f"   Stock actual: {stock_1}")
    
    print("\n" + "-"*30)
    
    # Prueba 2: Validar con 'camiseta_polo'
    print("\n2. PRUEBA CON 'camiseta_polo':")
    items_dict_2 = {'camiseta_polo': 2}
    estados_dict_2 = {'camiseta_polo': 'VALORADO'}
    
    es_valido_2, mensaje_2, stock_2 = validador.validar_stock_por_estado(items_dict_2, estados_dict_2)
    print(f"   Resultado: {'✅ VÁLIDO' if es_valido_2 else '❌ INVÁLIDO'}")
    print(f"   Mensaje: {mensaje_2}")
    print(f"   Stock actual: {stock_2}")
    
    print("\n" + "-"*30)
    
    # Prueba 3: Obtener stock detallado para ambas variantes
    print("\n3. STOCK DETALLADO PARA AMBAS VARIANTES:")
    
    print("\n   3a. Stock detallado para 'camisetapolo':")
    stock_detallado_1 = validador.obtener_stock_detallado_por_estado('camisetapolo')
    if stock_detallado_1:
        print(f"      VALORADO: Ingresos={stock_detallado_1['valorado']['ingresos']}, Disponible={stock_detallado_1['valorado']['disponible']}")
        print(f"      NO VALORADO: Ingresos={stock_detallado_1['no_valorado']['ingresos']}, Disponible={stock_detallado_1['no_valorado']['disponible']}")
    
    print("\n   3b. Stock detallado para 'camiseta_polo':")
    stock_detallado_2 = validador.obtener_stock_detallado_por_estado('camiseta_polo')
    if stock_detallado_2:
        print(f"      VALORADO: Ingresos={stock_detallado_2['valorado']['ingresos']}, Disponible={stock_detallado_2['valorado']['disponible']}")
        print(f"      NO VALORADO: Ingresos={stock_detallado_2['no_valorado']['ingresos']}, Disponible={stock_detallado_2['no_valorado']['disponible']}")
    
    # Verificar que ambas consultas devuelven los mismos resultados
    if stock_detallado_1 and stock_detallado_2:
        print("\n4. VERIFICACIÓN DE CONSISTENCIA:")
        valorado_igual = (stock_detallado_1['valorado']['ingresos'] == stock_detallado_2['valorado']['ingresos'])
        no_valorado_igual = (stock_detallado_1['no_valorado']['ingresos'] == stock_detallado_2['no_valorado']['ingresos'])
        
        if valorado_igual and no_valorado_igual:
            print("   ✅ CONSISTENCIA VERIFICADA: Ambas variantes devuelven los mismos resultados")
        else:
            print("   ❌ INCONSISTENCIA DETECTADA: Las variantes devuelven resultados diferentes")
            print(f"      Valorado igual: {valorado_igual}")
            print(f"      No valorado igual: {no_valorado_igual}")

def probar_api_stock():
    """Probar que la API de stock también funciona correctamente"""
    print("\n=== PRUEBA DE API DE STOCK ===\n")
    
    connection = conectar_db()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Simular la consulta que hace la API para camisetapolo
        print("1. CONSULTA DE STOCK COMO LA API:")
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0) as total_ingresos
            FROM ingresos_dotaciones 
            WHERE tipo_elemento = 'camisetapolo' OR tipo_elemento = 'camiseta_polo'
        """)
        
        resultado = cursor.fetchone()
        total_ingresos = resultado['total_ingresos'] if resultado else 0
        
        print(f"   Total de ingresos (ambas variantes): {total_ingresos}")
        
        # Comparar con consulta individual
        cursor.execute("""
            SELECT 
                (SELECT COALESCE(SUM(cantidad), 0) FROM ingresos_dotaciones WHERE tipo_elemento = 'camisetapolo') as solo_camisetapolo,
                (SELECT COALESCE(SUM(cantidad), 0) FROM ingresos_dotaciones WHERE tipo_elemento = 'camiseta_polo') as solo_camiseta_polo
        """)
        
        comparacion = cursor.fetchone()
        solo_camisetapolo = comparacion['solo_camisetapolo'] if comparacion else 0
        solo_camiseta_polo = comparacion['solo_camiseta_polo'] if comparacion else 0
        
        print(f"   Solo 'camisetapolo': {solo_camisetapolo}")
        print(f"   Solo 'camiseta_polo': {solo_camiseta_polo}")
        print(f"   Suma individual: {solo_camisetapolo + solo_camiseta_polo}")
        
        if total_ingresos == (solo_camisetapolo + solo_camiseta_polo):
            print("   ✅ VERIFICACIÓN EXITOSA: La consulta combinada es correcta")
        else:
            print("   ❌ ERROR: La consulta combinada no coincide con la suma individual")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error probando API de stock: {e}")

def main():
    """Función principal"""
    print("🔍 PRUEBA DE VALIDACIÓN CON AMBAS VARIANTES DE CAMISETA POLO")
    print("="*60)
    
    # 1. Verificar datos existentes
    verificar_datos_existentes()
    
    # 2. Probar validación
    probar_validacion_con_ambas_variantes()
    
    # 3. Probar API
    probar_api_stock()
    
    print("\n" + "="*60)
    print("✅ PRUEBA COMPLETADA")

if __name__ == "__main__":
    main()