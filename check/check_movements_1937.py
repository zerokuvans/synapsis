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

# Verificar movimientos para la asignación 1937
cursor.execute("""
    SELECT material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id 
    FROM movimientos_stock_ferretero 
    WHERE referencia_id = 1937 AND referencia_tipo = 'asignacion_ferretero'
""")
results = cursor.fetchall()

print('=== Movimientos para asignación 1937 ===')
print(f'Total movimientos encontrados: {len(results)}')
for r in results:
    print(f'Material: {r[0]}, Tipo: {r[1]}, Cantidad: {r[2]}, Anterior: {r[3]}, Nueva: {r[4]}, Ref: {r[5]}')

# También verificar todos los movimientos recientes
cursor.execute("""
    SELECT material_tipo, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, referencia_id, fecha_movimiento 
    FROM movimientos_stock_ferretero 
    ORDER BY fecha_movimiento DESC 
    LIMIT 10
""")
recent_results = cursor.fetchall()

print('\n=== Últimos 10 movimientos de stock ===')
for r in recent_results:
    print(f'Material: {r[0]}, Tipo: {r[1]}, Cantidad: {r[2]}, Anterior: {r[3]}, Nueva: {r[4]}, Ref: {r[5]}, Fecha: {r[6]}')

cursor.close()
connection.close()