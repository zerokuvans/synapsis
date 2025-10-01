import mysql.connector
import os

# Configuración de la base de datos
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

def buscar_consumidor_valido():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        print("BUSCANDO CONSUMIDORES VÁLIDOS:")
        print("=" * 50)
        
        # Ver estructura de la tabla
        print("Estructura de recurso_operativo:")
        cursor.execute("DESCRIBE recurso_operativo")
        columnas = cursor.fetchall()
        for col in columnas:
            print(f"  - {col[0]} | {col[1]}")
        
        print("\nBuscar algunos consumidores válidos:")
        # Buscar algunos consumidores válidos
        cursor.execute("""
            SELECT id_codigo_consumidor 
            FROM recurso_operativo 
            LIMIT 5
        """)
        resultados = cursor.fetchall()
        
        if resultados:
            print("Consumidores disponibles:")
            for row in resultados:
                print(f"  - ID: {row[0]}")
            return resultados[0][0]  # Retornar el primer ID
        else:
            print("No se encontraron consumidores")
            return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    id_valido = buscar_consumidor_valido()
    if id_valido:
        print(f"\nID válido para usar en tests: {id_valido}")
    else:
        print("\nNo se encontró un ID válido")