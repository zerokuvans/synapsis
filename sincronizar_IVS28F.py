#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para ejecutar sincronización manual de la placa IVS28F
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

def ejecutar_sincronizacion_manual(placa):
    """Ejecutar sincronización manual para una placa específica"""
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        print(f"=== SINCRONIZACIÓN MANUAL PARA PLACA: {placa} ===\n")
        
        # 1. Obtener el técnico asignado del vehículo
        print("1. Obteniendo técnico asignado del vehículo...")
        query_vehiculo = "SELECT tecnico_asignado FROM mpa_vehiculos WHERE placa = %s"
        cursor.execute(query_vehiculo, (placa,))
        resultado = cursor.fetchone()
        
        if not resultado:
            print(f"❌ No se encontró el vehículo con placa {placa}")
            return
        
        tecnico_asignado = resultado[0]
        print(f"✅ Técnico asignado en vehículo: {tecnico_asignado}")
        
        # 2. Actualizar registros de Tecnomecánica
        print("\n2. Actualizando registros de Tecnomecánica...")
        query_update_tm = """
        UPDATE mpa_tecnico_mecanica 
        SET tecnico_asignado = %s, fecha_actualizacion = NOW()
        WHERE placa = %s
        """
        cursor.execute(query_update_tm, (tecnico_asignado, placa))
        filas_tm = cursor.rowcount
        print(f"✅ Actualizados {filas_tm} registros de Tecnomecánica")
        
        # 3. Actualizar registros de SOAT (si existen)
        print("\n3. Actualizando registros de SOAT...")
        query_update_soat = """
        UPDATE mpa_soat 
        SET tecnico_asignado = %s, fecha_actualizacion = NOW()
        WHERE placa = %s
        """
        cursor.execute(query_update_soat, (tecnico_asignado, placa))
        filas_soat = cursor.rowcount
        
        if filas_soat > 0:
            print(f"✅ Actualizados {filas_soat} registros de SOAT")
        else:
            print("⚠️  No se encontraron registros SOAT para actualizar")
        
        # 4. Confirmar cambios
        connection.commit()
        print(f"\n✅ Sincronización completada para la placa {placa}")
        
        # 5. Verificar resultados
        print("\n=== VERIFICACIÓN POST-SINCRONIZACIÓN ===")
        
        # Verificar Tecnomecánica
        query_verify_tm = """
        SELECT tecnico_asignado, fecha_actualizacion 
        FROM mpa_tecnico_mecanica 
        WHERE placa = %s
        """
        cursor.execute(query_verify_tm, (placa,))
        tm_result = cursor.fetchone()
        
        if tm_result:
            print(f"Tecnomecánica - Técnico: {tm_result[0]}, Actualizado: {tm_result[1]}")
        
        # Verificar SOAT
        query_verify_soat = """
        SELECT tecnico_asignado, fecha_actualizacion 
        FROM mpa_soat 
        WHERE placa = %s
        """
        cursor.execute(query_verify_soat, (placa,))
        soat_result = cursor.fetchone()
        
        if soat_result:
            print(f"SOAT - Técnico: {soat_result[0]}, Actualizado: {soat_result[1]}")
        else:
            print("SOAT - No hay registros")
        
    except mysql.connector.Error as e:
        print(f"❌ Error ejecutando sincronización: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def verificar_procedimiento_completo():
    """Verificar el contenido del procedimiento sp_sincronizar_vehiculo_completo"""
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        print("\n=== VERIFICACIÓN DEL PROCEDIMIENTO EXISTENTE ===")
        
        query = """
        SELECT ROUTINE_DEFINITION
        FROM information_schema.ROUTINES 
        WHERE ROUTINE_SCHEMA = 'capired' 
        AND ROUTINE_NAME = 'sp_sincronizar_vehiculo_completo'
        """
        cursor.execute(query)
        resultado = cursor.fetchone()
        
        if resultado:
            print("✅ Procedimiento sp_sincronizar_vehiculo_completo encontrado")
            print("Definición del procedimiento:")
            print("-" * 50)
            print(resultado[0][:500] + "..." if len(resultado[0]) > 500 else resultado[0])
        else:
            print("❌ Procedimiento no encontrado")
        
    except mysql.connector.Error as e:
        print(f"Error verificando procedimiento: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    # Verificar procedimiento existente
    verificar_procedimiento_completo()
    
    # Ejecutar sincronización manual para IVS28F
    ejecutar_sincronizacion_manual("IVS28F")