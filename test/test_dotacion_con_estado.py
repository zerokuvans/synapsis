#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que las asignaciones de dotaciones
respeten la elección de valoración del usuario
"""

import requests
import json
from validacion_stock_por_estado import ValidadorStockPorEstado

def test_asignacion_dotacion_con_estado():
    """
    Probar que las asignaciones respeten la elección de valoración del usuario
    """
    print("=== PRUEBA DE ASIGNACIÓN DE DOTACIÓN CON ESTADO ===")
    
    # 1. Verificar stock actual por estado
    print("\n1. Verificando stock actual por estado...")
    validador = ValidadorStockPorEstado()
    
    # Verificar stock de botas
    stock_botas = validador.obtener_stock_detallado_por_estado('botas')
    print(f"Stock actual de botas:")
    print(f"  - VALORADO: {stock_botas.get('VALORADO', 0)}")
    print(f"  - NO VALORADO: {stock_botas.get('NO VALORADO', 0)}")
    
    # Verificar stock de pantalón
    stock_pantalon = validador.obtener_stock_detallado_por_estado('pantalon')
    print(f"Stock actual de pantalón:")
    print(f"  - VALORADO: {stock_pantalon.get('VALORADO', 0)}")
    print(f"  - NO VALORADO: {stock_pantalon.get('NO VALORADO', 0)}")
    
    # 2. Preparar datos de prueba para dotación
    print("\n2. Preparando datos de prueba...")
    
    # Caso 1: Asignar botas NO VALORADAS (debería funcionar si hay stock)
    dotacion_data_1 = {
        'cliente': 'CLIENTE_PRUEBA_ESTADO',
        'id_codigo_consumidor': 99999999,  # ID de prueba
        'botas': 1,
        'botas_talla': '42',
        'estado_botas': 'NO VALORADO',
        'pantalon': 0,
        'camisetagris': 0,
        'guerrera': 0,
        'camisetapolo': 0,
        'guantes_nitrilo': 0,
        'guantes_carnaza': 0,
        'gafas': 0,
        'gorra': 0,
        'casco': 0
    }
    
    # Caso 2: Asignar pantalón VALORADO (debería fallar si no hay stock valorado)
    dotacion_data_2 = {
        'cliente': 'CLIENTE_PRUEBA_ESTADO_2',
        'id_codigo_consumidor': 88888888,  # ID de prueba
        'pantalon': 1,
        'pantalon_talla': 'M',
        'estado_pantalon': 'VALORADO',
        'botas': 0,
        'camisetagris': 0,
        'guerrera': 0,
        'camisetapolo': 0,
        'guantes_nitrilo': 0,
        'guantes_carnaza': 0,
        'gafas': 0,
        'gorra': 0,
        'casco': 0
    }
    
    print("\n3. Probando asignación de botas NO VALORADAS...")
    print(f"Datos: {json.dumps(dotacion_data_1, indent=2)}")
    
    # Simular validación antes de enviar
    items_dict_1 = {'botas': 1}
    estados_dict_1 = {'botas': 'NO VALORADO'}
    
    es_valido_1, resultado_1 = validador.validar_asignacion_con_estados(
        99999999, items_dict_1, estados_dict_1
    )
    
    print(f"Validación previa:")
    print(f"  - Válido: {es_valido_1}")
    print(f"  - Resultado: {resultado_1}")
    
    print("\n4. Probando asignación de pantalón VALORADO...")
    print(f"Datos: {json.dumps(dotacion_data_2, indent=2)}")
    
    # Simular validación antes de enviar
    items_dict_2 = {'pantalon': 1}
    estados_dict_2 = {'pantalon': 'VALORADO'}
    
    es_valido_2, resultado_2 = validador.validar_asignacion_con_estados(
        88888888, items_dict_2, estados_dict_2
    )
    
    print(f"Validación previa:")
    print(f"  - Válido: {es_valido_2}")
    print(f"  - Resultado: {resultado_2}")
    
    # 5. Verificar comportamiento esperado
    print("\n5. Análisis de resultados:")
    
    if stock_botas.get('NO VALORADO', 0) > 0:
        if es_valido_1:
            print("✅ CORRECTO: Asignación de botas NO VALORADAS es válida (hay stock NO VALORADO)")
        else:
            print("❌ ERROR: Asignación de botas NO VALORADAS debería ser válida")
    else:
        if not es_valido_1:
            print("✅ CORRECTO: Asignación de botas NO VALORADAS es inválida (no hay stock NO VALORADO)")
        else:
            print("❌ ERROR: Asignación de botas NO VALORADAS debería ser inválida")
    
    if stock_pantalon.get('VALORADO', 0) > 0:
        if es_valido_2:
            print("✅ CORRECTO: Asignación de pantalón VALORADO es válida (hay stock VALORADO)")
        else:
            print("❌ ERROR: Asignación de pantalón VALORADO debería ser válida")
    else:
        if not es_valido_2:
            print("✅ CORRECTO: Asignación de pantalón VALORADO es inválida (no hay stock VALORADO)")
        else:
            print("❌ ERROR: Asignación de pantalón VALORADO debería ser inválida")
    
    print("\n=== PRUEBA COMPLETADA ===")
    
    return {
        'stock_botas': stock_botas,
        'stock_pantalon': stock_pantalon,
        'validacion_botas_no_valorado': (es_valido_1, resultado_1),
        'validacion_pantalon_valorado': (es_valido_2, resultado_2)
    }

if __name__ == "__main__":
    try:
        resultados = test_asignacion_dotacion_con_estado()
        print(f"\nResultados finales: {json.dumps(resultados, indent=2)}")
    except Exception as e:
        print(f"Error en la prueba: {e}")
        import traceback
        traceback.print_exc()