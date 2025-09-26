import requests
import re

# Configuración
BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"
ANALISTAS_URL = f"{BASE_URL}/analistas"

# Credenciales
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def test_frontend_html():
    """Prueba el HTML del frontend del módulo analistas"""
    print("="*60)
    print("PRUEBA DEL FRONTEND HTML - MÓDULO ANALISTAS")
    print("="*60)
    
    # Crear sesión
    session = requests.Session()
    
    print("\n[1] Realizando login...")
    try:
        # Obtener página de login
        session.get(LOGIN_URL)
        
        # Datos de login
        login_data = {
            "username": USERNAME,
            "password": PASSWORD
        }
        
        # Realizar login
        login_response = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        
        if "dashboard" in login_response.url or session.cookies.get('session'):
            print("   ✅ Login exitoso")
        else:
            print("   ❌ Login fallido")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False
    
    print("\n[2] Accediendo al módulo analistas...")
    try:
        response = session.get(ANALISTAS_URL)
        
        if response.status_code == 200:
            print("   ✅ Página cargada correctamente")
            html_content = response.text
        else:
            print(f"   ❌ Error al cargar página: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error al acceder: {e}")
        return False
    
    print("\n[3] Analizando contenido HTML...")
    
    # Verificar elementos clave en el HTML
    elementos_requeridos = [
        (r'id=["\']buscarTexto["\']', "Campo de búsqueda de texto"),
        (r'id=["\']filtroTecnologia["\']', "Filtro de tecnología"),
        (r'id=["\']filtroAgrupacion["\']', "Filtro de agrupación"),
        (r'id=["\']filtroGrupo["\']', "Filtro de grupo"),
        (r'id=["\']btnBuscar["\']', "Botón buscar"),
        (r'id=["\']btnLimpiar["\']', "Botón limpiar"),
        (r'id=["\']tablaCausas["\']', "Tabla de causas"),
        (r'id=["\']tablaCausasBody["\']', "Cuerpo de tabla"),
        (r'id=["\']contadorResultados["\']', "Contador de resultados"),
        (r'analistas\.js', "Archivo JavaScript analistas.js")
    ]
    
    elementos_encontrados = 0
    for patron, descripcion in elementos_requeridos:
        if re.search(patron, html_content, re.IGNORECASE):
            print(f"   ✅ {descripcion} encontrado")
            elementos_encontrados += 1
        else:
            print(f"   ❌ {descripcion} NO encontrado")
    
    print(f"\n   Elementos encontrados: {elementos_encontrados}/{len(elementos_requeridos)}")
    
    print("\n[4] Verificando estructura de la página...")
    
    # Verificar título
    title_match = re.search(r'<h3[^>]*>([^<]+)</h3>', html_content, re.IGNORECASE)
    if title_match and "Causas de Cierre" in title_match.group(1):
        print("   ✅ Título correcto encontrado")
    else:
        print("   ❌ Título no encontrado o incorrecto")
    
    # Verificar formulario de filtros
    if re.search(r'<form[^>]*id=["\']formFiltros["\']', html_content, re.IGNORECASE):
        print("   ✅ Formulario de filtros encontrado")
    else:
        print("   ❌ Formulario de filtros no encontrado")
    
    # Verificar tabla
    if re.search(r'<table[^>]*id=["\']tablaCausas["\']', html_content, re.IGNORECASE):
        print("   ✅ Tabla principal encontrada")
    else:
        print("   ❌ Tabla principal no encontrada")
    
    # Verificar headers de tabla
    headers_esperados = ["Código", "Descripción", "Tecnología", "Agrupación", "Grupo", "Facturable"]
    headers_encontrados = 0
    for header in headers_esperados:
        if header in html_content:
            headers_encontrados += 1
    
    print(f"   ✅ Headers de tabla: {headers_encontrados}/{len(headers_esperados)} encontrados")
    
    print("\n[5] Verificando scripts y estilos...")
    
    # Verificar jQuery
    if "jquery" in html_content.lower():
        print("   ✅ jQuery incluido")
    else:
        print("   ❌ jQuery no encontrado")
    
    # Verificar Bootstrap
    if "bootstrap" in html_content.lower():
        print("   ✅ Bootstrap incluido")
    else:
        print("   ❌ Bootstrap no encontrado")
    
    # Verificar archivo analistas.js
    if "analistas.js" in html_content:
        print("   ✅ Archivo analistas.js referenciado")
    else:
        print("   ❌ Archivo analistas.js no referenciado")
    
    print("\n[6] Verificando inicialización JavaScript...")
    
    # Buscar inicialización del módulo
    if re.search(r'AnalistasModule|analistas.*init', html_content, re.IGNORECASE):
        print("   ✅ Inicialización del módulo encontrada")
    else:
        print("   ❌ Inicialización del módulo no encontrada")
    
    # Verificar document.ready o similar
    if re.search(r'\$\(document\)\.ready|\$\(function|DOMContentLoaded', html_content, re.IGNORECASE):
        print("   ✅ Inicialización DOM encontrada")
    else:
        print("   ❌ Inicialización DOM no encontrada")
    
    print("\n[7] Verificando acceso a archivos estáticos...")
    
    # Probar acceso al archivo analistas.js
    try:
        js_response = session.get(f"{BASE_URL}/static/js/analistas.js")
        if js_response.status_code == 200:
            print("   ✅ Archivo analistas.js accesible")
            
            # Verificar contenido del JS
            js_content = js_response.text
            if "AnalistasModule" in js_content:
                print("   ✅ Clase AnalistasModule encontrada en JS")
            else:
                print("   ❌ Clase AnalistasModule no encontrada en JS")
                
            if "cargarDatos" in js_content:
                print("   ✅ Función cargarDatos encontrada en JS")
            else:
                print("   ❌ Función cargarDatos no encontrada en JS")
                
        else:
            print(f"   ❌ Archivo analistas.js no accesible: Status {js_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error al acceder a analistas.js: {e}")
    
    print("\n[8] Resumen del análisis...")
    
    if elementos_encontrados >= 8:
        print("   ✅ Estructura HTML parece correcta")
    else:
        print("   ❌ Faltan elementos importantes en el HTML")
    
    # Mostrar un fragmento del HTML para diagnóstico
    print("\n[9] Fragmento del HTML (primeros 500 caracteres):")
    print("   " + html_content[:500].replace("\n", "\n   "))
    
    return True

if __name__ == "__main__":
    test_frontend_html()