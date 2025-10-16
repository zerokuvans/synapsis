import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='732137A031E4b@',
        database='capired'
    )
    cursor = connection.cursor(dictionary=True)
    
    print('📋 ESTRUCTURA DE presupuesto_carpeta:')
    cursor.execute('DESCRIBE presupuesto_carpeta')
    columnas = cursor.fetchall()
    for col in columnas:
        print(f'  - {col["Field"]}')
    
    print('\n📋 ESTRUCTURA DE presupuesto_cargo:')
    cursor.execute('DESCRIBE presupuesto_cargo')
    columnas = cursor.fetchall()
    for col in columnas:
        print(f'  - {col["Field"]}')
    
    print('\n📊 EJEMPLO presupuesto_carpeta:')
    cursor.execute('SELECT * FROM presupuesto_carpeta LIMIT 2')
    datos = cursor.fetchall()
    for dato in datos:
        print(f'  {dato}')
    
    print('\n📊 EJEMPLO presupuesto_cargo:')
    cursor.execute('SELECT * FROM presupuesto_cargo LIMIT 2')
    datos = cursor.fetchall()
    for dato in datos:
        print(f'  {dato}')
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f'❌ Error: {e}')