#!/usr/bin/env python3
import sys
import os

print("=== Diagnóstico de main.py ===")

try:
    # Importar main
    import main
    print("✓ main.py importado exitosamente")
    
    # Verificar si hay una instancia de Flask
    if hasattr(main, 'app'):
        app = main.app
        print(f"✓ Instancia Flask encontrada: {app}")
        
        # Listar todas las rutas registradas
        print("\n=== Rutas registradas ===")
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(str(rule))
        
        print(f"Total de rutas: {len(routes)}")
        
        # Buscar rutas críticas
        critical_routes = ['/login', '/dashboard', '/mpa', '/lider', '/logistica/automotor']
        print("\n=== Verificación de rutas críticas ===")
        for route in critical_routes:
            found = any(route in r for r in routes)
            status = "✓" if found else "✗"
            print(f"{status} {route}")
        
        # Mostrar todas las rutas
        print("\n=== Todas las rutas ===")
        for route in sorted(routes):
            print(f"  {route}")
            
        # Verificar configuración
        print(f"\n=== Configuración ===")
        print(f"Debug mode: {app.debug}")
        print(f"Secret key configured: {'SECRET_KEY' in app.config}")
        
        # Verificar blueprints
        print(f"Blueprints registrados: {len(app.blueprints)}")
        for name, bp in app.blueprints.items():
            print(f"  - {name}: {bp}")
            
    else:
        print("✗ No se encontró instancia Flask en main.py")
        
except Exception as e:
    print(f"✗ Error al importar main.py: {e}")
    import traceback
    traceback.print_exc()