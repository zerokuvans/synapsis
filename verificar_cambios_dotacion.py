import mysql.connector

def verificar_estructura_cambios():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        cursor = conn.cursor()
        
        # Verificar estructura de cambios_dotacion
        cursor.execute('DESCRIBE cambios_dotacion')
        cols = cursor.fetchall()
        
        print('Estructura de cambios_dotacion:')
        for col in cols:
            print(f'  {col[0]}: {col[1]}')
        
        estado_cols = [col[0] for col in cols if 'estado_' in col[0]]
        print('\nCampos de estado:', estado_cols)
        
        # Verificar si la tabla tiene registros
        cursor.execute('SELECT COUNT(*) FROM cambios_dotacion')
        count = cursor.fetchone()[0]
        print(f'\nTotal de registros en cambios_dotacion: {count}')
        
        if count > 0:
            cursor.execute('SELECT * FROM cambios_dotacion LIMIT 3')
            registros = cursor.fetchall()
            print('\nEjemplos de registros:')
            for registro in registros:
                print(f'  {registro}')
        
        conn.close()
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    verificar_estructura_cambios()