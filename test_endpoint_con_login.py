#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar el endpoint /api/indicadores/estado_vehiculos con autenticación
"""

import requests
import json
from datetime import datetime

def test_endpoint_with_login():
    """Probar el endpoint de estado de vehículos con autenticación"""
    
    print("=== PRUEBA DEL ENDPOINT CON AUTENTICACIÓN ===")
    print(f"Fecha de prueba: {datetime.now()}")
    print()
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # URLs
    login_url = "http://localhost:8080/"
    endpoint_url = "http://localhost:8080/api/indicadores/estado_vehiculos"
    
    try:
        # Paso 1: Obtener la página de login para obtener el token CSRF si es necesario
        print("Paso 1: Obteniendo página de login...")
        login_page = session.get(login_url)
        print(f"Código de respuesta login page: {login_page.status_code}")
        
        # Paso 2: Intentar login con credenciales de administrador
        print("\nPaso 2: Intentando login...")
        
        # Datos de login usando la tabla recurso_operativo
        login_data = {
            'username': '12345678',  # Cédula del usuario de prueba
            'password': 'admin123'   # Contraseña del usuario de prueba
        }
        
        # Realizar login
        login_response = session.post(login_url, data=login_data)
        print(f"Código de respuesta login: {login_response.status_code}")
        
        # Verificar si el login fue exitoso
        if 'dashboard' in login_response.url or login_response.status_code == 302:
            print("✅ Login exitoso")
        else:
            print("❌ Login fallido")
            print(f"URL de respuesta: {login_response.url}")
            print("Contenido de respuesta (primeros 500 caracteres):")
            print(login_response.text[:500])
            return
        
        # Paso 3: Acceder al endpoint protegido
        print("\nPaso 3: Accediendo al endpoint protegido...")
        response = session.get(endpoint_url)
        
        print(f"Código de respuesta: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print()
        
        # Verificar el contenido de la respuesta
        if response.status_code == 200:
            if 'application/json' in response.headers.get('Content-Type', ''):
                try:
                    data = response.json()
                    print("=== RESPUESTA JSON ===")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    print()
                    
                    # Analizar la respuesta
                    if data.get('success'):
                        estadisticas = data.get('estadisticas', [])
                        print(f"✅ Endpoint funcionando correctamente")
                        print(f"📊 Se encontraron {len(estadisticas)} supervisores")
                        
                        if estadisticas:
                            print("\n=== PRIMEROS 5 SUPERVISORES ===")
                            for i, supervisor in enumerate(estadisticas[:5]):
                                print(f"{i+1}. {supervisor['supervisor']}: {supervisor['total']} vehículos")
                                print(f"   Bueno: {supervisor['bueno']}, Regular: {supervisor['regular']}, Malo: {supervisor['malo']}")
                        else:
                            print("⚠️  No se encontraron datos de supervisores")
                            print("💡 Esto indica que no hay registros en la tabla preoperacional para el mes actual")
                    else:
                        print(f"❌ Error en la respuesta: {data.get('error', 'Error desconocido')}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Error al decodificar JSON: {e}")
                    print(f"Contenido de la respuesta: {response.text[:500]}...")
            else:
                print("❌ La respuesta no es JSON")
                print(f"Contenido: {response.text[:500]}...")
                
        elif response.status_code == 401:
            print("❌ Error 401: No autorizado - Problema con la autenticación")
            
        elif response.status_code == 403:
            print("❌ Error 403: Prohibido - Sin permisos suficientes")
            print("💡 El usuario no tiene rol 'administrativo'")
            
        elif response.status_code == 500:
            print("❌ Error 500: Error interno del servidor")
            try:
                error_data = response.json()
                print(f"Detalles del error: {error_data}")
            except:
                print(f"Respuesta del servidor: {response.text[:500]}...")
        else:
            print(f"❌ Código de respuesta inesperado: {response.status_code}")
            print(f"Respuesta: {response.text[:500]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: No se pudo conectar al servidor")
        print("💡 Asegúrate de que el servidor Flask esté ejecutándose en localhost:8080")
        
    except requests.exceptions.Timeout:
        print("❌ Error de timeout: La petición tardó demasiado")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    print("\n=== FIN DE LA PRUEBA ===")

def test_direct_database_query():
    """Probar directamente la consulta a la base de datos"""
    
    print("\n=== PRUEBA DIRECTA A LA BASE DE DATOS ===")
    
    try:
        import mysql.connector
        from datetime import datetime, date
        
        # Configuración de la base de datos
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '732137A031E4b@',
            'database': 'capired'
        }
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Obtener fecha actual para filtrar por mes actual
        fecha_actual = date.today()
        primer_dia_mes = fecha_actual.replace(day=1)
        
        print(f"Consultando desde: {primer_dia_mes}")
        
        # Consultar preoperacionales del mes actual con supervisores
        query = """
            SELECT 
                supervisor,
                COUNT(*) as total_registros
            FROM preoperacional 
            WHERE DATE(fecha) >= %s 
                AND supervisor IS NOT NULL 
                AND supervisor != ''
            GROUP BY supervisor
            ORDER BY total_registros DESC
            LIMIT 10
        """
        
        cursor.execute(query, (primer_dia_mes,))
        resultados = cursor.fetchall()
        
        print(f"\n📊 Se encontraron {len(resultados)} supervisores con registros")
        
        if resultados:
            print("\n=== TOP 10 SUPERVISORES ===")
            for i, resultado in enumerate(resultados):
                print(f"{i+1}. {resultado['supervisor']}: {resultado['total_registros']} registros")
        else:
            print("⚠️  No se encontraron registros para el mes actual")
            
            # Verificar si hay registros en general
            cursor.execute("SELECT COUNT(*) as total FROM preoperacional")
            total_general = cursor.fetchone()['total']
            print(f"Total de registros en la tabla: {total_general}")
            
            if total_general > 0:
                cursor.execute("""
                    SELECT DATE(fecha) as fecha, COUNT(*) as registros 
                    FROM preoperacional 
                    GROUP BY DATE(fecha) 
                    ORDER BY fecha DESC 
                    LIMIT 5
                """)
                fechas_recientes = cursor.fetchall()
                print("\nÚltimas fechas con registros:")
                for fecha_reg in fechas_recientes:
                    print(f"  {fecha_reg['fecha']}: {fecha_reg['registros']} registros")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error en consulta directa: {e}")

if __name__ == "__main__":
    test_endpoint_with_login()
    test_direct_database_query()