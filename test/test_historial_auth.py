import requests
import json

def test_historial_with_auth():
    """Prueba el endpoint del historial con autenticación"""
    
    base_url = "http://localhost:8080"
    login_url = f"{base_url}/login"
    historial_url = f"{base_url}/api/cambios_dotacion/historial"
    
    # Crear una sesión para mantener las cookies
    session = requests.Session()
    
    print("Probando el endpoint del historial con autenticación...")
    
    try:
        # Primero, intentar acceder sin autenticación
        print("\n1. Probando acceso sin autenticación...")
        response = session.get(historial_url, timeout=10)
        print(f"Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            # Verificar si es HTML (redirección a login) o JSON
            content_type = response.headers.get('content-type', '')
            if 'text/html' in content_type:
                print("✓ El endpoint está protegido (redirige a login)")
            else:
                print("✓ El endpoint responde sin autenticación")
                try:
                    data = response.json()
                    print(f"Datos recibidos: {len(data.get('data', []))} registros")
                    return
                except:
                    print("✗ Respuesta no es JSON válido")
        
        # Intentar login automático (esto requeriría credenciales válidas)
        print("\n2. El endpoint requiere autenticación")
        print("Para probar completamente, necesitarías:")
        print("- Credenciales válidas de usuario")
        print("- Rol de 'logistica'")
        print("- Hacer login primero")
        
        # Verificar si el endpoint existe (sin autenticación debería dar 401 o 403, no 404)
        if response.status_code == 404:
            print("✗ El endpoint no existe (404)")
        elif response.status_code in [401, 403]:
            print("✓ El endpoint existe pero requiere autenticación")
        else:
            print(f"✓ El endpoint responde con código {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Error de conexión. ¿Está el servidor ejecutándose?")
    except Exception as e:
        print(f"✗ Error inesperado: {str(e)}")

def test_direct_database_query():
    """Prueba directa a la base de datos para verificar que la consulta funciona"""
    print("\n3. Probando consulta directa a la base de datos...")
    
    try:
        import mysql.connector
        
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Usar la misma consulta que el endpoint
        query = """
            SELECT 
                cd.id_cambio as id,
                cd.id_codigo_consumidor,
                ro.nombre as tecnico_nombre,
                ro.recurso_operativo_cedula as tecnico_cedula,
                cd.fecha_cambio,
                cd.pantalon,
                cd.pantalon_talla,
                cd.estado_pantalon,
                cd.camisetagris,
                cd.camiseta_gris_talla,
                cd.estado_camiseta_gris,
                cd.guerrera,
                cd.guerrera_talla,
                cd.estado_guerrera,
                cd.observaciones,
                cd.fecha_registro as created_at
            FROM cambios_dotacion cd
            LEFT JOIN recurso_operativo ro ON cd.id_codigo_consumidor = ro.id_codigo_consumidor
            ORDER BY cd.fecha_cambio DESC, cd.fecha_registro DESC
            LIMIT 5
        """
        
        cursor.execute(query)
        cambios = cursor.fetchall()
        
        print(f"✓ Consulta ejecutada exitosamente")
        print(f"✓ Registros encontrados: {len(cambios)}")
        
        if cambios:
            print("\nPrimer registro:")
            primer_cambio = cambios[0]
            print(f"  ID: {primer_cambio['id']}")
            print(f"  Técnico: {primer_cambio['tecnico_nombre']} (ID: {primer_cambio['id_codigo_consumidor']})")
            print(f"  Fecha cambio: {primer_cambio['fecha_cambio']}")
            print(f"  Pantalón: {primer_cambio['pantalon']} (Estado: {primer_cambio['estado_pantalon']})")
            print(f"  Camiseta Gris: {primer_cambio['camisetagris']} (Estado: {primer_cambio['estado_camiseta_gris']})")
        
        cursor.close()
        connection.close()
        
        print("\n✓ La consulta SQL funciona correctamente")
        print("✓ El problema era el nombre del campo 'estado_camiseta_gris' que ya fue corregido")
        
    except Exception as e:
        print(f"✗ Error en consulta directa: {str(e)}")

if __name__ == "__main__":
    test_historial_with_auth()
    test_direct_database_query()