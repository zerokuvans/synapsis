#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para verificar el total de vencimientos del API
"""

import requests
import json

def main():
    print("=== Verificando API de vencimientos (simple) ===\n")
    
    try:
        # Hacer petición al API
        url = "http://127.0.0.1:8080/api/mpa/vencimientos"
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verificar estructura de la respuesta
            if 'data' in data:
                vencimientos = data['data']
                total = len(vencimientos)
                print(f"✅ Total de vencimientos devueltos: {total}")
                
                if 'estadisticas' in data:
                    stats = data['estadisticas']
                    print(f"📊 Estadísticas:")
                    print(f"   Total: {stats.get('total', 'N/A')}")
                    print(f"   Vencidos: {stats.get('vencidos', 'N/A')}")
                    print(f"   Próximos a vencer: {stats.get('proximos_vencer', 'N/A')}")
                    print(f"   Vigentes: {stats.get('vigentes', 'N/A')}")
                    print(f"   Sin fecha: {stats.get('sin_fecha', 'N/A')}")
                
                # Mostrar algunos ejemplos
                print(f"\n📋 Primeros 5 vencimientos:")
                for i, v in enumerate(vencimientos[:5]):
                    print(f"   {i+1}. {v.get('tipo', 'N/A')} - Placa: {v.get('placa', 'N/A')} - Fecha: {v.get('fecha_vencimiento', 'N/A')} - Estado: {v.get('estado', 'N/A')}")
                
                if total == 249:
                    print(f"\n🎉 ¡ÉXITO! El API ahora devuelve los 249 vencimientos esperados")
                elif total == 3:
                    print(f"\n❌ PROBLEMA: El API sigue devolviendo solo 3 vencimientos")
                else:
                    print(f"\n⚠️  PARCIAL: El API devuelve {total} vencimientos (esperados: 249)")
                    
            else:
                print(f"❌ Error: Respuesta no tiene estructura esperada")
                print(f"Claves disponibles: {list(data.keys())}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()