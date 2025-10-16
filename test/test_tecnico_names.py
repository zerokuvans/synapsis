#!/usr/bin/env python3
"""
Script para verificar que el endpoint /api/mpa/vehiculos/placas 
está devolviendo nombres de técnicos en lugar de IDs
"""

import requests
import json
from datetime import datetime

def test_placas_endpoint():
    """Probar el endpoint de placas para verificar nombres de técnicos"""
    
    print("=== VERIFICACIÓN DE NOMBRES DE TÉCNICOS EN PLACAS ===")
    print(f"Fecha de prueba: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # URL del endpoint
    url = "http://127.0.0.1:8080/api/mpa/vehiculos/placas"
    
    try:
        # Realizar petición GET
        print(f"Realizando petición a: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"Código de respuesta: {response.status_code}")
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
                    placas = data.get('data', [])
                    print(f"✅ Endpoint funcionando correctamente")
                    print(f"🚗 Se encontraron {len(placas)} vehículos")
                    
                    if placas:
                        print("\n=== ANÁLISIS DE TÉCNICOS ASIGNADOS ===")
                        for i, vehiculo in enumerate(placas, 1):
                            placa = vehiculo.get('placa', 'N/A')
                            tipo_vehiculo = vehiculo.get('tipo_vehiculo', 'N/A')
                            tecnico_id = vehiculo.get('tecnico_asignado', 'N/A')
                            tecnico_nombre = vehiculo.get('tecnico_nombre', 'N/A')
                            
                            print(f"\n{i}. Placa: {placa}")
                            print(f"   Tipo: {tipo_vehiculo}")
                            print(f"   Técnico ID: {tecnico_id}")
                            print(f"   Técnico Nombre: {tecnico_nombre}")
                            
                            # Verificar si el nombre es diferente del ID
                            if str(tecnico_id) != str(tecnico_nombre) and tecnico_nombre != 'N/A':
                                print(f"   ✅ CORRECTO: Mostrando nombre en lugar de ID")
                            elif str(tecnico_id) == str(tecnico_nombre):
                                print(f"   ❌ PROBLEMA: Aún mostrando ID en lugar de nombre")
                            else:
                                print(f"   ⚠️  Sin técnico asignado")
                    else:
                        print("⚠️  No se encontraron vehículos")
                        
                else:
                    print(f"❌ Error en la respuesta: {data.get('message', 'Sin mensaje')}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error al decodificar JSON: {e}")
                print(f"Respuesta cruda: {response.text}")
                
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_placas_endpoint()