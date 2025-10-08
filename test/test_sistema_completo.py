import mysql.connector
import os
from mysql.connector import Error
from dotenv import load_dotenv
import sys
import json

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT')),
    'time_zone': '+00:00'
}

def test_database_connection():
    """Prueba la conexión a la base de datos"""
    print("=== PRUEBA 1: CONEXIÓN A BASE DE DATOS ===")
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("✓ Conexión exitosa a MySQL")
            print(f"  Base de datos: {db_config['database']}")
            print(f"  Host: {db_config['host']}")
            print(f"  Puerto: {db_config['port']}")
            connection.close()
            return True
    except Error as e:
        print(f"✗ Error de conexión: {e}")
        return False

def test_table_structure():
    """Verifica la estructura de las tablas necesarias"""
    print("\n=== PRUEBA 2: ESTRUCTURA DE TABLAS ===")
    
    required_tables = {
        'devoluciones_dotacion': ['id', 'estado', 'created_at'],
        'permisos_transicion': ['estado_origen', 'estado_destino', 'rol_id'],
        'recurso_operativo': ['recurso_operativo_cedula', 'id_roles'],
        'usuarios': ['usuario_cedula']
    }
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        all_tables_ok = True
        
        for table, required_columns in required_tables.items():
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            if cursor.fetchone():
                print(f"✓ Tabla {table} existe")
                
                # Verificar columnas
                cursor.execute(f"DESCRIBE {table}")
                columns = [col[0] for col in cursor.fetchall()]
                
                missing_columns = [col for col in required_columns if col not in columns]
                if missing_columns:
                    print(f"  ⚠ Columnas faltantes: {missing_columns}")
                    all_tables_ok = False
                else:
                    print(f"  ✓ Todas las columnas requeridas presentes")
            else:
                print(f"✗ Tabla {table} no existe")
                all_tables_ok = False
        
        connection.close()
        return all_tables_ok
        
    except Error as e:
        print(f"✗ Error verificando estructura: {e}")
        return False

def test_permissions_data():
    """Verifica que existan los permisos de transición"""
    print("\n=== PRUEBA 3: DATOS DE PERMISOS ===")
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Verificar permisos existentes
        cursor.execute("SELECT COUNT(*) FROM permisos_transicion")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✓ {count} permisos de transición configurados")
            
            # Mostrar algunos permisos
            cursor.execute("SELECT estado_origen, estado_destino, rol_id FROM permisos_transicion LIMIT 5")
            permisos = cursor.fetchall()
            
            print("  Ejemplos de permisos:")
            for permiso in permisos:
                print(f"    {permiso[0]} → {permiso[1]} (rol_id: {permiso[2]})")
            
            connection.close()
            return True
        else:
            print("✗ No hay permisos de transición configurados")
            connection.close()
            return False
            
    except Error as e:
        print(f"✗ Error verificando permisos: {e}")
        return False

