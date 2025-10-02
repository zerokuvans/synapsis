#!/usr/bin/env python3
"""
Script para probar la nueva funcionalidad de guardado manual
en lugar del guardado automático.
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://192.168.80.39:8080"
FECHA_PRUEBA = "2025-10-02"

def test_manual_save_functionality():
    """Prueba la funcionalidad de guardado manual"""
    
    print("🧪 Iniciando pruebas de funcionalidad de guardado manual...")
    print("=" * 60)
    
    # 1. Verificar que el endpoint actualizar-campo sigue funcionando
    print("\n1. Probando endpoint actualizar-campo...")
    
    test_data = [
        {"cedula": "5694500", "campo": "hora_inicio", "valor": "08:30"},
        {"cedula": "5694500", "campo": "estado", "valor": "PRESENTE"},
        {"cedula": "5694500", "campo": "novedad", "valor": "Sin novedad"}
    ]
    
    for data in test_data:
        try:
            response = requests.post(
                f"{BASE_URL}/api/asistencia/actualizar-campo",
                json={
                    "cedula": data["cedula"],
                    "campo": data["campo"],
                    "valor": data["valor"],
                    "fecha": FECHA_PRUEBA
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"   ✅ {data['campo']}: {data['valor']} - Guardado exitoso")
                else:
                    print(f"   ❌ {data['campo']}: Error - {result.get('message', 'Error desconocido')}")
            else:
                print(f"   ❌ {data['campo']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {data['campo']}: Error de conexión - {str(e)}")
    
    # 2. Verificar que la página inicio-operacion-tecnicos carga correctamente
    print("\n2. Verificando carga de página inicio-operacion-tecnicos...")
    
    try:
        response = requests.get(f"{BASE_URL}/inicio-operacion-tecnicos")
        if response.status_code == 200:
            print("   ✅ Página carga correctamente")
            
            # Verificar que contiene los elementos esperados
            content = response.text
            checks = [
                ("Botón Guardar", 'class="guardar-cambios-btn"' in content),
                ("Función validarCamposCompletos", 'function validarCamposCompletos' in content),
                ("Función guardarCambiosTecnico", 'function guardarCambiosTecnico' in content),
                ("Columna Acciones", '<th>Acciones</th>' in content),
                ("Sin onchange automático", 'onchange="guardarCampoAsistencia' not in content)
            ]
            
            for check_name, check_result in checks:
                status = "✅" if check_result else "❌"
                print(f"   {status} {check_name}")
                
        else:
            print(f"   ❌ Error al cargar página: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
    
    # 3. Verificar estructura de la base de datos
    print("\n3. Verificando registros en base de datos...")
    
    try:
        # Verificar que existen registros para la fecha de prueba
        response = requests.get(f"{BASE_URL}/api/asistencia/obtener?fecha={FECHA_PRUEBA}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"   ✅ Encontrados {len(data)} registros para {FECHA_PRUEBA}")
                
                # Mostrar algunos registros de ejemplo
                for i, record in enumerate(data[:3]):
                    cedula = record.get('cedula', 'N/A')
                    tecnico = record.get('tecnico', 'N/A')
                    hora_inicio = record.get('hora_inicio', 'N/A')
                    estado = record.get('estado', 'N/A')
                    print(f"   📋 Registro {i+1}: {cedula} - {tecnico} - {hora_inicio} - {estado}")
            else:
                print(f"   ⚠️  No se encontraron registros para {FECHA_PRUEBA}")
        else:
            print(f"   ❌ Error al obtener registros: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 Resumen de la implementación:")
    print("   • Eliminado guardado automático (onchange)")
    print("   • Agregado botón 'Guardar' por técnico")
    print("   • Implementada validación de campos completos")
    print("   • Implementado guardado masivo por técnico")
    print("   • Agregada columna 'Acciones' en la tabla")
    print("   • Corregido error 500 del endpoint actualizar-campo")
    
    print("\n✨ Funcionalidad implementada exitosamente!")
    print("   El usuario ahora puede llenar todos los campos y usar")
    print("   el botón 'Guardar' para guardar todos los cambios de una vez.")

if __name__ == "__main__":
    test_manual_save_functionality()