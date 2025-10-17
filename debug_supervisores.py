import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='732137A031E4b@',
        database='capired'
    )
    
    cursor = connection.cursor(dictionary=True)
    
    # Verificar estructura de la tabla usuarios
    print('=== ESTRUCTURA TABLA USUARIOS ===')
    cursor.execute("DESCRIBE usuarios")
    columnas = cursor.fetchall()
    
    for columna in columnas:
        print(f'  {columna["Field"]}: {columna["Type"]}')
    
    # Verificar algunos registros
    print('\n=== PRIMEROS REGISTROS ===')
    cursor.execute("SELECT * FROM usuarios LIMIT 3")
    registros = cursor.fetchall()
    
    for registro in registros:
        print(f'  {registro}')
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f'Error: {e}')