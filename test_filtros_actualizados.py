import requests
import json

# Configuración
BASE_URL = "http://localhost:8080"
LOGIN_URL = f"{BASE_URL}/login"
SUPERVISORES_URL = f"{BASE_URL}/api/lider/inicio-operacion/supervisores"
ANALISTAS_URL = f"{BASE_URL}/api/lider/inicio-operacion/analistas"
DATOS_URL = f"{BASE_URL}/api/lider/inicio-operacion/datos"

# Credenciales
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def test_filtros_actualizados():
    """Probar los filtros actualizados sin duplicados y con dropdown simple"""
    
    # Crear sesión
    session = requests.Session()
    
    print("=== PRUEBA DE FILTROS ACTUALIZADOS ===")
    
    # 1. Login
    print("\n1. Realizando login...")
    login_data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    
    login_response = session.post(LOGIN_URL, data=login_data)
    print(f"   Status login: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"   Error en login: {login_response.text}")
        return
    
    # 2. Probar endpoint de supervisores
    print("\n2. Probando endpoint de supervisores...")
    supervisores_response = session.get(SUPERVISORES_URL)
    print(f"   Status supervisores: {supervisores_response.status_code}")
    
    if supervisores_response.status_code == 200:
        supervisores_data = supervisores_response.json()
        if supervisores_data.get('success'):
            supervisores = supervisores_data.get('supervisores', [])
            print(f"   Total supervisores: {len(supervisores)}")
            print("   Lista de supervisores:")
            for i, supervisor in enumerate(supervisores, 1):
                print(f"     {i}. '{supervisor}'")
            
            # Verificar duplicados
            supervisores_set = set(supervisores)
            if len(supervisores) == len(supervisores_set):
                print("   ✅ No hay duplicados en supervisores")
            else:
                print(f"   ❌ Hay duplicados: {len(supervisores)} total vs {len(supervisores_set)} únicos")
        else:
            print(f"   Error en respuesta: {supervisores_data}")
    else:
        print(f"   Error: {supervisores_response.text}")
    
    # 3. Probar endpoint de analistas
    print("\n3. Probando endpoint de analistas...")
    analistas_response = session.get(ANALISTAS_URL)
    print(f"   Status analistas: {analistas_response.status_code}")
    
    if analistas_response.status_code == 200:
        analistas_data = analistas_response.json()
        if analistas_data.get('success'):
            analistas = analistas_data.get('analistas', [])
            print(f"   Total analistas: {len(analistas)}")
            print("   Lista de analistas:")
            for i, analista in enumerate(analistas, 1):
                print(f"     {i}. '{analista}'")
            
            # Verificar duplicados
            analistas_set = set(analistas)
            if len(analistas) == len(analistas_set):
                print("   ✅ No hay duplicados en analistas")
            else:
                print(f"   ❌ Hay duplicados: {len(analistas)} total vs {len(analistas_set)} únicos")
        else:
            print(f"   Error en respuesta: {analistas_data}")
    else:
        print(f"   Error: {analistas_response.text}")
    
    # 4. Probar filtro con un supervisor específico
    if supervisores_response.status_code == 200:
        supervisores_data = supervisores_response.json()
        if supervisores_data.get('success') and supervisores_data.get('supervisores'):
            primer_supervisor = supervisores_data['supervisores'][0]
            print(f"\n4. Probando filtro con supervisor: '{primer_supervisor}'")
            
            from datetime import date
            fecha_hoy = date.today().strftime('%Y-%m-%d')
            
            params = {
                'fecha': fecha_hoy,
                'supervisores[]': primer_supervisor
            }
            
            datos_response = session.get(DATOS_URL, params=params)
            print(f"   Status datos: {datos_response.status_code}")
            
            if datos_response.status_code == 200:
                datos_data = datos_response.json()
                if datos_data.get('success'):
                    data = datos_data.get('data', {})
                    print(f"   ✅ Filtro funcionando - Técnicos: {data.get('total_tecnicos', 0)}")
                else:
                    print(f"   Error en datos: {datos_data}")
            else:
                print(f"   Error: {datos_response.text}")
    
    print("\n=== PRUEBA COMPLETADA ===")

if __name__ == "__main__":
    test_filtros_actualizados()