#!/usr/bin/env python3
import requests
import json

# Configuración
BASE_URL = "http://192.168.80.39:8080"
API_TECNICOS_URL = f"{BASE_URL}/api/analistas/tecnicos-asignados"

def test_endpoint_analistas():
    """Test directo del endpoint de analistas"""
    
    print("🧪 TEST DIRECTO DEL ENDPOINT DE ANALISTAS")
    print("=" * 50)
    
    try:
        # Crear sesión
        session = requests.Session()
        
        # 1. PROBAR ENDPOINT SIN AUTENTICACIÓN (para ver qué pasa)
        print("1. 🔍 Probando endpoint sin autenticación...")
        response = session.get(API_TECNICOS_URL)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Respuesta JSON válida")
                print(f"📊 Datos recibidos: {len(data) if isinstance(data, list) else 'No es lista'}")
                
                if isinstance(data, list) and len(data) > 0:
                    print("\n📝 Primeros 3 registros:")
                    for i, item in enumerate(data[:3], 1):
                        print(f"  {i}. {item}")
                
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
                print(f"Contenido: {response.text[:200]}...")
        
        elif response.status_code == 302:
            print("🔄 Redirección detectada (probablemente a login)")
            print(f"Location: {response.headers.get('Location', 'No especificada')}")
        
        elif response.status_code == 401:
            print("🔒 No autorizado - se requiere autenticación")
        
        elif response.status_code == 404:
            print("❌ Endpoint no encontrado")
        
        else:
            print(f"⚠️ Respuesta inesperada: {response.status_code}")
            print(f"Contenido: {response.text[:200]}...")
        
        # 2. PROBAR CON FECHA ESPECÍFICA
        print("\n2. 📅 Probando con fecha específica...")
        response_fecha = session.get(f"{API_TECNICOS_URL}?fecha=2025-10-02")
        
        print(f"Status Code: {response_fecha.status_code}")
        
        if response_fecha.status_code == 200:
            try:
                data_fecha = response_fecha.json()
                print(f"✅ Respuesta con fecha válida")
                print(f"📊 Datos recibidos: {len(data_fecha) if isinstance(data_fecha, list) else 'No es lista'}")
            except json.JSONDecodeError:
                print("❌ Respuesta con fecha no es JSON válido")
        
        # 3. VERIFICAR CONECTIVIDAD GENERAL
        print("\n3. 🌐 Verificando conectividad general...")
        home_response = session.get(BASE_URL)
        print(f"Página principal: {home_response.status_code}")
        
        # 4. VERIFICAR RUTA DE ANALISTAS
        print("\n4. 📋 Verificando ruta del módulo de analistas...")
        analistas_response = session.get(f"{BASE_URL}/analistas/inicio-operacion-tecnicos")
        print(f"Módulo analistas: {analistas_response.status_code}")
        
        if analistas_response.status_code == 200:
            print("✅ Módulo de analistas accesible")
        elif analistas_response.status_code == 302:
            print("🔄 Redirección a login requerida")
        
        print("\n" + "=" * 50)
        print("🎯 RESUMEN:")
        print(f"✅ Servidor funcionando: {home_response.status_code == 200}")
        print(f"✅ Endpoint API existe: {response.status_code != 404}")
        print(f"✅ Módulo analistas existe: {analistas_response.status_code != 404}")
        
        if response.status_code == 302 or response.status_code == 401:
            print("🔒 Se requiere autenticación para acceder al endpoint")
        elif response.status_code == 200:
            print("🎉 Endpoint accesible sin autenticación")
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_endpoint_analistas()