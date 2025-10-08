#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from datetime import datetime

# Configuración
BASE_URL = 'http://192.168.80.15:8080'
USERNAME = '1085176966'  # Cédula de ejemplo
PASSWORD = 'Capired2024*'

def test_duplicados_fix():
    try:
        # Crear sesión para mantener cookies
        session = requests.Session()
        
        # 1. Login
        print('Realizando login...')
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        login_response = session.post(f'{BASE_URL}/login', data=login_data)
        
        if login_response.status_code == 200:
            print('✅ Login exitoso')
            
            # 2. Probar el endpoint corregido
            fecha_hoy = datetime.now().strftime('%Y-%m-%d')
            api_url = f'{BASE_URL}/api/operativo/inicio-operacion/asistencia'
            params = {'fecha': fecha_hoy}
            
            print(f'Probando endpoint: {api_url}')
            print(f'Fecha: {fecha_hoy}')
            
            response = session.get(api_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    registros = data.get('registros', [])
                    print(f'✅ Endpoint funciona correctamente')
                    print(f'Total registros: {len(registros)}')
                    
                    # Verificar duplicados
                    tecnicos_vistos = {}
                    duplicados_encontrados = []
                    
                    for registro in registros:
                        tecnico = registro.get('tecnico', '')
                        if tecnico in tecnicos_vistos:
                            duplicados_encontrados.append(tecnico)
                            tecnicos_vistos[tecnico] += 1
                        else:
                            tecnicos_vistos[tecnico] = 1
                    
                    if duplicados_encontrados:
                        print('❌ AÚN HAY DUPLICADOS:')
                        for tecnico in set(duplicados_encontrados):
                            print(f'  - {tecnico}: {tecnicos_vistos[tecnico]} veces')
                    else:
                        print('✅ NO HAY DUPLICADOS - Problema resuelto!')
                        
                    # Mostrar algunos registros de ejemplo
                    print(f'\nPrimeros 5 registros:')
                    for i, reg in enumerate(registros[:5]):
                        tecnico = reg.get('tecnico', '')
                        carpeta = reg.get('carpeta', '')
                        print(f'{i+1}. {tecnico} - {carpeta}')
                        
                else:
                    print(f'❌ Error en respuesta: {data.get("message", "")}')
            else:
                print(f'❌ Error HTTP: {response.status_code}')
                print(response.text[:500])
        else:
            print(f'❌ Error en login: {login_response.status_code}')
            
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    test_duplicados_fix()