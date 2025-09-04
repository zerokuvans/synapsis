import mysql.connector
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de conexión MySQL
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

try:
    # Conectar a MySQL
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    
    print("=== ANÁLISIS DE PANTALONES NÚMERO 30 ===")
    
    # 1. Verificar ingresos de pantalones número 30
    print("\n1. INGRESOS DE PANTALONES NÚMERO 30:")
    cursor.execute("""
        SELECT id_ingreso, fecha_ingreso, tipo_elemento, numero_calzado, cantidad, proveedor
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'pantalon' AND numero_calzado = '30'
        ORDER BY fecha_ingreso DESC
    """)
    
    ingresos = cursor.fetchall()
    total_ingresado = 0
    if ingresos:
        for ingreso in ingresos:
            print(f"   ID: {ingreso['id_ingreso']}, Fecha: {ingreso['fecha_ingreso']}, Cantidad: {ingreso['cantidad']}, Proveedor: {ingreso['proveedor']}")
            total_ingresado += ingreso['cantidad']
        print(f"   TOTAL INGRESADO: {total_ingresado}")
    else:
        print("   No se encontraron ingresos de pantalones número 30")
    
    # 2. Verificar entregas de pantalones número 30
    print("\n2. ENTREGAS DE PANTALONES NÚMERO 30:")
    cursor.execute("""
        SELECT id_dotacion, fecha_registro, id_codigo_consumidor, pantalon, pantalon_talla
        FROM dotaciones 
        WHERE pantalon > 0 AND pantalon_talla = 30
        ORDER BY fecha_registro DESC
    """)
    
    entregas = cursor.fetchall()
    total_entregado = 0
    if entregas:
        for entrega in entregas:
            print(f"   ID: {entrega['id_dotacion']}, Fecha: {entrega['fecha_registro']}, Empleado: {entrega['id_codigo_consumidor']}, Cantidad: {entrega['pantalon']}, Talla: {entrega['pantalon_talla']}")
            total_entregado += entrega['pantalon']
        print(f"   TOTAL ENTREGADO: {total_entregado}")
    else:
        print("   No se encontraron entregas de pantalones número 30")
    
    # 3. Cálculo manual del saldo
    print(f"\n3. CÁLCULO MANUAL:")
    print(f"   Total Ingresado: {total_ingresado}")
    print(f"   Total Entregado: {total_entregado}")
    print(f"   Saldo Disponible: {total_ingresado - total_entregado}")
    
    # 4. Verificar vista de stock para pantalones
    print("\n4. VISTA DE STOCK PARA PANTALONES:")
    cursor.execute("""
        SELECT * FROM vista_stock_dotaciones 
        WHERE tipo_elemento = 'pantalon'
    """)
    
    stock_vista = cursor.fetchone()
    if stock_vista:
        print(f"   Tipo: {stock_vista['tipo_elemento']}")
        print(f"   Cantidad Ingresada: {stock_vista['cantidad_ingresada']}")
        print(f"   Cantidad Entregada: {stock_vista['cantidad_entregada']}")
        print(f"   Saldo Disponible: {stock_vista['saldo_disponible']}")
    else:
        print("   No se encontró información de stock para pantalones en la vista")
    
    # 5. Verificar definición de la vista
    print("\n5. DEFINICIÓN DE LA VISTA vista_stock_dotaciones:")
    cursor.execute("SHOW CREATE VIEW vista_stock_dotaciones")
    vista_def = cursor.fetchone()
    if vista_def:
        print(f"   {vista_def['Create View']}")
    
    # 6. Stock detallado por número de pantalones
    print("\n6. STOCK DETALLADO POR NÚMERO DE PANTALONES:")
    cursor.execute("""
        SELECT 
            i.numero_calzado,
            SUM(i.cantidad) as total_ingresado,
            COALESCE((
                SELECT SUM(d.pantalon)
                FROM dotaciones d 
                WHERE d.pantalon > 0 AND d.pantalon_talla = CAST(i.numero_calzado AS UNSIGNED)
            ), 0) as total_entregado,
            SUM(i.cantidad) - COALESCE((
                SELECT SUM(d.pantalon)
                FROM dotaciones d 
                WHERE d.pantalon > 0 AND d.pantalon_talla = CAST(i.numero_calzado AS UNSIGNED)
            ), 0) as disponible
        FROM ingresos_dotaciones i
        WHERE i.tipo_elemento = 'pantalon' AND i.numero_calzado IS NOT NULL AND i.numero_calzado != ''
        GROUP BY i.numero_calzado
        ORDER BY CAST(i.numero_calzado AS UNSIGNED)
    """)
    
    stock_detallado = cursor.fetchall()
    if stock_detallado:
        for item in stock_detallado:
            print(f"   Número {item['numero_calzado']}: Ingresado={item['total_ingresado']}, Entregado={item['total_entregado']}, Disponible={item['disponible']}")
    else:
        print("   No se encontró stock detallado de pantalones")
    
except mysql.connector.Error as e:
    print(f"Error de MySQL: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("\nConexión cerrada.")