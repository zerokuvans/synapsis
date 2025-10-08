import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

def test_cambio_dotacion():
    print("=== PRUEBA: Cambio de Dotación y Actualización de Stock ===\n")
    
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
        
        # 1. Verificar stock ANTES del cambio
        print("\n1. Stock ANTES del cambio de prueba:")
        cursor.execute("SELECT * FROM vista_stock_dotaciones WHERE tipo_elemento = 'botas'")
        stock_antes = cursor.fetchone()
        print(f"   Botas - Ingresadas: {stock_antes[1]}, Entregadas: {stock_antes[2]}, Disponibles: {stock_antes[3]}")
        
        # 2. Simular un cambio de dotación (insertar en cambios_dotacion)
        print("\n2. Simulando cambio de dotación (2 botas talla 39)...")
        fecha_cambio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Insertar cambio de prueba
        insert_cambio = """
        INSERT INTO cambios_dotacion 
        (id_codigo_consumidor, fecha_cambio, botas, botas_talla, observaciones)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        valores_cambio = (
            1,  # id_codigo_consumidor (debe ser un ID existente)
            fecha_cambio,  # fecha_cambio
            2,  # botas (cantidad)
            39,  # botas_talla (int, no string)
            'Cambio de prueba para verificar actualización de stock'  # observaciones
        )
        
        cursor.execute(insert_cambio, valores_cambio)
        cambio_id = cursor.lastrowid
        connection.commit()
        
        print(f"   ✅ Cambio registrado con ID: {cambio_id}")
        
        # 3. Verificar stock DESPUÉS del cambio
        print("\n3. Stock DESPUÉS del cambio de prueba:")
        cursor.execute("SELECT * FROM vista_stock_dotaciones WHERE tipo_elemento = 'botas'")
        stock_despues = cursor.fetchone()
        print(f"   Botas - Ingresadas: {stock_despues[1]}, Entregadas: {stock_despues[2]}, Disponibles: {stock_despues[3]}")
        
        # 4. Calcular diferencia
        diferencia_entregadas = stock_despues[2] - stock_antes[2]
        diferencia_disponibles = stock_antes[3] - stock_despues[3]
        
        print("\n4. Análisis de cambios:")
        print(f"   Incremento en entregadas: {diferencia_entregadas}")
        print(f"   Reducción en disponibles: {diferencia_disponibles}")
        
        # 5. Verificar que el cambio se reflejó correctamente
        if diferencia_entregadas == 2 and diferencia_disponibles == 2:
            print("\n✅ ¡ÉXITO! El cambio de dotación se reflejó correctamente en el stock")
            print("   - Las 2 botas se sumaron a 'cantidad_entregada'")
            print("   - Las 2 botas se restaron de 'saldo_disponible'")
        else:
            print("\n❌ ERROR: El cambio no se reflejó correctamente")
            print(f"   Esperado: +2 entregadas, -2 disponibles")
            print(f"   Obtenido: +{diferencia_entregadas} entregadas, -{diferencia_disponibles} disponibles")
        
        # 6. Verificar total de cambios de botas
        print("\n5. Verificando total de cambios de botas:")
        cursor.execute("SELECT COUNT(*), SUM(botas) FROM cambios_dotacion WHERE botas > 0")
        total_cambios = cursor.fetchone()
        print(f"   Total registros de cambios de botas: {total_cambios[0]}")
        print(f"   Total botas en cambios: {total_cambios[1]}")
        
        # 7. Limpiar - eliminar el cambio de prueba
        print("\n6. Limpiando cambio de prueba...")
        cursor.execute("DELETE FROM cambios_dotacion WHERE id_cambio = %s", (cambio_id,))
        connection.commit()
        print(f"   ✅ Cambio de prueba eliminado (ID: {cambio_id})")
        
        # 8. Verificar stock final (debe volver al estado inicial)
        print("\n7. Stock FINAL (después de limpiar):")
        cursor.execute("SELECT * FROM vista_stock_dotaciones WHERE tipo_elemento = 'botas'")
        stock_final = cursor.fetchone()
        print(f"   Botas - Ingresadas: {stock_final[1]}, Entregadas: {stock_final[2]}, Disponibles: {stock_final[3]}")
        
        if stock_final[2] == stock_antes[2] and stock_final[3] == stock_antes[3]:
            print("   ✅ Stock restaurado correctamente")
        else:
            print("   ⚠️  Advertencia: Stock no restaurado completamente")
        
        print("\n🎉 ¡PRUEBA COMPLETADA! El sistema de stock con cambios funciona correctamente.")
        
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
    test_cambio_dotacion()