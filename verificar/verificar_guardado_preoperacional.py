#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from datetime import datetime, date
import sys

def get_db_connection():
    """Establecer conexión con la base de datos"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

def verificar_datos_preoperacionales():
    """Verificar si existen datos preoperacionales para el usuario"""
    connection = get_db_connection()
    if connection is None:
        return False
        
    try:
        cursor = connection.cursor(dictionary=True)
        
        print("\n1. Buscando registros del usuario 1032402333 (ID: 19)...")
        
        # Buscar registros del usuario específico
        cursor.execute("""
            SELECT id_preoperacional, fecha, centro_de_trabajo, supervisor, vehiculo_asistio_operacion
            FROM preoperacional 
            WHERE id_codigo_consumidor = %s 
            ORDER BY fecha DESC 
            LIMIT 5
        """, (19,))
        
        registros = cursor.fetchall()
        
        if registros:
            print(f"   ✓ Se encontraron {len(registros)} registros:")
            for i, registro in enumerate(registros, 1):
                print(f"   {i}. ID: {registro['id_preoperacional']}, Fecha: {registro['fecha']}, Centro: {registro['centro_de_trabajo']}")
        else:
            print("   ❌ No se encontraron registros para este usuario")
            
        # Buscar registros de hoy
        today = date.today()
        cursor.execute("""
            SELECT id_preoperacional, fecha, centro_de_trabajo, supervisor
            FROM preoperacional 
            WHERE id_codigo_consumidor = %s AND DATE(fecha) = %s
        """, (19, today))
        
        registros_hoy = cursor.fetchall()
        
        print(f"\n2. Registros de hoy ({today}):")
        if registros_hoy:
            print(f"   ✓ Se encontraron {len(registros_hoy)} registros de hoy")
            for registro in registros_hoy:
                print(f"   - ID: {registro['id_preoperacional']}, Fecha: {registro['fecha']}")
        else:
            print("   ❌ No hay registros de hoy")
            
        return len(registros) > 0
        
    except mysql.connector.Error as e:
        print(f"Error en la consulta: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def verificar_usuario():
    """Verificar información del usuario"""
    print("\n=== VERIFICACIÓN DE USUARIO ===")
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Verificar datos del usuario
        query = """
        SELECT 
            id_codigo_consumidor,
            recurso_operativo_cedula,
            nombre,
            id_roles,
            estado
        FROM recurso_operativo 
        WHERE recurso_operativo_cedula = '1032402333'
        """
        
        cursor.execute(query)
        usuario = cursor.fetchone()
        
        if usuario:
            print(f"   ✓ Usuario encontrado:")
            print(f"   ID: {usuario['id_codigo_consumidor']}")
            print(f"   Cédula: {usuario['recurso_operativo_cedula']}")
            print(f"   Nombre: {usuario['nombre']}")
            print(f"   Rol ID: {usuario['id_roles']}")
            print(f"   Estado: {usuario['estado']}")
            return True
        else:
            print("   ❌ Usuario no encontrado")
            return False
            
    except mysql.connector.Error as e:
        print(f"Error en la consulta: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    print("Iniciando verificación...")
    
    # Verificar usuario
    usuario_ok = verificar_usuario()
    
    # Verificar datos preoperacionales
    datos_ok = verificar_datos_preoperacionales()
    
    print("\n=== RESUMEN ===")
    if usuario_ok and datos_ok:
        print("✓ Verificación completada exitosamente")
        print("✓ El usuario existe y tiene registros preoperacionales")
    else:
        print("❌ Se encontraron problemas en la verificación")
        if not usuario_ok:
            print("   - Problema con el usuario")
        if not datos_ok:
            print("   - Problema con los datos preoperacionales")