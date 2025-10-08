import mysql.connector
from mysql.connector import Error

def buscar_mantenimiento_ftth():
    """Buscar usuarios con cargo MANTENIMIENTO FTTH"""
    connection = None
    try:
        # Configuración de la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='732137A031E4b@',
            database='capired',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Buscar usuarios con MANTENIMIENTO FTTH
            query = """
            SELECT recurso_operativo_cedula, cargo, nombre, carpeta, cliente, ciudad 
            FROM recurso_operativo 
            WHERE cargo LIKE '%MANTENIMIENTO%FTTH%'
            """
            
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            if resultados:
                print(f"Usuarios con cargo MANTENIMIENTO FTTH encontrados ({len(resultados)}):")
                for resultado in resultados:
                    print(f"Cédula: {resultado[0]}")
                    print(f"Cargo: {resultado[1]}")
                    print(f"Nombre: {resultado[2]}")
                    print(f"Carpeta: {resultado[3]}")
                    print(f"Cliente: {resultado[4]}")
                    print(f"Ciudad: {resultado[5]}")
                    print("-" * 50)
            else:
                print("No se encontraron usuarios con cargo MANTENIMIENTO FTTH")
            
            # Buscar todos los cargos únicos que contengan MANTENIMIENTO
            query_cargos = """
            SELECT DISTINCT cargo, COUNT(*) as cantidad
            FROM recurso_operativo 
            WHERE cargo LIKE '%MANTENIMIENTO%'
            GROUP BY cargo
            ORDER BY cargo
            """
            
            cursor.execute(query_cargos)
            cargos = cursor.fetchall()
            
            if cargos:
                print("\nTodos los cargos que contienen MANTENIMIENTO:")
                for cargo in cargos:
                    print(f"- {cargo[0]} ({cargo[1]} usuarios)")
            
            # Buscar todos los cargos únicos
            query_todos_cargos = """
            SELECT DISTINCT cargo, COUNT(*) as cantidad
            FROM recurso_operativo 
            GROUP BY cargo
            ORDER BY cargo
            """
            
            cursor.execute(query_todos_cargos)
            todos_cargos = cursor.fetchall()
            
            print("\nTodos los cargos disponibles:")
            for cargo in todos_cargos:
                print(f"- {cargo[0]} ({cargo[1]} usuarios)")
            
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    buscar_mantenimiento_ftth()