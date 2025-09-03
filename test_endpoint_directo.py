#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el endpoint /api/vehiculos/vencimientos directamente
sin necesidad del navegador
"""

import requests
import json
from bs4 import BeautifulSoup

def test_vencimientos_endpoint():
    """Prueba el endpoint de vencimientos con autenticación completa"""
    
    base_url = "http://localhost:8080"
    session = requests.Session()
    
    print("=== Test Endpoint /api/vehiculos/vencimientos ===")
    print(f"URL base: {base_url}")
    
    try:
        print("1. Preparando login...")
        
        # Crear sesión para mantener cookies
        session = requests.Session()
        
        # Paso 2: Realizar login
        print("\n2. Realizando login...")
        # Datos de login - probando con usuario DIANA CAROLINA SOSA
        login_data = {
            'username': '1002407101',  # Cédula de DIANA CAROLINA SOSA
            'password': '123456'       # Contraseña común
        }
        
        login_response = session.post(f"{base_url}/", data=login_data)
        
        if login_response.status_code != 200:
            print(f"Error en login: {login_response.status_code}")
            print(f"Respuesta: {login_response.text[:500]}")
            return False
            
        # Paso 3: Probar endpoint de vencimientos
        print("\n3. Probando endpoint /api/vehiculos/vencimientos...")
        vencimientos_response = session.get(f"{base_url}/api/vehiculos/vencimientos")
        
        print(f"Status code: {vencimientos_response.status_code}")
        print(f"Headers: {dict(vencimientos_response.headers)}")
        
        if vencimientos_response.status_code == 200:
            try:
                data = vencimientos_response.json()
                print(f"\nRespuesta JSON:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Verificar estructura de respuesta
                if 'success' in data and data['success']:
                    print(f"\n✓ Endpoint funcionando correctamente")
                    print(f"✓ Total de vehículos: {data.get('total', 'No especificado')}")
                    print(f"✓ Registros en data: {len(data.get('data', []))}")
                    
                    if data.get('data'):
                        print("\nPrimeros 3 registros:")
                        for i, vehiculo in enumerate(data['data'][:3]):
                            print(f"  {i+1}. Placa: {vehiculo.get('placa', 'N/A')}, "
                                  f"SOAT: {vehiculo.get('estado_soat', 'N/A')}, "
                                  f"Tecnomecánica: {vehiculo.get('estado_tecnomecanica', 'N/A')}")
                    else:
                        print("\n⚠ No hay datos de vencimientos")
                        
                    return True
                else:
                    print(f"\n✗ Respuesta indica fallo: {data}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"\n✗ Error decodificando JSON: {e}")
                print(f"Respuesta raw: {vencimientos_response.text[:500]}")
                return False
                
        elif vencimientos_response.status_code == 401:
            print("\n✗ Error 401: No autorizado - problema de autenticación")
            return False
        elif vencimientos_response.status_code == 403:
            print("\n✗ Error 403: Prohibido - problema de permisos de rol")
            return False
        else:
            print(f"\n✗ Error {vencimientos_response.status_code}: {vencimientos_response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Error de conexión: ¿Está el servidor Flask ejecutándose?")
        return False
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
        return False
        
    finally:
        # Logout
        try:
            session.get(f"{base_url}/logout")
            print("\n4. Logout realizado")
        except:
            pass

def main():
    """Función principal"""
    success = test_vencimientos_endpoint()
    
    print("\n" + "="*50)
    if success:
        print("✓ PRUEBA EXITOSA: El endpoint funciona correctamente")
    else:
        print("✗ PRUEBA FALLIDA: Hay problemas con el endpoint")
    print("="*50)
    
    return success

if __name__ == "__main__":
    main()