#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para depurar el problema de carga de firmas en dotaciones
"""

import requests
import json
from datetime import datetime

def test_firma_endpoint():
    """Prueba el endpoint de obtener firma con diferentes IDs"""
    base_url = "http://127.0.0.1:8080"
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    print("=== PRUEBA DE ENDPOINT DE FIRMA ===")
    print(f"Fecha: {datetime.now()}")
    print(f"URL base: {base_url}")
    print()
    
    # Paso 1: Intentar login
    print("1. Intentando login...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        login_response = session.post(f"{base_url}/", data=login_data)
        print(f"   Status login: {login_response.status_code}")
        print(f"   Cookies después del login: {dict(session.cookies)}")
        
        # Verificar si hay redirección o contenido que indique login exitoso
        if 'dashboard' in login_response.text.lower() or login_response.status_code == 200:
            print("   ✓ Login aparentemente exitoso")
        else:
            print("   ⚠ Login puede haber fallado")
            
    except Exception as e:
        print(f"   ✗ Error en login: {e}")
        return
    
    print()
    
    # Paso 2: Probar endpoint de firma con diferentes IDs
    test_ids = [12, 13, 1, 2, 3]  # IDs conocidos y algunos de prueba
    
    for dotacion_id in test_ids:
        print(f"2. Probando firma para dotación ID: {dotacion_id}")
        
        try:
            # Probar endpoint de firma
            firma_url = f"{base_url}/api/obtener-firma/{dotacion_id}"
            print(f"   URL: {firma_url}")
            
            firma_response = session.get(firma_url)
            print(f"   Status: {firma_response.status_code}")
            print(f"   Headers: {dict(firma_response.headers)}")
            
            if firma_response.status_code == 200:
                try:
                    firma_data = firma_response.json()
                    print(f"   ✓ Respuesta JSON: {json.dumps(firma_data, indent=2, ensure_ascii=False)}")
                    
                    if firma_data.get('success'):
                        print(f"   ✓ Firma encontrada para dotación {dotacion_id}")
                        if 'firma_url' in firma_data:
                            print(f"   ✓ URL de firma: {firma_data['firma_url']}")
                        if 'fecha_firma' in firma_data:
                            print(f"   ✓ Fecha de firma: {firma_data['fecha_firma']}")
                    else:
                        print(f"   ⚠ Sin firma para dotación {dotacion_id}: {firma_data.get('message', 'Sin mensaje')}")
                        
                except json.JSONDecodeError:
                    print(f"   ⚠ Respuesta no es JSON válido: {firma_response.text[:200]}")
                    
            elif firma_response.status_code == 401:
                print(f"   ✗ Error de autenticación (401)")
                print(f"   Respuesta: {firma_response.text[:200]}")
                
            elif firma_response.status_code == 404:
                print(f"   ⚠ Firma no encontrada (404)")
                try:
                    error_data = firma_response.json()
                    print(f"   Mensaje: {error_data.get('message', 'Sin mensaje')}")
                except:
                    print(f"   Respuesta: {firma_response.text[:200]}")
                    
            else:
                print(f"   ✗ Error inesperado: {firma_response.status_code}")
                print(f"   Respuesta: {firma_response.text[:200]}")
                
        except Exception as e:
            print(f"   ✗ Error al probar dotación {dotacion_id}: {e}")
            
        print()
    
    # Paso 3: Verificar endpoint de detalles también
    print("3. Probando endpoint de detalles para comparación...")
    
    for dotacion_id in [12, 13]:  # Solo IDs que sabemos que existen
        try:
            detalle_url = f"{base_url}/api/dotacion_detalle/{dotacion_id}"
            print(f"   URL detalles: {detalle_url}")
            
            detalle_response = session.get(detalle_url)
            print(f"   Status detalles: {detalle_response.status_code}")
            
            if detalle_response.status_code == 200:
                try:
                    detalle_data = detalle_response.json()
                    if detalle_data.get('success'):
                        dotacion = detalle_data.get('dotacion', {})
                        print(f"   ✓ Detalles obtenidos para dotación {dotacion_id}")
                        print(f"   Técnico: {dotacion.get('tecnico_nombre', 'N/A')}")
                        print(f"   Cliente: {dotacion.get('cliente_nombre', 'N/A')}")
                    else:
                        print(f"   ⚠ Error en detalles: {detalle_data.get('message')}")
                except json.JSONDecodeError:
                    print(f"   ⚠ Respuesta de detalles no es JSON válido")
            else:
                print(f"   ✗ Error en detalles: {detalle_response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Error al obtener detalles de {dotacion_id}: {e}")
            
        print()

if __name__ == "__main__":
    test_firma_endpoint()