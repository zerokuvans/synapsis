import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT'))
}

def test_trigger():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        print("=== Estado del stock ANTES de la prueba ===")
        cursor.execute("SELECT material_tipo, cantidad_disponible FROM stock_ferretero")
        stock_antes = cursor.fetchall()
        
        for item in stock_antes:
            print(f"{item[0]}: {item[1]} unidades")
        
        print("\n=== Insertando nueva asignación de prueba ===")
        
        # Insertar una nueva asignación de prueba
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
            INSERT INTO ferretero 
            (id_codigo_consumidor, silicona, amarres_negros, amarres_blancos, 
             cinta_aislante, grapas_blancas, grapas_negras, fecha_asignacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (11, 2, 10, 5, 1, 20, 15, fecha_actual))
        
        # Obtener el ID de la nueva asignación
        nuevo_id = cursor.lastrowid
        print(f"Nueva asignación creada con ID: {nuevo_id}")
        print("Materiales asignados: 2 siliconas, 10 amarres negros, 5 amarres blancos, 1 cinta aislante, 20 grapas blancas, 15 grapas negras")
        
        connection.commit()
        
        print("\n=== Estado del stock DESPUÉS de la prueba ===")
        cursor.execute("SELECT material_tipo, cantidad_disponible FROM stock_ferretero")
        stock_despues = cursor.fetchall()
        
        for item in stock_despues:
            print(f"{item[0]}: {item[1]} unidades")
        
        print("\n=== Movimientos generados por el trigger ===")
        cursor.execute("""
            SELECT material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva 
            FROM movimientos_stock_ferretero 
            WHERE referencia_id = %s AND referencia_tipo = 'asignacion_ferretero'
            ORDER BY id_movimiento
        """, (nuevo_id,))
        movimientos = cursor.fetchall()
        
        if movimientos:
            for mov in movimientos:
                print(f"Material: {mov[0]}, Tipo: {mov[1]}, Cantidad: {mov[2]}, Stock Anterior: {mov[3]}, Stock Nuevo: {mov[4]}")
        else:
            print("❌ No se generaron movimientos - El trigger no funcionó")
        
        print("\n=== Comparación de cambios en el stock ===")
        stock_antes_dict = {item[0]: item[1] for item in stock_antes}
        stock_despues_dict = {item[0]: item[1] for item in stock_despues}
        
        for material in stock_antes_dict:
            diferencia = stock_despues_dict[material] - stock_antes_dict[material]
            if diferencia != 0:
                print(f"{material}: {stock_antes_dict[material]} → {stock_despues_dict[material]} (cambio: {diferencia})")
        
        if len(movimientos) > 0:
            print("\n✅ El trigger está funcionando correctamente")
        else:
            print("\n❌ El trigger NO está funcionando")
        
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    test_trigger()