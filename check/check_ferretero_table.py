import mysql.connector
import sys

try:
    # Conectar a la base de datos
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='732137A031E4b@',
        database='capired'
    )
    
    cursor = conn.cursor()
    
    print("=== ESTRUCTURA DE LA TABLA FERRETERO ===")
    cursor.execute('DESCRIBE ferretero')
    result = cursor.fetchall()
    
    print("Columnas de la tabla ferretero:")
    for row in result:
        print(f"  {row[0]} - {row[1]} - {row[2]} - {row[3]} - {row[4]} - {row[5]}")
    
    print("\n=== DEFINICIÓN COMPLETA DE LA TABLA ===")
    cursor.execute('SHOW CREATE TABLE ferretero')
    create_table = cursor.fetchone()
    print(create_table[1])
    
    print("\n=== DATOS DE EJEMPLO (PRIMEROS 5 REGISTROS) ===")
    cursor.execute('SELECT * FROM ferretero LIMIT 5')
    sample_data = cursor.fetchall()
    
    if sample_data:
        print("Registros encontrados:")
        for i, row in enumerate(sample_data, 1):
            print(f"  Registro {i}: {row}")
    else:
        print("No hay datos en la tabla ferretero")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"Error de MySQL: {err}")
except Exception as e:
    print(f"Error: {e}")