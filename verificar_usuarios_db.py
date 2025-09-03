import mysql.connector
from mysql.connector import Error

def verificar_usuarios():
    try:
        # Configuración de conexión a MySQL
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("=== Verificación de Usuarios en la Base de Datos ===")
            print(f"Base de datos: capired")
            print(f"Host: localhost")
            print()
            
            # Consultar usuarios en la tabla recurso_operativo
            query = """
            SELECT 
                id_codigo_consumidor,
                nombre,
                recurso_operativo_cedula,
                id_roles,
                estado
            FROM recurso_operativo 
            ORDER BY id_codigo_consumidor
            """
            
            cursor.execute(query)
            usuarios = cursor.fetchall()
            
            if usuarios:
                print(f"Total de usuarios encontrados: {len(usuarios)}")
                print()
                print("Usuarios disponibles:")
                print("-" * 80)
                print(f"{'ID':<5} {'Cédula':<12} {'Nombre':<25} {'Rol ID':<8} {'Estado':<10}")
                print("-" * 80)
                
                for usuario in usuarios:
                    id_codigo, nombre, cedula, rol_id, estado = usuario
                    # Manejar valores None
                    id_codigo = id_codigo or 'N/A'
                    nombre = nombre or 'N/A'
                    cedula = cedula or 'N/A'
                    rol_id = rol_id or 'N/A'
                    estado = estado or 'N/A'
                    print(f"{str(id_codigo):<5} {str(cedula):<12} {str(nombre):<25} {str(rol_id):<8} {str(estado):<10}")
                
                print()
                print("Usuarios activos con rol ID '5' (logistica):")
                print("-" * 50)
                
                usuarios_logistica = [u for u in usuarios if str(u[3] or '') == '5' and str(u[4] or '').lower() == 'activo']
                if usuarios_logistica:
                    for usuario in usuarios_logistica:
                        id_codigo, nombre, cedula, rol_id, estado = usuario
                        print(f"- ID: {id_codigo or 'N/A'}, Nombre: {nombre or 'N/A'} (Cédula: {cedula or 'N/A'})")
                else:
                    print("No se encontraron usuarios activos con rol ID '5' (logistica)")
                    
            else:
                print("No se encontraron usuarios en la tabla recurso_operativo")
                
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión a MySQL cerrada")

if __name__ == "__main__":
    verificar_usuarios()