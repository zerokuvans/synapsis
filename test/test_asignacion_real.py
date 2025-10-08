#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba de asignación real de dotación con estado
Verifica que el problema reportado por el usuario esté resuelto
"""

import requests
import json
from validacion_stock_por_estado import ValidadorStockPorEstado
import mysql.connector
from decimal import Decimal

def obtener_conexion_db():
    """Obtener conexión a la base de datos"""
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            database='synapsis',
            user='root',
            password='Manzana123*',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return conexion
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def verificar_stock_antes_y_despues():
    """Verificar stock antes y después de una asignación"""
    print("=== PRUEBA DE ASIGNACIÓN REAL ===\n")
    
    # 1. Verificar stock inicial
    validador = ValidadorStockPorEstado()
    if not validador.conexion:
        print("❌ No se pudo conectar a la base de datos")
        return
    
    print("1. Stock inicial de botas:")
    stock_inicial = validador.obtener_stock_detallado_por_estado('botas')
    for estado, cantidad in stock_inicial.items():
        print(f"   {estado}: {cantidad}")
    
    # 2. Preparar datos para asignación de botas NO VALORADAS
    datos_asignacion = {
        "cliente": "PRUEBA_BOTAS_NO_VALORADAS",
        "id_codigo_consumidor": 1,
        "botas": 1,
        "botas_talla": "42",
        "estado_botas": "NO VALORADO",
        "pantalon": 0,
        "camisetagris": 0,
        "guerrera": 0,
        "camisetapolo": 0,
        "guantes_nitrilo": 0,
        "guantes_carnaza": 0,
        "gafas": 0,
        "gorra": 0,
        "casco": 0
    }
    
    print(f"\n2. Datos de asignación:")
    print(f"   Cliente: {datos_asignacion['cliente']}")
    print(f"   Botas: {datos_asignacion['botas']} (Estado: {datos_asignacion['estado_botas']})")
    
    # 3. Realizar asignación via API
    try:
        print("\n3. Realizando asignación via API...")
        response = requests.post(
            'http://localhost:8080/api/dotaciones',
            json=datos_asignacion,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            resultado = response.json()
            print(f"   ✅ Asignación exitosa: {resultado.get('message', 'Sin mensaje')}")
            dotacion_id = resultado.get('dotacion_id')
            print(f"   ID Dotación: {dotacion_id}")
        else:
            print(f"   ❌ Error en asignación: {response.text}")
            validador.cerrar_conexion()
            return
            
    except Exception as e:
        print(f"   ❌ Error realizando petición: {e}")
        validador.cerrar_conexion()
        return
    
    # 4. Verificar stock después de la asignación
    print("\n4. Stock después de la asignación:")
    stock_final = validador.obtener_stock_detallado_por_estado('botas')
    for estado, cantidad in stock_final.items():
        print(f"   {estado}: {cantidad}")
    
    # 5. Verificar cambios en stock
    print("\n5. Análisis de cambios:")
    cambio_valorado = stock_final['VALORADO'] - stock_inicial['VALORADO']
    cambio_no_valorado = stock_final['NO VALORADO'] - stock_inicial['NO VALORADO']
    
    print(f"   Stock VALORADO: {stock_inicial['VALORADO']} → {stock_final['VALORADO']} (Cambio: {cambio_valorado})")
    print(f"   Stock NO VALORADO: {stock_inicial['NO VALORADO']} → {stock_final['NO VALORADO']} (Cambio: {cambio_no_valorado})")
    
    # 6. Verificar en base de datos cómo se guardó la dotación
    print("\n6. Verificando registro en base de datos...")
    conexion = obtener_conexion_db()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT cliente, botas, estado_botas, created_at
                FROM dotaciones 
                WHERE id_codigo_consumidor = %s
                ORDER BY created_at DESC 
                LIMIT 1
            """, (77777777,))
            
            dotacion = cursor.fetchone()
            if dotacion:
                print(f"   Cliente: {dotacion['cliente']}")
                print(f"   Botas asignadas: {dotacion['botas']}")
                print(f"   Estado guardado: {dotacion['estado_botas']}")
                print(f"   Fecha: {dotacion['created_at']}")
            else:
                print("   ❌ No se encontró la dotación en la base de datos")
                
            cursor.close()
            conexion.close()
            
        except Exception as e:
            print(f"   ❌ Error consultando base de datos: {e}")
    
    # 7. Evaluación final
    print("\n7. Evaluación del problema reportado:")
    
    if cambio_valorado == 0 and cambio_no_valorado == -1:
        print("   ✅ CORRECTO: Se descontó del stock NO VALORADO como se esperaba")
        print("   ✅ CORRECTO: No se afectó el stock VALORADO")
        resultado_final = "PROBLEMA RESUELTO"
    elif cambio_valorado == -1 and cambio_no_valorado == 0:
        print("   ❌ PROBLEMA PERSISTE: Se descontó del stock VALORADO incorrectamente")
        print("   ❌ PROBLEMA PERSISTE: No se descontó del stock NO VALORADO")
        resultado_final = "PROBLEMA NO RESUELTO"
    else:
        print(f"   ⚠️  COMPORTAMIENTO INESPERADO: Cambios no esperados en stock")
        resultado_final = "COMPORTAMIENTO INESPERADO"
    
    print(f"\n=== RESULTADO FINAL: {resultado_final} ===")
    
    validador.cerrar_conexion()
    return resultado_final

if __name__ == "__main__":
    try:
        resultado = verificar_stock_antes_y_despues()
        print(f"\nPrueba completada: {resultado}")
    except Exception as e:
        print(f"Error en la prueba: {e}")
        import traceback
        traceback.print_exc()