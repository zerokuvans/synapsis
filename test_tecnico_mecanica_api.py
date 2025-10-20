#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el endpoint API de Técnico Mecánica
"""

import requests
import json
from datetime import datetime

def test_tecnico_mecanica_api():
    """Probar el endpoint de Técnico Mecánica"""
    
    # URL del endpoint
    base_url = "http://localhost:8080"
    
    print("=" * 60)
    print("PROBANDO API DE TÉCNICO MECÁNICA")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        # 1. Intentar acceder al endpoint sin autenticación
        print("1. Probando endpoint sin autenticación...")
        response = session.get(f"{base_url}/api/mpa/tecnico_mecanica")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("   ✅ Respuesta JSON válida")
                
                if data.get('success'):
                    tecnico_mecanicas = data.get('data', [])
                    print(f"   📊 Total registros: {len(tecnico_mecanicas)}")
                    
                    if tecnico_mecanicas:
                        print("\n   📋 Primeros 3 registros:")
                        for i, tm in enumerate(tecnico_mecanicas[:3]):
                            print(f"      {i+1}. Placa: {tm.get('placa')} - Estado: {tm.get('estado')}")
                            print(f"         Fecha Vencimiento: {tm.get('fecha_vencimiento')}")
                            print(f"         Días Restantes: {tm.get('dias_vencimiento')}")
                            print(f"         Técnico: {tm.get('tecnico_nombre', 'Sin asignar')}")
                            print()
                    else:
                        print("   ⚠️ No se encontraron registros")
                else:
                    print(f"   ❌ Operación fallida: {data.get('message', 'Error desconocido')}")
                
            except json.JSONDecodeError:
                print("   ❌ Respuesta no es JSON válido")
                print(f"   Contenido: {response.text[:200]}...")
                
        elif response.status_code == 302 or response.status_code == 401:
            print("   🔒 Requiere autenticación - redirigiendo al login")
            print("   Esto es normal para endpoints protegidos")
            
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            print(f"   Contenido: {response.text[:200]}...")
        
        # 2. Verificar estructura de la respuesta si es exitosa
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success') and data.get('data'):
                    print("\n2. Verificando estructura de datos...")
                    primer_registro = data['data'][0]
                    
                    campos_esperados = [
                        'id_mpa_tecnico_mecanica', 'placa', 'fecha_inicio', 
                        'fecha_vencimiento', 'tecnico_asignado', 'estado',
                        'observaciones', 'fecha_creacion', 'fecha_actualizacion',
                        'dias_vencimiento', 'tecnico_nombre'
                    ]
                    
                    print("   📋 Campos presentes:")
                    for campo in campos_esperados:
                        valor = primer_registro.get(campo)
                        estado = "✅" if campo in primer_registro else "❌"
                        print(f"      {estado} {campo}: {valor}")
                        
            except Exception as e:
                print(f"   ❌ Error verificando estructura: {e}")
        
        print("\n" + "=" * 60)
        print("RESUMEN:")
        print(f"- Endpoint accesible: {'✅' if response.status_code in [200, 302, 401] else '❌'}")
        print(f"- Respuesta JSON: {'✅' if response.status_code == 200 else '🔒 Requiere auth'}")
        print(f"- Datos disponibles: {'✅' if response.status_code == 200 and response.json().get('success') else '🔒 Requiere auth'}")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - Verificar que el servidor esté ejecutándose")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_tecnico_