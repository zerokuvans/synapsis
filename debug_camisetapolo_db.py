#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar directamente el stock de camisetapolo en la base de datos
"""

import mysql.connector
from validacion_stock_por_estado import ValidadorStockPorEstado

def debug_camisetapolo_db():
    """Debug directo de la base de datos para camisetapolo"""
    print("=== DEBUG CAMISETAPOLO BASE DE DATOS ===\n")
    
    validador = ValidadorStockPorEstado()
    if not validador.conexion:
        print("❌ No se pudo conectar a la base de datos")
        return
    
    cursor = validador.conexion.cursor(dictionary=True)
    
    # 1. Verificar ingresos_dotaciones
    print("1. INGRESOS_DOTACIONES:")
    cursor.execute("""
        SELECT tipo_elemento, estado, cantidad, fecha_ingreso
        FROM ingresos_dotaciones 
        WHERE tipo_elemento IN ('camisetapolo', 'camiseta_polo')
        ORDER BY fecha_ingreso DESC
    """)
    
    ingresos = cursor.fetchall()
    if ingresos:
        for ingreso in ingresos:
            print(f"  {ingreso['tipo_elemento']} - {ingreso['estado']}: {ingreso['cantidad']} (Fecha: {ingreso['fecha_ingreso']})")
    else:
        print("  ❌ NO HAY INGRESOS")
    
    # 2. Verificar dotaciones (salidas)
    print("\n2. DOTACIONES (SALIDAS):")
    cursor.execute("""
        SELECT camisetapolo, estado_camiseta_polo
        FROM dotaciones 
        WHERE camisetapolo > 0
        LIMIT 10
    """)
    
    dotaciones = cursor.fetchall()
    if dotaciones:
        for dotacion in dotaciones:
            print(f"  camisetapolo: {dotacion['camisetapolo']} - {dotacion['estado_camiseta_polo']}")
    else:
        print("  ✅ NO HAY SALIDAS EN DOTACIONES")
    
    # 3. Verificar cambios_dotacion (salidas)
    print("\n3. CAMBIOS_DOTACION (SALIDAS):")
    cursor.execute("""
        SELECT camisetapolo, estado_camiseta_polo
        FROM cambios_dotacion 
        WHERE camisetapolo > 0
        LIMIT 10
    """)
    
    cambios = cursor.fetchall()
    if cambios:
        for cambio in cambios:
            print(f"  camisetapolo: {cambio['camisetapolo']} - {cambio['estado_camiseta_polo']}")
    else:
        print("  ✅ NO HAY SALIDAS EN CAMBIOS_DOTACION")
    
    # 4. Calcular stock manualmente
    print("\n4. CÁLCULO MANUAL DE STOCK:")
    
    # Ingresos por estado
    cursor.execute("""
        SELECT estado, SUM(cantidad) as total
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'camisetapolo'
        GROUP BY estado
    """)
    
    ingresos_por_estado = {row['estado']: row['total'] for row in cursor.fetchall()}
    print(f"  Ingresos: {ingresos_por_estado}")
    
    # Salidas dotaciones por estado
    cursor.execute("""
        SELECT estado_camiseta_polo as estado, SUM(camisetapolo) as total
        FROM dotaciones 
        WHERE camisetapolo > 0
        GROUP BY estado_camiseta_polo
    """)
    
    salidas_dotaciones_por_estado = {row['estado']: row['total'] for row in cursor.fetchall()}
    print(f"  Salidas dotaciones: {salidas_dotaciones_por_estado}")
    
    # Salidas cambios por estado
    cursor.execute("""
        SELECT estado_camiseta_polo as estado, SUM(camisetapolo) as total
        FROM cambios_dotacion 
        WHERE camisetapolo > 0
        GROUP BY estado_camiseta_polo
    """)
    
    salidas_cambios_por_estado = {row['estado']: row['total'] for row in cursor.fetchall()}
    print(f"  Salidas cambios: {salidas_cambios_por_estado}")
    
    # Calcular disponible
    for estado in ['VALORADO', 'NO VALORADO']:
        ingresos = ingresos_por_estado.get(estado, 0)
        salidas_dot = salidas_dotaciones_por_estado.get(estado, 0)
        salidas_cam = salidas_cambios_por_estado.get(estado, 0)
        disponible = ingresos - salidas_dot - salidas_cam
        
        print(f"  {estado}: {ingresos} - {salidas_dot} - {salidas_cam} = {disponible}")
    
    # 5. Probar el método _calcular_stock_por_estado directamente
    print("\n5. MÉTODO _calcular_stock_por_estado:")
    
    for elemento in ['camisetapolo', 'camiseta_polo']:
        for estado in ['VALORADO', 'NO VALORADO']:
            try:
                stock = validador._calcular_stock_por_estado(cursor, elemento, estado)
                print(f"  {elemento} {estado}: {stock}")
            except Exception as e:
                print(f"  {elemento} {estado}: ERROR - {e}")
    
    cursor.close()
    validador.cerrar_conexion()

if __name__ == "__main__":
    debug_camisetapolo_db()