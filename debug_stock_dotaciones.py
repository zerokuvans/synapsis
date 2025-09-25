import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def main():
    print("=== DEPURANDO CÁLCULO DE STOCK DE DOTACIONES ===")
    
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
        
        # 1. Verificar qué tablas existen para stock
        print("1. VERIFICANDO TABLAS RELACIONADAS CON STOCK:")
        cursor.execute("SHOW TABLES LIKE '%stock%'")
        tablas_stock = cursor.fetchall()
        for tabla in tablas_stock:
            print(f"   - {tabla[0]}")
        
        cursor.execute("SHOW TABLES LIKE '%ferretero%'")
        tablas_ferretero = cursor.fetchall()
        for tabla in tablas_ferretero:
            print(f"   - {tabla[0]}")
            
        cursor.execute("SHOW TABLES LIKE '%ingresos%'")
        tablas_ingresos = cursor.fetchall()
        for tabla in tablas_ingresos:
            print(f"   - {tabla[0]}")
        
        # 2. Verificar contenido de ingresos_dotaciones para botas
        print("\n2. INGRESOS DE BOTAS EN ingresos_dotaciones:")
        cursor.execute("""
            SELECT fecha_ingreso, cantidad, proveedor, observaciones 
            FROM ingresos_dotaciones 
            WHERE tipo_elemento = 'botas'
            ORDER BY fecha_ingreso DESC
        """)
        ingresos_botas = cursor.fetchall()
        total_ingresos = 0
        for ingreso in ingresos_botas:
            print(f"   {ingreso[0]}: {ingreso[1]} unidades - {ingreso[2] or 'Sin proveedor'}")
            total_ingresos += ingreso[1]
        print(f"   TOTAL INGRESADO: {total_ingresos}")
        
        # 3. Verificar si existe stock_ferretero
        print("\n3. VERIFICANDO TABLA stock_ferretero:")
        try:
            cursor.execute("SELECT COUNT(*) FROM stock_ferretero WHERE material_tipo = 'botas'")
            count_stock_ferretero = cursor.fetchone()[0]
            print(f"   Registros de botas en stock_ferretero: {count_stock_ferretero}")
            
            if count_stock_ferretero > 0:
                cursor.execute("""
                    SELECT SUM(stock_actual) 
                    FROM stock_ferretero 
                    WHERE material_tipo = 'botas'
                """)
                stock_ferretero_total = cursor.fetchone()[0] or 0
                print(f"   Stock actual en stock_ferretero: {stock_ferretero_total}")
        except Error as e:
            print(f"   ❌ Error accediendo a stock_ferretero: {e}")
        
        # 4. Verificar asignaciones de botas
        print("\n4. ASIGNACIONES DE BOTAS:")
        cursor.execute("""
            SELECT COUNT(*), SUM(botas) 
            FROM dotaciones 
            WHERE botas > 0
        """)
        asignaciones = cursor.fetchone()
        print(f"   Asignaciones en dotaciones: {asignaciones[0]} registros, {asignaciones[1] or 0} botas")
        
        # 5. Verificar cambios de botas
        print("\n5. CAMBIOS DE BOTAS:")
        cursor.execute("""
            SELECT COUNT(*), SUM(botas) 
            FROM cambios_dotacion 
            WHERE botas > 0
        """)
        cambios = cursor.fetchone()
        print(f"   Cambios en cambios_dotacion: {cambios[0]} registros, {cambios[1] or 0} botas")
        
        # 6. Verificar la vista actual
        print("\n6. RESULTADO DE LA VISTA ACTUAL:")
        cursor.execute("SELECT * FROM vista_stock_dotaciones WHERE tipo_elemento = 'botas'")
        vista_resultado = cursor.fetchone()
        if vista_resultado:
            print(f"   Tipo: {vista_resultado[0]}")
            print(f"   Cantidad Ingresada: {vista_resultado[1]}")
            print(f"   Cantidad Entregada: {vista_resultado[2]}")
            print(f"   Saldo Disponible: {vista_resultado[3]}")
        
        # 7. Cálculo manual
        print("\n7. CÁLCULO MANUAL:")
        total_entregado = (asignaciones[1] or 0) + (cambios[1] or 0)
        saldo_calculado = total_ingresos - total_entregado
        print(f"   Ingresos: {total_ingresos}")
        print(f"   Entregado (asignaciones + cambios): {total_entregado}")
        print(f"   Saldo calculado manualmente: {saldo_calculado}")
        
        # 8. Verificar si hay diferencias con stock_ferretero
        print("\n8. ANÁLISIS DE DIFERENCIAS:")
        try:
            cursor.execute("""
                SELECT SUM(stock_actual) 
                FROM stock_ferretero 
                WHERE material_tipo = 'botas'
            """)
            stock_ferretero_result = cursor.fetchone()
            stock_ferretero_total = stock_ferretero_result[0] if stock_ferretero_result and stock_ferretero_result[0] else 0
            
            print(f"   Stock según vista_stock_dotaciones: {vista_resultado[3] if vista_resultado else 'N/A'}")
            print(f"   Stock según stock_ferretero: {stock_ferretero_total}")
            print(f"   Stock según cálculo manual: {saldo_calculado}")
            
            if vista_resultado and vista_resultado[3] != stock_ferretero_total:
                print(f"   ⚠️  DIFERENCIA DETECTADA: {abs(vista_resultado[3] - stock_ferretero_total)} unidades")
                
        except Error as e:
            print(f"   ❌ Error comparando con stock_ferretero: {e}")
        
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