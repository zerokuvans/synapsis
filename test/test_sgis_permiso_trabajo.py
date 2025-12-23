import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app, login_manager, User
import main as main_mod

DB = {
    'recurso_operativo': {
        '1001': {
            'nombre': 'Tecnico Prueba',
            'cargo': 'Operativo',
            'id_codigo_consumidor': '1001',
            'recurso_operativo_cedula': '99999999',
            'super': 'Supervisor Prueba',
            'cliente': 'Cliente Prueba',
            'ciudad': 'Bogota',
            'estado': 'Activo'
        }
    },
    'sgis_permiso_trabajo': [],
    'sgis_permiso_trabajo_historial_semanal_confinado': [],
    'sgis_permiso_trabajo_historial_semanal_altura': []
}

COLS = {
    'sgis_permiso_trabajo': {
        'id_sgis_permiso_trabajo',
        'id_codigo_consumidor',
        'sgis_permiso_trabajo_fecha_emision',
        'sgis_permiso_trabajo_fecha_finalizacion',
        'sgis_permiso_trabajo_trabajadores',
        'sgis_permiso_trabajo_emitido_por',
        'sgis_permiso_trabajo_proyecto',
        'sgis_permiso_trabajo_ciudad',
        'sgis_permiso_trabajo_responsable_trabajo',
        'sgis_permiso_trabajo_cargo',
        'nombre',
        'cargo',
        'cedula',
        'recurso_operativo_cedula',
        'sgis_permiso_trabajo_trabajo_ejecutar',
        'sgis_permiso_trabajo_descripcion_tarea',
        'sgis_permiso_trabajo_herramienta',
        'sgis_permiso_trabajo_herramienta_electrica',
        'sgis_permiso_trabajo_herramienta_manual',
        'sgis_permiso_trabajo_equipos_alturas',
        'sgis_permiso_trabajo_iluminacion',
        'sgis_permiso_trabajo_animales',
        'sgis_permiso_trabajo_notificacion_trabajo',
        'sgis_permiso_trabajo_responsabilidades_permiso',
        'sgis_permiso_trabajo_confinado_aplica',
        'sgis_permiso_trabajo_altura_aplica'
    },
    'sgis_permiso_trabajo_historial_semanal_confinado': {
        'id_sgis_permiso_trabajo_historial_semanal_confinado',
        'id_sgis_permiso_trabajo',
        'id_codigo_consumidor',
        'sgis_permiso_trabajo_historial_confinado_1',
        'sgis_permiso_trabajo_historial_confinado_2',
        'sgis_permiso_trabajo_historial_confinado_3',
        'sgis_permiso_trabajo_historial_confinado_4',
        'sgis_permiso_trabajo_historial_confinado_5',
        'sgis_permiso_trabajo_historial_confinado_6',
        'sgis_permiso_trabajo_historial_confinado_7',
        'sgis_permiso_trabajo_historial_confinado_8',
        'sgis_permiso_trabajo_historial_confinado_9',
        'sgis_permiso_trabajo_historial_confinado_10',
        'sgis_permiso_trabajo_historial_confinado_11',
        'sgis_permiso_trabajo_historial_confinado_fecha',
        'sgis_permiso_trabajo_historial_confinado_firma_tecnico',
        'sgis_permiso_trabajo_historial_confinado_firma_supervisor'
    },
    'sgis_permiso_trabajo_historial_semanal_altura': {
        'id_sgis_permiso_trabajo',
        'id_codigo_consumidor',
        'sgis_permiso_trabajo_historial_altura_1',
        'sgis_permiso_trabajo_historial_altura_2',
        'sgis_permiso_trabajo_historial_altura_3',
        'sgis_permiso_trabajo_historial_altura_4',
        'sgis_permiso_trabajo_historial_altura_5',
        'sgis_permiso_trabajo_historial_altura_6',
        'sgis_permiso_trabajo_historial_altura_7',
        'sgis_permiso_trabajo_historial_altura_8',
        'sgis_permiso_trabajo_historial_altura_9',
        'sgis_permiso_trabajo_historial_altura_10',
        'sgis_permiso_trabajo_historial_altura_11',
        'sgis_permiso_trabajo_historial_altura_12',
        'sgis_permiso_trabajo_historial_altura_13',
        'sgis_permiso_trabajo_historial_altura_14',
        'sgis_permiso_trabajo_historial_altura_15',
        'sgis_permiso_trabajo_historial_altura_16',
        'sgis_permiso_trabajo_historial_altura_17',
        'sgis_permiso_trabajo_historial_altura_18',
        'sgis_permiso_trabajo_historial_altura_19',
        'sgis_permiso_trabajo_historial_altura_20',
        'sgis_permiso_trabajo_historial_altura_21',
        'sgis_permiso_trabajo_historial_altura_22',
        'sgis_permiso_trabajo_historial_altura_23',
        'sgis_permiso_trabajo_historial_altura_24',
        'sgis_permiso_trabajo_historial_altura_fecha',
        'sgis_permiso_trabajo_historial_semanal_altura_firma_tecnico',
        'sgis_permiso_trabajo_historial_semanal_altura_firma_supervisor'
    }
}

