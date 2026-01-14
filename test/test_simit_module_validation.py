#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, get_db_connection, User
from flask_login import login_user
from flask import json

def upsert_comparendo(conn, placa, tecnico_id, tecnico_nombre, tipo, cantidad, valor_total):
    tiene = 'SI' if (cantidad or 0) > 0 else 'NO'
    cur = conn.cursor()
    from datetime import datetime
    cur.execute(
        """
        INSERT INTO mpa_comparendos (placa, tecnico_id, tecnico_nombre, tipo_vehiculo, tiene_multas, cantidad, valor_total, fuente, fecha_ultima_consulta)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            tecnico_id=VALUES(tecnico_id),
            tecnico_nombre=VALUES(tecnico_nombre),
            tipo_vehiculo=VALUES(tipo_vehiculo),
            tiene_multas=VALUES(tiene_multas),
            cantidad=VALUES(cantidad),
            valor_total=VALUES(valor_total),
            fuente=VALUES(fuente),
            fecha_ultima_consulta=VALUES(fecha_ultima_consulta)
        """,
        (placa, tecnico_id, tecnico_nombre, tipo, tiene, int(cantidad or 0), float(valor_total or 0), 'PRUEBA', datetime.now())
    )
    conn.commit()
    cur.close()

def main():
    conn = get_db_connection()
    if conn is None:
        print('BD no disponible')
        return 1
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT pa.placa, pa.comparendos AS cantidad, pa.total_comparendos AS total, pa.tipo_vehiculo AS tipo,
               pa.id_codigo_consumidor AS tecnico_id, ro.nombre AS tecnico_nombre
        FROM parque_automotor pa
        LEFT JOIN recurso_operativo ro ON pa.id_codigo_consumidor = ro.id_codigo_consumidor
        WHERE pa.placa IS NOT NULL AND TRIM(pa.placa) <> ''
        ORDER BY pa.placa
        LIMIT 5
        """
    )
    rows = cur.fetchall() or []
    if not rows:
        print('Sin placas para prueba')
        return 1
    for r in rows:
        c = r.get('cantidad')
        t = r.get('total')
        try:
            c_num = int(str(c).strip()) if c is not None else 0
        except Exception:
            c_num = 0
        try:
            t_num = float(str(t).strip()) if t is not None else 0.0
        except Exception:
            t_num = 0.0
        upsert_comparendo(conn, (r.get('placa') or '').strip().upper(), r.get('tecnico_id'), r.get('tecnico_nombre'), r.get('tipo'), c_num, t_num)
    cur.close(); conn.close()

    with app.test_request_context('/api/mpa/simit/resultados'):
        login_user(User(id=0, nombre='Tester', role='administrativo'))
        from app import api_simit_resultados
        resp = api_simit_resultados()
        if hasattr(resp, 'get_json'):
            data = resp.get_json()
        else:
            data = json.loads(resp[0]) if isinstance(resp, tuple) else json.loads(resp)
        ok = data and data.get('success') and isinstance(data.get('data'), list)
        print('Consulta OK:', bool(ok))
        if ok:
            print('Registros:', len(data['data']))
            print('Primeros:', [x.get('placa') for x in data['data'][:5]])
        return 0 if ok else 2

if __name__ == '__main__':
    sys.exit(main())
