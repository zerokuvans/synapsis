#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consulta: SELECT serial, super, observacion FROM disponibilidad_equipos WHERE serial = 'SKYWDA7C5F9B'
Compara 'super' con 'CACERES MARTINEZ CARLOS' y muestra diferencias (trim/upper)
"""
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

SERIAL = 'SKYWDA7C5F9B'
USER_PROVIDED = 'CACERES MARTINEZ CARLOS'

def main():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT serial, super, observacion
            FROM disponibilidad_equipos
            WHERE serial = %s
            LIMIT 1
            """,
            (SERIAL,)
        )
        row = cur.fetchone()
        if not row:
            print("No se encontró el serial en disponibilidad_equipos:", SERIAL)
            return
        serial = row.get('serial')
        super_db = row.get('super')
        observacion_db = row.get('observacion')
        print("=== Resultado de la consulta ===")
        print(f"serial       : {serial}")
        print(f"super (raw)  : {repr(super_db)}")
        print(f"observacion  : {repr(observacion_db)}")
        # Normalizaciones
        super_norm = (super_db or '').strip().upper()
        user_norm = USER_PROVIDED.strip().upper()
        print("=== Comparaciones ===")
        print(f"Usuario proporcionado (raw): {repr(USER_PROVIDED)}")
        print(f"super == usuario (exacto)   : {super_db == USER_PROVIDED}")
        print(f"trim+upper coincide         : {super_norm == user_norm}")
        # Mostrar diferencias de espacios si aplica
        if super_db is not None:
            print(f"len(super_db)={len(super_db)}, len(trim)={len(super_db.strip())}")
            if super_norm != user_norm:
                print(f"super_norm   : {repr(super_norm)}")
                print(f"user_norm    : {repr(user_norm)}")
        else:
            print("super_db es None o cadena vacía")
    except Error as e:
        print("Error de DB:", e)
    finally:
        try:
            cur.close()
        except:
            pass
        try:
            if conn and conn.is_connected():
                conn.close()
        except:
            pass

if __name__ == '__main__':
    main()