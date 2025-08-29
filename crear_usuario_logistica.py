import mysql.connector
import bcrypt
from mysql.connector import Error

def get_db_connection():
    """Función para obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='synapsis',
            user='root',
            password='',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def crear_usuario_logistica():
    """Crear un usuario de prueba con rol de logística"""
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if connection is None:
            print("Error: No se pudo conectar a la base de datos")
            return False
            
        cursor = connection.cursor(dictionary=True)
        
        # Verificar si ya existe un usuario con rol logística
        cursor.execute("""
            SELECT recurso_operativo_cedula, nombre, id_roles, estado 
            FROM recurso_operativo 
            WHERE id_roles = 5 AND