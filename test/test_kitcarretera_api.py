#!/usr/bin/env python3
import os
import sys
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, REPO_ROOT)

from app import app, login_manager, User

def main():
    app.testing = True

    @login_manager.user_loader
    def _dummy_loader(user_id):
        return User(id=user_id, nombre='Tester', role='administrativo')

    with app.test_client() as client:
        # Simular sesión autenticada administrativa
        with client.session_transaction() as sess:
            sess['_user_id'] = '1001'
            sess['user_id'] = '1001'
            sess['id_codigo_consumidor'] = '1001'
            sess['user_role'] = 'administrativo'
            sess['user_cedula'] = '99999999'

        print('\n=== PRUEBA: Validación de campos faltantes (payload vacío) ===')
        r1 = client.post('/api/mpa/kitcarretera', json={})
        print('Status:', r1.status_code)
        try:
            j1 = r1.get_json()
            print('Respuesta:', j1)
        except Exception:
            print('Respuesta no JSON')

        print('\n=== PRUEBA: Validación de campos faltantes (payload parcial) ===')
        payload_parcial = {
            'tecnico_id': '1001',
            'nombre': 'Tester',
            'recurso_operativo_cedula': '99999999',
            'fecha_inspeccion': datetime.now().strftime('%Y-%m-%dT%H:%M'),
            'placa': 'ABC123',
            'extintor_vencimiento': datetime.now().strftime('%Y-%m-%d'),
            'observaciones': 'Prueba automática',
            'gato': 'SI','cruceta': 'SI','senales': 'SI','botiquin': 'SI',
            'extintor_vigente': 'SI','tacos': 'SI','caja_herramienta_basica': 'SI','llanta_repuesto': 'SI',
            # Falta foto_kit y firmas
        }
        r2 = client.post('/api/mpa/kitcarretera', json=payload_parcial)
        print('Status:', r2.status_code)
        try:
            j2 = r2.get_json()
            print('Respuesta:', j2)
        except Exception:
            print('Respuesta no JSON')

if __name__ == '__main__':
    main()

