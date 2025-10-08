#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debuggear el problema de carga de firmas
"""

import requests
import mysql.connector
import json
from datetime import datetime

# Configuración
BASE_URL = 'http://localhost:8080'
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
    'autocommit': True
}

def verificar_dotaciones_firmadas():
    """Verificar qué dotaciones tienen firmas en la base de datos"""
    print("\n=== VERIFICANDO DOTACIONES FIRMADAS EN BD ===")
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Buscar dotaciones firmadas
        cursor.execute("""
            SELECT d.id_dotacion, d.cliente, d.firmado, d.fecha_firma, 
                   d.usuario_firma, ro.nombre as tecnico_nombre,
                   LENGTH(d.firma_imagen) as firma_size
            FROM dotaciones d
            LEFT JOIN recurso_operativo ro ON d.id_codigo_consumidor = ro.id_codigo_consumidor
            WHERE d.firmado = 1
            ORDER BY d.fecha_firma DESC
            LIMIT 10
        """)
        
        dotaciones = cursor.fetchall()
        
        if dotaciones:
            print(f"✅ Encontradas {len(dotaciones)} dotaciones firmadas:")
            for dot in dotaciones:
                print(f"  - ID: {dot['id_dotacion']}, Cliente: {dot['cliente']}, "
                      f"Técnico: {dot['tecnico_nombre']}, Fecha: {dot['fecha_firma']}, "
                      f"Tamaño firma: {dot['firma_size']} bytes")
        else:
            print("❌ No se encontraron dotaciones firmadas")
            
        connection.close()
        return dotaciones
        
    except Exception as e:
        print(f"❌ Error al verificar BD: {e}")
        return []

def test_login():
    """Probar el login y obtener cookies de sesión"""
    print("\n=== PROBANDO LOGIN ===")
    
    session = requests.Session()
    
    # Datos de login
    login_data = {
        'username': '80833959',
        'password': 'M4r14l4r@'
    }
    
    try:
        # Hacer login
        response = session.post(f'{BASE_URL}/', data=login_data)
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Cookies: {dict(session.cookies)}")
        
        if response.status_code == 200:
            # Verificar si hay redirección o contenido que indique éxito
            if 'dashboard' in response.text.lower() or 'bienvenido' in response.text.lower():
                print("✅ Login exitoso (detectado por contenido)")
                return session
            elif response.url != f'{BASE_URL}/':
                print(f"✅ Login exitoso (redirigido a: {response.url})")
                return session
            else:
                print("⚠️ Login posiblemente exitoso (status 200)")
                return session
        else:
            print(f"❌ Login falló con status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None

def test_firma_endpoint(session, id_dotacion):
    """Probar el endpoint de obtener firma"""
    print(f"\n=== PROBANDO ENDPOINT FIRMA PARA ID {id_dotacion} ===")
    
    try:
        response = session.get(f'{BASE_URL}/api/obtener-firma/{id_dotacion}')
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            print(f"Respuesta JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('success'):
                print("✅ Firma obtenida exitosamente")
                if 'firma_url' in data:
                    firma_size = len(data['firma_url'])
                    print(f"  - Tamaño URL firma: {firma_size} caracteres")
                    print(f"  - Técnico: {data.get('tecnico_nombre', 'N/A')}")
                    print(f"  - Fecha: {data.get('fecha_firma', 'N/A')}")
                    print(f"  - Cliente: {data.get('cliente', 'N/A')}")
                return True
            else:
                print(f"❌ Error en respuesta: {data.get('message', 'Sin mensaje')}")
                return False
                
        except json.JSONDecodeError:
            print(f"❌ Respuesta no es JSON válido: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error en request: {e}")
        return False

def main():
    print(f"🔍 DEBUG PROBLEMA DE FIRMAS - {datetime.now()}")
    print("=" * 60)
    
    # Paso 1: Verificar dotaciones firmadas en BD
    dotaciones_firmadas = verificar_dotaciones_firmadas()
    
    if not dotaciones_firmadas:
        print("\n❌ No hay dotaciones firmadas para probar")
        return
    
    # Paso 2: Hacer login
    session = test_login()
    
    if not session:
        print("\n❌ No se pudo hacer login")
        return
    
    # Paso 3: Probar endpoint con las dotaciones firmadas
    print(f"\n=== PROBANDO ENDPOINT CON {len(dotaciones_firmadas)} DOTACIONES ===")
    
    for dotacion in dotaciones_firmadas[:3]:  # Probar solo las primeras 3
        id_dotacion = dotacion['id_dotacion']
        success = test_firma_endpoint(session, id_dotacion)
        
        if success:
            print(f"✅ Dotación {id_dotacion}: OK")
        else:
            print(f"❌ Dotación {id_dotacion}: FALLO")
        
        print("-" * 40)
    
    print("\n🏁 Debug completado")

if __name__ == '__main__':
    main()