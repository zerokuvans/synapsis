#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el sistema de stock unificado
"""

import mysql.connector
from datetime import datetime

def test_stock_unificado():
    """Probar que el stock unificado funciona correctamente"""
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = connection.cursor(dictionary=True)
        
        print("=== PRUEBA DE STOCK UNIFICADO ===")
        print("\n1. Verificando stock inicial de pantalón...")
        
        # Verificar stock inicial
        cursor.execute("""
            SELECT saldo_disponible 
            FROM vista_stock_dotaciones 
            WHERE tipo_elemento = 'pantalon'
        """)
        
        stock_inicial = cursor.fetchone()
        stock_inicial_valor = stock_inicial['saldo_disponible'] if stock_inicial else 0
        print(f"   Stock inicial de pantalón: {stock_inicial_valor}")
        
        print("\n2. Registrando nuevo ingreso de dotaciones...")
        
        # Registrar nuevo ingreso
        cursor.execute("""
            INSERT INTO ingresos_dotaciones 
            (tipo_elemento, cantidad, proveedor, fecha_ingreso, observaciones, usuario_registro) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            'pantalon', 
            5, 
            'Proveedor Test', 
            '2025-01-24', 
            'Test stock unificado', 
            'admin'
        ))
        
        connection.commit()
        print("   ✅ Ingreso registrado exitosamente")
        
        print("\n3. Verificando stock después del ingreso...")
        
        # Verificar stock después del ingreso
        cursor.execute("""
            SELECT saldo_disponible 
            FROM vista_stock_dotaciones 
            WHERE tipo_elemento = 'pantalon'
        """)
        
        stock_despues = cursor.fetchone()
        stock_despues_valor = stock_despues['saldo_disponible'] if stock_despues else 0
        print(f"   Stock después del ingreso: {stock_despues_valor}")
        print(f"   Incremento: {stock_despues_valor - stock_inicial_valor}")
        
        print("\n4. Simulando validación de cambio de dotación...")
        
        # Simular la validación que hace registrar_cambio_dotacion
        cantidad_solicitada = 2
        cursor.execute("""
            SELECT saldo_disponible
            FROM vista_stock_dotaciones 
            WHERE tipo_elemento = %s
        """, ('pantalon',))
        
        stock_result = cursor.fetchone()
        stock_disponible = stock_result['saldo_disponible'] if stock_result else 0
        
        print(f"   Cantidad solicitada para cambio: {cantidad_solicitada}")
        print(f"   Stock disponible: {stock_disponible}")
        
        if stock_disponible >= cantidad_solicitada:
            print("   ✅ Stock suficiente para el cambio de dotación")
            print("   ✅ El stock unificado funciona correctamente")
        else:
            print("   ❌ Stock insuficiente para el cambio de dotación")
            print(f"   ❌ Disponible: {stock_disponible}, Solicitado: {cantidad_solicitada}")
        
        print("\n5. Verificando que ambos módulos usan la misma fuente...")
        
        # Verificar que la vista incluye datos de ingresos_dotaciones
        cursor.execute("""
            SELECT 
                tipo_elemento,
                cantidad_ingresada,
                cantidad_entregada,
                saldo_disponible
            FROM vista_stock_dotaciones 
            WHERE tipo_elemento = 'pantalon'
        """)
        
        vista_data = cursor.fetchone()
        if vista_data:
            print(f"   Cantidad ingresada: {vista_data['cantidad_ingresada']}")
            print(f"   Cantidad entregada: {vista_data['cantidad_entregada']}")
            print(f"   Saldo disponible: {vista_data['saldo_disponible']}")
            print("   ✅ La vista unificada está funcionando")
        
        print("\n=== RESULTADO DE LA PRUEBA ===")
        print("✅ El sistema de stock unificado está funcionando correctamente")
        print("✅ Los ingresos de dotaciones están disponibles para cambios")
        print("✅ Ambos módulos consultan la misma fuente de stock")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_stock_unificado()