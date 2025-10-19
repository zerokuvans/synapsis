#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importa datos desde el Excel 'seriales disponilbles.xlsx' a la tabla MySQL 'disponibilidad_equipos'.
- Muestra columnas y primeras filas para verificación.
- Inserta en bloque usando mysql.connector.

Requisitos:
- Variables de entorno MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT.
- Librerías: pandas, openpyxl, mysql-connector-python.
"""

import os
import sys
import math
import shutil
from datetime import datetime, date
import pandas as pd
import numpy as np
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

# Permitir pasar ruta por argumento: python import_disponibilidad_equipos.py <ruta_excel>
ARG_PATH = sys.argv[1] if len(sys.argv) > 1 else None

# Ruta del Excel dentro del proyecto
DEFAULT_PATH = os.path.join(os.getcwd(), 'excel', 'seriales disponilbles.xlsx')
COPIED_PATH = os.path.join(os.getcwd(), 'excel', 'seriales_import.xlsx')

EXCEL_PATH = ARG_PATH or (COPIED_PATH if os.path.exists(COPIED_PATH) else DEFAULT_PATH)

TABLE_NAME = 'disponibilidad_equipos'

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
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None


def table_exists(cursor, table_name: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = %s AND table_name = %s
        """,
        (DB_CONFIG['database'], table_name)
    )
    return cursor.fetchone()[0] > 0


def describe_table(cursor, table_name: str):
    cursor.execute(f"DESCRIBE {table_name}")
    cols = cursor.fetchall()
    print(f"\nEstructura de '{table_name}':")
    for c in cols:
        print(f"  - {c[0]} ({c[1]}) null={c[2]} key={c[3]}")
    return {c[0]: c[1] for c in cols}


def read_excel(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        print(f"❌ No existe el archivo: {path}")
        sys.exit(1)
    try:
        df = pd.read_excel(path)
    except PermissionError:
        # Intentar copiar a una ruta accesible y leer de allí
        try:
            print("⚠️ Permiso denegado al leer el Excel. Intentando copiar a 'excel/seriales_import.xlsx'...")
            shutil.copy2(DEFAULT_PATH, COPIED_PATH)
            df = pd.read_excel(COPIED_PATH)
            print("✅ Copia creada y leída correctamente:", COPIED_PATH)
        except Exception as e:
            print(f"❌ No fue posible copiar/leer el Excel: {e}")
            sys.exit(1)
    print("\nColumnas en Excel:", list(df.columns))
    print("Primeras 5 filas:")
    print(df.head(5))
    return df


def to_python_type(val, mysql_type: str):
    # Manejo de NaN/NaT
    if val is None:
        return None
    if isinstance(val, float) and math.isnan(val):
        return None
    if isinstance(val, (pd.Timestamp, np.datetime64)):
        if 'date' in mysql_type:
            return pd.to_datetime(val).date()
        else:
            return pd.to_datetime(val).to_pydatetime()
    if isinstance(val, np.generic):
        val = val.item()
    # Convertir por tipo MySQL
    t = mysql_type.lower()
    try:
        if 'int' in t:
            if isinstance(val, str) and val.strip() == '':
                return None
            return int(val)
        if 'decimal' in t or 'double' in t or 'float' in t:
            if isinstance(val, str) and val.strip() == '':
                return None
            return float(val)
        if 'date' in t and 'time' not in t:
            # tipo date
            d = pd.to_datetime(val, errors='coerce')
            return d.date() if d is not pd.NaT else None
        if 'datetime' in t or 'timestamp' in t or ('date' in t and 'time' in t):
            d = pd.to_datetime(val, errors='coerce')
            return d.to_pydatetime() if d is not pd.NaT else None
        # varchar/text/otros -> str
        return str(val).strip()
    except Exception:
        # Si falla conversión, devolver None para evitar error
        return None


def insert_dataframe(cursor, df: pd.DataFrame, table_name: str, column_types: dict) -> int:
    if df.empty:
        print("⚠️ DataFrame vacío, no se insertan filas.")
        return 0

    # Generar INSERT dinámico por columnas
    cols = list(df.columns)
    placeholders = ", ".join(["%s"] * len(cols))
    col_list = ", ".join([f"`{c}`" for c in cols])
    sql = f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})"

    # Preparar filas con conversión de tipos
    rows = []
    for i in range(len(df)):
        row_vals = []
        for c in cols:
            mysql_type = column_types.get(c, 'varchar(255)')
            val = df.iloc[i][c]
            row_vals.append(to_python_type(val, mysql_type))
        rows.append(tuple(row_vals))

    cursor.executemany(sql, rows)
    return len(rows)


def main():
    print("📦 Archivo Excel:", EXCEL_PATH)

    # Leer Excel
    df = read_excel(EXCEL_PATH)

    # Conexión DB
    conn = connect_db()
    if not conn:
        sys.exit(1)
    cursor = conn.cursor()

    # Validar existencia de la tabla
    if not table_exists(cursor, TABLE_NAME):
        print(f"❌ La tabla '{TABLE_NAME}' no existe en la BD '{DB_CONFIG['database']}'.")
        print("Por favor crea la tabla antes de importar.")
        cursor.close()
        conn.close()
        sys.exit(1)

    # Mostrar estructura tabla y obtener tipos
    column_types = describe_table(cursor, TABLE_NAME)

    # Validar que columnas del Excel coinciden con columnas de la tabla
    table_cols = list(column_types.keys())
    excel_cols = list(df.columns)

    # Comprobar coincidencia básica (Excel debe estar en la tabla)
    missing_in_table = [c for c in excel_cols if c not in table_cols]
    if missing_in_table:
        print("⚠️ Columnas del Excel que no están en la tabla:", missing_in_table)
        print("No se puede continuar si los nombres no coinciden.")
        cursor.close()
        conn.close()
        sys.exit(1)

    # Insertar datos
    try:
        inserted = insert_dataframe(cursor, df, TABLE_NAME, column_types)
        conn.commit()
        print(f"✅ Filas insertadas en '{TABLE_NAME}': {inserted}")
    except Error as e:
        conn.rollback()
        print(f"❌ Error insertando datos: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()