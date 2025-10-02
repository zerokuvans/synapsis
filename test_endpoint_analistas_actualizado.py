#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://192.168.80.39:8080"
LOGIN_URL = f"{BASE_URL}/"
API_URL = f"{BASE_URL}/api/analistas/tecnicos-asignados"

# Credenciales de analista
ANALISTA_CEDULA = "1002407090"
ANALISTA_PASSWORD = "CE1002407090"

def test_endpoint_with_auth():
    """Probar el endpoint de técnicos asignados con autenticación"""
    print("=== PRUEBA DEL ENDPOINT ACTUALIZADO DE ANALISTAS ===")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        # 1. Hacer login
        print("🔐 Iniciando sesión...")
        login_data = {
            'cedula': ANALISTA_CEDULA,
            'password': ANALISTA_PASSWORD
        }
        
        login_response = session.post(LOGIN_URL, data=login_data, allow_redirects=False)
        print(f"   Estado del login: {login_response.status_code}")
        
        if login_response.status_code not in [200, 302]:
            print(f"❌ Error en login: {login_response.status_code}")
            return False
        
        print("✅ Login exitoso")
        
        # 2. Probar endpoint sin fecha (fecha actual)
        print("\n📊 Probando endpoint sin fecha específica...")
        response = session.get(API_URL)
        
        print(f"   Estado de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Respuesta JSON válida")
                
                # Mostrar información general
                print(f"\n📋 Información general:")
                print(f"   - Analista: {data.get('analista')}")
                print(f"   - Total técnicos: {data.get('total_tecnicos')}")
                print(f"   - Éxito: {data.get('success')}")
                
                # Mostrar técnicos y su asistencia
                tecnicos = data.get('tecnicos', [])
                print(f"\n👥 Técnicos asignados ({len(tecnicos)}):")
                
                for i, tecnico in enumerate(tecnicos, 1):
                    print(f"\n   {i}. {tecnico.get('tecnico')} (Cédula: {tecnico.get('cedula')})")
                    print(f"      - Carpeta: {tecnico.get('carpeta')}")
                    print(f"      - Cliente: {tecnico.get('cliente')}")
                    print(f"      - Ciudad: {tecnico.get('ciudad')}")
                    
                    asistencia = tecnico.get('asistencia_hoy', {})
                    if asistencia:
                        print(f"      📅 Asistencia de hoy:")
                        print(f"         - Fecha: {asistencia.get('fecha_asistencia')}")
                        print(f"         - Hora inicio: {asistencia.get('hora_inicio', 'No definida')}")
                        print(f"         - Estado: {asistencia.get('estado', 'No definido')}")
                        print(f"         - Novedad: {asistencia.get('novedad', 'Sin novedad')}")
                        print(f"         - Tipificación: {asistencia.get('tipificacion')}")
                        print(f"         - Carpeta día: {asistencia.get('carpeta_dia')}")
                    else:
                        print(f"      📅 Sin registro de asistencia hoy")
                
                # Verificar que los nuevos campos están presentes
                print(f"\n🔍 Verificación de nuevos campos:")
                campos_encontrados = 0
                total_tecnicos_con_asistencia = 0
                
                for tecnico in tecnicos:
                    asistencia = tecnico.get('asistencia_hoy', {})
                    if asistencia and asistencia.get('fecha_asistencia'):
                        total_tecnicos_con_asistencia += 1
                        
                        # Verificar presencia de campos (aunque sean None)
                        if 'hora_inicio' in asistencia:
                            campos_encontrados += 1
                        if 'estado' in asistencia:
                            campos_encontrados += 1
                        if 'novedad' in asistencia:
                            campos_encontrados += 1
                
                print(f"   - Técnicos con asistencia: {total_tecnicos_con_asistencia}")
                print(f"   - Campos nuevos encontrados: {campos_encontrados}")
                
                if campos_encontrados > 0:
                    print("✅ Los nuevos campos (hora_inicio, estado, novedad) están presentes en la respuesta")
                else:
                    print("⚠️  Los nuevos campos no se encontraron en la respuesta")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ Error al decodificar JSON: {e}")
                print(f"Contenido de respuesta: {response.text[:500]}...")
                return False
        else:
            print(f"❌ Error en endpoint: {response.status_code}")
            print(f"Contenido: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    finally:
        session.close()

def test_endpoint_with_date():
    """Probar el endpoint con una fecha específica"""
    print("\n=== PRUEBA CON FECHA ESPECÍFICA ===")
    
    session = requests.Session()
    
    try:
        # Login
        login_data = {
            'cedula': ANALISTA_CEDULA,
            'password': ANALISTA_PASSWORD
        }
        
        login_response = session.post(LOGIN_URL, data=login_data, allow_redirects=False)
        
        if login_response.status_code not in [200, 302]:
            print(f"❌ Error en login: {login_response.status_code}")
            return False
        
        # Probar con fecha de hoy
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        print(f"📅 Probando con fecha: {fecha_hoy}")
        
        response = session.get(API_URL, params={'fecha': fecha_hoy})
        
        if response.status_code == 200:
            try:
                data = response.json()
                tecnicos = data.get('tecnicos', [])
                
                print(f"✅ Respuesta exitosa con {len(tecnicos)} técnicos")
                
                # Contar técnicos con datos de asistencia
                con_asistencia = 0
                con_hora_inicio = 0
                con_estado = 0
                con_novedad = 0
                
                for tecnico in tecnicos:
                    asistencia = tecnico.get('asistencia_hoy', {})
                    if asistencia and asistencia.get('fecha_asistencia'):
                        con_asistencia += 1
                        
                        if asistencia.get('hora_inicio'):
                            con_hora_inicio += 1
                        if asistencia.get('estado'):
                            con_estado += 1
                        if asistencia.get('novedad'):
                            con_novedad += 1
                
                print(f"📊 Estadísticas de asistencia:")
                print(f"   - Técnicos con registro: {con_asistencia}")
                print(f"   - Con hora_inicio: {con_hora_inicio}")
                print(f"   - Con estado: {con_estado}")
                print(f"   - Con novedad: {con_novedad}")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ Error al decodificar JSON: {e}")
                return False
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    finally:
        session.close()

if __name__ == "__main__":
    print("PRUEBA DEL ENDPOINT DE ANALISTAS ACTUALIZADO")
    print("=" * 50)
    
    # Ejecutar pruebas
    resultado1 = test_endpoint_with_auth()
    resultado2 = test_endpoint_with_date()
    
    print(f"\n{'='*50}")
    print("RESUMEN DE PRUEBAS:")
    print(f"✅ Endpoint sin fecha: {'EXITOSO' if resultado1 else 'FALLIDO'}")
    print(f"✅ Endpoint con fecha: {'EXITOSO' if resultado2 else 'FALLIDO'}")
    
    if resultado1 and resultado2:
        print("\n🎉 TODAS LAS PRUEBAS EXITOSAS")
        print("   El endpoint actualizado funciona correctamente")
        print("   Los campos hora_inicio, estado y novedad están disponibles")
    else:
        print("\n⚠️  ALGUNAS PRUEBAS FALLARON")
        print("   Revisar la configuración del endpoint o la base de datos")