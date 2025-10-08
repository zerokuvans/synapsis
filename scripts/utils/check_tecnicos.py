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
    
    # Verificar total de técnicos
    cursor.execute("SELECT COUNT(*) FROM recurso_operativo WHERE carpeta = 'tecnicos'")
    total_tecnicos = cursor.fetchone()[0]
    print(f"Total técnicos: {total_tecnicos}")
    
    # Verificar técnicos activos
    cursor.execute("SELECT COUNT(*) FROM recurso_operativo WHERE carpeta = 'tecnicos' AND estado = 'Activo'")
    tecnicos_activos = cursor.fetchone()[0]
    print(f"Técnicos activos: {tecnicos_activos}")
    
    # Ver carpetas disponibles
    cursor.execute("SELECT DISTINCT carpeta FROM recurso_operativo WHERE carpeta IS NOT NULL LIMIT 10")
    carpetas = cursor.fetchall()
    print(f"Carpetas disponibles: {carpetas}")
    
    # Ver algunos técnicos de ejemplo
    cursor.execute("SELECT id_codigo_consumidor, nombre, estado, carpeta FROM recurso_operativo WHERE carpeta LIKE '%tecnic%' LIMIT 5")
    ejemplos = cursor.fetchall()
    print(f"Ejemplos de técnicos: {ejemplos}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")