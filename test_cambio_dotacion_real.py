#!/usr/bin/env python3
"""
Script para simular exactamente la petición del frontend al endpoint de cambios de dotación
"""

import requests
import json
from datetime import datetime

def test_cambio_dotacion_real():
    """Simular la petición exacta del frontend"""
    print("🧪 TEST: Simulación de cambio de dotación real")
    print("=" * 60)
    
    # URL del endpoint
    url = "http://localhost:8080/api/cambios_dotacion"
    
    # Datos exactos como los envía el frontend
    data = {
        "id_codigo_consumidor": 12345,  # Un técnico válido
        "fecha_cambio": "2024-01-20",
        
        # Camiseta polo con estado VALORADO (como en el error)
        "camisetapolo": 1,
        "camiseta_polo_talla": "M",
        "camisetapolo_valorado": True,  # ✅ VALORADO como en el error
        
        # Otros elementos en 0
        "pantalon": 0,
        "pantalon_talla": "",
        "pantalon_valorado": False,
        
        "camisetagris": 0,
        "camiseta_gris_talla": "",
        "camisetagris_valorado": False,
        
        "guerrera": 0,
        "guerrera_talla": "",
        "guerrera_valorado": False,
        
        "chaqueta": 0,
        "chaqueta_talla": "",
        "chaqueta_valorado": False,
        
        "guantes_nitrilo": 0,
        "guantes_nitrilo_valorado": False,
        
        "guantes_carnaza": 0,
        "guantes_carnaza_valorado": False,
        
        "gafas": 0,
        "gafas_valorado": False,
        
        "gorra": 0,
        "gorra_valorado": False,
        
        "casco": 0,
        "casco_valorado": False,
        
        "botas": 0,
        "botas_talla": "",
        "botas_valorado": False,
        
        "observaciones": "Test de camiseta polo VALORADO"
    }
    
    print("📤 DATOS ENVIADOS:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    try:
        # Hacer la petición POST
        response = requests.post(
            url, 
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\n📥 RESPUESTA:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"   JSON Response:")
            print(json.dumps(response_data, indent=4, ensure_ascii=False))
            
            if response.status_code == 201:
                print("\n✅ ¡ÉXITO! El cambio de dotación se registró correctamente")
            elif response.status_code == 400:
                print(f"\n❌ ERROR 400: {response_data.get('message', 'Error desconocido')}")
                if 'errors' in response_data:
                    print("   Errores específicos:")
                    for error in response_data['errors']:
                        print(f"     - {error}")
            else:
                print(f"\n⚠️ RESPUESTA INESPERADA: {response.status_code}")
                
        except json.JSONDecodeError:
            print(f"   Raw Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté ejecutándose en http://localhost:8080")
    except requests.exceptions.Timeout:
        print("❌ ERROR: Timeout en la petición")
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")

def test_variaciones():
    """Probar diferentes variaciones del problema"""
    print("\n" + "=" * 60)
    print("🔬 PRUEBAS DE VARIACIONES")
    print("=" * 60)
    
    # Test 1: Con NO VALORADO
    print("\n1. TEST: Camiseta polo NO VALORADO")
    data_no_valorado = {
        "id_codigo_consumidor": 12345,
        "fecha_cambio": "2024-01-20",
        "camisetapolo": 1,
        "camiseta_polo_talla": "M",
        "camisetapolo_valorado": False,  # ❌ NO VALORADO
        "pantalon": 0, "camisetagris": 0, "guerrera": 0, "chaqueta": 0,
        "guantes_nitrilo": 0, "guantes_carnaza": 0, "gafas": 0, 
        "gorra": 0, "casco": 0, "botas": 0,
        "observaciones": "Test NO VALORADO"
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/api/cambios_dotacion",
            json=data_no_valorado,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code != 201:
            response_data = response.json()
            print(f"   Error: {response_data.get('message', 'Error desconocido')}")
        else:
            print("   ✅ Éxito")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Con cantidad mayor (121)
    print("\n2. TEST: Cantidad mayor al stock (121 unidades)")
    data_cantidad_mayor = {
        "id_codigo_consumidor": 12345,
        "fecha_cambio": "2024-01-20",
        "camisetapolo": 121,  # 🔥 Mayor al stock disponible (120)
        "camiseta_polo_talla": "M",
        "camisetapolo_valorado": True,
        "pantalon": 0, "camisetagris": 0, "guerrera": 0, "chaqueta": 0,
        "guantes_nitrilo": 0, "guantes_carnaza": 0, "gafas": 0, 
        "gorra": 0, "casco": 0, "botas": 0,
        "observaciones": "Test cantidad mayor"
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/api/cambios_dotacion",
            json=data_cantidad_mayor,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code != 201:
            response_data = response.json()
            print(f"   Error: {response_data.get('message', 'Error desconocido')}")
            if 'errors' in response_data:
                for error in response_data['errors']:
                    print(f"     - {error}")
        else:
            print("   ✅ Éxito (inesperado)")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_cambio_dotacion_real()
    test_variaciones()