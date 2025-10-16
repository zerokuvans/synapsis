#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_detail_api():
    """Probar la API de detalles específicamente"""
    
    base_url = "http://127.0.0.1:8080"
    
    print("🔍 Probando API de detalles de vencimientos...")
    print("=" * 60)
    
    # Primero obtener un vencimiento para probar
    try:
        response = requests.get(f"{base_url}/api/mpa/vencimientos", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                vencimiento = data['data'][0]  # Primer vencimiento
                print(f"📋 Vencimiento de prueba: {vencimiento['tipo']} - ID: {vencimiento['id']}")
                
                # Mapear tipos a nombres de API
                tipo_map = {
                    'SOAT': 'soat',
                    'Técnico Mecánica': 'tecnico_mecanica',
                    'Licencia de Conducir': 'licencia_conducir'
                }
                
                tipo_api = tipo_map.get(vencimiento['tipo'])
                if not tipo_api:
                    print(f"❌ Tipo no reconocido: {vencimiento['tipo']}")
                    return
                
                id_venc = vencimiento['id']
                detail_url = f"{base_url}/api/mpa/vencimiento/{tipo_api}/{id_venc}"
                
                print(f"🔗 URL de detalles: {detail_url}")
                
                detail_response = requests.get(detail_url, timeout=10)
                print(f"📊 Status: {detail_response.status_code}")
                print(f"📊 Headers: {dict(detail_response.headers)}")
                
                if detail_response.status_code == 200:
                    try:
                        detail_data = detail_response.json()
                        print(f"📊 Respuesta JSON: {json.dumps(detail_data, indent=2, ensure_ascii=False)}")
                        
                        if detail_data.get('success'):
                            print(f"✅ API de detalles funcionando correctamente")
                        else:
                            print(f"❌ Error en respuesta: {detail_data.get('error', 'Error desconocido')}")
                    except json.JSONDecodeError as e:
                        print(f"❌ Error decodificando JSON: {e}")
                        print(f"📄 Contenido de respuesta: {detail_response.text[:500]}")
                else:
                    print(f"❌ Error HTTP: {detail_response.status_code}")
                    print(f"📄 Contenido: {detail_response.text[:500]}")
            else:
                print("❌ No hay datos de vencimientos para probar")
        else:
            print(f"❌ Error obteniendo vencimientos: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_detail_api()