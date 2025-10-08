#!/usr/bin/env python3
"""
Script para probar el endpoint de resumen agrupado y diagnosticar el error 500
"""
import requests
import json
from datetime import datetime

# URL base del servidor
BASE_URL = "http://127.0.0.1:8080"

def test_endpoint_with_future_date():
    """Probar el endpoint con fecha futura para reproducir el error 500"""
    print("=== PRUEBA CON FECHA FUTURA ===")
    
    # Fecha futura que está causando el problema
    url = f"{BASE_URL}/api/asistencia/resumen_agrupado?fecha_inicio=2025-10-03&fecha_fin=2025-10-03"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response JSON: {json.dumps(data, indent=2)}")
            except:
                print(f"Response Text: {response.text[:500]}...")
        else:
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")

def test_endpoint_with_valid_date():
    """Probar el endpoint con fecha válida"""
    print("\n=== PRUEBA CON FECHA VÁLIDA ===")
    
    # Fecha válida (pasada)
    url = f"{BASE_URL}/api/asistencia/resumen_agrupado?fecha_inicio=2023-10-03&fecha_fin=2023-10-03"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response JSON: {json.dumps(data, indent=2)}")
            except:
                print(f"Response Text: {response.text[:500]}...")
        else:
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")

def test_endpoint_with_current_date():
    """Probar el endpoint con fecha actual"""
    print("\n=== PRUEBA CON FECHA ACTUAL ===")
    
    # Fecha actual
    current_date = datetime.now().strftime('%Y-%m-%d')
    url = f"{BASE_URL}/api/asistencia/resumen_agrupado?fecha_inicio={current_date}&fecha_fin={current_date}"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response JSON: {json.dumps(data, indent=2)}")
            except:
                print(f"Response Text: {response.text[:500]}...")
        else:
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    print("Iniciando pruebas del endpoint de resumen agrupado...")
    print(f"Fecha y hora actual: {datetime.now()}")
    
    # Ejecutar todas las pruebas
    test_endpoint_with_future_date()
    test_endpoint_with_valid_date()
    test_endpoint_with_current_date()
    
    print("\n=== PRUEBAS COMPLETADAS ===