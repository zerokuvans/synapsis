import mysql.connector
from mysql.connector import Error

def check_cambios_dotacion_table():
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar si la tabla cambios_dotacion existe
            cursor.execute("""
                SELECT COUNT(*) as existe 
                FROM information_schema.tables 
                WHERE table_schema = 'capired' AND table_name = 'cambios_dotacion'
            """)
            
            resultado = cursor.fetchone()
            tabla_existe = resultado[0] > 0
            
            print(f"Tabla 'cambios_dotacion' existe: {tabla_existe}")
            
            if tabla_existe:
                # Si existe, mostrar su estructura
                cursor.execute("DESCRIBE cambios_dotacion")
                columnas = cursor.fetchall()
                print("\nEstructura de la tabla 'cambios_dotacion':")
                for columna in columnas:
                    print(f"  {columna[0]} - {columna[1]} - {columna[2]} - {columna[3]}")
                    
                # Contar registros
                cursor.execute("SELECT COUNT(*) FROM cambios_dotacion")
                count = cursor.fetchone()[0]
                print(f"\nNúmero de registros: {count}")
                
            else:
                print("\nLa tabla 'cambios_dotacion' NO existe en la base de datos.")
                print("Esto explica el error HTTP 500 en el endpoint.")
                
    except Error as e:
        print(f"Error de base de datos: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    check_cambios_dotacion_table()