import mysql.connector

try:
    # Conectar a la base de datos
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='732137A031E4b@',
        database='capired'
    )
    
    cursor = connection.cursor(dictionary=True)
    
    # Verificar estructura de la tabla usuarios
    cursor.execute("DESCRIBE usuarios")
    columns = cursor.fetchall()
    print("Estructura de la tabla usuarios:")
    for col in columns:
        print(f"Columna: {col['Field']}, Tipo: {col['Type']}")
    
    # Verificar usuarios activos
    cursor.execute("SELECT * FROM usuarios LIMIT 3")
    users = cursor.fetchall()
    
    print("\nPrimeros usuarios:")
    for user in users:
        print(user)
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")