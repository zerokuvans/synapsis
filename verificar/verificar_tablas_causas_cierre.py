#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la existencia y estructura de las tablas relacionadas con causas de cierre
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
    'database': os.getenv('MYSQL_DB', 'capired'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

def verificar_tabla_existe(cursor, nombre_tabla):
    """Verificar si una tabla existe en la base de datos"""
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = %s AND table_name = %s
    """, (db_config['database'], nombre_tabla))
    return cursor.fetchone()[0] > 0

def mostrar_estructura_tabla(cursor, nombre_tabla):
    """Mostrar la estructura de una tabla"""
    print(f"\n=== Estructura de la tabla {nombre_tabla} ===")
    cursor.execute(f"DESCRIBE {nombre_tabla}")
    columnas = cursor.fetchall()
    
    print("Columnas:")
    for columna in columnas:
        print(f"  - {columna[0]} ({columna[1]}) - Key: {columna[3]} - Null: {columna[2]} - Default: {columna[4]}")
    
    # Mostrar algunos datos de ejemplo
    cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
    total_registros = cursor.fetchone()[0]
    print(f"\nTotal de registros: {total_registros}")
    
    if total_registros > 0:
        cursor.execute(f"SELECT * FROM {nombre_tabla} LIMIT 5")
        datos = cursor.fetchall()
        print("\nPrimeros 5 registros:")
        for i, registro in enumerate(datos, 1):
            print(f"  {i}. {registro}")

def crear_tablas_causas_cierre(cursor):
    """Crear las tablas según la documentación técnica"""
    print("\n=== Creando tablas de causas de cierre ===")
    
    # Crear tabla de tecnologías
    cursor.execute("""
        CREATE TABLE tecnologias_causas_cierre (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            estado ENUM('activo', 'inactivo') DEFAULT 'activo',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            INDEX idx_nombre (nombre),
            INDEX idx_estado (estado)
        )
    """)
    print("✓ Tabla tecnologias_causas_cierre creada")
    
    # Crear tabla de agrupaciones
    cursor.execute("""
        CREATE TABLE agrupaciones_causas_cierre (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            estado ENUM('activo', 'inactivo') DEFAULT 'activo',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            INDEX idx_nombre (nombre),
            INDEX idx_estado (estado)
        )
    """)
    print("✓ Tabla agrupaciones_causas_cierre creada")
    
    # Crear tabla de grupos
    cursor.execute("""
        CREATE TABLE todos_los_grupos_causas_cierre (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            estado ENUM('activo', 'inactivo') DEFAULT 'activo',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            INDEX idx_nombre (nombre),
            INDEX idx_estado (estado)
        )
    """)
    print("✓ Tabla todos_los_grupos_causas_cierre creada")
    
    # Crear tabla principal
    cursor.execute("""
        CREATE TABLE base_causas_cierre (
            id INT AUTO_INCREMENT PRIMARY KEY,
            codigo VARCHAR(50) UNIQUE NOT NULL,
            descripcion TEXT NOT NULL,
            tecnologia_id INT,
            agrupacion_id INT,
            grupo_id INT,
            estado ENUM('activo', 'inactivo') DEFAULT 'activo',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            
            INDEX idx_codigo (codigo),
            INDEX idx_tecnologia (tecnologia_id),
            INDEX idx_agrupacion (agrupacion_id),
            INDEX idx_grupo (grupo_id),
            INDEX idx_estado (estado),
            FULLTEXT INDEX idx_busqueda (codigo, descripcion),
            
            FOREIGN KEY (tecnologia_id) REFERENCES tecnologias_causas_cierre(id),
            FOREIGN KEY (agrupacion_id) REFERENCES agrupaciones_causas_cierre(id),
            FOREIGN KEY (grupo_id) REFERENCES todos_los_grupos_causas_cierre(id)
        )
    """)
    print("✓ Tabla base_causas_cierre creada")

def insertar_datos_iniciales(cursor):
    """Insertar datos iniciales de ejemplo"""
    print("\n=== Insertando datos iniciales ===")
    
    # Datos para tecnologías
    cursor.execute("""
        INSERT INTO tecnologias_causas_cierre (nombre, descripcion) VALUES
        ('PRIMERAS CLIENTE', 'Tecnología para primeras instalaciones de cliente'),
        ('OTROS TRABAJOS', 'Otras tecnologías de trabajo'),
        ('MANTENIMIENTO', 'Tecnologías de mantenimiento')
    """)
    print("✓ Datos de tecnologías insertados")
    
    # Datos para agrupaciones
    cursor.execute("""
        INSERT INTO agrupaciones_causas_cierre (nombre, descripcion) VALUES
        ('CSR', 'Customer Service Representative'),
        ('TECNICO', 'Agrupación técnica'),
        ('ADMINISTRATIVO', 'Agrupación administrativa')
    """)
    print("✓ Datos de agrupaciones insertados")
    
    # Datos para grupos
    cursor.execute("""
        INSERT INTO todos_los_grupos_causas_cierre (nombre, descripcion) VALUES
        ('OTROS TRABAJOS', 'Grupo de otros trabajos'),
        ('INSTALACIONES', 'Grupo de instalaciones'),
        ('REPARACIONES', 'Grupo de reparaciones')
    """)
    print("✓ Datos de grupos insertados")
    
    # Datos para la tabla principal
    cursor.execute("""
        INSERT INTO base_causas_cierre (codigo, descripcion, tecnologia_id, agrupacion_id, grupo_id) VALUES
        ('VTP', 'VISITA TECNICA PYMES', 1, 1, 1),
        ('VTC', 'VISITA TECNICA BIDI', 1, 1, 1),
        ('VER', 'VERIFICACIONES BIDI', 2, 2, 2),
        ('INS', 'INSTALACION NUEVA', 1, 2, 2),
        ('REP', 'REPARACION TECNICA', 2, 2, 3)
    """)
    print("✓ Datos de base_causas_cierre insertados")

def main():
    """Función principal"""
    try:
        print("=== VERIFICACIÓN DE TABLAS CAUSAS DE CIERRE ===")
        print(f"Conectando a la base de datos: {db_config['database']}")
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Lista de tablas a verificar
        tablas = [
            'base_causas_cierre',
            'tecnologias_causas_cierre',
            'agrupaciones_causas_cierre',
            'todos_los_grupos_causas_cierre'
        ]
        
        tablas_existentes = []
        tablas_faltantes = []
        
        # Verificar existencia de cada tabla
        for tabla in tablas:
            if verificar_tabla_existe(cursor, tabla):
                print(f"✓ Tabla {tabla} existe")
                tablas_existentes.append(tabla)
            else:
                print(f"✗ Tabla {tabla} NO existe")
                tablas_faltantes.append(tabla)
        
        # Mostrar estructura de tablas existentes
        for tabla in tablas_existentes:
            mostrar_estructura_tabla(cursor, tabla)
        
        # Crear tablas faltantes si es necesario
        if tablas_faltantes:
            respuesta = input(f"\n¿Desea crear las tablas faltantes? ({len(tablas_faltantes)} tablas) [s/N]: ")
            if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
                crear_tablas_causas_cierre(cursor)
                insertar_datos_iniciales(cursor)
                connection.commit()
                print("\n✓ Todas las tablas han sido creadas exitosamente")
                
                # Mostrar estructura de las nuevas tablas
                for tabla in tablas:
                    mostrar_estructura_tabla(cursor, tabla)
        else:
            print("\n✓ Todas las tablas ya existen en la base de datos")
        
    except Error as e:
        print(f"Error de MySQL: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    main()