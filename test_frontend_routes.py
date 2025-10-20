#!/usr/bin/env python3
"""
Script para verificar que las nuevas rutas del frontend MPA funcionen correctamente
"""

import requests
import time

BASE_URL = "http://127.0.0.1:8080"

def test_frontend_route(route_path, route_name):
    """Prueba una ruta del frontend"""
    try:
        print(f"\n🔍 Probando {route_name}: {route_path}")
        
        response = requests.get(f"{BASE_URL}{route_path}", timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {route_name}: OK (200)")
            return True
        elif response.status_code == 302:
            print(f"🔄 {route_name}: Redirección (302) - probablemente requiere login")
            return True
        elif response.status_code == 401:
            print(f"🔐 {route_name}: No autorizado (401) - requiere autenticación")
            return True
        elif response.status_code == 403:
            print(f"🚫 {route_name}: Prohibido (403) - sin permisos")
            return True
        else:
            print(f"❌ {route_name}: Error {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {route_name}: Error de conexión - servidor no disponible")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {route_name}: Timeout")
        return False
    except Exception as e:
        print(f"❌ {route_name}: Error inesperado - {str(e)}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de rutas del frontend MPA...")
    print("=" * 60)
    
    # Verificar que el servidor esté funcionando
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Servidor disponible en {BASE_URL}")
    except:
        print(f"❌ Servidor no disponible en {BASE_URL}")
        return
    
    # Rutas del frontend a probar
    frontend_routes = [
        ("/mpa", "Dashboard MPA"),
        ("/mpa/historial", "Historial Consolidado"),
        ("/mpa/reportes-sincronizacion", "Reportes de Sincronización"),
        ("/mpa/validaciones", "Validaciones de Documentos"),
        ("/mpa/configuracion", "Configuración MPA"),
        ("/mpa/vehiculos", "Gestión de Vehículos"),
        ("/mpa/soat", "Gestión de SOAT"),
        ("/mpa/tecnico-mecanica", "Gestión de Tecnomecánica"),
        ("/mpa/licencias-conducir", "Gestión de Licencias")
    ]
    
    print(f"\n📋 Probando {len(frontend_routes)} rutas del frontend...")
    
    successful_routes = 0
    for route, name in frontend_routes:
        if test_frontend_route(route, name):
            successful_routes += 1
        time.sleep(0.5)  # Pequeña pausa entre requests
    
    print("\n" + "=" * 60)
    print(f"📊 Resumen de pruebas del frontend:")
    print(f"   ✅ Rutas exitosas: {successful_routes}/{len(frontend_routes)}")
    print(f"   ❌ Rutas fallidas: {len(frontend_routes) - successful_routes}/{len(frontend_routes)}")
    
    if successful_routes == len(frontend_routes):
        print("🎉 ¡Todas las rutas del frontend están funcionando correctamente!")
    else:
        print("⚠️  Algunas rutas del frontend tienen problemas")
    
    print("\n💡 Nota: Las rutas que devuelven 302, 401 o 403 son normales")
    print("   ya que requieren autenticación y permisos administrativos.")

if __name__ == "__main__":
    main()