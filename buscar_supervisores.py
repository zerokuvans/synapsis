import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'synapsis'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'time_zone': '+00:00'
}

try:
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    # Buscar en la tabla recurso_operativo que es la que usa el login
    cursor.execute("SELECT recurso_operativo_cedula, nombre, recurso_operativo_password, id_roles, estado FROM recurso_operativo WHERE estado = 'Activo' LIMIT 5")
    usuarios = cursor.fetchall()
    
    print('Usuarios activos en recurso_operativo:')
    for usuario in usuarios:
        password_preview = str(usuario[2])[:50] + "..." if len(str(usuario[2])) > 50 else str(usuario[2])
        print(f'  Cedula: {usuario[0]}, Nombre: {usuario[1]}, Password: {password_preview}, Rol: {usuario[3]}, Estado: {usuario[4]}')
        
    # Buscar específicamente el usuario 80833959 que aparece en las pruebas
    cursor.execute("SELECT * FROM recurso_operativo WHERE recurso_operativo_cedula = '80833959'")
    usuario_especifico = cursor.fetchone()
    
    if usuario_especifico:
        print(f'\nUsuario 80833959 encontrado: {usuario_especifico}')
    else:
        print('\nUsuario 80833959 no encontrado')
        
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f'Error: {e}')