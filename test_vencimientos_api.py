#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar el API de vencimientos con credenciales correctas
"""

import requests
import json

def test_vencimientos_api():
    """Probar el API de vencimientos con credenciales correctas"""
    print("VERIFICANDO API DE VENCIMIENTOS")
    print("="*60)
    
    session = requests.Session()
    
    # Usar las credenciales proporcionadas por el usuario
    usuario = {'username': '80833959', 'password': 'M4r14l4r@'}
    
    print(f"Login con: {usuario['username']}")
    login_response = session.post('http://127.0.0.1:8080/', data=usuario)
    print(f"Status login: {login_response.status_code}")
    
    if login_response.status_code == 200:
        print("✅ Login exitoso")
        
        # Probar API de vencimientos
        print("📡 Probando API /api/mpa/vencimientos...")
        api_response = session.get('http://127.0.0.1:8080/api/mpa/vencimientos')
        print(f"Status API: {api_response.status_code}")
        
        if api_response.status_code == 200:
            data = api_response.json()
            print(f"📊 Respuesta del API: {type(data)}")
            
            # Verificar el tipo de respuesta
            if isinstance(data, dict) and 'vencimientos' in data:
                vencimientos = data['vencimientos']
                total_api = data.get('total', len(vencimientos))
                success = data.get('success', False)
                
                print(f"📊 Success: {success}")
                print(f"📊 Total reportado por API: {total_api}")
                print(f"📊 Total vencimientos en lista: {len(vencimientos)}")
                
                # Contar por tipo
                tipos = {}
                for item in vencimientos:
                    if isinstance(item, dict):
                        tipo = item.get('tipo', 'Desconocido')
                        tipos[tipo] = tipos.get(tipo, 0) + 1
                    else:
                        print(f"⚠️  Item no es diccionario: {type(item)} - {item}")
                
                print("📋 Distribución por tipo:")
                for tipo, count in tipos.items():
                    print(f"   {tipo}: {count}")
                
                # Mostrar algunos ejemplos
                print("\n📋 Ejemplos de vencimientos:")
                for i, item in enumerate(vencimientos[:5], 1):
                    if isinstance(item, dict):
                        placa = item.get('placa', 'N/A')
                        tipo = item.get('tipo', 'N/A')
                        fecha = item.get('fecha_vencimiento', 'N/A')
                        tecnico = item.get('tecnico_nombre', 'N/A')
                        print(f"   {i}. Tipo: {tipo}, Placa: {placa}, Técnico: {tecnico}, Fecha: {fecha}")
                    else:
                        print(f"   {i}. Item: {item}")
                
                # Verificar si tenemos los 249 registros esperados
                if total_api == 249 and len(vencimientos) == 249:
                    print("\n✅ CONFIRMADO: El API devuelve exactamente 249 vencimientos como esperado")
                    print("✅ CONFIRMADO: La lista contiene exactamente 249 vencimientos")
                else:
                    print(f"\n⚠️  DISCREPANCIA: Se esperaban 249 vencimientos")
                    print(f"   API reporta: {total_api}")
                    print(f"   Lista contiene: {len(vencimientos)}")
                
                return True, len(vencimientos), tipos
            elif isinstance(data, list):
                print(f"📊 Total vencimientos: {len(data)}")
                # Manejar respuesta como lista (código anterior)
                tipos = {}
                for item in data:
                    if isinstance(item, dict):
                        tipo = item.get('tipo', 'Desconocido')
                        tipos[tipo] = tipos.get(tipo, 0) + 1
                
                return True, len(data), tipos
            else:
                print(f"📊 Respuesta inesperada: {type(data)}")
                print(f"📊 Contenido: {data}")
                return True, 0, {}
        else:
            print(f"❌ Error API: {api_response.status_code}")
            if api_response.text:
                print(f"Response: {api_response.text[:200]}")
    else:
        print(f"❌ Error login: {login_response.status_code}")
        if login_response.text:
            print(f"Response: {login_response.text[:200]}")
    
    return False, 0, {}

if __name__ == "__main__":
    api_ok, total, tipos = test_vencimientos_api()
    
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print("="*60)
    print(f"API funciona: {'✅' if api_ok else '❌'}")
    if api_ok:
        print(f"Total vencimientos: {total}")
        print("Distribución por tipo:")
        for tipo, count in tipos.items():
            print(f"  - {tipo}: {count}")
        
        if total == 249:
            print("\n🎉 RESULTADO: El sistema está funcionando correctamente")
            print("   Todos los 249 vencimientos están siendo devueltos por el API")
        else:
            print(f"\n⚠️  ATENCIÓN: Hay una discrepancia en el número de vencimientos")
            print(f"   Esperados: 249, Obtenidos: {total}")
    else:
        print("❌ No se pudo verificar el API")