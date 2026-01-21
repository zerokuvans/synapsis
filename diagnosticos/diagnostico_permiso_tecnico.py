#!/usr/bin/env python3
import os
import sys
from datetime import date, datetime, timedelta
import mysql.connector

def get_db_connection():
    host = os.getenv('MYSQL_HOST', 'localhost')
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '732137A031E4b@')
    database = os.getenv('MYSQL_DB', os.getenv('MYSQL_DATABASE', 'capired'))
    port = int(os.getenv('MYSQL_PORT', '3306')) if os.getenv('MYSQL_PORT') else None
    if port:
        return mysql.connector.connect(host=host, user=user, password=password, database=database, port=port)
    return mysql.connector.connect(host=host, user=user, password=password, database=database)

def parse_args():
    if len(sys.argv) >= 3:
        cedula = sys.argv[1]
        ym = sys.argv[2]
        try:
            inicio = datetime.strptime(ym + '-01', '%Y-%m-%d').date()
        except Exception:
            today = date.today()
            inicio = date(today.year, today.month, 1)
    else:
        cedula = '1019093439'
        today = date.today()
        inicio = date(today.year, 1, 1)
    if inicio.month == 12:
        fin = inicio.replace(year=inicio.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        fin = inicio.replace(month=inicio.month + 1, day=1) - timedelta(days=1)
    return cedula, inicio, fin

def main():
    cedula, inicio, fin = parse_args()
    print('=== DIAGNOSTICO PERMISO DE TRABAJO TECNICO ===')
    print(f'Tecnico cedula: {cedula}  Mes: {inicio.strftime("%Y-%m")}')
    cn = get_db_connection()
    cur = cn.cursor(dictionary=True)

    cur.execute("SELECT id_codigo_consumidor, nombre, super FROM recurso_operativo WHERE recurso_operativo_cedula=%s AND estado='Activo'", (cedula,))
    ro = cur.fetchone() or {}
    print('recurso_operativo:', ro)
    idc = ro.get('id_codigo_consumidor')

    cur.execute(
        """
        SELECT DISTINCT DATE(a.fecha_asistencia) AS dia
        FROM asistencia a
        WHERE a.cedula = %s AND DATE(a.fecha_asistencia) BETWEEN %s AND %s
          AND EXISTS (
                SELECT 1 FROM tipificacion_asistencia t
                WHERE TRIM(UPPER(t.codigo_tipificacion)) = TRIM(UPPER(COALESCE(a.carpeta_dia,'')))
                  AND t.valor = '1'
          )
        ORDER BY dia
        """,
        (cedula, inicio, fin)
    )
    dias = [r['dia'] for r in cur.fetchall()]
    print('asistencia_dias_validos:', len(dias), dias)

    # Determinar columnas existentes para filtrar correctamente
    cur.execute(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'sgis_permiso_trabajo'
        """
    )
    cols = {r['COLUMN_NAME'] if isinstance(r, dict) else r[0] for r in (cur.fetchall() or [])}
    where_parts = []
    params = []
    if 'id_codigo_consumidor' in cols and idc:
        where_parts.append('p.id_codigo_consumidor = %s')
        params.append(idc)
    if 'recurso_operativo_cedula' in cols:
        where_parts.append('p.recurso_operativo_cedula = %s')
        params.append(cedula)
    if 'cedula' in cols:
        where_parts.append('p.cedula = %s')
        params.append(cedula)
    filtro_usuario = ' OR '.join(where_parts) if where_parts else '1=1'
    params.extend([fin, inicio])
    sql_perm = (
        "SELECT id_sgis_permiso_trabajo, sgis_permiso_trabajo_fecha_emision AS emision, "
        "sgis_permiso_trabajo_fecha_finalizacion AS final, sgis_permiso_trabajo_emitido_por AS emitido_por, "
        "sgis_permiso_trabajo_responsable_trabajo AS responsable "
        "FROM sgis_permiso_trabajo p "
        f"WHERE ({filtro_usuario}) AND p.sgis_permiso_trabajo_fecha_emision <= %s AND p.sgis_permiso_trabajo_fecha_finalizacion >= %s "
        "ORDER BY id_sgis_permiso_trabajo DESC"
    )
    cur.execute(sql_perm, tuple(params))
    permisos = cur.fetchall() or []
    print('permisos_semanales_en_mes:', len(permisos))
    for p in permisos:
        print(p)
    perm_ids = [p['id_sgis_permiso_trabajo'] for p in permisos]

    hconf = set(); halt = set()
    if perm_ids:
        fmt_in = (
            f"SELECT DISTINCT DATE(sgis_permiso_trabajo_historial_confinado_fecha) AS dia "
            f"FROM sgis_permiso_trabajo_historial_semanal_confinado "
            f"WHERE id_sgis_permiso_trabajo IN ({','.join(['%s']*len(perm_ids))}) "
            f"AND DATE(sgis_permiso_trabajo_historial_confinado_fecha) BETWEEN %s AND %s"
        )
        cur.execute(fmt_in, tuple(perm_ids) + (inicio, fin))
        hconf = {r['dia'] for r in (cur.fetchall() or [])}

        fmt_al = (
            f"SELECT DISTINCT DATE(sgis_permiso_trabajo_historial_altura_fecha) AS dia "
            f"FROM sgis_permiso_trabajo_historial_semanal_altura "
            f"WHERE id_sgis_permiso_trabajo IN ({','.join(['%s']*len(perm_ids))}) "
            f"AND DATE(sgis_permiso_trabajo_historial_altura_fecha) BETWEEN %s AND %s"
        )
        cur.execute(fmt_al, tuple(perm_ids) + (inicio, fin))
        halt = {r['dia'] for r in (cur.fetchall() or [])}

    print('hist_confinado_dias:', len(hconf), sorted(list(hconf)))
    print('hist_altura_dias:', len(halt), sorted(list(halt)))

    covered = set()
    for p in permisos:
        e = p.get('emision'); f = p.get('final')
        if isinstance(e, datetime):
            e = e.date()
        for d in dias:
            if e and f and e <= d <= f:
                covered.add(d)

    union_perm = covered | hconf | halt
    print('dias_cubiertos_por_rango_semana:', len(covered), sorted(list(covered)))
    print('dias_cubiertos_por_historic:', len(hconf | halt), sorted(list(hconf | halt)))
    print('dias_total_permiso_union:', len(set(dias) & union_perm))

    cur.close(); cn.close()

if __name__ == '__main__':
    main()
