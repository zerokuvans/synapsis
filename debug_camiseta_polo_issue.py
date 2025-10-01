#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debuggear el problema específico con camiseta_polo
"""

from validacion_stock_por_estado import ValidadorStockPorEstado
import mysql.connector

def debug_camiseta_polo_issue():
    """Debug específico del problema con camiseta_polo"""
    print("=== DEBUG CAMISETA POLO ISSUE ===\n")
    
    validador = ValidadorStockPorEstado()
    if not validador.conexion:
        print("❌ No se pudo conectar a la base de datos")
        return
    
    # 1. Verificar stock en ingresos_dotaciones
    print("1. VERIFICANDO STOCK EN INGRESOS_DOTACIONES:")
    cursor = validador.conexion.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT tipo_elemento, estado, SUM(cantidad) as total
        FROM ingresos_dotaciones 
        WHERE tipo_elemento IN ('camiseta_polo', 'camisetapolo')
        GROUP BY tipo_elemento, estado
        ORDER BY tipo_elemento, estado
    """)
    
    stock_ingresos = cursor.fetchall()
    for row in stock_ingresos:
        print(f"  {row['tipo_elemento']} - {row['estado']}: {row['total']}")
    
    if not stock_ingresos:
        print("  ❌ NO HAY STOCK DE CAMISETA POLO EN INGRESOS_DOTACIONES")
    
    # 2. Verificar salidas en dotaciones
    print("\n2. VERIFICANDO SALIDAS EN DOTACIONES:")
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN estado_camiseta_polo = 'VALORADO' THEN camisetapolo ELSE 0 END) as valorado,
            SUM(CASE WHEN estado_camiseta_polo = 'NO VALORADO' THEN camisetapolo ELSE 0 END) as no_valorado
        FROM dotaciones 
        WHERE camisetapolo > 0
    """)
    
    salidas_dotaciones = cursor.fetchone()
    print(f"  Salidas VALORADO: {salidas_dotaciones['valorado'] or 0}")
    print(f"  Salidas NO VALORADO: {salidas_dotaciones['no_valorado'] or 0}")
    
    # 3. Verificar salidas en cambios_dotacion
    print("\n3. VERIFICANDO SALIDAS EN CAMBIOS_DOTACION:")
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN estado_camiseta_polo = 'VALORADO' THEN camisetapolo ELSE 0 END) as valorado,
            SUM(CASE WHEN estado_camiseta_polo = 'NO VALORADO' THEN camisetapolo ELSE 0 END) as no_valorado
        FROM cambios_dotacion 
        WHERE camisetapolo > 0
    """)
    
    salidas_cambios = cursor.fetchone()
    print(f"  Salidas VALORADO: {salidas_cambios['valorado'] or 0}")
    print(f"  Salidas NO VALORADO: {salidas_cambios['no_valorado'] or 0}")
    
    # 4. Probar validador con camiseta_polo
    print("\n4. PROBANDO VALIDADOR CON CAMISETA_POLO:")
    
    items_dict = {'camiseta_polo': 1}
    estados_dict = {'camiseta_polo': 'NO VALORADO'}
    
    print(f"  Solicitando: {items_dict}")
    print(f"  Estados: {estados_dict}")
    
    es_valido, mensaje = validador.validar_asignacion_con_estados(1, items_dict, estados_dict)
    
    print(f"  Resultado: {es_valido}")
    print(f"  Mensaje: {mensaje}")
    
    # 5. Probar validador con camisetapolo (como viene del frontend)
    print("\n5. PROBANDO VALIDADOR CON CAMISETAPOLO (FRONTEND):")
    
    items_dict_frontend = {'camisetapolo': 1}
    estados_dict_frontend = {'camisetapolo': 'NO VALORADO'}
    
    print(f"  Solicitando: {items_dict_frontend}")
    print(f"  Estados: {estados_dict_frontend}")
    
    es_valido_frontend, mensaje_frontend = validador.validar_asignacion_con_estados(1, items_dict_frontend, estados_dict_frontend)
    
    print(f"  Resultado: {es_valido_frontend}")
    print(f"  Mensaje: {mensaje_frontend}")
    
    # 6. Verificar el método _calcular_stock_por_estado directamente
    print("\n6. VERIFICANDO _calcular_stock_por_estado DIRECTAMENTE:")
    
    stock_camiseta_polo_no_valorado = validador._calcular_stock_por_estado(cursor, 'camiseta_polo', 'NO VALORADO')
    stock_camisetapolo_no_valorado = validador._calcular_stock_por_estado(cursor, 'camisetapolo', 'NO VALORADO')
    
    print(f"  Stock 'camiseta_polo' NO VALORADO: {stock_camiseta_polo_no_valorado}")
    print(f"  Stock 'camisetapolo' NO VALORADO: {stock_camisetapolo_no_valorado}")
    
    cursor.close()
    validador.cerrar_conexion()

if __name__ == "__main__":
    debug_camiseta_polo_issue()