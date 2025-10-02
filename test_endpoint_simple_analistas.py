#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# Configuración
BASE_URL = "http://192.168.80.39:8080"

def test_endpoint():
    """Probar el endpoint de técnicos asignados"""
    session = requests.Session()
    
    try:
        # 1. Login
        print("🔐 Haciendo login...")
        login_data = {
            'cedula': '1002407090',
            'password': 'CE1002407090'
        }
        
        login_response = session.post(f"{BASE_URL}/", data=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code not in [200, 302]:
            print("❌ Login fallido")
            return
        
        # 2. Probar endpoint
        print("\n📊 Probando endpoint...")
        response = session.get(f"{BASE_URL}/api/analistas/tecnicos-asignados?fecha=2025-10-02")
        print(f"Endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Respuesta exitosa")
            print(f"Analista: {data.get('analista')}")
            print(f"Total técnicos: {data.get('total_tecnicos')}")
            
            # Mostrar primer técnico con detalle
            tecnicos = data.get('tecnicos', [])
            if tecnicos:
                primer_tecnico = tecnicos[0]
                print(f"\n👤 Primer técnico: {primer_tecnico.get('tecnico')}")
                
                asistencia = primer_tecnico.get('asistencia_hoy', {})
                print(f"📅 Asistencia:")
                print(f"   - Fecha: {asistencia.get('fecha_asistencia')}")
                print(f"   - Hora inicio: {asistencia.get('hora_inicio')}")
                print(f"   - Estado: {asistencia.get('estado')}")
                print(f"   - Novedad: {asistencia.get('novedad')}")
                print(f"   - Tipificación: {asistencia.get('tipificacion')}")
                
                # Verificar campos nuevos
                campos_nuevos = ['hora_inicio', 'estado', 'novedad']
                campos_presentes = [campo for campo in campos_nuevos if campo in asistencia]
                print(f"\n🔍 Campos nuevos presentes: {campos_presentes}")
                
                if len(campos_presentes) == 3:
                    print("✅ TODOS los campos nuevos están presentes")
                else:
                    print("⚠️  Faltan algunos campos nuevos")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text[:200])
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        session.close