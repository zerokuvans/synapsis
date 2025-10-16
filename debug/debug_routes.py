#!/usr/bin/env python3
"""
Script para debuggear las rutas registradas en Flask
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Importando app...")
    from app import app
    print("✅ App importada exitosamente")
    
    print("\n🔍 Verificando rutas registradas...")
    
    # Buscar rutas relacionadas con vencimientos
    vencimientos_routes = []
    all_routes = []
    
    for rule in app.url_map.iter_rules():
        route_info = {
            'rule': str(rule),
            'endpoint': rule.endpoint,
            'methods': list(rule.methods)
        }
        all_routes.append(route_info)
        
        if 'vencimiento' in str(rule).lower():
            vencimientos_routes.append(route_info)
    
    print(f"📊 Total de rutas registradas: {len(all_routes)}")
    print(f"📊 Rutas de vencimientos encontradas: {len(vencimientos_routes)}")
    
    if vencimientos_routes:
        print("\n✅ Rutas de vencimientos registradas:")
        for route in vencimientos_routes:
            print(f"  - {route['rule']} [{', '.join(route['methods'])}] -> {route['endpoint']}")
    else:
        print("\n❌ No se encontraron rutas de vencimientos")
        
        # Mostrar algunas rutas de MPA para comparar
        print("\n🔍 Rutas de MPA encontradas:")
        mpa_routes = [r for r in all_routes if '/mpa/' in r['rule']]
        for route in mpa_routes[:10]:  # Mostrar solo las primeras 10
            print(f"  - {route['rule']} [{', '.join(route['methods'])}] -> {route['endpoint']}")
        
        if len(mpa_routes) > 10:
            print(f"  ... y {len(mpa_routes) - 10} más")
    
    # Verificar si las funciones existen
    print("\n🔍 Verificando funciones de vencimientos...")
    
    functions_to_check = [
        'api_get_vencimientos',
        'api_get_vencimiento_detalle'
    ]
    
    for func_name in functions_to_check:
        if hasattr(app, 'view_functions') and func_name in app.view_functions:
            print(f"✅ Función {func_name} registrada")
        else:
            print(f"❌ Función {func_name} NO registrada")
    
except ImportError as e:
    print(f"❌ Error al importar app: {e}")
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    import traceback
    traceback.print_exc()