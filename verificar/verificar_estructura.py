import mysql.connector
from mysql.connector import Error

def verificar_estructura():
    """Verificar la estructura de la tabla recurso_operativo"""
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
            
            # Verificar estructura de la tabla
            cursor.execute("DESCRIBE recurso_operativo")
            columnas = cursor.fetchall()
            
            print("Estructura de la tabla recurso_operativo:")
            for columna in columnas:
                print(f"- {columna[0]} ({columna[1]})")
            
            # Buscar registros que contengan '1019112308'
            print("\nBuscando usuario 1019112308 en todas las columnas...")
            
            # Primero obtener los nombres de las columnas
            cursor.execute("SELECT * FROM recurso_operativo LIMIT 1")
            nombres_columnas = [desc[0] for desc in cursor.description]
            
            # Buscar en cada columna que pueda contener el ID
            for columna in nombres_columnas:
                try:
                    query = f"SELECT * FROM recurso_operativo WHERE {columna} = %s LIMIT 5"
                    cursor.execute(query, ('1019112308',))
                    resultados = cursor.fetchall()
                    
                    if resultados:
                        print(f"\nEncontrado en columna '{columna}':")
                        for resultado in resultados:
                            print(f"Registro: {dict(zip(nombres_columnas, resultado))}")
                except Exception as e:
                    # Ignorar errores de tipo de datos
                    pass
            
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    verificar_estructura()