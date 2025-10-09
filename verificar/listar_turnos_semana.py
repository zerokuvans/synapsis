#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()

db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
}

def main():
    if len(sys.argv) >= 3:
        fecha_inicio = sys.argv[1]
        fecha_fin = sys.argv[2]
    else:
        hoy = datetime.now()
        monday_offset = (hoy.weekday() + 6) % 7  # lunes=0
        start = hoy - timedelta(days=monday_offset)
        end = start + timedelta(days=6)
        fecha_inicio = start.strftime('%Y-%m-%d')
        fecha_fin = end.strftime('%Y-%m-%d')
    print(f"Consultando turnos entre {fecha_inicio} y {fecha_fin}\n")

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT 
                atb.analistas_turnos_fecha,
                atb.analistas_turnos_analista,
                atb.analistas_turnos_turno,
                atb.analistas_turnos_almuerzo,
                atb.analistas_turnos_break,
                atb.analistas_turnos_horas_trabajadas
            FROM analistas_turnos_base atb
            WHERE atb.analistas_turnos_fecha BETWEEN %s AND %s
            ORDER BY atb.analistas_turnos_fecha, atb.analistas_turnos_analista
            """,
            (fecha_inicio, fecha_fin)
        )
        rows = cursor.fetchall()
        print(f"Registros encontrados: {len(rows)}")
        for r in rows[:20]:
            fecha_val = r['analistas_turnos_fecha']
            if hasattr(fecha_val, 'strftime'):
                fecha_str = fecha_val.strftime('%Y-%m-%d')
            else:
                fecha_str = str(fecha_val)[:10]
            print(json.dumps({
                'fecha': fecha_str,
                'analista_id': r['analistas_turnos_analista'],
                'turno_guardado': r['analistas_turnos_turno'],
                'almuerzo': r['analistas_turnos_almuerzo'],
                'break': r['analistas_turnos_break'],
                'horas': r['analistas_turnos_horas_trabajadas'],
            }, ensure_ascii=False))

        cursor.execute(
            """
            SELECT 
                atb.analistas_turnos_fecha,
                atb.analistas_turnos_analista,
                atb.analistas_turnos_turno,
                t.turnos_horario,
                t.turnos_nombre
            FROM analistas_turnos_base atb
            LEFT JOIN turnos t ON atb.analistas_turnos_turno = t.turnos_horario
            WHERE atb.analistas_turnos_fecha BETWEEN %s AND %s
            ORDER BY atb.analistas_turnos_fecha, atb.analistas_turnos_analista
            """,
            (fecha_inicio, fecha_fin)
        )
        join_rows = cursor.fetchall()
        print(f"\nRegistros con join: {len(join_rows)}")
        for r in join_rows[:20]:
            fecha_val = r['analistas_turnos_fecha']
            fecha_str = fecha_val.strftime('%Y-%m-%d') if hasattr(fecha_val, 'strftime') else str(fecha_val)[:10]
            print(json.dumps({
                'fecha': fecha_str,
                'analista_id': r['analistas_turnos_analista'],
                'turno_guardado': r['analistas_turnos_turno'],
                'turno_horario': r['turnos_horario'],
                'turno_nombre': r['turnos_nombre'],
            }, ensure_ascii=False))

    except Error as e:
        print(f"ERROR MySQL: {e}")
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass

if __name__ == '__main__':
    main()