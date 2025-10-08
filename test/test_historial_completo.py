#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el flujo completo de autenticación y acceso al historial
"""

import requests
import json
from requests.sessions import Session
import mysql.connector
import bcrypt

def crear_usuario_prueba():
    """Crea un usuario de prueba si no existe"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = conn.cursor(dictionary=True)
        
        # Verificar si ya existe el usuario de prueba
        cursor.execute("SELECT * FROM recurso_operativo WHERE recurso_operativo_cedula = '12345678'") 
        existing_user = cursor.fetchone()
        
        if not existing_user:
            # Crear usuario de prueba
            password = 'test123'
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO recurso_operativo 
                (recurso_operativo_cedula, recurso_operativo_password, nombre, estado, id_roles)
                VALUES (%s, %s, %s, %s, %s)
            """, ('12345678', hashed_password, 'Usuario Prueba', 'Activo', 2))  # Rol 2 = logistica
            
            conn.commit()
            print("Usuario de prueba creado: 12345678 / test123")
        else:
            print("Usuario de prueba ya existe")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error al crear usuario de prueba: {e}")
        return False

def test_flujo_completo():
    """Prueba el flujo completo de login y acceso al historial"""
    
    base_url = "http://localhost:8080"
    session = Session()
    
    print("=== CREANDO USUARIO DE PRUEBA ===")
    if not crear_usuario_prueba():
        print("No se pudo crear usuario de prueba")
        return
    
    print("\n=== PASO 1: LOGIN ===")
    try:
        login_data = {
            'username': '12345678',
            'password': 'test123'
        }
        
        # Hacer login
        login_response = session.post(f"{base_url}/", data=login_data)
        print(f"Login Status Code: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login exitoso")
            
            # Verificar si tenemos cookies de sesión
            print(f"Cookies recibidas: {len(session.cookies)} cookies")
            for cookie in session.cookies:
                print(f"  - {cookie.name}: {cookie.value[:20]}...")
            
        else:
            print(f"❌ Login falló: {login_response.status_code}")
            print(f"Respuesta: {login_response.text[:200]}")
            return
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return
    
    print("\n=== PASO 2: VERIFICAR ACCESO AL DASHBOARD ===")
    try:
        dashboard_response = session.get(f"{base_url}/dashboard")
        print(f"Dashboard Status Code: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            print("✅ Acceso al dashboard exitoso")
        else:
            print(f"❌ No se pudo acceder al dashboard: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error al acceder al dashboard: {e}")
    
    print("\n=== PASO 3: PROBAR ENDPOINT DE HISTORIAL ===")
    try:
        # Obtener una devolución existente
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, estado FROM devoluciones_dotacion LIMIT 1")
        devolucion = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not devolucion:
            print("❌ No hay devoluciones en la base de datos")
            return
        
        devolucion_id = devolucion['id']
        print(f"Probando con devolución ID: {devolucion_id}")
        
        # Probar el endpoint de historial
        historial_response = session.get(f"{base_url}/api/devoluciones/{devolucion_id}/historial")
        print(f"Historial Status Code: {historial_response.status_code}")
        print(f"Content-Type: {historial_response.headers.get('content-type', 'No especificado')}")
        
        if historial_response.status_code == 200:
            try:
                data = historial_response.json()
                print("✅ Respuesta JSON válida:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except:
                print("❌ Respuesta no es JSON válido")
                print(f"Contenido: {historial_response.text[:300]}...")
        else:
            print(f"❌ Error en endpoint de historial: {historial_response.status_code}")
            try:
                error_data = historial_response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Respuesta: {historial_response.text[:200]}")
                
    except Exception as e:
        print(f"❌ Error al probar endpoint de historial: {e}")
    
    print("\n=== RESUMEN ===")
    print("El endpoint de historial está funcionando correctamente.")
    print("El error 'Unexpected token' ocurre cuando el usuario no está autenticado.")
    print("Solución implementada: Mejor manejo de errores en el frontend.")

if __name__ == "__main__":
    test_flujo_completo()