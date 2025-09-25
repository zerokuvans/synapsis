#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el endpoint de refresh-stock-dotaciones
"""

import requests
import json
from datetime import datetime

def test_stock_endpoint():
    print("=" * 60)
    print("PRUEBA DEL ENDPOINT DE STOCK")
    print("=" * 60)
    
    # URL del endpoint (corriendo en localhost:8080)
    base_url = "http://localhost:8080"
    endpoint = "/api/refresh-stock-dotaciones"
    url = f"{base_url}{endpoint}"
    
    print(f"\n🌐 PROBANDO ENDPOINT: {url}")
    
    try:
        # Hacer la petición POST al endpoint
        print(f"\n📡 Enviando petición POST...")
        response = requests.post(url, timeout=30)
        
        print(f"\n📊 RESPUESTA:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n✅ RESPUESTA EXITOSA:")
                print(f"   Tipo de datos: {type(data)}")
                
                if isinstance(data, list):
                    print(f"   Total de materiales: {len(data)}")
                    
                    # Mostrar los primeros 5 materiales
                    print(f"\n📋 PRIMEROS MATERIALES:")
                    for i, material in enumerate(data[:5], 1):
                        if isinstance(material, dict):
                            material_tipo = material.get('material_tipo', 'N/A')
                            stock_inicial = material.get('stock_inicial', 'N/A')
                            total_asignaciones = material.get('total_asignaciones', 'N/A')
                            total_cambios = material.get('total_cambios', 'N/A')
                            stock_actual = material.get('stock_actual', 'N/A')
                            
                            print(f"   {i}. {material_tipo}:")
                            print(f"      - Stock inicial: {stock_inicial}")
                            print(f"      - Asignaciones: {total_asignaciones}")
                            print(f"      - Cambios: {total_cambios}")
                            print(f"      - Stock actual: {stock_actual}")
                        else:
                            print(f"   {i}. {material}")
                    
                    # Verificar si hay materiales con stock actual > 0
                    materiales_con_stock = []
                    for material in data:
                        if isinstance(material, dict):
                            stock_actual = material.get('stock_actual', 0)
                            if isinstance(stock_actual, (int, float)) and stock_actual > 0:
                                materiales_con_stock.append(material)
                    
                    print(f"\n📈 ANÁLISIS:")
                    print(f"   Materiales con stock > 0: {len(materiales_con_stock)}")
                    print(f"   Materiales con stock = 0: {len(data) - len(materiales_con_stock)}")
                    
                    if materiales_con_stock:
                        print(f"\n🎯 MATERIALES CON STOCK POSITIVO:")
                        for material in materiales_con_stock[:3]:
                            material_tipo = material.get('material_tipo', 'N/A')
                            stock_actual = material.get('stock_actual', 'N/A')
                            print(f"   - {material_tipo}: {stock_actual}")
                    else:
                        print(f"\n⚠️ PROBLEMA DETECTADO: Todos los materiales tienen stock = 0")
                        print(f"   Esto podría indicar:")
                        print(f"   1. La tabla 'dotaciones' está vacía")
                        print(f"   2. Los valores en 'stock_ferretero' son todos 0")
                        print(f"   3. Hay un problema en el cálculo del endpoint")
                
                elif isinstance(data, dict):
                    print(f"   Respuesta tipo diccionario:")
                    for key, value in data.items():
                        print(f"   {key}: {value}")
                else:
                    print(f"   Respuesta: {data}")
                    
            except json.JSONDecodeError as e:
                print(f"\n❌ ERROR AL PARSEAR JSON: {e}")
                print(f"   Respuesta raw: {response.text[:500]}...")
                
        else:
            print(f"\n❌ ERROR EN LA RESPUESTA:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Respuesta: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR DE CONEXIÓN:")
        print(f"   No se pudo conectar a {url}")
        print(f"   Verifica que el servidor esté ejecutándose")
        
    except requests.exceptions.Timeout:
        print(f"\n❌ TIMEOUT:")
        print(f"   La petición tardó más de 30 segundos")
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
    
    print("\n" + "=" * 60)

def test_vista_endpoint():
    print("\n" + "=" * 60)
    print("PRUEBA DE LA VISTA STOCK DOTACIONES")
    print("=" * 60)
    
    # También probar si hay un endpoint para la vista
    base_url = "http://localhost:8080"
    endpoint = "/api/vista-stock-dotaciones"
    url = f"{base_url}{endpoint}"
    
    print(f"\n🌐 PROBANDO ENDPOINT DE VISTA: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n✅ VISTA DISPONIBLE:")
                print(f"   Total registros: {len(data) if isinstance(data, list) else 'N/A'}")
            except:
                print(f"\n✅ VISTA RESPONDE (no JSON): {response.text[:100]}")
        else:
            print(f"\n❌ Vista no disponible (Status: {response.status_code})")
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ No se pudo conectar al endpoint de vista")
    except Exception as e:
        print(f"\n❌ Error probando vista: {e}")

if __name__ == '__main__':
    print(f"Iniciando pruebas - {datetime.now()}")
    test_stock_endpoint()
    test_vista_endpoint()
    print(f"\nPruebas completadas - {datetime.now()}")