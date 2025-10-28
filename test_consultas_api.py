#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar las consultas exactas que usa la API de vencimientos
"""

import mysql.connector
from datetime import datetime, date
import pytz
import re

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            sql_mode=''
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def validar_fecha(fecha_str):
    """Valida que una fecha tenga el formato YYYY-MM-DD y sea válida"""
    if not fecha_str or fecha_str == '0000-00-00':
        return False, None, 'Sin fecha'
        
    # Validar formato YYYY-MM-DD
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', fecha_str):
        return False, None, 'Fecha inválida'
        
    try:
        # Convertir a fecha y validar
        year, month, day = map(int, fecha_str.split('-'))
        fecha = date(year, month, day)
        
        # Validar que los componentes coincidan (para detectar fechas inválidas como 2024-02-31)
        if fecha.year != year or fecha.month != month or fecha.day != day:
            return False, None, 'Fecha inválida'
            
        return True, fecha, None
    except ValueError:
        return False, None, 'Fecha inválida'

def main():
    print("=== Probando consultas exactas de la API ===\n")
    
    connection = get_db_connection()
    if not connection:
        print("No se pudo conectar a la base de datos")
        return
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        vencimientos_consolidados = []
        
        # 1. Consulta SOAT (exacta del código)
        print("1. Ejecutando consulta SOAT...")
        query_soat = """
        SELECT 
            s.id_mpa_soat as id,
            s.placa,
            s.fecha_vencimiento,
            s.tecnico_asignado,
            ro.nombre as tecnico_nombre,
            'SOAT' as tipo,
            s.estado
        FROM mpa_soat s
        LEFT JOIN recurso_operativo ro ON s.tecnico_asignado = ro.id_codigo_consumidor
        WHERE s.fecha_vencimiento IS NOT NULL
          AND s.fecha_vencimiento NOT LIKE '0000-00-00%'
          AND s.fecha_vencimiento > '1900-01-01'
          AND (
              s.tecnico_asignado IS NULL
              OR TRIM(s.tecnico_asignado) = ''
              OR ro.estado = 'Activo'
          )
        ORDER BY s.fecha_vencimiento ASC
        """
        
        cursor.execute(query_soat)
        soats = cursor.fetchall()
        print(f"   SOAT encontrados: {len(soats)}")
        
        for soat in soats:
            vencimientos_consolidados.append({
                'id': soat['id'],
                'tipo': 'SOAT',
                'placa': soat['placa'],
                'fecha_vencimiento': soat['fecha_vencimiento'].strftime('%Y-%m-%d') if soat['fecha_vencimiento'] else None,
                'tecnico_nombre': soat['tecnico_nombre'] or 'Sin asignar',
                'estado_original': soat['estado']
            })
        
        # 2. Consulta Técnico Mecánica (exacta del código)
        print("2. Ejecutando consulta Técnico Mecánica...")
        query_tm = """
        SELECT 
            tm.id_mpa_tecnico_mecanica as id,
            tm.placa,
            tm.fecha_vencimiento,
            tm.tecnico_asignado,
            ro.nombre as tecnico_nombre,
            'Técnico Mecánica' as tipo,
            tm.estado
        FROM mpa_tecnico_mecanica tm
        LEFT JOIN recurso_operativo ro ON tm.tecnico_asignado = ro.id_codigo_consumidor
        WHERE tm.fecha_vencimiento IS NOT NULL
          AND tm.fecha_vencimiento NOT LIKE '0000-00-00%'
          AND tm.fecha_vencimiento > '1900-01-01'
          AND (
              tm.tecnico_asignado IS NULL
              OR TRIM(tm.tecnico_asignado) = ''
              OR ro.estado = 'Activo'
          )
        ORDER BY tm.fecha_vencimiento ASC
        """
        
        cursor.execute(query_tm)
        tecnicos = cursor.fetchall()
        print(f"   Técnico Mecánica encontrados: {len(tecnicos)}")
        
        for tm in tecnicos:
            vencimientos_consolidados.append({
                'id': tm['id'],
                'tipo': 'Técnico Mecánica',
                'placa': tm['placa'],
                'fecha_vencimiento': tm['fecha_vencimiento'].strftime('%Y-%m-%d') if tm['fecha_vencimiento'] else None,
                'tecnico_nombre': tm['tecnico_nombre'] or 'Sin asignar',
                'estado_original': tm['estado']
            })
        
        # 3. Consulta Licencias (exacta del código)
        print("3. Ejecutando consulta Licencias...")
        query_lc = """
        SELECT 
            lc.id_mpa_licencia_conducir as id,
            lc.fecha_vencimiento,
            lc.tecnico,
            ro.nombre as tecnico_nombre,
            'Licencia de Conducir' as tipo
        FROM mpa_licencia_conducir lc
        LEFT JOIN recurso_operativo ro ON lc.tecnico = ro.id_codigo_consumidor
        WHERE lc.fecha_vencimiento IS NOT NULL
          AND lc.fecha_vencimiento NOT LIKE '0000-00-00%'
          AND lc.fecha_vencimiento > '1900-01-01'
          AND (
              lc.tecnico IS NULL
              OR TRIM(lc.tecnico) = ''
              OR ro.estado = 'Activo'
          )
        ORDER BY lc.fecha_vencimiento ASC
        """
        
        cursor.execute(query_lc)
        licencias = cursor.fetchall()
        print(f"   Licencias encontradas: {len(licencias)}")
        
        for lc in licencias:
            vencimientos_consolidados.append({
                'id': lc['id'],
                'tipo': 'Licencia de Conducir',
                'placa': None,  # Las licencias no tienen placa
                'fecha_vencimiento': lc['fecha_vencimiento'].strftime('%Y-%m-%d') if lc['fecha_vencimiento'] else None,
                'tecnico_nombre': lc['tecnico_nombre'] or 'Sin asignar',
                'estado_original': None  # Las licencias no tienen campo estado
            })
        
        print(f"\n4. Total antes de validación de fechas: {len(vencimientos_consolidados)}")
        
        # 4. Calcular días restantes y estado (exacto del código)
        colombia_tz = pytz.timezone('America/Bogota')
        fecha_actual = datetime.now(colombia_tz).date()
        
        vencimientos_validos = []
        vencimientos_invalidos = 0
        
        for vencimiento in vencimientos_consolidados:
            try:
                fecha_str = vencimiento['fecha_vencimiento']
                es_valida, fecha_venc, estado_error = validar_fecha(fecha_str)
                
                if not es_valida:
                    vencimiento['dias_restantes'] = None
                    vencimiento['estado'] = estado_error
                    vencimientos_invalidos += 1
                    continue
                
                # Calcular días restantes
                dias_restantes = (fecha_venc - fecha_actual).days
                vencimiento['dias_restantes'] = dias_restantes
                
                # Determinar estado basado en días restantes
                if dias_restantes < 0:
                    vencimiento['estado'] = 'Vencido'
                elif dias_restantes <= 30:
                    vencimiento['estado'] = 'Próximo a vencer'
                else:
                    vencimiento['estado'] = 'Vigente'
                
                vencimientos_validos.append(vencimiento)
                    
            except Exception as e:
                vencimiento['dias_restantes'] = None
                vencimiento['estado'] = 'Fecha inválida'
                vencimientos_invalidos += 1
                print(f"Error procesando fecha para vencimiento ID {vencimiento['id']}: {str(e)}")
        
        print(f"5. Vencimientos con fechas válidas: {len(vencimientos_validos)}")
        print(f"6. Vencimientos con fechas inválidas: {vencimientos_invalidos}")
        
        # 5. Ordenar por fecha de vencimiento (exacto del código)
        def get_sort_key(x):
            try:
                fecha_str = x['fecha_vencimiento']
                es_valida, fecha, _ = validar_fecha(fecha_str)
                if not es_valida:
                    return '9999-12-31'
                return fecha_str
            except Exception as e:
                print(f"Error al ordenar vencimiento ID {x['id']}: {str(e)}")
                return '9999-12-31'
        
        vencimientos_consolidados.sort(key=get_sort_key)
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"Total de vencimientos que devolvería la API: {len(vencimientos_consolidados)}")
        
        # Mostrar algunos ejemplos
        print(f"\nPrimeros 5 vencimientos:")
        for i, v in enumerate(vencimientos_consolidados[:5]):
            print(f"   {i+1}. {v['tipo']} - Placa: {v.get('placa', 'N/A')} - Fecha: {v['fecha_vencimiento']} - Estado: {v.get('estado', 'N/A')}")
        
        # Estadísticas por estado
        estados = {}
        for v in vencimientos_consolidados:
            estado = v.get('estado', 'Sin estado')
            estados[estado] = estados.get(estado, 0) + 1
        
        print(f"\nEstadísticas por estado:")
        for estado, cantidad in estados.items():
            print(f"   {estado}: {cantidad}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()