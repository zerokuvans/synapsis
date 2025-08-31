#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

def check_table_structure():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB'),
            port=int(os.getenv('MYSQL_PORT'))
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar si la tabla existe
            cursor.execute("SHOW TABLES LIKE 'preoperacional'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                print("Tabla 'preoperacional' encontrada.")
                
                # Obtener estructura de la tabla
                cursor.execute("DESCRIBE preoperacional")
                columns = cursor.fetchall()
                
                print("\nEstructura de la tabla 'preoperacional':")
                print("Campo\t\t\tTipo\t\t\tNull\tKey\tDefault\tExtra")
                print("-" * 80)
                for column in columns:
                    print(f"{column[0]:<20}\t{column[1]:<15}\t{column[2]}\t{column[3]}\t{column[4]}\t{column[5]}")
                
                # Contar registros
                cursor.execute("SELECT COUNT(*) FROM preoperacional")
                count = cursor.fetchone()[0]
                print(f"\nTotal de registros en la tabla: {count}")
                
                if count > 0:
                    # Mostrar algunos registros de ejemplo
                    cursor.execute("SELECT * FROM preoperacional LIMIT 3")
                    records = cursor.fetchall()
                    print("\nPrimeros 3 registros:")
                    for i, record in enumerate(records, 1):
                        print(f"Registro {i}: {record[:5]}...")  # Solo primeros 5 campos
                        
            else:
                print("La tabla 'preoperacional' NO existe.")
                
    except Error as e:
        print(f"Error de base de datos: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada.")

if __name__ == "__main__":
    check_table_structure()