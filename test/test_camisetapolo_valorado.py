#!/usr/bin/env python3
"""
Script para probar exactamente el escenario del error:
VALORADO : ✅ asi la envio y asi sale el error
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from validacion_stock_por_estado import ValidadorStockPorEstado

def test_camisetapolo_valorado():
    """Probar el escenario exacto del error"""
    print("🧪 TEST: Camiseta Polo VALORADO")
    print("=" * 50)
    
    # Crear validador
    validador = ValidadorStockPorEstado()
    
    if not validador.conexion:
        print("❌ No se pudo conectar a la base de datos")
        return
    
    # Escenario 1: Como viene del frontend (camiseta_polo)
    print("\n1. TEST CON 'camiseta_polo' (frontend):")
    items_dict = {'camiseta_polo': 1}
    estados_dict = {'camiseta_polo': 'VALORADO'}
    
    es_valido, mensaje, stock_actual = validador.validar_stock_por_estado(
        items_dict, estados_dict
    )
    
    print(f"   Items: {items_dict}")
    print(f"   Estados: {estados_dict}")
    print(f"   Resultado: {es_valido}")
    print(f"   Mensaje: {mensaje}")
    print(f"   Stock actual: {stock_actual}")
    
    # Escenario 2: Con el nombre de BD (camisetapolo)
    print("\n2. TEST CON 'camisetapolo' (base de datos):")
    items_dict = {'camisetapolo': 1}
    estados_dict = {'camisetapolo': 'VALORADO'}
    
    es_valido, mensaje, stock_actual = validador.validar_stock_por_estado(
        items_dict, estados_dict
    )
    
    print(f"   Items: {items_dict}")
    print(f"   Estados: {estados_dict}")
    print(f"   Resultado: {es_valido}")
    print(f"   Mensaje: {mensaje}")
    print(f"   Stock actual: {stock_actual}")
    
    # Escenario 3: Probar con cantidad mayor
    print("\n3. TEST CON CANTIDAD MAYOR (121 unidades):")
    items_dict = {'camisetapolo': 121}
    estados_dict = {'camisetapolo': 'VALORADO'}
    
    es_valido, mensaje, stock_actual = validador.validar_stock_por_estado(
        items_dict, estados_dict
    )
    
    print(f"   Items: {items_dict}")
    print(f"   Estados: {estados_dict}")
    print(f"   Resultado: {es_valido}")
    print(f"   Mensaje: {mensaje}")
    print(f"   Stock actual: {stock_actual}")
    
    # Escenario 4: Probar con NO VALORADO
    print("\n4. TEST CON 'NO VALORADO':")
    items_dict = {'camisetapolo': 1}
    estados_dict = {'camisetapolo': 'NO VALORADO'}
    
    es_valido, mensaje, stock_actual = validador.validar_stock_por_estado(
        items_dict, estados_dict
    )
    
    print(f"   Items: {items_dict}")
    print(f"   Estados: {estados_dict}")
    print(f"   Resultado: {es_valido}")
    print(f"   Mensaje: {mensaje}")
    print(f"   Stock actual: {stock_actual}")
    
    # Verificar mapeo de nombres
    print("\n5. VERIFICACIÓN DE MAPEO DE NOMBRES:")
    
    # Revisar si el validador tiene mapeo interno
    cursor = validador.conexion.cursor(dictionary=True)
    
    # Verificar si existe camiseta_polo en alguna tabla
    cursor.execute("SHOW TABLES")
    tablas = cursor.fetchall()
    
    for tabla in tablas:
        tabla_nombre = list(tabla.values())[0]
        try:
            cursor.execute(f"SHOW COLUMNS FROM {tabla_nombre} LIKE '%camiseta%'")
            columnas = cursor.fetchall()
            if columnas:
                print(f"   Tabla {tabla_nombre}: {[col['Field'] for col in columnas]}")
        except:
            pass
    
    cursor.close()
    validador.cerrar_conexion()

if __name__ == "__main__":
    test_camisetapolo_valorado()