#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import get_db_connection

def main():
    ced = '1030545700'  # BETANCOURT CAÑAS DANIEL FRANCISCO
    conn = get_db_connection()
    if conn is None:
        print('❌ No se pudo conectar a la base de datos')
        return
    cur = conn.cursor(dictionary=True)

    print('== Periodico existente ==')
    cur.execute(
        """
        SELECT DATE(vcP.sstt_vencimientos_cursos_fecha_ven) AS fecha
        FROM sstt_vencimientos_cursos vcP
        WHERE vcP.recurso_operativo_cedula=%s
          AND vcP.sstt_vencimientos_cursos_tipo_curso='EXAMEN MEDICO PERIODICO'
          AND vcP.sstt_vencimientos_cursos_fecha_ven IS NOT NULL
          AND vcP.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01')
          AND vcP.sstt_vencimientos_cursos_fecha_ven > '1900-01-01'
        ORDER BY vcP.sstt_vencimientos_cursos_fecha_ven DESC
        LIMIT 5
        """,
        (ced,)
    )
    rowsP = cur.fetchall() or []
    for r in rowsP:
        print('PERIODICO:', r['fecha'])

    print('\n== Export rows (aplicando filtro) ==')
    sql = """
    SELECT 
        ro.recurso_operativo_cedula AS cedula,
        ro.nombre AS nombre,
        vc.sstt_vencimientos_cursos_tipo_curso AS curso,
        DATE(vc.sstt_vencimientos_cursos_fecha_ven) AS vencimiento
    FROM sstt_vencimientos_cursos vc
    LEFT JOIN recurso_operativo ro ON vc.recurso_operativo_cedula = ro.recurso_operativo_cedula
    WHERE ro.estado='Activo'
      AND ro.recurso_operativo_cedula = %s
      AND (
        vc.sstt_vencimientos_cursos_fecha_ven IS NOT NULL
        AND vc.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01')
        AND vc.sstt_vencimientos_cursos_fecha_ven > '1900-01-01'
        AND (
          DATE(vc.sstt_vencimientos_cursos_fecha_ven) <= CURDATE()
          OR (
            DATE(vc.sstt_vencimientos_cursos_fecha_ven) > CURDATE()
            AND DATEDIFF(vc.sstt_vencimientos_cursos_fecha_ven, CURDATE()) <= 30
          )
        )
      )
      AND (vc.sstt_vencimientos_cursos_validado IS NULL OR vc.sstt_vencimientos_cursos_validado = 0)
      AND (vc.sstt_vencimientos_cursos_pendiente IS NULL OR vc.sstt_vencimientos_cursos_pendiente = 0)
      AND NOT EXISTS (
        SELECT 1 FROM sstt_vencimientos_cursos vc2
        WHERE vc2.recurso_operativo_cedula = vc.recurso_operativo_cedula
          AND vc2.sstt_vencimientos_cursos_tipo_curso = vc.sstt_vencimientos_cursos_tipo_curso
          AND vc2.sstt_vencimientos_cursos_fecha_ven IS NOT NULL
          AND vc2.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01')
          AND vc2.sstt_vencimientos_cursos_fecha_ven > '1900-01-01'
          AND DATE(vc2.sstt_vencimientos_cursos_fecha_ven) > CURDATE()
          AND DATEDIFF(vc2.sstt_vencimientos_cursos_fecha_ven, CURDATE()) > 30
      )
      AND (
        vc.sstt_vencimientos_cursos_tipo_curso <> 'EXAMEN MEDICO INGRESO'
        OR NOT EXISTS (
          SELECT 1 FROM sstt_vencimientos_cursos vcP
          WHERE vcP.recurso_operativo_cedula = vc.recurso_operativo_cedula
            AND vcP.sstt_vencimientos_cursos_tipo_curso = 'EXAMEN MEDICO PERIODICO'
            AND vcP.sstt_vencimientos_cursos_fecha_ven IS NOT NULL
            AND vcP.sstt_vencimientos_cursos_fecha_ven NOT IN ('0000-00-00','1900-01-01')
            AND vcP.sstt_vencimientos_cursos_fecha_ven > '1900-01-01'
            AND (
              (
                DATE(vc.sstt_vencimientos_cursos_fecha_ven) <= CURDATE()
                AND DATEDIFF(vcP.sstt_vencimientos_cursos_fecha_ven, CURDATE()) > 30
              )
              OR (
                DATE(vc.sstt_vencimientos_cursos_fecha_ven) > CURDATE()
                AND DATEDIFF(vc.sstt_vencimientos_cursos_fecha_ven, CURDATE()) <= 30
                AND DATE(vcP.sstt_vencimientos_cursos_fecha_ven) >= CURDATE()
              )
            )
        )
      )
    ORDER BY ro.nombre ASC, vc.sstt_vencimientos_cursos_fecha_ven ASC
    """
    cur.execute(sql, (ced,))
    for r in cur.fetchall() or []:
        print(r['cedula'], '|', r['nombre'], '|', r['curso'], '|', r['vencimiento'])

    cur.close(); conn.close()

if __name__ == '__main__':
    main()
