import os
import sys
from datetime import datetime
from dotenv import load_dotenv

try:
    import mysql.connector
except ImportError:
    print("Falta el paquete mysql-connector-python. Instálalo con: pip install mysql-connector-python")
    sys.exit(1)

# Cargar variables de entorno desde .env
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

SUPERVISOR = os.getenv('SUPERVISOR_NOMBRE', 'CACERES MARTINEZ CARLOS')


def conectar_db():
    return mysql.connector.connect(**DB_CONFIG)


def mostrar_columnas(cursor):
    try:
        cursor.execute("SHOW COLUMNS FROM disponibilidad_equipos")
        cols = cursor.fetchall()
        print("\nColumnas en disponibilidad_equipos:")
        for c in cols:
            # mysql.connector con dictionary=True devuelve dict con 'Field'
            nombre = c.get('Field', list(c.values())[0] if isinstance(c, dict) else c[0])
            tipo = c.get('Type', '') if isinstance(c, dict) else ''
            print(f"- {nombre} {tipo}")
    except Exception as e:
        print(f"No se pudieron listar columnas: {e}")


def contar_equipos(cursor, supervisor):
    cursor.execute("SELECT COUNT(*) as total FROM disponibilidad_equipos WHERE super = %s", (supervisor,))
    row = cursor.fetchone()
    return row['total'] if row and 'total' in row else 0


def obtener_muestras(cursor, supervisor, limit=10):
    cursor.execute("SELECT * FROM disponibilidad_equipos WHERE super = %s LIMIT %s", (supervisor, limit))
    return cursor.fetchall()


def listar_supervisores(cursor, limit=20):
    cursor.execute("SELECT super, COUNT(*) as cantidad FROM disponibilidad_equipos GROUP BY super ORDER BY cantidad DESC, super ASC LIMIT %s", (limit,))
    return cursor.fetchall()


def normalizaciones(cursor, supervisor):
    consulta = """
        SELECT super, COUNT(*) as cantidad
        FROM disponibilidad_equipos
        WHERE REPLACE(UPPER(TRIM(super)), '  ', ' ') = REPLACE(UPPER(TRIM(%s)), '  ', ' ')
        GROUP BY super
    """
    cursor.execute(consulta, (supervisor,))
    return cursor.fetchall()


def main():
    print(f"Usando configuración MySQL: host={DB_CONFIG['host']} db={DB_CONFIG['database']} user={DB_CONFIG['user']} port={DB_CONFIG['port']}")
    print(f"Conectando a MySQL...")
    try:
        cnx = conectar_db()
        cursor = cnx.cursor(dictionary=True)
    except Exception as e:
        print(f"Error de conexión: {e}")
        sys.exit(1)

    print(f"\nSupervisor objetivo: '{SUPERVISOR}'\n")

    try:
        mostrar_columnas(cursor)

        total = contar_equipos(cursor, SUPERVISOR)
        print(f"\nTotal de equipos asignados: {total}")

        if total == 0:
            print("\nNo se encontraron equipos con coincidencia exacta del nombre. Probando normalización de espacios y mayúsculas...")
            normas = normalizaciones(cursor, SUPERVISOR)
            if normas:
                print("Coincidencias por normalización (super en BD y cantidad):")
                for n in normas:
                    print(f"- '{n['super']}' -> {n['cantidad']} equipos")
            else:
                print("No hay coincidencias ni siquiera con normalización.")

            print("\nSupervisores con más equipos (TOP 20):")
            for s in listar_supervisores(cursor):
                print(f"- {s['super']}: {s['cantidad']} equipos")
        else:
            print("\nPrimeros 10 registros:")
            for i, eq in enumerate(obtener_muestras(cursor, SUPERVISOR, 10), 1):
                serial = eq.get('serial', '')
                tecnico = eq.get('tecnico', '')
                familia = eq.get('familia', '')
                elemento = eq.get('elemento', '')
                superv = eq.get('super', '')
                fecha_ultimo = eq.get('fecha_ultimo')
                dias_ultimo = eq.get('dias_ultimo')
                estado = eq.get('estado', '')
                cuenta = eq.get('cuenta', '')
                ot = eq.get('ot', '')
                print(f"{i}. Serial: {serial} | Técnico: {tecnico} | Familia: {familia} | Elemento: {elemento} | Super: {superv} | Fecha Últ.: {fecha_ultimo} | Días: {dias_ultimo} | Estado: {estado} | Cuenta: {cuenta} | OT: {ot}")

    except Exception as e:
        print(f"Error en consulta: {e}")
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            cnx.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()