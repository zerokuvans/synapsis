#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar los datos del endpoint /api/turnos-semana con la corrección
"""

import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
}

def main():
    """Verificar datos de turnos de la semana actual con la nueva consulta"""
    print("=== VERIFICACIÓN DE DATOS DE TURNOS SEMANA (CORREGIDA) ===")
    
    # Calcular fechas de la semana actual
    today = datetime.now()
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)
    sunday = monday + timedelta(days=6)
    
    fecha_inicio = monday.strftime('%Y-%m-%d')
    fecha_fin = sunday.strftime('%Y-%m-%d')
    
    print(f"Consultando turnos entre {fecha_inicio} y {fecha_fin}")
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Consulta corregida igual que en el endpoint
        cursor.execute("""
            SELECT 
                atb.analistas_turnos_fecha,
                COALESCE(ro.nombre, atb.analistas_turnos_analista) as analistas_turnos_analista,
                atb.analistas_turnos_turno,
                atb.analistas_turnos_almuerzo,
                atb.analistas_turnos_break,
                atb.analistas_turnos_horas_trabajadas
            FROM analistas_turnos_base atb
            LEFT JOIN recurso_operativo ro ON atb.analistas_turnos_analista = ro.id_codigo_consumidor
            WHERE atb.analistas_turnos_fecha BETWEEN %s AND %s
            ORDER BY atb.analistas_turnos_fecha, ro.nombre
        """, (fecha_inicio, fecha_fin))
        
        turnos = cursor.fetchall()
        
        print(f"\nRegistros encontrados: {len(turnos)}")
        
        if turnos:
            print("\nPrimeros 5 registros:")
            for i, turno in enumerate(turnos[:5]):
                print(f"{i+1}. Fecha: {turno['analistas_turnos_fecha']}")
                print(f"   Analista: {turno['analistas_turnos_analista']}")
                print(f"   Turno: {turno['analistas_turnos_turno']}")
                print(f"   Almuerzo: {turno['analistas_turnos_almuerzo']}")
                print(f"   Break: {turno['analistas_turnos_break']}")
                print(f"   Horas: {turno['analistas_turnos_horas_trabajadas']}")
                print()
        else:
            print("\n❌ No se encontraron registros para esta semana")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    main()