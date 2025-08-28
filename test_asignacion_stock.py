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
    
    print("🧪 PRUEBA DE ASIGNACIÓN Y VALIDACIÓN DE STOCK")
    print("=" * 50)
    
    # Verificar stock actual
    cursor.execute("SELECT cantidad_disponible FROM stock_ferretero WHERE material_tipo = 'silicona'")
    stock_actual = cursor.fetchone()[0]
    print(f"Stock actual de silicona: {stock_actual}")
    
    # Caso 1: Asignación válida (menor al stock disponible)
    print("\n=== CASO 1: Asignación válida ===")
    cantidad_asignar = min(10, stock_actual)  # Asignar 10 o el stock disponible si es menor
    
    if stock_actual >= cantidad_asignar:
        cursor.execute("""
            INSERT INTO ferretero 
            (id_codigo_consumidor, silicona, amarres_negros, amarres_blancos, 
             cinta_aislante, grapas_blancas, grapas_negras, fecha_asignacion)
            VALUES 
            (1, %s, '0', '0', '0', '0', '0', NOW())
        """, (str(cantidad_asignar),))
        
        asignacion_id = cursor.lastrowid
        print(f"✓ Asignación creada con ID: {asignacion_id}")
        
        # Verificar stock después
        cursor.execute("SELECT cantidad_disponible FROM stock_ferretero WHERE material_tipo = 'silicona'")
        stock_nuevo = cursor.fetchone()[0]
        print(f"Stock después: {stock_nuevo}")
        print(f"Diferencia: {stock_actual - stock_nuevo}")
        
        # Verificar movimientos
        cursor.execute("""
            SELECT COUNT(*) FROM movimientos_stock_ferretero 
            WHERE referencia_id = %s AND referencia_tipo = 'asignacion_ferretero'
        """, (asignacion_id,))
        
        movimientos = cursor.fetchone()[0]
        print(f"Movimientos registrados: {movimientos}")
        
        if stock_nuevo == (stock_actual - cantidad_asignar) and movimientos > 0:
            print("✅ ASIGNACIÓN Y TRIGGER FUNCIONANDO CORRECTAMENTE")
        else:
            print("❌ PROBLEMA CON LA ASIGNACIÓN O TRIGGER")
    else:
        print(f"❌ No hay suficiente stock para asignar {cantidad_asignar} unidades")
    
    # Caso 2: Intentar asignación que excede el stock
    print("\n=== CASO 2: Asignación que excede stock ===")
    cursor.execute("SELECT cantidad_disponible FROM stock_ferretero WHERE material_tipo = 'silicona'")
    stock_actual_2 = cursor.fetchone()[0]
    cantidad_excesiva = stock_actual_2 + 100  # Intentar asignar más de lo disponible
    
    print(f"Stock disponible: {stock_actual_2}")
    print(f"Intentando asignar: {cantidad_excesiva}")
    
    try:
        cursor.execute("""
            INSERT INTO ferretero 
            (id_codigo_consumidor, silicona, amarres_negros, amarres_blancos, 
             cinta_aislante, grapas_blancas, grapas_negras, fecha_asignacion)
            VALUES 
            (1, %s, '0', '0', '0', '0', '0', NOW())
        """, (str(cantidad_excesiva),))
        
        connection.commit()
        print("❌ LA ASIGNACIÓN EXCESIVA FUE PERMITIDA (PROBLEMA)")
        
    except mysql.connector.Error as e:
        print(f"✅ ASIGNACIÓN EXCESIVA BLOQUEADA: {e}")
        connection.rollback()
    
    connection.commit()
    
except mysql.connector.Error as e:
    print(f"❌ Error de MySQL: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()