import requests
import json
from datetime import datetime
import time

# Configuración
BASE_URL = 'http://localhost:8080'

def debug_frontend_asistencia():
    """Debug del frontend de asistencia"""
    session = requests.Session()
    
    print("=== DEBUG FRONTEND ASISTENCIA ===")
    
    # Datos de login
    login_data = {
        'username': '80833959',
        'password': 'M4r14l4r@'
    }
    
    try:
        # 1. Hacer login
        print("\n1. Haciendo login...")
        login_response = session.post(f'{BASE_URL}/', data=login_data)
        
        if login_response.status_code == 200 and 'dashboard' in login_response.url:
            print("✓ Login exitoso")
        else:
            print(f"✗ Error en login: {login_response.status_code}")
            return
        
        # 2. Acceder a la página de asistencia
        print("\n2. Accediendo a página de asistencia...")
        asistencia_response = session.get(f'{BASE_URL}/asistencia')
        
        if asistencia_response.status_code == 200:
            print("✓ Página de asistencia cargada")
            
            # Verificar si contiene los elementos necesarios
            html_content = asistencia_response.text
            
            elementos_necesarios = [
                'tablaResumenAgrupado',
                'mensajeCargaResumen', 
                'mensajeSinDatosResumen',
                'cargarResumenAgrupado',
                'inicializarResumen'
            ]
            
            print("\n3. Verificando elementos DOM necesarios:")
            for elemento in elementos_necesarios:
                if elemento in html_content:
                    print(f"✓ {elemento} encontrado")
                else:
                    print(f"✗ {elemento} NO encontrado")
            
            # Verificar si hay errores JavaScript obvios
            errores_js = [
                'loadingResumen',  # ID incorrecto que debería ser mensajeCargaResumen
                'tablaResumen',    # ID incorrecto que debería ser tablaResumenAgrupado
                'noDataResumen'    # ID incorrecto que debería ser mensajeSinDatosResumen
            ]
            
            print("\n4. Verificando IDs incorrectos en JavaScript:")
            for error in errores_js:
                if error in html_content:
                    print(f"✗ ID incorrecto '{error}' encontrado en el código")
                else:
                    print(f"✓ ID incorrecto '{error}' no encontrado")
                    
        else:
            print(f"✗ Error al cargar página de asistencia: {asistencia_response.status_code}")
            return
        
        # 3. Probar endpoint directamente
        print("\n5. Probando endpoint de resumen...")
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        url_resumen = f'{BASE_URL}/api/asistencia/resumen_agrupado?fecha_inicio={fecha_hoy}&fecha_fin={fecha_hoy}'
        
        response = session.get(url_resumen)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    print(f"✓ Endpoint funciona - Total registros: {data.get('total_general', 0)}")
                    print(f"✓ Grupos encontrados: {len(data.get('resumen_grupos', []))}")
                    print(f"✓ Carpetas encontradas: {len(data.get('detallado', []))}")
                else:
                    print(f"✗ Endpoint devuelve error: {data.get('message')}")
            except json.JSONDecodeError:
                print("✗ Respuesta no es JSON válido")
        else:
            print(f"✗ Error en endpoint: {response.status_code}")
        
        # 4. Verificar endpoint de supervisores
        print("\n6. Verificando endpoint de supervisores...")
        supervisores_response = session.get(f'{BASE_URL}/api/supervisores')
        
        if supervisores_response.status_code == 200:
            try:
                supervisores_data = supervisores_response.json()
                print(f"✓ Endpoint supervisores funciona - {len(supervisores_data.get('supervisores', []))} supervisores")
            except json.JSONDecodeError:
                print("✗ Respuesta de supervisores no es JSON válido")
        else:
            print(f"✗ Error en endpoint supervisores: {supervisores_response.status_code}")
            
        print("\n=== RESUMEN ===")
        print("Si todos los elementos están presentes pero no se muestran datos:")
        print("1. Verificar que inicializarResumen() se ejecute al cargar la página")
        print("2. Verificar que no hay errores JavaScript en la consola del navegador")
        print("3. Verificar que los IDs de los elementos DOM coincidan con el JavaScript")
        print("4. Verificar que las fechas por defecto sean correctas")
        
    except Exception as e:
        print(f"✗ Error durante debug: {e}")

if __name__ == '__main__':
    debug_frontend_asistencia()