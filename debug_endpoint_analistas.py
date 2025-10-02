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

def debug_endpoint():
    """Debug del endpoint de analistas para ver la estructura exacta de datos"""
    try:
        # Crear sesión
        session = requests.Session()
        
        # 1. Login
        print("1. Realizando login...")
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        response = session.post(LOGIN_URL, data=login_data)
        if response.status_code != 200:
            print(f"✗ Error en login: {response.status_code}")
            return
        
        print("✓ Login exitoso")
        
        # 2. Probar endpoint sin fecha
        print("\n2. Probando endpoint sin fecha...")
        response = session.get(API_URL)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Tipo de respuesta: {type(data)}")
                print(f"Contenido (primeros 500 caracteres):")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                
                if isinstance(data, list) and len(data) > 0:
                    print(f"\nPrimer elemento de la lista:")
                    print(json.dumps(data[0], indent=2, ensure_ascii=False))
                elif isinstance(data, dict):
                    print(f"\nClaves del diccionario: {list(data.keys())}")
                    if 'tecnicos' in data and len(data['tecnicos']) > 0:
                        print(f"\nPrimer técnico:")
                        print(json.dumps(data['tecnicos'][0], indent=2, ensure_ascii=False))
                
            except json.JSONDecodeError as e:
                print(f"Error decodificando JSON: {e}")
                print(f"Respuesta raw: {response.text[:500]}")
        else:
            print(f"Error: {response.status_code}")
            print(f"Respuesta: {response.text[:200]}")
        
        # 3. Probar endpoint con fecha específica
        print("\n3. Probando endpoint con fecha 2025-10-02...")
        params = {'fecha': '2025-10-02'}
        response = session.get(API_URL, params=params)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Tipo de respuesta: {type(data)}")
                print(f"Contenido (primeros 500 caracteres):")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                
            except json.JSONDecodeError as e:
                print(f"Error decodificando JSON: {e}")
                print(f"Respuesta raw: {response.text[:500]}")
        else:
            print(f"Error: {response.status_code}")
            print(f"Respuesta: {response.text[:200]}")
        
    except Exception as e:
        print(f"Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== DEBUG ENDPOINT ANALISTAS ===")
    debug_endpoint()
    print("\n=== DEBUG COMPLETADO ===")