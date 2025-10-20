import requests
import json

def test_tecnico_mecanica_update():
    """Probar la actualizacion de tecnico mecanica con sesion"""
    
    # Crear sesion para mantener cookies
    session = requests.Session()
    
    print("=== PRUEBA DE ACTUALIZACION TECNICO MECANICA ===")
    
    # 1. Login
    print("1. Realizando login...")
    login_data = {
        'username': '80833959',
        'password': 'M4r14l4r@'
    }
    
    login_response = session.post('http://localhost:8080/', data=login_data)
    print(f"   Login Status: {login_response.status_code}")
    
    if login_response.status_code not in [200, 302]:
        print("   Error en login")
        return False
    
    # 2. Obtener lista de tecnico mecanica
    print("2. Obteniendo lista...")
    list_response = session.get('http://localhost:8080/api/mpa/tecnico_mecanica')
    print(f"   Lista Status: {list_response.status_code}")
    
    if list_response.status_code != 200:
        print("   Error al obtener lista")
        return False
    
    data = list_response.json()
    if not data.get('success') or not data.get('data'):
        print("   No hay datos")
        return False
    
    # Usar el primer registro
    tm_record = data['data'][0]
    tm_id = tm_record['id_mpa_tecnico_mecanica']
    print(f"   Usando ID: {tm_id}, Placa: {tm_record['placa']}")
    
    # 3. Probar actualizacion
    print("3. Probando actualizacion...")
    update_data = {
        'observaciones': 'Prueba de actualizacion - corregido',
        'estado': 'Activo'
    }
    
    update_response = session.put(
        f'http://localhost:8080/api/mpa/tecnico_mecanica/{tm_id}',
        json=update_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   Update Status: {update_response.status_code}")
    
    if update_response.status_code == 200:
        try:
            result = update_response.json()
            print(f"   Respuesta: {json.dumps(result, indent=2)}")
            if result.get('success'):
                print("   ✅ ACTUALIZACION EXITOSA")
                return True
            else:
                print(f"   ❌ Error en respuesta: {result.get('error')}")
        except:
            print(f"   ❌ Error al parsear JSON: {update_response.text}")
    else:
        print(f"   ❌ Error HTTP: {update_response.status_code}")
        print(f"   Respuesta: {update_response.text}")
    
    return False

if __name__ == "__main__":
    test_tecnico_mecanica_update()