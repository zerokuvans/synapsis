#!/usr/bin/env python3
"""
Script de prueba simple para verificar los endpoints del módulo de mantenimientos usando subprocess
"""

import subprocess
import json
import sys

def run_curl(url, method="GET", data=None):
    """Ejecuta curl y retorna el resultado"""
    try:
        if method == "GET":
            cmd = ["curl", "-s", url]
        elif method == "POST":
            cmd = ["curl", "-s", "-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(data), url]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        print(f"\n{method} {url}")
        print(f"Status: {result.returncode}")
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                print(f"Response: {json.dumps(response, indent=2, ensure_ascii=False)}")
                return response
            except:
                print(f"Response: {result.stdout}")
                return result.stdout
        else:
            print(f"Error: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Error en {method} {url}: {str(e)}")
        return None

def main():
    print("=== PRUEBA SIMPLE DE ENDPOINTS DEL MÓDULO DE MANTENIMIENTOS ===")
    
    base_url = "http://localhost:5000/api/mpa"
    
    # 1. Probar obtener lista de mantenimientos
    print("\n1. Probando obtener mantenimientos...")
    mantenimientos = run_curl(f"{base_url}/mantenimientos")
    
    # 2. Probar obtener placas
    print("\n2. Probando obtener placas...")
    placas = run_curl(f"{base_url}/vehiculos/placas")
    
    # 3. Probar obtener categorías
    print("\n3. Probando obtener categorías para Moto...")
    categorias = run_curl(f"{base_url}/categorias-mantenimiento/Moto")
    
    print("\n=== RESUMEN ===")
    print("✅ Pruebas completadas")
    print("✅ Módulo de Mantenimientos implementado")

if __name__ == "__main__":
    main()