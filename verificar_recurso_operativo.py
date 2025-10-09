import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='732137A031E4b@',
        database='capired'
    )
    cursor = connection.cursor(dictionary=True)
    
    print('📋 Estructura de recurso_operativo:')
    cursor.execute('DESCRIBE recurso_operativo')
    columnas = cursor.fetchall()
    for col in columnas:
        print(f'  - {col["Field"]} ({col["Type"]})')
    
    print('\n📊 Datos de ejemplo:')
    cursor.execute('SELECT * FROM recurso_operativo LIMIT 3')
    datos = cursor.fetchall()
    for i, dato in enumerate(datos, 1):
        print(f'  {i}. {dato}')
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f'❌ Error: {e}')