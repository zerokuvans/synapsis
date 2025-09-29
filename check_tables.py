import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='732137A031E4b@',
        database='capired'
    )
    cursor = conn.cursor()
    
    # Verificar tabla ingresos_dotaciones
    cursor.execute('DESCRIBE ingresos_dotaciones')
    print('=== INGRESOS_DOTACIONES ===')
    for row in cursor.fetchall():
        print(row)
    
    # Verificar tabla dotaciones
    cursor.execute('DESCRIBE dotaciones')
    print('\n=== DOTACIONES ===')
    for row in cursor.fetchall():
        print(row)
    
    # Verificar tabla cambios_dotacion
    cursor.execute('DESCRIBE cambios_dotacion')
    print('\n=== CAMBIOS_DOTACION ===')
    for row in cursor.fetchall():
        print(row)
    
    conn.close()
    print('\n✓ Verificación completada')
    
except Exception as e:
    print(f'Error: {e}')