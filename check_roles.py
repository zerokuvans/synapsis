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
    
    print("=== ROLES DISPONIBLES ===")
    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()
    for role in roles:
        print(f"Rol: {role}")
    
    print("\n=== USUARIOS EXISTENTES ===")
    cursor.execute("""
        SELECT recurso_operativo_cedula, nombre, id_roles, estado 
        FROM recurso_operativo 
        WHERE estado = 'Activo'
        LIMIT 5
    """)
    users = cursor.fetchall()
    
    for user in users:
        print(f"Usuario: {user['nombre']}, Cédula: {user['recurso_operativo_cedula']}, Rol ID: {user['id_roles']}, Estado: {user['estado']}")
    
    # Buscar rol de logística
    print("\n=== BUSCANDO ROL LOGISTICA ===")
    cursor.execute("SELECT * FROM roles WHERE nombre LIKE '%logistica%' OR nombre LIKE '%LOGISTICA%'")
    logistica_roles = cursor.fetchall()
    
    if logistica_roles:
        for role in logistica_roles:
            print(f"Rol logística encontrado: {role}")
    else:
        print("No se encontró rol específico de logística")
        print("Mostrando todos los roles:")
        cursor.execute("SELECT * FROM roles")
        all_roles = cursor.fetchall()
        for role in all_roles:
            print(f"  {role}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")