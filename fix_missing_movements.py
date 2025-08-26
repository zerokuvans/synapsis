import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT'))
}

def fix_missing_movements():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        print("Corrigiendo movimientos faltantes para la asignación 1901...")
        
        # Obtener detalles de la asignación 1901
        cursor.execute("SELECT * FROM ferretero WHERE id_ferretero = 1901")
        asignacion = cursor.fetchone()
        
        if not asignacion:
            print("No se encontró la asignación 1901")
            return
        
        id_ferretero = asignacion[0]
        id_codigo_consumidor = asignacion[2]
        silicona = int(asignacion[3]) if asignacion[3] else 0
        amarres_negros = int(asignacion[4]) if asignacion[4] else 0
        amarres_blancos = int(asignacion[5]) if asignacion[5] else 0
        cinta_aislante = int(asignacion[6]) if asignacion[6] else 0
        grapas_blancas = int(asignacion[7]) if asignacion[7] else 0
        grapas_negras = int(asignacion[8]) if asignacion[8] else 0
        
        print(f"Asignación encontrada: ID {id_ferretero}")
        print(f"Silicona: {silicona}, Grapas Blancas: {grapas_blancas}")
        
        # Procesar silicona si > 0
        if silicona > 0:
            cursor.execute("SELECT cantidad_disponible FROM stock_ferretero WHERE material_tipo = 'silicona'")
            stock_actual = cursor.fetchone()[0]
            stock_anterior = stock_actual + silicona  # Calculamos el stock que debería haber tenido antes
            
            # Actualizar stock
            cursor.execute("""
                UPDATE stock_ferretero 
                SET cantidad_disponible = cantidad_disponible - %s 
                WHERE material_tipo = 'silicona'
            """, (silicona,))
            
            # Insertar movimiento
            cursor.execute("""
                INSERT INTO movimientos_stock_ferretero 
                (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, 
                 referencia_id, referencia_tipo, observaciones, usuario_movimiento)
                VALUES ('silicona', 'salida', %s, %s, %s, %s, 'asignacion_ferretero', 
                        'Corrección: Asignación a técnico', %s)
            """, (silicona, stock_anterior, stock_actual, id_ferretero, id_codigo_consumidor))
            
            print(f"✓ Movimiento de silicona corregido: -{silicona} unidades")
        
        # Procesar grapas blancas si > 0
        if grapas_blancas > 0:
            cursor.execute("SELECT cantidad_disponible FROM stock_ferretero WHERE material_tipo = 'grapas_blancas'")
            stock_actual = cursor.fetchone()[0]
            stock_anterior = stock_actual + grapas_blancas
            
            # Actualizar stock
            cursor.execute("""
                UPDATE stock_ferretero 
                SET cantidad_disponible = cantidad_disponible - %s 
                WHERE material_tipo = 'grapas_blancas'
            """, (grapas_blancas,))
            
            # Insertar movimiento
            cursor.execute("""
                INSERT INTO movimientos_stock_ferretero 
                (material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, 
                 referencia_id, referencia_tipo, observaciones, usuario_movimiento)
                VALUES ('grapas_blancas', 'salida', %s, %s, %s, %s, 'asignacion_ferretero', 
                        'Corrección: Asignación a técnico', %s)
            """, (grapas_blancas, stock_anterior, stock_actual, id_ferretero, id_codigo_consumidor))
            
            print(f"✓ Movimiento de grapas blancas corregido: -{grapas_blancas} unidades")
        
        connection.commit()
        
        print("\n=== Verificando correcciones ===")
        cursor.execute("""
            SELECT material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva 
            FROM movimientos_stock_ferretero 
            WHERE referencia_id = 1901 AND referencia_tipo = 'asignacion_ferretero'
        """)
        movimientos = cursor.fetchall()
        
        for mov in movimientos:
            print(f"Material: {mov[0]}, Tipo: {mov[1]}, Cantidad: {mov[2]}, Stock Anterior: {mov[3]}, Stock Nuevo: {mov[4]}")
        
        print("\n=== Stock actual ===")
        cursor.execute("SELECT material_tipo, cantidad_disponible FROM stock_ferretero")
        stock = cursor.fetchall()
        
        for item in stock:
            print(f"{item[0]}: {item[1]} unidades")
        
        print("\n✅ Movimientos corregidos exitosamente")
        
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión cerrada")

if __name__ == "__main__":
    fix_missing_movements()