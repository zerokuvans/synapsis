import mysql.connector

def get_operativo_users():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@'
        )
        
        cursor = connection.cursor(dictionary=True)
        
        print("=== USUARIOS OPERATIVOS ACTIVOS ===")
        cursor.execute("""
            SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre 
            FROM recurso_operativo 
            WHERE id_roles = 3 AND estado = 'Activo'
        """)
        
        users = cursor.fetchall()
        
        for user in users:
            print(f"ID: {user['id_codigo_consumidor']} - Cédula: {user['recurso_operativo_cedula']} - Nombre: {user['nombre']}")
        
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    get_operativo_users()