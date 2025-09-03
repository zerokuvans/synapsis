import mysql.connector
from datetime import datetime, timedelta
import requests
import json

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'port': 3306
}

def verificar_datos_vencimientos():
    """Verificar datos de vencimientos en la base de datos"""
    print("=== VERIFICACIÓN DE DATOS DE VENCIMIENTOS ===")
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        print("\n1. VERIFICANDO ESTRUCTURA DE DATOS:")
        
        # Contar total de vehículos
        cursor.execute("SELECT COUNT(*) as total FROM parque_automotor")
        total_vehiculos = cursor.fetchone()['total']
        print(f"   ✓ Total de vehículos: {total_vehiculos}")
        
        # Contar vehículos activos
        cursor.execute("SELECT COUNT(*) as activos FROM parque_automotor WHERE estado = 'Activo'")
        vehiculos_activos = cursor.fetchone()['activos']
        print(f"   ✓ Vehículos activos: {vehiculos_activos}")
        
        # Verificar fechas de SOAT válidas (no '0000-00-00' y no NULL)
        cursor.execute("""
            SELECT COUNT(*) as soat_validos 
            FROM parque_automotor 
            WHERE soat_vencimiento IS NOT NULL 
            AND soat_vencimiento != '0000-00-00'
            AND estado = 'Activo'
        """)
        soat_validos = cursor.fetchone()['soat_validos']
        print(f"   ✓ Vehículos con SOAT válido: {soat_validos}")
        
        # Verificar fechas de Tecnomecánica válidas
        cursor.execute("""
            SELECT COUNT(*) as tecno_validos 
            FROM parque_automotor 
            WHERE tecnomecanica_vencimiento IS NOT NULL 
            AND tecnomecanica_vencimiento != '0000-00-00'
            AND estado = 'Activo'
        """)
        tecno_validos = cursor.fetchone()['tecno_validos']
        print(f"   ✓ Vehículos con Tecnomecánica válida: {tecno_validos}")
        
        print("\n2. VERIFICANDO VENCIMIENTOS PRÓXIMOS (30 días):")
        
        fecha_limite = datetime.now() + timedelta(days=30)
        
        # SOAT próximos a vencer
        cursor.execute("""
            SELECT COUNT(*) as soat_proximos
            FROM parque_automotor 
            WHERE estado = 'Activo'
            AND soat_vencimiento IS NOT NULL 
            AND soat_vencimiento != '0000-00-00'
            AND soat_vencimiento <= %s
        """, (fecha_limite.date(),))
        soat_proximos = cursor.fetchone()['soat_proximos']
        print(f"   ✓ SOAT próximos a vencer: {soat_proximos}")
        
        # Tecnomecánica próximas a vencer
        cursor.execute("""
            SELECT COUNT(*) as tecno_proximos
            FROM parque_automotor 
            WHERE estado = 'Activo'
            AND tecnomecanica_vencimiento IS NOT NULL 
            AND tecnomecanica_vencimiento != '0000-00-00'
            AND tecnomecanica_vencimiento <= %s
        """, (fecha_limite.date(),))
        tecno_proximos = cursor.fetchone()['tecno_proximos']
        print(f"   ✓ Tecnomecánica próximas a vencer: {tecno_proximos}")
        
        print("\n3. MUESTRA DE VEHÍCULOS CON VENCIMIENTOS:")
        
        # Mostrar algunos vehículos con vencimientos próximos
        cursor.execute("""
            SELECT placa, tipo_vehiculo, soat_vencimiento, tecnomecanica_vencimiento,
                   DATEDIFF(soat_vencimiento, CURDATE()) as dias_soat,
                   DATEDIFF(tecnomecanica_vencimiento, CURDATE()) as dias_tecno
            FROM parque_automotor 
            WHERE estado = 'Activo'
            AND (
                (soat_vencimiento IS NOT NULL AND soat_vencimiento != '0000-00-00' AND soat_vencimiento <= %s)
                OR 
                (tecnomecanica_vencimiento IS NOT NULL AND tecnomecanica_vencimiento != '0000-00-00' AND tecnomecanica_vencimiento <= %s)
            )
            ORDER BY 
                LEAST(
                    COALESCE(soat_vencimiento, '9999-12-31'),
                    COALESCE(tecnomecanica_vencimiento, '9999-12-31')
                ) ASC
            LIMIT 5
        """, (fecha_limite.date(), fecha_limite.date()))
        
        vehiculos_muestra = cursor.fetchall()
        if vehiculos_muestra:
            for vehiculo in vehiculos_muestra:
                print(f"   - Placa: {vehiculo['placa']}, Tipo: {vehiculo['tipo_vehiculo']}")
                print(f"     SOAT: {vehiculo['soat_vencimiento']} (días: {vehiculo['dias_soat']})")
                print(f"     Tecno: {vehiculo['tecnomecanica_vencimiento']} (días: {vehiculo['dias_tecno']})")
        else:
            print("   ⚠️  No se encontraron vehículos con vencimientos próximos")
        
        print("\n4. VERIFICANDO USUARIOS CON ROL LOGÍSTICA:")
        
        # Buscar usuarios con rol de logística (id_roles = 5)
        cursor.execute("""
            SELECT recurso_operativo_cedula, nombre, id_roles
            FROM recurso_operativo 
            WHERE id_roles = 5
            LIMIT 3
        """)
        usuarios_logistica = cursor.fetchall()
        
        if usuarios_logistica:
            print(f"   ✓ Usuarios con rol logística encontrados: {len(usuarios_logistica)}")
            for usuario in usuarios_logistica:
                print(f"     - Cédula: {usuario['recurso_operativo_cedula']}, Nombre: {usuario['nombre']}")
        else:
            print("   ⚠️  No se encontraron usuarios con rol de logística")
            # Buscar cualquier usuario para pruebas
            cursor.execute("""
                SELECT recurso_operativo_cedula, nombre, id_roles
                FROM recurso_operativo 
                LIMIT 3
            """)
            usuarios_cualquiera = cursor.fetchall()
            print("   Usuarios disponibles para prueba:")
            for usuario in usuarios_cualquiera:
                print(f"     - Cédula: {usuario['recurso_operativo_cedula']}, Nombre: {usuario['nombre']}, Rol: {usuario['id_roles']}")
        
        cursor.close()
        connection.close()
        
        return {
            'total_vehiculos': total_vehiculos,
            'vehiculos_activos': vehiculos_activos,
            'soat_validos': soat_validos,
            'tecno_validos': tecno_validos,
            'soat_proximos': soat_proximos,
            'tecno_proximos': tecno_proximos,
            'usuarios_logistica': usuarios_logistica
        }
        
    except Exception as e:
        print(f"❌ Error al verificar datos: {str(e)}")
        return None

