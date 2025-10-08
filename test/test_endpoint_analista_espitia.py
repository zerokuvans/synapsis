#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el endpoint /api/analistas/tecnicos-asignados 
con la analista ESPITIA BARON LICED JOANA
"""

import requests
import json
from datetime import datetime

# Configuración del servidor
BASE_URL = "http://localhost:8080"
USERNAME = "1002407090"  # Cédula de ESPITIA BARON LICED JOANA
PASSWORD = "CE1002407090"  # Contraseña por defecto

def test_endpoint_con_analista():
    """Probar el endpoint con credenciales de analista"""
    print("=== PRUEBA DEL ENDPOINT /api/analistas/tecnicos-asignados ===")
    print(f"Analista: ESPITIA BARON LICED JOANA")
    print(f"Cédula: {USERNAME}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Crear sesión
    session = requests.Session()
    
    # 1. Login
    print("[1] Realizando login...")
    try:
        # Obtener página de login
        login_page = session.get(f"{BASE_URL}/")
        print(f"   Página de login: {login_page.status_code}")
        
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
        print(f"   Login response: {login_response.status_code}")
        print(f"   URL final: {login_response.url}")
        
        if "dashboard" in login_response.url or session.cookies.get('session'):
            print("   ✅ Login exitoso")
        else:
            print("   ❌ Login fallido")
            print(f"   Respuesta: {login_response.text[:200]}...")
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
                        print(f"\n[3] Verificando estructura de datos:")
                        
                        # Mostrar estructura del primer técnico
                        primer_tecnico = tecnicos[0]
                        print(f"   📋 Estructura del primer técnico:")
                        print(f"      Nombre: {primer_tecnico.get('tecnico')}")
                        print(f"      Cédula: {primer_tecnico.get('cedula')}")
                        print(f"      Supervisor: {primer_tecnico.get('supervisor')}")
                        print(f"      Carpeta: {primer_tecnico.get('carpeta')}")
                        
                        asistencia = primer_tecnico.get('asistencia_hoy', {})
                        print(f"      Asistencia hoy:")
                        print(f"         Carpeta día: {asistencia.get('carpeta_dia')}")
                        print(f"         Hora inicio: {asistencia.get('hora_inicio')}")
                        print(f"         Estado: {asistencia.get('estado')}")
                        print(f"         Novedad: {asistencia.get('novedad')}")
                        print(f"         Tipificación: {asistencia.get('tipificacion')}")
                        
                        # Verificar si los campos están presentes
                        campos_requeridos = ['hora_inicio', 'estado', 'novedad']
                        campos_presentes = []
                        
                        for campo in campos_requeridos:
                            if campo in asistencia:
                                campos_presentes.append(campo)
                                print(f"         ✅ Campo '{campo}': PRESENTE")
                            else:
                                print(f"         ❌ Campo '{campo}': AUSENTE")
                        
                        if len(campos_presentes) == len(campos_requeridos):
                            print(f"\n   ✅ TODOS LOS CAMPOS REQUERIDOS ESTÁN PRESENTES")
                            print(f"   🎯 El endpoint ha sido corregido exitosamente")
                        else:
                            print(f"\n   ❌ FALTAN CAMPOS: {len(campos_requeridos) - len(campos_presentes)}")
                        
                        # Mostrar todos los técnicos
                        print(f"\n[4] Lista completa de técnicos asignados:")
                        for i, tecnico in enumerate(tecnicos, 1):
                            asistencia = tecnico.get('asistencia_hoy', {})
                            print(f"   {i}. {tecnico.get('tecnico')} (Cédula: {tecnico.get('cedula')})")
                            print(f"      Supervisor: {tecnico.get('supervisor')}")
                            
                            if asistencia.get('hora_inicio') or asistencia.get('estado') or asistencia.get('novedad'):
                                print(f"      ✅ Con datos de asistencia:")
                                print(f"         Hora: {asistencia.get('hora_inicio')}")
                                print(f"         Estado: {asistencia.get('estado')}")
                                print(f"         Novedad: {asistencia.get('novedad')}")
                            else:
                                print(f"      ⚪ Sin datos de asistencia para hoy")
                            print()
                    else:
                        print(f"   ⚠️  No se encontraron técnicos asignados")
                        
                else:
                    print(f"   ❌ Error en respuesta: {data}")
                    
            except json.JSONDecodeError:
                print(f"   ❌ Respuesta no es JSON válido")
                print(f"   Primeros 500 caracteres: {response.text[:500]}...")
                
        elif response.status_code == 401:
            print(f"   ❌ Error de autenticación - Usuario no autorizado")
            print(f"   💡 Verificar que el usuario tenga permisos de analista")
            
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Error al consultar endpoint: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_endpoint_con_analista()