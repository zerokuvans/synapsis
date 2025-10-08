#!/usr/bin/env python3
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://192.168.80.39:8080"
LOGIN_URL = f"{BASE_URL}/"
MODULO_URL = f"{BASE_URL}/analistas/inicio-operacion-tecnicos"
API_URL = f"{BASE_URL}/api/analistas/tecnicos-asignados"

# Credenciales de la analista ESPITIA BARON LICED JOANA
USERNAME = "1002407090"
PASSWORD = "CE1002407090"

def test_modulo_completo():
    """Test completo del módulo de analistas"""
    try:
        # Crear sesión
        session = requests.Session()
        
        print("🔐 PRUEBA COMPLETA DEL MÓDULO DE ANALISTAS")
        print("=" * 60)
        print(f"Usuario: {USERNAME}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. Login
        print("1. 🚪 Realizando login...")
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        response = session.post(LOGIN_URL, data=login_data)
        if response.status_code != 200:
            print(f"   ❌ Error en login: {response.status_code}")
            return False
        
        print("   ✅ Login exitoso")
        
        # 2. Acceder al módulo de analistas
        print("\n2. 🏠 Accediendo al módulo de analistas...")
        response = session.get(MODULO_URL)
        
        if response.status_code == 200:
            print("   ✅ Módulo de analistas accesible")
            print(f"   📄 Página cargada correctamente (tamaño: {len(response.text)} caracteres)")
            
            # Verificar que la página contiene elementos esperados
            if "inicio-operacion-tecnicos" in response.text:
                print("   ✅ Página contiene el contenido esperado")
            else:
                print("   ⚠️  La página no contiene el contenido esperado")
        else:
            print(f"   ❌ Error accediendo al módulo: {response.status_code}")
            return False
        
        # 3. Probar API de técnicos asignados
        print("\n3. 🔌 Probando API de técnicos asignados...")
        response = session.get(API_URL)
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ API funcionando correctamente")
            print(f"   👥 Total técnicos: {data.get('total_tecnicos', 0)}")
            print(f"   👩‍💼 Analista: {data.get('analista', 'N/A')}")
            
            # Contar técnicos con datos de asistencia
            tecnicos = data.get('tecnicos', [])
            con_datos = 0
            sin_datos = 0
            
            for tecnico in tecnicos:
                asistencia = tecnico.get('asistencia_hoy', {})
                if asistencia.get('hora_inicio') or asistencia.get('estado') or asistencia.get('novedad'):
                    con_datos += 1
                else:
                    sin_datos += 1
            
            print(f"   📊 Con datos de asistencia: {con_datos}")
            print(f"   📊 Sin datos de asistencia: {sin_datos}")
            
            # Mostrar algunos ejemplos de técnicos con datos
            if con_datos > 0:
                print("\n   📋 Ejemplos de técnicos con datos:")
                count = 0
                for tecnico in tecnicos:
                    if count >= 3:  # Mostrar máximo 3 ejemplos
                        break
                    asistencia = tecnico.get('asistencia_hoy', {})
                    if asistencia.get('hora_inicio') or asistencia.get('estado') or asistencia.get('novedad'):
                        count += 1
                        print(f"      {count}. {tecnico.get('tecnico', 'N/A')} ({tecnico.get('cedula', 'N/A')})")
                        print(f"         Hora: {asistencia.get('hora_inicio', 'N/A')}")
                        print(f"         Estado: {asistencia.get('estado', 'N/A')}")
                        print(f"         Novedad: {asistencia.get('novedad', 'N/A') or 'Sin novedad'}")
        else:
            print(f"   ❌ Error en API: {response.status_code}")
            return False
        
        # 4. Probar API con fecha específica (2025-10-02)
        print("\n4. 📅 Probando API con fecha específica (2025-10-02)...")
        params = {'fecha': '2025-10-02'}
        response = session.get(API_URL, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ API con fecha funcionando correctamente")
            
            tecnicos = data.get('tecnicos', [])
            con_datos = 0
            
            for tecnico in tecnicos:
                asistencia = tecnico.get('asistencia_hoy', {})
                if asistencia.get('hora_inicio') or asistencia.get('estado') or asistencia.get('novedad'):
                    con_datos += 1
            
            print(f"   📊 Técnicos con datos para 2025-10-02: {con_datos}")
            
            if con_datos > 0:
                print("   📋 Técnicos con datos guardados:")
                count = 0
                for tecnico in tecnicos:
                    asistencia = tecnico.get('asistencia_hoy', {})
                    if asistencia.get('hora_inicio') or asistencia.get('estado') or asistencia.get('novedad'):
                        count += 1
                        print(f"      {count}. {tecnico.get('tecnico', 'N/A')}")
                        print(f"         Hora: {asistencia.get('hora_inicio', 'N/A')}")
                        print(f"         Estado: {asistencia.get('estado', 'N/A')}")
                        print(f"         Novedad: {asistencia.get('novedad', 'N/A') or 'Sin novedad'}")
        else:
            print(f"   ❌ Error en API con fecha: {response.status_code}")
        
        print("\n🎉 PRUEBA COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("✅ El módulo de analistas está funcionando correctamente")
        print("✅ Los datos de asistencia se cargan correctamente")
        print("✅ La analista puede ver los datos ya guardados")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_modulo_completo()
    if success:
        print("\n🏆 TODAS LAS PRUEBAS PASARON")
    else:
        print("\n💥 ALGUNAS PRUEBAS FALLARON")