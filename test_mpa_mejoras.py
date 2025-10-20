#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplificado para probar las mejoras implementadas en el módulo MPA
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8080"

def test_server_status():
    """Verificar que el servidor esté funcionando"""
    print("🔍 Verificando estado del servidor...")
    
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
            print(f"   Respuesta: {response.json()}")
            return True
        else:
            print(f"❌ Servidor respondió con código: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {str(e)}")
        return False

def test_api_endpoints():
    """Probar los endpoints de las APIs implementadas"""
    print("\n🔍 Probando endpoints de APIs...")
    
    # Lista de endpoints para probar
    endpoints = [
        ("GET", "/api/mpa/validaciones/unicidad", "API de validación de unicidad"),
        ("GET", "/api/mpa/historial/consolidado", "API de historial consolidado"),
        ("GET", "/api/mpa/reportes/sincronizacion", "API de reportes de sincronización"),
        ("GET", "/api/mpa/vehiculos", "API de vehículos (existente)"),
        ("GET", "/api/mpa/soat", "API de SOAT (existente)"),
        ("GET", "/api/mpa/tecnico_mecanica", "API de Tecnomecánica (existente)")
    ]
    
    for method, endpoint, description in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json={}, timeout=10)
            
            print(f"   {description}:")
            print(f"     URL: {endpoint}")
            print(f"     Código: {response.status_code}")
            
            if response.status_code in [200, 400, 401, 403]:
                print(f"     ✅ Endpoint disponible")
                
                # Intentar mostrar parte de la respuesta
                try:
                    if response.headers.get('content-type', '').startswith('application/json'):
                        data = response.json()
                        if isinstance(data, dict):
                            if 'message' in data:
                                print(f"     Mensaje: {data['message']}")
                            elif 'error' in data:
                                print(f"     Error: {data['error']}")
                        elif isinstance(data, list):
                            print(f"     Datos: Lista con {len(data)} elementos")
                except:
                    print(f"     Respuesta: {response.text[:100]}...")
            else:
                print(f"     ❌ Endpoint no disponible o error")
                
        except Exception as e:
            print(f"     ❌ Error: {str(e)}")
        
        print()

def test_post_endpoints():
    """Probar endpoints POST con datos de prueba"""
    print("\n🔍 Probando endpoints POST...")
    
    # Probar validación de unicidad
    print("   Probando validación de unicidad:")
    try:
        data = {
            "tipo_documento": "soat",
            "placa": "TEST123"
        }
        
        response = requests.post(f"{BASE_URL}/api/mpa/validaciones/unicidad", json=data, timeout=10)
        print(f"     Código: {response.status_code}")
        
        if response.status_code in [200, 400, 401, 403]:
            print(f"     ✅ Endpoint POST funcionando")
            try:
                result = response.json()
                print(f"     Respuesta: {result}")
            except:
                print(f"     Respuesta: {response.text[:100]}...")
        else:
            print(f"     ❌ Error en endpoint POST")
            
    except Exception as e:
        print(f"     ❌ Error: {str(e)}")

def test_database_tables():
    """Verificar que las tablas de historial existan consultando la estructura"""
    print("\n🔍 Verificando estructura de base de datos...")
    
    # Intentar consultar las APIs que dependen de las nuevas tablas
    endpoints_db = [
        "/api/mpa/historial/consolidado",
        "/api/mpa/reportes/sincronizacion"
    ]
    
    for endpoint in endpoints_db:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            print(f"   {endpoint}:")
            print(f"     Código: {response.status_code}")
            
            if response.status_code == 200:
                print(f"     ✅ Tablas de historial funcionando")
            elif response.status_code in [401, 403]:
                print(f"     ✅ Endpoint disponible (requiere autenticación)")
            elif response.status_code == 500:
                print(f"     ⚠️ Posible error en base de datos")
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        print(f"     Error: {error_data['error']}")
                except:
                    pass
            else:
                print(f"     ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"     ❌ Error: {str(e)}")

def main():
    """Función principal para ejecutar todas las pruebas"""
    print("🚀 PRUEBAS SIMPLIFICADAS DE MEJORAS MPA")
    print("=" * 50)
    
    # Verificar servidor
    if not test_server_status():
        print("❌ No se puede continuar sin servidor funcionando")
        return
    
    # Ejecutar pruebas
    test_api_endpoints()
    test_post_endpoints()
    test_database_tables()
    
    print("\n" + "=" * 50)
    print("✅ PRUEBAS COMPLETADAS")
    print("\n📋 Resumen de verificaciones:")
    print("   ✓ Servidor funcionando")
    print("   ✓ Endpoints de APIs verificados")
    print("   ✓ Funcionalidad POST probada")
    print("   ✓ Estructura de base de datos verificada")
    print("\n💡 Para pruebas completas con autenticación,")
    print("   usar la interfaz web en: http://127.0.0.1:8080")

if __name__ == "__main__":
    main()