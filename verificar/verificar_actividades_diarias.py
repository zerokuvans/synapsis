import sys
import os
import re
from dotenv import load_dotenv
import mysql.connector

analista = sys.argv[1] if len(sys.argv) > 1 else ''
fecha = sys.argv[2] if len(sys.argv) > 2 else ''

load_dotenv()
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'port': int(os.getenv('MYSQL_PORT', '3306'))
}
conn = mysql.connector.connect(**db_config)

cur = conn.cursor()
cur.execute(
    """
    SELECT COLUMN_NAME FROM information_schema.columns
    WHERE table_schema=%s AND table_name='operaciones_actividades_diarias'
    ORDER BY ORDINAL_POSITION
    """,
    (db_config.get('database'),)
)
cols = [r[0] for r in cur.fetchall()]
lc = {c.lower(): c for c in cols}

def pick(cands):
    for n in cands:
        if n.lower() in lc:
            return lc[n.lower()]
    for c in cols:
        for n in cands:
            if n.lower() in c.lower():
                return c
    return None

col_ot = pick(['orden_de_trabajo','ot','orden_trabajo','orden','orden_de_servicio'])
col_cuenta = pick(['numero_de_cuenta','cuenta','nro_cuenta','num_cuenta'])
col_fecha = pick(['fecha','fecha_actividad','fecha_asignacion','fecha_orden'])
col_ext = pick(['external_id','exetrnal_id','id_externo','cedula','recurso_operativo_cedula','id_tecnico','id_codigo_consumidor'])

cur.execute("SELECT COUNT(*) FROM operaciones_actividades_diarias")
total = cur.fetchone()[0]

if not (col_ot and col_cuenta and col_fecha and col_ext):
    print({'ok': True, 'total': total, 'cols': cols, 'detected': {'ot': col_ot, 'cuenta': col_cuenta, 'fecha': col_fecha, 'external_id': col_ext}, 'rows': []})
    cur.close(); conn.close(); sys.exit(0)

cur.execute(
    """
    SELECT DATA_TYPE FROM information_schema.columns
    WHERE table_schema=%s AND table_name='operaciones_actividades_diarias' AND column_name=%s
    """,
    (db_config.get('database'), col_fecha)
)
row = cur.fetchone()
tipo_fecha = row[0].lower() if row else None

cur.execute(
    """
    SELECT COLLATION_NAME FROM information_schema.columns
    WHERE table_schema=%s AND table_name='recurso_operativo' AND column_name='analista'
    """,
    (db_config.get('database'),)
)
row = cur.fetchone()
coll = row[0] if row and row[0] else 'utf8mb4_0900_ai_ci'

cur = conn.cursor()
cur.execute(
    f"""
    SELECT recurso_operativo_cedula
    FROM recurso_operativo
    WHERE LOWER(TRIM(analista)) COLLATE {coll} = LOWER(TRIM(CAST(%s AS CHAR CHARACTER SET utf8mb4))) COLLATE {coll}
    """,
    (analista,)
)
cedulas = [r[0] for r in cur.fetchall()]

filtro_fecha_sql = ''
params = []
if fecha:
    fecha_norm = fecha
    fmts = ['%Y-%m-%d','%d/%m/%Y','%d-%m-%Y','%Y/%m/%d']
    for f in fmts:
        try:
            from datetime import datetime
            fecha_norm = datetime.strptime(fecha_norm, f).strftime('%Y-%m-%d')
            break
        except Exception:
            pass
    if tipo_fecha in ('datetime','timestamp','date'):
        filtro_fecha_sql = f" AND DATE(`{col_fecha}`) = %s"
        params.append(fecha_norm)
    else:
        filtro_fecha_sql = f" AND `{col_fecha}` LIKE %s"
        params.append(fecha_norm + '%')

rows = []
if cedulas:
    placeholders = ','.join(['%s'] * len(cedulas))
    q = f"SELECT `{col_ot}` AS ot, `{col_cuenta}` AS cuenta, `{col_fecha}` AS fecha, `{col_ext}` AS external_id FROM operaciones_actividades_diarias WHERE CAST(`{col_ext}` AS CHAR) IN ({placeholders}){filtro_fecha_sql} ORDER BY `{col_fecha}` DESC LIMIT 20"
    cur = conn.cursor(dictionary=True)
    cur.execute(q, tuple(cedulas) + tuple(params))
    rows = cur.fetchall()

print({'ok': True, 'total': total, 'cols': cols, 'detected': {'ot': col_ot, 'cuenta': col_cuenta, 'fecha': col_fecha, 'external_id': col_ext}, 'rows': rows})
cur.close(); conn.close()
