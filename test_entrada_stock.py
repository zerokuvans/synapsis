#!/usr/bin/env python3
import requests
import json
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT'))
}

def verificar_stock_antes():
    """Verificar stock antes de la prueba"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        print("=== STOCK ANTES DE LA PRUEBA ===")
        cursor.execute("SELECT material_tipo, cantidad_disponible FROM stock_ferretero WHERE material_tipo = 'silicona'")
        stock = cursor.fetchone()
        
        if stock:
            print(f"Silicona: {stock['cantidad_disponible']} unidades")
            return stock['cantidad_disponible']
        else:
            print("Silicona: No existe registro")
            return 0
            
        connection.close()
        
    except Error as e:
        print(f"❌ Error: {e}")
        return 0

def simular_entrada_directa():
    """Simular entrada directa en la base de datos"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        print("\n=== SIMULANDO ENTRADA DIRECTA ===")
        
        # Datos de prueba
        material_tipo = 'silicona'
        cantidad = 100
        precio_unitario = 5.50
        precio_total = cantidad * precio_unitario
        
        # Insertar entrada
        cursor.execute("""
            INSERT INTO entradas_ferretero (
                material_tipo, cantidad_entrada, precio_unitario, precio_total,
                proveedor, numero_factura, observaciones, fecha_entrada, usuario_registro
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
        """, (
            material_tipo,
            cantidad,
            precio_unitario,
            precio_total,
            'Proveedor Test',
            'FACT-001',
            'Entrada de prueba automática',
            1  # Usuario ID de prueba
        ))
        
        # Obtener el ID de la entrada recién insertada
        entrada_id = cursor.lastrowid
        print(f"✓ Entrada registrada con ID: {entrada_id}")
        
        # Actualizar stock manualmente (simulando el endpoint modificado)
        cursor.execute("""
            INSERT INTO stock_ferretero (material_tipo, cantidad_disponible, cantidad_minima)
            VALUES (%s, %s, 10)
            ON DUPLICATE KEY UPDATE 
            cantidad_disponible = cantidad_disponible + VALUES(cantidad_disponible)
        """, (material_tipo, cantidad))
        
        print(f"✓ Stock actualizado: +{cantidad} unidades")
        
        # Registrar movimiento de stock
        cursor.execute("""
            INSERT INTO movimientos_stock_ferretero (
                material_tipo, tipo_movimiento, cantidad, fecha_movimiento,
                referencia_id, referencia_tipo, observaciones
            ) VALUES (%s, 'entrada', %s, NOW(), %s, 'entrada_ferretero', %s)
        """, (
            material_tipo,
            cantidad,
            entrada_id,
            f"Entrada de {cantidad} unidades - Entrada de prueba automática"
        ))
        
        print(f"✓ Movimiento registrado")
        
        connection.commit()
        connection.close()
        
        return entrada_id
        
    except Error as e:
        print(f"❌ Error: {e}")
        if connection:
            connection.rollback()
        return None

def verificar_stock_despues():
    """Verificar stock después de la prueba"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        print("\n=== STOCK DESPUÉS DE LA PRUEBA ===")
        cursor.execute("SELECT material_tipo, cantidad_disponible FROM stock_ferretero WHERE material_tipo = 'silicona'")
        stock = cursor.fetchone()
        
        if stock:
            print(f"Silicona: {stock['cantidad_disponible']} unidades")
            stock_actual = stock['cantidad_disponible']
        else:
            print("Silicona: No existe registro")
            stock_actual = 0
            
        # Verificar movimientos
        print("\n=== MOVIMIENTOS REGISTRADOS ===")
        cursor.execute("""
            SELECT tipo_movimiento, cantidad, fecha_movimiento, observaciones 
            FROM movimientos_stock_ferretero 
            WHERE material_tipo = 'silicona' 
            ORDER BY fecha_movimiento DESC 
            LIMIT 3
        """)
        movimientos = cursor.fetchall()
        
        if movimientos:
            for mov in movimientos:
                print(f"  {mov['tipo_movimiento']}: {mov['cantidad']} - {mov['observaciones']} ({mov['fecha_movimiento']})")
        else:
            print("  No hay movimientos registrados")
            
        connection.close()
        return stock_actual
        
    except Error as e:
        print(f"❌ Error: {e}")
        return 0

if __name__ == "__main__":
    print("🧪 PRUEBA DE FUNCIONALIDAD DE STOCK")
    print("=" * 50)
    
    # Verificar stock inicial
    stock_inicial = verificar_stock_antes()
    
    # Simular entrada
    entrada_id = simular_entrada_directa()
    
    if entrada_id:
        # Verificar stock final
        stock_final = verificar_stock_despues()
        
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE LA PRUEBA")
        print(f"Stock inicial: {stock_inicial} unidades")
        print(f"Stock final: {stock_final} unidades")
        print(f"Diferencia: {stock_final - stock_inicial} unidades")
        
        if stock_final > stock_inicial:
            print("✅ PRUEBA EXITOSA: El stock se actualizó correctamente")
        else:
            print("❌ PRUEBA FALLIDA: El stock no se actualizó")
    else:
        print("❌ PRUEBA FALLIDA: No se pudo registrar la entrada")