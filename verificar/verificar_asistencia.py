import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root', 
        password='732137A031E4b@',
        database='capired'
    )
    cursor = conn.cursor(dictionary=True)
    
    print("=== Estructura tabla asistencia ===")
    cursor.execute('DESCRIBE asistencia')
    columns = cursor.fetchall()
    for col in columns:
        print(f"{col['Field']}: {col['Type']}")
    
    print("\n=== Total registros ===")
    cursor.execute('SELECT COUNT(*) as total FROM asistencia')
    total = cursor.fetchone()
    print(f"Total registros: {total['total']}")
    
    print("\n=== Muestra de datos ===")
    cursor.execute('SELECT * FROM asistencia LIMIT 3')
    sample = cursor.fetchall()
    for i, row in enumerate(sample, 1):
        print(f"Registro {i}: {row}")
    
    print("\n=== Verificar datos para hoy ===")
    cursor.execute("SELECT COUNT(*) as hoy FROM asistencia WHERE DATE(fecha_asistencia) = CURDATE()")
    hoy = cursor.fetchone()
    print(f"Registros de hoy: {hoy['hoy']}")
    
    print("\n=== Verificar tipificacion_asistencia ===")
    cursor.execute('SELECT COUNT(*) as total FROM tipificacion_asistencia')
    total_tip = cursor.fetchone()
    print(f"Total tipificaciones: {total_tip['total']}")
    
    cursor.execute('SELECT * FROM tipificacion_asistencia LIMIT 5')
    tip_sample = cursor.fetchall()
    for i, row in enumerate(tip_sample, 1):
        print(f"Tipificación {i}: {row}")
    
    conn.close()
    print("\n✓ Verificación completada")
    
except Exception as e:
    print(f"Error: {e}")