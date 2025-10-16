#!/usr/bin/env python3
"""
Script para probar directamente las funciones de vencimientos
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Importando app...")
    from app import app
    print("✅ App importada exitosamente")
    
    # Crear contexto de aplicación
    with app.app_context():
        print("\n🔍 Probando función api_get_vencimientos directamente...")
        
        # Intentar importar la función directamente
        try:
            from app import api_get_vencimientos
            print("✅ Función api_get_vencimientos importada")
            
            # Probar la función
            result = api_get_vencimientos()
            print(f"✅ Resultado: {result.get_json()}")
            
        except ImportError as e:
            print(f"❌ No se pudo importar api_get_vencimientos: {e}")
        except Exception as e:
            print(f"❌ Error al ejecutar api_get_vencimientos: {e}")
    
    # Verificar en view_functions
    print(f"\n🔍 Verificando en app.view_functions...")
    if 'api_get_vencimientos' in app.view_functions:
        print(f"✅ api_get_vencimientos está en view_functions")
        func = app.view_functions['api_get_vencimientos']
        print(f"   Función: {func}")
    else:
        print(f"❌ api_get_vencimientos NO está en view_functions")
        print(f"   Funciones disponibles que contienen 'vencimiento':")
        for name, func in app.view_functions.items():
            if 'vencimiento' in name.lower():
                print(f"     - {name}: {func}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n🏁 Prueba completada")