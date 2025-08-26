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

def add_initial_stock():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        print("Agregando stock inicial para pruebas...")
        
        # Agregar stock inicial para todos los materiales
        stock_updates = [
            ('silicona', 1000),
            ('amarres_negros', 5000),
            ('amarres_blancos', 5000),
            ('cinta_aislante', 2000),
            ('grapas_blancas', 10000),
            ('grapas_negras', 10000)
        ]
        
        for material, cantidad in stock_updates:
            cursor.execute("""
                UPDATE stock_ferretero 
                SET cantidad_disponible = %s 
                WHERE material_tipo = %s
            """, (cantidad, material))
            print(f"✓ Stock de {material} actualizado a {cantidad} unidades")
        
        connection.commit()
        
        print("\n=== Stock actual después de la actualización ===")
        cursor.execute("SELECT material_tipo, cantidad_disponible FROM stock_ferretero")
        stock = cursor.fetchall()
        
        for item in stock:
            print(f"{item[0]}: {item[1]} unidades")
        
        print("\n✅ Stock inicial agregado exitosamente")
        
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión cerrada")

if __name__ == "__main__":
    add_initial_stock()