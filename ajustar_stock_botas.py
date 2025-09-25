import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

def ajustar_stock_botas():
    print("=== AJUSTE DE STOCK DE BOTAS ===")
    print("Este script permite agregar un ajuste de inventario para corregir el stock de botas")
    print("Análisis actual:")
    print("- Stock calculado por sistema: 27 botas")
    print("- Stock reportado por usuario: 28 botas")
    print("- Diferencia: 1 bota")
    print()
    
    # Solicitar confirmación
    respuesta = input("¿Desea agregar 1 bota como ajuste de inventario? (s/n): ").lower().strip()
    
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Operación cancelada")
        return
    
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
        
        print("✅ Conexión exitosa a MySQL\n")
        
        # 1. Verificar stock actual antes del ajuste
        print("1. VERIFICANDO STOCK ACTUAL:")
        cursor.execute("""
            SELECT cantidad_ingresada, cantidad_entregada, saldo_disponible
            FROM vista_stock_dotaciones 
            WHERE tipo_elemento = 'botas'
        """)
        stock_actual = cursor.fetchone()
        
        if stock_actual:
            print(f"   Cantidad ingresada: {stock_actual['cantidad_ingresada']}")
            print(f"   Cantidad entregada: {stock_actual['cantidad_entregada']}")
            print(f"   Saldo disponible: {stock_actual['saldo_disponible']}")
        else:
            print("   ❌ No se encontró información de stock para botas")
            return
        
        # 2. Agregar ajuste de inventario
        print("\n2. AGREGANDO AJUSTE DE INVENTARIO:")
        
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Insertar en ingresos_dotaciones como ajuste de inventario
        query_ajuste = """
            INSERT INTO ingresos_dotaciones 
            (tipo_elemento, cantidad, proveedor, observaciones, fecha_ingreso, usuario_registro)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        valores_ajuste = (
            'botas',
            1,
            'AJUSTE DE INVENTARIO',
            'Ajuste de inventario - Diferencia detectada entre stock físico y sistema',
            fecha_actual,
            'SISTEMA'
        )
        
        cursor.execute(query_ajuste, valores_ajuste)
        connection.commit()
        
        print(f"   ✅ Ajuste agregado exitosamente")
        print(f"   - Cantidad: 1 bota")
        print(f"   - Proveedor: AJUSTE DE INVENTARIO")
        print(f"   - Fecha: {fecha_actual}")
        
        # 3. Verificar stock después del ajuste
        print("\n3. VERIFICANDO STOCK DESPUÉS DEL AJUSTE:")
        cursor.execute("""
            SELECT cantidad_ingresada, cantidad_entregada, saldo_disponible
            FROM vista_stock_dotaciones 
            WHERE tipo_elemento = 'botas'
        """)
        stock_nuevo = cursor.fetchone()
        
        if stock_nuevo:
            print(f"   Cantidad ingresada: {stock_nuevo['cantidad_ingresada']}")
            print(f"   Cantidad entregada: {stock_nuevo['cantidad_entregada']}")
            print(f"   Saldo disponible: {stock_nuevo['saldo_disponible']}")
            
            if stock_nuevo['saldo_disponible'] == 28:
                print("   ✅ Stock corregido exitosamente - Ahora muestra 28 botas")
            else:
                print(f"   ⚠️ Stock actual: {stock_nuevo['saldo_disponible']} (esperado: 28)")
        
        # 4. Mostrar resumen del ajuste
        print("\n4. RESUMEN DEL AJUSTE:")
        print(f"   Stock anterior: {stock_actual['saldo_disponible']} botas")
        print(f"   Ajuste aplicado: +1 bota")
        print(f"   Stock nuevo: {stock_nuevo['saldo_disponible']} botas")
        print(f"   Estado: {'✅ CORRECTO' if stock_nuevo['saldo_disponible'] == 28 else '❌ REVISAR'}")
        
        # 5. Verificar el último registro agregado
        print("\n5. VERIFICANDO ÚLTIMO REGISTRO:")
        cursor.execute("""
            SELECT id, tipo_elemento, cantidad, proveedor, observaciones, fecha_ingreso
            FROM ingresos_dotaciones 
            WHERE tipo_elemento = 'botas'
            ORDER BY id DESC
            LIMIT 1
        """)
        ultimo_registro = cursor.fetchone()
        
        if ultimo_registro:
            print(f"   ID: {ultimo_registro['id']}")
            print(f"   Tipo: {ultimo_registro['tipo_elemento']}")
            print(f"   Cantidad: {ultimo_registro['cantidad']}")
            print(f"   Proveedor: {ultimo_registro['proveedor']}")
            print(f"   Observaciones: {ultimo_registro['observaciones']}")
            print(f"   Fecha: {ultimo_registro['fecha_ingreso']}")
        
    except Error as e:
        print(f"❌ Error de MySQL: {e}")
        if connection:
            connection.rollback()
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión cerrada")

def mostrar_opciones():
    print("\n=== OPCIONES DISPONIBLES ===")
    print("1. Ejecutar ajuste de inventario (+1 bota)")
    print("2. Solo verificar stock actual")
    print("3. Salir")
    print()
    
    opcion = input("Seleccione una opción (1-3): ").strip()
    
    if opcion == '1':
        ajustar_stock_botas()
    elif opcion == '2':
        verificar_stock_actual()
    elif opcion == '3':
        print("👋 Saliendo...")
    else:
        print("❌ Opción inválida")
        mostrar_opciones()

def verificar_stock_actual():
    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'database': os.getenv('MYSQL_DB', 'capired'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'charset': 'utf8mb4'
    }
    
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT cantidad_ingresada, cantidad_entregada, saldo_disponible
            FROM vista_stock_dotaciones 
            WHERE tipo_elemento = 'botas'
        """)
        stock = cursor.fetchone()
        
        if stock:
            print(f"\n📊 STOCK ACTUAL DE BOTAS:")
            print(f"   Cantidad ingresada: {stock['cantidad_ingresada']}")
            print(f"   Cantidad entregada: {stock['cantidad_entregada']}")
            print(f"   Saldo disponible: {stock['saldo_disponible']}")
        else:
            print("❌ No se encontró información de stock")
            
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    mostrar_opciones()