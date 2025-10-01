#!/usr/bin/env python3
"""
Script para verificar el stock real de camisetapolo
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import get_db_connection

def verificar_stock_camisetapolo():
    """Verificar el stock real de camisetapolo"""
    print("🔍 VERIFICACIÓN DE STOCK: camisetapolo")
    print("=" * 60)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Stock en ingresos_dotaciones
    print("\n1. STOCK EN INGRESOS_DOTACIONES:")
    cursor.execute("""
        SELECT 
            tipo_elemento,
            estado,
            SUM(cantidad) as total_cantidad
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'camisetapolo'
        GROUP BY tipo_elemento, estado
        ORDER BY estado
    """)
    
    ingresos = cursor.fetchall()
    
    if ingresos:
        for ingreso in ingresos:
            print(f"   {ingreso['tipo_elemento']} - {ingreso['estado']}: {ingreso['total_cantidad']} unidades")
    else:
        print("   ❌ No se encontró stock de camisetapolo en ingresos")
    
    # 2. Salidas en dotaciones
    print("\n2. SALIDAS EN DOTACIONES:")
    cursor.execute("""
        SELECT 
            SUM(camisetapolo) as total_salidas
        FROM dotaciones 
        WHERE camisetapolo > 0
    """)
    
    result = cursor.fetchone()
    salidas_dotaciones = result['total_salidas'] if result['total_salidas'] else 0
    print(f"   Total salidas en dotaciones: {salidas_dotaciones}")
    
    # 3. Salidas en cambios_dotacion
    print("\n3. SALIDAS EN CAMBIOS_DOTACION:")
    cursor.execute("""
        SELECT 
            SUM(camisetapolo) as total_cambios
        FROM cambios_dotacion 
        WHERE camisetapolo > 0
    """)
    
    result = cursor.fetchone()
    salidas_cambios = result['total_cambios'] if result['total_cambios'] else 0
    print(f"   Total salidas en cambios: {salidas_cambios}")
    
    # 4. Cálculo manual del stock
    print("\n4. CÁLCULO MANUAL DEL STOCK:")
    
    total_ingresos = sum(ingreso['total_cantidad'] for ingreso in ingresos)
    total_salidas = salidas_dotaciones + salidas_cambios
    stock_disponible = total_ingresos - total_salidas
    
    print(f"   Total ingresos: {total_ingresos}")
    print(f"   Total salidas: {total_salidas}")
    print(f"   Stock disponible: {stock_disponible}")
    
    # 5. Stock por estado
    print("\n5. STOCK DISPONIBLE POR ESTADO:")
    
    for ingreso in ingresos:
        estado = ingreso['estado']
        cantidad_ingreso = ingreso['total_cantidad']
        
        # Para simplificar, asumimos que las salidas se distribuyen proporcionalmente
        # En un sistema real, necesitarías rastrear el estado de cada salida
        if total_ingresos > 0:
            proporcion = cantidad_ingreso / total_ingresos
            salidas_estado = int(total_salidas * proporcion)
            stock_estado = cantidad_ingreso - salidas_estado
        else:
            stock_estado = 0
        
        print(f"   {estado}: {stock_estado} unidades disponibles")
    
    # 6. Verificar con el validador del sistema
    print("\n6. VERIFICACIÓN CON VALIDADOR DEL SISTEMA:")
    
    try:
        from validacion_stock_por_estado import ValidacionStockPorEstado
        validador = ValidacionStockPorEstado()
        
        # Probar con camiseta_polo (frontend)
        items_dict = {'camiseta_polo': 1}
        estados_dict = {'camiseta_polo': 'VALORADO'}
        
        es_valido, mensaje = validador.validar_asignacion_con_estados(
            1, items_dict, estados_dict
        )
        
        print(f"   Validación 'camiseta_polo' VALORADO:")
        print(f"     Resultado: {es_valido}")
        print(f"     Mensaje: {mensaje}")
        
        # Probar con NO VALORADO
        estados_dict = {'camiseta_polo': 'NO VALORADO'}
        
        es_valido, mensaje = validador.validar_asignacion_con_estados(
            1, items_dict, estados_dict
        )
        
        print(f"   Validación 'camiseta_polo' NO VALORADO:")
        print(f"     Resultado: {es_valido}")
        print(f"     Mensaje: {mensaje}")
        
        validador.cerrar_conexion()
        
    except Exception as e:
        print(f"   ❌ Error al usar el validador: {e}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    verificar_stock_camisetapolo()