#!/usr/bin/env python3
"""
Script para debuggear las rutas registradas en Flask
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar la aplicación
from app import app

def debug_routes():
    print('=== RUTAS REGISTRADAS EN FLASK ===')
    
    # Obtener todas las rutas registradas
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': rule.rule
        })
    
    # Filtrar rutas relacionadas con preoperacional
    preop_routes = [r for r in routes if 'preoperacional' in r['rule'].lower()]
    
    print(f'Total de rutas registradas: {len(routes)}')
    print(f'Rutas relacionadas con preoperacional: {len(preop_routes)}')
    
    print('\n=== RUTAS DE PREOPERACIONAL ===')
    for route in preop_routes:
        print(f"  Endpoint: {route['endpoint']}")
        print(f"  Métodos: {route['methods']}")
        print(f"  Ruta: {route['rule']}")
        print(f"  ---")
    
    # Buscar específicamente la ruta /preoperacional POST
    post_preop = [r for r in routes if r['rule'] == '/preoperacional' and 'POST' in r['methods']]
    
    print(f'\n=== RUTA /preoperacional POST ===')
    if post_preop:
        for route in post_preop:
            print(f"  Endpoint: {route['endpoint']}")
            print(f"  Métodos: {route['methods']}")
            print(f"  Ruta: {route['rule']}")
            
            # Intentar obtener información sobre la función
            try:
                view_func = app.view_functions.get(route['endpoint'])
                if view_func:
                    print(f"  Función: {view_func.__name__}")
                    print(f"  Módulo: {view_func.__module__}")
                    print(f"  Archivo: {view_func.__code__.co_filename}")
                    print(f"  Línea: {view_func.__code__.co_firstlineno}")
            except Exception as e:
                print(f"  Error obteniendo info de función: {e}")
    else:
        print("  ❌ No se encontró la ruta /preoperacional POST")

if __name__ == "__main__":
    debug_routes()