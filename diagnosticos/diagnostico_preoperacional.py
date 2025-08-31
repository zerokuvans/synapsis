#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para la tabla preoperacional
Verifica datos y estructura para el endpoint de estado de vehículos
"""

import sqlite3
from datetime import datetime
import json

def conectar_db():
    """Conecta a la base de datos"""
    try:
        conn = sqlite3.connect('synapsis.db')
        conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def verificar_tabla_existe(conn):
    """Verifica si la tabla preoperacional existe"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='preoperacional'
    """)
    return cursor.fetchone() is not None

def obtener_estructura_tabla(conn):
    """Obtiene la estructura de la tabla preoperacional"""
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(preoperacional)")
    return cursor.fetchall()

def contar_registros_total(conn):
    """Cuenta el total de registros en preoperacional"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM preoperacional")
    return cursor.fetchone()['total']

def contar_registros_mes_actual(conn):
    """Cuenta registros del mes actual"""
    cursor = conn.cursor()
    mes_actual = datetime.now().strftime('%Y-%m')
    cursor.execute("""
        SELECT COUNT(*) as total FROM preoperacional 
        WHERE strftime('%Y-%m', fecha) = ?
    """, (mes_actual,))
    return cursor.fetchone()['total']

def obtener_primeros_registros(conn, limite=10):
    """Obtiene los primeros registros con información de supervisor"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, fecha, supervisor, vehiculo, 
               estado_motor, estado_frenos, estado_luces,
               estado_llantas, estado_carroceria
        FROM preoperacional 
        ORDER BY fecha DESC 
        LIMIT ?
    """, (limite,))
    return cursor.fetchall()

def analizar_supervisores(conn):
    """Analiza los datos de supervisores"""
    cursor = conn.cursor()
    
    # Supervisores únicos
    cursor.execute("""
        SELECT DISTINCT supervisor, COUNT(*) as cantidad
        FROM preoperacional 
        WHERE supervisor IS NOT NULL AND supervisor != ''
        GROUP BY supervisor
        ORDER BY cantidad DESC
    """)
    supervisores = cursor.fetchall()
    
    # Registros con supervisor NULL o vacío
    cursor.execute("""
        SELECT COUNT(*) as sin_supervisor
        FROM preoperacional 
        WHERE supervisor IS NULL OR supervisor = ''
    """)
    sin_supervisor = cursor.fetchone()['sin_supervisor']
    
    return supervisores, sin_supervisor

def analizar_campos_estado(conn):
    """Analiza los campos de estado del vehículo"""
    cursor = conn.cursor()
    
    campos_estado = [
        'estado_motor', 'estado_frenos', 'estado_luces', 'estado_llantas',
        'estado_carroceria', 'estado_suspension', 'estado_direccion',
        'estado_transmision', 'estado_embrague', 'estado_bateria',
        'estado_alternador', 'estado_arranque', 'estado_radiador',
        'estado_aceite', 'estado_liquido_frenos', 'estado_refrigerante',
        'estado_combustible', 'estado_neumaticos'
    ]
    
    resultados = {}
    for campo in campos_estado:
        try:
            cursor.execute(f"""
                SELECT {campo}, COUNT(*) as cantidad
                FROM preoperacional 
                WHERE {campo} IS NOT NULL
                GROUP BY {campo}
                ORDER BY cantidad DESC
            """)
            resultados[campo] = cursor.fetchall()
        except sqlite3.OperationalError:
            resultados[campo] = "Campo no existe"
    
    return resultados

