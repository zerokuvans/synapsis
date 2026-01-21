import json
import sys
import os
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
import main

def run(cedula: str, ym: str):
    app = main.app
    with app.test_client() as client:
        with client.session_transaction() as s:
            s['user_id'] = '1'
            s['user_role'] = 'administrativo'
            s['user_name'] = 'Admin'
        resp = client.get(f"/api/sgis/reportes/tecnicos-mes?mes={ym}")
        print("status:", resp.status_code)
        data = resp.get_json(silent=True) or {}
        arr = data.get('data') or []
        tec = next((t for t in arr if str(t.get('cedula')) == str(cedula)), None)
        print(json.dumps(tec, ensure_ascii=False, indent=2))

def run_supervisor(supervisor: str, ym: str):
    app = main.app
    with app.test_client() as client:
        with client.session_transaction() as s:
            s['user_id'] = '1'
            s['user_role'] = 'operativo'
            s['user_name'] = supervisor
        resp = client.get(f"/api/sgis/indicadores/supervisores?mes={ym}")
        print("status_sup:", resp.status_code)
        data = resp.get_json(silent=True) or {}
        arr = data.get('supervisores') or []
        sup = next((r for r in arr if str(r.get('supervisor','')).strip().upper() == supervisor.strip().upper()), None)
        print(json.dumps(sup, ensure_ascii=False, indent=2))
    # Agregar cálculo comparativo desde tecnicos-mes
    app = main.app
    with app.test_client() as client:
        with client.session_transaction() as s:
            s['user_id'] = '2'
            s['user_role'] = 'operativo'
            s['user_name'] = supervisor
        r2 = client.get(f"/api/sgis/reportes/tecnicos-mes?mes={ym}")
        print("status_tm_sup:", r2.status_code)
        d2 = r2.get_json(silent=True) or {}
        tecnicos = d2.get('data') or []
        td = sum(int(t.get('asistencia_dias') or 0) for t in tecnicos)
        tp = sum(int(t.get('permiso_dias') or 0) for t in tecnicos)
        print(json.dumps({'calc_from_tecnicos_mes': {'total_dias': td, 'permiso_dias': tp, 'pct_permiso': int(round((tp*100.0)/(td or 1)))}}, indent=2))

def run_debug_permiso(cedula: str, ym: str):
    app = main.app
    with app.test_client() as client:
        with client.session_transaction() as s:
            s['user_id'] = '3'
            s['user_role'] = 'administrativo'
            s['user_name'] = 'Admin'
        r = client.get(f"/api/sgis/reportes/tecnicos-mes/debug-permiso?cedula={cedula}&mes={ym}")
        print("status_debug:", r.status_code)
        print(json.dumps(r.get_json(silent=True) or {}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    ced = sys.argv[1] if len(sys.argv) > 1 else '1019093439'
    ym = sys.argv[2] if len(sys.argv) > 2 else '2026-01'
    run(ced, ym)
    run_supervisor('CACERES MARTINEZ CARLOS', ym)
    run_debug_permiso(ced, ym)
