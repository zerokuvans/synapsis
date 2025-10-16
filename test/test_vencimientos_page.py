#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_vencimientos_page():
    """Probar la página de vencimientos y la API"""
    
    base_url = "http://127.0.0.1:8080"
    
    print("🔍 Probando módulo de vencimientos...")
    print("=" * 60)
    
    # 1. Probar API de vencimientos
    print("1. Probando API de vencimientos...")
    try:
        response = requests.get(f"{base_url}/api/mpa/vencimientos", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ API funcionando - {data.get('total', len(data.get('data', [])))} vencimientos encontrados")
                
                # Mostrar algunos datos de ejemplo
                vencimientos = data.get('data', [])[:3]  # Primeros 3
                for i, v in enumerate(vencimientos, 1):
                    print(f"   📋 Vencimiento {i}: {v.get('tipo')} - {v.get('placa', 'N/A')} - {v.get('estado')}")
            else:
                print(f"   ❌ Error en API: {data.get('error')}")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 2. Probar página HTML
    print("\n2. Probando página HTML...")
    try:
        response = requests.get(f"{base_url}/mpa/vencimientos", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if 'Control de Vencimientos - MPA' in content:
                print("   ✅ Página HTML cargando correctamente")
                print("   📄 Título encontrado: 'Control de Vencimientos - MPA'")
                
                # Verificar elementos clave
                elementos = [
                    ('tabla de vencimientos', 'vencimientosTable'),
                    ('filtros', 'filtroTipo'),
                    ('estadísticas', 'countTotal'),
                    ('modal de detalles', 'viewVencimientoModal')
                ]
                
                for nombre, elemento in elementos:
                    if elemento in content:
                        print(f"   ✅ {nombre.capitalize()} presente")
                    else:
                        print(f"   ⚠️ {nombre.capitalize()} no encontrado")
            else:
                print("   ❌ Contenido de página no reconocido")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            if response.status_code == 401:
                print("   🔐 Requiere autenticación")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 3. Probar API de detalles (si hay datos)
    print("\n3. Probando API de detalles...")
    try:
        # Primero obtener un vencimiento para probar
        response = requests.get(f"{base_url}/api/mpa/vencimientos", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                vencimiento = data['data'][0]  # Primer vencimiento
                tipo = vencimiento['tipo'].lower().replace(' ', '_').replace('é', 'e').replace('í', 'i')
                id_venc = vencimiento['id']
                
                detail_response = requests.get(f"{base_url}/api/mpa/vencimiento/{tipo}/{id_venc}", timeout=10)
                print(f"   Status: {detail_response.status_code}")
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    if detail_data.get('success'):
                        print(f"   ✅ API de detalles funcionando para {vencimiento['tipo']}")
                    else:
                        print(f"   ❌ Error en API de detalles: {detail_data.get('error')}")
                else:
                    print(f"   ❌ Error HTTP en detalles: {detail_response.status_code}")
            else:
                print("   ⚠️ No hay datos para probar detalles")
        
    except Exception as e:
        print(f"   ❌ Error probando detalles: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")

if __name__ == "__main__":
    test_vencimientos_page()