#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT'))
}

def verificar_triggers():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("=== Verificando triggers de stock ferretero ===")
            
            # Verificar triggers existentes
            cursor.execute("SHOW TRIGGERS LIKE '%ferretero%'")
            triggers = cursor.fetchall()
            
            if triggers:
                print(f"\n✓ Se encontraron {len(triggers)} triggers:")
                for trigger in triggers:
                    print(f"  - Trigger: {trigger[0]}")
                    print(f"    Evento: {trigger[1]}")
                    print(f"    Tabla: {trigger[2]}")
                    print(f"    Timing: {trigger[4]}")
                    print()
            else:
                print("❌ No se encontraron triggers de ferretero")
                
            # Verificar estado actual del stock
            print("=== Estado actual del stock ===")
            cursor.execute("SELECT material_tipo, cantidad_disponible FROM stock_ferretero ORDER BY material_tipo")
            stock = cursor.fetchall()
            
            for item in stock:
                print(f"  {item[0]}: {item[1]} unidades")
                
            # Verificar última entrada registrada
            print("\n=== Última entrada registrada ===")
            cursor.execute("""
                SELECT id_entrada, material_tipo, cantidad_entrada, fecha_registro 
                FROM entradas_ferretero 
                ORDER BY fecha_registro DESC 
                LIMIT 1
            """)
            ultima_entrada = cursor.fetchone()
            
            if ultima_entrada:
                print(f"  ID: {ultima_entrada[0]}")
                print(f"  Material: {ultima_entrada[1]}")
                print(f"  Cantidad: {ultima_entrada[2]}")
                print(f"  Fecha: {ultima_entrada[3]}")
                
                # Verificar si hay movimiento asociado
                cursor.execute("""
                    SELECT COUNT(*) FROM movimientos_stock_ferretero 
                    WHERE referencia_id = %s AND referencia_tipo = 'entrada_ferretero'
                """, (ultima_entrada[0],))
                movimientos = cursor.fetchone()[0]
                
                if movimientos > 0:
                    print(f"  ✓ Tiene {movimientos} movimiento(s) asociado(s)")
                else:
                    print(f"  ❌ No tiene movimientos asociados - TRIGGER NO FUNCIONÓ")
            else:
                print("  No hay entradas registradas")
                
            connection.close()
            
    except Error as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verificar_triggers()