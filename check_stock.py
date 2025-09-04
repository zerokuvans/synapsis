import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def main():
    print("=== Investigación de discrepancia en stock de pantalones ===")
    
    # Configuración de conexión MySQL usando variables de entorno
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
        # Conectar a MySQL
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        
        print("✅ Conexión exitosa a MySQL")
        
        # 1. Revisar vista_stock_dotaciones para pantalones
        print("\n1. Revisando vista_stock_dotaciones para pantalones:")
        cursor.execute("""
            SELECT * FROM vista_stock_dotaciones 
            WHERE tipo_elemento LIKE '%pantalon%' OR tipo_elemento LIKE '%Pantalón%'
        """)
        stock_vista = cursor.fetchall()
        
        if stock_vista:
            for item in stock_vista:
                print(f"   - {item['tipo_elemento']}: Stock={item.get('stock_disponible', 'N/A')}")
        else:
            print("   No se encontraron pantalones en vista_stock_dotaciones")
        
        # 2. Revisar tabla dotaciones para entregas de pantalones
        print("\n2. Revisando entregas en tabla dotaciones:")
        cursor.execute("""
            SELECT COUNT(*) as total_entregas, 
                   SUM(CASE WHEN pantalon = 'Si' THEN 1 ELSE 0 END) as pantalones_entregados
            FROM dotaciones
        """)
        entregas = cursor.fetchone()
        print(f"   - Total entregas: {entregas['total_entregas']}")
        print(f"   - Pantalones entregados: {entregas['pantalones_entregados']}")
        
        # 3. Revisar ingresos_dotaciones para pantalones
        print("\n3. Revisando ingresos en tabla ingresos_dotaciones:")
        cursor.execute("""
            SELECT tipo_elemento, SUM(cantidad) as total_ingresado
            FROM ingresos_dotaciones 
            WHERE tipo_elemento LIKE '%pantalon%' OR tipo_elemento LIKE '%Pantalón%'
            GROUP BY tipo_elemento
        """)
        ingresos = cursor.fetchall()
        
        if ingresos:
            for item in ingresos:
                print(f"   - {item['tipo_elemento']}: Ingresado={item['total_ingresado']}")
        else:
            print("   No se encontraron ingresos de pantalones")
        
        # 4. Cálculo manual del stock
        print("\n4. Cálculo manual del stock:")
        total_ingresado = sum(item['total_ingresado'] for item in ingresos) if ingresos else 0
        total_entregado = entregas['pantalones_entregados'] if entregas else 0
        stock_calculado = total_ingresado - total_entregado
        
        print(f"   - Total ingresado: {total_ingresado}")
        print(f"   - Total entregado: {total_entregado}")
        print(f"   - Stock calculado: {stock_calculado}")
        
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n✅ Conexión cerrada")

if __name__ == "__main__":
    main()