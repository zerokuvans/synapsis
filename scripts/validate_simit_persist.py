import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, api_mpa_simit_job_run, api_mpa_simit_job_status, get_db_connection, User, login_user, _update_comparendos_from_result

def run_job_and_status(interval=10):
    with app.test_request_context(f'/api/mpa/simit/job/run?force=1&interval={interval}', method='POST'):
        login_user(User(id=0, nombre='Admin', role='administrativo'))
        r = api_mpa_simit_job_run()
        try:
            print('RUN', r.get_data(as_text=True))
        except Exception:
            print('RUN', r)
    import time
    for i in range(3):
        time.sleep(10)
        with app.test_request_context('/api/mpa/simit/job/status', method='GET'):
            login_user(User(id=0, nombre='Admin', role='administrativo'))
            s = api_mpa_simit_job_status()
            try:
                print('STATUS', s.get_data(as_text=True))
            except Exception:
                print('STATUS', s)

def validate_db_one():
    conn = get_db_connection(); cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT mv.placa, mv.tipo_vehiculo, CAST(mv.tecnico_asignado AS UNSIGNED) AS tecnico_id, ro.nombre AS tecnico_nombre
        FROM mpa_vehiculos mv
        LEFT JOIN recurso_operativo ro ON CAST(mv.tecnico_asignado AS UNSIGNED) = ro.id_codigo_consumidor
        WHERE mv.placa IS NOT NULL AND TRIM(mv.placa) <> '' AND mv.estado = 'Activo'
          AND mv.tecnico_asignado IS NOT NULL AND TRIM(mv.tecnico_asignado) <> ''
          AND ro.estado = 'Activo'
        ORDER BY mv.placa LIMIT 1
        """
    )
    row = cur.fetchone(); cur.close(); conn.close()
    if not row:
        print('NO_VALID_PLACA')
        return
    result_data = [{'numero': 'TEST123', 'fecha': '2026-01-14', 'valor': 12345.67, 'entidad': 'SIMIT TEST', 'estado': 'PENDIENTE'}]
    upd = _update_comparendos_from_result((row.get('placa') or '').strip().upper(), row.get('tecnico_id'), row.get('tecnico_nombre'), row.get('tipo_vehiculo'), result_data)
    print('UPD', upd)
    conn = get_db_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT placa, cantidad, valor_total, fuente, fecha_ultima_consulta FROM mpa_comparendos WHERE UPPER(TRIM(placa)) = %s LIMIT 1", ((row.get('placa') or '').strip().upper(),))
    print('DB', cur.fetchone()); cur.close(); conn.close()

def test_playwright(placa='APU64G'):
    payload = json.dumps({'placa': (placa or '').strip().upper()})
    with app.test_request_context('/api/mpa/simit/consultar-playwright', method='POST', data=payload, content_type='application/json'):
        login_user(User(id=0, nombre='Admin', role='administrativo'))
        from app import api_mpa_simit_consultar_playwright
        r = api_mpa_simit_consultar_playwright()
        try:
            if isinstance(r, tuple):
                print('PLAYWRIGHT', r[0].get_data(as_text=True), r[1])
            else:
                print('PLAYWRIGHT', r.get_data(as_text=True))
        except Exception:
            print('PLAYWRIGHT', r)

if __name__ == '__main__':
    run_job_and_status()
    validate_db_one()
    test_playwright('APU64G')
