#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modifica el tipo de la columna 'observacion' en 'disponibilidad_equipos' a TEXT si actualmente es VARCHAR(100) u otro tipo corto.
Usa variables de entorno MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT.
"""
import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}


def connect_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None


def get_observacion_column_info(cursor):
    cursor.execute(
        """
        SELECT COLUMN_TYPE, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """,
        (DB_CONFIG['database'], 'disponibilidad_equipos', 'observacion')
    )
    return cursor.fetchone()


def alter_column_to_text(cursor):
    print("➕ Modificando columna 'observacion' a TEXT NULL...")
    cursor.execute("ALTER TABLE disponibilidad_equipos MODIFY COLUMN observacion TEXT NULL")
    print("✅ Columna 'observacion' modificada a TEXT NULL correctamente.")


def main():
    conn = connect_db()
    if not conn:
        sys.exit(1)
    try:
        cur = conn.cursor()
        info = get_observacion_column_info(cur)
        if not info:
            print("⚠️ La columna 'observacion' no existe; se intentará crearla como TEXT NULL.")
            cur.execute("ALTER TABLE disponibilidad_equipos ADD COLUMN observacion TEXT NULL")
            conn.commit()
            print("✅ Columna 'observacion' creada como TEXT NULL.")
        else:
            col_type, data_type, char_len = info
            print(f"🔎 Tipo actual: {col_type} | DataType: {data_type} | Len: {char_len}")
            # Si no es tipo text o tiene longitud limitada, modificar
            if (data_type.lower() != 'text') or (char_len is not None and char_len < 1000):
                alter_column_to_text(cur)
                conn.commit()
            else:
                print("✅ La columna 'observacion' ya es suficientemente amplia. No se realizan cambios.")
    except Exception as e:
        print(f"❌ Error ejecutando migración: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        sys.exit(1)
    finally:
        try:
            cur.close()
        except Exception:
            pass
        if conn.is_connected():
            conn.close()
    print("🏁 Migración finalizada.")


if __name__ == '__main__':
    main()