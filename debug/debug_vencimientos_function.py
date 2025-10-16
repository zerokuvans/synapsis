#!/usr/bin/env python3
"""
Script para debuggear las funciones de vencimientos directamente
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
        print("\n🔍 Probando función api_get_vencimientos...")
        
        try:
            # Importar la función directamente
            from app import api_get_vencimientos
            
            print("✅ Función importada, ejecutando...")
            result = api_get_vencimientos()
            print(f"✅ Función ejecutada exitosamente")
            print(f"📊 Tipo de resultado: {type(result)}")
            
            # Si es una respuesta de Flask, obtener los datos
            if hasattr(result, 'get_json'):
                data = result.get_json()
                print(f"📊 Datos JSON: {len(data) if isinstance(data, list) else 'No es lista'}")
            elif hasattr(result, 'data'):
                print(f"📊 Datos raw: {len(str(result.data))} caracteres")
            else:
                print(f"📊 Resultado directo: {result}")
                
        except Exception as e:
            print(f"❌ Error en api_get_vencimientos: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n🔍 Probando función api_get_vencimiento_detalle...")
        
        try:
            from app import api_get_vencimiento_detalle
            
            print("✅ Función importada, probando con parámetros de prueba...")
            # Probar con parámetros de ejemplo
            result = api_get_vencimiento_detalle('soat', 1)
            print(f"✅ Función ejecutada exitosamente")
            print(f"📊 Tipo de resultado: {type(result)}")
            
        except Exception as e:
            print(f"❌ Error en api_get_vencimiento_detalle: {e}")
            import traceback
            traceback.print_exc()

except ImportError as e:
    print(f"❌ Error al importar app: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    import traceback
    traceback.print_exc()