import mysql.connector
import sys
import os

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotaciones_api import get_db_connection
from validacion_stock_por_estado import ValidadorStockPorEstado

def verificar_resultado():
    """Verificar el resultado de la asignación"""
    print("=== VERIFICACIÓN DEL RESULTADO ===")
    
    connection = get_db_connection()
    if not connection:
        print("❌ Error de conexión a la base de datos")
        return
    
    try:
        # 1. Verificar stock actual después de la asignación
        print("\n1. Stock actual de botas después de la asignación:")
        validador = ValidadorStockPorEstado()
        stock_detallado = validador.obtener_stock_detallado_por_estado('botas')
        
        stock_valorado = stock_detallado.get('VALORADO', 0)
        stock_no_valorado = stock_detallado.get('NO VALORADO', 0)
        
        print(f"   VALORADO: {stock_valorado}")
        print(f"   NO VALORADO: {stock_no_valorado}")
        
        # Cerrar conexión del validador
        validador.cerrar_conexion()
        
        # 2. Verificar la última dotación creada
        print("\n2. Última dotación creada:")
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id_dotacion, cliente, botas, estado_botas, fecha_registro 
            FROM dotaciones 
            WHERE cliente = 'PRUEBA_BOTAS_NO_VALORADAS' 
            ORDER BY id_dotacion DESC 
            LIMIT 1
        """)
        
        resultado = cursor.fetchone()
        if resultado:
            id_dot, cliente, botas, estado_botas, fecha = resultado
            print(f"   ID Dotación: {id_dot}")
            print(f"   Cliente: {cliente}")
            print(f"   Botas asignadas: {botas}")
            print(f"   Estado registrado: {estado_botas}")
            print(f"   Fecha: {fecha}")
            
            # 3. Análisis del resultado
            print("\n3. Análisis del resultado:")
            if estado_botas == 'NO VALORADO':
                print("   ✅ El estado se registró correctamente como 'NO VALORADO'")
            else:
                print(f"   ❌ ERROR: El estado se registró como '{estado_botas}' en lugar de 'NO VALORADO'")
            
            # Verificar si el stock se descontó del estado correcto
            print("\n4. Verificación del descuento de stock:")
            print("   Stock inicial era: VALORADO=17, NO VALORADO=3")
            print(f"   Stock actual es: VALORADO={stock_valorado}, NO VALORADO={stock_no_valorado}")
            
            if stock_no_valorado == 2:  # 3 - 1 = 2
                print("   ✅ El stock se descontó correctamente del estado NO VALORADO")
            elif stock_valorado == 16:  # 17 - 1 = 16
                print("   ❌ ERROR: El stock se descontó del estado VALORADO (problema reportado por el usuario)")
            else:
                print("   ⚠️  Resultado inesperado en el descuento de stock")
        else:
            print("   ❌ No se encontró la dotación creada")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        connection.close()
        print("\n✅ Conexión cerrada")

if __name__ == "__main__":
    verificar_resultado()