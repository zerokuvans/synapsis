import json
import types
import unittest
import os
import sys

# Ensure repository root is on sys.path to import main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class MockCursor:
    def __init__(self):
        self.executed = []
        self._fetchone_queue = []
        self._fetchall_queue = []

    def queue_fetchone(self, value):
        self._fetchone_queue.append(value)

    def queue_fetchall(self, value):
        self._fetchall_queue.append(value)

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchone(self):
        return self._fetchone_queue.pop(0) if self._fetchone_queue else None

    def fetchall(self):
        return self._fetchall_queue.pop(0) if self._fetchall_queue else []

    def close(self):
        pass


class MockConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self._connected = True

    def cursor(self, dictionary=False, buffered=False):
        return self._cursor

    def commit(self):
        pass

    def is_connected(self):
        return self._connected

    def close(self):
        self._connected = False


class GuardarAsistenciasOperativoNormalizacionTest(unittest.TestCase):
    def setUp(self):
        import main
        self.main = main
        self.app = main.app

        # Prepare mock cursor/connection
        self.cursor = MockCursor()
        self.connection = MockConnection(self.cursor)

        # Patch get_db_connection to use our mock
        main.get_db_connection = lambda: self.connection

        # Queue responses for queries used in the route
        # 1) Verificación de registros hoy
        self.cursor.queue_fetchone({'registros_hoy': 0})
        # 2) SELECT carpeta, cargo FROM recurso_operativo
        # Case A: POSTVENTA FTTH BACK → normaliza a POSTVENTA FTTH
        self.cursor.queue_fetchone({'carpeta': 'POSTVENTA FTTH BACK', 'cargo': 'TECNICO'})
        # 3) Presupuesto para carpeta normalizada + cargo
        self.cursor.queue_fetchone({'presupuesto_diario': 5, 'presupuesto_eventos': 2})

    def test_inserta_carpeta_normalizada_y_presupuestos(self):
        client = self.app.test_client()
        with client.session_transaction() as sess:
            sess['user_role'] = 'operativo'
            sess['user_name'] = 'Supervisor Prueba'
            sess['user_cedula'] = '123456789'
            sess['id_codigo_consumidor'] = 42
            sess['user_id'] = 42

        payload = {
            'asistencias': [
                {
                    'cedula': '11111',
                    'tecnico': 'Tecnico Uno',
                    'carpeta_dia': 'POSTVENTA FTTH',
                    'carpeta': 'POSTVENTA FTTH BACK',
                    'super': 'Supervisor Prueba',
                    'id_codigo_consumidor': 42,
                }
            ]
        }

        resp = client.post('/api/operativo/asistencia/guardar',
                           data=json.dumps(payload),
                           content_type='application/json')

        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))

        # Find INSERT into asistencia and validate parameters
        inserts = [q for q in self.cursor.executed if 'INSERT INTO asistencia' in q[0]]
        self.assertEqual(len(inserts), 1, 'Se esperaba un único INSERT')
        _, params = inserts[0]

        # Params: (cedula, tecnico, carpeta_dia, carpeta, super, fecha_asistencia, id_codigo_consumidor, valor, eventos)
        self.assertEqual(params[0], '11111')
        self.assertEqual(params[1], 'Tecnico Uno')
        self.assertEqual(params[2], 'POSTVENTA FTTH')
        # Carpeta debe estar normalizada, sin sufijo BACK
        self.assertEqual(params[3], 'POSTVENTA FTTH')
        self.assertEqual(params[4], 'Supervisor Prueba')
        self.assertEqual(params[6], 42)
        # Presupuestos aplicados desde presupuesto_carpeta
        self.assertEqual(params[7], 5)  # valor
        self.assertEqual(params[8], 2)  # eventos

    def test_normaliza_browfield_a_brownfield(self):
        # Reset executed and queues
        self.cursor.executed.clear()
        self.cursor._fetchone_queue.clear()

        # Responder check de registros hoy
        self.cursor.queue_fetchone({'registros_hoy': 0})
        # recurso_operativo retorna BROWFIELD (mal escrito), debe normalizar a BROWNFIELD
        self.cursor.queue_fetchone({'carpeta': 'BROWFIELD', 'cargo': 'TECNICO'})
        # Presupuesto para BROWNFIELD + TECNICO
        self.cursor.queue_fetchone({'presupuesto_diario': 3, 'presupuesto_eventos': 1})

        client = self.app.test_client()
        with client.session_transaction() as sess:
            sess['user_role'] = 'operativo'
            sess['user_name'] = 'Supervisor Prueba'
            sess['user_cedula'] = '123456789'
            sess['id_codigo_consumidor'] = 42
            sess['user_id'] = 42

        payload = {
            'asistencias': [
                {
                    'cedula': '22222',
                    'tecnico': 'Tecnico Dos',
                    'carpeta_dia': 'BROWNFIELD',
                    'carpeta': 'BROWFIELD',
                    'super': 'Supervisor Prueba',
                    'id_codigo_consumidor': 42,
                }
            ]
        }

        resp = client.post('/api/operativo/asistencia/guardar',
                           data=json.dumps(payload),
                           content_type='application/json')

        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))

        inserts = [q for q in self.cursor.executed if 'INSERT INTO asistencia' in q[0]]
        self.assertEqual(len(inserts), 1, 'Se esperaba un único INSERT')
        _, params = inserts[0]
        self.assertEqual(params[3], 'BROWNFIELD')  # Carpeta normalizada
        self.assertEqual(params[7], 3)
        self.assertEqual(params[8], 1)


if __name__ == '__main__':
    unittest.main()