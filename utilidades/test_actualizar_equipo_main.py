#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba del endpoint /api/actualizar_equipo en main.py usando Flask test_client:
- Setea sesión con user_name igual al 'super' del registro
- Envía POST con serial y observacion
- Imprime respuesta y verifica cambios en DB
"""
import sys
import json

try:
    import main
except Exception as e:
    print("Error importando main:", e)
    raise

app = main.app
get_db_connection = main.get_db_connection

SERIAL = 'SKYWDA7C5F9B'
OBS = 'Prueba IDE - ' + SERIAL
USER_NAME = 'CACERES MARTINEZ CARLOS'
USER_CEDULA = '1032402333'
USER_ROLE = 'operativo'

print('=== Prueba API /api/actualizar_equipo en main.py ===')
with app.test_client() as client:
    # Simular sesión operativa del usuario
    with client.session_transaction() as sess:
        sess['user_name'] = USER_NAME
        sess['user_cedula'] = USER_CEDULA
        sess['user_role'] = USER_ROLE
    # Enviar POST sólo con observación
    resp = client.post('/api/actualizar_equipo', json={
        'serial': SERIAL,
        'observacion': OBS
    })
    print('Status:', resp.status_code)
    try:
        print('Resp JSON:', resp.get_json())
    except Exception:
        print('Resp text:', resp.data.decode('utf-8', errors='ignore'))

print('\n=== Verificación en BD ===')
conn = get_db_connection()
if conn is None:
    print('Error: no hay conexión a BD')