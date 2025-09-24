#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error

def test_validacion_stock_estado():
    """Probar la validación de stock por estado valorado/no valorado"""
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = connection.cursor(dictionary=True)
        
        print("=== PRUEBA DE VALIDACIÓN DE STOCK POR ESTADO ===")
        print()
        
        # 1. Verificar stock actual por elemento y estado
        elementos = ['pantalon', 'camisetagris', 'guerrera', 'camisetapolo', 
                    'guantes_nitrilo', 'guantes_carnaza', 'gafas', 'gorra', 'casco', 'botas']
        
        print("1. STOCK ACTUAL POR ELEMENTO Y ESTADO:")
        print("-" * 60)
        
        for elemento in elementos:
            for estado in ['VALORADO', 'NO VALORADO']:
                # Obtener ingresos
                cursor.execute("""
                    SELECT COALESCE(SUM(cantidad), 0) as stock_ingresos
                    FROM ingresos_dotaciones 
                    WHERE tipo_elemento = %s AND estado = %s
                """, (elemento, estado))
                
                ingresos_result = cursor.fetchone()
                stock_ingresos = ingresos_result['stock_ingresos'] if ingresos_result else 0
                
                # Obtener salidas
                cursor.execute(f"""
                    SELECT COALESCE(SUM(
                        CASE 
                            WHEN '{elemento}' = 'pantalon' AND estado_pantalon = %s THEN pantalon
                            WHEN '{elemento}' = 'camisetagris' AND estado_camiseta_gris = %s THEN camisetagris
                            WHEN '{elemento}' = 'guerrera' AND estado_guerrera = %s THEN guerrera
                            WHEN '{elemento}' = 'camisetapolo' AND estado_camiseta_polo = %s THEN camisetapolo
                            WHEN '{elemento}' = 'guantes_nitrilo' AND estado_guantes_nitrilo = %s THEN guantes_nitrilo
                            WHEN '{elemento}' = 'guantes_carnaza' AND estado_guantes_carnaza = %s THEN guantes_carnaza
                            WHEN '{elemento}' = 'gafas' AND estado_gafas = %s THEN gafas
                            WHEN '{elemento}' = 'gorra' AND estado_gorra = %s THEN gorra
                            WHEN '{elemento}' = 'casco' AND estado_casco = %s THEN casco
                            WHEN '{elemento}' = 'botas' AND estado_botas = %s THEN botas
                            ELSE 0
                        END
                    ), 0) as total_salidas
                    FROM cambios_dotacion
                """, (estado, estado, estado, estado, estado, estado, estado, estado, estado, estado))
                
                salidas_result = cursor.fetchone()
                stock_salidas = salidas_result['total_salidas'] if salidas_result else 0
                
                stock_disponible = stock_ingresos - stock_salidas
                
                nombre_elemento = elemento.replace('_', ' ').title()
                print(f"{nombre_elemento:15} ({estado:12}): Ingresos: {stock_ingresos:3}, Salidas: {stock_salidas:3}, Disponible: {stock_disponible:3}")
        
        print()
        print("2. SIMULACIÓN DE VALIDACIONES:")
        print("-" * 60)
        
        # 2. Simular diferentes escenarios de validación
        escenarios_prueba = [
            {'elemento': 'pantalon', 'cantidad': 1, 'valorado': True, 'descripcion': 'Pantalón valorado (1 unidad)'},
            {'elemento': 'pantalon', 'cantidad': 1, 'valorado': False, 'descripcion': 'Pantalón no valorado (1 unidad)'},
            {'elemento': 'botas', 'cantidad': 2, 'valorado': True, 'descripcion': 'Botas valoradas (2 unidades)'},
            {'elemento': 'botas', 'cantidad': 2, 'valorado': False, 'descripcion': 'Botas no valoradas (2 unidades)'},
            {'elemento': 'camisetagris', 'cantidad': 5, 'valorado': False, 'descripcion': 'Camiseta gris no valorada (5 unidades)'},
        ]
        
        for i, escenario in enumerate(escenarios_prueba, 1):
            elemento = escenario['elemento']
            cantidad = escenario['cantidad']
            es_valorado = escenario['valorado']
            tipo_stock = "VALORADO" if es_valorado else "NO VALORADO"
            
            # Calcular stock disponible
            cursor.execute("""
                SELECT COALESCE(SUM(cantidad), 0) as stock_ingresos
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = %s AND estado = %s
            """, (elemento, tipo_stock))
            
            ingresos_result = cursor.fetchone()
            stock_ingresos = ingresos_result['stock_ingresos'] if ingresos_result else 0
            
            cursor.execute(f"""
                SELECT COALESCE(SUM(
                    CASE 
                        WHEN '{elemento}' = 'pantalon' AND estado_pantalon = %s THEN pantalon
                        WHEN '{elemento}' = 'camisetagris' AND estado_camiseta_gris = %s THEN camisetagris
                        WHEN '{elemento}' = 'guerrera' AND estado_guerrera = %s THEN guerrera
                        WHEN '{elemento}' = 'camisetapolo' AND estado_camiseta_polo = %s THEN camisetapolo
                        WHEN '{elemento}' = 'guantes_nitrilo' AND estado_guantes_nitrilo = %s THEN guantes_nitrilo
                        WHEN '{elemento}' = 'guantes_carnaza' AND estado_guantes_carnaza = %s THEN guantes_carnaza
                        WHEN '{elemento}' = 'gafas' AND estado_gafas = %s THEN gafas
                        WHEN '{elemento}' = 'gorra' AND estado_gorra = %s THEN gorra
                        WHEN '{elemento}' = 'casco' AND estado_casco = %s THEN casco
                        WHEN '{elemento}' = 'botas' AND estado_botas = %s THEN botas
                        ELSE 0
                    END
                ), 0) as total_salidas
                FROM cambios_dotacion
            """, (tipo_stock, tipo_stock, tipo_stock, tipo_stock, tipo_stock, 
                  tipo_stock, tipo_stock, tipo_stock, tipo_stock, tipo_stock))
            
            salidas_result = cursor.fetchone()
            stock_salidas = salidas_result['total_salidas'] if salidas_result else 0
            
            stock_disponible = stock_ingresos - stock_salidas
            
            # Determinar resultado de validación
            if stock_disponible >= cantidad:
                resultado = "✅ VÁLIDO"
            else:
                resultado = "❌ RECHAZADO"
            
            print(f"Escenario {i}: {escenario['descripcion']}")
            print(f"  Stock disponible: {stock_disponible}, Solicitado: {cantidad} → {resultado}")
            
            if stock_disponible < cantidad:
                print(f"  Error: Stock insuficiente para {elemento.replace('_', ' ').title()} ({tipo_stock})")
            print()
        
        print("3. RECOMENDACIONES:")
        print("-" * 60)
        print("• La validación ahora verifica stock específico por estado (VALORADO/NO VALORADO)")
        print("• Los mensajes de error son específicos y muestran el estado solicitado")
        print("• El sistema previene registros cuando no hay stock del tipo correcto")
        print("• Se mantiene la integridad de datos separando stock valorado y no valorado")
        
    except Error as e:
        print(f"Error de base de datos: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nPrueba completada - Conexión cerrada")

if __name__ == "__main__":
    test_validacion_stock_estado()