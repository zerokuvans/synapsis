import mysql.connector
from mysql.connector import Error

def check_roles():
    try:
        # Configuración de conexión a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("=== VERIFICANDO ROLES EN LA BASE DE DATOS ===")
            
            # Verificar roles existentes
            cursor.execute("SELECT * FROM roles ORDER BY id_roles")
            roles = cursor.fetchall()
            
            print("\nRoles existentes:")
            for role in roles:
                print(f"ID: {role[0]}, Nombre: {role[1]}")
            
            # Verificar el usuario específico 1032402333
            print("\n=== VERIFICANDO USUARIO 1032402333 ===")
            
            cursor.execute("""
                SELECT ro.id_codigo_consumidor, ro.recurso_operativo_cedula, ro.nombre, 
                       ro.id_roles, r.nombre_rol, ro.estado
                FROM recurso_operativo ro
                LEFT JOIN roles r ON ro.id_roles = r.id_roles
                WHERE ro.recurso_operativo_cedula = '1032402333'
            """)
            
            user_data = cursor.fetchone()
            
            if user_data:
                print(f"Usuario encontrado:")
                print(f"ID: {user_data[0]}")
                print(f"Cédula: {user_data[1]}")
                print(f"Nombre: {user_data[2]}")
                print(f"ID Rol: {user_data[3]}")
                print(f"Nombre Rol: {user_data[4]}")
                print(f"Estado: {user_data[5]}")
            else:
                print("Usuario 1032402333 no encontrado en recurso_operativo")
            
            # Verificar todos los usuarios operativos (id_roles = 3)
            print("\n=== USUARIOS CON ROL OPERATIVO (id_roles = 3) ===")
            
            cursor.execute("""
                SELECT ro.recurso_operativo_cedula, ro.nombre, ro.estado
                FROM recurso_operativo ro
                WHERE ro.id_roles = 3 AND ro.estado = 'Activo'
                ORDER BY ro.nombre
            """)
            
            operativos = cursor.fetchall()
            
            if operativos:
                print(f"Usuarios operativos activos ({len(operativos)}):")
                for op in operativos:
                    print(f"Cédula: {op[0]}, Nombre: {op[1]}, Estado: {op[2]}")
            else:
                print("No hay usuarios con rol operativo activos")
                
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    check_roles()