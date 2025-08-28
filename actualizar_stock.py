import mysql.connector
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
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
    
    # Actualizar stock a 100 para todos los materiales
    cursor.execute("""
        UPDATE stock_ferretero 
        SET cantidad_disponible = 100 
        WHERE material_tipo IN ('silicona', 'amarres_negros', 'amarres_blancos', 'cinta_aislante', 'grapas_blancas', 'grapas_negras')
    """)
    
    connection.commit()
    print("✅ Stock actualizado a 100 para todos los materiales")
    
    # Verificar el stock actualizado
    cursor.execute("SELECT material_tipo, cantidad_disponible FROM stock_ferretero")
    stock = cursor.fetchall()
    print("\nStock actual:")
    for row in stock:
        print(f"{row[0]}: {row[1]}")
    
except mysql.connector.Error as e:
    print(f"❌ Error de base de datos: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()