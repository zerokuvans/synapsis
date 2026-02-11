#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
from datetime import datetime

def run_debug(supervisor: str, mes: str):
    base_url = os.environ.get('BASE_URL', 'http://192.168.80.39:8080')
    admin_user = os.environ.get('ADMIN_USER')
    admin_pass = os.environ.get('ADMIN_PASS')

    print("=" * 80)
    print("PRUEBA DETALLADA INDICADORES SGIS POR SUPERVISOR")
    print("=" * 80)
    print(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"BASE_URL: {base_url}")
    print(f"Supervisor: {supervisor}")
    print(f"Mes: {mes}")
    print()

    sess = requests.Session()

    # Login (si se proveen credenciales)
    if admin_user and admin_pass:
        print("🔐 Login administrativo...")
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        resp = sess.post(f"{base_url}/login", data={'username': admin_user, 'password': admin_pass}, headers=headers)
        print(f"   Status: {resp.status_code}")
        try:
            lj = resp.json()
            print(f"   Resultado: {lj.get('status')} - Rol: {lj.get('user_role')} - Usuario: {lj.get('user_name')}")
        except Exception:
            print("   Respuesta no JSON")
    else:
        print("⚠️ Sin credenciales en entorno, se intentará acceder con sesión existente/permiso público.")

    # Endpoint debug por supervisor (muestra totales y porcentajes)
    print("\n🔍 Indicadores DEBUG (supervisor/mes)")
    params_debug = {'supervisor': supervisor, 'mes': mes}
    r1 = sess.get(f"{base_url}/api/sgis/indicadores/supervisores/debug", params=params_debug, headers={'Accept': 'application/json'})
    print(f"GET /api/sgis/indicadores/supervisores/debug -> {r1.status_code}")
    if r1.status_code == 200:
        jd = r1.json()
        if jd.get('success'):
            print("- Porcentajes:")
            for k, v in jd.get('porcentajes', {}).items():
                print(f"  {k}: {v}")
            print("- Totales:")
            for k, v in jd.get('totales', {}).items():
                print(f"  {k}: {v}")
        else:
            print(f"  Error: {jd.get('error')}")
    else:
        print(f"  Error HTTP: {r1.text[:200]}")

    # Endpoint caídas técnicos (lista técnicos y denominador real)
    print("\n🔍 Detalle técnicos Caídas (denominador y numerador)")
    params_tec = {'supervisor': supervisor, 'mes': mes}
    r2 = sess.get(f"{base_url}/api/sgis/indicadores/caidas/tecnicos", params=params_tec, headers={'Accept': 'application/json'})
    print(f"GET /api/sgis/indicadores/caidas/tecnicos -> {r2.status_code}")
    if r2.status_code == 200:
        jt = r2.json()
        if jt.get('success'):
            print(f"- Porcentaje Caídas: {jt.get('porcentaje_caidas')}%")
            print(f"- Denominador (días válidos no AUXILIAR): {jt.get('denominador_dias')}")
            print(f"- Numerador (días con caídas): {jt.get('numerador_dias')}")
            tecs = jt.get('tecnicos', [])
            print(f"- Técnicos: {len(tecs)}")
            print("\nNombre | Cédula | Carpeta | Días asistencia | Días caídas | Incluido denom")
            print("-" * 80)
            for t in tecs:
                print(f"{t.get('nombre')} | {t.get('cedula')} | {t.get('carpeta')} | "
                      f"{t.get('dias_asistencia')} | {t.get('dias_caidas')} | {t.get('incluido_denominador')}")
            # Promedio Caídas: simple vs ponderado
            if tecs:
                den = 0
                num = 0
                porcentajes = []
                for t in tecs:
                    dias = int(t.get('dias_asistencia') or 0)
                    dias_c = int(t.get('dias_caidas') or 0)
                    incluido = bool(t.get('incluido_denominador'))
                    if incluido and dias > 0:
                        den += dias
                        num += dias_c
                        porcentajes.append((dias_c * 100.0) / dias)
                prom_simple = sum(porcentajes) / float(len(porcentajes) or 1)
                prom_pond = (num * 100.0) / float(den or 1)
                print(f"\n- Caídas promedio simple (por técnico): {int(round(prom_simple))}%")
                print(f"- Caídas promedio ponderado (por días): {int(round(prom_pond))}%")
        else:
            print(f"  Error: {jt.get('error')}")
    else:
        print(f"  Error HTTP: {r2.text[:200]}")

    # Endpoint detalle por técnico (validar promedios simple vs ponderado)
    print("\n🔍 Detalle por técnico de TODOS los indicadores")
    params_det = {'supervisor': supervisor, 'mes': mes}
    r3 = sess.get(f"{base_url}/api/sgis/indicadores/supervisores/detalle", params=params_det, headers={'Accept': 'application/json'})
    print(f"GET /api/sgis/indicadores/supervisores/detalle -> {r3.status_code}")
    if r3.status_code == 200:
        jd = r3.json()
        if jd.get('success'):
            det = jd.get('tecnicos', [])
            # EPP: promedio simple vs ponderado
            epp_simple = None
            if det:
                epp_porcentajes = []
                total_dias = 0
                epp_dias_total = 0
                for t in det:
                    dias = int(t.get('dias_asistencia') or 0)
                    epp_d = int(t.get('epp_dias') or 0)
                    total_dias += dias
                    epp_dias_total += epp_d
                    pct = (epp_d * 100.0) / (dias if dias > 0 else 1)
                    epp_porcentajes.append(pct)
                epp_simple = sum(epp_porcentajes) / float(len(epp_porcentajes))
                epp_ponderado = (epp_dias_total * 100.0) / (total_dias if total_dias > 0 else 1)
                print(f"- EPP promedio simple (por técnico): {int(round(epp_simple))}%")
                print(f"- EPP promedio ponderado (por días): {int(round(epp_ponderado))}%")
                print(f"- EPP agregado (API): {jd.get('porcentajes',{}).get('epp')}%")
            # TSR: promedio simple vs ponderado
            if det:
                tsr_porcentajes = []
                tsr_dias_total = 0
                total_dias = 0
                for t in det:
                    dias = int(t.get('dias_asistencia') or 0)
                    tsr_d = int(t.get('tsr_dias') or 0)
                    total_dias += dias
                    tsr_dias_total += tsr_d
                    pct = (tsr_d * 100.0) / (dias if dias > 0 else 1)
                    tsr_porcentajes.append(pct)
                tsr_simple = sum(tsr_porcentajes) / float(len(tsr_porcentajes))
                tsr_ponderado = (tsr_dias_total * 100.0) / (total_dias if total_dias > 0 else 1)
                print(f"- TSR promedio simple (por técnico): {int(round(tsr_simple))}%")
                print(f"- TSR promedio ponderado (por días): {int(round(tsr_ponderado))}%")
                print(f"- TSR agregado (API): {jd.get('porcentajes',{}).get('tsr')}%")
            # Permiso: promedio simple vs ponderado
            if det:
                per_porcentajes = []
                per_dias_total = 0
                total_dias = 0
                for t in det:
                    dias = int(t.get('dias_asistencia') or 0)
                    per_d = int(t.get('permiso_dias') or 0)
                    total_dias += dias
                    per_dias_total += per_d
                    pct = (per_d * 100.0) / (dias if dias > 0 else 1)
                    per_porcentajes.append(pct)
                per_simple = sum(per_porcentajes) / float(len(per_porcentajes))
                per_ponderado = (per_dias_total * 100.0) / (total_dias if total_dias > 0 else 1)
                print(f"- Permiso promedio simple (por técnico): {int(round(per_simple))}%")
                print(f"- Permiso promedio ponderado (por días): {int(round(per_ponderado))}%")
                print(f"- Permiso agregado (API): {jd.get('porcentajes',{}).get('permiso')}%")
            # Escaleras: promedio simple vs ponderado (solo conductores)
            if det:
                esc_porcentajes = []
                esc_dias_total = 0
                den_esc = 0
                for t in det:
                    dias = int(t.get('dias_asistencia') or 0)
                    esc_d = int(t.get('escaleras_dias') or 0)
                    incluye = t.get('incluye_escaleras_den')
                    if incluye:
                        den_esc += dias
                        esc_dias_total += esc_d
                        pct = (esc_d * 100.0) / (dias if dias > 0 else 1)
                        esc_porcentajes.append(pct)
                if den_esc > 0:
                    esc_simple = sum(esc_porcentajes) / float(len(esc_porcentajes))
                    esc_ponderado = (esc_dias_total * 100.0) / den_esc
                    esc_api = jd.get('porcentajes',{}).get('escaleras')
                    print(f"- Escaleras promedio simple (conductores): {int(round(esc_simple))}%")
                    print(f"- Escaleras promedio ponderado (por días): {int(round(esc_ponderado))}%")
                    print(f"- Escaleras agregado (API): {esc_api}%")
            # Mostrar algunos técnicos
            print("\nNombre | Días | EPP días | Caídas días | Escaleras días | TSR días | Permiso días")
            print("-" * 90)
            for t in det:
                print(f"{t.get('nombre')} | {t.get('dias_asistencia')} | {t.get('epp_dias')} | {t.get('caidas_dias')} | {t.get('escaleras_dias')} | {t.get('tsr_dias')} | {t.get('permiso_dias')}")
        else:
            print(f"  Error: {jd.get('error')}")
    else:
        print(f"  Error HTTP: {r3.text[:200]}")

    print("\n✅ Prueba finalizada")


if __name__ == '__main__':
    # Parámetros solicitados
    run_debug(supervisor='MALDONADO GARNICA JAVIER HERNANDO', mes='2026-02')
