import requests
import re

# Configuración
BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"
ANALISTAS_URL = f"{BASE_URL}/analistas"

# Credenciales
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def test_js_initialization():
    """Prueba la inicialización del módulo JavaScript analistas"""
    print("="*60)
    print("DIAGNÓSTICO FINAL - INICIALIZACIÓN JAVASCRIPT")
    print("="*60)
    
    # Crear sesión
    session = requests.Session()
    
    print("\n[1] Realizando login...")
    try:
        session.get(LOGIN_URL)
        login_data = {"username": USERNAME, "password": PASSWORD}
        login_response = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        
        if "dashboard" in login_response.url or session.cookies.get('session'):
            print("   ✅ Login exitoso")
        else:
            print("   ❌ Login fallido")
            return False
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False
    
    print("\n[2] Analizando HTML del módulo analistas...")
    try:
        response = session.get(ANALISTAS_URL)
        if response.status_code == 200:
            html_content = response.text
            print("   ✅ HTML obtenido correctamente")
        else:
            print(f"   ❌ Error al obtener HTML: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n[3] Verificando inicialización JavaScript en HTML...")
    
    # Buscar patrones de inicialización
    initialization_patterns = [
        (r'\$\(document\)\.ready\(function\(\)\s*\{', "$(document).ready"),
        (r'\$\(function\(\)\s*\{', "$(function()"),
        (r'document\.addEventListener\(["\']DOMContentLoaded["\']', "DOMContentLoaded"),
        (r'new\s+AnalistasModule', "new AnalistasModule"),
        (r'AnalistasModule\s*\(', "AnalistasModule()"),
        (r'analistas\.init', "analistas.init"),
        (r'window\.onload', "window.onload")
    ]
    
    found_patterns = []
    for pattern, description in initialization_patterns:
        if re.search(pattern, html_content, re.IGNORECASE):
            print(f"   ✅ {description} encontrado")
            found_patterns.append(description)
        else:
            print(f"   ❌ {description} no encontrado")
    
    print(f"\n   Patrones de inicialización encontrados: {len(found_patterns)}")
    
    print("\n[4] Analizando archivo analistas.js...")
    try:
        js_response = session.get(f"{BASE_URL}/static/js/analistas.js")
        if js_response.status_code == 200:
            js_content = js_response.text
            print("   ✅ Archivo analistas.js obtenido")
            
            # Verificar estructura del módulo
            js_checks = [
                (r'class\s+AnalistasModule', "Definición de clase AnalistasModule"),
                (r'constructor\s*\(', "Constructor de la clase"),
                (r'init\s*\(', "Método init"),
                (r'cargarDatos\s*\(', "Método cargarDatos"),
                (r'cargarGrupos\s*\(', "Método cargarGrupos"),
                (r'cargarAgrupaciones\s*\(', "Método cargarAgrupaciones"),
                (r'aplicarFiltros\s*\(', "Método aplicarFiltros"),
                (r'/api/analistas/causas-cierre', "URL del endpoint causas-cierre"),
                (r'/api/analistas/grupos', "URL del endpoint grupos"),
                (r'/api/analistas/agrupaciones', "URL del endpoint agrupaciones")
            ]
            
            js_found = 0
            for pattern, description in js_checks:
                if re.search(pattern, js_content, re.IGNORECASE):
                    print(f"   ✅ {description}")
                    js_found += 1
                else:
                    print(f"   ❌ {description} no encontrado")
            
            print(f"\n   Elementos JS encontrados: {js_found}/{len(js_checks)}")
            
        else:
            print(f"   ❌ Error al obtener analistas.js: Status {js_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error al analizar JS: {e}")
        return False
    
    print("\n[5] Verificando inicialización específica en HTML...")
    
    # Buscar la inicialización específica del módulo
    script_sections = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL | re.IGNORECASE)
    
    initialization_found = False
    for i, script in enumerate(script_sections, 1):
        if 'analistas' in script.lower() or 'AnalistasModule' in script:
            print(f"   ✅ Script {i} contiene referencias al módulo analistas")
            print(f"      Contenido: {script.strip()[:200]}...")
            initialization_found = True
    
    if not initialization_found:
        print("   ❌ No se encontró inicialización específica del módulo")
        
        # Buscar al final del HTML
        html_end = html_content[-1000:]  # Últimos 1000 caracteres
        if 'analistas' in html_end.lower():
            print("   ⚠️ Referencias al módulo encontradas al final del HTML")
    
    print("\n[6] Verificando dependencias...")
    
    # Verificar jQuery
    if 'jquery' in html_content.lower():
        print("   ✅ jQuery incluido")
        
        # Verificar versión de jQuery
        jquery_match = re.search(r'jquery[/-](\d+\.\d+\.\d+)', html_content, re.IGNORECASE)
        if jquery_match:
            print(f"   ✅ Versión jQuery: {jquery_match.group(1)}")
    else:
        print("   ❌ jQuery no encontrado")
    
    # Verificar Bootstrap
    if 'bootstrap' in html_content.lower():
        print("   ✅ Bootstrap incluido")
    else:
        print("   ❌ Bootstrap no encontrado")
    
    print("\n[7] Diagnóstico de problemas potenciales...")
    
    problems = []
    solutions = []
    
    # Verificar si hay inicialización
    if len(found_patterns) == 0:
        problems.append("No se encontró inicialización JavaScript")
        solutions.append("Agregar $(document).ready() o similar para inicializar el módulo")
    
    # Verificar si el módulo se instancia
    if not re.search(r'new\s+AnalistasModule|AnalistasModule\s*\(', html_content, re.IGNORECASE):
        problems.append("El módulo AnalistasModule no se instancia")
        solutions.append("Agregar 'const analistas = new AnalistasModule();' en el script")
    
    # Verificar si se llama init
    if not re.search(r'init\s*\(', html_content, re.IGNORECASE):
        problems.append("No se llama al método init del módulo")
        solutions.append("Agregar 'analistas.init();' después de instanciar el módulo")
    
    if problems:
        print("\n   ❌ Problemas encontrados:")
        for i, problem in enumerate(problems, 1):
            print(f"      {i}. {problem}")
        
        print("\n   💡 Soluciones sugeridas:")
        for i, solution in enumerate(solutions, 1):
            print(f"      {i}. {solution}")
    else:
        print("   ✅ No se encontraron problemas obvios")
    
    print("\n[8] Recomendación final...")
    
    if len(found_patterns) > 0 and js_found >= 8:
        print("   ✅ El módulo parece estar correctamente configurado")
        print("   💡 Si los filtros no funcionan, verificar:")
        print("      - Errores en la consola del navegador")
        print("      - Permisos CORS")
        print("      - Autenticación de sesión")
    else:
        print("   ❌ Hay problemas en la configuración del módulo")
        print("   💡 Revisar la inicialización JavaScript en el HTML")
    
    return True

def generate_fix_script():
    """Genera un script de corrección para el HTML"""
    print("\n" + "="*60)
    print("SCRIPT DE CORRECCIÓN SUGERIDO")
    print("="*60)
    
    fix_script = '''
<!-- Agregar al final del HTML, antes de </body> -->
<script>
$(document).ready(function() {
    console.log('Inicializando módulo analistas...');
    
    // Verificar que AnalistasModule esté disponible
    if (typeof AnalistasModule !== 'undefined') {
        try {
            // Instanciar el módulo
            const analistas = new AnalistasModule();
            
            // Inicializar
            analistas.init();
            
            console.log('Módulo analistas inicializado correctamente');
        } catch (error) {
            console.error('Error al inicializar módulo analistas:', error);
        }
    } else {
        console.error('AnalistasModule no está definido. Verificar que analistas.js se haya cargado.');
    }
});
</script>
'''
    
    print(fix_script)
    
    return fix_script

if __name__ == "__main__":
    test_js_initialization()
    generate_fix_script()