def probar_endpoint_vencimientos(usuario_cedula=None):
    """Probar el endpoint de vencimientos"""
    print("\n=== PRUEBA DEL ENDPOINT /api/vehiculos/vencimientos ===")
    
    BASE_URL = 'http://localhost:8080'
    LOGIN_URL = f'{BASE_URL}/'
    VENCIMIENTOS_URL = f'{BASE_URL}/api/vehiculos/vencimientos'
    
    session = requests.Session()
    
    try:
        # 1. Verificar que el servidor esté corriendo
        print("\n1. Verificando servidor...")
        response = session.get(BASE_URL, timeout=5)
        print(f"   ✓ Servidor responde: {response.status_code}")
        
        # 2. Intentar acceso directo al endpoint (debería fallar)
        print("\n2. Probando acceso sin autenticación...")
        response = session.get(VENCIMIENTOS_URL, timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✓ Redirige al login (comportamiento esperado)")
        elif response.status_code == 401:
            print("   ✓ No autorizado (comportamiento esperado)")
        else:
            print(f"   ⚠️  Respuesta inesperada: {response.status_code}")
        
        # 3. Si tenemos un usuario, intentar login
        if usuario_cedula:
            print(f"\n3. Intentando login con usuario {usuario_cedula}...")
            
            # Obtener la página de login para el token CSRF si es necesario
            login_page = session.get(LOGIN_URL)
            
            # Intentar login
            login_data = {
                'username': usuario_cedula,
                'password': 'admin123'  # Contraseña de prueba
            }
            
            login_response = session.post(LOGIN_URL, data=login_data)
            print(f"   Login status: {login_response.status_code}")
            
            if login_response.status_code == 200 and 'dashboard' in login_response.url:
                print("   ✓ Login exitoso")
                
                # 4. Probar endpoint después del login
                print("\n4. Probando endpoint después del login...")
                venc_response = session.get(VENCIMIENTOS_URL)
                print(f"   Status: {venc_response.status_code}")
                
                if venc_response.status_code == 200:
                    try:
                        data = venc_response.json()
                        print(f"   ✓ Respuesta JSON válida")
                        print(f"   Success: {data.get('success')}")
                        print(f"   Total registros: {data.get('total', 0)}")
                        
                        if data.get('data'):
                            print(f"   Primeros registros:")
                            for i, item in enumerate(data['data'][:3]):
                                print(f"     {i+1}. Placa: {item.get('placa')}, Documento: {item.get('tipo_documento')}, Días: {item.get('dias_restantes')}")
                        else:
                            print("   ⚠️  No hay datos en la respuesta")
                            
                    except json.JSONDecodeError:
                        print("   ❌ Respuesta no es JSON válido")
                        print(f"   Contenido: {venc_response.text[:200]}...")
                        
                elif venc_response.status_code == 403:
                    print("   ❌ Acceso denegado - Usuario sin permisos de logística")
                else:
                    print(f"   ❌ Error: {venc_response.status_code}")
                    
            else:
                print("   ❌ Login fallido")
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error de conexión: {str(e)}")
    except Exception as e:
        print(f"   ❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    print("DIAGNÓSTICO COMPLETO DEL SISTEMA DE VENCIMIENTOS")
    print("=" * 60)
    
    # Verificar datos en la base de datos
    datos = verificar_datos_vencimientos()
    
    if datos and datos['usuarios_logistica']:
        # Usar el primer usuario de logística encontrado
        usuario_prueba = datos['usuarios_logistica'][0]['recurso_operativo_cedula']
        probar_endpoint_vencimientos(usuario_prueba)
    else:
        print("\n⚠️  No se encontraron usuarios de logística para probar el endpoint")
        probar_endpoint_vencimientos()
    
    print("\n=== FIN DEL DIAGNÓSTICO ===")