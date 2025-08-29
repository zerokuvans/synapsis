#!/usr/bin/env python3
import mysql.connector
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'port': 3306
}

try:
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    
    print("🧪 PRUEBA CORRECTA DEL TRIGGER")
    print("=" * 40)
    
    # Verificar stock actual en stock_general (tabla correcta)
    cursor.execute("SELECT cantidad_disponible FROM stock_general WHERE codigo_material = 'silicona'")
    result = cursor.fetchone()
    if result:
        stock_actual = result[0]
        print(f"Stock actual de silicona: {stock_actual}")
    else:
        print("❌ Material 'silicona' no encontrado en stock_general")
        exit(1)
    
    # Insertar entrada en entradas_ferretero
    print("\nInsertando entrada en entradas_ferretero...")
    cursor.execute("""
        INSERT INTO entradas_ferretero 
        (material_tipo, cantidad_entrada, fecha_entrada, observaciones)
        VALUES 
        ('silicona', 50, CURDATE(), 'Prueba de trigger - test correcto')
    """)
    
    entrada_id = cursor.lastrowid
    print(f"✓ Entrada creada con ID: {entrada_id}")
    
    # Verificar stock después en stock_general
    cursor.execute("SELECT cantidad_disponible FROM stock_general WHERE codigo_material = 'silicona'")
    stock_nuevo = cursor.fetchone()[0]
    print(f"Stock después: {stock_nuevo}")
    print(f"Diferencia: {stock_nuevo - stock_actual}")
    
    # Verificar eventos del sistema
    cursor.execute("""
        SELECT COUNT(*) FROM eventos_sistema 
        WHERE tipo = 'ENTRADA_FERRETERO' AND mensaje LIKE '%silicona%'
        ORDER BY fecha_evento DESC LIMIT 1
    """)
    
    eventos = cursor.fetchone()[0]
    print(f"Eventos registrados: {eventos}")
    
    if stock_nuevo > stock_actual:
        print("\n✅ TRIGGER FUNCIONANDO CORRECTAMENTE")
        print(f"   Stock aumentó de {stock_actual} a {stock_nuevo} (+{stock_nuevo - stock_actual})")
    else:
        print("\n❌ TRIGGER NO ESTÁ FUNCIONANDO")
        print(f"   Stock no cambió: {stock_actual} -> {stock_nuevo}")
    
    connection.commit()
    
except mysql.connector.Error as e:
    print(f"❌ Error de MySQL: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()