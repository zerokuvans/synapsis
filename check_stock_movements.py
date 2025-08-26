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

def check_stock_movements():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("=== Detalles de la asignación más reciente (ID 1901) ===")
        cursor.execute("SELECT * FROM ferretero WHERE id_ferretero = 1901")
        asignacion = cursor.fetchone()
        
        if asignacion:
            print(f"ID: {asignacion[0]}")
            print(f"Técnico ID: {asignacion[2]}")
            print(f"Silicona: {asignacion[3]}")
            print(f"Amarres Negros: {asignacion[4]}")
            print(f"Amarres Blancos: {asignacion[5]}")
            print(f"Cinta Aislante: {asignacion[6]}")
            print(f"Grapas Blancas: {asignacion[7]}")
            print(f"Grapas Negras: {asignacion[8]}")
            print(f"Fecha: {asignacion[9]}")
        
        print("\n=== Movimientos relacionados con la asignación 1901 ===")
        cursor.execute("SELECT * FROM movimientos_stock_ferretero WHERE referencia_id = 1901 AND referencia_tipo = 'asignacion_ferretero'")
        movimientos = cursor.fetchall()
        
        if movimientos:
            for mov in movimientos:
                print(f"Material: {mov[1]}, Tipo: {mov[2]}, Cantidad: {mov[3]}, Stock Anterior: {mov[4]}, Stock Nuevo: {mov[5]}")
        else:
            print("No se encontraron movimientos para esta asignación")
        
        print("\n=== Estado actual del stock ===")
        cursor.execute("SELECT material_tipo, cantidad_disponible FROM stock_ferretero")
        stock = cursor.fetchall()
        
        for item in stock:
            print(f"{item[0]}: {item[1]} unidades")
        
        print("\n=== Verificando triggers activos ===")
        cursor.execute("SHOW TRIGGERS LIKE '%ferretero%'")
        triggers = cursor.fetchall()
        
        if triggers:
            for trigger in triggers:
                print(f"Trigger: {trigger[0]}, Tabla: {trigger[2]}, Evento: {trigger[1]}")
        else:
            print("No se encontraron triggers")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_stock_movements()