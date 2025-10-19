#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificación para la tabla disponibilidad_equipos:
- Muestra columnas y valida existencia de 'observacion'
- Toma un serial (por argumento o el más reciente) y hace UPDATE observacion='prueba'
- Vuelve a leer para confirmar el cambio
- Lista triggers asociados a la tabla
"""

import mysql.connector
import sys
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
}


def get_conn():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None


def print_columns(cursor):
    cursor.execute(
        """
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """,
        ('capired', 'disponibilidad_equipos')
    )
    cols = cursor.fetchall()
    print("\n📋 Columnas de disponibilidad_equipos:")
    for c in cols:
        print(f" - {c[0]} ({c[1]}) NULLABLE={c[2]}")
    has_observacion = any(c[0].lower() == 'observacion' for c in cols)
    print(f"\n✔ Existe columna 'observacion': {has_observacion}")
    return has_observacion


def pick_serial(cursor):
    # Si viene por argumento, usarlo
    if len(sys.argv) > 1:
        return sys.argv[1]
    # Elegir el más reciente
    try:
        cursor.execute(
            """
            SELECT serial
            FROM disponibilidad_equipos
            ORDER BY fecha_creacion DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        return row[0] if row else None
    except mysql.connector.Error:
        cursor.execute("SELECT serial FROM disponibilidad_equipos LIMIT 1")
        row = cursor.fetchone()
        return row[0] if row else None


def get_row(cursor, serial):
    cursor.execute(
        """
        SELECT serial, cuenta, ot, observacion, super, estado, fecha_ultimo_movimiento, dias_ultimo
        FROM disponibilidad_equipos
        WHERE serial = %s
        LIMIT 1
        """,
        (serial,)
    )
    return cursor.fetchone()


def update_observacion(cursor, conn, serial, valor='prueba'):
    cursor.execute(
        """
        UPDATE disponibilidad_equipos
        SET observacion = %s
        WHERE serial = %s
        """,
        (valor, serial)
    )
    conn.commit()
    print(f"\n🛠 UPDATE ejecutado: observacion='{valor}' WHERE serial='{serial}' (rows={cursor.rowcount})")


def list_triggers(cursor):
    cursor.execute(
        """
        SELECT TRIGGER_NAME, EVENT_MANIPULATION, ACTION_TIMING, EVENT_OBJECT_TABLE, ACTION_STATEMENT
        FROM INFORMATION_SCHEMA.TRIGGERS
        WHERE TRIGGER_SCHEMA = %s AND EVENT_OBJECT_TABLE = %s
        ORDER BY TRIGGER_NAME
        """,
        ('capired', 'disponibilidad_equipos')
    )
    triggers = cursor.fetchall()
    print("\n⏱ Triggers asociados a disponibilidad_equipos:")
    if not triggers:
        print(" - (no hay triggers)")
    else:
        for t in triggers:
            name, event, timing, table, stmt = t
            stmt_short = (stmt[:200] + '...') if stmt and len(stmt) > 200 else (stmt or '')
            print(f" - {name}: {event} {timing} ON {table} | {stmt_short}")


def main():
    conn = get_conn()
    if not conn:
        return 1
    cursor = conn.cursor()
    try:
        has_obs = print_columns(cursor)
        serial = pick_serial(cursor)
        print(f"\n🔎 Serial de prueba: {serial}")
        if not serial:
            print("⚠ No se encontró ningún serial en la tabla.")
            return 0
        row_before = get_row(cursor, serial)
        print(f"\nAntes del UPDATE: {row_before}")
        # Probar UPDATE directo
        update_observacion(cursor, conn, serial, 'prueba')
        row_after = get_row(cursor, serial)
        print(f"Después del UPDATE: {row_after}")
        list_triggers(cursor)
        return 0
    except mysql.connector.Error as e:
        print(f"❌ Error durante verificación: {e}")
        return 2
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


if __name__ == '__main__':
    exit(main())