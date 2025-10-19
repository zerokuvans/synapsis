#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agrega la columna 'observacion' a la tabla 'disponibilidad_equipos' si no existe.
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
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'charset': 'utf8mb4'
}


def connect_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None


def column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
    """, (DB_CONFIG['database'], table, column))
    return cursor.fetchone()[0] > 0


def add_column_observacion(cursor):
    print("🔎 Verificando existencia de columna 'observacion' en disponibilidad_equipos...")
    if column_exists(cursor, 'disponibilidad_equipos', 'observacion'):
        print("✅ La columna 'observacion' ya existe. No se realizan cambios.")
        return False
    print("➕ Agregando columna 'observacion' (TEXT NULL)...")
    cursor.execute("ALTER TABLE disponibilidad_equipos ADD COLUMN observacion TEXT NULL")
    print("✅ Columna 'observacion' agregada correctamente.")
    return True


def main():
    conn = connect_db()
    if not conn:
        sys.exit(1)
    try:
        cur = conn.cursor()
        changed = add_column_observacion(cur)
        if changed:
            conn.commit()
        else:
            conn.rollback()
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