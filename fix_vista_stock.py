import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def main():
    print("=== Corrigiendo vista vista_stock_dotaciones DEFINITIVAMENTE ===")
    
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
        
        # Primero eliminar la vista existente
        print("\n1. Eliminando vista existente...")
        cursor.execute("DROP VIEW IF EXISTS vista_stock_dotaciones")
        
        # Crear la nueva vista CORRECTA sin el JOIN problemático
        print("\n2. Creando vista corregida SIN JOIN problemático...")
        nueva_vista = """
        CREATE VIEW vista_stock_dotaciones AS
        SELECT 
            'pantalon' AS tipo_elemento,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'pantalon'
            ) AS cantidad_ingresada,
            (
                SELECT COALESCE(SUM(pantalon), 0) 
                FROM dotaciones 
                WHERE pantalon IS NOT NULL AND pantalon > 0
            ) AS cantidad_entregada,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'pantalon'
            ) - (
                SELECT COALESCE(SUM(pantalon), 0) 
                FROM dotaciones 
                WHERE pantalon IS NOT NULL AND pantalon > 0
            ) AS saldo_disponible
        
        UNION ALL
        
        SELECT 
            'camisetagris' AS tipo_elemento,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'camisetagris'
            ) AS cantidad_ingresada,
            (
                SELECT COALESCE(SUM(camisetagris), 0) 
                FROM dotaciones 
                WHERE camisetagris IS NOT NULL AND camisetagris > 0
            ) AS cantidad_entregada,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'camisetagris'
            ) - (
                SELECT COALESCE(SUM(camisetagris), 0) 
                FROM dotaciones 
                WHERE camisetagris IS NOT NULL AND camisetagris > 0
            ) AS saldo_disponible
        
        UNION ALL
        
        SELECT 
            'guerrera' AS tipo_elemento,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'guerrera'
            ) AS cantidad_ingresada,
            (
                SELECT COALESCE(SUM(guerrera), 0) 
                FROM dotaciones 
                WHERE guerrera IS NOT NULL AND guerrera > 0
            ) AS cantidad_entregada,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'guerrera'
            ) - (
                SELECT COALESCE(SUM(guerrera), 0) 
                FROM dotaciones 
                WHERE guerrera IS NOT NULL AND guerrera > 0
            ) AS saldo_disponible
        
        UNION ALL
        
        SELECT 
            'camisetapolo' AS tipo_elemento,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'camisetapolo'
            ) AS cantidad_ingresada,
            (
                SELECT COALESCE(SUM(camisetapolo), 0) 
                FROM dotaciones 
                WHERE camisetapolo IS NOT NULL AND camisetapolo > 0
            ) AS cantidad_entregada,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'camisetapolo'
            ) - (
                SELECT COALESCE(SUM(camisetapolo), 0) 
                FROM dotaciones 
                WHERE camisetapolo IS NOT NULL AND camisetapolo > 0
            ) AS saldo_disponible
        
        UNION ALL
        
        SELECT 
            'botas' AS tipo_elemento,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'botas'
            ) AS cantidad_ingresada,
            (
                SELECT COALESCE(SUM(botas), 0) 
                FROM dotaciones 
                WHERE botas IS NOT NULL AND botas > 0
            ) AS cantidad_entregada,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'botas'
            ) - (
                SELECT COALESCE(SUM(botas), 0) 
                FROM dotaciones 
                WHERE botas IS NOT NULL AND botas > 0
            ) AS saldo_disponible
        
        UNION ALL
        
        SELECT 
            'guantes_nitrilo' AS tipo_elemento,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'guantes_nitrilo'
            ) AS cantidad_ingresada,
            (
                SELECT COALESCE(SUM(guantes_nitrilo), 0) 
                FROM dotaciones 
                WHERE guantes_nitrilo IS NOT NULL AND guantes_nitrilo > 0
            ) AS cantidad_entregada,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'guantes_nitrilo'
            ) - (
                SELECT COALESCE(SUM(guantes_nitrilo), 0) 
                FROM dotaciones 
                WHERE guantes_nitrilo IS NOT NULL AND guantes_nitrilo > 0
            ) AS saldo_disponible
        
        UNION ALL
        
        SELECT 
            'guantes_carnaza' AS tipo_elemento,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'guantes_carnaza'
            ) AS cantidad_ingresada,
            (
                SELECT COALESCE(SUM(guantes_carnaza), 0) 
                FROM dotaciones 
                WHERE guantes_carnaza IS NOT NULL AND guantes_carnaza > 0
            ) AS cantidad_entregada,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'guantes_carnaza'
            ) - (
                SELECT COALESCE(SUM(guantes_carnaza), 0) 
                FROM dotaciones 
                WHERE guantes_carnaza IS NOT NULL AND guantes_carnaza > 0
            ) AS saldo_disponible
        
        UNION ALL
        
        SELECT 
            'gafas' AS tipo_elemento,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'gafas'
            ) AS cantidad_ingresada,
            (
                SELECT COALESCE(SUM(gafas), 0) 
                FROM dotaciones 
                WHERE gafas IS NOT NULL AND gafas > 0
            ) AS cantidad_entregada,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'gafas'
            ) - (
                SELECT COALESCE(SUM(gafas), 0) 
                FROM dotaciones 
                WHERE gafas IS NOT NULL AND gafas > 0
            ) AS saldo_disponible
        
        UNION ALL
        
        SELECT 
            'gorra' AS tipo_elemento,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'gorra'
            ) AS cantidad_ingresada,
            (
                SELECT COALESCE(SUM(gorra), 0) 
                FROM dotaciones 
                WHERE gorra IS NOT NULL AND gorra > 0
            ) AS cantidad_entregada,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'gorra'
            ) - (
                SELECT COALESCE(SUM(gorra), 0) 
                FROM dotaciones 
                WHERE gorra IS NOT NULL AND gorra > 0
            ) AS saldo_disponible
        
        UNION ALL
        
        SELECT 
            'casco' AS tipo_elemento,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'casco'
            ) AS cantidad_ingresada,
            (
                SELECT COALESCE(SUM(casco), 0) 
                FROM dotaciones 
                WHERE casco IS NOT NULL AND casco > 0
            ) AS cantidad_entregada,
            (
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ingresos_dotaciones 
                WHERE tipo_elemento = 'casco'
            ) - (
                SELECT COALESCE(SUM(casco), 0) 
                FROM dotaciones 
                WHERE casco IS NOT NULL AND casco > 0
            ) AS saldo_disponible
        """
        
        cursor.execute(nueva_vista)
        connection.commit()
        
        print("✅ Vista corregida creada exitosamente")
        
        # Verificar el resultado
        print("\n3. Verificando resultado corregido:")
        cursor.execute("SELECT * FROM vista_stock_dotaciones WHERE tipo_elemento = 'pantalon'")
        result = cursor.fetchone()
        if result:
            print(f"Pantalón - Ingresado: {result[1]}, Entregado: {result[2]}, Disponible: {result[3]}")
            print(f"\n🎯 STOCK CORREGIDO: {result[3]} (era 580, ahora es {result[3]})")
        
    except Error as e:
        print(f"Error: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n✅ Conexión cerrada")

if __name__ == "__main__":
    main()