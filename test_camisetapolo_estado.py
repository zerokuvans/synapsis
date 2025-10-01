#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el estado específico de camisetapolo
"""

from validacion_stock_por_estado import ValidadorStockPorEstado
import mysql.connector

def test_camisetapolo_estado():
    """Probar diferentes estados para camisetapolo"""
    print("=== TEST CAMISETAPOLO ESTADO ===\n")
    
    validador = ValidadorStockPorEstado()
    if not validador.conexion:
        print("❌ No se pudo conectar a la base de datos")
        return
    
    cursor = validador.conexion.cursor(dictionary=True)
    
    # 1. Verificar stock disponible por estado
    print("1. STOCK DISPONIBLE POR ESTADO:")
    
    for estado in ['VALORADO', 'NO VALORADO']:
        stock_camisetapolo = validador._calcular_stock_por_estado(cursor, 'camisetapolo', estado)
        stock_camiseta_polo = validador._calcular_stock_por_estado(cursor, 'camiseta_polo', estado)
        
        print(f"  {estado}:")
        print(f"    camisetapolo: {stock_camisetapolo}")
        print(f"    camiseta_polo: {stock_camiseta_polo}")
    
    # 2. Probar validación con diferentes estados
    print("\n2. PROBANDO VALIDACIÓN CON DIFERENTES ESTADOS:")
    
    # Caso 1: camiseta_polo VALORADO (debería funcionar)
    print("\n  Caso 1: camiseta_polo VALORADO")
    items_dict = {'camiseta_polo': 1}
    estados_dict = {'camiseta_polo': 'VALORADO'}
    es_valido, mensaje = validador.validar_asignacion_con_estados(1, items_dict, estados_dict)
    print(f"    Resultado: {es_valido}")
    print(f"    Mensaje: {mensaje}")
    
    # Caso 2: camiseta_polo NO VALORADO (debería fallar)
    print("\n  Caso 2: camiseta_polo NO VALORADO")
    items_dict = {'camiseta_polo': 1}
    estados_dict = {'camiseta_polo': 'NO VALORADO'}
    es_valido, mensaje = validador.validar_asignacion_con_estados(1, items_dict, estados_dict)
    print(f"    Resultado: {es_valido}")
    print(f"    Mensaje: {mensaje}")
    
    # Caso 3: camisetapolo VALORADO (como viene del frontend)
    print("\n  Caso 3: camisetapolo VALORADO")
    items_dict = {'camisetapolo': 1}
    estados_dict = {'camisetapolo': 'VALORADO'}
    es_valido, mensaje = validador.validar_asignacion_con_estados(1, items_dict, estados_dict)
    print(f"    Resultado: {es_valido}")
    print(f"    Mensaje: {mensaje}")
    
    # Caso 4: camisetapolo NO VALORADO (como viene del frontend)
    print("\n  Caso 4: camisetapolo NO VALORADO")
    items_dict = {'camisetapolo': 1}
    estados_dict = {'camisetapolo': 'NO VALORADO'}
    es_valido, mensaje = validador.validar_asignacion_con_estados(1, items_dict, estados_dict)
    print(f"    Resultado: {es_valido}")
    print(f"    Mensaje: {mensaje}")
    
    # 3. Simular el mapeo que hace dotaciones_api.py
    print("\n3. SIMULANDO MAPEO DE DOTACIONES_API.PY:")
    
    # Simular datos del frontend con checkbox NO marcado (NO VALORADO)
    data_frontend_no_valorado = {
        'camisetapolo': 1,
        'camisetapolo_valorado': False  # Checkbox no marcado
    }
    
    # Simular datos del frontend con checkbox marcado (VALORADO)
    data_frontend_valorado = {
        'camisetapolo': 1,
        'camisetapolo_valorado': True  # Checkbox marcado
    }
    
    for i, (data, descripcion) in enumerate([
        (data_frontend_no_valorado, "Checkbox NO marcado (NO VALORADO)"),
        (data_frontend_valorado, "Checkbox marcado (VALORADO)")
    ], 1):
        print(f"\n  Simulación {i}: {descripcion}")
        print(f"    Datos frontend: {data}")
        
        # Simular el mapeo de dotaciones_api.py
        elemento = 'camisetapolo'
        cantidad = data.get(elemento)
        if cantidad and cantidad > 0:
            elemento_mapeado = 'camiseta_polo'  # Mapeo camisetapolo -> camiseta_polo
            valorado_key = f'{elemento}_valorado'
            es_valorado = data.get(valorado_key, False)
            estado = 'VALORADO' if es_valorado else 'NO VALORADO'
            
            print(f"    Elemento mapeado: {elemento_mapeado}")
            print(f"    Estado calculado: {estado}")
            
            # Probar validación
            items_dict = {elemento_mapeado: cantidad}
            estados_dict = {elemento_mapeado: estado}
            es_valido, mensaje = validador.validar_asignacion_con_estados(1, items_dict, estados_dict)
            print(f"    Validación: {es_valido}")
            print(f"    Mensaje: {mensaje}")
    
    cursor.close()
    validador.cerrar_conexion()

if __name__ == "__main__":
    test_camisetapolo_estado()