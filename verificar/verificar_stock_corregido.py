import mysql.connector
import os
from datetime import datetime

# Configuración de la base de datos (usando las mismas variables que main.py)
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

def conectar_db():
    try:
        print(f"Conectando con: {db_config}")
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return None

def verificar_stock_camiseta_polo():
    connection = conectar_db()
    if not connection:
        return
    
    cursor = connection.cursor()
    
    print("=" * 60)
    print("VERIFICACIÓN DE STOCK CAMISETA POLO")
    print("=" * 60)
    
    try:
        # 1. Verificar vista_stock_dotaciones
        print("\n1. VISTA STOCK DOTACIONES:")
        cursor.execute("""
            SELECT * FROM vista_stock_dotaciones 
            WHERE elemento LIKE '%camiseta%polo%' OR elemento LIKE '%polo%'
        """)
        resultados = cursor.fetchall()
        
        if resultados:
            for row in resultados:
                print(f"  - {row}")
        else:
            print("  No se encontraron registros de camiseta polo")
        
        # 2. Verificar tabla dotaciones - últimos registros con camiseta polo
        print("\n2. ÚLTIMAS DOTACIONES CON CAMISETA POLO:")
        cursor.execute("""
            SELECT id_dotacion, id_codigo_consumidor, camisetapolo, estado_camiseta_polo, 
                   camiseta_polo_talla, fecha_registro
            FROM dotaciones 
            WHERE camisetapolo > 0 
            ORDER BY fecha_registro DESC 
            LIMIT 10
        """)
        resultados = cursor.fetchall()
        
        if resultados:
            for row in resultados:
                print(f"  - ID: {row[0]}, Consumidor: {row[1]}, Cantidad: {row[2]}, Estado: {row[3]}, Talla: {row[4]}, Fecha: {row[5]}")
        else:
            print("  No se encontraron dotaciones con camiseta polo")
        
        # 3. Verificar tabla cambios_dotacion - últimos cambios con camiseta polo
        print("\n3. ÚLTIMOS CAMBIOS CON CAMISETA POLO:")
        cursor.execute("""
            SELECT id_cambio, id_codigo_consumidor, camisetapolo, estado_camiseta_polo, 
                   camiseta_polo_talla, fecha_cambio
            FROM cambios_dotacion 
            WHERE camisetapolo > 0 
            ORDER BY fecha_registro DESC 
            LIMIT 10
        """)
        resultados = cursor.fetchall()
        
        if resultados:
            for row in resultados:
                print(f"  - ID: {row[0]}, Consumidor: {row[1]}, Cantidad: {row[2]}, Estado: {row[3]}, Talla: {row[4]}, Fecha: {row[5]}")
        else:
            print("  No se encontraron cambios con camiseta polo")
        
        # 4. Contar estados de camiseta polo en dotaciones
        print("\n4. CONTEO POR ESTADO EN DOTACIONES:")
        cursor.execute("""
            SELECT estado_camiseta_polo, COUNT(*) as cantidad, SUM(camisetapolo) as total_prendas
            FROM dotaciones 
            WHERE camisetapolo > 0 
            GROUP BY estado_camiseta_polo
        """)
        resultados = cursor.fetchall()
        
        if resultados:
            for row in resultados:
                print(f"  - Estado: {row[0]}, Registros: {row[1]}, Total prendas: {row[2]}")
        else:
            print("  No se encontraron estados de camiseta polo")
        
        # 5. Contar estados de camiseta polo en cambios
        print("\n5. CONTEO POR ESTADO EN CAMBIOS:")
        cursor.execute("""
            SELECT estado_camiseta_polo, COUNT(*) as cantidad, SUM(camisetapolo) as total_prendas
            FROM cambios_dotacion 
            WHERE camisetapolo > 0 
            GROUP BY estado_camiseta_polo
        """)
        resultados = cursor.fetchall()
        
        if resultados:
            for row in resultados:
                print(f"  - Estado: {row[0]}, Registros: {row[1]}, Total prendas: {row[2]}")
        else:
            print("  No se encontraron estados de camiseta polo en cambios")
        
        # 6. Verificar si hay registros con estado específico "NO VALORADO"
        print("\n6. BÚSQUEDA ESPECÍFICA DE 'NO VALORADO':")
        
        # En dotaciones
        cursor.execute("""
            SELECT COUNT(*) as cantidad, SUM(camisetapolo) as total_prendas
            FROM dotaciones 
            WHERE camisetapolo > 0 AND estado_camiseta_polo = 'NO VALORADO'
        """)
        resultado = cursor.fetchone()
        print(f"  - Dotaciones NO VALORADO: {resultado[1] or 0} prendas en {resultado[0]} registros")
        
        # En cambios
        cursor.execute("""
            SELECT COUNT(*) as cantidad, SUM(camisetapolo) as total_prendas
            FROM cambios_dotacion 
            WHERE camisetapolo > 0 AND estado_camiseta_polo = 'NO VALORADO'
        """)
        resultado = cursor.fetchone()
        print(f"  - Cambios NO VALORADO: {resultado[1] or 0} prendas en {resultado[0]} registros")
        
        # 7. Verificar si hay registros con estado específico "VALORADO"
        print("\n7. BÚSQUEDA ESPECÍFICA DE 'VALORADO':")
        
        # En dotaciones
        cursor.execute("""
            SELECT COUNT(*) as cantidad, SUM(camisetapolo) as total_prendas
            FROM dotaciones 
            WHERE camisetapolo > 0 AND estado_camiseta_polo = 'VALORADO'
        """)
        resultado = cursor.fetchone()
        print(f"  - Dotaciones VALORADO: {resultado[1] or 0} prendas en {resultado[0]} registros")
        
        # En cambios
        cursor.execute("""
            SELECT COUNT(*) as cantidad, SUM(camisetapolo) as total_prendas
            FROM cambios_dotacion 
            WHERE camisetapolo > 0 AND estado_camiseta_polo = 'VALORADO'
        """)
        resultado = cursor.fetchone()
        print(f"  - Cambios VALORADO: {resultado[1] or 0} prendas en {resultado[0]} registros")
        
    except mysql.connector.Error as err:
        print(f"Error al ejecutar consulta: {err}")
    
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    verificar_stock_camiseta_polo()