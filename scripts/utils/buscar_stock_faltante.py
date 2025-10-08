import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def buscar_stock_faltante():
    print("=== BUSCANDO STOCK FALTANTE ===")
    
    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'database': os.getenv('MYSQL_DB', 'capired'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'charset': 'utf8mb4'
    }
    
    connection = None
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        
        print("✅ Conexión exitosa a MySQL\n")
        
        # 1. Buscar todas las tablas que contengan 'botas'
        print("1. BUSCANDO TABLAS QUE CONTENGAN 'botas':")
        cursor.execute("SHOW TABLES")
        todas_las_tablas = cursor.fetchall()
        
        tablas_con_botas = []
        for tabla_info in todas_las_tablas:
            tabla = list(tabla_info.values())[0]
            try:
                # Verificar si la tabla tiene una columna 'botas'
                cursor.execute(f"DESCRIBE {tabla}")
                columnas = cursor.fetchall()
                tiene_botas = any(col['Field'] == 'botas' for col in columnas)
                
                if tiene_botas:
                    tablas_con_botas.append(tabla)
                    print(f"   ✅ {tabla} tiene columna 'botas'")
                    
                    # Verificar si tiene registros con botas > 0
                    cursor.execute(f"SELECT COUNT(*) as total FROM {tabla} WHERE botas > 0")
                    count_result = cursor.fetchone()
                    if count_result and count_result['total'] > 0:
                        print(f"     - {count_result['total']} registros con botas > 0")
                        
                        # Mostrar algunos registros
                        cursor.execute(f"SELECT * FROM {tabla} WHERE botas > 0 LIMIT 5")
                        registros = cursor.fetchall()
                        for registro in registros:
                            print(f"       {registro}")
                            
            except Error as e:
                if "doesn't exist" not in str(e):
                    print(f"   ❌ Error verificando {tabla}: {e}")
        
        # 2. Verificar si hay stock inicial en alguna configuración
        print("\n2. BUSCANDO CONFIGURACIONES DE STOCK INICIAL:")
        
        # Buscar tablas de configuración
        tablas_config = ['configuracion', 'config', 'settings', 'parametros', 'stock_inicial']
        for tabla in tablas_config:
            try:
                cursor.execute(f"SELECT * FROM {tabla}")
                config_data = cursor.fetchall()
                if config_data:
                    print(f"   ✅ Encontrada tabla {tabla}:")
                    for config in config_data:
                        if 'botas' in str(config).lower() or 'stock' in str(config).lower():
                            print(f"     {config}")
            except Error as e:
                if "doesn't exist" not in str(e):
                    print(f"   ❌ Error en {tabla}: {e}")
        
        # 3. Verificar si hay algún campo de stock inicial en las tablas principales
        print("\n3. VERIFICANDO CAMPOS DE STOCK INICIAL:")
        
        tablas_principales = ['dotaciones', 'cambios_dotacion', 'ingresos_dotaciones']
        for tabla in tablas_principales:
            try:
                cursor.execute(f"DESCRIBE {tabla}")
                columnas = cursor.fetchall()
                campos_stock = [col['Field'] for col in columnas if 'stock' in col['Field'].lower() or 'inicial' in col['Field'].lower()]
                if campos_stock:
                    print(f"   ✅ {tabla} tiene campos relacionados con stock: {campos_stock}")
                else:
                    print(f"   ❌ {tabla} no tiene campos de stock inicial")
            except Error as e:
                print(f"   ❌ Error verificando {tabla}: {e}")
        
        # 4. Buscar registros con fechas muy antiguas que puedan ser stock inicial
        print("\n4. VERIFICANDO REGISTROS ANTIGUOS EN ingresos_dotaciones:")
        cursor.execute("""
            SELECT fecha_ingreso, cantidad, observaciones, proveedor
            FROM ingresos_dotaciones 
            WHERE tipo_elemento = 'botas'
            ORDER BY fecha_ingreso ASC
            LIMIT 10
        """)
        registros_antiguos = cursor.fetchall()
        
        for registro in registros_antiguos:
            print(f"   {registro['fecha_ingreso']}: {registro['cantidad']} - {registro['proveedor']} - {registro['observaciones']}")
        
        # 5. Verificar si hay algún registro de ajuste de inventario
        print("\n5. BUSCANDO AJUSTES DE INVENTARIO:")
        
        # Buscar en observaciones palabras clave
        cursor.execute("""
            SELECT fecha_ingreso, cantidad, observaciones, proveedor
            FROM ingresos_dotaciones 
            WHERE tipo_elemento = 'botas'
            AND (observaciones LIKE '%ajuste%' 
                 OR observaciones LIKE '%inicial%' 
                 OR observaciones LIKE '%inventario%'
                 OR observaciones LIKE '%corrección%'
                 OR observaciones LIKE '%diferencia%')
        """)
        ajustes = cursor.fetchall()
        
        if ajustes:
            print("   ✅ Encontrados posibles ajustes:")
            for ajuste in ajustes:
                print(f"     {ajuste}")
        else:
            print("   ❌ No se encontraron ajustes de inventario")
        
        # 6. Calcular manualmente el stock esperado
        print("\n6. CÁLCULO MANUAL DETALLADO:")
        
        # Total ingresos
        cursor.execute("""
            SELECT SUM(cantidad) as total_ingresos
            FROM ingresos_dotaciones 
            WHERE tipo_elemento = 'botas'
        """)
        total_ingresos = cursor.fetchone()['total_ingresos'] or 0
        
        # Total asignaciones
        cursor.execute("""
            SELECT SUM(botas) as total_asignaciones
            FROM dotaciones 
            WHERE botas > 0
        """)
        total_asignaciones = cursor.fetchone()['total_asignaciones'] or 0
        
        # Total cambios
        cursor.execute("""
            SELECT SUM(botas) as total_cambios
            FROM cambios_dotacion 
            WHERE botas > 0
        """)
        total_cambios = cursor.fetchone()['total_cambios'] or 0
        
        stock_calculado = total_ingresos - total_asignaciones - total_cambios
        
        print(f"   Total ingresos: {total_ingresos}")
        print(f"   Total asignaciones: {total_asignaciones}")
        print(f"   Total cambios: {total_cambios}")
        print(f"   Stock calculado: {stock_calculado}")
        print(f"   Stock reportado por usuario: 28")
        print(f"   Diferencia: {28 - stock_calculado}")
        
        # 7. Proponer solución
        print("\n7. PROPUESTA DE SOLUCIÓN:")
        if stock_calculado == 27 and 28 - stock_calculado == 1:
            print("   La diferencia es de 1 bota.")
            print("   Posibles causas:")
            print("   1. Hay 1 bota de stock inicial que no está registrada")
            print("   2. Error en el conteo manual del usuario")
            print("   3. Hay una entrada que no se registró correctamente")
            print("   4. Hay una salida que se registró de más")
            print("\n   Recomendaciones:")
            print("   1. Verificar físicamente el inventario")
            print("   2. Si hay 28 botas físicamente, agregar 1 bota como ajuste de inventario")
            print("   3. Si hay 27 botas físicamente, el cálculo es correcto")
        
    except Error as e:
        print(f"❌ Error de MySQL: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    buscar_stock_faltante()