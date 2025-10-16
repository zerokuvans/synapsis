#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la API directamente con el usuario 80833959
"""

import requests
import json

def test_api_obtener_usuario():
    """Probar la API obtener_usuario directamente"""
    print("🧪 PROBANDO API DIRECTAMENTE - USUARIO 80833959")
    print("="*60)
    
    # URL de la API
    url = "http://192.168.80.15:8080/obtener_usuario/1"
    
    try:
        print(f"📡 Haciendo petición GET a: {url}")
        
        # Hacer la petición
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Respuesta exitosa")
            
            # Intentar parsear JSON
            try:
                data = response.json()
                print("📤 RESPUESTA JSON:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Verificar específicamente las fechas
                print(f"\n📅 ANÁLISIS DE FECHAS:")
                print(f"   fecha_ingreso: '{data.get('fecha_ingreso')}' (tipo: {type(data.get('fecha_ingreso'))})")
                print(f"   fecha_retiro: '{data.get('fecha_retiro')}' (tipo: {type(data.get('fecha_retiro'))})")
                
                # Verificar si las fechas son válidas para input date
                fecha_ingreso = data.get('fecha_ingreso')
                if fecha_ingreso:
                    if isinstance(fecha_ingreso, str) and len(fecha_ingreso) == 10:
                        print(f"   ✅ fecha_ingreso tiene formato correcto para input date")
                    else:
                        print(f"   ❌ fecha_ingreso NO tiene formato correcto: {fecha_ingreso}")
                else:
                    print(f"   ⚠️  fecha_ingreso está vacía o es null")
                
            except json.JSONDecodeError as e:
                print(f"❌ Error parseando JSON: {e}")
                print(f"📄 Contenido de respuesta: {response.text[:500]}")
                
        else:
            print(f"❌ Error en la petición: {response.status_code}")
            print(f"📄 Contenido: {response.text[:500]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    
    print(f"\n🏁 PRUEBA COMPLETADA")
    print("="*60)

if __name__ == "__main__":
    test_api_obtener_usuario()