class FakeCursor:
    def __init__(self, dictionary=False):
        self.dictionary = dictionary
        self._result = None
        self.lastrowid = None
    def execute(self, sql, params=None):
        s = sql.lower()
        if 'information_schema.columns' in s:
            if 'sgis_permiso_trabajo_historial_semanal_confinado' in s:
                cols = [{'COLUMN_NAME': c} for c in COLS['sgis_permiso_trabajo_historial_semanal_confinado']]
                self._result = cols
                return
            if 'sgis_permiso_trabajo_historial_semanal_altura' in s:
                cols = [{'COLUMN_NAME': c} for c in COLS['sgis_permiso_trabajo_historial_semanal_altura']]
                self._result = cols
                return
            if 'sgis_permiso_trabajo' in s:
                cols = [{'COLUMN_NAME': c} for c in COLS['sgis_permiso_trabajo']]
                self._result = cols
                return
        if 'coalesce(max(id_sgis_permiso_trabajo_historial_semanal_confinado)' in s:
            next_id = len(DB['sgis_permiso_trabajo_historial_semanal_confinado']) + 1
            self._result = [{'next_id': next_id}]
            return
        if 'from recurso_operativo' in s:
            uid = str(params[0])
            ro = DB['recurso_operativo'].get(uid) or {}
            self._result = [ro]
            return
        if 'insert into sgis_permiso_trabajo_historial_semanal_confinado' in s:
            cols_part = sql.split('(')[1].split(')')[0]
            cols = [c.strip() for c in cols_part.split(',')]
            row = dict(zip(cols, params))
            DB['sgis_permiso_trabajo_historial_semanal_confinado'].append(row)
            self.lastrowid = len(DB['sgis_permiso_trabajo_historial_semanal_confinado'])
            self._result = None
            return
        if 'insert into sgis_permiso_trabajo_historial_semanal_altura' in s:
            cols_part = sql.split('(')[1].split(')')[0]
            cols = [c.strip() for c in cols_part.split(',')]
            row = dict(zip(cols, params))
            DB['sgis_permiso_trabajo_historial_semanal_altura'].append(row)
            self.lastrowid = len(DB['sgis_permiso_trabajo_historial_semanal_altura'])
            self._result = None
            return
        if 'insert into sgis_permiso_trabajo' in s:
            cols_part = sql.split('(')[1].split(')')[0]
            cols = [c.strip() for c in cols_part.split(',')]
            row = dict(zip(cols, params))
            row['id_sgis_permiso_trabajo'] = len(DB['sgis_permiso_trabajo']) + 1
            DB['sgis_permiso_trabajo'].append(row)
            self.lastrowid = row['id_sgis_permiso_trabajo']
            self._result = None
            return
        if 'select * from sgis_permiso_trabajo_historial_semanal_confinado' in s:
            pid = params[0]
            rows = [r for r in DB['sgis_permiso_trabajo_historial_semanal_confinado'] if r.get('id_sgis_permiso_trabajo') == pid]
            self._result = rows
            return
        if 'select * from sgis_permiso_trabajo_historial_semanal_altura' in s:
            pid = params[0]
            rows = [r for r in DB['sgis_permiso_trabajo_historial_semanal_altura'] if r.get('id_sgis_permiso_trabajo') == pid]
            self._result = rows
            return
        if 'select id_sgis_permiso_trabajo' in s and 'from sgis_permiso_trabajo' in s:
            u, hoy, fin = params
            for r in DB['sgis_permiso_trabajo']:
                if r.get('id_codigo_consumidor') == u and r.get('sgis_permiso_trabajo_fecha_emision') == hoy and r.get('sgis_permiso_trabajo_fecha_finalizacion') == fin:
                    self._result = [{'id_sgis_permiso_trabajo': r['id_sgis_permiso_trabajo']}]
                    return
            self._result = []
            return
        if 'select * from sgis_permiso_trabajo' in s:
            if params and len(params) == 3:
                u, hoy, fin = params
                rows = [r for r in DB['sgis_permiso_trabajo'] if r.get('id_codigo_consumidor') == u and r.get('sgis_permiso_trabajo_fecha_emision') == hoy and r.get('sgis_permiso_trabajo_fecha_finalizacion') == fin]
                self._result = rows
                return
            if params and len(params) == 2:
                hoy, fin = params
                rows = [r for r in DB['sgis_permiso_trabajo'] if r.get('sgis_permiso_trabajo_fecha_emision') == hoy and r.get('sgis_permiso_trabajo_fecha_finalizacion') == fin]
                rows.sort(key=lambda x: x.get('id_sgis_permiso_trabajo', 0), reverse=True)
                self._result = rows[:1]
                return
        self._result = []
    def fetchone(self):
        if self._result:
            return self._result[0]
        return None
    def fetchall(self):
        return self._result or []
    def close(self):
        return None

