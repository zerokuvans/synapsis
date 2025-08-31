import mysql.connector
from datetime import datetime
import sys

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def clean_preoperacional_today(args=None):
    """Limpia los registros preoperacionales de hoy para permitir nuevos envíos"""
    
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Obtener la fecha de hoy
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"Limpiando registros preoperacionales del día: {today}")
        
        # Query to check today's records using the fecha column
        query = "SELECT COUNT(*) FROM preoperacional WHERE DATE(fecha) = CURDATE()"
        cursor.execute(query)
        count = cursor.fetchone()[0]
        
        if args.check:
            print(f"Registros preoperacionales encontrados para hoy: {count}")
            if count > 0:
                # Show details of today's records
                detail_query = "SELECT id_preoperacional, id_codigo_consumidor, supervisor, fecha FROM preoperacional WHERE DATE(fecha) = CURDATE() ORDER BY id_preoperacional DESC LIMIT 10"
                cursor.execute(detail_query)
                records = cursor.fetchall()
                print("\nRegistros de hoy:")
                for record in records:
                    print(f"ID: {record[0]}, Usuario: {record[1]}, Supervisor: {record[2]}, Fecha: {record[3]}")
        else:
            if count > 0:
                # Delete today's records
                print(f"Se encontraron {count} registros preoperacionales para hoy")
                confirm = input("¿Desea eliminar los registros de hoy? (escriba 'SI' para confirmar): ")
                if confirm == 'SI':
                    delete_query = "DELETE FROM preoperacional WHERE DATE(fecha) = CURDATE()"
                    cursor.execute(delete_query)
                    connection.commit()
                    print(f"Se eliminaron {count} registros preoperacionales de hoy")
                else:
                    print("Operación cancelada")
            else:
                print("No hay registros preoperacionales de hoy para eliminar")
        
        return True
        
    except mysql.connector.Error as e:
        print(f"Error de base de datos: {e}")
        return False
        
    except Exception as e:
        print(f"Error general: {e}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def check_preoperacional_today():
    """Solo verifica los registros de hoy sin eliminar"""
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"Verificando registros preoperacionales del día: {today}")
        
        cursor.execute("""
            SELECT id_preoperacional, id_codigo_consumidor, fecha, observaciones 
            FROM preoperacional 
            WHERE DATE(fecha) = %s
            ORDER BY id_preoperacional DESC
        """, (today,))
        
        records = cursor.fetchall()
        
        if not records:
            print("✓ No hay registros preoperacionales para hoy. El usuario puede enviar el formulario.")
        else:
            print(f"\n⚠ Se encontraron {len(records)} registros para hoy:")
            for record in records:
                print(f"  ID: {record[0]}, Usuario: {record[1]}, Fecha: {record[2]}")
                if record[3]:  # observaciones
                    print(f"     Observaciones: {record[3][:50]}...")
                print()
        
        return len(records) == 0
        
    except Exception as e:
        print(f"Error: {e}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Gestionar registros preoperacionales')
    parser.add_argument('--check', action='store_true', help='Solo verificar registros sin eliminar')
    args = parser.parse_args()
    
    if args.check:
        check_preoperacional_today()
    else:
        clean_preoperacional_today(args)