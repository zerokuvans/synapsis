#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para describir la estructura de la tabla base_codigos_facturacion.
Escribe resultados en data/describe_base_codigos_facturacion.txt
"""

import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

OUTPUT_PATH = os.path.join('data', 'describe_base_codigos_facturacion.txt')

load_dotenv()


def get_db_config():
    return {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
        'database': os.getenv('MYSQL_DB', 'capired'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
    }


def conectar_db():
    try:
        cnx = mysql.connector.connect(**get_db_config())
        return cnx
    except Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None


def describe_tabla(cnx, tabla):
    lines = []
    try:
        cursor = cnx.cursor()
        cursor.execute(f"SHOW COLUMNS FROM {tabla}")
        columnas = cursor.fetchall()
        lines.append(f"== Columnas de {tabla} ==\n")
        for col in columnas:
            lines.append(f"- {col[0]} | {col[1]} | Null={col[2]} | Key={col[3]} | Default={col[4]} | Extra={col[5]}\n")
        cursor.close()
    except Error as e:
        lines.append(f"❌ Error describiendo la tabla {tabla}: {e}\n")
    return lines


def muestra_ejemplo(cnx, tabla):
    lines = []
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {tabla} LIMIT 1")
        fila = cursor.fetchone()
        lines.append(f"\n== Ejemplo de fila en {tabla} ==\n")
        if fila:
            for k, v in fila.items():
                lines.append(f"{k}: {v}\n")
        else:
            lines.append("(La tabla no tiene filas)\n")
        cursor.close()
    except Error as e:
        lines.append(f"❌ Error consultando ejemplo de {tabla}: {e}\n")
    return lines


def main():
    tabla = 'base_codigos_facturacion'
    cnx = conectar_db()
    if not cnx:
        return
    lines = []
    lines += describe_tabla(cnx, tabla)
    lines += muestra_ejemplo(cnx, tabla)
    cnx.close()

    os.makedirs('data', exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✅ Resultado escrito en {OUTPUT_PATH}")


if __name__ == '__main__':
    main()