#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTEGRACIÓN DE DOTACIONES CON VALIDACIÓN Y STOCK UNIFICADO

Este script proporciona funciones mejoradas para integrar las operaciones
de dotación con el sistema de validación y stock unificado.

Autor: Sistema de Integración
Fecha: 2025-01-24
"""

import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os
import json
from validacion_dotaciones_unificada import ValidadorDotaciones
from mecanismo_stock_unificado import GestorStockUnificado

# Cargar variables de entorno
load_dotenv()

class DotacionesIntegradas:
    def __init__(self):
        self.conexion = None
        self.validador = ValidadorDotaciones()
        self.gestor_stock = GestorStockUnificado()
        self.conectar_bd()
    
    def conectar_bd(self):
        """Establecer conexión con la base de datos"""
        try:
            self.conexion = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                database=os.getenv('MYSQL_DB', 'capired'),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD', ''),
                port=int(os.getenv('MYSQL_PORT', '3306')),
                charset='utf8mb4'
            )
            print("✅ Conexión exitosa a la base de datos")
        except Exception as e:
            print(f"❌ Error conectando a la base de datos: {e}")
            self.conexion = None
    
    def crear_dotacion_validada(self, datos_dotacion):
        """
        Crear una nueva dotación con validación completa
        
        Args:
            datos_dotacion (dict): Datos de la dotación incluyendo:
                - cedula_tecnico
                - nombre_tecnico
                - items (dict con cantidades)
                - observaciones (opcional)
        
        Returns:
            tuple: (exito, mensaje, detalles)
        """
        print(f"\n=== CREANDO DOTACIÓN VALIDADA ===")
        
        cedula_tecnico = datos_dotacion.get('cedula_tecnico')
        nombre_tecnico = datos_dotacion.get('nombre_tecnico')
        items = datos_dotacion.get('items', {})
        observaciones = datos_dotacion.get('observaciones', '')
        
        if not cedula_tecnico or not nombre_tecnico:
            return False, "Cédula y nombre del técnico son obligatorios", {}
        
        # 1. Validar integridad de la operación
        validacion_exitosa, resultado_validacion = self.validador.validar_integridad_operacion(
            'asignacion', cedula_tecnico, items
        )
        
        if not validacion_exitosa:
            return False, f"Validación fallida: {resultado_validacion}", {}
        
        # 2. Procesar en stock unificado
        referencia_operacion = f"DOTACION_{cedula_tecnico}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        stock_exitoso, resultado_stock = self.gestor_stock.procesar_asignacion_dotacion(
            cedula_tecnico, items, referencia_operacion
        )
        
        if not stock_exitoso:
            return False, "Error procesando stock unificado", resultado_stock
        
        # 3. Insertar en tabla dotaciones
        try:
            cursor = self.conexion.cursor()
            
            # Preparar datos para inserción
            fecha_asignacion = datetime.now()
            
            insert_query = """
                INSERT INTO dotaciones (
                    cedula_tecnico, nombre_tecnico, fecha_asignacion,
                    pantalon, camisetagris, guerrera, camisetapolo, botas,
                    guantes_nitrilo, guantes_carnaza, gafas, gorra, casco,
                    observaciones, referencia_operacion, validado
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            valores = (
                cedula_tecnico, nombre_tecnico, fecha_asignacion,
                items.get('pantalon', 0), items.get('camisetagris', 0),
                items.get('guerrera', 0), items.get('camisetapolo', 0),
                items.get('botas', 0), items.get('guantes_nitrilo', 0),
                items.get('guantes_carnaza', 0), items.get('gafas', 0),
                items.get('gorra', 0), items.get('casco', 0),
                observaciones, referencia_operacion, True
            )
            
            cursor.execute(insert_query, valores)
            dotacion_id = cursor.lastrowid
            
            self.conexion.commit()
            cursor.close()
            
            # 4. Crear log de validación
            self.validador.crear_log_validacion(
                'asignacion', cedula_tecnico, items, resultado_validacion
            )
            
            print(f"✅ Dotación creada exitosamente - ID: {dotacion_id}")
            
            return True, "Dotación creada exitosamente", {
                'dotacion_id': dotacion_id,
                'referencia_operacion': referencia_operacion,
                'validacion': resultado_validacion,
                'stock': resultado_stock
            }
            
        except Exception as e:
            print(f"❌ Error creando dotación: {e}")
            return False, f"Error en base de datos: {e}", {}
    
    def registrar_cambio_dotacion_validado(self, datos_cambio):
        """
        Registrar un cambio de dotación con validación completa
        
        Args:
            datos_cambio (dict): Datos del cambio incluyendo:
                - cedula_tecnico
                - nombre_tecnico
                - items (dict con cantidades)
                - motivo_cambio
                - observaciones (opcional)
        
        Returns:
            tuple: (exito, mensaje, detalles)
        """
        print(f"\n=== REGISTRANDO CAMBIO DE DOTACIÓN VALIDADO ===")
        
        cedula_tecnico = datos_cambio.get('cedula_tecnico')
        nombre_tecnico = datos_cambio.get('nombre_tecnico')
        items = datos_cambio.get('items', {})
        motivo_cambio = datos_cambio.get('motivo_cambio', '')
        observaciones = datos_cambio.get('observaciones', '')
        
        if not cedula_tecnico or not nombre_tecnico:
            return False, "Cédula y nombre del técnico son obligatorios", {}
        
        if not motivo_cambio:
            return False, "Motivo del cambio es obligatorio", {}
        
        # 1. Validar integridad de la operación
        validacion_exitosa, resultado_validacion = self.validador.validar_integridad_operacion(
            'cambio', cedula_tecnico, items
        )
        
        if not validacion_exitosa:
            return False, f"Validación fallida: {resultado_validacion}", {}
        
        # 2. Procesar en stock unificado
        referencia_operacion = f"CAMBIO_{cedula_tecnico}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        stock_exitoso, resultado_stock = self.gestor_stock.procesar_cambio_dotacion(
            cedula_tecnico, items, referencia_operacion
        )
        
        if not stock_exitoso:
            return False, "Error procesando stock unificado", resultado_stock
        
        # 3. Insertar en tabla cambios_dotacion
        try:
            cursor = self.conexion.cursor()
            
            # Preparar datos para inserción
            fecha_cambio = datetime.now()
            
            insert_query = """
                INSERT INTO cambios_dotacion (
                    cedula_tecnico, nombre_tecnico, fecha_cambio, motivo_cambio,
                    pantalon, camisetagris, guerrera, camisetapolo, botas,
                    guantes_nitrilo, guantes_carnaza, gafas, gorra, casco,
                    observaciones, referencia_operacion, validado
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            valores = (
                cedula_tecnico, nombre_tecnico, fecha_cambio, motivo_cambio,
                items.get('pantalon', 0), items.get('camisetagris', 0),
                items.get('guerrera', 0), items.get('camisetapolo', 0),
                items.get('botas', 0), items.get('guantes_nitrilo', 0),
                items.get('guantes_carnaza', 0), items.get('gafas', 0),
                items.get('gorra', 0), items.get('casco', 0),
                observaciones, referencia_operacion, True
            )
            
            cursor.execute(insert_query, valores)
            cambio_id = cursor.lastrowid
            
            self.conexion.commit()
            cursor.close()
            
            # 4. Crear log de validación
            self.validador.crear_log_validacion(
                'cambio', cedula_tecnico, items, resultado_validacion
            )
            
            print(f"✅ Cambio de dotación registrado exitosamente - ID: {cambio_id}")
            
            return True, "Cambio de dotación registrado exitosamente", {
                'cambio_id': cambio_id,
                'referencia_operacion': referencia_operacion,
                'validacion': resultado_validacion,
                'stock': resultado_stock
            }
            
        except Exception as e:
            print(f"❌ Error registrando cambio: {e}")
            return False, f"Error en base de datos: {e}", {}
    
    def verificar_integridad_datos(self):
        """
        Verificar la integridad de los datos entre las diferentes tablas
        
        Returns:
            dict: Reporte de integridad
        """
        print(f"\n=== VERIFICANDO INTEGRIDAD DE DATOS ===")
        
        if not self.conexion:
            return {'error': 'No hay conexión a la base de datos'}
        
        try:
            cursor = self.conexion.cursor(dictionary=True)
            reporte = {
                'fecha_verificacion': datetime.now().isoformat(),
                'tablas_verificadas': [],
                'inconsistencias': [],
                'resumen': {}
            }
            
            # 1. Verificar dotaciones sin validar
            query_dotaciones_sin_validar = """
                SELECT COUNT(*) as total 
                FROM dotaciones 
                WHERE validado IS NULL OR validado = FALSE
            """
            cursor.execute(query_dotaciones_sin_validar)
            dotaciones_sin_validar = cursor.fetchone()['total']
            
            if dotaciones_sin_validar > 0:
                reporte['inconsistencias'].append({
                    'tipo': 'dotaciones_sin_validar',
                    'cantidad': dotaciones_sin_validar,
                    'descripcion': 'Dotaciones que no han pasado por el proceso de validación'
                })
            
            # 2. Verificar cambios sin validar
            query_cambios_sin_validar = """
                SELECT COUNT(*) as total 
                FROM cambios_dotacion 
                WHERE validado IS NULL OR validado = FALSE
            """
            cursor.execute(query_cambios_sin_validar)
            cambios_sin_validar = cursor.fetchone()['total']
            
            if cambios_sin_validar > 0:
                reporte['inconsistencias'].append({
                    'tipo': 'cambios_sin_validar',
                    'cantidad': cambios_sin_validar,
                    'descripcion': 'Cambios de dotación que no han pasado por el proceso de validación'
                })
            
            # 3. Verificar operaciones sin referencia
            query_sin_referencia = """
                SELECT 
                    'dotaciones' as tabla,
                    COUNT(*) as total 
                FROM dotaciones 
                WHERE referencia_operacion IS NULL
                UNION ALL
                SELECT 
                    'cambios_dotacion' as tabla,
                    COUNT(*) as total 
                FROM cambios_dotacion 
                WHERE referencia_operacion IS NULL
            """
            cursor.execute(query_sin_referencia)
            sin_referencia = cursor.fetchall()
            
            for item in sin_referencia:
                if item['total'] > 0:
                    reporte['inconsistencias'].append({
                        'tipo': f"{item['tabla']}_sin_referencia",
                        'cantidad': item['total'],
                        'descripcion': f"Registros en {item['tabla']} sin referencia de operación"
                    })
            
            # 4. Verificar stock unificado
            query_stock_critico = """
                SELECT COUNT(*) as total 
                FROM stock_unificado 
                WHERE cantidad_disponible <= cantidad_minima
                AND activo = TRUE
            """
            cursor.execute(query_stock_critico)
            stock_critico = cursor.fetchone()['total']
            
            if stock_critico > 0:
                reporte['inconsistencias'].append({
                    'tipo': 'stock_critico',
                    'cantidad': stock_critico,
                    'descripcion': 'Materiales con stock crítico o agotado'
                })
            
            # 5. Resumen general
            reporte['resumen'] = {
                'total_inconsistencias': len(reporte['inconsistencias']),
                'dotaciones_sin_validar': dotaciones_sin_validar,
                'cambios_sin_validar': cambios_sin_validar,
                'stock_critico': stock_critico,
                'estado_general': 'CRITICO' if len(reporte['inconsistencias']) > 3 else 'ADVERTENCIA' if len(reporte['inconsistencias']) > 0 else 'NORMAL'
            }
            
            cursor.close()
            
            print(f"📊 Verificación completada - Estado: {reporte['resumen']['estado_general']}")
            print(f"📋 Inconsistencias encontradas: {reporte['resumen']['total_inconsistencias']}")
            
            return reporte
            
        except Exception as e:
            print(f"❌ Error verificando integridad: {e}")
            return {'error': str(e)}
    
    def migrar_datos_existentes(self):
        """
        Migrar datos existentes al nuevo sistema validado
        
        Returns:
            dict: Resultado de la migración
        """
        print(f"\n=== MIGRANDO DATOS EXISTENTES ===")
        
        if not self.conexion:
            return {'error': 'No hay conexión a la base de datos'}
        
        try:
            cursor = self.conexion.cursor()
            
            # 1. Agregar columnas de validación si no existen
            agregar_columnas = [
                "ALTER TABLE dotaciones ADD COLUMN IF NOT EXISTS validado BOOLEAN DEFAULT FALSE",
                "ALTER TABLE dotaciones ADD COLUMN IF NOT EXISTS referencia_operacion VARCHAR(100)",
                "ALTER TABLE cambios_dotacion ADD COLUMN IF NOT EXISTS validado BOOLEAN DEFAULT FALSE",
                "ALTER TABLE cambios_dotacion ADD COLUMN IF NOT EXISTS referencia_operacion VARCHAR(100)"
            ]
            
            for query in agregar_columnas:
                try:
                    cursor.execute(query)
                except Exception as e:
                    print(f"⚠️ Columna ya existe o error: {e}")
            
            # 2. Generar referencias para registros existentes
            update_dotaciones = """
                UPDATE dotaciones 
                SET referencia_operacion = CONCAT('LEGACY_DOT_', id, '_', DATE_FORMAT(fecha_asignacion, '%Y%m%d'))
                WHERE referencia_operacion IS NULL
            """
            cursor.execute(update_dotaciones)
            dotaciones_actualizadas = cursor.rowcount
            
            update_cambios = """
                UPDATE cambios_dotacion 
                SET referencia_operacion = CONCAT('LEGACY_CAM_', id, '_', DATE_FORMAT(fecha_cambio, '%Y%m%d'))
                WHERE referencia_operacion IS NULL
            """
            cursor.execute(update_cambios)
            cambios_actualizados = cursor.rowcount
            
            self.conexion.commit()
            cursor.close()
            
            print(f"✅ Migración completada:")
            print(f"  - Dotaciones actualizadas: {dotaciones_actualizadas}")
            print(f"  - Cambios actualizados: {cambios_actualizados}")
            
            return {
                'exito': True,
                'dotaciones_actualizadas': dotaciones_actualizadas,
                'cambios_actualizados': cambios_actualizados
            }
            
        except Exception as e:
            print(f"❌ Error en migración: {e}")
            return {'error': str(e)}
    
    def cerrar_conexion(self):
        """Cerrar todas las conexiones"""
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
        
        self.validador.cerrar_conexion()
        self.gestor_stock.cerrar_conexion()
        
        print("✅ Todas las conexiones cerradas")

def test_integracion_completa():
    """Función de prueba para la integración completa"""
    dotaciones = DotacionesIntegradas()
    
    if not dotaciones.conexion:
        print("❌ No se pudo establecer conexión con la base de datos")
        return
    
    print("\n=== PRUEBA DE INTEGRACIÓN COMPLETA ===")
    
    # 1. Migrar datos existentes
    print("\n--- MIGRACIÓN DE DATOS ---")
    resultado_migracion = dotaciones.migrar_datos_existentes()
    print(f"Resultado migración: {resultado_migracion}")
    
    # 2. Inicializar sistemas
    dotaciones.gestor_stock.crear_tabla_stock_unificado()
    dotaciones.gestor_stock.sincronizar_stock_inicial()
    
    # 3. Probar creación de dotación
    print("\n--- PRUEBA DE CREACIÓN DE DOTACIÓN ---")
    datos_dotacion = {
        'cedula_tecnico': '87654321',
        'nombre_tecnico': 'Juan Pérez',
        'items': {
            'pantalon': 1,
            'camisetagris': 2,
            'botas': 1,
            'gafas': 1
        },
        'observaciones': 'Dotación de prueba integrada'
    }
    
    exito_dotacion, mensaje_dotacion, detalles_dotacion = dotaciones.crear_dotacion_validada(datos_dotacion)
    print(f"Resultado dotación: {exito_dotacion} - {mensaje_dotacion}")
    
    # 4. Probar cambio de dotación
    print("\n--- PRUEBA DE CAMBIO DE DOTACIÓN ---")
    datos_cambio = {
        'cedula_tecnico': '87654321',
        'nombre_tecnico': 'Juan Pérez',
        'items': {
            'guerrera': 1,
            'casco': 1
        },
        'motivo_cambio': 'Cambio por deterioro',
        'observaciones': 'Cambio de prueba integrado'
    }
    
    exito_cambio, mensaje_cambio, detalles_cambio = dotaciones.registrar_cambio_dotacion_validado(datos_cambio)
    print(f"Resultado cambio: {exito_cambio} - {mensaje_cambio}")
    
    # 5. Verificar integridad
    print("\n--- VERIFICACIÓN DE INTEGRIDAD ---")
    reporte_integridad = dotaciones.verificar_integridad_datos()
    print(f"Estado general: {reporte_integridad.get('resumen', {}).get('estado_general', 'DESCONOCIDO')}")
    
    dotaciones.cerrar_conexion()

if __name__ == "__main__":
    test_integracion_completa()