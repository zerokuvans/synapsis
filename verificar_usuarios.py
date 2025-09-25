import mysql.connector

connection = mysql.connector.connect(
    host='localhost', 
    user='root', 
    password='732137A031E4b@', 
    database='capired'
)

cursor = connection.cursor(dictionary=True)

print('Estructura de la tabla recurso_operativo:')
cursor.execute('DESCRIBE recurso_operativo')
estructura = cursor.fetchall()
for campo in estructura:
    print(f'  - {campo["Field"]}: {campo["Type"]} {campo["Null"]} {campo["Key"]} {campo["Default"]}')

print('\nPrimeros 3 registros de recurso_operativo:')
cursor.execute('SELECT * FROM recurso_operativo LIMIT 3')
usuarios = cursor.fetchall()
for usuario in usuarios:
    print(f'  - {usuario}')

cursor.close()
connection.close()