import mysql.connector
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def verificar_estructura_preoperacional():
    try:
        # Configuración de la base de datos
        config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
            'port': int(os.getenv('DB_PORT', 3306))
        }
        
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        
        print("=== ESTRUCTURA DE LA TABLA PREOPERACIONAL ===")
        cursor.execute("DESCRIBE capired.preoperacional")
        columnas = cursor.fetchall()
        
        for columna in columnas:
            print(f"Columna: {columna['Field']} - Tipo: {columna['Type']} - Null: {columna['Null']} - Default: {columna['Default']}")
        
        print("\n=== BUSCAR COLUMNAS DE FECHA ===")
        columnas_fecha = [col for col in columnas if 'fecha' in col['Field'].lower() or 'date' in col['Field'].lower() or 'time' in col['Field'].lower()]
        
        if columnas_fecha:
            print("Columnas relacionadas con fecha encontradas:")
            for col in columnas_fecha:
                print(f"  - {col['Field']} ({col['Type']})")
        else:
            print("No se encontraron columnas de fecha obvias")
        
        print("\n=== MUESTRA DE DATOS ===")
        cursor.execute("SELECT * FROM capired.preoperacional LIMIT 3")
        registros = cursor.fetchall()
        
        if registros:
            print("Primeros 3 registros:")
            for i, registro in enumerate(registros, 1):
                print(f"\nRegistro {i}:")
                for campo, valor in registro.items():
                    print(f"  {campo}: {valor}")
        else:
            print("No hay registros en la tabla")
            
    except mysql.connector.Error as e:
        print(f"Error de MySQL: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    verificar_estructura_preoperacional()