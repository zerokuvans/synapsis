#!/usr/bin/env python3
"""
Script para diagnosticar el estado de la aplicación Flask
"""

import sys
import traceback

def diagnose_flask_app():
    try:
        print("=== DIAGNÓSTICO DE LA APLICACIÓN FLASK ===\n")
        
        # Intentar importar la aplicación
        print("1. Importando app.py...")
        try:
            from app import app
            print("✓ app.py importado exitosamente")
        except Exception as e:
            print(f"✗ Error al importar app.py: {e}")
            traceback.print_exc()
            return
        
        # Verificar que la app sea una instancia de Flask
        print("\n2. Verificando instancia de Flask...")
        from flask import Flask
        if isinstance(app, Flask):
            print("✓ app es una instancia válida de Flask")
        else:
            print(f"✗ app no es una instancia de Flask: {type(app)}")
            return
        
        # Listar todas las rutas registradas
        print("\n3. Rutas registradas en la aplicación:")
        print("-" * 50)
        
        routes_found = []
        for rule in app.url_map.iter_rules():
            routes_found.append({
                'rule': str(rule),
                'endpoint': rule.endpoint,
                'methods': list(rule.methods)
            })
        
        if routes_found:
            for route in sorted(routes_found, key=lambda x: x['rule']):
                print(f"Ruta: {route['rule']}")
                print(f"  Endpoint: {route['endpoint']}")
                print(f"  Métodos: {route['methods']}")
                print()
        else:
            print("✗ No se encontraron rutas registradas")
        
        # Verificar rutas específicas críticas
        print("\n4. Verificando rutas críticas:")
        critical_routes = ['/login', '/dashboard', '/lider', '/mpa', '/logistica/automotor']
        
        for route in critical_routes:
            found = any(r['rule'] == route for r in routes_found)
            status = "✓" if found else "✗"
            print(f"{status} {route}")
        
        # Verificar configuración de la app
        print("\n5. Configuración de la aplicación:")
        print(f"Debug mode: {app.debug}")
        print(f"Testing: {app.testing}")
        print(f"Secret key configurado: {'Sí' if app.secret_key else 'No'}")
        
        # Verificar blueprints
        print("\n6. Blueprints registrados:")
        if app.blueprints:
            for name, blueprint in app.blueprints.items():
                print(f"  - {name}: {blueprint}")
        else:
            print("  No hay blueprints registrados")
        
        print(f"\n=== TOTAL DE RUTAS ENCONTRADAS: {len(routes_found)} ===")
        
    except Exception as e:
        print(f"Error durante el diagnóstico: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_flask_app()