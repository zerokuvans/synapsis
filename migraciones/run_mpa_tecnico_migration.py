import os
import mysql.connector


DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}


def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None


def execute_sql_file(connection, file_path):
    """Ejecuta un archivo SQL manejando bloques con DELIMITER (triggers)."""
    if not os.path.exists(file_path):
        print(f"❌ Archivo SQL no encontrado: {file_path}")
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    cursor = connection.cursor()

    current_delimiter = ';'
    in_delimiter_block = False
    buffer = ''

    def run_statement(stmt: str):
        s = stmt.strip()
        if not s:
            return True
        try:
            cursor.execute(s)
            return True
        except mysql.connector.Error as e:
            print(f"✗ Error ejecutando statement:\n{s}\n→ {e}")
            return False

    for raw_line in sql_content.splitlines():
        line = raw_line.strip()

        # Ignorar comentarios y vacíos
        if not line or line.startswith('--') or line.startswith('#'):
            continue

        # Manejo de DELIMITER
        if line.upper().startswith('DELIMITER'):
            if '//' in line:
                current_delimiter = '//'
                in_delimiter_block = True
            else:
                current_delimiter = ';'
                in_delimiter_block = False
            continue

        buffer += line + '\n'
        if line.endswith(current_delimiter):
            # Remover delimitador del final
            stmt = buffer.rstrip(current_delimiter + '\n').strip()
            buffer = ''
            ok = run_statement(stmt)
            if not ok:
                cursor.close()
                return False

    # Ejecutar cualquier remanente fuera de bloques
    if buffer.strip():
        ok = run_statement(buffer)
        if not ok:
            cursor.close()
            return False

    connection.commit()
    cursor.close()
    return True


def main():
    print("🚀 Migración de técnico en mpa_mantenimientos (histórico + triggers)")
    sql_path = os.path.join('sql', 'mpa_mantenimientos_tecnico_name_migration.sql')
    conn = get_db_connection()
    if not conn:
        return False
    try:
        ok = execute_sql_file(conn, sql_path)
        if not ok:
            print("❌ Falló la ejecución del archivo SQL")
            return False
        print("✅ Migración ejecutada correctamente")
        return True
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()