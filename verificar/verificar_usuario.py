import mysql.connector
from mysql.connector import Error

def verificar_usuario():
    """Verificar el cargo del usuario 1019112308 en la tabla recurso_operativo"""
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
            
            # Consultar el usuario específico
            query = """
            SELECT recurso_operativo_cedula, cargo, nombre, carpeta, cliente, ciudad 
            FROM recurso_operativo 
            WHERE recurso_operativo_cedula = %s
            """
            
            cursor.execute(query, ('1019112308',))
            resultado = cursor.fetchone()
            
            if resultado:
                print(f"Usuario encontrado:")
                print(f"Cédula: {resultado[0]}")
                print(f"Cargo: {resultado[1]}")
                print(f"Nombre: {resultado[2]}")
                print(f"Carpeta: {resultado[3]}")
                print(f"Cliente: {resultado[4]}")
                print(f"Ciudad: {resultado[5]}")
            else:
                print("Usuario no encontrado en la tabla recurso_operativo")
                
            # También verificar si hay otros usuarios con cargo similar
            query_similar = """
            SELECT cargo, COUNT(*) as cantidad
            FROM recurso_operativo 
            WHERE cargo LIKE '%MANTENIMIENTO%FTTH%'
            GROUP BY cargo
            """
            
            cursor.execute(query_similar)
            resultados_similares = cursor.fetchall()
            
            if resultados_similares:
                print("\nUsuarios con cargos similares:")
                for resultado in resultados_similares:
                    print(f"Cargo: {resultado[0]} - Cantidad: {resultado[1]}")
            
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    verificar_usuario()