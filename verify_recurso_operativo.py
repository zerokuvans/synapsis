import mysql.connector
from mysql.connector import Error

def verify_recurso_operativo():
    try:
        # Conexión a la base de datos usando las mismas credenciales de main.py
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar si la tabla recurso_operativo existe
            cursor.execute("SHOW TABLES LIKE 'recurso_operativo'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                print("✓ La tabla 'recurso_operativo' existe")
                
                # Describir la estructura de la tabla
                cursor.execute("DESCRIBE recurso_operativo")
                columns = cursor.fetchall()
                print("\n📋 Estructura de la tabla 'recurso_operativo':")
                for column in columns:
                    print(f"  - {column[0]} ({column[1]}) - {column[3]} - {column[5]}")
                
                # Contar registros
                cursor.execute("SELECT COUNT(*) FROM recurso_operativo")
                count = cursor.fetchone()[0]
                print(f"\n📊 Total de registros: {count}")
                
                # Mostrar algunos registros de ejemplo
                if count > 0:
                    cursor.execute("SELECT * FROM recurso_operativo LIMIT 5")
                    records = cursor.fetchall()
                    print("\n📝 Registros de ejemplo:")
                    for record in records:
                        print(f"  {record}")
                else:
                    print("\n⚠️  No hay registros en la tabla")
                    
            else:
                print("❌ La tabla 'recurso_operativo' NO existe")
                
                # Buscar tablas similares
                cursor.execute("SHOW TABLES LIKE '%recurso%'")
                similar_tables = cursor.fetchall()
                if similar_tables:
                    print("\n🔍 Tablas similares encontradas:")
                    for table in similar_tables:
                        print(f"  - {table[0]}")
                else:
                    print("\n🔍 No se encontraron tablas similares")
                    
                # Mostrar todas las tablas
                cursor.execute("SHOW TABLES")
                all_tables = cursor.fetchall()
                print(f"\n📋 Total de tablas en la base de datos: {len(all_tables)}")
                print("Primeras 10 tablas:")
                for i, table in enumerate(all_tables[:10]):
                    print(f"  {i+1}. {table[0]}")
                    
    except Error as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    verify_recurso_operativo()