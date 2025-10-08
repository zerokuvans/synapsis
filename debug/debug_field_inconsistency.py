#!/usr/bin/env python3
"""
Script para identificar la inconsistencia entre nombres de campos
en ingresos_dotaciones vs consultas de dotaciones
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import get_db_connection

def verificar_inconsistencia_campos():
    """Verificar la inconsistencia entre nombres de campos"""
    print("🔍 VERIFICACIÓN DE INCONSISTENCIA DE CAMPOS")
    print("=" * 60)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Verificar qué se guarda en ingresos_dotaciones para camiseta polo
    print("\n1. REGISTROS EN ingresos_dotaciones PARA CAMISETA POLO:")
    cursor.execute("""
        SELECT tipo_elemento, COUNT(*) as cantidad_registros, SUM(cantidad) as total_cantidad
        FROM ingresos_dotaciones 
        WHERE tipo_elemento IN ('camisetapolo', 'camiseta_polo')
        GROUP BY tipo_elemento
    """)
    
    registros_ingresos = cursor.fetchall()
    for reg in registros_ingresos:
        print(f"   ✅ {reg['tipo_elemento']}: {reg['cantidad_registros']} registros, {reg['total_cantidad']} unidades")
    
    if not registros_ingresos:
        print("   ❌ No se encontraron registros de camiseta polo")
    
    # 2. Verificar cómo se consulta en el API
    print("\n2. CONSULTA ACTUAL EN API (obtener_stock_por_estado):")
    print("   📝 La API busca en ingresos_dotaciones con tipo_elemento = 'camisetapolo'")
    print("   📝 Pero también podría buscar con 'camiseta_polo'")
    
    # 3. Probar ambas consultas
    print("\n3. PRUEBA DE CONSULTAS:")
    
    for nombre_campo in ['camisetapolo', 'camiseta_polo']:
        print(f"\n   🔍 Consultando con '{nombre_campo}':")
        
        for estado in ['VALORADO', 'NO VALORADO']:
            cursor.execute("""
                SELECT COALESCE(SUM(cantidad), 0) as total
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = %s AND estado = %s
            """, (nombre_campo, estado))
            
            resultado = cursor.fetchone()
            total = resultado['total'] if resultado else 0
            print(f"      {estado}: {total} unidades")
    
    # 4. Verificar estructura de tabla dotaciones
    print("\n4. ESTRUCTURA DE TABLA dotaciones (campos de camiseta polo):")
    cursor.execute("DESCRIBE dotaciones")
    columnas = cursor.fetchall()
    
    campos_camiseta = [col['Field'] for col in columnas if 'camiseta' in col['Field'].lower()]
    for campo in campos_camiseta:
        print(f"   ✅ {campo}")
    
    # 5. Verificar estructura de tabla cambios_dotacion
    print("\n5. ESTRUCTURA DE TABLA cambios_dotacion (campos de camiseta polo):")
    cursor.execute("DESCRIBE cambios_dotacion")
    columnas = cursor.fetchall()
    
    campos_camiseta = [col['Field'] for col in columnas if 'camiseta' in col['Field'].lower()]
    for campo in campos_camiseta:
        print(f"   ✅ {campo}")
    
    # 6. Mostrar el problema específico
    print("\n6. PROBLEMA IDENTIFICADO:")
    print("   ❌ En ingresos_dotaciones se guarda como 'camisetapolo'")
    print("   ❌ En dotaciones/cambios_dotacion el campo es 'camisetapolo'")
    print("   ❌ Pero el campo de estado es 'estado_camiseta_polo' (con guión bajo)")
    print("   ❌ Esto puede causar confusión en las consultas")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    verificar_inconsistencia_campos()