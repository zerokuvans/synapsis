import mysql.connector

try:
    # Conectar a la base de datos
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='732137A031E4b@',
        database='capired'
    )
    cursor = conn.cursor()
    
    # Obtener estructura de la tabla
    cursor.execute('DESCRIBE cambios_dotacion')
    result = cursor.fetchall()
    
    print('Estructura de la tabla cambios_dotacion:')
    print('Campo | Tipo | Null | Key | Default | Extra')
    print('-' * 60)
    for row in result:
        print(f'{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}')
    
    # También obtener información adicional sobre las columnas
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE, COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'capired' AND TABLE_NAME = 'cambios_dotacion'
        ORDER BY ORDINAL_POSITION
    """)
    
    detailed_result = cursor.fetchall()
    print('\nInformación detallada de columnas:')
    print('Campo | Tipo | Longitud | Nullable | Default')
    print('-' * 50)
    for row in detailed_result:
        length = row[2] if row[2] is not None else 'N/A'
        print(f'{row[0]} | {row[1]} | {length} | {row[3]} | {row[4]}')
    
except mysql.connector.Error as err:
    print(f'Error: {err}')
finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print('\nConexión cerrada.')