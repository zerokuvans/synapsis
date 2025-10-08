#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar directamente en la base de datos que la consulta
solo cuenta registros con grupos válidos
"""

import mysql.connector
from datetime import date

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def test_consulta_grupos_validos():
    """Probar la consulta SQL modificada directamente en la base de datos"""
    
    print("=" * 70)
    print("PRUEBA DIRECTA: CONSULTA SQL - SOLO GRUPOS VÁLIDOS")
    print("=" * 70)
    
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        fecha_hoy = date.today()
        print(f"\nFecha de consulta: {fecha_hoy}")
        
        # 1. Consulta ANTES de la modificación (todos los registros)
        print("\n1. CONSULTA ORIGINAL (todos los registros):")
        query_original = """
            SELECT 
                t.grupo,
                t.nombre_tipificacion as carpeta,
                COUNT(DISTINCT a.id_codigo_consumidor) as total_tecnicos
            FROM asistencia a
            INNER JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
            WHERE DATE(a.fecha_asistencia) = %s
            GROUP BY t.grupo, t.nombre_tipificacion
            ORDER BY t.grupo, t.nombre_tipificacion
        """
        
        cursor.execute(query_original, (fecha_hoy,))
        resultados_original = cursor.fetchall()
        
        print(f"   Total de registros encontrados: {len(resultados_original)}")
        
        grupos_todos = {}
        for resultado in resultados_original:
            grupo = resultado['grupo']
            tecnicos = resultado['total_tecnicos']
            
            if grupo not in grupos_todos:
                grupos_todos[grupo] = 0
            grupos_todos[grupo] += tecnicos
        
        print("   Grupos encontrados (TODOS):")
        total_original = 0
        for grupo, tecnicos in grupos_todos.items():
            print(f"     - {grupo}: {tecnicos} técnicos")
            total_original += tecnicos
        
        print(f"   TOTAL ORIGINAL: {total_original} técnicos")
        
        # 2. Consulta DESPUÉS de la modificación (solo grupos válidos)
        print("\n2. CONSULTA MODIFICADA (solo grupos válidos):")
        query_modificada = """
            SELECT 
                t.grupo,
                t.nombre_tipificacion as carpeta,
                COUNT(DISTINCT a.id_codigo_consumidor) as total_tecnicos
            FROM asistencia a
            INNER JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
            WHERE DATE(a.fecha_asistencia) = %s
                AND t.grupo IS NOT NULL 
                AND t.grupo != ''
                AND t.grupo IN ('ARREGLOS', 'AUSENCIA INJUSTIFICADA', 'AUSENCIA JUSTIFICADA', 'INSTALACIONES', 'POSTVENTA')
            GROUP BY t.grupo, t.nombre_tipificacion
            ORDER BY t.grupo, t.nombre_tipificacion
        """
        
        cursor.execute(query_modificada, (fecha_hoy,))
        resultados_modificada = cursor.fetchall()
        
        print(f"   Total de registros encontrados: {len(resultados_modificada)}")
        
        grupos_validos = {}
        for resultado in resultados_modificada:
            grupo = resultado['grupo']
            tecnicos = resultado['total_tecnicos']
            
            if grupo not in grupos_validos:
                grupos_validos[grupo] = 0
            grupos_validos[grupo] += tecnicos
        
        print("   Grupos encontrados (SOLO VÁLIDOS):")
        total_modificado = 0
        for grupo, tecnicos in grupos_validos.items():
            print(f"     - {grupo}: {tecnicos} técnicos")
            total_modificado += tecnicos
        
        print(f"   TOTAL MODIFICADO: {total_modificado} técnicos")
        
        # 3. Análisis de diferencias
        print("\n3. ANÁLISIS DE DIFERENCIAS:")
        
        grupos_excluidos = set(grupos_todos.keys()) - set(grupos_validos.keys())
        tecnicos_excluidos = total_original - total_modificado
        
        if grupos_excluidos:
            print(f"   ✓ Grupos excluidos correctamente: {sorted(grupos_excluidos)}")
            print(f"   ✓ Técnicos excluidos: {tecnicos_excluidos}")
            
            for grupo in grupos_excluidos:
                print(f"     - {grupo}: {grupos_todos[grupo]} técnicos excluidos")
        else:
            print(f"   ℹ️  No hay grupos para excluir (todos son válidos)")
        
        # 4. Validación final
        print("\n4. VALIDACIÓN FINAL:")
        
        grupos_validos_esperados = {'ARREGLOS', 'AUSENCIA INJUSTIFICADA', 'AUSENCIA JUSTIFICADA', 'INSTALACIONES', 'POSTVENTA'}
        grupos_encontrados = set(grupos_validos.keys())
        
        grupos_invalidos = grupos_encontrados - grupos_validos_esperados
        
        if not grupos_invalidos:
            print(f"   ✅ ÉXITO: Solo se encontraron grupos válidos")
            print(f"   ✅ Grupos válidos: {sorted(grupos_encontrados)}")
        else:
            print(f"   ❌ ERROR: Se encontraron grupos inválidos: {sorted(grupos_invalidos)}")
        
        # 5. Calcular porcentajes
        print("\n5. CÁLCULO DE PORCENTAJES:")
        
        if total_modificado > 0:
            for grupo, tecnicos in grupos_validos.items():
                porcentaje = round((tecnicos * 100) / total_modificado, 2)
                print(f"   {grupo}: {tecnicos} técnicos ({porcentaje}%)")
        else:
            print("   No hay datos para calcular porcentajes")
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error general: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()
            print("\n✓ Conexión a la base de datos cerrada")

if __name__ == '__main__':
    test_consulta_grupos_validos()