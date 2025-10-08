#!/usr/bin/env python3
"""
Script para debuggear la consulta SQL corregida del endpoint de asistencia
"""

import mysql.connector
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """Obtiene conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'capired'),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error conectando a la base de datos: {err}")
        return None

def test_consulta_corregida():
    """Prueba la consulta SQL corregida"""
    
    # Parámetros de prueba
    supervisor_actual = 'SILVA CASTRO DANIEL ALBERTO'
    fecha_consulta = date(2025, 10, 8)
    
    print(f"🔍 Probando consulta corregida para:")
    print(f"   Supervisor: {supervisor_actual}")
    print(f"   Fecha: {fecha_consulta}")
    print("=" * 80)
    
    connection = get_db_connection()
    if connection is None:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    # Consulta corregida (la misma del endpoint)
    consulta = """
        SELECT 
            a.cedula,
            a.tecnico,
            a.carpeta,
            a.super,
            a.carpeta_dia,
            COALESCE(t.nombre_tipificacion, '') AS carpeta_dia_nombre,
            a.eventos AS eventos,
            COALESCE(pc.presupuesto_eventos, 0) AS ok_eventos,
            COALESCE(pc.presupuesto_diario, 0) AS presupuesto_diario,
            a.valor,
            a.estado,
            a.novedad,
            a.id_asistencia,
            a.fecha_asistencia
        FROM asistencia a
        LEFT JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
        LEFT JOIN presupuesto_carpeta pc ON t.nombre_tipificacion = pc.presupuesto_carpeta
        WHERE a.super = %s AND DATE(a.fecha_asistencia) = %s
        AND a.id_asistencia = (
            SELECT MAX(a2.id_asistencia)
            FROM asistencia a2
            WHERE a2.cedula = a.cedula 
            AND a2.super = %s 
            AND DATE(a2.fecha_asistencia) = %s
        )
        ORDER BY a.tecnico
    """
    
    try:
        print("📊 Ejecutando consulta corregida...")
        cursor.execute(consulta, (supervisor_actual, fecha_consulta, supervisor_actual, fecha_consulta))
        registros = cursor.fetchall()
        
        print(f"✅ Consulta ejecutada exitosamente")
        print(f"📋 Total de registros devueltos: {len(registros)}")
        print()
        
        # Verificar duplicados por cédula
        cedulas_vistas = {}
        duplicados = []
        
        for i, registro in enumerate(registros, 1):
            cedula = registro['cedula']
            tecnico = registro['tecnico']
            id_asistencia = registro['id_asistencia']
            fecha_asistencia = registro['fecha_asistencia']
            
            if cedula in cedulas_vistas:
                duplicados.append({
                    'cedula': cedula,
                    'tecnico': tecnico,
                    'primera_aparicion': cedulas_vistas[cedula],
                    'segunda_aparicion': i,
                    'id_asistencia': id_asistencia
                })
                print(f"🔴 DUPLICADO #{len(duplicados)}: {cedula} - {tecnico}")
                print(f"   Primera aparición: fila {cedulas_vistas[cedula]}")
                print(f"   Segunda aparición: fila {i}")
                print(f"   ID asistencia: {id_asistencia}")
                print()
            else:
                cedulas_vistas[cedula] = i
                print(f"✅ Fila {i:2d}: {cedula} - {tecnico} (ID: {id_asistencia})")
        
        print("=" * 80)
        print(f"📊 RESUMEN:")
        print(f"   Total registros: {len(registros)}")
        print(f"   Técnicos únicos: {len(cedulas_vistas)}")
        print(f"   Duplicados encontrados: {len(duplicados)}")
        
        if duplicados:
            print(f"🔴 ¡PROBLEMA! Aún hay {len(duplicados)} duplicados")
            print("   La subconsulta no está funcionando correctamente")
        else:
            print("✅ ¡PERFECTO! No hay duplicados")
            
    except mysql.connector.Error as err:
        print(f"❌ Error ejecutando consulta: {err}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    test_consulta_corregida()