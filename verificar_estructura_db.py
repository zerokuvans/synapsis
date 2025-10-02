#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host='localhost',
        database='capired',
        user='root',
        password='732137A031E4b@'
    )
    
    cursor = connection.cursor()
    
    # Verificar si existe la tabla usuarios
    cursor.execute("SHOW TABLES LIKE 'usuarios'")
    usuarios_table = cursor.fetchone()
    
    if usuarios_table:
        print('✅ Tabla usuarios existe')
        cursor.execute('DESCRIBE usuarios')
        columns = cursor.fetchall()
        print('Columnas en usuarios:')
        for col in columns:
            print(f'  - {col[0]}: {col[1]}')
    else:
        print('❌ Tabla usuarios NO existe')
    
    # Verificar tabla recurso_operativo
    cursor.execute('DESCRIBE recurso_operativo')
    columns = cursor.fetchall()
    print('\nColumnas en recurso_operativo:')
    for col in columns:
        print(f'  - {col[0]}: {col[1]}')
    
    # Verificar tabla asistencia
    cursor.execute('DESCRIBE asistencia')
    columns = cursor.fetchall()
    print('\nColumnas en asistencia:')
    for col in columns:
        print(f'  - {col[0]}: {col[1]}')
        
    cursor.close()
    connection.close()
    
except Error as e:
    print(f'Error: {e}')