class FakeConnection:
    def cursor(self, dictionary=False):
        return FakeCursor(dictionary=dictionary)
    def commit(self):
        return None
    def rollback(self):
        return None
    def close(self):
        return None


def run_tests():
    results = []
    app.testing = True
    main_mod.get_db_connection = lambda: FakeConnection()
    with app.test_client() as client:
        @login_manager.user_loader
        def _dummy_loader(user_id):
            return User(id=user_id, nombre='Test', role='operativo')
        with client.session_transaction() as sess:
            sess['user_id'] = '1001'
            sess['id_codigo_consumidor'] = '1001'
            sess['user_role'] = 'administrativo'
            sess['user_cedula'] = '99999999'
            sess['_user_id'] = '1001'

        r1 = client.get('/api/sgis/permiso-trabajo/current')
        results.append({'step': 'GET current', 'status': r1.status_code})

        payload_permiso = {
            'sgis_permiso_trabajo_trabajo_ejecutar': 'Mantenimiento correctivo',
            'sgis_permiso_trabajo_descripcion_tarea': 'Revisión de equipo en sitio',
            'sgis_permiso_trabajo_herramienta': 'Herramienta manual y eléctrica',
            'sgis_permiso_trabajo_herramienta_electrica': 'C',
            'sgis_permiso_trabajo_herramienta_manual': 'C',
            'sgis_permiso_trabajo_equipos_alturas': 'NA',
            'sgis_permiso_trabajo_iluminacion': 'C',
            'sgis_permiso_trabajo_animales': 'NA',
            'sgis_permiso_trabajo_notificacion_trabajo': 'SI',
            'sgis_permiso_trabajo_responsabilidades_permiso': 'NO',
            'sgis_permiso_trabajo_confinado_aplica': 'APLICA',
            'sgis_permiso_trabajo_altura_aplica': 'NO_APLICA'
        }
        r2 = client.post('/api/sgis/permiso-trabajo', json=payload_permiso)
        j2 = r2.get_json(silent=True) or {}
        results.append({'step': 'POST permiso', 'status': r2.status_code, 'id': j2.get('id_sgis_permiso_trabajo') if isinstance(j2, dict) else None})

        permiso_id = (j2.get('id_sgis_permiso_trabajo') if isinstance(j2, dict) else None)

        payload_confinado = {
            'id_sgis_permiso_trabajo': permiso_id,
            'sgis_permiso_trabajo_historial_confinado_1': 'C',
            'sgis_permiso_trabajo_historial_confinado_2': 'C',
            'sgis_permiso_trabajo_historial_confinado_3': 'NC',
            'sgis_permiso_trabajo_historial_confinado_4': 'NA',
            'sgis_permiso_trabajo_historial_confinado_5': 'C',
            'sgis_permiso_trabajo_historial_confinado_6': 'C',
            'sgis_permiso_trabajo_historial_confinado_7': 'C',
            'sgis_permiso_trabajo_historial_confinado_8': 'C',
            'sgis_permiso_trabajo_historial_confinado_9': 'C',
            'sgis_permiso_trabajo_historial_confinado_10': 'C',
            'sgis_permiso_trabajo_historial_confinado_11': 'C',
            'sgis_permiso_trabajo_historial_confinado_fecha': str(date.today()),
            'sgis_permiso_trabajo_historial_confinado_firma_tecnico': 'Prueba Tecnico',
            'sgis_permiso_trabajo_historial_confinado_firma_supervisor': 'Prueba Supervisor'
        }
        r3 = client.post('/api/sgis/permiso-trabajo/historial/confinado', json=payload_confinado)
        results.append({'step': 'POST historial confinados', 'status': r3.status_code, 'json': r3.get_json(silent=True)})

        payload_altura = {
            'id_sgis_permiso_trabajo': permiso_id,
            'sgis_permiso_trabajo_historial_altura_1': '12m',
            'sgis_permiso_trabajo_historial_altura_2': 'C',
            'sgis_permiso_trabajo_historial_altura_3': 'C',
            'sgis_permiso_trabajo_historial_altura_4': 'C',
            'sgis_permiso_trabajo_historial_altura_5': 'C',
            'sgis_permiso_trabajo_historial_altura_6': 'C',
            'sgis_permiso_trabajo_historial_altura_7': 'C',
            'sgis_permiso_trabajo_historial_altura_8': 'C',
            'sgis_permiso_trabajo_historial_altura_9': 'C',
            'sgis_permiso_trabajo_historial_altura_10': 'C',
            'sgis_permiso_trabajo_historial_altura_11': 'C',
            'sgis_permiso_trabajo_historial_altura_12': 'C',
            'sgis_permiso_trabajo_historial_altura_13': 'C',
            'sgis_permiso_trabajo_historial_altura_14': 'C',
            'sgis_permiso_trabajo_historial_altura_15': 'C',
            'sgis_permiso_trabajo_historial_altura_16': 'C',
            'sgis_permiso_trabajo_historial_altura_17': 'C',
            'sgis_permiso_trabajo_historial_altura_18': 'C',
            'sgis_permiso_trabajo_historial_altura_19': 'C',
            'sgis_permiso_trabajo_historial_altura_20': 'C',
            'sgis_permiso_trabajo_historial_altura_21': 'C',
            'sgis_permiso_trabajo_historial_altura_22': 'C',
            'sgis_permiso_trabajo_historial_altura_23': 'C',
            'sgis_permiso_trabajo_historial_altura_24': 'C',
            'sgis_permiso_trabajo_historial_altura_fecha': str(date.today()),
            'sgis_permiso_trabajo_historial_semanal_altura_firma_tecnico': 'Prueba Tecnico',
            'sgis_permiso_trabajo_historial_semanal_altura_firma_supervisor': 'Prueba Supervisor'
        }
        r4 = client.post('/api/sgis/permiso-trabajo/historial/alturas', json=payload_altura)
        results.append({'step': 'POST historial alturas', 'status': r4.status_code})

        rc = client.get('/api/sgis/permiso-trabajo/current')
        results.append({'step': 'GET current after', 'status': rc.status_code})

        if permiso_id:
            rch = client.get(f'/api/sgis/permiso-trabajo/historial/confinado?id_sgis_permiso_trabajo={permiso_id}')
            rah = client.get(f'/api/sgis/permiso-trabajo/historial/alturas?id_sgis_permiso_trabajo={permiso_id}')
            results.append({'step': 'GET historial confinados', 'status': rch.status_code, 'json': rch.get_json(silent=True)})
            results.append({'step': 'GET historial alturas', 'status': rah.status_code, 'json': rah.get_json(silent=True)})

        mes = date.today().strftime('%Y-%m')
        rm = client.get(f'/api/sgis/reportes/permiso-trabajo-matriz?cedula=99999999&mes={mes}')
        results.append({'step': 'GET matriz permiso-trabajo', 'status': rm.status_code, 'json': rm.get_json(silent=True)})

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    run_tests()
