#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_vencimientos_api():
    """Probar la API de vencimientos y mostrar errores detallados"""
    
    base_url = "http://127.0.0.1:8080"
    
    print("🔍 Probando API de vencimientos...")
    print("=" * 60)
    
    try:
        # Probar API de vencimientos
        response = requests.get(f"{base_url}/api/mpa/vencimientos", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 500:
            print("❌ Error 500 - Error interno del servidor")
            try:
                error_data = response.json()
                print(f"Error JSON: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error Text: {response.text}")
        elif response.status_code == 200:
            print("✅ API funcionando correctamente")
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Response Text: {response.text}")
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_vencimientos_api()