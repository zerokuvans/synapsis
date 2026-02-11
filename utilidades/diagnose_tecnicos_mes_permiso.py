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
    # Agregar cálculo comparativo desde tecnicos-mes (todas las métricas)
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
        tepp = sum(int(t.get('epp_dias') or 0) for t in tecnicos)
        tcaidas = sum(int(t.get('caidas_dias') or 0) for t in tecnicos)
        tescaleras = sum(int(t.get('escaleras_dias') or 0) for t in tecnicos)
        ttsr = sum(int(t.get('tsr_dias') or 0) for t in tecnicos)
        tp = sum(int(t.get('permiso_dias') or 0) for t in tecnicos)
        # Denominador escaleras aproximado: técnicos con registros de escalera
        td_escaleras_aprox = sum(int(t.get('asistencia_dias') or 0) for t in tecnicos if int(t.get('escaleras_dias') or 0) > 0)
        calc = {
            'total_dias': td,
            'epp_dias': tepp,
            'caidas_dias': tcaidas,
            'escaleras_dias': tescaleras,
            'tsr_dias': ttsr,
            'permiso_dias': tp,
            'pct_epp': int(round((tepp*100.0)/(td or 1))),
            'pct_caidas': int(round((tcaidas*100.0)/(td or 1))),
            'pct_escaleras_aprox': int(round((tescaleras*100.0)/(td_escaleras_aprox or 1))) if td_escaleras_aprox>0 else 0,
            'pct_tsr': int(round((ttsr*100.0)/(td or 1))),
            'pct_permiso': int(round((tp*100.0)/(td or 1))),
            'pct_general_aprox': int(round(((tepp+tcaidas+tescaleras+ttsr+tp)*100.0)/(td*5 or 1)))
        }
        print(json.dumps({'calc_from_tecnicos_mes': calc}, indent=2))

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
    sup = sys.argv[3] if len(sys.argv) > 3 else 'CACERES MARTINEZ CARLOS'
    run(ced, ym)
    run_supervisor(sup, ym)
    run_debug_permiso(ced, ym)
