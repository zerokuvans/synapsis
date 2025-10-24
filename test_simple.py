#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_endpoints():
    print("=== PRUEBA DE ENDPOINTS ===")
    
    # Crear sesión
    session = requests.Session()
    
    # 1. Test login
    print("\n1. Probando login...")
    login_data = {
        'username': '1019112308',
        'password': '123456'
    }
    
    login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    print(f"Login Status: {login_response.status_code}")
    print(f"Login URL: {login_response.url}")
    
    # 2. Test endpoint preoperacional con GET (debería dar 405 Method Not Allowed)
    print("\n2. Probando GET /preoperacional...")
    get_response = session.get(f"{BASE_URL}/preoperacional")
    print(f"GET Status: {get_response.status_code}")
    try:
        print(f"GET Response: {get_response.json()}")
    except:
        print(f"GET Response Text: {get_response.text[:200]}")
    
    # 3. Test endpoint preoperacional con POST
    print("\n3. Probando POST /preoperacional...")
    post_data = {
        'placa_vehiculo': 'TON81E',
        'kilometraje': '50000'
    }
    
    post_response = session.post(f"{BASE_URL}/preoperacional", json=post_data)
    print(f"POST Status: {post_response.status_code}")
    try:
        print(f"POST Response: {json.dumps(post_response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"POST Response Text: {post_response.text[:200]}")

if __name__ == "__main__":
    test_endpoints()