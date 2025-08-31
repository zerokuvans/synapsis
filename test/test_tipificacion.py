#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar el endpoint /api/asistencia/tipificacion
"""

import requests
import json

def test_tipificacion_endpoint():
    """Prueba el endpoint de tipificación"""
    
    # URL del endpoint
    url = 'http://localhost:5000/api/asistencia/tipificacion'
    
    try:
        # Realizar petición GET
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nRespuesta JSON:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('success'):
                tipificaciones = data.get('tipificaciones', [])
                print(f"\nNúmero de tipificaciones encontradas: {len(tipificaciones)}")
                
                if tipificaciones:
                    print("\nPrimeras 3 tipificaciones:")
                    for i, tip in enumerate(tipificaciones[:3]):
                        print(f"  {i+1}. Código: {tip.get('codigo')}, Descripción: {tip.get('descripcion')}")
                else:
                    print("\n⚠️  No se encontraron tipificaciones en la respuesta")
            else:
                print(f"\n❌ Error en la respuesta: {data.get('message', 'Sin mensaje')}")
        else:
            print(f"\n❌ Error HTTP {response.status_code}")
            print(f"Contenido: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está el servidor ejecutándose en localhost:5000?")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la petición: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ Error al decodificar JSON: {e}")
        print(f"Contenido de respuesta: {response.text[:500]}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == '__main__':
    print("=== Prueba del endpoint /api/asistencia/tipificacion ===")
    test_tipificacion_endpoint()