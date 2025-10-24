#!/usr/bin/env python3
"""
Script para verificar la importación de app.py y detectar problemas
"""

import sys
import traceback

def debug_app_import():
    """Verificar la importación de app.py"""
    
    print("🔍 Verificando importación de app.py...")
    print("=" * 60)
    
    try:
        # Intentar importar la aplicación Flask
        print("📦 Importando app.py...")
        from app import app
        print("✅ app.py importado correctamente")
        
        # Verificar las rutas registradas
        print(f"\n📋 Total de rutas registradas: {len(list(app.url_map.iter_rules()))}")
        
        # Buscar rutas específicas
        preoperacional_routes = []
        test_routes = []
        
        for rule in app.url_map.iter_rules():
            if 'preoperacional' in rule.rule:
                preoperacional_routes.append(f"   🔗 {rule.rule} -> {rule.endpoint} (métodos: {list(rule.methods)})")
            if 'test' in rule.rule:
                test_routes.append(f"   🔗 {rule.rule} -> {rule.endpoint} (métodos: {list(rule.methods)})")
        
        print(f"\n🎯 Rutas de preoperacional encontradas: {len(preoperacional_routes)}")
        for route in preoperacional_routes:
            print(route)
            
        print(f"\n🧪 Rutas de test encontradas: {len(test_routes)}")
        for route in test_routes:
            print(route)
        
        # Verificar funciones específicas en view_functions
        print(f"\n🔍 Total de view_functions: {len(app.view_functions)}")
        
        target_functions = ['preoperacional', 'test_auth', 'test_simple', 'test_auth_simple']
        for func_name in target_functions:
            if func_name in app.view_functions:
                func = app.view_functions[func_name]
                print(f"   ✅ {func_name}: {func}")
            else:
                print(f"   ❌ {func_name}: NO ENCONTRADA")
        
        # Verificar configuración de Flask-Login
        print(f"\n🔐 Verificando Flask-Login...")
        from flask_login import current_user
        print(f"   ✅ current_user importado: {current_user}")
        
        # Verificar si hay login_manager
        if hasattr(app, 'login_manager'):
            print(f"   ✅ login_manager configurado: {app.login_manager}")
        else:
            print(f"   ❌ login_manager NO configurado")
            
    except ImportError as e:
        print(f"❌ Error importando app.py: {e}")
        traceback.print_exc()
    except SyntaxError as e:
        print(f"❌ Error de sintaxis en app.py: {e}")
        print(f"   Línea {e.lineno}: {e.text}")
        traceback.print_exc()
    except Exception as e:
        print(f"❌ Error general: {e}")
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Verificación completada")

if __name__ == "__main__":
    debug_app_import()