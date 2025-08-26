import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

def debug_user_session():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        print("=== DEBUG: Buscando usuario 52912112 en todas las tablas ===")
        
        # Buscar en recurso_operativo
        cursor.execute("""
            SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, super, carpeta, estado
            FROM capired.recurso_operativo
            WHERE id_codigo_consumidor = 52912112
        """)
        user_ro = cursor.fetchone()
        
        if user_ro:
            print(f"Encontrado en recurso_operativo: {user_ro}")
        else:
            print("NO encontrado en recurso_operativo")
        
        # Buscar por cédula 52912112
        cursor.execute("""
            SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, super, carpeta, estado
            FROM capired.recurso_operativo
            WHERE recurso_operativo_cedula = '52912112'
        """)
        user_cedula = cursor.fetchone()
        
        if user_cedula:
            print(f"Encontrado por cédula en recurso_operativo: {user_cedula}")
        else:
            print("NO encontrado por cédula en recurso_operativo")
        
        # Buscar en tabla usuarios (si existe)
        try:
            cursor.execute("""
                SELECT * FROM usuarios WHERE id = 52912112 OR cedula = '52912112'
            """)
            user_usuarios = cursor.fetchone()
            if user_usuarios:
                print(f"Encontrado en tabla usuarios: {user_usuarios}")
            else:
                print("NO encontrado en tabla usuarios")
        except:
            print("Tabla usuarios no existe")
        
        # Buscar en todas las tablas que contengan 52912112
        print("\n=== Buscando 52912112 en todas las tablas ===")
        
        # Obtener todas las tablas
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = list(table.values())[0]
            try:
                # Obtener columnas de la tabla
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                
                # Buscar en columnas que puedan contener el ID
                for column in columns:
                    col_name = column['Field']
                    if 'id' in col_name.lower() or 'codigo' in col_name.lower() or 'cedula' in col_name.lower():
                        try:
                            cursor.execute(f"SELECT * FROM {table_name} WHERE {col_name} = '52912112' OR {col_name} = 52912112 LIMIT 1")
                            result = cursor.fetchone()
                            if result:
                                print(f"Encontrado en tabla {table_name}, columna {col_name}: {result}")
                        except:
                            pass
            except:
                pass
        
        print("\n=== DEBUG: Consulta que debería funcionar ===")
        cursor.execute("""
            SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, carpeta
            FROM capired.recurso_operativo
            WHERE carpeta IN ('SUPERVISORES', 'APOYO CAMIONETAS') AND estado = 'Activo'
            ORDER BY nombre
        """)
        tecnicos = cursor.fetchall()
        
        print(f"Total técnicos que deberían aparecer: {len(tecnicos)}")
        for tecnico in tecnicos:
            print(f"  - {tecnico['nombre']} (Carpeta: {tecnico['carpeta']})")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    debug_user_session()