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
    
    # Verificar estructura de la tabla recurso_operativo
    cursor.execute("DESCRIBE recurso_operativo")
    columns = cursor.fetchall()
    
    print("Estructura de la tabla recurso_operativo:")
    for column in columns:
        print(f"  - {column[0]}: {column[1]}")
    
    print("\n" + "="*50)
    
    # Buscar campos que puedan relacionar con analistas
    print("Buscando campos relacionados con analistas...")
    for column in columns:
        if 'analista' in column[0].lower() or 'supervisor' in column[0].lower():
            print(f"  ✓ Campo encontrado: {column[0]}")
    
    print("\n" + "="*50)
    
    # Ver algunos registros de ejemplo
    cursor.execute("SELECT * FROM recurso_operativo WHERE carpeta = 'tecnicos' LIMIT 3")
    ejemplos = cursor.fetchall()
    
    print("Ejemplos de registros:")
    for ejemplo in ejemplos:
        print(f"  - {ejemplo}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")