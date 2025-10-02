import mysql.connector
from datetime import datetime

try:
    # Conectar a la base de datos
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='732137A031E4b@',
        database='capired'
    )
    
    cursor = conn.cursor()
    
    # Verificar fecha actual del servidor MySQL
    cursor.execute("SELECT CURDATE() as fecha_mysql, NOW() as datetime_mysql")
    fecha_mysql = cursor.fetchone()
    print(f"Fecha MySQL (CURDATE()): {fecha_mysql[0]}")
    print(f"DateTime MySQL (NOW()): {fecha_mysql[1]}")
    
    # Verificar fecha actual de Python
    fecha_python = datetime.now().strftime('%Y-%m-%d')
    print(f"Fecha Python: {fecha_python}")
    
    print("\n" + "="*50)
    
    # Verificar datos de asistencia para hoy usando CURDATE()
    cursor.execute("""
        SELECT a.cedula, a.tecnico, a.hora_inicio, a.estado, a.novedad, DATE(a.fecha_asistencia) as fecha
        FROM asistencia a
        JOIN recurso_operativo ro ON a.cedula = ro.recurso_operativo_cedula
        WHERE DATE(a.fecha_asistencia) = CURDATE()
        AND ro.analista = 'ESPITIA BARON LICED JOANA'
    """)
    
    resultados_curdate = cursor.fetchall()
    print(f"Registros encontrados con CURDATE(): {len(resultados_curdate)}")
    for resultado in resultados_curdate:
        print(f"  - {resultado[1]} ({resultado[0]}): {resultado[2]}, {resultado[3]}, {resultado[4]} - Fecha: {resultado[5]}")
    
    print("\n" + "="*50)
    
    # Verificar datos de asistencia para hoy usando fecha específica
    cursor.execute("""
        SELECT a.cedula, a.tecnico, a.hora_inicio, a.estado, a.novedad, DATE(a.fecha_asistencia) as fecha
        FROM asistencia a
        JOIN recurso_operativo ro ON a.cedula = ro.recurso_operativo_cedula
        WHERE DATE(a.fecha_asistencia) = %s
        AND ro.analista = 'ESPITIA BARON LICED JOANA'
    """, (fecha_python,))
    
    resultados_fecha = cursor.fetchall()
    print(f"Registros encontrados con fecha específica ({fecha_python}): {len(resultados_fecha)}")
    for resultado in resultados_fecha:
        print(f"  - {resultado[1]} ({resultado[0]}): {resultado[2]}, {resultado[3]}, {resultado[4]} - Fecha: {resultado[5]}")
    
    print("\n" + "="*50)
    
    # Verificar todos los registros de asistencia para estos técnicos
    cursor.execute("""
        SELECT a.cedula, a.tecnico, a.hora_inicio, a.estado, a.novedad, a.fecha_asistencia
        FROM asistencia a
        JOIN recurso_operativo ro ON a.cedula = ro.recurso_operativo_cedula
        WHERE ro.analista = 'ESPITIA BARON LICED JOANA'
        ORDER BY a.fecha_asistencia DESC
    """)
    
    todos_registros = cursor.fetchall()
    print(f"Todos los registros de asistencia para técnicos de ESPITIA: {len(todos_registros)}")
    for resultado in todos_registros:
        print(f"  - {resultado[1]} ({resultado[0]}): {resultado[2]}, {resultado[3]}, {resultado[4]} - Fecha: {resultado[5]}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")