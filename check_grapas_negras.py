import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'capired')
}

connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# Verificar historial de grapas negras
print('=== Historial de movimientos de grapas negras ===')
cursor.execute("""
    SELECT material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, fecha_movimiento 
    FROM movimientos_stock_ferretero 
    WHERE material_tipo = 'grapas_negras' 
    ORDER BY fecha_movimiento DESC 
    LIMIT 10
""")
results = cursor.fetchall()

if results:
    for r in results:
        print(f'Tipo: {r[1]}, Cantidad: {r[2]}, Anterior: {r[3]}, Nueva: {r[4]}, Ref: {r[5]}, Fecha: {r[6]}')
else:
    print('No se encontraron movimientos de grapas negras')

# Verificar stock actual de grapas negras
print('\n=== Stock actual de grapas negras ===')
cursor.execute("SELECT cantidad_disponible FROM stock_ferretero WHERE material_tipo = 'grapas_negras'")
stock_result = cursor.fetchone()
if stock_result:
    print(f'Stock actual: {stock_result[0]} unidades')
else:
    print('No se encontró registro de stock para grapas negras')

# Verificar la asignación 1901 específicamente
print('\n=== Detalles de la asignación 1901 ===')
cursor.execute("SELECT grapas_negras, fecha_asignacion FROM ferretero WHERE id_ferretero = 1901")
asignacion_result = cursor.fetchone()
if asignacion_result:
    print(f'Grapas negras asignadas: {asignacion_result[0]}')
    print(f'Fecha de asignación: {asignacion_result[1]}')
else:
    print('No se encontró la asignación 1901')

# Verificar si hay restricciones en el trigger
print('\n=== Verificando lógica del trigger ===')
print('El trigger solo actualiza stock si NEW.grapas_negras > 0')
print('Y solo si hay stock disponible para restar')

cursor.close()
connection.close()