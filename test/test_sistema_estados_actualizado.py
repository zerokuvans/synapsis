import mysql.connector
import sys
import os

# Agregar el directorio actual al path para importar main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_conexion_db():
    """Prueba la conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        cursor = connection.cursor(dictionary=True)
        
        print("✅ Conexión a la base de datos exitosa")
        
        # Verificar que las tablas necesarias existen
        tablas_necesarias = ['recurso_operativo', 'roles', 'devoluciones_dotacion', 
                           'permisos_transicion', 'auditoria_estados', 'configuracion_notificaciones']
        
        for tabla in tablas_necesarias:
            cursor.execute(f"SHOW TABLES LIKE '{tabla}'")
            if cursor.fetchone():
                print(f"✅ Tabla {tabla} existe")
            else:
                print(f"❌ Tabla {tabla} no existe")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

def test_validar_transicion_estado():
    """Prueba la función validar_transicion_estado"""
    try:
        # Importar la función desde main
        from main import validar_transicion_estado
        
        print("\n🔍 Probando validar_transicion_estado...")
        
        # Obtener un usuario de prueba
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT id_codigo_consumidor FROM recurso_operativo WHERE estado = 'Activo' LIMIT 1")
        usuario = cursor.fetchone()
        
        if usuario:
            usuario_id = usuario['id_codigo_consumidor']
            resultado = validar_transicion_estado('REGISTRADA', 'EN_REVISION', usuario_id)
            
            print(f"Usuario ID: {usuario_id}")
            print(f"Resultado: {resultado}")
            
            if 'valida' in resultado:
                print("✅ Función validar_transicion_estado funciona correctamente")
            else:
                print("❌ Función validar_transicion_estado tiene problemas")
        else:
            print("❌ No se encontró usuario activo para prueba")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error en validar_transicion_estado: {str(e)}")

def test_obtener_transiciones_validas():
    """Prueba la función obtener_transiciones_validas"""
    try:
        from main import obtener_transiciones_validas
        
        print("\n🔍 Probando obtener_transiciones_validas...")
        
        # Obtener un usuario de prueba
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT id_codigo_consumidor FROM recurso_operativo WHERE estado = 'Activo' LIMIT 1")
        usuario = cursor.fetchone()
        
        if usuario:
            usuario_id = usuario['id_codigo_consumidor']
            transiciones = obtener_transiciones_validas('REGISTRADA', usuario_id)
            
            print(f"Usuario ID: {usuario_id}")
            print(f"Transiciones válidas desde REGISTRADA: {transiciones}")
            
            if isinstance(transiciones, list):
                print("✅ Función obtener_transiciones_validas funciona correctamente")
            else:
                print("❌ Función obtener_transiciones_validas tiene problemas")
        else:
            print("❌ No se encontró usuario activo para prueba")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error en obtener_transiciones_validas: {str(e)}")

def test_estructura_recurso_operativo():
    """Verifica que recurso_operativo tenga la estructura correcta"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        cursor = connection.cursor(dictionary=True)
        
        print("\n🔍 Verificando estructura de recurso_operativo...")
        
        # Verificar que existe la relación con roles
        cursor.execute("""
            SELECT ro.id_codigo_consumidor, ro.nombre, r.nombre_rol
            FROM recurso_operativo ro
            JOIN roles r ON ro.id_roles = r.id_roles
            WHERE ro.estado = 'Activo'
            LIMIT 3
        """)
        
        usuarios_con_roles = cursor.fetchall()
        
        if usuarios_con_roles:
            print("✅ Relación recurso_operativo -> roles funciona correctamente")
            for usuario in usuarios_con_roles:
                print(f"  - {usuario['nombre']} (ID: {usuario['id_codigo_consumidor']}) - Rol: {usuario['nombre_rol']}")
        else:
            print("❌ No se encontraron usuarios activos con roles")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error verificando estructura: {str(e)}")

def main():
    print("🚀 Iniciando pruebas del sistema de estados actualizado\n")
    
    # Ejecutar todas las pruebas
    if test_conexion_db():
        test_estructura_recurso_operativo()
        test_validar_transicion_estado()
        test_obtener_transiciones_validas()
    
    print("\n✅ Pruebas completadas")

if __name__ == "__main__":
    main()