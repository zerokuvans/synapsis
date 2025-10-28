#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def main():
    print("🔍 Verificando API de vencimientos...")
    
    session = requests.Session()
    usuario = {'username': '80833959', 'password': 'M4r14l4r@'}
    
    # Login
    print("🔐 Iniciando sesión...")
    login_response = session.post('http://127.0.0.1:8080/', data=usuario)
    
    if login_response.status_code != 200:
        print(f"❌ ERROR LOGIN: {login_response.status_code}")
        return
    
    print("✅ Login exitoso")
    
    # Consultar API
    print("📡 Consultando API de vencimientos...")
    api_response = session.get('http://127.0.0.1:8080/api/mpa/vencimientos')
    
    if api_response.status_code != 200:
        print(f"❌ ERROR API: {api_response.status_code}")
        return
    
    print("✅ API respondió correctamente")
    
    # Procesar respuesta
    data = api_response.json()
    
    if 'data' not in data:
        print(f"❌ ERROR: No se encontró clave 'data'. Claves disponibles: {list(data.keys())}")
        return
    
    vencimientos = data['data']
    total = data.get('total', 0)
    
    # Contar por tipo
    tipos = {}
    for item in vencimientos:
        tipo = item.get('tipo', 'Desconocido')
        tipos[tipo] = tipos.get(tipo, 0) + 1
    
    # Mostrar resultados
    print("\n" + "="*50)
    print("📊 RESULTADO FINAL")
    print("="*50)
    print(f"Total vencimientos reportado por API: {total}")
    print(f"Vencimientos en lista: {len(vencimientos)}")
    print()
    print("📋 Distribución por tipo:")
    for tipo, count in tipos.items():
        print(f"  • {tipo}: {count}")
    print()
    
    if total == 249:
        print("✅ ÉXITO: El sistema muestra todos los 249 vencimientos correctamente")
    else:
        print(f"❌ PROBLEMA: Se esperaban 249, se obtuvieron {total}")
    
    print()
    print("📝 Ejemplos de vencimientos:")
    for i, item in enumerate(vencimientos[:3]):
        tipo = item.get('tipo', 'N/A')
        tecnico = item.get('tecnico_nombre', 'N/A')
        fecha = item.get('fecha_vencimiento', 'N/A')
        placa = item.get('placa', 'N/A')
        print(f"  {i+1}. {tipo} - {tecnico} - Vence: {fecha} - Placa: {placa}")

if __name__ == "__main__":
    main()