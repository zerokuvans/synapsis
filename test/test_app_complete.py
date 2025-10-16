#!/usr/bin/env python3
"""
Script completo para probar todas las rutas de la aplicación Flask
"""

import requests
import sys
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8080"

def test_route(route, description):
    """Prueba una ruta específica y retorna el resultado"""
    try:
        url = f"{BASE_URL}{route}"
        response = requests.get(url, timeout=10, allow_redirects=False)
        
        status_icon = "✅" if response.status_code in [200, 302] else "❌"
        redirect_info = ""
        
        if response.status_code == 302:
            location = response.headers.get('Location', 'Unknown')
            redirect_info = f" → {location}"
        
        print(f"{status_icon} {route:<25} | Status: {response.status_code:<3} | {description}{redirect_info}")
        return response.status_code in [200, 302]
        
    except requests.exceptions.ConnectionError:
        print(f"❌ {route:<25} | ERROR: No se puede conectar al servidor")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {route:<25} | ERROR: Timeout")
        return False
    except Exception as e:
        print(f"❌ {route:<25} | ERROR: {str(e)}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 PRUEBA COMPLETA DE LA APLICACIÓN FLASK")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL Base: {BASE_URL}")
    print("=" * 80)
    
    # Rutas básicas
    print("\n📋 RUTAS BÁSICAS:")
    basic_routes = [
        ("/", "Página principal"),
        ("/login", "Página de login"),
        ("/logout", "Logout"),
        ("/dashboard", "Dashboard principal"),
        ("/register", "Registro de usuarios")
    ]
    
    basic_success = 0
    for route, desc in basic_routes:
        if test_route(route, desc):
            basic_success += 1
    
    # Rutas de módulos principales
    print("\n🏢 MÓDULOS PRINCIPALES:")
    module_routes = [
        ("/administrativo", "Módulo Administrativo"),
        ("/operativo", "Módulo Operativo"),
        ("/tecnicos", "Módulo Técnicos"),
        ("/lider", "Módulo Líder"),
        ("/logistica", "Módulo Logística"),
        ("/sstt", "Módulo SSTT"),
        ("/analistas", "Módulo Analistas")
    ]
    
    module_success = 0
    for route, desc in module_routes:
        if test_route(route, desc):
            module_success += 1
    
    # Rutas MPA
    print("\n🚗 MÓDULO MPA (Parque Automotor):")
    mpa_routes = [
        ("/mpa", "Dashboard MPA"),
        ("/mpa/vehiculos", "Gestión de Vehículos"),
        ("/mpa/vencimientos", "Gestión de Vencimientos"),
        ("/mpa/soat", "Gestión de SOAT"),
        ("/mpa/tecnico-mecanica", "Revisión Técnico Mecánica"),
        ("/mpa/licencias", "Gestión de Licencias"),
        ("/mpa/inspecciones", "Inspecciones Vehiculares"),
        ("/mpa/siniestros", "Gestión de Siniestros"),
        ("/mpa/mantenimientos", "Gestión de Mantenimientos")
    ]
    
    mpa_success = 0
    for route, desc in mpa_routes:
        if test_route(route, desc):
            mpa_success += 1
    
    # APIs importantes
    print("\n🔌 APIs IMPORTANTES:")
    api_routes = [
        ("/api/mpa/dashboard-stats", "API Estadísticas MPA"),
        ("/api/supervisores", "API Supervisores"),
        ("/api/tecnicos_por_supervisor", "API Técnicos por Supervisor")
    ]
    
    api_success = 0
    for route, desc in api_routes:
        if test_route(route, desc):
            api_success += 1
    
    # Resumen final
    total_routes = len(basic_routes) + len(module_routes) + len(mpa_routes) + len(api_routes)
    total_success = basic_success + module_success + mpa_success + api_success
    
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE RESULTADOS:")
    print("=" * 80)
    print(f"Rutas Básicas:        {basic_success}/{len(basic_routes)} funcionando")
    print(f"Módulos Principales:  {module_success}/{len(module_routes)} funcionando")
    print(f"Módulo MPA:          {mpa_success}/{len(mpa_routes)} funcionando")
    print(f"APIs:                {api_success}/{len(api_routes)} funcionando")
    print("-" * 40)
    print(f"TOTAL:               {total_success}/{total_routes} rutas funcionando")
    
    success_rate = (total_success / total_routes) * 100
    print(f"Tasa de éxito:       {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 ¡APLICACIÓN FUNCIONANDO CORRECTAMENTE!")
    elif success_rate >= 70:
        print("\n⚠️  APLICACIÓN FUNCIONANDO CON ALGUNOS PROBLEMAS")
    else:
        print("\n❌ APLICACIÓN CON PROBLEMAS GRAVES")
    
    print("\n💡 NOTAS:")
    print("- Status 200: Página carga correctamente")
    print("- Status 302: Redirección (normal para rutas protegidas)")
    print("- Status 404: Ruta no encontrada")
    print("- Status 500: Error del servidor")

if __name__ == "__main__":
    main()