#!/usr/bin/env python3
import mysql.connector
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de base de datos
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT'))
}

try:
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    
    print("🧪 PRUEBA SIMPLE DE ENTRADA")
    print("=" * 40)
    
    # Verificar stock actual
    cursor.execute("SELECT cantidad_disponible FROM stock_ferretero WHERE material_tipo = 'silicona'")
    stock_actual = cursor.fetchone()[0]
    print(f"Stock actual de silicona: {stock_actual}")
    
    # Insertar entrada directamente
    print("\nInsertando entrada...")
    cursor.execute("""
        INSERT INTO entradas_ferretero 
        (material_tipo, cantidad_entrada, proveedor, numero_factura, observaciones, usuario_registro, fecha_entrada)
        VALUES 
        ('silicona', 50, 'Proveedor Test', 'FAC-001', 'Prueba de trigger', 1, NOW())
    """)
    
    entrada_id = cursor.lastrowid
    print(f"✓ Entrada creada con ID: {entrada_id}")
    
    # Verificar stock después
    cursor.execute("SELECT cantidad_disponible FROM stock_ferretero WHERE material_tipo = 'silicona'")
    stock_nuevo = cursor.fetchone()[0]
    print(f"Stock después: {stock_nuevo}")
    print(f"Diferencia: {stock_nuevo - stock_actual}")
    
    # Verificar movimientos
    cursor.execute("""
        SELECT COUNT(*) FROM movimientos_stock_ferretero 
        WHERE referencia_id = %s AND referencia_tipo = 'entrada_ferretero'
    """, (entrada_id,))
    
    movimientos = cursor.fetchone()[0]
    print(f"Movimientos registrados: {movimientos}")
    
    if stock_nuevo > stock_actual and movimientos > 0:
        print("\n✅ TRIGGER FUNCIONANDO CORRECTAMENTE")
    else:
        print("\n❌ TRIGGER NO ESTÁ FUNCIONANDO")
    
    connection.commit()
    
except mysql.connector.Error as e:
    print(f"❌ Error de MySQL: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()