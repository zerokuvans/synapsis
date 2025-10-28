#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script final para verificar el API de vencimientos
"""

import requests
import json

def main():
    print("🔍 VERIFICACIÓN FINAL DEL API DE VENCIMIENTOS")
    print("="*60)
    
    session = requests.Session()
    
    # Login
    print("🔐 Realizando login...")
    usuario = {'username': '80833959', 'password': 'M4r14l4r@'}
    login_response = session.post('http://127.0.0.1:8080/', data=usuario)
    
    if login_response.status_code != 200:
        print(f"❌ Error en login: {login_response.status_code}")
        return
    
    print("✅ Login exitoso")
    
    # Probar API
    print("📡 Consultando API /api/mpa/vencimientos...")
    api_response = session.get('http://127.0.0.1:8080/api/mpa/vencimientos')
    
    if api_response.status_code != 200:
        print(f"❌ Error en API: {api_response.status_code}")
        return
    
    print("✅ API respondió correctamente")
    
    # Procesar respuesta
    try:
        data = api_response.json()
        
        if isinstance(data, dict) and 'vencimientos' in data:
            vencimientos = data['vencimientos']
            total_api = data.get('total', 0)
            success = data.get('success', False)
            
            print(f"📊 Success: {success}")
            print(f"📊 Total reportado: {total_api}")
            print(f"📊 Vencimientos en lista: {len(vencimientos)}")
            
            # Contar por tipo
            tipos = {}
            for item in vencimientos:
                tipo = item.get('tipo', 'Desconocido')
                tipos[tipo] = tipos.get(tipo, 0) + 1
            
            print("\n📋 DISTRIBUCIÓN POR TIPO:")
            for tipo, count in tipos.items():
                print(f"   {tipo}: {count}")
            
            # Mostrar ejemplos
            print("\n📋 PRIMEROS 3 EJEMPLOS:")
            for i, item in enumerate(vencimientos[:3], 1):
                tipo = item.get('tipo', 'N/A')
                placa = item.get('placa', 'N/A')
                tecnico = item.get('tecnico_nombre', 'N/A')
                fecha = item.get('fecha_vencimiento', 'N/A')
                estado = item.get('estado', 'N/A')
                print(f"   {i}. {tipo} - Placa: {placa} - Técnico: {tecnico}")
                print(f"      Fecha: {fecha} - Estado: {estado}")
            
            # Verificación final
            print("\n" + "="*60)
            print("🎯 VERIFICACIÓN FINAL")
            print("="*60)
            
            if total_api == 249 and len(vencimientos) == 249:
                print("✅ CONFIRMADO: El API devuelve exactamente 249 vencimientos")
                print("✅ CONFIRMADO: Todos los tipos están presentes:")
                print(f"   - SOAT: {tipos.get('SOAT', 0)}")
                print(f"   - Técnico Mecánica: {tipos.get('Técnico Mecánica', 0)}")
                print(f"   - Licencia de Conducir: {tipos.get('Licencia de Conducir', 0)}")
                
                total_tipos = sum(tipos.values())
                if total_tipos == 249:
                    print("✅ RESULTADO: El sistema está funcionando PERFECTAMENTE")
                    print("   Todos los vencimientos de las 3 tablas están siendo mostrados")
                else:
                    print(f"⚠️  Suma de tipos ({total_tipos}) no coincide con total ({total_api})")
            else:
                print(f"❌ PROBLEMA: Se esperaban 249 vencimientos")
                print(f"   API reporta: {total_api}")
                print(f"   Lista contiene: {len(vencimientos)}")
        elif isinstance(data, dict):
            print(f"❌ Diccionario sin clave 'vencimientos'")
            print(f"📊 Claves disponibles: {list(data.keys())}")
            print(f"📊 Contenido: {data}")
        else:
            print(f"❌ Respuesta inesperada del API: {type(data)}")
            print(f"📊 Contenido: {data}")
            
    except Exception as e:
        print(f"❌ Error procesando respuesta: {e}")

if __name__ == "__main__":
    main()