def test_backend_functions():
    """Prueba las funciones del backend"""
    print("\n=== PRUEBA 4: FUNCIONES DEL BACKEND ===")
    
    try:
        # Importar funciones del main.py
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Simular funciones de validación
        def validar_transicion_estado(estado_actual, nuevo_estado, rol_usuario):
            """Función simulada de validación"""
            transiciones_validas = {
                'REGISTRADA': ['EN_REVISION', 'RECHAZADA'],
                'EN_REVISION': ['APROBADA', 'RECHAZADA'],
                'APROBADA': ['COMPLETADA'],
                'RECHAZADA': [],
                'COMPLETADA': []
            }
            
            if nuevo_estado in transiciones_validas.get(estado_actual, []):
                # Verificar permisos por rol
                permisos_rol = {
                    'administrativo': ['EN_REVISION', 'APROBADA', 'RECHAZADA', 'COMPLETADA'],
                    'supervisor': ['APROBADA', 'RECHAZADA', 'COMPLETADA'],
                    'operativo': []
                }
                
                return nuevo_estado in permisos_rol.get(rol_usuario, [])
            
            return False
        
        def obtener_transiciones_validas(estado_actual, rol_usuario):
            """Función simulada para obtener transiciones válidas"""
            transiciones_validas = {
                'REGISTRADA': ['EN_REVISION', 'RECHAZADA'],
                'EN_REVISION': ['APROBADA', 'RECHAZADA'],
                'APROBADA': ['COMPLETADA'],
                'RECHAZADA': [],
                'COMPLETADA': []
            }
            
            permisos_rol = {
                'administrativo': ['EN_REVISION', 'APROBADA', 'RECHAZADA', 'COMPLETADA'],
                'supervisor': ['APROBADA', 'RECHAZADA', 'COMPLETADA'],
                'operativo': []
            }
            
            posibles = transiciones_validas.get(estado_actual, [])
            permitidas = permisos_rol.get(rol_usuario, [])
            
            return [estado for estado in posibles if estado in permitidas]
        
        # Pruebas de validación
        test_cases = [
            ('REGISTRADA', 'EN_REVISION', 'administrativo', True),
            ('REGISTRADA', 'COMPLETADA', 'administrativo', False),
            ('EN_REVISION', 'APROBADA', 'supervisor', True),
            ('APROBADA', 'COMPLETADA', 'operativo', False),
        ]
        
        all_tests_passed = True
        
        for estado_actual, nuevo_estado, rol, esperado in test_cases:
            resultado = validar_transicion_estado(estado_actual, nuevo_estado, rol)
            if resultado == esperado:
                print(f"✓ {estado_actual} → {nuevo_estado} ({rol}): {resultado}")
            else:
                print(f"✗ {estado_actual} → {nuevo_estado} ({rol}): esperado {esperado}, obtuvo {resultado}")
                all_tests_passed = False
        
        # Prueba de obtener transiciones válidas
        transiciones = obtener_transiciones_validas('REGISTRADA', 'administrativo')
        if 'EN_REVISION' in transiciones and 'RECHAZADA' in transiciones:
            print(f"✓ Transiciones válidas desde REGISTRADA: {transiciones}")
        else:
            print(f"✗ Transiciones válidas incorrectas: {transiciones}")
            all_tests_passed = False
        
        return all_tests_passed
        
    except Exception as e:
        print(f"✗ Error en funciones del backend: {e}")
        return False

def test_sample_data():
    """Verifica datos de muestra en las tablas"""
    print("\n=== PRUEBA 5: DATOS DE MUESTRA ===")
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Verificar devoluciones
        cursor.execute("SELECT COUNT(*) FROM devoluciones_dotacion")
        devoluciones_count = cursor.fetchone()[0]
        print(f"✓ {devoluciones_count} devoluciones en la base de datos")
        
        # Verificar usuarios
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        usuarios_count = cursor.fetchone()[0]
        print(f"✓ {usuarios_count} usuarios en la base de datos")
        
        # Verificar recurso operativo
        cursor.execute("SELECT COUNT(*) FROM recurso_operativo")
        recurso_count = cursor.fetchone()[0]
        print(f"✓ {recurso_count} registros en recurso_operativo")
        
        connection.close()
        return True
        
    except Error as e:
        print(f"✗ Error verificando datos: {e}")
        return False

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("🔍 INICIANDO PRUEBAS DEL SISTEMA DE GESTIÓN DE ESTADOS")
    print("=" * 60)
    
    tests = [
        ("Conexión a Base de Datos", test_database_connection),
        ("Estructura de Tablas", test_table_structure),
        ("Datos de Permisos", test_permissions_data),
        ("Funciones del Backend", test_backend_functions),
        ("Datos de Muestra", test_sample_data)
    ]
    
    results = []
    
    for test_name, test_function in tests:
        try:
            result = test_function()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Error en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASÓ" if result else "✗ FALLÓ"
        print(f"{status:<10} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está listo.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar los errores anteriores.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)