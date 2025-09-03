import mysql.connector
from mysql.connector import Error
import requests
import json
from datetime import datetime, timedelta

print("=== TEST FINAL: Verificación completa de vencimientos ===")

# 1. VERIFICAR DATOS EN BASE DE DATOS
print("\n1. VERIFICANDO DATOS EN BASE DE DATOS:")
try:
    connection = mysql.connector.connect(
        host='localhost',
        database='capired',
        user='root',
        password='732137A031E4b@',
        port=3306
    )
    
    if connection.is_connected():
        print("   ✓ Conexión exitosa a MySQL")
        cursor = connection.cursor(dictionary=True)
        
        # Verificar usuarios
        cursor.execute("SELECT COUNT(*) as total FROM recurso_operativo")
        total_usuarios = cursor.fetchone()['total']
        print(f"   ✓ Total usuarios: {total_usuarios}")
        
        # Verificar vehículos
        cursor.execute("SELECT COUNT(*) as total FROM parque_automotor")
        total_vehiculos = cursor.fetchone()['total']
        print(f"   ✓ Total vehículos: {total_vehiculos}")
        
        # Verificar vehículos con fechas de vencimiento válidas
        cursor.execute("""
            SELECT COUNT(*) as con_soat 
            FROM parque_automotor 
            WHERE soat_vencimiento IS NOT NULL 
              AND soat_vencimiento != '0000-00-00'
              AND soat_vencimiento > '1900-01-01'
        """)
        con_soat = cursor.fetchone()['con_soat']
        
        cursor.execute("""
            SELECT COUNT(*) as con_tecno 
            FROM parque_automotor 
            WHERE tecnomecanica_vencimiento IS NOT NULL 
              AND tecnomecanica_vencimiento != '0000-00-00'
              AND tecnomecanica_vencimiento > '1900-01-01'
        """)
        con_tecno = cursor.fetchone()['con_tecno']
        
        print(f"   ✓ Vehículos con SOAT válido: {con_soat}")
        print(f"   ✓ Vehículos con Tecnomecánica válida: {con_tecno}")
        
        # Mostrar ejemplos de vehículos con vencimientos
        if con_soat > 0 or con_tecno > 0:
            cursor.execute("""
                SELECT placa, tipo_vehiculo, soat_vencimiento, tecnomecanica_vencimiento
                FROM parque_automotor 
                WHERE (soat_vencimiento IS NOT NULL AND soat_vencimiento != '0000-00-00' AND soat_vencimiento > '1900-01-01')
                   OR (tecnomecanica_vencimiento IS NOT NULL AND tecnomecanica_vencimiento != '0000-00-00' AND tecnomecanica_vencimiento > '1900-01-01')
                LIMIT 3
            """)
            ejemplos = cursor.fetchall()
            print("   Ejemplos de vehículos:")
            for vehiculo in ejemplos:
                print(f"     - Placa: {vehiculo['placa']}, SOAT: {vehiculo['soat_vencimiento']}, Tecnomecánica: {vehiculo['tecnomecanica_vencimiento']}")
        
        # Verificar vencimientos próximos (60 días)
        fecha_limite = datetime.now() + timedelta(days=60)
        cursor.execute("""
            SELECT COUNT(*) as proximos_vencer
            FROM parque_automotor 
            WHERE (soat_vencimiento IS NOT NULL AND soat_vencimiento != '0000-00-00' AND soat_vencimiento <= %s)
               OR (tecnomecanica_vencimiento IS NOT NULL AND tecnomecanica_vencimiento != '0000-00-00' AND tecnomecanica_vencimiento <= %s)
        """, (fecha_limite.date(), fecha_limite.date()))
        proximos = cursor.fetchone()['proximos_vencer']
        print(f"   ✓ Vehículos con vencimientos próximos (60 días): {proximos}")
        
        # Buscar un usuario válido para login
        cursor.execute("""
            SELECT recurso_operativo_cedula, nombre 
            FROM recurso_operativo 
            WHERE estado = 'activo' OR estado IS NULL
            LIMIT 3
        """)
        usuarios_activos = cursor.fetchall()
        print(f"   ✓ Usuarios activos encontrados: {len(usuarios_activos)}")
        if usuarios_activos:
            for usuario in usuarios_activos:
                print(f"     - Cédula: {usuario['recurso_operativo_cedula']}, Nombre: {usuario['nombre']}")
        
except Error as e:
    print(f"   ✗ Error en base de datos: {e}")
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()

# 2. PROBAR ENDPOINT
print("\n2. PROBANDO ENDPOINT /api/vehiculos/vencimientos:")

BASE_URL = 'http://localhost:8080'
LOGIN_URL = f'{BASE_URL}/'
VENCIMIENTOS_URL = f'{BASE_URL}/api/vehiculos/vencimientos'

# Intentar con diferentes usuarios
usuarios_prueba = [
    {'username': '1019112308', 'password': 'Capired2024*'},  # Usuario común
    {'username': 'admin', 'password': 'admin123'},           # Admin genérico
    {'username': '1019112308', 'password': '123456'},        # Contraseña simple
]

try:
    session = requests.Session()
    
    # Verificar conectividad
    response = session.get(BASE_URL, timeout=5)
    print(f"   ✓ Servidor responde: {response.status_code}")
    
    login_exitoso = False
    for i, credenciales in enumerate(usuarios_prueba):
        print(f"\n   Probando usuario {i+1}: {credenciales['username']}")
        
        response = session.post(LOGIN_URL, data=credenciales, timeout=10, allow_redirects=False)
        print(f"     Status: {response.status_code}")
        
        if response.status_code in [200, 302]:
            print(f"     ✓ Login exitoso")
            login_exitoso = True
            
            # Seguir redirección si es necesario
            if response.status_code == 302:
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    session.get(f"{BASE_URL}{redirect_url}" if redirect_url.startswith('/') else redirect_url)
            
            # Probar endpoint de vencimientos
            print(f"     Probando endpoint de vencimientos...")
            response = session.get(VENCIMIENTOS_URL, timeout=10)
            print(f"     Status endpoint: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"     ✓ Respuesta JSON válida")
                    print(f"     Success: {data.get('success')}")
                    print(f"     Message: {data.get('message')}")
                    print(f"     Data count: {len(data.get('data', []))}")
                    
                    if data.get('data'):
                        print(f"     Primer elemento: {json.dumps(data['data'][0], indent=8, ensure_ascii=False, default=str)}")
                    
                except json.JSONDecodeError as e:
                    print(f"     ✗ Error JSON: {e}")
                    print(f"     Contenido: {response.text[:200]}")
            else:
                print(f"     ✗ Error endpoint: {response.status_code}")
                print(f"     Respuesta: {response.text[:200]}")
            
            break  # Salir del bucle si login fue exitoso
        else:
            print(f"     ✗ Login fallido: {response.status_code}")
            try:
                error_data = response.json()
                print(f"     Error: {error_data.get('message', 'Sin mensaje')}")
            except:
                print(f"     Respuesta: {response.text[:100]}")
    
    if not login_exitoso:
        print("\n   ✗ No se pudo hacer login con ningún usuario")
        print("   Probando endpoint sin autenticación...")
        response = session.get(VENCIMIENTOS_URL, timeout=10)
        print(f"   Status sin auth: {response.status_code}")
        if response.status_code != 200:
            print(f"   Respuesta: {response.text[:200]}")
        
except requests.exceptions.ConnectionError:
    print("   ✗ Error de conexión al servidor")
except Exception as e:
    print(f"   ✗ Error inesperado: {e}")

print("\n=== FIN DEL TEST ===")