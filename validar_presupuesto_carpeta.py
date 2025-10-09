#!/usr/bin/env python3
import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost', 
        user='root', 
        password='732137A031E4b@', 
        database='capired'
    )
    cursor = connection.cursor(dictionary=True)
    print('✅ Conexión exitosa a la base de datos')
    
    # Verificar tabla presupuesto_carpeta
    print('\n📋 Estructura de presupuesto_carpeta:')
    cursor.execute('DESCRIBE presupuesto_carpeta')
    columnas = cursor.fetchall()
    tiene_presupuesto_cargo = False
    for col in columnas:
        print(f'  - {col["Field"]} ({col["Type"]})')
        if col["Field"] == 'presupuesto_cargo':
            tiene_presupuesto_cargo = True
    
    print(f'\n¿Tiene columna presupuesto_cargo? {tiene_presupuesto_cargo}')
    
    # Verificar datos
    print('\n📊 Datos de ejemplo en presupuesto_carpeta:')
    cursor.execute('SELECT * FROM presupuesto_carpeta LIMIT 3')
    datos = cursor.fetchall()
    for i, dato in enumerate(datos, 1):
        print(f'  {i}. {dato}')
    
    # Verificar tabla asistencia
    print('\n📋 Estructura de asistencia:')
    cursor.execute('DESCRIBE asistencia')
    columnas_asistencia = cursor.fetchall()
    eventos_existe = False
    valor_existe = False
    for col in columnas_asistencia:
        if col["Field"] in ['eventos', 'valor']:
            print(f'  ✅ {col["Field"]} ({col["Type"]})')
        if col["Field"] == 'eventos':
            eventos_existe = True
        if col["Field"] == 'valor':
            valor_existe = True
    
    print(f'\n¿Tiene columna eventos? {eventos_existe}')
    print(f'¿Tiene columna valor? {valor_existe}')
    
    # Si no tienen las columnas, mostrar todas las columnas
    if not eventos_existe or not valor_existe:
        print('\n📋 Todas las columnas de asistencia:')
        for col in columnas_asistencia:
            print(f'  - {col["Field"]} ({col["Type"]})')
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f'❌ Error: {e}')