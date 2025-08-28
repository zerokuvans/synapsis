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

# Verificar movimientos para la asignación 1901
print('=== Movimientos para asignación 1901 ===')
cursor.execute("""
    SELECT material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, fecha_movimiento 
    FROM movimientos_stock_ferretero 
    WHERE referencia_id = 1901 AND referencia_tipo = 'asignacion_ferretero'
""")
results = cursor.fetchall()

print(f'Total movimientos encontrados: {len(results)}')
for r in results:
    print(f'Material: {r[0]}, Tipo: {r[1]}, Cantidad: {r[2]}, Anterior: {r[3]}, Nueva: {r[4]}, Ref: {r[5]}, Fecha: {r[6]}')

# Verificar historial de cinta aislante
print('\n=== Historial reciente de cinta aislante ===')
cursor.execute("""
    SELECT material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, fecha_movimiento 
    FROM movimientos_stock_ferretero 
    WHERE material_tipo = 'cinta_aislante' 
    ORDER BY fecha_movimiento DESC 
    LIMIT 5
""")
cinta_results = cursor.fetchall()

for r in cinta_results:
    print(f'Tipo: {r[1]}, Cantidad: {r[2]}, Anterior: {r[3]}, Nueva: {r[4]}, Ref: {r[5]}, Fecha: {r[6]}')

# Verificar stock actual de cinta aislante
print('\n=== Stock actual de cinta aislante ===')
cursor.execute("SELECT cantidad_disponible FROM stock_ferretero WHERE material_tipo = 'cinta_aislante'")
stock_result = cursor.fetchone()
if stock_result:
    print(f'Stock actual: {stock_result[0]} unidades')

cursor.close()
connection.close()