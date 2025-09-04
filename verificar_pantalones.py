import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def main():
    print("=== VERIFICACIÓN STOCK PANTALONES ===")
    
    # Configuración de conexión MySQL
    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'database': os.getenv('MYSQL_DB', 'capired'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'charset': 'utf8mb4'
    }
    
    connection = None
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("✅ Conexión exitosa a MySQL")
        
        # 1. Verificar ingresos de pantalones
        print("\n1. INGRESOS DE PANTALONES:")
        cursor.execute("SELECT SUM(cantidad) FROM ingresos_dotaciones WHERE tipo_elemento = 'pantalon'")
        ingresados = cursor.fetchone()[0] or 0
        print(f"   Total ingresados: {ingresados}")
        
        # 2. Verificar entregas de pantalones
        print("\n2. ENTREGAS DE PANTALONES:")
        cursor.execute("SELECT SUM(pantalon) FROM dotaciones WHERE pantalon IS NOT NULL AND pantalon > 0")
        entregados = cursor.fetchone()[0] or 0
        print(f"   Total entregados: {entregados}")
        
        # 3. Calcular disponible
        disponible_calculado = ingresados - entregados
        print(f"\n3. DISPONIBLE CALCULADO: {disponible_calculado}")
        
        # 4. Verificar vista
        print("\n4. LO QUE MUESTRA LA VISTA:")
        cursor.execute("SELECT * FROM vista_stock_dotaciones WHERE tipo_elemento = 'pantalon'")
        vista = cursor.fetchone()
        if vista:
            print(f"   Tipo: {vista[0]}")
            print(f"   Ingresado: {vista[1]}")
            print(f"   Entregado: {vista[2]}")
            print(f"   Disponible: {vista[3]}")
        
        # 5. Verificar registros detallados de entregas
        print("\n5. DETALLE DE ENTREGAS:")
        cursor.execute("""SELECT id, cedula, pantalon, fecha_registro 
                         FROM dotaciones 
                         WHERE pantalon IS NOT NULL AND pantalon > 0 
                         ORDER BY fecha_registro DESC LIMIT 10""")
        entregas = cursor.fetchall()
        print(f"   Últimas 10 entregas:")
        for entrega in entregas:
            print(f"     ID: {entrega[0]}, Cédula: {entrega[1]}, Cantidad: {entrega[2]}, Fecha: {entrega[3]}")
        
        # 6. Verificar si hay valores no numéricos
        print("\n6. VERIFICAR VALORES NO NUMÉRICOS:")
        cursor.execute("""SELECT pantalon, COUNT(*) 
                         FROM dotaciones 
                         WHERE pantalon IS NOT NULL 
                         GROUP BY pantalon""")
        valores = cursor.fetchall()
        print("   Valores únicos en campo pantalon:")
        for valor in valores:
            print(f"     '{valor[0]}': {valor[1]} registros")
        
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    main()