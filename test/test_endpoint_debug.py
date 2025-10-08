#!/usr/bin/env python3
"""
Script para probar el endpoint /api/indicadores/detalle_tecnicos directamente
"""

import requests
import json
from datetime import datetime

def test_endpoint():
    """Probar el endpoint directamente"""
    
    # URL del endpoint
    base_url = "http://127.0.0.1:8080"
    endpoint = "/api/indicadores/detalle_tecnicos"
    
    # Parámetros de prueba
    params = {
        'fecha': '2025-01-10',
        'supervisor': 'CORTES CUERVO SANDRA CECILIA'
    }
    
    url = f"{base_url}{endpoint}"
    
    print(f"=== PROBANDO ENDPOINT ===")
    print(f"URL: {url}")
    print(f"Parámetros: {params}")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 50)
    
    try:
        # Hacer la solicitud
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print("=" * 50)
        
        # Intentar parsear como JSON
        try:
            json_data = response.json()
            print("✅ Respuesta JSON válida:")
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print("❌ Error al parsear JSON:")
            print(f"Error: {e}")
            print("Contenido raw:")
            print(response.text[:1000])  # Primeros 1000 caracteres
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Error de conexión: {e}")
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la solicitud: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_endpoint()