#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar que el endpoint de resumen de asistencia
solo cuenta registros con grupos válidos
"""

import requests
import json
from datetime import datetime, date

# Configuración
BASE_URL = 'http://127.0.0.1:5000'
USERNAME = 'vnaranjos'
PASSWORD = '732137A031E4b@'

def test_resumen_grupos_validos():
    """Probar que el resumen solo incluye grupos válidos"""
    
    print("=" * 60)
    print("PRUEBA: RESUMEN DE ASISTENCIA - SOLO GRUPOS VÁLIDOS")
    print("=" * 60)
    
    # Crear sesión
    session = requests.Session()
    
    # 1. Login
    print("\n1. Realizando login...")
    login_data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    
    login_response = session.post(f'{BASE_URL}/login', data=login_data)
    
    if login_response.status_code == 200:
        print("✓ Login exitoso")
    else:
        print(f"✗ Error en login: {login_response.status_code}")
        return
    
    # 2. Probar endpoint de resumen
    print("\n2. Probando endpoint de resumen agrupado...")
    
    fecha_hoy = date.today().strftime('%Y-%m-%d')
    url_resumen = f'{BASE_URL}/api/asistencia/resumen_agrupado?fecha_inicio={fecha_hoy}&fecha_fin={fecha_hoy}'
    
    print(f"URL: {url_resumen}")
    
    response = session.get(url_resumen)
    
    if response.status_code == 200:
        print("✓ Endpoint responde correctamente")
        
        try:
            data = response.json()
            
            if data.get('success'):
                print("✓ Respuesta exitosa del endpoint")
                
                # Analizar datos
                resumen_data = data.get('data', {})
                resumen_grupos = resumen_data.get('resumen_grupos', [])
                detallado = resumen_data.get('detallado', [])
                total_general = resumen_data.get('total_general', 0)
                
                print(f"\n📊 RESULTADOS DEL RESUMEN:")
                print(f"   Total general de técnicos: {total_general}")
                print(f"   Grupos encontrados: {len(resumen_grupos)}")
                print(f"   Registros detallados: {len(detallado)}")
                
                # Verificar que solo hay grupos válidos
                grupos_validos = {'ARREGLOS', 'AUSENCIA INJUSTIFICADA', 'AUSENCIA JUSTIFICADA', 'INSTALACIONES', 'POSTVENTA'}
                
                print(f"\n🔍 VALIDACIÓN DE GRUPOS:")
                grupos_encontrados = set()
                
                for grupo_info in resumen_grupos:
                    grupo = grupo_info.get('grupo')
                    tecnicos = grupo_info.get('total_tecnicos', 0)
                    porcentaje = grupo_info.get('porcentaje', 0)
                    
                    grupos_encontrados.add(grupo)
                    
                    if grupo in grupos_validos:
                        print(f"   ✓ {grupo}: {tecnicos} técnicos ({porcentaje}%)")
                    else:
                        print(f"   ✗ GRUPO INVÁLIDO: {grupo}: {tecnicos} técnicos ({porcentaje}%)")
                
                # Verificar que no hay grupos inválidos
                grupos_invalidos = grupos_encontrados - grupos_validos
                
                if not grupos_invalidos:
                    print(f"\n✅ VALIDACIÓN EXITOSA: Solo se encontraron grupos válidos")
                    print(f"   Grupos válidos encontrados: {sorted(grupos_encontrados)}")
                else:
                    print(f"\n❌ VALIDACIÓN FALLIDA: Se encontraron grupos inválidos")
                    print(f"   Grupos inválidos: {sorted(grupos_invalidos)}")
                
                # Mostrar detalle por carpeta
                if detallado:
                    print(f"\n📋 DETALLE POR CARPETA:")
                    for item in detallado:
                        grupo = item.get('grupo')
                        carpeta = item.get('carpeta')
                        tecnicos = item.get('total_tecnicos', 0)
                        porcentaje = item.get('porcentaje', 0)
                        
                        print(f"   {grupo} - {carpeta}: {tecnicos} técnicos ({porcentaje}%)")
                
            else:
                print(f"✗ Error en respuesta: {data.get('message')}")
                
        except json.JSONDecodeError:
            print("✗ Respuesta no es JSON válido")
            print(f"Contenido: {response.text[:500]}...")
            
    else:
        print(f"✗ Error en endpoint: {response.status_code}")
        print(f"Respuesta: {response.text[:500]}...")

if __name__ == '__main__':
    test_resumen_grupos_validos()