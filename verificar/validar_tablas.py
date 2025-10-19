import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Cargar variables desde .env si no están en el entorno

def load_env_from_dotenv():
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        env_path = os.path.join(project_root, '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and value and not os.getenv(key):
                        os.environ[key] = value
    except Exception as e:
        print(f"[WARN] No se pudo cargar .env: {e}")

load_env_from_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'validacion_tablas')


def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"[ERROR] Conexión MySQL: {e}")
        return None


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_tables(cursor):
    cursor.execute("SELECT TABLE_NAME FROM information_schema.tables WHERE table_schema = DATABASE() ORDER BY TABLE_NAME")
    return [row[0] for row in cursor.fetchall()]


def fetch_columns(cursor, table):
    cursor.execute(
        """
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY, EXTRA
        FROM information_schema.columns
        WHERE table_schema = DATABASE() AND table_name = %s
        ORDER BY ORDINAL_POSITION
        """,
        (table,)
    )
    return cursor.fetchall()


def fetch_sample_row(cursor, table):
    try:
        cursor.execute(f"SELECT * FROM `{table}` LIMIT 1")
        return cursor.fetchone(), [desc[0] for desc in cursor.description] if cursor.description else []
    except Exception as e:
        return None, []


def write_table_report(table, columns, sample_row, sample_cols):
    path = os.path.join(OUTPUT_DIR, f"{table}.txt")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"Tabla: {table}\n")
        f.write(f"Generado: {datetime.now().isoformat()}\n\n")
        f.write("Columnas:\n")
        for col in columns:
            name, dtype, nullable, default, key, extra = col
            f.write(f"- {name} ({dtype}) NULLABLE={nullable} DEFAULT={default} KEY={key} EXTRA={extra}\n")
        f.write("\nMuestra de datos (LIMIT 1):\n")
        if sample_row and sample_cols:
            for i, col_name in enumerate(sample_cols):
                f.write(f"{col_name}: {sample_row[i]}\n")
        else:
            f.write("(sin datos)\n")
    print(f"[OK] Reporte generado: {path}")


def main():
    ensure_output_dir()
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return
    try:
        cursor = conn.cursor()
        tables = fetch_tables(cursor)
        if not tables:
            print("No se encontraron tablas en el esquema actual.")
            return
        print(f"Validando {len(tables)} tablas...")
        for table in tables:
            cols = fetch_columns(cursor, table)
            sample, sample_cols = fetch_sample_row(cursor, table)
            write_table_report(table, cols, sample, sample_cols)
        print(f"Listo. Archivos en: {OUTPUT_DIR}")
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        if conn and conn.is_connected():
            conn.close()


if __name__ == '__main__':
    main()