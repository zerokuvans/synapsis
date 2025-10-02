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
    
    # Obtener la fecha de hoy
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    print(f"Creando datos de asistencia para la fecha: {fecha_hoy}")
    
    # Obtener algunos técnicos asignados a la analista ESPITIA BARON LICED JOANA
    cursor.execute("""
        SELECT ro.recurso_operativo_cedula, ro.nombre 
        FROM recurso_operativo ro
        WHERE ro.analista = 'ESPITIA BARON LICED JOANA'
        AND ro.estado = 'Activo'
        LIMIT 3
    """)
    
    tecnicos = cursor.fetchall()
    print(f"Técnicos encontrados: {len(tecnicos)}")
    
    for i, (cedula, nombre) in enumerate(tecnicos):
        print(f"Procesando técnico: {nombre} (Cédula: {cedula})")
        
        # Verificar si ya existe un registro de asistencia para hoy
        cursor.execute("""
            SELECT id_asistencia FROM asistencia 
            WHERE cedula = %s AND DATE(fecha_asistencia) = %s
        """, (cedula, fecha_hoy))
        
        existing = cursor.fetchone()
        
        if existing:
            print(f"  - Ya existe registro de asistencia para {nombre}")
            continue
        
        # Crear datos de ejemplo variados
        if i == 0:
            hora_inicio = "08:30"
            estado = "CUMPLE"
            novedad = ""
        elif i == 1:
            hora_inicio = "09:15"
            estado = "NOVEDAD"
            novedad = "Llegó tarde por tráfico"
        else:
            hora_inicio = "08:00"
            estado = "NO CUMPLE"
            novedad = ""
        
        # Insertar registro de asistencia
        cursor.execute("""
            INSERT INTO asistencia (
                cedula, 
                tecnico,
                fecha_asistencia, 
                hora_inicio, 
                estado, 
                novedad,
                carpeta_dia,
                carpeta,
                super
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            cedula, 
            nombre,
            fecha_hoy, 
            hora_inicio, 
            estado, 
            novedad,
            f"CARP{i+1:03d}",  # Carpeta día de ejemplo
            "tecnicos",  # Carpeta
            "SUPERVISOR_EJEMPLO"  # Supervisor
        ))
        
        print(f"  - Creado registro: {hora_inicio}, {estado}, {novedad}")
    
    # Confirmar cambios
    conn.commit()
    print(f"\n✅ Datos de asistencia creados exitosamente para {len(tecnicos)} técnicos")
    
    # Verificar los datos creados
    cursor.execute("""
        SELECT a.cedula, a.tecnico, a.hora_inicio, a.estado, a.novedad
        FROM asistencia a
        JOIN recurso_operativo ro ON a.cedula = ro.recurso_operativo_cedula
        WHERE DATE(a.fecha_asistencia) = %s
        AND ro.analista = 'ESPITIA BARON LICED JOANA'
    """, (fecha_hoy,))
    
    resultados = cursor.fetchall()
    print(f"\nDatos verificados:")
    for cedula, nombre, hora, estado, novedad in resultados:
        print(f"  - {nombre} ({cedula}): {hora}, {estado}, {novedad}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")