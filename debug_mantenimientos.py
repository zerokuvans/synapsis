#!/usr/bin/env python3
"""
Script para verificar mantenimientos de TON81E
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

def main():
    connection = get_db_connection()
    if not connection:
        print('No se pudo conectar a la base de datos')
        return
    
    cursor = connection.cursor()
    
    print('=== ESTRUCTURA DE LA TABLA mpa_mantenimientos ===')
    cursor.execute("DESCRIBE mpa_mantenimientos")
    columns = cursor.fetchall()
    for column in columns:
        print(f'{column[0]} - {column[1]}')
    
    print('\n=== VERIFICANDO MANTENIMIENTOS PARA TON81E ===')
    
    # Probar con columna "placa"
    try:
        cursor.execute("""
            SELECT * FROM mpa_mantenimientos 
            WHERE placa = %s
            ORDER BY fecha_mantenimiento DESC
        """, ('TON81E',))
        
        mantenimientos = cursor.fetchall()
        
        if mantenimientos:
            print(f'Mantenimientos encontrados para TON81E: {len(mantenimientos)}')
            for i, mant in enumerate(mantenimientos):
                print(f'  Registro {i+1}: {mant}')
                
            # Verificar específicamente mantenimientos abiertos
            cursor.execute("""
                SELECT COUNT(*) FROM mpa_mantenimientos 
                WHERE placa = %s AND estado = %s
            """, ('TON81E', 'Abierto'))
            
            count_abiertos = cursor.fetchone()[0]
            print(f'\nMantenimientos con estado "Abierto": {count_abiertos}')
            
            # Verificar todos los estados posibles
            cursor.execute("""
                SELECT DISTINCT estado FROM mpa_mantenimientos 
                WHERE placa = %s
            """, ('TON81E',))
            
            estados = cursor.fetchall()
            print(f'\nEstados encontrados para TON81E:')
            for estado in estados:
                print(f'  "{estado[0]}"')
        else:
            print('No se encontraron mantenimientos para TON81E')
            
    except mysql.connector.Error as e:
        print(f'Error en consulta: {e}')
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()