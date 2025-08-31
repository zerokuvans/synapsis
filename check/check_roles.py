import mysql.connector

def check_roles():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@'
        )
        
        cursor = connection.cursor(dictionary=True)
        
        print("=== ROLES DISPONIBLES ===")
        cursor.execute("SELECT * FROM roles")
        roles = cursor.fetchall()
        
        for role in roles:
            print(f"ID: {role['id_roles']} - Nombre: {role['nombre_rol']}")
        
        print("\n=== USUARIOS POR ROL ===")
        cursor.execute("""
            SELECT r.nombre_rol, COUNT(*) as total
            FROM recurso_operativo ro
            JOIN roles r ON ro.id_roles = r.id_roles
            WHERE ro.estado = 'Activo'
            GROUP BY r.nombre_rol
        """)
        
        usuarios_por_rol = cursor.fetchall()
        for item in usuarios_por_rol:
            print(f"{item['nombre_rol']}: {item['total']} usuarios activos")
        
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_roles()