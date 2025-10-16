#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

def test_page_error():
    """Probar el error de la página de vencimientos"""
    
    url = "http://127.0.0.1:8080/mpa/vencimientos"
    
    print("🔍 Probando página de vencimientos...")
    print(f"URL: {url}")
    print("=" * 60)
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 500:
            print("\n❌ Error 500 - Internal Server Error")
            print("Contenido de la respuesta:")
            print("-" * 40)
            print(response.text[:1000])  # Primeros 1000 caracteres
            print("-" * 40)
        else:
            print(f"\n✅ Respuesta exitosa")
            print("Primeros 500 caracteres:")
            print("-" * 40)
            print(response.text[:500])
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_page_error()