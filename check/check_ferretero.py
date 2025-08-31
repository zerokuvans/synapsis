import mysql.connector
from datetime import datetime

# Conectar a la base de datos
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='732137A031E4b@',
    database='capired'
)

cursor = conn.cursor(dictionary=True)

# Verificar últimos registros
cursor.execute('SELECT * FROM ferretero ORDER BY fecha_asignacion DESC LIMIT 5')
results = cursor.fetchall()

print('Últimos 5 registros en tabla ferretero:')
print('=' * 50)
for r in results:
    print(f"ID Consumidor: {r['id_codigo_consumidor']}")
    print(f"Fecha: {r['fecha_asignacion']}")
    print(f"Silicona: {r['silicona']}")
    print(f"Amarres negros: {r['amarres_negros']}")
    print(f"Amarres blancos: {r['amarres_blancos']}")
    print('-' * 30)

# Verificar distribución por mes
cursor.execute('SELECT MONTH(fecha_asignacion) as mes, COUNT(*) as total FROM ferretero GROUP BY MONTH(fecha_asignacion) ORDER BY mes')
mes_results = cursor.fetchall()

print('\nDistribución por mes:')
print('=' * 30)
for r in mes_results:
    print(f"Mes {r['mes']}: {r['total']} registros")

# Verificar si hay registros con JOIN a recurso_operativo
cursor.execute('''
    SELECT COUNT(*) as total
    FROM ferretero f 
    LEFT JOIN recurso_operativo r ON f.id_codigo_consumidor = r.id_codigo_consumidor
''')
join_result = cursor.fetchone()
print(f"\nRegistros con JOIN: {join_result['total']}")

cursor.close()
conn.close()