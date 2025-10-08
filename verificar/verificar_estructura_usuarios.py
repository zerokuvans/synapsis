import mysql.connector
from mysql.connector import Error

def verificar_estructura_usuarios():
    """Verifica la estructura de las tablas usuarios y roles"""
    
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@',
            port=3306,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        cursor = connection.cursor()
        
        print("=== ESTRUCTURA DE LA TABLA USUARIOS ===")
        cursor.execute("DESCRIBE usuarios")
        columnas_usuarios = cursor.fetchall()
        
        for columna in columnas_usuarios:
            print(f"{columna[0]} | {columna[1]} | {columna[2]} | {columna[3]} | {columna[4]}")
        
        print("\n=== ESTRUCTURA DE LA TABLA ROLES ===")
        cursor.execute("DESCRIBE roles")
        columnas_roles = cursor.fetchall()
        
        for columna in columnas_roles:
            print(f"{columna[0]} | {columna[1]} | {columna[2]} | {columna[3]} | {columna[4]}")
        
        print("\n=== PRIMEROS 5 REGISTROS DE USUARIOS ===")
        cursor.execute("SELECT * FROM usuarios LIMIT 5")
        usuarios = cursor.fetchall()
        
        # Obtener nombres de columnas
        cursor.execute("SHOW COLUMNS FROM usuarios")
        nombres_columnas = [col[0] for col in cursor.fetchall()]
        print(f"Columnas: {', '.join(nombres_columnas)}")
        print()
        
        for usuario in usuarios:
            print(usuario)
        
        print("\n=== TODOS LOS ROLES ===")
        cursor.execute("SELECT * FROM roles")
        roles = cursor.fetchall()
        
        for rol in roles:
            print(rol)
        
        cursor.close()
        connection.close()
        print("\n✓ Conexión cerrada")
        
    except Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_estructura_usuarios()