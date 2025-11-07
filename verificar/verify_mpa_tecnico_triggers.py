import os
import mysql.connector


DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
}


def main():
    print("🔍 Verificando triggers y últimos datos de mpa_mantenimientos...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        print(f"❌ Error de conexión: {e}")
        return False

    try:
        cur = conn.cursor(dictionary=True)

        # Triggers en la tabla
        cur.execute("""
            SELECT TRIGGER_NAME, EVENT_MANIPULATION
            FROM INFORMATION_SCHEMA.TRIGGERS
            WHERE EVENT_OBJECT_SCHEMA = %s
              AND EVENT_OBJECT_TABLE = 'mpa_mantenimientos'
            ORDER BY TRIGGER_NAME
        """, (DB_CONFIG['database'],))
        triggers = cur.fetchall()
        if triggers:
            print("\n✅ Triggers encontrados:")
            for t in triggers:
                print(f"  - {t['TRIGGER_NAME']} ({t['EVENT_MANIPULATION']})")
        else:
            print("\n✗ No se encontraron triggers para mpa_mantenimientos")

        # Últimos mantenimientos
        cur.execute(
            "SELECT id_mpa_mantenimientos, placa, tecnico FROM mpa_mantenimientos ORDER BY id_mpa_mantenimientos DESC LIMIT 10"
        )
        rows = cur.fetchall()
        print("\n📋 Últimos registros:")
        if not rows:
            print("  (sin datos)")
        for r in rows:
            print(f"  #{r['id_mpa_mantenimientos']} placa={r['placa']} tecnico={r['tecnico']}")

        cur.close()
        conn.close()
        return True
    except mysql.connector.Error as e:
        print(f"❌ Error consultando BD: {e}")
        return False


if __name__ == '__main__':
    main()