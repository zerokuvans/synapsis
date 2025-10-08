import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def main():
    print("=== Revisión de la vista vista_stock_dotaciones ===")
    
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
        
        # Obtener la definición de la vista
        print("\n1. Definición de la vista vista_stock_dotaciones:")
        cursor.execute("SHOW CREATE VIEW vista_stock_dotaciones")
        result = cursor.fetchone()
        if result:
            print("\nDefinición de la vista:")
            print(result[1])  # El segundo elemento contiene la definición
        
        # Verificar datos de origen
        print("\n\n2. Verificando datos de origen:")
        
        # Revisar ingresos_dotaciones
        print("\nTabla ingresos_dotaciones:")
        cursor.execute("""
            SELECT tipo_elemento, COUNT(*) as registros, SUM(cantidad) as total_cantidad
            FROM ingresos_dotaciones 
            WHERE tipo_elemento = 'pantalon'
            GROUP BY tipo_elemento
        """)
        ingresos = cursor.fetchall()
        for row in ingresos:
            print(f"  - {row[0]}: {row[1]} registros, total: {row[2]}")
        
        # Revisar dotaciones
        print("\nTabla dotaciones (entregas de pantalones):")
        cursor.execute("""
            SELECT COUNT(*) as total_registros,
                   SUM(CASE WHEN pantalon = 'Si' THEN 1 ELSE 0 END) as pantalones_si,
                   SUM(CASE WHEN pantalon > 0 AND pantalon != 'Si' THEN CAST(pantalon AS UNSIGNED) ELSE 0 END) as pantalones_numericos
            FROM dotaciones
        """)
        entregas = cursor.fetchall()
        for row in entregas:
            print(f"  - Total registros: {row[0]}")
            print(f"  - Pantalones 'Si': {row[1]}")
            print(f"  - Pantalones numéricos: {row[2]}")
        
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n✅ Conexión cerrada")

if __name__ == "__main__":
    main()