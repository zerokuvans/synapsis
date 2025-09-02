#!/usr/bin/env python3
"""
Script para probar el endpoint API de comparación mensual
"""

import requests
import json

def test_api_endpoint():
    base_url = "http://localhost:5000"
    endpoint = "/api/comparacion_mensual_materiales"
    
    # Parámetros de prueba
    params = {
        'material': 'silicona',
        'anio': '2025'
    }
    
    try:
        print(f"Probando endpoint: {base_url}{endpoint}")
        print(f"Parámetros: {params}")
        
        response = requests.get(f"{base_url}{endpoint}", params=params)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✓ Respuesta exitosa:")
            print(json.dumps(data, indent=2, default=str))
            
            # Verificar estructura de datos
            if 'datos_mensuales' in data:
                datos = data['datos_mensuales']
                print(f"\nDatos mensuales encontrados: {len(datos)} registros")
                
                for dato in datos:
                    print(f"  Mes {dato['mes']}: Entradas={dato['entradas']}, Salidas={dato['salidas']}, Stock Final={dato['stock_final']}")
            else:
                print("\n✗ No se encontraron datos_mensuales en la respuesta")
        else:
            print(f"\n✗ Error en la respuesta: {response.status_code}")
            print(f"Contenido: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Error de conexión. Asegúrate de que la aplicación Flask esté ejecutándose en localhost:5000")
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")

def test_different_materials():
    """Probar con diferentes materiales"""
    base_url = "http://localhost:5000"
    endpoint = "/api/comparacion_mensual_materiales"
    
    materiales = ['silicona', 'amarres_negros', 'amarres_blancos', 'cinta_aislante', 'grapas_blancas', 'grapas_negras']
    
    print("\n=== PROBANDO DIFERENTES MATERIALES ===")
    
    for material in materiales:
        params = {
            'material': material,
            'anio': '2025'
        }
        
        try:
            response = requests.get(f"{base_url}{endpoint}", params=params)
            
            if response.status_code == 200:
                data = response.json()
                datos = data.get('datos_mensuales', [])
                
                if datos and any(d['entradas'] > 0 or d['salidas'] > 0 for d in datos):
                    print(f"✓ {material}: {len(datos)} registros con datos")
                else:
                    print(f"- {material}: Sin datos de movimientos")
            else:
                print(f"✗ {material}: Error {response.status_code}")
                
        except Exception as e:
            print(f"✗ {material}: Error - {e}")

if __name__ == "__main__":
    print("PRUEBA DEL ENDPOINT API DE COMPARACIÓN MENSUAL")
    print("=" * 50)
    
    test_api_endpoint()
    test_different_materials()
    
    print("\n=== PRUEBA COMPLETADA ===")