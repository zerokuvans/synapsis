import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def main():
    print("=== Corrigiendo vista vista_stock_dotaciones para incluir CAMBIOS ===\n")
    
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
        
        # Crear la nueva vista INCLUYENDO cambios_dotacion
        print("\n2. Creando vista corregida INCLUYENDO cambios_dotacion...")
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
            ) + (
                SELECT COALESCE(SUM(pantalon), 0) 
                FROM cambios_dotacion 
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
            ) - (
                SELECT COALESCE(SUM(pantalon), 0) 
                FROM cambios_dotacion 
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
            ) + (
                SELECT COALESCE(SUM(camisetagris), 0) 
                FROM cambios_dotacion 
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
            ) - (
                SELECT COALESCE(SUM(camisetagris), 0) 
                FROM cambios_dotacion 
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
            ) + (
                SELECT COALESCE(SUM(guerrera), 0) 
                FROM cambios_dotacion 
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
            ) - (
                SELECT COALESCE(SUM(guerrera), 0) 
                FROM cambios_dotacion 
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
            ) + (
                SELECT COALESCE(SUM(camisetapolo), 0) 
                FROM cambios_dotacion 
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
            ) - (
                SELECT COALESCE(SUM(camisetapolo), 0) 
                FROM cambios_dotacion 
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
            ) + (
                SELECT COALESCE(SUM(botas), 0) 
                FROM cambios_dotacion 
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
            ) - (
                SELECT COALESCE(SUM(botas), 0) 
                FROM cambios_dotacion 
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
            ) + (
                SELECT COALESCE(SUM(guantes_nitrilo), 0) 
                FROM cambios_dotacion 
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
            ) - (
                SELECT COALESCE(SUM(guantes_nitrilo), 0) 
                FROM cambios_dotacion 
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
            ) + (
                SELECT COALESCE(SUM(guantes_carnaza), 0) 
                FROM cambios_dotacion 
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
            ) - (
                SELECT COALESCE(SUM(guantes_carnaza), 0) 
                FROM cambios_dotacion 
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
            ) + (
                SELECT COALESCE(SUM(gafas), 0) 
                FROM cambios_dotacion 
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
            ) - (
                SELECT COALESCE(SUM(gafas), 0) 
                FROM cambios_dotacion 
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
            ) + (
                SELECT COALESCE(SUM(gorra), 0) 
                FROM cambios_dotacion 
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
            ) - (
                SELECT COALESCE(SUM(gorra), 0) 
                FROM cambios_dotacion 
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
            ) + (
                SELECT COALESCE(SUM(casco), 0) 
                FROM cambios_dotacion 
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
            ) - (
                SELECT COALESCE(SUM(casco), 0) 
                FROM cambios_dotacion 
                WHERE casco IS NOT NULL AND casco > 0
            ) AS saldo_disponible
        """
        
        cursor.execute(nueva_vista)
        connection.commit()
        
        print("✅ Vista vista_stock_dotaciones recreada exitosamente INCLUYENDO cambios_dotacion")
        
        # Verificar el resultado
        print("\n3. Verificando la nueva vista...")
        cursor.execute("SELECT * FROM vista_stock_dotaciones WHERE tipo_elemento = 'botas'")
        resultado = cursor.fetchone()
        
        if resultado:
            print(f"\n📊 Stock de BOTAS después de incluir cambios:")
            print(f"   Cantidad Ingresada: {resultado[1]}")
            print(f"   Cantidad Entregada (dotaciones + cambios): {resultado[2]}")
            print(f"   Saldo Disponible: {resultado[3]}")
        
        # Verificar cambios específicos de botas
        print("\n4. Verificando cambios de botas registrados...")
        cursor.execute("SELECT COUNT(*), SUM(botas) FROM cambios_dotacion WHERE botas > 0")
        cambios_botas = cursor.fetchone()
        print(f"   Cambios de botas registrados: {cambios_botas[0]} registros")
        print(f"   Total botas en cambios: {cambios_botas[1] or 0}")
        
        print("\n✅ ¡Corrección completada! Ahora la vista incluye los cambios de dotación.")
        
    except Error as e:
        print(f"❌ Error de MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión cerrada")
    
    return True

if __name__ == "__main__":
    main()