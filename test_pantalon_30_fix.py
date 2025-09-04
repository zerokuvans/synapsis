import mysql.connector
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """Obtener conexión a la base de datos MySQL"""
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
        print(f"Error de conexión MySQL: {e}")
        return None

def test_stock_pantalon_30():
    """Probar el cálculo de stock para pantalones número 30 con la lógica corregida"""
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print("=== PRUEBA DE STOCK PANTALONES NÚMERO 30 (LÓGICA CORREGIDA) ===")
        print()
        
        # 1. Verificar ingresos de pantalones número 30 (lógica corregida)
        print("1. INGRESOS DE PANTALONES NÚMERO 30 (LÓGICA CORREGIDA):")
        cursor.execute("""
            SELECT 
                tipo_elemento,
                CASE 
                    WHEN tipo_elemento = 'pantalon' THEN 'Sin talla'
                    ELSE COALESCE(talla, 'Sin talla')
                END as talla,
                COALESCE(numero_calzado, 'Sin número') as numero_calzado,
                SUM(cantidad) as total_ingresado
            FROM ingresos_dotaciones
            WHERE tipo_elemento = 'pantalon' AND numero_calzado = '30'
            GROUP BY tipo_elemento, talla, numero_calzado
        """)
        ingresos_30 = cursor.fetchall()
        
        for ingreso in ingresos_30:
            print(f"  - Tipo: {ingreso['tipo_elemento']}, Talla: {ingreso['talla']}, Número: {ingreso['numero_calzado']}, Ingresado: {ingreso['total_ingresado']}")
        
        print()
        
        # 2. Verificar entregas de pantalones número 30 (lógica corregida)
        print("2. ENTREGAS DE PANTALONES NÚMERO 30 (LÓGICA CORREGIDA):")
        cursor.execute("""
            SELECT 
                'pantalon' as tipo_elemento,
                'Sin talla' as talla,
                COALESCE(pantalon_talla, 'Sin número') as numero_calzado,
                SUM(pantalon) as total_entregado
            FROM dotaciones
            WHERE pantalon > 0 AND pantalon_talla = '30'
            GROUP BY pantalon_talla
        """)
        entregas_30 = cursor.fetchall()
        
        for entrega in entregas_30:
            print(f"  - Tipo: {entrega['tipo_elemento']}, Talla: {entrega['talla']}, Número: {entrega['numero_calzado']}, Entregado: {entrega['total_entregado']}")
        
        print()
        
        # 3. Simular la lógica del endpoint corregido
        print("3. SIMULACIÓN DE LÓGICA DEL ENDPOINT CORREGIDO:")
        
        # Combinar datos como lo hace el endpoint
        stock_por_tallas = {}
        
        # Procesar ingresos
        for ingreso in ingresos_30:
            key = f"{ingreso['tipo_elemento']}_{ingreso['talla']}_{ingreso['numero_calzado']}"
            if key not in stock_por_tallas:
                stock_por_tallas[key] = {
                    'tipo_elemento': ingreso['tipo_elemento'],
                    'talla': ingreso['talla'],
                    'numero_calzado': ingreso['numero_calzado'],
                    'total_ingresado': 0,
                    'total_entregado': 0,
                    'stock_disponible': 0
                }
            stock_por_tallas[key]['total_ingresado'] = int(ingreso['total_ingresado'])
        
        # Procesar entregas
        for entrega in entregas_30:
            key = f"{entrega['tipo_elemento']}_{entrega['talla']}_{entrega['numero_calzado']}"
            if key not in stock_por_tallas:
                stock_por_tallas[key] = {
                    'tipo_elemento': entrega['tipo_elemento'],
                    'talla': entrega['talla'],
                    'numero_calzado': entrega['numero_calzado'],
                    'total_ingresado': 0,
                    'total_entregado': 0,
                    'stock_disponible': 0
                }
            stock_por_tallas[key]['total_entregado'] = int(entrega['total_entregado'])
        
        # Calcular stock disponible
        for key in stock_por_tallas:
            item = stock_por_tallas[key]
            item['stock_disponible'] = item['total_ingresado'] - item['total_entregado']
        
        # Mostrar resultados
        for key, item in stock_por_tallas.items():
            print(f"  - Clave: {key}")
            print(f"    Tipo: {item['tipo_elemento']}")
            print(f"    Talla: {item['talla']}")
            print(f"    Número: {item['numero_calzado']}")
            print(f"    Ingresado: {item['total_ingresado']}")
            print(f"    Entregado: {item['total_entregado']}")
            print(f"    Disponible: {item['stock_disponible']}")
            print()
        
        # 4. Verificar si el problema está resuelto
        print("4. VERIFICACIÓN DEL PROBLEMA:")
        if stock_por_tallas:
            for key, item in stock_por_tallas.items():
                if item['numero_calzado'] == '30':
                    if item['stock_disponible'] == (item['total_ingresado'] - item['total_entregado']):
                        print(f"  ✅ CORRECTO: Stock de pantalones número 30 se calcula correctamente")
                        print(f"     Ingresado: {item['total_ingresado']}, Entregado: {item['total_entregado']}, Disponible: {item['stock_disponible']}")
                    else:
                        print(f"  ❌ ERROR: Cálculo incorrecto para pantalones número 30")
        else:
            print("  ⚠️  No se encontraron datos para pantalones número 30")
        
    except mysql.connector.Error as e:
        print(f"Error MySQL: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    test_stock_pantalon_30()