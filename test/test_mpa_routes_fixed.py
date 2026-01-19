#!/usr/bin/env python3
"""
Script para verificar que las rutas MPA funcionen correctamente después del fix
"""

import requests
import time

BASE_URL = "http://127.0.0.1:8080"

def test_mpa_route(route_path, route_name):
    """Prueba una ruta MPA específica"""
    try:
        url = f"{BASE_URL}{route_path}"
        response = requests.get(url, timeout=10)
        
        print(f"🔍 Probando {route_name} ({route_path}):")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ FUNCIONANDO - Contenido: {len(response.text)} caracteres")
            return True
        elif response.status_code == 302:
            print(f"   ✅ REDIRIGIENDO (requiere autenticación)")
            return True
        elif response.status_code == 500:
            print(f"   ❌ ERROR 500 - Problema en el servidor")
            return False
        else:
            print(f"   ⚠️  Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🔧 VERIFICACIÓN DE RUTAS MPA DESPUÉS DEL FIX")
    print("=" * 60)
    
    # Esperar un momento para que el servidor esté completamente listo
    print("⏳ Esperando que el servidor esté listo...")
    time.sleep(2)
    
    # Rutas MPA que estaban fallando
    routes_to_test = [
        ("/mpa", "Dashboard MPA"),
        ("/mpa/vehiculos", "Vehículos MPA"),
        ("/mpa/mantenimientos", "Mantenimientos MPA"),
        ("/mpa/inspecciones", "Inspecciones MPA"),
        ("/mpa/licencias", "Licencias MPA"),
        ("/mpa/vencimientos", "Vencimientos MPA"),
        ("/mpa/kit-carretera", "Kit de Carretera (principal)"),
        ("/mpa/kitcarretera", "Kit de Carretera (alias sin guión)"),
        ("/mpa/kit-carretera/", "Kit de Carretera (con slash final)"),
        ("/api/mpa/dashboard-stats", "API Dashboard Stats")
    ]
    
    results = []
    
    for route_path, route_name in routes_to_test:
        success = test_mpa_route(route_path, route_name)
        results.append((route_name, success))
        print()  # Línea en blanco para separar
    
    # Resumen
    print("=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN:")
    print("=" * 60)
    
    successful = 0
    total = len(results)
    
    for route_name, success in results:
        icon = "✅" if success else "❌"
        print(f"{icon} {route_name}")
        if success:
            successful += 1
    
    print(f"\nTotal: {successful}/{total} rutas funcionando")
    
    if successful == total:
        print("\n🎉 ¡TODAS LAS RUTAS MPA FUNCIONAN CORRECTAMENTE!")
        print("✅ El problema del flash ha sido resuelto")
    else:
        print(f"\n⚠️  {total - successful} rutas aún tienen problemas")

if __name__ == "__main__":
    main()
