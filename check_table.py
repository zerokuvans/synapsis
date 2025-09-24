import mysql.connector

try:
    # Conectar a la base de datos
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='732137A031E4b@',
        database='capired'
    )
    
    cursor = connection.cursor()
    
    # Verificar si la tabla cambios_dotacion existe
    cursor.execute("SHOW TABLES LIKE 'cambios_dotacion'")
    result = cursor.fetchall()
    
    if result:
        print("✓ La tabla 'cambios_dotacion' existe")
        
        # Verificar la estructura de la tabla
        cursor.execute("DESCRIBE cambios_dotacion")
        columns = cursor.fetchall()
        print("\nEstructura de la tabla:")
        for column in columns:
            print(f"  - {column[0]}: {column[1]}")
            
        # Verificar si hay datos
        cursor.execute("SELECT COUNT(*) FROM cambios_dotacion")
        count = cursor.fetchone()[0]
        print(f"\nNúmero de registros: {count}")
        
    else:
        print("✗ La tabla 'cambios_dotacion' NO existe")
        
        # Mostrar todas las tablas disponibles
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\nTablas disponibles en la base de datos:")
        for table in tables:
            if 'dotacion' in table[0].lower() or 'cambio' in table[0].lower():
                print(f"  - {table[0]}")
    
    cursor.close()
    connection.close()
    
except mysql.connector.Error as e:
    print(f"Error de base de datos: {e}")
except Exception as e:
    print(f"Error: {e}")