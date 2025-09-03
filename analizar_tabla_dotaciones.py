#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de análisis para la tabla 'dotaciones' en la base de datos capired
Este script analiza la estructura, relaciones y datos de la tabla dotaciones
para diseñar correctamente el módulo de gestión de dotaciones.
"""

import mysql.connector
import json
from datetime import datetime
import sys

class AnalizadorDotaciones:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '732137A031E4b@',
            'database': 'capired',
            'charset': 'utf8mb4'
        }
        self.conexion = None
        self.cursor = None
        
    def conectar(self):
        """Establece conexión con la base de datos"""
        try:
            self.conexion = mysql.connector.connect(**self.config)
            self.cursor = self.conexion.cursor(dictionary=True)
            print("✓ Conexión exitosa a la base de datos capired")
            return True
        except mysql.connector.Error as e:
            print(f"✗ Error de conexión: {e}")
            return False
    
    def analizar_estructura_tabla(self):
        """Analiza la estructura completa de la tabla dotaciones"""
        print("\n=== ANÁLISIS DE ESTRUCTURA DE LA TABLA 'dotaciones' ===")
        
        try:
            # Verificar si la tabla existe
            self.cursor.execute("""
                SELECT COUNT(*) as existe 
                FROM information_schema.tables 
                WHERE table_schema = 'capired' AND table_name = 'dotaciones'
            """)
            
            resultado = self.cursor.fetchone()
            if resultado['existe'] == 0:
                print("✗ La tabla 'dotaciones' no existe en la base de datos")
                return False
            
            print("✓ La tabla 'dotaciones' existe")
            
            # Obtener estructura de columnas
            self.cursor.execute("""
                SELECT 
                    COLUMN_NAME as campo,
                    DATA_TYPE as tipo,
                    IS_NULLABLE as nulo,
                    COLUMN_DEFAULT as valor_defecto,
                    CHARACTER_MAXIMUM_LENGTH as longitud_max,
                    NUMERIC_PRECISION as precision_numerica,
                    COLUMN_KEY as clave,
                    EXTRA as extra,
                    COLUMN_COMMENT as comentario
                FROM information_schema.COLUMNS 
                WHERE table_schema = 'capired' AND table_name = 'dotaciones'
                ORDER BY ORDINAL_POSITION
            """)
            
            columnas = self.cursor.fetchall()
            
            print(f"\n📋 ESTRUCTURA DE COLUMNAS ({len(columnas)} campos):")
            print("-" * 100)
            print(f"{'Campo':<20} {'Tipo':<15} {'Nulo':<5} {'Clave':<8} {'Extra':<15} {'Comentario':<20}")
            print("-" * 100)
            
            for col in columnas:
                tipo_completo = col['tipo']
                if col['longitud_max']:
                    tipo_completo += f"({col['longitud_max']})"
                elif col['precision_numerica']:
                    tipo_completo += f"({col['precision_numerica']})"
                
                print(f"{col['campo']:<20} {tipo_completo:<15} {col['nulo']:<5} {col['clave']:<8} {col['extra']:<15} {col['comentario'] or '':<20}")
            
            return columnas
            
        except mysql.connector.Error as e:
            print(f"✗ Error al analizar estructura: {e}")
            return False
    
    def analizar_indices_claves(self):
        """Analiza índices y claves de la tabla"""
        print("\n=== ANÁLISIS DE ÍNDICES Y CLAVES ===")
        
        try:
            # Obtener información de índices
            self.cursor.execute("""
                SELECT 
                    INDEX_NAME as nombre_indice,
                    COLUMN_NAME as columna,
                    NON_UNIQUE as no_unico,
                    INDEX_TYPE as tipo_indice,
                    SEQ_IN_INDEX as secuencia
                FROM information_schema.STATISTICS 
                WHERE table_schema = 'capired' AND table_name = 'dotaciones'
                ORDER BY INDEX_NAME, SEQ_IN_INDEX
            """)
            
            indices = self.cursor.fetchall()
            
            if indices:
                print(f"\n🔑 ÍNDICES ENCONTRADOS ({len(indices)} registros):")
                print("-" * 80)
                print(f"{'Índice':<20} {'Columna':<20} {'Único':<8} {'Tipo':<15}")
                print("-" * 80)
                
                for idx in indices:
                    unico = "Sí" if idx['no_unico'] == 0 else "No"
                    print(f"{idx['nombre_indice']:<20} {idx['columna']:<20} {unico:<8} {idx['tipo_indice']:<15}")
            else:
                print("ℹ️ No se encontraron índices específicos")
                
        except mysql.connector.Error as e:
            print(f"✗ Error al analizar índices: {e}")
    
    def analizar_relaciones(self):
        """Analiza relaciones con otras tablas"""
        print("\n=== ANÁLISIS DE RELACIONES CON OTRAS TABLAS ===")
        
        try:
            # Buscar claves foráneas
            self.cursor.execute("""
                SELECT 
                    CONSTRAINT_NAME as nombre_restriccion,
                    COLUMN_NAME as columna_local,
                    REFERENCED_TABLE_NAME as tabla_referenciada,
                    REFERENCED_COLUMN_NAME as columna_referenciada
                FROM information_schema.KEY_COLUMN_USAGE 
                WHERE table_schema = 'capired' 
                AND table_name = 'dotaciones' 
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            
            relaciones = self.cursor.fetchall()
            
            if relaciones:
                print(f"\n🔗 RELACIONES ENCONTRADAS ({len(relaciones)}):")
                print("-" * 80)
                print(f"{'Columna Local':<20} {'Tabla Referenciada':<20} {'Columna Referenciada':<20}")
                print("-" * 80)
                
                for rel in relaciones:
                    print(f"{rel['columna_local']:<20} {rel['tabla_referenciada']:<20} {rel['columna_referenciada']:<20}")
            else:
                print("ℹ️ No se encontraron relaciones de clave foránea")
            
            # Buscar tablas que referencien a dotaciones
            self.cursor.execute("""
                SELECT DISTINCT
                    table_name as tabla_que_referencia,
                    COLUMN_NAME as columna_que_referencia,
                    REFERENCED_COLUMN_NAME as columna_referenciada
                FROM information_schema.KEY_COLUMN_USAGE 
                WHERE table_schema = 'capired' 
                AND REFERENCED_TABLE_NAME = 'dotaciones'
            """)
            
            referencias_entrantes = self.cursor.fetchall()
            
            if referencias_entrantes:
                print(f"\n📥 TABLAS QUE REFERENCIAN A 'dotaciones' ({len(referencias_entrantes)}):")
                print("-" * 80)
                print(f"{'Tabla':<20} {'Columna':<20} {'Referencia':<20}")
                print("-" * 80)
                
                for ref in referencias_entrantes:
                    print(f"{ref['tabla_que_referencia']:<20} {ref['columna_que_referencia']:<20} {ref['columna_referenciada']:<20}")
            else:
                print("ℹ️ No hay tablas que referencien a 'dotaciones'")
                
        except mysql.connector.Error as e:
            print(f"✗ Error al analizar relaciones: {e}")
    
    def obtener_datos_ejemplo(self, limite=10):
        """Obtiene datos de ejemplo de la tabla"""
        print(f"\n=== DATOS DE EJEMPLO (primeros {limite} registros) ===")
        
        try:
            # Contar total de registros
            self.cursor.execute("SELECT COUNT(*) as total FROM dotaciones")
            total = self.cursor.fetchone()['total']
            
            print(f"\n📊 Total de registros en la tabla: {total}")
            
            if total == 0:
                print("ℹ️ La tabla está vacía")
                return
            
            # Obtener datos de ejemplo
            self.cursor.execute(f"SELECT * FROM dotaciones LIMIT {limite}")
            registros = self.cursor.fetchall()
            
            if registros:
                print(f"\n📋 PRIMEROS {len(registros)} REGISTROS:")
                print("-" * 120)
                
                # Mostrar datos en formato JSON para mejor legibilidad
                for i, registro in enumerate(registros, 1):
                    print(f"\nRegistro {i}:")
                    for campo, valor in registro.items():
                        print(f"  {campo}: {valor}")
                    print("-" * 60)
            
        except mysql.connector.Error as e:
            print(f"✗ Error al obtener datos de ejemplo: {e}")
    
    def analizar_otras_tablas_relacionadas(self):
        """Analiza otras tablas que podrían estar relacionadas con dotaciones"""
        print("\n=== ANÁLISIS DE TABLAS RELACIONADAS EN EL SISTEMA ===")
        
        try:
            # Buscar tablas que contengan palabras clave relacionadas
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'capired' 
                AND (table_name LIKE '%tecnico%' 
                     OR table_name LIKE '%equipo%' 
                     OR table_name LIKE '%herramienta%'
                     OR table_name LIKE '%asignacion%'
                     OR table_name LIKE '%stock%'
                     OR table_name LIKE '%inventario%'
                     OR table_name LIKE '%material%')
                ORDER BY table_name
            """)
            
            tablas_relacionadas = self.cursor.fetchall()
            
            if tablas_relacionadas:
                print(f"\n🔍 TABLAS POTENCIALMENTE RELACIONADAS ({len(tablas_relacionadas)}):")
                for tabla in tablas_relacionadas:
                    nombre_tabla = tabla['table_name'] if isinstance(tabla, dict) else tabla[0]
                    print(f"  - {nombre_tabla}")
            else:
                print("ℹ️ No se encontraron tablas con nombres relacionados")
            
            # Listar todas las tablas del sistema
            self.cursor.execute("""
                SELECT table_name, table_rows, table_comment
                FROM information_schema.tables 
                WHERE table_schema = 'capired' 
                ORDER BY table_name
            """)
            
            todas_tablas = self.cursor.fetchall()
            
            print(f"\n📋 TODAS LAS TABLAS EN LA BASE DE DATOS ({len(todas_tablas)}):")
            print("-" * 60)
            print(f"{'Tabla':<30} {'Registros':<10} {'Comentario':<20}")
            print("-" * 60)
            
            for tabla in todas_tablas:
                registros = tabla['table_rows'] or 0
                comentario = tabla['table_comment'] or ''
                print(f"{tabla['table_name']:<30} {registros:<10} {comentario:<20}")
                
        except mysql.connector.Error as e:
            print(f"✗ Error al analizar tablas relacionadas: {e}")
    
    def generar_reporte_completo(self):
        """Genera un reporte completo del análisis"""
        print("\n" + "=" * 80)
        print("🔍 INICIANDO ANÁLISIS COMPLETO DE LA TABLA 'dotaciones'")
        print("=" * 80)
        
        if not self.conectar():
            return False
        
        try:
            # Ejecutar todos los análisis
            estructura = self.analizar_estructura_tabla()
            self.analizar_indices_claves()
            self.analizar_relaciones()
            self.obtener_datos_ejemplo()
            self.analizar_otras_tablas_relacionadas()
            
            print("\n" + "=" * 80)
            print("✅ ANÁLISIS COMPLETADO EXITOSAMENTE")
            print("=" * 80)
            
            # Resumen de hallazgos
            print("\n📋 RESUMEN DE HALLAZGOS:")
            if estructura:
                print(f"  ✓ Tabla 'dotaciones' encontrada con {len(estructura)} campos")
                print("  ✓ Estructura analizada correctamente")
                print("  ✓ Relaciones y dependencias identificadas")
                print("  ✓ Datos de ejemplo obtenidos")
                print("\n🎯 PRÓXIMOS PASOS:")
                print("  1. Diseñar interfaz web basada en la estructura encontrada")
                print("  2. Implementar funcionalidades de asignación y control")
                print("  3. Crear gráficos de control de stock")
                print("  4. Configurar rutas y endpoints del módulo")
            else:
                print("  ⚠️ Problemas encontrados durante el análisis")
                print("  ⚠️ Revisar la estructura de la base de datos")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Error durante el análisis: {e}")
            return False
        
        finally:
            self.cerrar_conexion()
    
    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.conexion:
            self.conexion.close()
        print("\n🔌 Conexión cerrada")

def main():
    """Función principal"""
    print("🚀 Analizador de Tabla Dotaciones - Sistema Capired")
    print(f"📅 Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    analizador = AnalizadorDotaciones()
    
    try:
        exito = analizador.generar_reporte_completo()
        
        if exito:
            print("\n✅ Análisis completado. Proceder con el desarrollo del módulo.")
            sys.exit(0)
        else:
            print("\n❌ Análisis falló. Revisar configuración de base de datos.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Análisis interrumpido por el usuario")
        analizador.cerrar_conexion()
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        analizador.cerrar_conexion()
        sys.exit(1)

if __name__ == "__main__":
    main()