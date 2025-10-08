#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debuggear el problema del historial de devoluciones
"""

import requests
import json
from requests.sessions import Session

def test_historial_endpoint():
    """Prueba el endpoint de historial con diferentes escenarios"""
    
    base_url = "http://localhost:8080"
    
    # Crear sesión para mantener cookies
    session = Session()
    
    print("=== PRUEBA 1: Acceso sin autenticación ===")
    try:
        response = session.get(f"{base_url}/api/devoluciones/1/historial")
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'No especificado')}")
        
        # Verificar si es JSON o HTML
        try:
            data = response.json()
            print("Respuesta JSON:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            print("Respuesta NO es JSON:")
            print(f"Primeros 200 caracteres: {response.text[:200]}...")
            
    except Exception as e:
        print(f"Error en la petición: {e}")
    
    print("\n=== PRUEBA 2: Intentar login primero ===")
    try:
        # Intentar login
        login_data = {
            'username': '1234567890',  # Usar una cédula de prueba
            'password': 'password123'   # Usar una contraseña de prueba
        }
        
        login_response = session.post(f"{base_url}/", data=login_data)
        print(f"Login Status Code: {login_response.status_code}")
        
        # Verificar si el login fue exitoso
        if login_response.status_code == 200:
            print("Login aparentemente exitoso")
            
            # Ahora probar el endpoint de historial
            print("\n=== PRUEBA 3: Acceso con sesión autenticada ===")
            response = session.get(f"{base_url}/api/devoluciones/1/historial")
            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'No especificado')}")
            
            try:
                data = response.json()
                print("Respuesta JSON:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except:
                print("Respuesta NO es JSON:")
                print(f"Primeros 500 caracteres: {response.text[:500]}...")
        else:
            print(f"Login falló con código: {login_response.status_code}")
            print(f"Respuesta: {login_response.text[:200]}...")
            
    except Exception as e:
        print(f"Error en login/prueba autenticada: {e}")
    
    print("\n=== PRUEBA 4: Verificar si existe la devolución ID 1 ===")
    try:
        # Verificar directamente en la base de datos si existe la devolución
        import mysql.connector
        
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, estado FROM devoluciones_dotacion WHERE id = 1")
        devolucion = cursor.fetchone()
        
        if devolucion:
            print(f"Devolución encontrada: ID={devolucion['id']}, Estado={devolucion['estado']}")
        else:
            print("No se encontró devolución con ID 1")
            
            # Buscar cualquier devolución
            cursor.execute("SELECT id, estado FROM devoluciones_dotacion LIMIT 5")
            devoluciones = cursor.fetchall()
            print(f"Devoluciones disponibles: {len(devoluciones)}")
            for dev in devoluciones:
                print(f"  - ID: {dev['id']}, Estado: {dev['estado']}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error al verificar base de datos: {e}")

if __name__ == "__main__":
    test_historial_endpoint()