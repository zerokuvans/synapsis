import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DB'),
        port=int(os.getenv('MYSQL_PORT'))
    )
    cursor = conn.cursor(dictionary=True)
    
    print('Probando consulta preoperacional...')
    
    # Verificar total de registros
    cursor.execute('SELECT COUNT(*) as total FROM preoperacional')
    total = cursor.fetchone()
    print(f'Total registros preoperacionales: {total}')
    
    # Verificar primeros registros
    cursor.execute('SELECT id_codigo_consumidor, fecha FROM preoperacional LIMIT 5')
    registros = cursor.fetchall()
    print('Primeros 5 registros:')
    for r in registros:
        print(f'ID: {r["id_codigo_consumidor"]}, Fecha: {r["fecha"]}')
    
    # Probar la consulta específica del endpoint
    fecha_actual = datetime.now().date()
    print(f'\nProbando consulta del endpoint para fecha: {fecha_actual}')
    
    cursor.execute("""
        SELECT COUNT(*) as count, 
               MAX(CONVERT_TZ(fecha, '+00:00', '-05:00')) as ultimo_registro_bogota
        FROM preoperacional 
        WHERE id_codigo_consumidor = %s 
        AND DATE(CONVERT_TZ(fecha, '+00:00', '-05:00')) = %s
    """, (1, fecha_actual))  # Usando ID 1 como ejemplo
    
    resultado = cursor.fetchone()
    print(f'Resultado consulta: {resultado}')
    
    cursor.close()
    conn.close()
    print('Consulta completada exitosamente')
    
except Exception as e:
    print(f'Error: {str(e)}')
    import traceback
    traceback.print_exc()