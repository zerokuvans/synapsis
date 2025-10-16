#!/usr/bin/env python3
"""
Script para verificar la importación y registro de funciones en app.py
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_app_import():
    """Verificar la importación de app.py y las funciones registradas"""
    
    print("🔍 Verificando importación de app.py...")
    print("=" * 60)
    
    try:
        # Importar la aplicación Flask
        from app import app
        print("✅ app.py importado correctamente")
        
        # Verificar las rutas registradas
        print("\n📋 Rutas registradas en la aplicación:")
        for rule in app.url_map.iter_rules():
            if 'vencimientos' in rule.rule:
                print(f"   🔗 {rule.rule} -> {rule.endpoint} (métodos: {list(rule.methods)})")
        
        # Verificar funciones específicas en view_functions
        print("\n🔍 Verificando funciones en view_functions:")
        vencimientos_functions = [
            'api_vencimientos_consolidados',
            'api_test_vencimientos',
            'mpa_vencimientos'
        ]
        
        for func_name in vencimientos_functions:
            if func_name in app.view_functions:
                func = app.view_functions[func_name]
                print(f"   ✅ {func_name}: {func}")
            else:
                print(f"   ❌ {func_name}: NO ENCONTRADA")
        
        # Intentar ejecutar las funciones directamente
        print("\n🧪 Probando ejecución directa de funciones:")
        
        try:
            from app import api_vencimientos_consolidados
            print("   ✅ api_vencimientos_consolidados importada")
            
            # Crear un contexto de aplicación para la prueba
            with app.app_context():
                result = api_vencimientos_consolidados()
                print(f"   ✅ Función ejecutada: {result.get_json()}")
                
        except ImportError as e:
            print(f"   ❌ Error importando api_vencimientos_consolidados: {e}")
        except Exception as e:
            print(f"   ❌ Error ejecutando api_vencimientos_consolidados: {e}")
        
        try:
            from app import api_test_vencimientos
            print("   ✅ api_test_vencimientos importada")
            
            with app.app_context():
                result = api_test_vencimientos()
                print(f"   ✅ Función ejecutada: {result.get_json()}")
                
        except ImportError as e:
            print(f"   ❌ Error importando api_test_vencimientos: {e}")
        except Exception as e:
            print(f"   ❌ Error ejecutando api_test_vencimientos: {e}")
        
        # Verificar si hay errores de sintaxis en el archivo
        print("\n🔍 Verificando sintaxis del archivo app.py...")
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            compile(content, 'app.py', 'exec')
            print("   ✅ Sintaxis correcta en app.py")
            
        except SyntaxError as e:
            print(f"   ❌ Error de sintaxis en app.py: {e}")
            print(f"      Línea {e.lineno}: {e.text}")
        
    except ImportError as e:
        print(f"❌ Error importando app.py: {e}")
    except Exception as e:
        print(f"❌ Error general: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Verificación completada")

if __name__ == "__main__":
    debug_app_import()