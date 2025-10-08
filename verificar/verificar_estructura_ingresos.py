#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla ingresos_dotaciones
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import get_db_connection

def verificar_estructura_ingresos():
    """Verificar la estructura de la tabla ingresos_dotaciones"""
    print("🔍 VERIFICACIÓN DE ESTRUCTURA: ingresos_dotaciones")
    print("=" * 60)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Mostrar estructura de la tabla
    print("\n1. ESTRUCTURA DE LA TABLA:")
    cursor.execute("DESCRIBE ingresos_dotaciones")
    columnas = cursor.fetchall()
    
    for columna in columnas:
        print(f"   {columna['Field']} - {columna['Type']} - {columna['Null']} - {columna['Key']} - {columna['Default']}")
    
    # 2. Buscar columnas relacionadas con estado
    print("\n2. COLUMNAS RELACIONADAS CON ESTADO:")
    columnas_estado = [col['Field'] for col in columnas if 'estado' in col['Field'].lower()]
    
    if columnas_estado:
        for col in columnas_estado:
            print(f"   ✅ {col}")
    else:
        print("   ❌ No se encontraron columnas de estado")
    
    # 3. Buscar columnas relacionadas con camiseta polo
    print("\n3. COLUMNAS RELACIONADAS CON CAMISETA POLO:")
    columnas_camiseta = [col['Field'] for col in columnas if 'camiseta' in col['Field'].lower()]
    
    if columnas_camiseta:
        for col in columnas_camiseta:
            print(f"   ✅ {col}")
    else:
        print("   ❌ No se encontraron columnas de camiseta")
    
    # 4. Mostrar algunos registros de ejemplo
    print("\n4. REGISTROS DE EJEMPLO:")
    cursor.execute("SELECT * FROM ingresos_dotaciones LIMIT 3")
    
    registros = cursor.fetchall()
    
    if registros:
        for i, registro in enumerate(registros, 1):
            print(f"\n   Registro {i}:")
            for campo, valor in registro.items():
                if valor is not None and valor != 0:
                    print(f"     {campo}: {valor}")
    else:
        print("   ❌ No se encontraron registros")
    
    # 5. Verificar si existe la columna estado_camiseta_polo
    print("\n5. VERIFICACIÓN ESPECÍFICA:")
    
    columnas_nombres = [col['Field'] for col in columnas]
    
    if 'estado_camiseta_polo' in columnas_nombres:
        print("   ✅ La columna 'estado_camiseta_polo' SÍ existe")
    else:
        print("   ❌ La columna 'estado_camiseta_polo' NO existe")
        
        # Buscar columnas similares
        posibles = [col for col in columnas_nombres if 'estado' in col.lower() and 'camiseta' in col.lower()]
        if posibles:
            print("   🔍 Columnas similares encontradas:")
            for col in posibles:
                print(f"     - {col}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    verificar_estructura_ingresos()