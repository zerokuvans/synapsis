import mysql.connector
from mysql.connector import Error

def verificar_cedulas():
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Consultar usuarios activos con rol de logística (id_roles = 5)
            query = """
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula,
                nombre,
                id_roles,
                estado,
                recurso_operativo_password
            FROM recurso_operativo 
            WHERE estado = 'Activo'
            ORDER BY id_roles, nombre
            """
            
            cursor.execute(query)
            usuarios = cursor.fetchall()
            
            print("=== USUARIOS ACTIVOS EN LA BASE DE DATOS ===")
            print(f"Total usuarios encontrados: {len(usuarios)}")
            print()
            
            for usuario in usuarios:
                id_codigo = usuario['id_codigo_consumidor'] or 'N/A'
                cedula = usuario['recurso_operativo_cedula'] or 'N/A'
                nombre = usuario['nombre'] or 'N/A'
                rol_id = usuario['id_roles'] or 'N/A'
                estado = usuario['estado'] or 'N/A'
                password_hash = usuario['recurso_operativo_password'] or 'N/A'
                
                print(f"ID: {id_codigo}")
                print(f"Cédula: {cedula}")
                print(f"Nombre: {nombre}")
                print(f"Rol ID: {rol_id}")
                print(f"Estado: {estado}")
                print(f"Password Hash: {password_hash[:50]}..." if len(str(password_hash)) > 50 else f"Password Hash: {password_hash}")
                print("-" * 50)
            
            # Mostrar usuarios de logística específicamente
            usuarios_logistica = [u for u in usuarios if str(u['id_roles']) == '5']
            print(f"\n=== USUARIOS DE LOGÍSTICA (ROL 5) ===")
            print(f"Total usuarios de logística: {len(usuarios_logistica)}")
            
            for usuario in usuarios_logistica:
                cedula = usuario['recurso_operativo_cedula'] or 'N/A'
                nombre = usuario['nombre'] or 'N/A'
                print(f"Cédula para login: {cedula}")
                print(f"Nombre: {nombre}")
                print()
            
    except Error as e:
        print(f"Error al conectar con MySQL: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión cerrada.")

if __name__ == "__main__":
    import sys
    
    # Redirigir salida a archivo
    with open('cedulas_results.txt', 'w', encoding='utf-8') as f:
        sys.stdout = f
        verificar_cedulas()
        sys.stdout = sys.__stdout__
    
    print("Resultados guardados en cedulas_results.txt")