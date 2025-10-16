import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'),
    database=os.getenv('MYSQL_DB'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    port=int(os.getenv('MYSQL_PORT'))
)
cursor = conn.cursor()
cursor.execute("SELECT recurso_operativo_cedula, nombre, id_roles, estado FROM recurso_operativo WHERE estado = 'Activo' LIMIT 5")
print('=== USUARIOS ACTIVOS ===')
for row in cursor.fetchall():
    print(f'Cédula: {row[0]}, Nombre: {row[1]}, Rol: {row[2]}, Estado: {row[3]}')
conn.close()