#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la sincronización de datos para la placa IVS28F
"""

import mysql.connector
from datetime import datetime

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def verificar_estructura_tablas():
    """Verificar la estructura de las tablas MPA"""
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        print("=== ESTRUCTURA DE TABLAS MPA ===\n")
        
        tablas = ['mpa_vehiculos', 'mpa_soat', 'mpa_tecnico_mecanica']
        
        for tabla in tablas:
            print(f"Estructura de {tabla}:")
            print("-" * 50)
            cursor.execute(f"DESCRIBE {tabla}")
            columnas = cursor.fetchall()
            for columna in columnas:
                print(f"  {columna[0]} - {columna[1]} - {columna[2]} - {columna[3]}")
            print()
        
    except mysql.connector.Error as e:
        print(f"Error verificando estructura: {e}")
    finally:
        cursor.close()
        connection.close()

def verificar_datos_placa(placa):
    """Verificar datos en las tres tablas para una placa específica"""
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        print(f"=== VERIFICACIÓN DE DATOS PARA PLACA: {placa} ===\n")
        
        # 1. Verificar datos en mpa_vehiculos
        print("1. DATOS EN mpa_vehiculos:")
        print("-" * 50)
        query_vehiculos = """
        SELECT placa, tecnico_asignado, fecha_creacion, observaciones
        FROM mpa_vehiculos 
        WHERE placa = %s
        """
        cursor.execute(query_vehiculos, (placa,))
        vehiculo = cursor.fetchone()
        
        if vehiculo:
            print(f"Placa: {vehiculo['placa']}")
            print(f"Técnico Asignado: {vehiculo['tecnico_asignado']}")
            print(f"Fecha Creación: {vehiculo['fecha_creacion']}")
            print(f"Observaciones: {vehiculo['observaciones']}")
        else:
            print("No se encontró el vehículo en mpa_vehiculos")
            return
        
        print("\n" + "="*60 + "\n")
        
        # 2. Verificar datos en mpa_soat
        print("2. DATOS EN mpa_soat:")
        print("-" * 50)
        query_soat = """
        SELECT placa, tecnico_asignado, fecha_vencimiento, fecha_actualizacion, observaciones
        FROM mpa_soat 
        WHERE placa = %s
        ORDER BY fecha_actualizacion DESC
        """
        cursor.execute(query_soat, (placa,))
        soats = cursor.fetchall()
        
        if soats:
            for i, soat in enumerate(soats, 1):
                print(f"Registro {i}:")
                print(f"  Placa: {soat['placa']}")
                print(f"  Técnico Asignado: {soat['tecnico_asignado']}")
                print(f"  Fecha Vencimiento: {soat['fecha_vencimiento']}")
                print(f"  Fecha Actualización: {soat['fecha_actualizacion']}")
                print(f"  Observaciones: {soat['observaciones']}")
                print()
        else:
            print("No se encontraron registros SOAT para esta placa")
        
        print("="*60 + "\n")
        
        # 3. Verificar datos en mpa_tecnico_mecanica
        print("3. DATOS EN mpa_tecnico_mecanica:")
        print("-" * 50)
        query_tecnico = """
        SELECT placa, tecnico_asignado, fecha_vencimiento, fecha_actualizacion, observaciones
        FROM mpa_tecnico_mecanica 
        WHERE placa = %s
        ORDER BY fecha_actualizacion DESC
        """
        cursor.execute(query_tecnico, (placa,))
        tecnicos = cursor.fetchall()
        
        if tecnicos:
            for i, tecnico in enumerate(tecnicos, 1):
                print(f"Registro {i}:")
                print(f"  Placa: {tecnico['placa']}")
                print(f"  Técnico Asignado: {tecnico['tecnico_asignado']}")
                print(f"  Fecha Vencimiento: {tecnico['fecha_vencimiento']}")
                print(f"  Fecha Actualización: {tecnico['fecha_actualizacion']}")
                print(f"  Observaciones: {tecnico['observaciones']}")
                print()
        else:
            print("No se encontraron registros de Tecnomecánica para esta placa")
        
        print("="*60 + "\n")
        
        # 4. Análisis de sincronización
        print("4. ANÁLISIS DE SINCRONIZACIÓN:")
        print("-" * 50)
        
        if vehiculo:
            tecnico_vehiculo = vehiculo['tecnico_asignado']
            print(f"Técnico en vehículo: {tecnico_vehiculo}")
            
            # Verificar SOAT
            if soats:
                tecnico_soat = soats[0]['tecnico_asignado']  # Más reciente
                print(f"Técnico en SOAT (más reciente): {tecnico_soat}")
                if str(tecnico_vehiculo) == str(tecnico_soat):
                    print("✅ SOAT está sincronizado")
                else:
                    print("❌ SOAT NO está sincronizado")
            else:
                print("⚠️  No hay registros SOAT para comparar")
            
            # Verificar Tecnomecánica
            if tecnicos:
                tecnico_tm = tecnicos[0]['tecnico_asignado']  # Más reciente
                print(f"Técnico en Tecnomecánica (más reciente): {tecnico_tm}")
                if str(tecnico_vehiculo) == str(tecnico_tm):
                    print("✅ Tecnomecánica está sincronizada")
                else:
                    print("❌ Tecnomecánica NO está sincronizada")
            else:
                print("⚠️  No hay registros de Tecnomecánica para comparar")
        
    except mysql.connector.Error as e:
        print(f"Error ejecutando consultas: {e}")
    finally:
        cursor.close()
        connection.close()

def verificar_procedimiento_sincronizacion():
    """Verificar si existe el procedimiento almacenado de sincronización"""
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        print("\n" + "="*60)
        print("VERIFICACIÓN DE PROCEDIMIENTOS ALMACENADOS")
        print("="*60)
        
        # Buscar procedimientos relacionados con sincronización
        query = """
        SELECT ROUTINE_NAME, ROUTINE_TYPE, CREATED, LAST_ALTERED
        FROM information_schema.ROUTINES 
        WHERE ROUTINE_SCHEMA = 'capired' 
        AND ROUTINE_NAME LIKE '%sincroniz%'
        """
        cursor.execute(query)
        procedimientos = cursor.fetchall()
        
        if procedimientos:
            print("Procedimientos de sincronización encontrados:")
            for proc in procedimientos:
                print(f"- {proc[0]} ({proc[1]}) - Creado: {proc[2]}, Modificado: {proc[3]}")
        else:
            print("❌ No se encontraron procedimientos de sincronización")
        
        # Buscar específicamente sp_sincronizar_vehiculo_automatico
        query_especifico = """
        SELECT ROUTINE_NAME, ROUTINE_DEFINITION
        FROM information_schema.ROUTINES 
        WHERE ROUTINE_SCHEMA = 'capired' 
        AND ROUTINE_NAME = 'sp_sincronizar_vehiculo_automatico'
        """
        cursor.execute(query_especifico)
        proc_especifico = cursor.fetchone()
        
        if proc_especifico:
            print(f"\n✅ Procedimiento sp_sincronizar_vehiculo_automatico encontrado")
        else:
            print(f"\n❌ Procedimiento sp_sincronizar_vehiculo_automatico NO encontrado")
        
    except mysql.connector.Error as e:
        print(f"Error verificando procedimientos: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    # Primero verificar estructura de tablas
    verificar_estructura_tablas()
    
    # Verificar datos para la placa IVS28F
    verificar_datos_placa("IVS28F")
    
    # Verificar procedimientos de sincronización
    verificar_procedimiento_sincronizacion()