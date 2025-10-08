import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def main():
    print("=== INVESTIGACIÓN FINAL DEL STOCK DE PANTALONES ===")
    
    # Configuración de conexión MySQL
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
        cursor = connection.cursor()
        
        print("✅ Conexión exitosa a MySQL")
        
        # 1. Verificar estructura de ingresos_dotaciones
        print("\n1. Estructura de ingresos_dotaciones:")
        cursor.execute("DESCRIBE ingresos_dotaciones")
        estructura = cursor.fetchall()
        for col in estructura:
            print(f"Columna: {col[0]}, Tipo: {col[1]}")
        
        # 2. Verificar TODOS los registros de ingresos_dotaciones
        print("\n2. TODOS los registros en ingresos_dotaciones:")
        cursor.execute("SELECT * FROM ingresos_dotaciones")
        ingresos = cursor.fetchall()
        total_pantalones_ingresados = 0
        
        for ingreso in ingresos:
            print(f"Registro completo: {ingreso}")
            # Buscar pantalon en cualquier posición
            if 'pantalon' in str(ingreso):
                # Encontrar el valor numérico
                for valor in ingreso:
                    if isinstance(valor, int) and valor > 0:
                        total_pantalones_ingresados += valor
                        break
        
        print(f"\n📊 TOTAL PANTALONES INGRESADOS: {total_pantalones_ingresados}")
        
        # 3. Verificar estructura de dotaciones
        print("\n3. Estructura de dotaciones:")
        cursor.execute("DESCRIBE dotaciones")
        estructura_dot = cursor.fetchall()
        for col in estructura_dot:
            print(f"Columna: {col[0]}, Tipo: {col[1]}")
        
        # 4. Verificar TODOS los registros de dotaciones
        print("\n4. TODOS los registros en dotaciones:")
        cursor.execute("SELECT * FROM dotaciones")
        dotaciones = cursor.fetchall()
        total_pantalones_entregados = 0
        
        for dotacion in dotaciones:
            print(f"Registro completo: {dotacion}")
            # Buscar el campo pantalon (debería estar en posición 2 según DESCRIBE anterior)
            if len(dotacion) > 2 and dotacion[2] is not None:
                pantalon_val = str(dotacion[2])
                if pantalon_val.isdigit():
                    total_pantalones_entregados += int(pantalon_val)
                    print(f"  -> Pantalones entregados: {pantalon_val}")
        
        print(f"\n📊 TOTAL PANTALONES ENTREGADOS: {total_pantalones_entregados}")
        
        # 3. Calcular stock manual
        stock_manual = total_pantalones_ingresados - total_pantalones_entregados
        print(f"\n📊 STOCK MANUAL CALCULADO: {stock_manual}")
        
        # 4. Verificar qué muestra la vista
        print("\n3. Lo que muestra vista_stock_dotaciones:")
        cursor.execute("SELECT * FROM vista_stock_dotaciones WHERE tipo_elemento = 'pantalon'")
        vista_result = cursor.fetchone()
        if vista_result:
            print(f"Vista - Ingresado: {vista_result[1]}, Entregado: {vista_result[2]}, Disponible: {vista_result[3]}")
        
        # 5. Verificar si hay duplicados o problemas en los datos
        print("\n4. Verificando posibles duplicados en ingresos:")
        cursor.execute("""
            SELECT tipo_elemento, talla, COUNT(*) as cantidad_registros, SUM(cantidad) as total_cantidad
            FROM ingresos_dotaciones 
            WHERE tipo_elemento = 'pantalon'
            GROUP BY tipo_elemento, talla
        """)
        duplicados = cursor.fetchall()
        for dup in duplicados:
            print(f"Talla {dup[1]}: {dup[2]} registros, Total: {dup[3]} unidades")
        
        # 6. Verificar el JOIN que usa la vista
        print("\n5. Verificando el cálculo que hace la vista (simulando el JOIN):")
        cursor.execute("""
            SELECT 
                SUM(i.cantidad) as total_ingresado,
                SUM(d.pantalon) as total_entregado
            FROM ingresos_dotaciones i
            LEFT JOIN dotaciones d ON 1=1
            WHERE i.tipo_elemento = 'pantalon'
        """)
        join_result = cursor.fetchone()
        if join_result:
            print(f"JOIN Result - Ingresado: {join_result[0]}, Entregado: {join_result[1]}")
            print(f"Diferencia: {join_result[0] - (join_result[1] if join_result[1] else 0)}")
        
        print("\n=== RESUMEN ===")
        print(f"Stock real calculado manualmente: {stock_manual}")
        print(f"Stock que muestra la vista: {vista_result[3] if vista_result else 'N/A'}")
        print(f"Discrepancia: {vista_result[3] - stock_manual if vista_result else 'N/A'}")
        
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n✅ Conexión cerrada")

if __name__ == "__main__":
    main()