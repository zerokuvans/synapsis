#!/usr/bin/env python3
"""
Debug para verificar qué datos está devolviendo el endpoint de consulta de asistencia
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8080"
SUPERVISOR = "CARLOS ANDRES VARGAS TORRES"
FECHA = "2024-09-30"  # Fecha donde sabemos que existe el registro 5992

def debug_endpoint_consultar():
    """Debug del endpoint /api/asistencia/consultar"""
    
    print("=== DEBUG ENDPOINT /api/asistencia/consultar ===")
    print(f"Supervisor: {SUPERVISOR}")
    print(f"Fecha: {FECHA}")
    print()
    
    try:
        # Hacer la petición al endpoint
        response = requests.get(
            f"{BASE_URL}/api/asistencia/consultar",
            params={
                "supervisor": SUPERVISOR,
                "fecha": FECHA
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Raw Response Text: {repr(response.text[:500])}")  # Primeros 500 caracteres
        print()
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Success: {data.get('success')}")
                
                if data.get('success'):
                    registros = data.get('registros', [])
                    print(f"Total registros: {len(registros)}")
                    print()
                    
                    # Mostrar cada registro
                    for i, registro in enumerate(registros, 1):
                        print(f"--- REGISTRO {i} ---")
                        print(f"ID Asistencia: {registro.get('id_asistencia')}")
                        print(f"Cédula: {registro.get('cedula')}")
                        print(f"Técnico: {registro.get('tecnico')}")
                        print(f"ID Código Consumidor: {registro.get('id_codigo_consumidor')}")
                        print(f"Hora Inicio: {registro.get('hora_inicio')}")
                        print(f"Estado: {registro.get('estado')}")
                        print(f"Novedad: {registro.get('novedad')}")
                        print(f"Carpeta Día: {registro.get('carpeta_dia')}")
                        print(f"Fecha Asistencia: {registro.get('fecha_asistencia')}")
                        print()
                        
                        # Verificar si es el registro 5992
                        if registro.get('id_asistencia') == 5992:
                            print("🎯 ENCONTRADO REGISTRO 5992!")
                            print(f"   Datos actuales:")
                            print(f"   - Hora Inicio: {registro.get('hora_inicio')}")
                            print(f"   - Estado: {registro.get('estado')}")
                            print(f"   - Novedad: {registro.get('novedad')}")
                            print()
                            
                else:
                    print(f"Error en respuesta: {data.get('message')}")
            except json.JSONDecodeError as e:
                print(f"Error decodificando JSON: {e}")
                print(f"Respuesta completa: {response.text}")
        else:
            print(f"Error HTTP: {response.text}")
            
    except Exception as e:
        print(f"Error de conexión: {e}")

def debug_endpoint_tecnicos():
    """Debug del endpoint /api/tecnicos_por_supervisor como fallback"""
    
    print("=== DEBUG ENDPOINT /api/tecnicos_por_supervisor (FALLBACK) ===")
    print(f"Supervisor: {SUPERVISOR}")
    print()
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/tecnicos_por_supervisor",
            params={"supervisor": SUPERVISOR}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            
            if data.get('success'):
                tecnicos = data.get('tecnicos', [])
                print(f"Total técnicos: {len(tecnicos)}")
                
                # Buscar el técnico con cédula 5694500
                for tecnico in tecnicos:
                    if tecnico.get('recurso_operativo_cedula') == '5694500':
                        print(f"🎯 ENCONTRADO TÉCNICO CON CÉDULA 5694500:")
                        print(f"   Nombre: {tecnico.get('nombre')}")
                        print(f"   ID Código Consumidor: {tecnico.get('id_codigo_consumidor')}")
                        print(f"   Carpeta: {tecnico.get('carpeta')}")
                        break
            else:
                print(f"Error en respuesta: {data.get('message')}")
        else:
            print(f"Error HTTP: {response.text}")
            
    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == "__main__":
    debug_endpoint_consultar()
    print("\n" + "="*60 + "\n")
    debug_endpoint_tecnicos()