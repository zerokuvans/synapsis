import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def verificar_estructura_dotaciones():
    try:
        # Configuración de la base de datos
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            database=os.getenv('MYSQL_DB', 'capired'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("=== ESTRUCTURA DE LA TABLA DOTACIONES ===")
            print()
            
            # Verificar estructura de la tabla dotaciones
            cursor.execute("DESCRIBE dotaciones")
            columns = cursor.fetchall()
            
            print("Columnas encontradas en la tabla 'dotaciones':")
            print("-" * 60)
            for column in columns:
                print(f"Columna: {column[0]:<20} | Tipo: {column[1]:<15} | Null: {column[2]:<5} | Key: {column[3]:<5} | Default: {column[4]}")
            
            print()
            print("=== VERIFICACIÓN DE COLUMNAS CHAQUETA ===")
            print()
            
            # Buscar específicamente las columnas de chaqueta
            columnas_chaqueta = ['chaqueta', 'chaqueta_talla', 'estado_chaqueta']
            columnas_existentes = [col[0] for col in columns]
            
            for col_chaqueta in columnas_chaqueta:
                if col_chaqueta in columnas_existentes:
                    print(f"✓ Columna '{col_chaqueta}' EXISTE en la tabla dotaciones")
                else:
                    print(f"✗ Columna '{col_chaqueta}' NO EXISTE en la tabla dotaciones")
            
            print()
            print("=== COMPARACIÓN CON OTRAS COLUMNAS SIMILARES ===")
            print()
            
            # Verificar otras columnas de dotaciones para comparar
            columnas_similares = ['pantalon', 'camisetagris', 'camisetapolo', 'botas']
            for col_similar in columnas_similares:
                if col_similar in columnas_existentes:
                    print(f"✓ Columna '{col_similar}' existe (para comparación)")
                else:
                    print(f"✗ Columna '{col_similar}' no existe")
            
            print()
            print("=== TOTAL DE COLUMNAS ===")
            print(f"Total de columnas en la tabla dotaciones: {len(columns)}")
            
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada.")

if __name__ == "__main__":
    verificar_estructura_dotaciones()