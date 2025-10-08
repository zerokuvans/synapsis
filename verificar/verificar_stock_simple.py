import mysql.connector
import os
from datetime import datetime

# Configuración de la base de datos
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

def conectar_db():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return None

def verificar_stock_simple():
    connection = conectar_db()
    if not connection:
        return
    
    cursor = connection.cursor()
    
    print("=" * 60)
    print("VERIFICACIÓN SIMPLE DE STOCK CAMISETA POLO")
    print("=" * 60)
    
    try:
        # 1. Ver estructura de vista_stock_dotaciones
        print("\n1. ESTRUCTURA DE VISTA_STOCK_DOTACIONES:")
        cursor.execute("DESCRIBE vista_stock_dotaciones")
        columnas = cursor.fetchall()
        for col in columnas:
            print(f"  - {col[0]} | {col[1]}")
        
        # 2. Ver todos los datos de vista_stock_dotaciones
        print("\n2. DATOS EN VISTA_STOCK_DOTACIONES:")
        cursor.execute("SELECT * FROM vista_stock_dotaciones LIMIT 10")
        resultados = cursor.fetchall()
        for row in resultados:
            print(f"  - {row}")
        
        # 3. Contar estados de camiseta polo en dotaciones
        print("\n3. ESTADOS EN DOTACIONES:")
        cursor.execute("""
            SELECT estado_camiseta_polo, COUNT(*) as cantidad, SUM(camisetapolo) as total_prendas
            FROM dotaciones 
            WHERE camisetapolo > 0 
            GROUP BY estado_camiseta_polo
        """)
        resultados = cursor.fetchall()
        
        if resultados:
            for row in resultados:
                print(f"  - Estado: '{row[0]}', Registros: {row[1]}, Total prendas: {row[2]}")
        else:
            print("  No se encontraron estados de camiseta polo")
        
        # 4. Verificar específicamente NO VALORADO
        print("\n4. BÚSQUEDA ESPECÍFICA 'NO VALORADO':")
        cursor.execute("""
            SELECT COUNT(*) as cantidad, SUM(camisetapolo) as total_prendas
            FROM dotaciones 
            WHERE camisetapolo > 0 AND estado_camiseta_polo = 'NO VALORADO'
        """)
        resultado = cursor.fetchone()
        print(f"  - Dotaciones NO VALORADO: {resultado[1] or 0} prendas en {resultado[0]} registros")
        
        # 5. Verificar específicamente VALORADO
        print("\n5. BÚSQUEDA ESPECÍFICA 'VALORADO':")
        cursor.execute("""
            SELECT COUNT(*) as cantidad, SUM(camisetapolo) as total_prendas
            FROM dotaciones 
            WHERE camisetapolo > 0 AND estado_camiseta_polo = 'VALORADO'
        """)
        resultado = cursor.fetchone()
        print(f"  - Dotaciones VALORADO: {resultado[1] or 0} prendas en {resultado[0]} registros")
        
        # 6. Ver algunos ejemplos de registros
        print("\n6. EJEMPLOS DE REGISTROS CON CAMISETA POLO:")
        cursor.execute("""
            SELECT id_dotacion, id_codigo_consumidor, camisetapolo, estado_camiseta_polo, 
                   camiseta_polo_talla, fecha_registro
            FROM dotaciones 
            WHERE camisetapolo > 0 
            ORDER BY fecha_registro DESC 
            LIMIT 5
        """)
        resultados = cursor.fetchall()
        
        if resultados:
            for row in resultados:
                print(f"  - ID: {row[0]}, Consumidor: {row[1]}, Cantidad: {row[2]}, Estado: '{row[3]}', Talla: {row[4]}, Fecha: {row[5]}")
        else:
            print("  No se encontraron dotaciones con camiseta polo")
        
    except mysql.connector.Error as err:
        print(f"Error al ejecutar consulta: {err}")
    
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    verificar_stock_simple()