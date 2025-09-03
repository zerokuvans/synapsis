import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# Configuración de la base de datos (igual que en main.py)
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT')),
    'time_zone': '+00:00'
}

try:
    # Conectar a la base de datos
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    print('=== VERIFICACIÓN DE DATOS DE VENCIMIENTOS ===')
    print(f'Conectado a: {db_config["database"]} en {db_config["host"]}')
    print('-' * 60)
    
    # Verificar si hay datos de vencimientos
    cursor.execute('''
        SELECT placa, soat_vencimiento, tecnomecanica_vencimiento 
        FROM parque_automotor 
        WHERE soat_vencimiento IS NOT NULL OR tecnomecanica_vencimiento IS NOT NULL 
        LIMIT 10
    ''')
    
    rows = cursor.fetchall()
    print(f'Total de registros con vencimientos: {len(rows)}')
    print('-' * 60)
    
    if rows:
        for row in rows:
            print(f'Placa: {row[0]}, SOAT: {row[1]}, Tecnomecánica: {row[2]}')
    else:
        print('❌ No se encontraron registros con fechas de vencimiento')
    
    # También verificar el total de vehículos
    cursor.execute('SELECT COUNT(*) FROM parque_automotor')
    total = cursor.fetchone()[0]
    print(f'\nTotal de vehículos en la base de datos: {total}')
    
    # Verificar estructura de la tabla
    cursor.execute('DESCRIBE parque_automotor')
    columns = cursor.fetchall()
    print('\n=== ESTRUCTURA DE LA TABLA ===')
    for col in columns:
        if 'vencimiento' in col[0].lower():
            print(f'✓ {col[0]} - {col[1]}')
    
except mysql.connector.Error as e:
    print(f'❌ Error de conexión a MySQL: {e}')
finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print('\n✓ Conexión cerrada')