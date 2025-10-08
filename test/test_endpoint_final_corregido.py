#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script corregido para probar el endpoint /api/vehiculos/vencimientos
Basado en el análisis del código de login en main.py
"""

import requests
import json
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def conectar_db():
    """Conectar a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            database=os.getenv('MYSQL_DB', 'synapsis'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )
        return connection
    except Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None

def obtener_usuarios_logistica():
    """Obtener usuarios con rol de logística de la base de datos"""
    connection = conectar_db()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, estado
            FROM recurso_operativo 
            WHERE id_roles = 5 AND estado = 'Activo'
            LIMIT 3
        """)
        usuarios = cursor.fetchall()
        cursor.close()
        connection.close()
        return usuarios
    except Error as e:
        print(f"❌ Error consultando usuarios: {e}")
        return []

def test_login_y_endpoint():
    """Probar login y endpoint de vencimientos"""
    print("=== PRUEBA CORREGIDA DEL ENDPOINT /api/vehiculos/vencimientos ===")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Obtener usuarios de logística
    usuarios = obtener_usuarios_logistica()
    if not usuarios:
        print("❌ No se encontraron usuarios de logística activos")
        return
    
    print(f"✅ Encontrados {len(usuarios)} usuarios de logística:")
    for usuario in usuarios:
        print(f"   - {usuario['nombre']} (Cédula: {usuario['recurso_operativo_cedula']})")
    
    BASE_URL = 'http://127.0.0.1:8080'
    
    # Probar con cada usuario
    for usuario in usuarios:
        print(f"\n--- Probando con {usuario['nombre']} ---")
        
        # Crear nueva sesión
        session = requests.Session()
        
        # Datos de login - usar contraseña específica por usuario
        if usuario['recurso_operativo_cedula'] == 'test123':
            password = 'test123'
        else:
            password = '123456'  # Contraseña por defecto
            
        login_data = {
            'username': usuario['recurso_operativo_cedula'],
            'password': password
        }
        
        try:
            # Intentar login con header XMLHttpRequest
            print("1. Intentando login...")
            login_response = session.post(
                BASE_URL,
                data=login_data,
                headers={'X-Requested-With': 'XMLHttpRequest'},
                timeout=10
            )
            
            print(f"   Status: {login_response.status_code}")
            print(f"   Headers: {dict(login_response.headers)}")
            
            if login_response.status_code == 200:
                try:
                    login_json = login_response.json()
                    print(f"   Respuesta JSON: {login_json}")
                    
                    if login_json.get('status') == 'success':
                        print("   ✅ Login exitoso")
                        
                        # Probar endpoint de vencimientos
                        print("\n2. Probando endpoint de vencimientos...")
                        endpoint_response = session.get(
                            f"{BASE_URL}/api/vehiculos/vencimientos",
                            timeout=10
                        )
                        
                        print(f"   Status: {endpoint_response.status_code}")
                        print(f"   Content-Type: {endpoint_response.headers.get('Content-Type')}")
                        
                        if endpoint_response.status_code == 200:
                            try:
                                data = endpoint_response.json()
                                print("   ✅ Respuesta JSON válida")
                                print(f"   Success: {data.get('success')}")
                                print(f"   Total registros: {data.get('total', 0)}")
                                
                                if data.get('data'):
                                    print("   Primeros 3 registros:")
                                    for i, item in enumerate(data['data'][:3]):
                                        print(f"     {i+1}. Placa: {item.get('placa')}, Documento: {item.get('tipo_documento')}, Días: {item.get('dias_restantes')}")
                                else:
                                    print("   ⚠️ No hay datos de vencimientos")
                                
                                return True  # Éxito
                                
                            except json.JSONDecodeError:
                                print("   ❌ Respuesta no es JSON válido")
                                print(f"   Contenido: {endpoint_response.text[:200]}...")
                        else:
                            print(f"   ❌ Error en endpoint: {endpoint_response.status_code}")
                            print(f"   Contenido: {endpoint_response.text[:200]}...")
                    else:
                        print(f"   ❌ Login fallido: {login_json.get('message')}")
                        
                except json.JSONDecodeError:
                    print("   ❌ Respuesta de login no es JSON válido")
                    print(f"   Contenido: {login_response.text[:200]}...")
            else:
                print(f"   ❌ Error en login: {login_response.status_code}")
                print(f"   Contenido: {login_response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error de conexión: {e}")
        except Exception as e:
            print(f"   ❌ Error inesperado: {e}")
    
    print("\n❌ No se pudo autenticar con ningún usuario")
    return False

if __name__ == "__main__":
    test_login_y_endpoint()