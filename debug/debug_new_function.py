#!/usr/bin/env python3
"""
Script para verificar la nueva función de vencimientos
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Importando app...")
    from app import app
    print("✅ App importada exitosamente")
    
    print("\n📋 Buscando rutas de vencimientos:")
    print("=" * 60)
    
    vencimientos_routes = []
    
    for rule in app.url_map.iter_rules():
        if 'vencimiento' in rule.rule.lower():
            route_info = f"{rule.rule} -> {rule.endpoint} ({', '.join(rule.methods)})"
            vencimientos_routes.append(route_info)
            print(f"🎯 {route_info}")
    
    print(f"\n🔍 Verificando funciones en view_functions:")
    for name, func in app.view_functions.items():
        if 'vencimiento' in name.lower():
            print(f"✅ {name}: {func}")
    
    # Probar la función directamente
    print(f"\n🔍 Probando función directamente...")
    try:
        from app import api_vencimientos_consolidados
        print("✅ Función api_vencimientos_consolidados importada")
        
        with app.app_context():
            result = api_vencimientos_consolidados()
            print(f"✅ Resultado: {result.get_json()}")
            
    except ImportError as e:
        print(f"❌ No se pudo importar api_vencimientos_consolidados: {e}")
    except Exception as e:
        print(f"❌ Error al ejecutar api_vencimientos_consolidados: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n🏁 Verificación completada")