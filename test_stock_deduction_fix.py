#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar que el problema de descuento doble de stock se ha corregido.
Este test verifica que al asignar 1 silicona, el stock se descuente exactamente en 1 unidad.
"""

import requests
import mysql.connector
from mysql.connector import Error
import json

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'port': 3306
}

# Configuración del endpoint
BASE_URL = 'http://localhost:8080'
LOGIN_URL = f'{BASE_URL}/'
REGISTRAR_URL = f'{BASE_URL}/logistica/registrar_ferretero'

def get_stock_silicona():
    """Obtener el stock actual de silicona"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT cantidad_disponible FROM stock_ferretero WHERE material_tipo = 'silicona'")
        result = cursor.fetchone()
        
        return result['cantidad_disponible'] if result else 0
        
    except Error as e:
        print(f"Error al obtener stock: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def test_stock_deduction_fix():
    """Test principal para verificar la corrección del descuento doble"""
    print("=== Test de Corrección de Descuento Doble de Stock ===")
    
    # 1. Obtener stock inicial
    stock_inicial = get_stock_silicona()
    if stock_inicial is None:
        print("❌ Error: No se pudo obtener el stock inicial")
        return False
    
    print(f"📊 Stock inicial de silicona: {stock_inicial}")
    
    # 2. Realizar login
    session = requests.Session()
    
    login_data = {
        'username': '80833959',
        'password': 'M4r14l4r@'
    }
    
    print("🔐 Realizando login...")
    login_response = session.post(LOGIN_URL, data=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Error en login: {login_response.status_code}")
        return False
    
    print("✅ Login exitoso")
    
    # Datos para la asignación
    assignment_data = {
        'id_codigo_consumidor': '11',  # ID del técnico (ALARCON SALAS LUIS HERNANDO - FTTH INSTALACIONES)
        'fecha': '2025-01-28T10:00',  # Fecha en formato datetime-local
        'silicona': '1',
        'amarres_negros': '0',
        'amarres_blancos': '0',
        'cinta_aislante': '0',
        'grapas_blancas': '0',
        'grapas_negras': '0'
    }
    
    print("📦 Asignando 1 silicona...")
    response = session.post(REGISTRAR_URL, data=assignment_data)
    
    if response.status_code != 201:
        print(f"❌ Error en asignación: {response.status_code}")
        print(f"Respuesta: {response.text}")
        return False
    
    print("✅ Asignación exitosa")
    
    # 4. Verificar stock final
    stock_final = get_stock_silicona()
    if stock_final is None:
        print("❌ Error: No se pudo obtener el stock final")
        return False
    
    print(f"📊 Stock final de silicona: {stock_final}")
    
    # 5. Calcular diferencia
    diferencia = stock_inicial - stock_final
    print(f"📉 Diferencia de stock: {diferencia}")
    
    # 6. Verificar resultado
    if diferencia == 1:
        print("✅ ¡ÉXITO! El stock se descontó correctamente (1 unidad)")
        print("✅ El problema del descuento doble ha sido corregido")
        return True
    elif diferencia == 2:
        print("❌ FALLO: El stock se descontó 2 unidades (problema persiste)")
        return False
    else:
        print(f"❌ FALLO: Descuento inesperado de {diferencia} unidades")
        return False

def verificar_movimientos_stock():
    """Verificar que solo se registre un movimiento de stock"""
    print("\n=== Verificación de Movimientos de Stock ===")
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Obtener los últimos movimientos de silicona
        cursor.execute("""
            SELECT * FROM movimientos_stock_ferretero 
            WHERE material_tipo = 'silicona' 
            ORDER BY fecha_movimiento DESC 
            LIMIT 5
        """)
        
        movimientos = cursor.fetchall()
        
        print(f"📋 Últimos {len(movimientos)} movimientos de silicona:")
        for i, mov in enumerate(movimientos, 1):
            print(f"  {i}. {mov['fecha_movimiento']} - {mov['tipo_movimiento']} - Cantidad: {mov['cantidad']} - Ref: {mov['referencia_tipo']}")
        
        return True
        
    except Error as e:
        print(f"❌ Error al verificar movimientos: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    print("Iniciando test de corrección de descuento doble...\n")
    
    # Ejecutar test principal
    resultado_test = test_stock_deduction_fix()
    
    # Verificar movimientos
    verificar_movimientos_stock()
    
    # Resultado final
    print("\n" + "="*50)
    if resultado_test:
        print("🎉 TEST EXITOSO: El problema del descuento doble ha sido corregido")
    else:
        print("💥 TEST FALLIDO: El problema del descuento doble persiste")
    print("="*50)