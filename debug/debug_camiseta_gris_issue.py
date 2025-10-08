#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debuggear el problema específico con camiseta_gris VALORADO
"""

from validacion_stock_por_estado import ValidadorStockPorEstado
import mysql.connector

def debug_camiseta_gris_issue():
    """Debug específico del problema con camiseta_gris"""
    print("=== DEBUG CAMISETA GRIS ISSUE ===\n")
    
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
        WHERE tipo_elemento IN ('camiseta_gris', 'camisetagris')
        GROUP BY tipo_elemento, estado
        ORDER BY tipo_elemento, estado
    """)
    
    stock_ingresos = cursor.fetchall()
    for row in stock_ingresos:
        print(f"  {row['tipo_elemento']} - {row['estado']}: {row['total']}")
    
    # 2. Verificar salidas en dotaciones
    print("\n2. VERIFICANDO SALIDAS EN DOTACIONES:")
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN estado_camisetagris = 'VALORADO' THEN camisetagris ELSE 0 END) as valorado,
            SUM(CASE WHEN estado_camisetagris = 'NO VALORADO' THEN camisetagris ELSE 0 END) as no_valorado
        FROM dotaciones 
        WHERE camisetagris > 0
    """)
    
    salidas_dotaciones = cursor.fetchone()
    print(f"  Salidas VALORADO: {salidas_dotaciones['valorado'] or 0}")
    print(f"  Salidas NO VALORADO: {salidas_dotaciones['no_valorado'] or 0}")
    
    # 3. Verificar salidas en cambios_dotacion
    print("\n3. VERIFICANDO SALIDAS EN CAMBIOS_DOTACION:")
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN estado_camiseta_gris = 'VALORADO' THEN camisetagris ELSE 0 END) as valorado,
            SUM(CASE WHEN estado_camiseta_gris = 'NO VALORADO' THEN camisetagris ELSE 0 END) as no_valorado
        FROM cambios_dotacion 
        WHERE camisetagris > 0
    """)
    
    salidas_cambios = cursor.fetchone()
    print(f"  Salidas VALORADO: {salidas_cambios['valorado'] or 0}")
    print(f"  Salidas NO VALORADO: {salidas_cambios['no_valorado'] or 0}")
    
    # 4. Calcular stock disponible manualmente
    print("\n4. CÁLCULO MANUAL DE STOCK DISPONIBLE:")
    
    # Para camiseta_gris VALORADO
    ingresos_valorado = 0
    ingresos_no_valorado = 0
    
    for row in stock_ingresos:
        if row['tipo_elemento'] == 'camiseta_gris':
            if row['estado'] == 'VALORADO':
                ingresos_valorado = row['total']
            elif row['estado'] == 'NO VALORADO':
                ingresos_no_valorado = row['total']
    
    salidas_valorado = (salidas_dotaciones['valorado'] or 0) + (salidas_cambios['valorado'] or 0)
    salidas_no_valorado = (salidas_dotaciones['no_valorado'] or 0) + (salidas_cambios['no_valorado'] or 0)
    
    disponible_valorado = ingresos_valorado - salidas_valorado
    disponible_no_valorado = ingresos_no_valorado - salidas_no_valorado
    
    print(f"  VALORADO: {ingresos_valorado} (ingresos) - {salidas_valorado} (salidas) = {disponible_valorado} (disponible)")
    print(f"  NO VALORADO: {ingresos_no_valorado} (ingresos) - {salidas_no_valorado} (salidas) = {disponible_no_valorado} (disponible)")
    
    # 5. Probar validador con camiseta_gris
    print("\n5. PROBANDO VALIDADOR CON CAMISETA_GRIS:")
    
    items_dict = {'camiseta_gris': 3}
    estados_dict = {'camiseta_gris': 'VALORADO'}
    
    print(f"  Solicitando: {items_dict}")
    print(f"  Estados: {estados_dict}")
    
    es_valido, mensaje = validador.validar_asignacion_con_estados(1, items_dict, estados_dict)
    
    print(f"  Resultado: {es_valido}")
    print(f"  Mensaje: {mensaje}")
    
    # 6. Probar validador con camisetagris (como viene del frontend)
    print("\n6. PROBANDO VALIDADOR CON CAMISETAGRIS (FRONTEND):")
    
    items_dict_frontend = {'camisetagris': 3}
    estados_dict_frontend = {'camisetagris': 'VALORADO'}
    
    print(f"  Solicitando: {items_dict_frontend}")
    print(f"  Estados: {estados_dict_frontend}")
    
    es_valido_frontend, mensaje_frontend = validador.validar_asignacion_con_estados(1, items_dict_frontend, estados_dict_frontend)
    
    print(f"  Resultado: {es_valido_frontend}")
    print(f"  Mensaje: {mensaje_frontend}")
    
    # 7. Verificar el método _calcular_stock_por_estado directamente
    print("\n7. VERIFICANDO _calcular_stock_por_estado DIRECTAMENTE:")
    
    stock_camiseta_gris_valorado = validador._calcular_stock_por_estado(cursor, 'camiseta_gris', 'VALORADO')
    stock_camisetagris_valorado = validador._calcular_stock_por_estado(cursor, 'camisetagris', 'VALORADO')
    
    print(f"  Stock 'camiseta_gris' VALORADO: {stock_camiseta_gris_valorado}")
    print(f"  Stock 'camisetagris' VALORADO: {stock_camisetagris_valorado}")
    
    cursor.close()
    validador.cerrar_conexion()

if __name__ == "__main__":
    debug_camiseta_gris_issue()