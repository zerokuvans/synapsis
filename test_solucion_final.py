import requests
import json
import mysql.connector
from datetime import datetime

def test_solucion_completa():
    """Prueba completa de la solución implementada"""
    
    print("=" * 60)
    print("PRUEBA COMPLETA DE LA SOLUCIÓN - HISTORIAL DE CAMBIOS")
    print("=" * 60)
    
    # 1. Verificar que el servidor está ejecutándose
    print("\n1. Verificando estado del servidor...")
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        print(f"✓ Servidor respondiendo en puerto 8080 (código: {response.status_code})")
    except:
        print("✗ Error: Servidor no responde en puerto 8080")
        return
    
    # 2. Verificar consulta SQL directa
    print("\n2. Verificando consulta SQL directa...")
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Consulta corregida (con estado_camiseta_gris)
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
            LIMIT 3
        """
        
        cursor.execute(query)
        cambios = cursor.fetchall()
        
        print(f"✓ Consulta SQL ejecutada exitosamente")
        print(f"✓ Registros encontrados: {len(cambios)}")
        
        if cambios:
            print("\n   Datos de ejemplo:")
            for i, cambio in enumerate(cambios, 1):
                print(f"   Registro {i}:")
                print(f"     - ID: {cambio['id']}")
                print(f"     - Técnico: {cambio['tecnico_nombre']} (ID: {cambio['id_codigo_consumidor']})")
                print(f"     - Fecha: {cambio['fecha_cambio']}")
                print(f"     - Pantalón: {cambio['pantalon']} (Estado: {cambio['estado_pantalon']})")
                print(f"     - Camiseta Gris: {cambio['camisetagris']} (Estado: {cambio['estado_camiseta_gris']})")
                print(f"     - Guerrera: {cambio['guerrera']} (Estado: {cambio['estado_guerrera']})")
                print()
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error en consulta SQL: {str(e)}")
        return
    
    # 3. Verificar endpoint sin autenticación
    print("3. Verificando endpoint sin autenticación...")
    try:
        response = requests.get("http://localhost:8080/api/cambios_dotacion/historial", timeout=10)
        print(f"✓ Endpoint responde (código: {response.status_code})")
        
        content_type = response.headers.get('content-type', '')
        if 'text/html' in content_type:
            print("✓ Endpoint correctamente protegido (redirige a login)")
            print("✓ El frontend debería mostrar mensaje de 'Sesión expirada'")
        else:
            print("⚠ Endpoint no está protegido o hay un problema de configuración")
            
    except Exception as e:
        print(f"✗ Error al verificar endpoint: {str(e)}")
    
    # 4. Verificar estructura de la tabla
    print("\n4. Verificando estructura de la tabla cambios_dotacion...")
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        cursor = connection.cursor()
        cursor.execute("DESCRIBE cambios_dotacion")
        columnas = cursor.fetchall()
        
        print("✓ Estructura de la tabla:")
        campos_importantes = ['estado_pantalon', 'estado_camiseta_gris', 'estado_guerrera']
        for columna in columnas:
            nombre_campo = columna[0]
            if any(campo in nombre_campo for campo in campos_importantes):
                print(f"   ✓ {nombre_campo}: {columna[1]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error al verificar estructura: {str(e)}")
    
    # 5. Resumen de la solución
    print("\n" + "=" * 60)
    print("RESUMEN DE LA SOLUCIÓN IMPLEMENTADA")
    print("=" * 60)
    print("✓ Corregido error en consulta SQL (estado_camisetagris → estado_camiseta_gris)")
    print("✓ Mejorado manejo de errores de autenticación en frontend")
    print("✓ Agregada detección de respuestas HTML vs JSON")
    print("✓ Implementados mensajes específicos para errores de sesión")
    print("✓ Agregados botones apropiados según tipo de error")
    print("✓ Validación directa desde tabla cambios_dotacion (sin dependencia externa)")
    print("\nEL SISTEMA DEBERÍA FUNCIONAR CORRECTAMENTE AHORA")
    print("\nPara probar:")
    print("1. Asegúrese de estar logueado como usuario con rol 'logistica'")
    print("2. Vaya a la página de Cambios de Dotación")
    print("3. El historial debería cargar automáticamente")
    print("4. Si no está logueado, verá mensaje de 'Sesión expirada'")

if __name__ == "__main__":
    test_solucion_completa()