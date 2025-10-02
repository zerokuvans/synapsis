#!/usr/bin/env python3
import requests
import json

# Configuración
BASE_URL = "http://192.168.80.39:8080"
LOGIN_URL = f"{BASE_URL}/"
API_URL = f"{BASE_URL}/api/analistas/tecnicos-asignados"

# Credenciales de la analista ESPITIA BARON LICED JOANA
USERNAME = "1002407090"
PASSWORD = "CE1002407090"

def debug_current_user():
    """Debug para ver qué información tiene current_user"""
    try:
        # Crear sesión
        session = requests.Session()
        
        print("🔍 DEBUG CURRENT_USER")
        print("=" * 40)
        
        # 1. Login
        print("1. Realizando login...")
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        response = session.post(LOGIN_URL, data=login_data)
        if response.status_code != 200:
            print(f"❌ Error en login: {response.status_code}")
            return
        
        print("✅ Login exitoso")
        
        # 2. Llamar al endpoint para ver el error
        print("\n2. Llamando al endpoint...")
        response = session.get(API_URL)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta exitosa")
            print(f"Analista detectado: {data.get('analista', 'N/A')}")
            print(f"Total técnicos: {data.get('total_tecnicos', 0)}")
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Respuesta: {response.text[:200]}")
        
        # 3. Verificar con fecha específica
        print("\n3. Probando con fecha específica...")
        params = {'fecha': '2025-10-02'}
        response = session.get(API_URL, params=params)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta exitosa con fecha")
            print(f"Analista detectado: {data.get('analista', 'N/A')}")
            print(f"Total técnicos: {data.get('total_tecnicos', 0)}")
            
            # Mostrar algunos técnicos
            tecnicos = data.get('tecnicos', [])
            if tecnicos:
                print(f"\nPrimeros 3 técnicos:")
                for i, tecnico in enumerate(tecnicos[:3]):
                    print(f"  {i+1}. {tecnico.get('tecnico', 'N/A')} ({tecnico.get('cedula', 'N/A')})")
                    asistencia = tecnico.get('asistencia_hoy', {})
                    print(f"     Hora: {asistencia.get('hora_inicio', 'N/A')}")
                    print(f"     Estado: {asistencia.get('estado', 'N/A')}")
                    print(f"     Novedad: {asistencia.get('novedad', 'N/A')}")
        else:
            print(f"❌ Error con fecha: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Respuesta: {response.text[:200]}")
        
    except Exception as e:
        print(f"❌ Error durante debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_current_user()