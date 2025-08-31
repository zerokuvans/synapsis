import mysql.connector
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB')
}

try:
    # Conectar a la base de datos
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Primero verificar la estructura de la tabla
    cursor.execute("DESCRIBE recurso_operativo")
    columnas = cursor.fetchall()
    
    print("Estructura de la tabla recurso_operativo:")
    print("=" * 50)
    for columna in columnas:
        print(f"Columna: {columna[0]}, Tipo: {columna[1]}")
    
    print("\n" + "=" * 50)
    
    # Consultar algunos registros
    cursor.execute("SELECT * FROM recurso_operativo LIMIT 5")
    registros = cursor.fetchall()
    
    print("Primeros 5 registros:")
    for i, registro in enumerate(registros):
        print(f"Registro {i+1}: {registro}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error al consultar usuarios: {e}")