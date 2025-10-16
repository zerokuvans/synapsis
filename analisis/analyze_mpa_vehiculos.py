#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analizar la estructura de la tabla mpa_vehiculos
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def analyze_mpa_vehiculos_table():
    """Analiza la estructura de la tabla mpa_vehiculos"""
    try:
        # Configuración de conexión a la base de datos (usando las mismas credenciales que app.py)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("=" * 60)
            print("ANÁLISIS DE LA TABLA mpa_vehiculos")
            print("=" * 60)
            
            # Verificar si la tabla existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'capired' 
                AND table_name = 'mpa_vehiculos'
            """)
            
            table_exists = cursor.fetchone()[0]
            
            if table_exists == 0:
                print("❌ La tabla 'mpa_vehiculos' NO EXISTE en la base de datos 'capired'")
                print("\n📋 ESTRUCTURA REQUERIDA SEGÚN ESPECIFICACIONES:")
                print("-" * 50)
                required_fields = [
                    "id_mpa_vehiculos (INT, AUTO_INCREMENT, PRIMARY KEY)",
                    "cedula_propietario (VARCHAR)",
                    "nombre_propietario (VARCHAR)",
                    "placa (VARCHAR, UNIQUE)",
                    "tipo_vehiculo (ENUM: 'Moto', 'Camioneta', 'Camión')",
                    "vin (VARCHAR, UNIQUE)",
                    "numero_motor (VARCHAR)",
                    "fecha_matricula (DATE)",
                    "estado (ENUM: 'Activo', 'Inactivo')",
                    "linea (VARCHAR)",
                    "modelo (VARCHAR)",
                    "color (VARCHAR)",
                    "kilometraje_actual (INT)",
                    "fecha_creacion (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)",
                    "tecnico_asignado (INT, FK a recursos_operativo)",
                    "observaciones (TEXT)"
                ]
                
                for field in required_fields:
                    print(f"  • {field}")
                
                print("\n🔧 RECOMENDACIÓN: Crear la tabla con la estructura especificada")
                return False
            
            print("✅ La tabla 'mpa_vehiculos' EXISTE en la base de datos")
            
            # Obtener estructura de la tabla
            cursor.execute("DESCRIBE mpa_vehiculos")
            columns = cursor.fetchall()
            
            print("\n📋 ESTRUCTURA ACTUAL DE LA TABLA:")
            print("-" * 50)
            print(f"{'Campo':<25} {'Tipo':<20} {'Null':<8} {'Key':<8} {'Default':<15} {'Extra'}")
            print("-" * 90)
            
            for column in columns:
                field, type_info, null, key, default, extra = column
                default_str = str(default) if default is not None else 'NULL'
                print(f"{field:<25} {type_info:<20} {null:<8} {key:<8} {default_str:<15} {extra}")
            
            # Obtener índices
            cursor.execute("SHOW INDEX FROM mpa_vehiculos")
            indexes = cursor.fetchall()
            
            if indexes:
                print("\n🔑 ÍNDICES DE LA TABLA:")
                print("-" * 30)
                for index in indexes:
                    print(f"  • {index[2]} ({index[4]})")
            
            # Verificar datos existentes
            cursor.execute("SELECT COUNT(*) FROM mpa_vehiculos")
            record_count = cursor.fetchone()[0]
            
            print(f"\n📊 REGISTROS EXISTENTES: {record_count}")
            
            if record_count > 0:
                # Mostrar algunos registros de ejemplo
                cursor.execute("SELECT * FROM mpa_vehiculos LIMIT 3")
                sample_records = cursor.fetchall()
                
                print("\n📝 REGISTROS DE EJEMPLO:")
                print("-" * 40)
                for i, record in enumerate(sample_records, 1):
                    print(f"Registro {i}: {record}")
            
            # Verificar relación con recursos_operativo
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'capired' 
                AND table_name = 'recursos_operativo'
            """)
            
            recursos_exists = cursor.fetchone()[0]
            
            if recursos_exists > 0:
                cursor.execute("SELECT COUNT(*) FROM recursos_operativo")
                tecnicos_count = cursor.fetchone()[0]
                print(f"\n👥 TÉCNICOS DISPONIBLES EN recursos_operativo: {tecnicos_count}")
                
                # Mostrar algunos técnicos de ejemplo
                cursor.execute("SELECT id, nombre, cedula FROM recursos_operativo LIMIT 5")
                tecnicos = cursor.fetchall()
                
                print("\n👨‍🔧 TÉCNICOS DE EJEMPLO:")
                print("-" * 30)
                for tecnico in tecnicos:
                    print(f"  • ID: {tecnico[0]}, Nombre: {tecnico[1]}, Cédula: {tecnico[2]}")
            else:
                print("\n❌ La tabla 'recursos_operativo' NO EXISTE")
            
            print("\n" + "=" * 60)
            print("ANÁLISIS COMPLETADO")
            print("=" * 60)
            
            return True
            
    except Error as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        return False
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    analyze_mpa_vehiculos_table()