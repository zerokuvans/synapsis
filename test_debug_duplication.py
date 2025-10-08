#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el endpoint de asistencia y detectar duplicados
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración
BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"
API_URL = f"{BASE_URL}/api/operativo/inicio-operacion/asistencia"

# Credenciales
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"

def test_duplication_issue():
    """Probar el endpoint con diferentes fechas para detectar duplicados"""
    print("=" * 60)
    print("DIAGNÓSTICO DE DUPLICACIÓN - ENDPOINT ASISTENCIA")
    print("=" * 60)
    
    session = requests.Session()
    
    # 1. Login
    print("\n[1] Realizando login...")
    try:
        login_data = {
            "username": USERNAME,
            "password": PASSWORD
        }
        
        login_response = session.post(LOGIN_URL, data=login_data)
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("   ❌ Login fallido")
            return False
            
        print("   ✅ Login exitoso")
        
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False
    
    # 2. Probar con diferentes fechas
    fechas_prueba = [
        datetime.now().strftime('%Y-%m-%d'),  # Hoy
        (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),  # Ayer
        (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),  # Anteayer
        (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),  # 3 días atrás
        (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),  # 1 semana atrás
        "2024-10-08",  # Fecha del año pasado
        "2024-12-15",  # Fecha de diciembre 2024
        "2024-11-20",  # Fecha de noviembre 2024
    ]
    
    for fecha in fechas_prueba:
        print(f"\n[2] Probando fecha: {fecha}")
        try:
            params = {'fecha': fecha}
            response = session.get(API_URL, params=params)
            
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'No especificado')}")
            
            if response.status_code == 200 and 'application/json' in response.headers.get('content-type', ''):
                data = response.json()
                
                if data.get('success'):
                    registros = data.get('registros', [])
                    print(f"   📊 Total registros: {len(registros)}")
                    
                    if registros:
                        # Verificar duplicados por cédula
                        cedulas = [r.get('cedula') for r in registros]
                        cedulas_unicas = set(cedulas)
                        
                        print(f"   🔍 Cédulas únicas: {len(cedulas_unicas)}")
                        
                        if len(cedulas) != len(cedulas_unicas):
                            print("   🔴 ¡DUPLICADOS DETECTADOS EN BACKEND!")
                            
                            # Mostrar duplicados
                            from collections import Counter
                            contador = Counter(cedulas)
                            duplicados = {k: v for k, v in contador.items() if v > 1}
                            
                            for cedula, count in duplicados.items():
                                print(f"      Cédula {cedula}: {count} veces")
                                
                                # Mostrar registros duplicados
                                registros_dup = [r for r in registros if r.get('cedula') == cedula]
                                for i, reg in enumerate(registros_dup, 1):
                                    print(f"         Registro {i}: {reg.get('tecnico')} - {reg.get('carpeta_dia')}")
                        else:
                            print("   ✅ No hay duplicados en backend")
                            
                        # Mostrar muestra de registros
                        print(f"   📋 Muestra (primeros 3):")
                        for i, reg in enumerate(registros[:3], 1):
                            print(f"      {i}. {reg.get('cedula')} - {reg.get('tecnico')}")
                            
                        # Verificar estadísticas
                        stats = data.get('stats', {})
                        if stats:
                            print(f"   📈 Estadísticas:")
                            print(f"      Total técnicos: {stats.get('total_tecnicos', 0)}")
                            print(f"      Con asistencia: {stats.get('con_asistencia', 0)}")
                            print(f"      Sin asistencia: {stats.get('sin_asistencia', 0)}")
                    else:
                        print("   ⚠️ No hay registros para esta fecha")
                else:
                    print(f"   ❌ API reportó error: {data.get('message', 'Sin mensaje')}")
            else:
                print(f"   ❌ Respuesta no válida")
                print(f"   Contenido: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n{'=' * 60}")
    print("DIAGNÓSTICO COMPLETADO")
    print("Si se detectaron duplicados en el backend, el problema está en la consulta SQL.")
    print("Si no hay duplicados en el backend, el problema está en el frontend.")
    print("=" * 60)

if __name__ == "__main__":
    test_duplication_issue()