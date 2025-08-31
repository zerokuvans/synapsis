#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar el endpoint /api/indicadores/estado_vehiculos
"""

import requests
import json
from datetime import datetime

def test_endpoint():
    """Probar el endpoint de estado de vehículos"""
    
    print("=== PRUEBA DEL ENDPOINT /api/indicadores/estado_vehiculos ===")
    print(f"Fecha de prueba: {datetime.now()}")
    print()
    
    # URL del endpoint
    url = "http://localhost:8080/api/indicadores/estado_vehiculos"
    
    try:
        # Realizar petición GET
        print(f"Realizando petición a: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"Código de respuesta: {response.status_code}")
        print(f"Headers de respuesta: {dict(response.headers)}")
        print()
        
        # Verificar el contenido de la respuesta
        if response.status_code == 200:
            try:
                data = response.json()
                print("=== RESPUESTA JSON ===")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                print()
                
                # Analizar la respuesta
                if data.get('success'):
                    estadisticas = data.get('estadisticas', [])
                    print(f"✅ Endpoint funcionando correctamente")
                    print(f"📊 Se encontraron {len(estadisticas)} supervisores")
                    
                    if estadisticas:
                        print("\n=== PRIMEROS 5 SUPERVISORES ===")
                        for i, supervisor in enumerate(estadisticas[:5]):
                            print(f"{i+1}. {supervisor['supervisor']}: {supervisor['total']} vehículos")
                            print(f"   Bueno: {supervisor['bueno']}, Regular: {supervisor['regular']}, Malo: {supervisor['malo']}")
                    else:
                        print("⚠️  No se encontraron datos de supervisores")
                else:
                    print(f"❌ Error en la respuesta: {data.get('error', 'Error desconocido')}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error al decodificar JSON: {e}")
                print(f"Contenido de la respuesta: {response.text[:500]}...")
                
        elif response.status_code == 401:
            print("❌ Error 401: No autorizado - Se requiere autenticación")
            print("💡 El endpoint requiere estar logueado con rol 'administrativo'")
            
        elif response.status_code == 403:
            print("❌ Error 403: Prohibido - Sin permisos suficientes")
            print("💡 Se requiere rol 'administrativo' para acceder")
            
        elif response.status_code == 500:
            print("❌ Error 500: Error interno del servidor")
            try:
                error_data = response.json()
                print(f"Detalles del error: {error_data}")
            except:
                print(f"Respuesta del servidor: {response.text[:500]}...")
        else:
            print(f"❌ Código de respuesta inesperado: {response.status_code}")
            print(f"Respuesta: {response.text[:500]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: No se pudo conectar al servidor")
        print("💡 Asegúrate de que el servidor Flask esté ejecutándose en localhost:5000")
        
    except requests.exceptions.Timeout:
        print("❌ Error de timeout: La petición tardó demasiado")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    print("\n=== FIN DE LA PRUEBA ===")

if __name__ == "__main__":
    test_endpoint()