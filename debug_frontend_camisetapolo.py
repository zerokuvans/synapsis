#!/usr/bin/env python3
"""
Script de debug para analizar el problema de camiseta polo en el frontend
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import get_db_connection
import json
from datetime import datetime

def debug_frontend_camisetapolo():
    """Debug del problema de camiseta polo en el frontend"""
    print("🔍 DEBUG: Problema de camiseta polo en frontend")
    print("=" * 60)
    
    # 1. Verificar el mapeo de elementos en dotaciones_api.py
    print("\n1. MAPEO DE ELEMENTOS:")
    mapeo_elementos = {
        'camisetapolo': 'camiseta_polo',  # Frontend -> Backend
        'camisetagris': 'camiseta_gris',
        'pantalon': 'pantalon',
        'guerrera': 'guerrera'
    }
    
    for frontend, backend in mapeo_elementos.items():
        print(f"   {frontend} -> {backend}")
    
    # 2. Simular datos del frontend
    print("\n2. SIMULACIÓN DE DATOS DEL FRONTEND:")
    
    # Caso 1: Checkbox marcado (VALORADO)
    datos_valorado = {
        'camisetapolo': 1,
        'camisetapolo_valorado': 'on'  # Checkbox marcado
    }
    
    # Caso 2: Checkbox NO marcado (NO VALORADO)
    datos_no_valorado = {
        'camisetapolo': 1
        # camisetapolo_valorado no está presente cuando no está marcado
    }
    
    casos = [
        ("Checkbox MARCADO (VALORADO)", datos_valorado),
        ("Checkbox NO MARCADO (NO VALORADO)", datos_no_valorado)
    ]
    
    for descripcion, datos in casos:
        print(f"\n  {descripcion}:")
        print(f"    Datos enviados: {datos}")
        
        # Simular procesamiento en dotaciones_api.py
        elemento = 'camisetapolo'
        cantidad = datos.get(elemento, 0)
        
        if cantidad > 0:
            # Mapear elemento
            elemento_mapeado = mapeo_elementos.get(elemento, elemento)
            
            # Determinar estado
            valorado_key = f'{elemento}_valorado'
            es_valorado = datos.get(valorado_key) == 'on'  # Checkbox marcado
            estado = 'VALORADO' if es_valorado else 'NO VALORADO'
            
            print(f"    Elemento original: {elemento}")
            print(f"    Elemento mapeado: {elemento_mapeado}")
            print(f"    Checkbox key: {valorado_key}")
            print(f"    Checkbox value: {datos.get(valorado_key, 'NO PRESENTE')}")
            print(f"    Es valorado: {es_valorado}")
            print(f"    Estado final: {estado}")
    
    # 3. Verificar stock disponible
    print("\n3. VERIFICACIÓN DE STOCK:")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Stock de camisetapolo por estado
    query = """
    SELECT 
        tipo_elemento,
        estado_camiseta_polo as estado,
        SUM(camisetapolo) as stock_total
    FROM ingresos_dotaciones 
    WHERE camisetapolo > 0 
    GROUP BY tipo_elemento, estado_camiseta_polo
    ORDER BY tipo_elemento, estado_camiseta_polo
    """
    
    cursor.execute(query)
    resultados = cursor.fetchall()
    
    print("   Stock en ingresos_dotaciones:")
    for resultado in resultados:
        print(f"     {resultado['tipo_elemento']} - {resultado['estado']}: {resultado['stock_total']} unidades")
    
    # 4. Simular validación de stock
    print("\n4. SIMULACIÓN DE VALIDACIÓN:")
    
    from validacion_stock_por_estado import ValidacionStockPorEstado
    validador = ValidacionStockPorEstado()
    
    for descripcion, datos in casos:
        print(f"\n  {descripcion}:")
        
        elemento = 'camisetapolo'
        cantidad = datos.get(elemento, 0)
        
        if cantidad > 0:
            elemento_mapeado = mapeo_elementos.get(elemento, elemento)
            valorado_key = f'{elemento}_valorado'
            es_valorado = datos.get(valorado_key) == 'on'
            estado = 'VALORADO' if es_valorado else 'NO VALORADO'
            
            # Validar con elemento original
            items_dict_original = {elemento: cantidad}
            estados_dict_original = {elemento: estado}
            
            es_valido_original, mensaje_original = validador.validar_asignacion_con_estados(
                1, items_dict_original, estados_dict_original
            )
            
            print(f"    Validación con '{elemento}' {estado}:")
            print(f"      Resultado: {es_valido_original}")
            print(f"      Mensaje: {mensaje_original}")
            
            # Validar con elemento mapeado
            items_dict_mapeado = {elemento_mapeado: cantidad}
            estados_dict_mapeado = {elemento_mapeado: estado}
            
            es_valido_mapeado, mensaje_mapeado = validador.validar_asignacion_con_estados(
                1, items_dict_mapeado, estados_dict_mapeado
            )
            
            print(f"    Validación con '{elemento_mapeado}' {estado}:")
            print(f"      Resultado: {es_valido_mapeado}")
            print(f"      Mensaje: {mensaje_mapeado}")
    
    # 5. Verificar inconsistencias en IDs de checkboxes
    print("\n5. ANÁLISIS DE IDS DE CHECKBOXES:")
    
    ids_checkboxes = {
        'cambios_dotacion.html': {
            'id': 'estado_camiseta_polo',
            'name': 'camisetapolo_valorado'
        },
        'dotaciones.html (nuevo)': {
            'id': 'estadoCamisetaPolo',
            'name': 'camiseta_polo_valorado'
        },
        'dotaciones.html (viejo)': {
            'id': 'estadoCamisetapolo',
            'name': 'estado_camiseta_polo'
        }
    }
    
    print("   IDs de checkboxes en diferentes archivos:")
    for archivo, ids in ids_checkboxes.items():
        print(f"     {archivo}:")
        print(f"       ID: {ids['id']}")
        print(f"       Name: {ids['name']}")
    
    cursor.close()
    conn.close()
    validador.cerrar_conexion()

if __name__ == "__main__":
    debug_frontend_camisetapolo()