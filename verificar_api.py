import requests
import json
from datetime import datetime, timedelta
import sys

# Configuración
BASE_URL = "http://localhost:8080"
API_URL = f"{BASE_URL}/api/indicadores/cumplimiento"
INDICADORES_PAGE_URL = f"{BASE_URL}/indicadores/api"
LOGIN_URL = f"{BASE_URL}/"  # La ruta de login es la raíz

# Configuración de credenciales
USERNAME = "admin"  # Reemplazar con usuario válido
PASSWORD = "admin"  # Reemplazar con contraseña válida

# Función para iniciar sesión
def iniciar_sesion(username=USERNAME, password=PASSWORD):
    print(f"\n{'='*50}")
    print(f"Iniciando sesión con usuario: {username}")
    print(f"{'='*50}")
    
    # Crear sesión
    session = requests.Session()
    
    try:
        # Obtener página de login para cookies iniciales
        session.get(BASE_URL)
        
        # Preparar datos de login
        login_data = {
            "username": username,
            "password": password
        }
        
        # Intentar login
        response = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        
        print(f"Código de respuesta: {response.status_code}")
        print(f"URL después de login: {response.url}")
        print(f"Cookies de sesión: {session.cookies}")
        
        # Verificar si el login fue exitoso
        if "dashboard" in response.url or "/home" in response.url or response.status_code == 200:
            # Si tenemos una sesión de cookies, probablemente funcionó
            if session.cookies:
                print("✓ Login exitoso!")
                return session
        
        print("✗ Login fallido. Redirigido a:", response.url)
        print(f"Contenido de respuesta (primeros 200 caracteres):\n{response.text[:200]}...")
        return None
    
    except Exception as e:
        print(f"✗ Error durante el login: {e}")
        return None

# Función para probar la API directamente
def probar_api_directa(session, fecha_inicio="2025-03-17", fecha_fin="2025-03-17", supervisor=None):
    print(f"\n\n{'='*50}")
    print(f"Probando API directamente con fechas: {fecha_inicio} a {fecha_fin}")
    print(f"{'='*50}")
    
    # Construir parámetros
    params = {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin
    }
    
    if supervisor:
        params["supervisor"] = supervisor
    
    try:
        # Añadir cabeceras para simular una petición AJAX
        headers = {
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        print(f"URL a consultar: {API_URL}")
        print(f"Parámetros: {params}")
        print(f"Cabeceras: {headers}")
        
        # Realizar petición
        response = session.get(API_URL, params=params, headers=headers)
        
        # Mostrar detalles de la respuesta
        print(f"\nCódigo de respuesta: {response.status_code}")
        print(f"Cabeceras de respuesta: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"ERROR: La API retornó un código de error {response.status_code}")
            print(f"Contenido: {response.text[:500]}...")
            return False
        
        # Intentar analizar como JSON
        try:
            datos = response.json()
            print("\nRespuesta JSON válida")
            
            # Verificar estructura y datos
            if not datos.get("success", False):
                print(f"ERROR: La API reporta error: {datos.get('error', 'No especificado')}")
                return False
            
            # Verificar indicadores
            indicadores = datos.get("indicadores", [])
            print(f"\nSe encontraron {len(indicadores)} indicadores")
            
            # Mostrar resultados
            for i, indicador in enumerate(indicadores, 1):
                print(f"\nIndicador #{i}:")
                print(f"  Supervisor: {indicador.get('supervisor', 'No especificado')}")
                print(f"  Asistencia: {indicador.get('total_asistencia', 0)}")
                print(f"  Preoperacional: {indicador.get('total_preoperacional', 0)}")
                print(f"  Cumplimiento: {indicador.get('porcentaje_cumplimiento', 0)}%")
            
            return len(indicadores) > 0
                
        except json.JSONDecodeError as e:
            print(f"ERROR: No se pudo analizar la respuesta como JSON: {e}")
            print(f"Contenido recibido (primeros 500 caracteres):\n{response.text[:500]}...")
            return False
    
    except Exception as e:
        print(f"ERROR de conexión: {e}")
        return False

# Función para probar la página web
def probar_pagina_web(session):
    print(f"\n\n{'='*50}")
    print(f"Probando página web en: {INDICADORES_PAGE_URL}")
    print(f"{'='*50}")
    
    try:
        response = session.get(INDICADORES_PAGE_URL)
        print(f"Código de respuesta: {response.status_code}")
        
        if response.status_code != 200:
            print(f"ERROR: La página retornó código {response.status_code}")
            return False
        
        # Buscar elementos clave en el HTML
        html = response.text
        checks = [
            ("Contenedor principal", "#indicadores-container", "id='indicadores-container'" in html),
            ("Sección de indicadores", "#indicadores-seccion", "id='indicadores-seccion'" in html),
            ("Formulario de filtros", "#filtrosForm", "id='filtrosForm'" in html),
            ("Botón de recarga", "#recargar-indicadores", "id='recargar-indicadores'" in html),
        ]
        
        print("\nVerificando elementos HTML críticos:")
        todas_ok = True
        for nombre, selector, existe in checks:
            print(f"  {nombre} ({selector}): {'✓ Encontrado' if existe else '✗ NO ENCONTRADO'}")
            todas_ok = todas_ok and existe
        
        return todas_ok
    
    except Exception as e:
        print(f"ERROR al acceder a la página: {e}")
        return False

# Función principal
def main():
    print("VERIFICACIÓN DE API Y PÁGINA DE INDICADORES")
    print("===========================================")
    print(f"Fecha y hora actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Obtener credenciales desde la línea de comandos si se proporcionan
    if len(sys.argv) >= 3:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        username = USERNAME
        password = PASSWORD
        print(f"Usando credenciales por defecto. Para cambiar: python {sys.argv[0]} USUARIO CONTRASEÑA")
    
    # Iniciar sesión
    session = iniciar_sesion(username, password)
    
    if not session:
        print("\n✗ No se pudo iniciar sesión. Verificación cancelada.")
        return
    
    # Probar con diferentes fechas
    fechas_a_probar = [
        ("2025-03-17", "2025-03-17"),
        ("2025-03-16", "2025-03-16"),
        ("2025-03-10", "2025-03-10")
    ]
    
    resultados_api = []
    for fecha_inicio, fecha_fin in fechas_a_probar:
        resultado = probar_api_directa(session, fecha_inicio, fecha_fin)
        resultados_api.append(resultado)
    
    # Probar la página web
    resultado_web = probar_pagina_web(session)
    
    # Resumen final
    print("\n\nRESUMEN DE VERIFICACIÓN")
    print("=======================")
    print(f"Login: ✓ EXITOSO")
    print(f"API: {'✓ FUNCIONANDO' if any(resultados_api) else '✗ NO FUNCIONA'}")
    print(f"Página Web: {'✓ FUNCIONANDO' if resultado_web else '✗ POSIBLES PROBLEMAS'}")
    
    print("\nRecomendaciones:")
    if not any(resultados_api):
        print("- Verificar que el endpoint de API esté correctamente implementado")
        print("- Revisar registros del servidor para detectar errores")
    
    if not resultado_web:
        print("- Verificar que la estructura HTML contiene los elementos necesarios")
        print("- Revisar consola del navegador (F12) para detectar errores JavaScript")
    
    if any(resultados_api) and not resultado_web:
        print("- La API funciona pero la página tiene problemas. Revisa la implementación JavaScript")
        print("- Verifica que las URLs utilizadas en JavaScript sean correctas")

if __name__ == "__main__":
    main() 