def main():
    print("=== DIAGNÓSTICO TABLA PREOPERACIONAL ===")
    print(f"Fecha de diagnóstico: {datetime.now()}")
    print()
    
    conn = conectar_db()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return
    
    try:
        # 1. Verificar si la tabla existe
        print("1. VERIFICACIÓN DE TABLA")
        print("   Verificando existencia de tabla 'preoperacional'...")
        
        # Primero listar todas las tablas
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = cursor.fetchall()
        print(f"   Tablas encontradas en la base de datos: {[t['name'] for t in tablas]}")
        
        if verificar_tabla_existe(conn):
            print("✓ La tabla 'preoperacional' existe")
        else:
            print("✗ La tabla 'preoperacional' NO existe")
            print("   Buscando tablas similares...")
            for tabla in tablas:
                if 'preop' in tabla['name'].lower() or 'operac' in tabla['name'].lower():
                    print(f"   Tabla similar encontrada: {tabla['name']}")
            return
        
        # 2. Estructura de la tabla
        print("\n2. ESTRUCTURA DE LA TABLA")
        estructura = obtener_estructura_tabla(conn)
        for col in estructura:
            print(f"  - {col['name']}: {col['type']} (NULL: {'Sí' if col['notnull'] == 0 else 'No'})")
        
        # 3. Conteo de registros
        print("\n3. CONTEO DE REGISTROS")
        total = contar_registros_total(conn)
        mes_actual = contar_registros_mes_actual(conn)
        print(f"  - Total de registros: {total}")
        print(f"  - Registros del mes actual: {mes_actual}")
        
        if total == 0:
            print("\n⚠️  NO HAY REGISTROS EN LA TABLA")
            return
        
        # 4. Primeros registros
        print("\n4. PRIMEROS 10 REGISTROS")
        registros = obtener_primeros_registros(conn)
        for i, reg in enumerate(registros, 1):
            print(f"  {i}. ID: {reg['id']}, Fecha: {reg['fecha']}, Supervisor: '{reg['supervisor']}', Vehículo: {reg['vehiculo']}")
            print(f"     Estados: Motor={reg['estado_motor']}, Frenos={reg['estado_frenos']}, Luces={reg['estado_luces']}")
        
        # 5. Análisis de supervisores
        print("\n5. ANÁLISIS DE SUPERVISORES")
        supervisores, sin_supervisor = analizar_supervisores(conn)
        print(f"  - Registros sin supervisor: {sin_supervisor}")
        print(f"  - Supervisores únicos encontrados: {len(supervisores)}")
        for sup in supervisores[:10]:  # Primeros 10
            print(f"    * '{sup['supervisor']}': {sup['cantidad']} registros")
        
        # 6. Análisis de campos de estado
        print("\n6. ANÁLISIS DE CAMPOS DE ESTADO")
        campos_estado = analizar_campos_estado(conn)
        campos_existentes = [k for k, v in campos_estado.items() if v != "Campo no existe"]
        campos_no_existentes = [k for k, v in campos_estado.items() if v == "Campo no existe"]
        
        print(f"  - Campos de estado existentes: {len(campos_existentes)}")
        print(f"  - Campos de estado NO existentes: {len(campos_no_existentes)}")
        
        if campos_no_existentes:
            print("  - Campos faltantes:")
            for campo in campos_no_existentes:
                print(f"    * {campo}")
        
        # Mostrar valores de algunos campos existentes
        for campo in campos_existentes[:5]:  # Primeros 5 campos
            valores = campos_estado[campo]
            if valores and len(valores) > 0:
                print(f"  - Valores en '{campo}':")
                for val in valores[:3]:  # Primeros 3 valores
                    print(f"    * '{val[campo]}': {val['cantidad']} veces")
        
        # 7. Diagnóstico específico para el endpoint
        print("\n7. DIAGNÓSTICO PARA ENDPOINT")
        mes_actual_str = datetime.now().strftime('%Y-%m')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM preoperacional 
            WHERE strftime('%Y-%m', fecha) = ?
            AND supervisor IS NOT NULL 
            AND supervisor != ''
        """, (mes_actual_str,))
        registros_validos = cursor.fetchone()['total']
        
        print(f"  - Registros del mes actual con supervisor válido: {registros_validos}")
        
        if registros_validos == 0:
            print("\n⚠️  PROBLEMA IDENTIFICADO:")
            print("     No hay registros del mes actual con supervisor válido")
            print("     El endpoint retornará una lista vacía")
        else:
            print("\n✓ Datos suficientes para el endpoint")
    
    except Exception as e:
        print(f"\nError durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()
        print("\n=== FIN DEL DIAGNÓSTICO ===")

if __name__ == "__main__":
    main()