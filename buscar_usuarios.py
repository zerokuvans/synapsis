import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def buscar_usuarios():
    """Buscar usuarios activos en la base de datos"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        print("=== USUARIOS ACTIVOS EN LA BASE DE DATOS ===")
        print()
        
        # Buscar usuarios activos
        cursor.execute("""
            SELECT recurso_operativo_cedula, nombre, id_roles, estado 
            FROM recurso_operativo 
            WHERE estado = 'Activo' 
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        if results:
            for row in results:
                print(f"Cédula: {row['recurso_operativo_cedula']}, Nombre: {row['nombre']}, Rol: {row['id_roles']}, Estado: {row['estado']}")
        else:
            print("No se encontraron usuarios activos")
        
        print()
        print("=== TODOS LOS USUARIOS (PRIMEROS 10) ===")
        
        # Buscar todos los usuarios
        cursor.execute("""
            SELECT recurso_operativo_cedula, nombre, id_roles, estado 
            FROM recurso_operativo 
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        if results:
            for row in results:
                print(f"Cédula: {row['recurso_operativo_cedula']}, Nombre: {row['nombre']}, Rol: {row['id_roles']}, Estado: {row['estado']}")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")

if __name__ == "__main__":
    buscar_usuarios()