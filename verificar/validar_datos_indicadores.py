import mysql.connector
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Conectar a la base de datos
conn = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST', 'localhost'),
    user=os.getenv('MYSQL_USER', 'root'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DB', 'capired')
)

cursor = conn.cursor(dictionary=True)

# Fecha para búsqueda (hoy y últimos 30 días)
hoy = datetime.now().date()
hace_30_dias = hoy - timedelta(days=30)

# Verificar tabla tipificacion_asistencia
cursor.execute("SHOW TABLES LIKE 'tipificacion_asistencia'")
tiene_tabla_tipificacion = cursor.fetchone() is not None
print(f"✓ Tabla tipificacion_asistencia existe: {tiene_tabla_tipificacion}")

if tiene_tabla_tipificacion:
    cursor.execute("SELECT * FROM tipificacion_asistencia")
    tipificaciones = cursor.fetchall()
    print(f"  - Registros en tipificacion_asistencia: {len(tipificaciones)}")
    for t in tipificaciones:
        print(f"    - {t['codigo_tipificacion']}: {t.get('descripcion', 'Sin descripción')} (valor: {t['valor']})")

# Verificar datos en tabla asistencia
cursor.execute("SHOW TABLES LIKE 'asistencia'")
tiene_tabla_asistencia = cursor.fetchone() is not None
print(f"✓ Tabla asistencia existe: {tiene_tabla_asistencia}")

if tiene_tabla_asistencia:
    # Verificar registros de hoy
    cursor.execute("SELECT COUNT(*) as total FROM asistencia WHERE DATE(fecha_asistencia) = %s", (hoy,))
    total_hoy = cursor.fetchone()['total']
    print(f"  - Registros de asistencia hoy: {total_hoy}")
    
    # Verificar registros de los últimos 30 días
    cursor.execute("SELECT COUNT(*) as total FROM asistencia WHERE DATE(fecha_asistencia) BETWEEN %s AND %s", 
                 (hace_30_dias, hoy))
    total_30_dias = cursor.fetchone()['total']
    print(f"  - Registros de asistencia últimos 30 días: {total_30_dias}")
    
    # Mostrar supervisores con registros
    cursor.execute("SELECT super as supervisor, COUNT(*) as total FROM asistencia GROUP BY super")
    supervisores = cursor.fetchall()
    print(f"  - Supervisores con registros: {len(supervisores)}")
    for s in supervisores:
        if s['supervisor']:  # Evitar supervisores nulos
            print(f"    - {s['supervisor']}: {s['total']} registros")

# Verificar datos en tabla preoperacional
cursor.execute("SHOW TABLES LIKE 'preoperacional'")
tiene_tabla_preoperacional = cursor.fetchone() is not None
print(f"✓ Tabla preoperacional existe: {tiene_tabla_preoperacional}")

if tiene_tabla_preoperacional:
    # Verificar registros de hoy
    cursor.execute("SELECT COUNT(*) as total FROM preoperacional WHERE DATE(fecha) = %s", (hoy,))
    total_hoy = cursor.fetchone()['total']
    print(f"  - Registros preoperacionales hoy: {total_hoy}")
    
    # Verificar registros de los últimos 30 días
    cursor.execute("SELECT COUNT(*) as total FROM preoperacional WHERE DATE(fecha) BETWEEN %s AND %s", 
                 (hace_30_dias, hoy))
    total_30_dias = cursor.fetchone()['total']
    print(f"  - Registros preoperacionales últimos 30 días: {total_30_dias}")
    
    # Mostrar supervisores con registros
    cursor.execute("SELECT supervisor, COUNT(*) as total FROM preoperacional GROUP BY supervisor")
    supervisores = cursor.fetchall()
    print(f"  - Supervisores con registros preoperacionales: {len(supervisores)}")
    for s in supervisores:
        if s['supervisor']:  # Evitar supervisores nulos
            print(f"    - {s['supervisor']}: {s['total']} registros")

# Verificar JOIN entre tablas
if tiene_tabla_tipificacion and tiene_tabla_asistencia:
    try:
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM asistencia a 
            JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
            WHERE DATE(a.fecha_asistencia) BETWEEN %s AND %s AND t.valor = '1'
        """, (hace_30_dias, hoy))
        total_join = cursor.fetchone()['total']
        print(f"✓ JOIN entre asistencia y tipificacion funciona correctamente")
        print(f"  - Registros válidos de asistencia: {total_join}")
    except Exception as e:
        print(f"❌ Error al realizar JOIN: {str(e)}")

# Verificar coincidencias entre asistencia y preoperacional
if tiene_tabla_asistencia and tiene_tabla_preoperacional:
    try:
        cursor.execute("""
            SELECT a.fecha_asistencia, a.super, 
                   COUNT(DISTINCT a.id_asistencia) as total_asistencia,
                   COUNT(DISTINCT p.id) as total_preoperacional
            FROM asistencia a
            LEFT JOIN preoperacional p ON a.super = p.supervisor 
                AND DATE(a.fecha_asistencia) = DATE(p.fecha)
            WHERE DATE(a.fecha_asistencia) BETWEEN %s AND %s
            GROUP BY DATE(a.fecha_asistencia), a.super
            HAVING total_asistencia > 0 AND total_preoperacional > 0
            LIMIT 5
        """, (hace_30_dias, hoy))
        coincidencias = cursor.fetchall()
        print(f"✓ Coincidencias entre asistencia y preoperacional: {len(coincidencias)}")
        for c in coincidencias:
            print(f"  - Fecha: {c['fecha_asistencia']}, Supervisor: {c['super']}")
            print(f"    Asistencias: {c['total_asistencia']}, Preoperacionales: {c['total_preoperacional']}")
    except Exception as e:
        print(f"❌ Error al buscar coincidencias: {str(e)}")

cursor.close()
conn.close()

print("\nResumen final:")
if not tiene_tabla_tipificacion:
    print("❌ FALTA: Tabla tipificacion_asistencia no existe. Debes crearla.")
if not tiene_tabla_asistencia:
    print("❌ FALTA: Tabla asistencia no existe. Debes crearla.")
if not tiene_tabla_preoperacional:
    print("❌ FALTA: Tabla preoperacional no existe. Debes crearla.")

if tiene_tabla_asistencia and tiene_tabla_preoperacional:
    if total_30_dias == 0:
        print("❌ ALERTA: No hay registros de asistencia en los últimos 30 días.")
    if total_30_dias == 0:
        print("❌ ALERTA: No hay registros preoperacionales en los últimos 30 días.")
    
    print("\nPara que el indicador funcione necesitas:")
    print("1. Al menos un registro de asistencia con carpeta_dia que coincida con un código en tipificacion_asistencia") 
    print("2. Al menos un registro preoperacional con el mismo supervisor que en asistencia")
    print("3. Ambos registros deben tener la misma fecha") 