import mysql.connector
from mysql.connector import Error

def verificar_usuarios():
    print("=== Verificando usuarios en la base de datos ===\n")
    
    try:
        # Configuración de la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Consultar usuarios con sus estados
            query = """
            SELECT recurso_operativo_cedula, nombre, estado, id_roles
            FROM recurso_operativo 
            WHERE recurso_operativo_cedula IN ('1019112308', '80085017', '1085176966', '1023010816')
            ORDER BY estado, nombre
            """
            
            cursor.execute(query)
            usuarios = cursor.fetchall()
            
            print("USUARIOS ENCONTRADOS:")
            print("-" * 80)
            for usuario in usuarios:
                print(f"Cédula: {usuario['recurso_operativo_cedula']}")
                print(f"Nombre: {usuario['nombre']}")
                print(f"Estado: {usuario['estado']}")
                print(f"Rol: {usuario['id_roles']}")
                print("-" * 40)
            
            # Contar usuarios por estado
            cursor.execute("SELECT estado, COUNT(*) as total FROM recurso_operativo GROUP BY estado")
            estados = cursor.fetchall()
            
            print("\nRESUMEN POR ESTADO:")
            print("-" * 30)
            for estado in estados:
                print(f"{estado['estado']}: {estado['total']} usuarios")
            
            # Buscar algunos usuarios activos para las pruebas
            cursor.execute("""
            SELECT recurso_operativo_cedula, nombre, estado 
            FROM recurso_operativo 
            WHERE estado = 'Activo' 
            LIMIT 5
            """)
            activos = cursor.fetchall()
            
            print("\nUSUARIOS ACTIVOS (primeros 5):")
            print("-" * 50)
            for activo in activos:
                print(f"Cédula: {activo['recurso_operativo_cedula']} - {activo['nombre']}")
            
            # Buscar algunos usuarios inactivos
            cursor.execute("""
            SELECT recurso_operativo_cedula, nombre, estado 
            FROM recurso_operativo 
            WHERE estado != 'Activo' 
            LIMIT 5
            """)
            inactivos = cursor.fetchall()
            
            print("\nUSUARIOS INACTIVOS (primeros 5):")
            print("-" * 50)
            for inactivo in inactivos:
                print(f"Cédula: {inactivo['recurso_operativo_cedula']} - {inactivo['nombre']} - Estado: {inactivo['estado']}")
                
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada.")

if __name__ == "__main__":
    verificar_usuarios()