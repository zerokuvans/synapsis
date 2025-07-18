import mysql.connector
from datetime import datetime

def main():
    try:
        # Conectar a la base de datos capired
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = conn.cursor(dictionary=True)
        
        # Examinar la estructura de la columna fecha
        cursor.execute("SHOW COLUMNS FROM preoperacional WHERE Field = 'fecha'")
        fecha_column = cursor.fetchone()
        print(f"Estructura de la columna fecha: {fecha_column['Type']}")
        
        # Consultar los últimos 10 registros preoperacionales
        cursor.execute("""
            SELECT id_preoperacional, id_codigo_consumidor, fecha
            FROM preoperacional 
            ORDER BY fecha DESC LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        print('\nRegistros preoperacionales recientes:')
        for r in results:
            print(f"ID: {r['id_preoperacional']}, Usuario: {r['id_codigo_consumidor']}")
            print(f"  Fecha UTC: {r['fecha']}")
            
            # Formatear la fecha como se muestra en la interfaz
            if r['fecha']:
                fecha_utc = r['fecha']
                hora_formateada = fecha_utc.strftime('%I:%M:%S %p')
                print(f"  Hora formateada (como en interfaz): {hora_formateada}")
            
            print('-' * 50)
        
        # Mostrar la hora UTC actual
        print("\nHora UTC actual:")
        cursor.execute("SELECT NOW() as utc_now")
        time_info = cursor.fetchone()
        print(f"  Hora actual UTC: {time_info['utc_now']}")
        
        # Cerrar conexiones
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()