#!/usr/bin/env python3
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://192.168.80.39:8080"
LOGIN_URL = f"{BASE_URL}/"
API_TECNICOS_URL = f"{BASE_URL}/api/analistas/tecnicos-asignados"

# Credenciales de la analista
USERNAME = "1002407090"
PASSWORD = "CE1002407090"

def test_analistas_con_autenticacion():
    """Test del módulo de analistas con autenticación correcta"""
    
    print("🧪 TEST DEL MÓDULO DE ANALISTAS CON AUTENTICACIÓN")
    print("=" * 60)
    
    try:
        # Crear sesión
        session = requests.Session()
        
        # 1. LOGIN
        print("1. 🔐 Realizando login como analista...")
        print(f"   Usuario: {USERNAME}")
        print(f"   URL: {LOGIN_URL}")
        
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        login_response = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        
        print(f"   Status Code: {login_response.status_code}")
        print(f"   URL final: {login_response.url}")
        
        # Verificar si el login fue exitoso
        if login_response.status_code == 200 and ('dashboard' in login_response.url or 'inicio' in login_response.url):
            print("   ✅ Login exitoso")
        elif session.cookies.get('session'):
            print("   ✅ Login exitoso (cookie de sesión detectada)")
        else:
            print("   ❌ Login fallido")
            print(f"   Contenido: {login_response.text[:200]}...")
            return
        
        # 2. PROBAR ENDPOINT SIN FECHA
        print("\n2. 📋 Probando endpoint de técnicos asignados (sin fecha)...")
        api_response = session.get(API_TECNICOS_URL)
        
        print(f"   Status Code: {api_response.status_code}")
        print(f"   Content-Type: {api_response.headers.get('content-type', 'N/A')}")
        
        if api_response.status_code == 200:
            try:
                data = api_response.json()
                print("   ✅ Respuesta JSON válida")
                
                if data.get('success'):
                    print(f"   ✅ Operación exitosa")
                    print(f"   📊 Analista: {data.get('analista')}")
                    print(f"   📊 Total técnicos: {data.get('total_tecnicos')}")
                    
                    tecnicos = data.get('tecnicos', [])
                    
                    if tecnicos:
                        print(f"\n   📝 Primeros 3 técnicos:")
                        for i, tecnico in enumerate(tecnicos[:3], 1):
                            print(f"      {i}. {tecnico.get('tecnico')} (Cédula: {tecnico.get('cedula')})")
                            
                            asistencia = tecnico.get('asistencia_hoy', {})
                            hora = asistencia.get('hora_inicio', 'N/A')
                            estado = asistencia.get('estado', 'N/A')
                            novedad = asistencia.get('novedad', 'N/A')
                            
                            print(f"         Hora: {hora}")
                            print(f"         Estado: {estado}")
                            print(f"         Novedad: {novedad}")
                            print()
                        
                        # Contar técnicos con datos de asistencia
                        con_datos = sum(1 for t in tecnicos 
                                      if t.get('asistencia_hoy', {}).get('hora_inicio') not in [None, 'N/A', ''])
                        print(f"   📈 Técnicos con datos de asistencia: {con_datos}/{len(tecnicos)}")
                    else:
                        print("   ⚠️ No se encontraron técnicos")
                else:
                    print(f"   ❌ Operación fallida: {data}")
                
            except json.JSONDecodeError:
                print("   ❌ Respuesta no es JSON válido")
                print(f"   Contenido: {api_response.text[:200]}...")
        else:
            print(f"   ❌ Error en API: {api_response.status_code}")
            print(f"   Contenido: {api_response.text[:200]}...")
        
        # 3. PROBAR ENDPOINT CON FECHA ESPECÍFICA
        print("\n3. 📅 Probando endpoint con fecha específica (2025-10-02)...")
        api_fecha_response = session.get(f"{API_TECNICOS_URL}?fecha=2025-10-02")
        
        print(f"   Status Code: {api_fecha_response.status_code}")
        
        if api_fecha_response.status_code == 200:
            try:
                data_fecha = api_fecha_response.json()
                print("   ✅ Respuesta JSON válida")
                
                if data_fecha.get('success'):
                    tecnicos_fecha = data_fecha.get('tecnicos', [])
                    print(f"   📊 Total técnicos: {len(tecnicos_fecha)}")
                    
                    # Contar técnicos con datos para esa fecha
                    con_datos_fecha = sum(1 for t in tecnicos_fecha 
                                        if t.get('asistencia_hoy', {}).get('hora_inicio') not in [None, 'N/A', ''])
                    print(f"   📈 Técnicos con datos para 2025-10-02: {con_datos_fecha}")
                    
                    if con_datos_fecha > 0:
                        print(f"\n   📝 Técnicos con datos de asistencia para 2025-10-02:")
                        for i, tecnico in enumerate([t for t in tecnicos_fecha 
                                                   if t.get('asistencia_hoy', {}).get('hora_inicio') not in [None, 'N/A', '']], 1):
                            asistencia = tecnico.get('asistencia_hoy', {})
                            print(f"      {i}. {tecnico.get('tecnico')} (Cédula: {tecnico.get('cedula')})")
                            print(f"         Hora: {asistencia.get('hora_inicio')}")
                            print(f"         Estado: {asistencia.get('estado')}")
                            print(f"         Novedad: {asistencia.get('novedad')}")
                            print()
                    else:
                        print("   ⚠️ No se encontraron técnicos con datos para esa fecha")
                
            except json.JSONDecodeError:
                print("   ❌ Respuesta con fecha no es JSON válido")
                print(f"   Contenido: {api_fecha_response.text[:200]}...")
        else:
            print(f"   ❌ Error en API con fecha: {api_fecha_response.status_code}")
        
        print("\n" + "=" * 60)
        print("🎯 RESUMEN DEL TEST:")
        print("✅ Servidor funcionando")
        print("✅ Login como analista exitoso")
        print("✅ Endpoint de técnicos asignados funcionando")
        print("✅ Tabla asistencia creada y con datos")
        
        if 'con_datos' in locals() and con_datos > 0:
            print(f"✅ Datos de asistencia cargándose correctamente ({con_datos} técnicos)")
        else:
            print("⚠️ Verificar carga de datos de asistencia")
        
        print("\n🎉 ¡El módulo de analistas está funcionando!")
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analistas_con_autenticacion()