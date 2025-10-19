#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba del endpoint /api/actualizar_equipo usando Flask test_client:
- Setea sesión con user_name igual a 'super' del registro de prueba
- Envía POST con serial y observacion
- Imprime respuesta y verifica cambios en DB
"""
import sys
import json
import mysql.connector
from contextlib import closing

# Importar la app Flask
import importlib.util
import os
APP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app.py'))
spec = importlib.util.spec_from_file_location("app_module", APP_PATH)
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
app = app_module.app
get_db_connection = app_module.get_db_connection

SERIAL_ARG = sys.argv[1] if len(sys.argv) > 1 else None


def pick_row():
    with closing(get_db_connection()) as conn:
        with closing(conn.cursor(dictionary=True)) as cur:
            if SERIAL_ARG:
                cur.execute("SELECT serial, super FROM disponibilidad_equipos WHERE serial=%s LIMIT 1", (SERIAL_ARG,))
            else:
                cur.execute("SELECT serial, super FROM disponibilidad_equipos ORDER BY fecha_creacion DESC LIMIT 1")
            row = cur.fetchone()
            return row


def get_row(serial):
    with closing(get_db_connection()) as conn:
        with closing(conn.cursor(dictionary=True)) as cur:
            cur.execute("""
                SELECT serial, cuenta, ot, observacion, super
                FROM disponibilidad_equipos WHERE serial=%s LIMIT 1
            """, (serial,))
            return cur.fetchone()


if __name__ == '__main__':
    row = pick_row()
    if not row:
        print("⚠ No hay registros en disponibilidad_equipos")
        sys.exit(0)
    serial = row['serial']
    super_name = row['super'] or ''
    print(f"🔧 Probando serial={serial} con super='{super_name}'")

    before = get_row(serial)
    print(f"Antes: {before}")

    with app.test_client() as client:
        # Setear sesión con user_name igual al 'super' del registro
        with client.session_transaction() as sess:
            sess['user_name'] = super_name
            sess['user_role'] = 'operativo'
            sess['id_codigo_consumidor'] = 'test'
            sess['user_cedula'] = 'test'
        payload = {
            'serial': serial,
            'cuenta': '',
            'ot': '',
            'observacion': 'prueba_test_client'
        }
        resp = client.post('/api/actualizar_equipo', data=json.dumps(payload), content_type='application/json')
        print(f"HTTP {resp.status_code} -> {resp.get_data(as_text=True)}")

    after = get_row(serial)
    print(f"Después: {after}")