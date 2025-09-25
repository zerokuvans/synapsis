import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def main():
    print("=== VERIFICANDO ESTRUCTURA DE TABLAS DE STOCK ===")
    
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
        
        print("✅ Conexión exitosa a MySQL\n")
        
        # 1. Verificar estructura de stock_ferretero
        print("1. ESTRUCTURA DE stock_ferretero:")
        cursor.execute("DESCRIBE stock_ferretero")
        columnas = cursor.fetchall()
        for columna in columnas:
            print(f"   {columna[0]} - {columna[1]} - {columna[2]}")
        
        # 2. Verificar contenido de stock_ferretero para botas
        print("\n2. CONTENIDO DE stock_ferretero PARA BOTAS:")
        cursor.execute("SELECT * FROM stock_ferretero WHERE material_tipo = 'botas'")
        stock_botas = cursor.fetchall()
        if stock_botas:
            for registro in stock_botas:
                print(f"   {registro}")
        else:
            print("   No hay registros de botas en stock_ferretero")
        
        # 3. Verificar si hay otras tablas con stock de botas
        print("\n3. VERIFICANDO OTRAS TABLAS DE STOCK:")
        
        # stock_general
        try:
            cursor.execute("SELECT * FROM stock_general WHERE tipo_elemento = 'botas'")
            stock_general = cursor.fetchall()
            if stock_general:
                print("   stock_general:")
                for registro in stock_general:
                    print(f"     {registro}")
            else:
                print("   stock_general: Sin registros de botas")
        except Error as e:
            print(f"   stock_general: Error - {e}")
        
        # stock_unificado
        try:
            cursor.execute("SELECT * FROM stock_unificado WHERE material_tipo = 'botas'")
            stock_unificado = cursor.fetchall()
            if stock_unificado:
                print("   stock_unificado:")
                for registro in stock_unificado:
                    print(f"     {registro}")
            else:
                print("   stock_unificado: Sin registros de botas")
        except Error as e:
            print(f"   stock_unificado: Error - {e}")
        
        # entradas_stock
        try:
            cursor.execute("SELECT * FROM entradas_stock WHERE material_tipo = 'botas'")
            entradas_stock = cursor.fetchall()
            if entradas_stock:
                print("   entradas_stock:")
                for registro in entradas_stock:
                    print(f"     {registro}")
            else:
                print("   entradas_stock: Sin registros de botas")
        except Error as e:
            print(f"   entradas_stock: Error - {e}")
        
        # 4. Verificar la definición actual de la vista
        print("\n4. DEFINICIÓN DE vista_stock_dotaciones:")
        cursor.execute("SHOW CREATE VIEW vista_stock_dotaciones")
        vista_def = cursor.fetchone()
        if vista_def:
            print("   Definición actual:")
            print(f"   {vista_def[1]}")
        
        # 5. Verificar si hay algún stock inicial o base que no esté siendo considerado
        print("\n5. VERIFICANDO POSIBLES FUENTES DE STOCK ADICIONAL:")
        
        # Buscar en ferretero
        try:
            cursor.execute("SELECT * FROM ferretero WHERE material_tipo = 'botas'")
            ferretero_botas = cursor.fetchall()
            if ferretero_botas:
                print("   ferretero:")
                for registro in ferretero_botas:
                    print(f"     {registro}")
            else:
                print("   ferretero: Sin registros de botas")
        except Error as e:
            print(f"   ferretero: Error - {e}")
        
        # Buscar en entradas_ferretero
        try:
            cursor.execute("SELECT * FROM entradas_ferretero WHERE material_tipo = 'botas'")
            entradas_ferretero = cursor.fetchall()
            if entradas_ferretero:
                print("   entradas_ferretero:")
                total_entradas_ferretero = 0
                for registro in entradas_ferretero:
                    print(f"     {registro}")
                    # Asumir que la cantidad está en una columna específica
                    if len(registro) > 2:  # Ajustar según la estructura real
                        try:
                            total_entradas_ferretero += int(registro[2])  # Ajustar índice según estructura
                        except:
                            pass
                print(f"   Total en entradas_ferretero: {total_entradas_ferretero}")
            else:
                print("   entradas_ferretero: Sin registros de botas")
        except Error as e:
            print(f"   entradas_ferretero: Error - {e}")
        
        # 6. Verificar si la vista debería incluir más fuentes
        print("\n6. ANÁLISIS FINAL:")
        print("   Vista actual muestra: 27 botas disponibles")
        print("   Usuario reporta: 28 botas")
        print("   Diferencia: 1 bota")
        print("   Posibles causas:")
        print("   - Stock inicial no considerado en ingresos_dotaciones")
        print("   - Entrada en otra tabla (ferretero, stock_general, etc.)")
        print("   - Error en el conteo de asignaciones o cambios")
        print("   - Cache o datos no actualizados en la interfaz")
        
    except Error as e:
        print(f"❌ Error de MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión cerrada")
    
    return True

if __name__ == "__main__":
    main()