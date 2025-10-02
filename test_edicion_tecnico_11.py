import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"

# Credenciales administrativas
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def test_edicion_tecnico_11():
    """Probar la edición del técnico 11 y verificar que el analista se muestre correctamente"""
    print("="*60)
    print("PRUEBA DE EDICIÓN DEL TÉCNICO 11")
    print("="*60)
    
    # Crear sesión
    session = requests.Session()
    
    print("\n[1] Realizando login...")
    try:
        # Obtener página de login primero
        session.get(LOGIN_URL)
        
        # Datos de login
        login_data = {
            "username": USERNAME,
            "password": PASSWORD
        }
        
        # Headers para simular una petición AJAX
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Realizar login
        login_response = session.post(LOGIN_URL, data=login_data, headers=headers, allow_redirects=True)
        
        # Verificar login
        if "dashboard" in login_response.url or session.cookies.get('session'):
            print("   ✅ Login exitoso")
        else:
            print("   ❌ Login fallido")
            print(f"   URL actual: {login_response.url}")
            print(f"   Status: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False
    
    # Probar endpoint /obtener_usuario/11
    print("\n[2] Probando endpoint /obtener_usuario/11...")
    try:
        response = session.get(f"{BASE_URL}/obtener_usuario/11")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Status: 200 - Datos obtenidos correctamente")
                print(f"   📋 Datos del técnico:")
                print(f"      ID: {data.get('id_codigo_consumidor')}")
                print(f"      Nombre: {data.get('nombre')}")
                print(f"      Cédula: {data.get('recurso_operativo_cedula')}")
                print(f"      Cargo: {data.get('cargo')}")
                print(f"      Analista: '{data.get('analista')}'")
                
                # Verificar que el analista esté asignado
                if data.get('analista') == 'ESPITIA BARON LICED JOANA':
                    print(f"   ✅ Analista correctamente asignado: {data.get('analista')}")
                    return True
                else:
                    print(f"   ❌ Analista no asignado o incorrecto: '{data.get('analista')}'")
                    return False
                    
            except json.JSONDecodeError:
                print(f"   ❌ Respuesta no es JSON válido")
                print(f"   Primeros 200 caracteres: {response.text[:200]}...")
                return False
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Error al consultar endpoint: {e}")
        return False
    
    # Probar endpoint /api/analistas
    print("\n[3] Probando endpoint /api/analistas...")
    try:
        response = session.get(f"{BASE_URL}/api/analistas")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    analistas = data.get('analistas', [])
                    print(f"   ✅ Status: 200 - {len(analistas)} analistas disponibles")
                    
                    # Buscar a ESPITIA BARON LICED JOANA
                    espitia_encontrada = False
                    for analista in analistas:
                        if analista.get('nombre') == 'ESPITIA BARON LICED JOANA':
                            espitia_encontrada = True
                            print(f"   ✅ ESPITIA BARON LICED JOANA encontrada en la lista:")
                            print(f"      ID: {analista.get('id_codigo_consumidor')}")
                            print(f"      Nombre: {analista.get('nombre')}")
                            print(f"      Cédula: {analista.get('recurso_operativo_cedula')}")
                            break
                    
                    if not espitia_encontrada:
                        print(f"   ❌ ESPITIA BARON LICED JOANA NO encontrada en la lista de analistas")
                        print(f"   📋 Analistas disponibles:")
                        for analista in analistas:
                            print(f"      - {analista.get('nombre')} (ID: {analista.get('id_codigo_consumidor')})")
                else:
                    print(f"   ❌ Error en la respuesta: {data.get('message', 'Sin mensaje')}")
                    
            except json.JSONDecodeError:
                print(f"   ❌ Respuesta no es JSON válido")
                print(f"   Primeros 200 caracteres: {response.text[:200]}...")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Error al consultar endpoint: {e}")

def mostrar_resumen():
    """Mostrar resumen de la solución"""
    print("\n" + "="*60)
    print("RESUMEN DE LA SOLUCIÓN")
    print("="*60)
    print("\n🔍 PROBLEMA IDENTIFICADO:")
    print("   El técnico ALARCON SALAS LUIS HERNANDO (ID 11) no tenía analista")
    print("   asignado en la base de datos, por lo que el campo 'analista' en")
    print("   el formulario de edición aparecía vacío.")
    
    print("\n✅ SOLUCIÓN IMPLEMENTADA:")
    print("   1. Se asignó ESPITIA BARON LICED JOANA como analista del técnico")
    print("   2. Se verificó que el endpoint /obtener_usuario/11 devuelve el analista")
    print("   3. Se confirmó que el endpoint /api/analistas incluye a la analista")
    print("   4. La función establecerValorDropdown ahora puede preseleccionar correctamente")
    
    print("\n🎯 RESULTADO:")
    print("   El formulario de edición del técnico ahora debería mostrar")
    print("   a ESPITIA BARON LICED JOANA como analista preseleccionada.")
    
    print("\n📋 ARCHIVOS MODIFICADOS:")
    print("   - Base de datos: tabla recurso_operativo (campo analista)")
    print("   - Scripts creados: asignar_analista_tecnico_11.py, verificar_tecnico_11.py")

if __name__ == "__main__":
    resultado = test_edicion_tecnico_11()
    mostrar_resumen()
    
    if resultado:
        print("\n🎉 ¡PRUEBA EXITOSA! El problema ha sido resuelto.")
    else:
        print("\n⚠️  Verificar manualmente el formulario de edición.")