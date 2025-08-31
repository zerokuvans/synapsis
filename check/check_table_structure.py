import mysql.connector
from main import get_db_connection

try:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("=== Estructura de la tabla tipificacion_asistencia ===")
    cursor.execute("DESCRIBE tipificacion_asistencia")
    
    columns = cursor.fetchall()
    print("Columnas de la tabla:")
    for col in columns:
        print(f"  - {col['Field']} ({col['Type']}) - {col['Key']} - {col['Null']} - {col['Default']}")
    
    print("\n=== Muestra de datos ===")
    cursor.execute("SELECT * FROM tipificacion_asistencia LIMIT 5")
    
    sample = cursor.fetchall()
    if sample:
        print("Primeros 5 registros:")
        for i, row in enumerate(sample, 1):
            print(f"  {i}. {row}")
    else:
        print("No hay datos en la tabla")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()