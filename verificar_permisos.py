import mysql.connector

# Conectar a la base de datos
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='732137A031E4b@',
    database='capired'
)

cursor = connection.cursor(dictionary=True)

print('=== VERIFICACIÓN DE CONFIGURACIÓN DE PERMISOS ===\n')

# Verificar todas las tablas existentes
cursor.execute("SHOW TABLES")
tablas = cursor.fetchall()
print('Tablas existentes en la base de datos:')
for tabla in tablas:
    print(f'  - {list(tabla.values())[0]}')

print('\n=== VERIFICACIÓN DE TABLAS ESPECÍFICAS ===\n')

# Verificar tabla roles
cursor.execute("SHOW TABLES LIKE 'roles'")
tabla_roles = cursor.fetchone()

if tabla_roles:
    print('✓ Tabla roles existe')
    cursor.execute('DESCRIBE roles')
    estructura = cursor.fetchall()
    print('Estructura:')
    for campo in estructura:
        print(f'  - {campo["Field"]}: {campo["Type"]}')
    
    # Mostrar roles
    cursor.execute('SELECT * FROM roles')
    roles = cursor.fetchall()
    print(f'Roles ({len(roles)} registros):')
    for rol in roles:
        print(f'  - {rol}')
else:
    print('⚠️  Tabla roles NO existe')

# Verificar tabla usuarios
cursor.execute("SHOW TABLES LIKE 'usuarios'")
tabla_usuarios = cursor.fetchone()

if tabla_usuarios:
    print('\n✓ Tabla usuarios existe')
    cursor.execute('DESCRIBE usuarios')
    estructura = cursor.fetchall()
    print('Estructura:')
    for campo in estructura:
        print(f'  - {campo["Field"]}: {campo["Type"]}')
else:
    print('\n⚠️  Tabla usuarios NO existe')

# Verificar estados en devoluciones
cursor.execute('DESCRIBE devoluciones_dotacion')
estructura_dev = cursor.fetchall()
print('\n✓ Estructura de devoluciones_dotacion:')
for campo in estructura_dev:
    print(f'  - {campo["Field"]}: {campo["Type"]}')

cursor.execute('SELECT DISTINCT estado FROM devoluciones_dotacion')
estados_usados = cursor.fetchall()
print(f'\nEstados actualmente en uso:')
for estado in estados_usados:
    print(f'  - {estado["estado"]}')

cursor.close()
connection.close()