#!/usr/bin/env python3
"""
Script para verificar la tabla mpa_mantenimientos
"""

import mysql.connector

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        return connection
    except mysql.connector.Error as e:
        print(f'Error al conectar a la base de datos: {e}')
        return None

def debug_mpa_table():
    """Verificar la tabla mpa_mantenimientos"""
    
    connection = get_db_connection()
    if not connection:
        print('No se pudo conectar a la base de datos')
        return
    
    cursor = connection.cursor()
    
    print('=== DEBUG TABLA MPA_MANTENIMIENTOS ===\n')
    
    # 1. Verificar si la tabla existe
    print('1. Verificando si la tabla mpa_mantenimientos existe:')
    try:
        cursor.execute("SHOW TABLES LIKE 'mpa_mantenimientos'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print('   ✅ La tabla mpa_mantenimientos existe')
        else:
            print('   ❌ La tabla mpa_mantenimientos NO existe')
            return
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
        return
    
    # 2. Verificar estructura de la tabla
    print('\n2. Estructura de la tabla:')
    try:
        cursor.execute("DESCRIBE mpa_mantenimientos")
        columns = cursor.fetchall()
        print('   Columnas disponibles:')
        for column in columns:
            print(f'     {column[0]} - {column[1]}')
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
        return
    
    # 3. Verificar registros para TON81E
    print('\n3. Verificando registros para vehículo TON81E:')
    try:
        cursor.execute("""
            SELECT * FROM mpa_mantenimientos 
            WHERE placa = %s
        """, ('TON81E',))
        
        registros = cursor.fetchall()
        
        if registros:
            print(f'   Encontrados {len(registros)} registro(s):')
            for i, registro in enumerate(registros):
                print(f'     {i+1}. {registro}')
        else:
            print('   No hay registros para TON81E')
    
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
    
    # 4. Verificar registros con estado 'Abierto'
    print('\n4. Verificando registros con estado "Abierto":')
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM mpa_mantenimientos 
            WHERE placa = %s AND estado = 'Abierto'
        """, ('TON81E',))
        
        result = cursor.fetchone()
        count = result[0] if result else 0
        
        print(f'   Mantenimientos abiertos para TON81E: {count}')
        
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
    
    # 5. Verificar todos los estados disponibles
    print('\n5. Estados disponibles en la tabla:')
    try:
        cursor.execute("""
            SELECT DISTINCT estado FROM mpa_mantenimientos 
            WHERE estado IS NOT NULL
        """, )
        
        estados = cursor.fetchall()
        
        if estados:
            print('   Estados encontrados:')
            for estado in estados:
                print(f'     - {estado[0]}')
        else:
            print('   No hay estados definidos')
    
    except mysql.connector.Error as e:
        print(f'   Error: {e}')
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    debug_mpa_table()