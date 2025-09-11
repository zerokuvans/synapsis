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
    
    # Verificar estructura de devoluciones_dotacion
    print("Estructura de la tabla devoluciones_dotacion:")
    cursor.execute("DESCRIBE devoluciones_dotacion")
    for row in cursor.fetchall():
        print(f"Campo: {row[0]}, Tipo: {row[1]}, Null: {row[2]}, Key: {row[3]}, Default: {row[4]}, Extra: {row[5]}")
    
    print("\n" + "="*50 + "\n")
    
    # Verificar si existe tabla devolucion_detalles
    print("Verificando si existe tabla devolucion_detalles:")
    cursor.execute("SHOW TABLES LIKE 'devolucion_detalles'")
    result = cursor.fetchone()
    if result:
        print("La tabla devolucion_detalles ya existe")
        cursor.execute("DESCRIBE devolucion_detalles")
        for row in cursor.fetchall():
            print(f"Campo: {row[0]}, Tipo: {row[1]}, Null: {row[2]}, Key: {row[3]}, Default: {row[4]}, Extra: {row[5]}")
    else:
        print("La tabla devolucion_detalles NO existe")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {str(e)}")