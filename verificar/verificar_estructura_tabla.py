import mysql.connector

def verificar_estructura():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@'
        )
        cursor = connection.cursor()
        
        # Verificar estructura de recurso_operativo
        print("=== ESTRUCTURA DE TABLA recurso_operativo ===")
        cursor.execute("DESCRIBE recurso_operativo")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]} - {col[1]}")
            
        # Verificar estructura de asistencia
        print("\n=== ESTRUCTURA DE TABLA asistencia ===")
        cursor.execute("DESCRIBE asistencia")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]} - {col[1]}")
        
        # Verificar si existe el usuario 1032402333
        print("\n=== BUSCAR USUARIO 1032402333 ===")
        cursor.execute("SELECT * FROM recurso_operativo WHERE recurso_operativo_cedula = %s", ('1032402333',))
        usuario = cursor.fetchone()
        if usuario:
            print(f"Usuario encontrado: {usuario}")
        else:
            print("Usuario no encontrado")
            
        # Buscar usuarios que contengan "CACERES"
        print("\n=== BUSCAR USUARIOS CON CACERES ===")
        cursor.execute("SELECT * FROM recurso_operativo WHERE recurso_operativo_nombre LIKE %s", ('%CACERES%',))
        usuarios = cursor.fetchall()
        for usuario in usuarios:
            print(f"Usuario: {usuario}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verificar_estructura()