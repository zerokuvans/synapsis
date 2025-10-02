#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el endpoint /api/analistas/tecnicos-asignados corregido
que ahora debe incluir los campos hora_inicio, estado y novedad
"""

import requests
import json
from datetime import datetime

# Configuración del servidor
BASE_URL = "http://localhost:8080"
USERNAME = "80833959"  # Usuario administrativo
PASSWORD = "CE80833959"

def test_endpoint_analistas_tecnicos():
    """Probar el endpoint /api/analistas/tecnicos-asignados"""
    print("=== PRUEBA DEL ENDPOINT /api/analistas/tecnicos-asignados CORREGIDO ===")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Crear sesión
    session = requests.Session()
    
    # 1. Login
    print("[1] Realizando login...")
    try:
        # Obtener página de login
        session.get(f"{BASE_URL}/")
        
        # Realizar login
        login_data = {
            "username": USERNAME,
            "password": PASSWORD
        }
        
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        login_response = session.post(f"{BASE_URL}/", data=login_data, headers=headers, allow_redirects=True)
        
        if "dashboard" in login_response.url or session.cookies.get('session'):
            print("   ✅ Login exitoso")
        else:
            print("   ❌ Login fallido")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False
    
    # 2. Probar endpoint
    print("\n[2] Probando endpoint /api/analistas/tecnicos-asignados...")
    try:
        response = session.get(f"{BASE_URL}/api/analistas/tecnicos-asignados")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                if data.get('success'):
                    print(f"   ✅ Respuesta exitosa")
                    print(f"   📊 Analista: {data.get('analista')}")
                    print(f"   📊 Total técnicos: {data.get('total_tecnicos')}")
                    
                    tecnicos = data.get('tecnicos', [])
                    
                    if tecnicos:
                        print(f"\n[3] Verificando datos de asistencia en técnicos:")
                        
                        for i, tecnico in enumerate(tecnicos[:3], 1):  # Solo primeros 3
                            print(f"\n   Técnico {i}:")
                            print(f"      Nombre: {tecnico.get('tecnico')}")
                            print(f"      Cédula: {tecnico.get('cedula')}")
                            print(f"      Supervisor: {tecnico.get('supervisor')}")
                            
                            asistencia = tecnico.get('asistencia_hoy', {})
                            print(f"      Asistencia hoy:")
                            print(f"         Carpeta día: {asistencia.get('carpeta_dia')}")
                            print(f"         Hora inicio: {asistencia.get('hora_inicio')}")
                            print(f"         Estado: {asistencia.get('estado')}")
                            print(f"         Novedad: {asistencia.get('novedad')}")
                            print(f"         Tipificación: {asistencia.get('tipificacion')}")
                            
                            # Verificar si tiene datos de asistencia
                            if asistencia.get('hora_inicio') or asistencia.get('estado') or asistencia.get('novedad'):
                                print(f"         ✅ TIENE DATOS DE ASISTENCIA")
                            else:
                                print(f"         ⚠️  Sin datos de asistencia para hoy")
                        
                        # Buscar específicamente técnicos con datos conocidos
                        print(f"\n[4] Buscando técnicos con datos conocidos:")
                        tecnicos_con_datos = []
                        
                        for tecnico in tecnicos:
                            asistencia = tecnico.get('asistencia_hoy', {})
                            if asistencia.get('hora_inicio') or asistencia.get('estado') or asistencia.get('novedad'):
                                tecnicos_con_datos.append(tecnico)
                        
                        print(f"   📊 Técnicos con datos de asistencia: {len(tecnicos_con_datos)}")
                        
                        if tecnicos_con_datos:
                            print(f"   ✅ ENDPOINT FUNCIONANDO CORRECTAMENTE")
                            print(f"   📋 Ejemplos de técnicos con datos:")
                            
                            for tecnico in tecnicos_con_datos[:2]:
                                asistencia = tecnico.get('asistencia_hoy', {})
                                print(f"      - {tecnico.get('tecnico')} (Cédula: {tecnico.get('cedula')})")
                                print(f"        Hora: {asistencia.get('hora_inicio')}, Estado: {asistencia.get('estado')}, Novedad: {asistencia.get('novedad')}")
                        else:
                            print(f"   ⚠️  Ningún técnico tiene datos de asistencia para hoy")
                            print(f"   💡 Esto puede ser normal si no hay registros para la fecha actual")
                    else:
                        print(f"   ⚠️  No se encontraron técnicos asignados")
                        
                else:
                    print(f"   ❌ Error en respuesta: {data}")
                    
            except json.JSONDecodeError:
                print(f"   ❌ Respuesta no es JSON válido")
                print(f"   Primeros 200 caracteres: {response.text[:200]}...")
                
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Error al consultar endpoint: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_endpoint_analistas_tecnicos()