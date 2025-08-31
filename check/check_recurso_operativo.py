import mysql.connector
from mysql.connector import Error

def check_recurso_operativo():
    try:
        # Usar las mismas credenciales que la aplicación
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar estructura de la tabla
            print("=== ESTRUCTURA DE LA TABLA recurso_operativo ===")
            cursor.execute("DESCRIBE recurso_operativo")
            columns = cursor.fetchall()
            for col in columns:
                print(f"{col[0]} - {col[1]}")
            
            print("\n=== REGISTROS ACTIVOS EN recurso_operativo ===")
            cursor.execute("""
                SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, estado 
                FROM recurso_operativo 
                WHERE estado = 'Activo' 
                ORDER BY id_codigo_consumidor
            """)
            
            results = cursor.fetchall()
            if results:
                print(f"Total de registros activos: {len(results)}")
                for row in results:
                    print(f"ID: {row[0]}, Cédula: {row[1]}, Nombre: {row[2]}, Estado: {row[3]}")
            else:
                print("No se encontraron registros activos")
                
            # Verificar si existe el usuario específico
            print("\n=== VERIFICANDO USUARIO ESPECÍFICO (Cédula: 52912112) ===")
            cursor.execute("""
                SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, estado 
                FROM recurso_operativo 
                WHERE recurso_operativo_cedula = '52912112'
            """)
            
            user_result = cursor.fetchone()
            if user_result:
                print(f"Usuario encontrado - ID: {user_result[0]}, Cédula: {user_result[1]}, Nombre: {user_result[2]}, Estado: {user_result[3]}")
            else:
                print("Usuario con cédula 52912112 NO encontrado en recurso_operativo")
                
    except Error as e:
        print(f"Error al conectar con MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    check_recurso_operativo()