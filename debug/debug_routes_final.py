#!/usr/bin/env python3
"""
Script para verificar las rutas registradas en Flask después de los cambios
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Importando app...")
    from app import app
    print("✅ App importada exitosamente")
    
    print("\n📋 Rutas registradas en Flask:")
    print("=" * 60)
    
    vencimientos_routes = []
    total_routes = 0
    
    for rule in app.url_map.iter_rules():
        total_routes += 1
        route_info = f"{rule.rule} -> {rule.endpoint} ({', '.join(rule.methods)})"
        
        if 'vencimiento' in rule.rule.lower():
            vencimientos_routes.append(route_info)
            print(f"🎯 {route_info}")
        elif total_routes <= 10:  # Mostrar solo las primeras 10 rutas para referencia
            print(f"   {route_info}")
    
    print(f"\n📊 Resumen:")
    print(f"   Total de rutas: {total_routes}")
    print(f"   Rutas de vencimientos: {len(vencimientos_routes)}")
    
    if vencimientos_routes:
        print(f"\n✅ Rutas de vencimientos encontradas:")
        for route in vencimientos_routes:
            print(f"   - {route}")
    else:
        print(f"\n❌ No se encontraron rutas de vencimientos")
    
    # Verificar si la función existe
    print(f"\n🔍 Verificando funciones:")
    if hasattr(app.view_functions, 'api_get_vencimientos'):
        print(f"✅ Función api_get_vencimientos existe")
    else:
        print(f"❌ Función api_get_vencimientos NO existe")
    
    if hasattr(app.view_functions, 'api_get_vencimiento_detalle'):
        print(f"✅ Función api_get_vencimiento_detalle existe")
    else:
        print(f"❌ Función api_get_vencimiento_detalle NO existe")

except Exception as e:
    print(f"❌ Error al importar o verificar: {e}")
    import traceback
    traceback.print_exc()

print(f"\n🏁 Verificación completada")