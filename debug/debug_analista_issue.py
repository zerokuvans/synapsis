import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"

# Credenciales administrativas
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def debug_analista_issue():
    """Debug completo del problema de la analista que no aparece"""
    print("="*70)
    print("DEBUG: PROBLEMA DE ANALISTA NO VISIBLE EN FORMULARIO")
    print("="*70)
    
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
            return False
            
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False
    
    # [2] Verificar endpoint /obtener_usuario/11
    print("\n[2] Verificando endpoint /obtener_usuario/11...")
    try:
        response = session.get(f"{BASE_URL}/obtener_usuario/11")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Status: 200 - Datos obtenidos")
                print(f"   📋 DATOS COMPLETOS DEL TÉCNICO:")
                for key, value in data.items():
                    print(f"      {key}: '{value}'")
                
                # Verificar específicamente el campo analista
                analista_value = data.get('analista')
                print(f"\n   🔍 ANÁLISIS DEL CAMPO 'analista':")
                print(f"      Valor: '{analista_value}'")
                print(f"      Tipo: {type(analista_value)}")
                print(f"      Es None: {analista_value is None}")
                print(f"      Es string vacío: {analista_value == ''}")
                print(f"      Longitud: {len(str(analista_value)) if analista_value else 0}")
                
                return data
                    
            except json.JSONDecodeError:
                print(f"   ❌ Respuesta no es JSON válido")
                print(f"   Primeros 200 caracteres: {response.text[:200]}...")
                return None
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"   ❌ Error al consultar endpoint: {e}")
        return None

def verificar_api_analistas():
    """Verificar el endpoint /api/analistas"""
    print("\n[3] Verificando endpoint /api/analistas...")
    
    session = requests.Session()
    
    # Login rápido
    session.get(f"{BASE_URL}/")
    login_data = {"username": USERNAME, "password": PASSWORD}
    headers = {"X-Requested-With": "XMLHttpRequest", "Content-Type": "application/x-www-form-urlencoded"}
    session.post(f"{BASE_URL}/", data=login_data, headers=headers, allow_redirects=True)
    
    try:
        response = session.get(f"{BASE_URL}/api/analistas")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    analistas = data.get('analistas', [])
                    print(f"   ✅ Status: 200 - {len(analistas)} analistas disponibles")
                    
                    print(f"\n   📋 LISTA COMPLETA DE ANALISTAS:")
                    for i, analista in enumerate(analistas, 1):
                        print(f"      {i}. ID: {analista.get('id_codigo_consumidor')}")
                        print(f"         Nombre: '{analista.get('nombre')}'")
                        print(f"         Cédula: {analista.get('recurso_operativo_cedula')}")
                        print()
                    
                    # Buscar específicamente a ESPITIA BARON LICED JOANA
                    espitia_encontrada = None
                    for analista in analistas:
                        if 'ESPITIA' in analista.get('nombre', '').upper():
                            espitia_encontrada = analista
                            break
                    
                    if espitia_encontrada:
                        print(f"   ✅ ESPITIA BARON LICED JOANA encontrada:")
                        print(f"      ID: {espitia_encontrada.get('id_codigo_consumidor')}")
                        print(f"      Nombre exacto: '{espitia_encontrada.get('nombre')}'")
                        print(f"      Cédula: {espitia_encontrada.get('recurso_operativo_cedula')}")
                    else:
                        print(f"   ❌ ESPITIA BARON LICED JOANA NO encontrada en la lista")
                    
                    return analistas
                else:
                    print(f"   ❌ Error en la respuesta: {data.get('message', 'Sin mensaje')}")
                    return None
                    
            except json.JSONDecodeError:
                print(f"   ❌ Respuesta no es JSON válido")
                print(f"   Primeros 200 caracteres: {response.text[:200]}...")
                return None
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"   ❌ Error al consultar endpoint: {e}")
        return None

def analizar_coincidencia(datos_tecnico, lista_analistas):
    """Analizar por qué no coinciden los datos"""
    print("\n[4] ANÁLISIS DE COINCIDENCIA DE DATOS...")
    
    if not datos_tecnico or not lista_analistas:
        print("   ❌ No hay datos suficientes para analizar")
        return
    
    analista_asignado = datos_tecnico.get('analista')
    print(f"   🔍 Analista asignado al técnico: '{analista_asignado}'")
    
    # Buscar coincidencias exactas
    coincidencia_exacta = None
    coincidencias_parciales = []
    
    for analista in lista_analistas:
        nombre_analista = analista.get('nombre', '')
        
        # Coincidencia exacta
        if nombre_analista == analista_asignado:
            coincidencia_exacta = analista
            break
        
        # Coincidencias parciales
        if analista_asignado and analista_asignado.upper() in nombre_analista.upper():
            coincidencias_parciales.append(analista)
        elif nombre_analista.upper() in (analista_asignado or '').upper():
            coincidencias_parciales.append(analista)
    
    if coincidencia_exacta:
        print(f"   ✅ COINCIDENCIA EXACTA encontrada:")
        print(f"      Nombre en dropdown: '{coincidencia_exacta.get('nombre')}'")
        print(f"      ID: {coincidencia_exacta.get('id_codigo_consumidor')}")
    else:
        print(f"   ❌ NO hay coincidencia exacta")
        
        if coincidencias_parciales:
            print(f"   ⚠️  Coincidencias parciales encontradas:")
            for analista in coincidencias_parciales:
                print(f"      - '{analista.get('nombre')}' (ID: {analista.get('id_codigo_consumidor')})")
        else:
            print(f"   ❌ NO hay coincidencias parciales")
    
    # Análisis de caracteres
    if analista_asignado:
        print(f"\n   🔍 ANÁLISIS DE CARACTERES:")
        print(f"      Analista asignado: '{analista_asignado}'")
        print(f"      Longitud: {len(analista_asignado)}")
        print(f"      Caracteres especiales: {[c for c in analista_asignado if not c.isalnum() and c != ' ']}")
        print(f"      Bytes: {analista_asignado.encode('utf-8')}")

def mostrar_recomendaciones():
    """Mostrar recomendaciones para solucionar el problema"""
    print("\n" + "="*70)
    print("RECOMENDACIONES PARA SOLUCIONAR EL PROBLEMA")
    print("="*70)
    
    print("\n🔧 POSIBLES CAUSAS Y SOLUCIONES:")
    print("   1. COINCIDENCIA DE NOMBRES:")
    print("      - El nombre en la BD puede tener espacios extra o caracteres especiales")
    print("      - Solución: Normalizar nombres en el JavaScript")
    
    print("\n   2. TIMING DE CARGA:")
    print("      - Los analistas se cargan después de los datos del técnico")
    print("      - Solución: Usar callbacks o promesas para sincronizar")
    
    print("\n   3. CASE SENSITIVITY:")
    print("      - Diferencias en mayúsculas/minúsculas")
    print("      - Solución: Comparación case-insensitive")
    
    print("\n   4. FORMATO DE DATOS:")
    print("      - El dropdown espera un formato específico")
    print("      - Solución: Verificar el value vs text del option")

if __name__ == "__main__":
    # Ejecutar debug completo
    datos_tecnico = debug_analista_issue()
    lista_analistas = verificar_api_analistas()
    
    if datos_tecnico and lista_analistas:
        analizar_coincidencia(datos_tecnico, lista_analistas)
    
    mostrar_recomendaciones