import requests
import json
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def test_api_vs_database():
    print("=== COMPARANDO API VS BASE DE DATOS ===")
    
    # 1. Probar la API
    print("\n1. PROBANDO API /api/stock-dotaciones:")
    try:
        response = requests.get('http://localhost:5000/api/stock-dotaciones')
        if response.status_code == 200:
            api_data = response.json()
            if api_data['success']:
                stock_botas_api = None
                for item in api_data['stock']:
                    if item['tipo_elemento'] == 'botas':
                        stock_botas_api = item
                        break
                
                if stock_botas_api:
                    print(f"   API - Botas:")
                    print(f"     Cantidad Ingresada: {stock_botas_api['cantidad_ingresada']}")
                    print(f"     Cantidad Entregada: {stock_botas_api['cantidad_entregada']}")
                    print(f"     Saldo Disponible: {stock_botas_api['saldo_disponible']}")
                else:
                    print("   ❌ No se encontraron datos de botas en la API")
            else:
                print(f"   ❌ Error en API: {api_data.get('message', 'Error desconocido')}")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error conectando a API: {e}")
    
    # 2. Consultar directamente la base de datos
    print("\n2. CONSULTANDO DIRECTAMENTE LA BASE DE DATOS:")
    
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
        cursor = connection.cursor(dictionary=True)
        
        # Consultar la vista directamente
        cursor.execute("SELECT * FROM vista_stock_dotaciones WHERE tipo_elemento = 'botas'")
        db_result = cursor.fetchone()
        
        if db_result:
            print(f"   BD - Botas:")
            print(f"     Cantidad Ingresada: {db_result['cantidad_ingresada']}")
            print(f"     Cantidad Entregada: {db_result['cantidad_entregada']}")
            print(f"     Saldo Disponible: {db_result['saldo_disponible']}")
        else:
            print("   ❌ No se encontraron datos de botas en la BD")
        
        # 3. Verificar si hay algún stock inicial no considerado
        print("\n3. VERIFICANDO POSIBLES FUENTES DE STOCK INICIAL:")
        
        # Buscar en todas las tablas que puedan tener stock inicial
        tablas_a_verificar = [
            ('stock_general', 'tipo_elemento', 'botas'),
            ('stock_inicial', 'tipo_elemento', 'botas'),
            ('inventario_inicial', 'tipo_elemento', 'botas'),
            ('stock_base', 'tipo_elemento', 'botas'),
            ('dotaciones_iniciales', 'tipo_elemento', 'botas')
        ]
        
        for tabla, campo, valor in tablas_a_verificar:
            try:
                cursor.execute(f"SELECT * FROM {tabla} WHERE {campo} = %s", (valor,))
                resultados = cursor.fetchall()
                if resultados:
                    print(f"   ✅ Encontrado en {tabla}:")
                    for resultado in resultados:
                        print(f"     {resultado}")
                else:
                    print(f"   ❌ Sin datos en {tabla}")
            except Error as e:
                if "doesn't exist" in str(e):
                    print(f"   ❌ Tabla {tabla} no existe")
                else:
                    print(f"   ❌ Error en {tabla}: {e}")
        
        # 4. Verificar si hay algún campo de stock inicial en ingresos_dotaciones
        print("\n4. VERIFICANDO ESTRUCTURA DE ingresos_dotaciones:")
        cursor.execute("DESCRIBE ingresos_dotaciones")
        estructura = cursor.fetchall()
        for campo in estructura:
            print(f"   {campo['Field']} - {campo['Type']}")
        
        # 5. Verificar si hay registros con observaciones que indiquen stock inicial
        print("\n5. VERIFICANDO OBSERVACIONES EN INGRESOS:")
        cursor.execute("""
            SELECT fecha_ingreso, cantidad, observaciones, proveedor
            FROM ingresos_dotaciones 
            WHERE tipo_elemento = 'botas'
            ORDER BY fecha_ingreso ASC
        """)
        ingresos = cursor.fetchall()
        
        for ingreso in ingresos:
            obs = ingreso['observaciones'] or ''
            if 'inicial' in obs.lower() or 'base' in obs.lower() or 'inventario' in obs.lower():
                print(f"   ⚠️  Posible stock inicial: {ingreso}")
        
        # 6. Verificar si hay diferencias en el cálculo
        print("\n6. ANÁLISIS FINAL:")
        if 'stock_botas_api' in locals() and stock_botas_api and db_result:
            if stock_botas_api['saldo_disponible'] == db_result['saldo_disponible']:
                print("   ✅ API y BD coinciden")
                print(f"   Stock calculado: {db_result['saldo_disponible']}")
                print(f"   Stock reportado por usuario: 28")
                print(f"   Diferencia: {28 - db_result['saldo_disponible']}")
            else:
                print("   ❌ API y BD no coinciden")
                print(f"   API: {stock_botas_api['saldo_disponible']}")
                print(f"   BD: {db_result['saldo_disponible']}")
        
    except Error as e:
        print(f"❌ Error de MySQL: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    test_api_vs_database()