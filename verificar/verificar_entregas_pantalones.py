import mysql.connector
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def conectar_db():
    """Conectar a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB'),
            port=int(os.getenv('MYSQL_PORT', 3306))
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

def main():
    connection = conectar_db()
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    print("=== VERIFICACIÓN DE ENTREGAS DE PANTALONES ===")
    
    # 1. Verificar todas las entregas de pantalones
    print("\n1. Entregas de pantalones registradas:")
    cursor.execute("""
        SELECT 
            id_dotacion,
            cliente,
            pantalon,
            pantalon_talla,
            fecha_registro,
            fecha_actualizacion
        FROM dotaciones 
        WHERE pantalon > 0
        ORDER BY fecha_registro DESC
    """)
    
    entregas = cursor.fetchall()
    total_entregado = 0
    
    for entrega in entregas:
        print(f"ID: {entrega['id_dotacion']}, Cliente: {entrega['cliente']}, Cantidad: {entrega['pantalon']}, Talla: {entrega['pantalon_talla']}, Fecha: {entrega['fecha_registro']}")
        total_entregado += entrega['pantalon']
    
    print(f"\nTotal pantalones entregados: {total_entregado}")
    
    # 2. Verificar stock disponible desde vista
    print("\n2. Stock disponible desde vista_stock_dotaciones:")
    cursor.execute("""
        SELECT 
            tipo_elemento,
            cantidad_ingresada,
            cantidad_entregada,
            saldo_disponible
        FROM vista_stock_dotaciones 
        WHERE tipo_elemento = 'pantalon'
    """)
    
    stock_vista = cursor.fetchone()
    if stock_vista:
        print(f"Ingresado: {stock_vista['cantidad_ingresada']}")
        print(f"Entregado: {stock_vista['cantidad_entregada']}")
        print(f"Disponible: {stock_vista['saldo_disponible']}")
    else:
        print("No se encontraron datos en vista_stock_dotaciones para pantalones")
    
    # 3. Verificar cálculo manual
    print("\n3. Cálculo manual:")
    
    # Total ingresado
    cursor.execute("""
        SELECT COALESCE(SUM(cantidad), 0) as total_ingresado
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'pantalon'
    """)
    total_ingresado = cursor.fetchone()['total_ingresado']
    
    # Total entregado
    cursor.execute("""
        SELECT COALESCE(SUM(pantalon), 0) as total_entregado
        FROM dotaciones 
        WHERE pantalon > 0
    """)
    total_entregado_manual = cursor.fetchone()['total_entregado']
    
    disponible_manual = total_ingresado - total_entregado_manual
    
    print(f"Total ingresado (manual): {total_ingresado}")
    print(f"Total entregado (manual): {total_entregado_manual}")
    print(f"Disponible (manual): {disponible_manual}")
    
    # 4. Comparar resultados
    print("\n4. Comparación de resultados:")
    if stock_vista:
        print(f"Vista - Entregado: {stock_vista['cantidad_entregada']} vs Manual: {total_entregado_manual}")
        print(f"Vista - Disponible: {stock_vista['saldo_disponible']} vs Manual: {disponible_manual}")
        
        if stock_vista['cantidad_entregada'] != total_entregado_manual:
            print("⚠️  DISCREPANCIA ENCONTRADA en cantidad entregada!")
        else:
            print("✅ Los cálculos coinciden")
    
    # 5. Verificar registros recientes
    print("\n5. Últimas 5 entregas de pantalones:")
    cursor.execute("""
        SELECT 
            id_dotacion,
            cliente,
            pantalon,
            pantalon_talla,
            fecha_registro
        FROM dotaciones 
        WHERE pantalon > 0
        ORDER BY fecha_registro DESC
        LIMIT 5
    """)
    
    ultimas_entregas = cursor.fetchall()
    for entrega in ultimas_entregas:
        print(f"ID: {entrega['id_dotacion']}, Cliente: {entrega['cliente']}, Cantidad: {entrega['pantalon']}, Fecha: {entrega['fecha_registro']}")
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()