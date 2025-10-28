#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECANISMO UNIFICADO DE AJUSTE DE STOCK

Este script implementa un mecanismo para unificar el manejo de stock
entre dotaciones y ferretería, asegurando que los ajustes se reflejen
correctamente en el stock general.

Autor: Sistema de Stock Unificado
Fecha: 2025-01-24
"""

import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os
import json

# Cargar variables de entorno
load_dotenv()

class GestorStockUnificado:
    def __init__(self):
        self.conexion = None
        self.conectar_bd()
        self.mapeo_dotacion_ferreteria = {
            'pantalon': 'PANTALON_DOTACION',
            'camisetagris': 'CAMISA_GRIS_DOTACION',
            'guerrera': 'GUERRERA_DOTACION',
            'camisetapolo': 'POLO_DOTACION',
            'chaqueta': 'CHAQUETA_DOTACION',
            'botas': 'BOTAS_DOTACION',
            'guantes_nitrilo': 'GUANTES_NITRILO',
            'guantes_carnaza': 'GUANTES_CARNAZA',
            'gafas': 'GAFAS_SEGURIDAD',
            'gorra': 'GORRA_DOTACION',
            'casco': 'CASCO_SEGURIDAD'
        }
    
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
    
    def crear_tabla_stock_unificado(self):
        """Crear tabla de stock unificado si no existe"""
        if not self.conexion:
            return False
        
        try:
            cursor = self.conexion.cursor()
            
            # Crear tabla de stock unificado
            crear_tabla = """
                CREATE TABLE IF NOT EXISTS stock_unificado (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    codigo_material VARCHAR(50) NOT NULL UNIQUE,
                    descripcion VARCHAR(200) NOT NULL,
                    categoria ENUM('dotacion', 'ferreteria', 'mixto') NOT NULL,
                    cantidad_disponible INT DEFAULT 0,
                    cantidad_asignada INT DEFAULT 0,
                    cantidad_reservada INT DEFAULT 0,
                    cantidad_minima INT DEFAULT 0,
                    unidad_medida VARCHAR(20) DEFAULT 'unidad',
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT TRUE,
                    INDEX idx_codigo (codigo_material),
                    INDEX idx_categoria (categoria),
                    INDEX idx_disponible (cantidad_disponible)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
            
            cursor.execute(crear_tabla)
            
            # Crear tabla de movimientos de stock unificado
            crear_movimientos = """
                CREATE TABLE IF NOT EXISTS movimientos_stock_unificado (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    codigo_material VARCHAR(50) NOT NULL,
                    tipo_movimiento ENUM('entrada', 'salida', 'ajuste', 'asignacion', 'cambio') NOT NULL,
                    cantidad INT NOT NULL,
                    cantidad_anterior INT NOT NULL,
                    cantidad_nueva INT NOT NULL,
                    motivo VARCHAR(200),
                    referencia_operacion VARCHAR(100),
                    cedula_tecnico VARCHAR(20),
                    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usuario_sistema VARCHAR(50),
                    INDEX idx_material_fecha (codigo_material, fecha_movimiento),
                    INDEX idx_tecnico (cedula_tecnico),
                    INDEX idx_tipo (tipo_movimiento),
                    FOREIGN KEY (codigo_material) REFERENCES stock_unificado(codigo_material) ON UPDATE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
            
            cursor.execute(crear_movimientos)
            
            self.conexion.commit()
            cursor.close()
            
            print("✅ Tablas de stock unificado creadas exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")
            return False
    
    def sincronizar_stock_inicial(self):
        """Sincronizar stock inicial desde las tablas existentes"""
        if not self.conexion:
            return False
        
        try:
            cursor = self.conexion.cursor(dictionary=True)
            
            # Sincronizar desde vista_stock_dotaciones
            print("📊 Sincronizando stock de dotaciones...")
            
            query_dotaciones = """
                SELECT tipo_elemento, saldo_disponible 
                FROM vista_stock_dotaciones
            """
            
            cursor.execute(query_dotaciones)
            stock_dotaciones = cursor.fetchall()
            
            for item in stock_dotaciones:
                tipo_elemento = item['tipo_elemento']
                cantidad = item['saldo_disponible'] or 0
                
                if tipo_elemento in self.mapeo_dotacion_ferreteria:
                    codigo_material = self.mapeo_dotacion_ferreteria[tipo_elemento]
                    
                    # Insertar o actualizar en stock unificado
                    upsert_query = """
                        INSERT INTO stock_unificado 
                        (codigo_material, descripcion, categoria, cantidad_disponible)
                        VALUES (%s, %s, 'dotacion', %s)
                        ON DUPLICATE KEY UPDATE
                        cantidad_disponible = %s,
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    """
                    
                    descripcion = f"Dotación - {tipo_elemento.replace('_', ' ').title()}"
                    cursor.execute(upsert_query, (codigo_material, descripcion, cantidad, cantidad))
            
            # Sincronizar desde stock_ferretero
            print("🔧 Sincronizando stock de ferretería...")
            
            query_ferreteria = """
                SELECT codigo_material, descripcion, cantidad_disponible 
                FROM stock_ferretero
                WHERE activo = TRUE
            """
            
            cursor.execute(query_ferreteria)
            stock_ferreteria = cursor.fetchall()
            
            for item in stock_ferreteria:
                codigo_material = item['codigo_material']
                descripcion = item['descripcion']
                cantidad = item['cantidad_disponible'] or 0
                
                # Verificar si ya existe (podría ser mixto)
                check_query = "SELECT categoria FROM stock_unificado WHERE codigo_material = %s"
                cursor.execute(check_query, (codigo_material,))
                existente = cursor.fetchone()
                
                if existente:
                    # Actualizar como mixto si ya existe
                    update_query = """
                        UPDATE stock_unificado 
                        SET categoria = 'mixto',
                            descripcion = CONCAT(descripcion, ' / Ferretería'),
                            fecha_actualizacion = CURRENT_TIMESTAMP
                        WHERE codigo_material = %s
                    """
                    cursor.execute(update_query, (codigo_material,))
                else:
                    # Insertar como ferretería
                    insert_query = """
                        INSERT INTO stock_unificado 
                        (codigo_material, descripcion, categoria, cantidad_disponible)
                        VALUES (%s, %s, 'ferreteria', %s)
                    """
                    cursor.execute(insert_query, (codigo_material, descripcion, cantidad))
            
            self.conexion.commit()
            cursor.close()
            
            print("✅ Sincronización de stock inicial completada")
            return True
            
        except Exception as e:
            print(f"❌ Error sincronizando stock: {e}")
            return False
    
    def registrar_movimiento_stock(self, codigo_material, tipo_movimiento, cantidad, motivo, referencia_operacion=None, cedula_tecnico=None):
        """Registrar un movimiento de stock en el sistema unificado"""
        if not self.conexion:
            return False, "Error de conexión"
        
        try:
            cursor = self.conexion.cursor(dictionary=True)
            
            # Obtener cantidad actual
            query_actual = "SELECT cantidad_disponible FROM stock_unificado WHERE codigo_material = %s"
            cursor.execute(query_actual, (codigo_material,))
            resultado = cursor.fetchone()
            
            if not resultado:
                cursor.close()
                return False, f"Material {codigo_material} no encontrado en stock unificado"
            
            cantidad_anterior = resultado['cantidad_disponible']
            
            # Calcular nueva cantidad
            if tipo_movimiento in ['entrada', 'ajuste']:
                cantidad_nueva = cantidad_anterior + cantidad
            elif tipo_movimiento in ['salida', 'asignacion', 'cambio']:
                cantidad_nueva = cantidad_anterior - cantidad
                if cantidad_nueva < 0:
                    cursor.close()
                    return False, f"Stock insuficiente. Disponible: {cantidad_anterior}, Solicitado: {cantidad}"
            else:
                cursor.close()
                return False, f"Tipo de movimiento no válido: {tipo_movimiento}"
            
            # Actualizar stock
            update_query = """
                UPDATE stock_unificado 
                SET cantidad_disponible = %s,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE codigo_material = %s
            """
            cursor.execute(update_query, (cantidad_nueva, codigo_material))
            
            # Registrar movimiento
            insert_movimiento = """
                INSERT INTO movimientos_stock_unificado 
                (codigo_material, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, 
                 motivo, referencia_operacion, cedula_tecnico, usuario_sistema)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_movimiento, (
                codigo_material, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva,
                motivo, referencia_operacion, cedula_tecnico, 'sistema_dotaciones'
            ))
            
            self.conexion.commit()
            cursor.close()
            
            print(f"✅ Movimiento registrado: {codigo_material} - {tipo_movimiento} - {cantidad} unidades")
            return True, f"Stock actualizado: {cantidad_anterior} → {cantidad_nueva}"
            
        except Exception as e:
            return False, f"Error registrando movimiento: {e}"
    
    def procesar_asignacion_dotacion(self, cedula_tecnico, items_dict, referencia_operacion=None):
        """Procesar una asignación de dotación en el stock unificado"""
        print(f"\n=== PROCESANDO ASIGNACIÓN DE DOTACIÓN ===")
        print(f"Técnico: {cedula_tecnico}")
        print(f"Items: {items_dict}")
        
        movimientos_exitosos = []
        movimientos_fallidos = []
        
        for tipo_elemento, cantidad in items_dict.items():
            if cantidad > 0 and tipo_elemento in self.mapeo_dotacion_ferreteria:
                codigo_material = self.mapeo_dotacion_ferreteria[tipo_elemento]
                motivo = f"Asignación de dotación - {tipo_elemento}"
                
                exito, mensaje = self.registrar_movimiento_stock(
                    codigo_material, 'asignacion', cantidad, motivo, referencia_operacion, cedula_tecnico
                )
                
                if exito:
                    movimientos_exitosos.append({
                        'elemento': tipo_elemento,
                        'codigo': codigo_material,
                        'cantidad': cantidad,
                        'mensaje': mensaje
                    })
                else:
                    movimientos_fallidos.append({
                        'elemento': tipo_elemento,
                        'codigo': codigo_material,
                        'cantidad': cantidad,
                        'error': mensaje
                    })
        
        # Resumen de la operación
        print(f"\n📊 RESUMEN DE ASIGNACIÓN:")
        print(f"✅ Exitosos: {len(movimientos_exitosos)}")
        print(f"❌ Fallidos: {len(movimientos_fallidos)}")
        
        if movimientos_fallidos:
            print("\n❌ ERRORES:")
            for fallo in movimientos_fallidos:
                print(f"  - {fallo['elemento']}: {fallo['error']}")
        
        return len(movimientos_fallidos) == 0, {
            'exitosos': movimientos_exitosos,
            'fallidos': movimientos_fallidos
        }
    
    def procesar_cambio_dotacion(self, cedula_tecnico, items_dict, referencia_operacion=None):
        """Procesar un cambio de dotación en el stock unificado"""
        print(f"\n=== PROCESANDO CAMBIO DE DOTACIÓN ===")
        print(f"Técnico: {cedula_tecnico}")
        print(f"Items: {items_dict}")
        
        movimientos_exitosos = []
        movimientos_fallidos = []
        
        for tipo_elemento, cantidad in items_dict.items():
            if cantidad > 0 and tipo_elemento in self.mapeo_dotacion_ferreteria:
                codigo_material = self.mapeo_dotacion_ferreteria[tipo_elemento]
                motivo = f"Cambio de dotación - {tipo_elemento}"
                
                exito, mensaje = self.registrar_movimiento_stock(
                    codigo_material, 'cambio', cantidad, motivo, referencia_operacion, cedula_tecnico
                )
                
                if exito:
                    movimientos_exitosos.append({
                        'elemento': tipo_elemento,
                        'codigo': codigo_material,
                        'cantidad': cantidad,
                        'mensaje': mensaje
                    })
                else:
                    movimientos_fallidos.append({
                        'elemento': tipo_elemento,
                        'codigo': codigo_material,
                        'cantidad': cantidad,
                        'error': mensaje
                    })
        
        # Resumen de la operación
        print(f"\n📊 RESUMEN DE CAMBIO:")
        print(f"✅ Exitosos: {len(movimientos_exitosos)}")
        print(f"❌ Fallidos: {len(movimientos_fallidos)}")
        
        if movimientos_fallidos:
            print("\n❌ ERRORES:")
            for fallo in movimientos_fallidos:
                print(f"  - {fallo['elemento']}: {fallo['error']}")
        
        return len(movimientos_fallidos) == 0, {
            'exitosos': movimientos_exitosos,
            'fallidos': movimientos_fallidos
        }
    
    def obtener_reporte_stock_unificado(self):
        """Obtener reporte completo del stock unificado"""
        if not self.conexion:
            return None
        
        try:
            cursor = self.conexion.cursor(dictionary=True)
            
            query = """
                SELECT 
                    codigo_material,
                    descripcion,
                    categoria,
                    cantidad_disponible,
                    cantidad_asignada,
                    cantidad_reservada,
                    cantidad_minima,
                    unidad_medida,
                    fecha_actualizacion,
                    CASE 
                        WHEN cantidad_disponible <= cantidad_minima THEN 'CRITICO'
                        WHEN cantidad_disponible <= cantidad_minima * 1.5 THEN 'BAJO'
                        ELSE 'NORMAL'
                    END as estado_stock
                FROM stock_unificado
                WHERE activo = TRUE
                ORDER BY categoria, codigo_material
            """
            
            cursor.execute(query)
            reporte = cursor.fetchall()
            cursor.close()
            
            return reporte
            
        except Exception as e:
            print(f"❌ Error obteniendo reporte: {e}")
            return None
    
    def cerrar_conexion(self):
        """Cerrar conexión a la base de datos"""
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
            print("✅ Conexión cerrada")

def test_stock_unificado():
    """Función de prueba para el stock unificado"""
    gestor = GestorStockUnificado()
    
    if not gestor.conexion:
        print("❌ No se pudo establecer conexión con la base de datos")
        return
    
    print("\n=== PRUEBA DE STOCK UNIFICADO ===")
    
    # Crear tablas
    gestor.crear_tabla_stock_unificado()
    
    # Sincronizar stock inicial
    gestor.sincronizar_stock_inicial()
    
    # Datos de prueba
    cedula_test = "12345678"
    items_asignacion = {
        'pantalon': 2,
        'camisetagris': 1,
        'botas': 1
    }
    
    items_cambio = {
        'guerrera': 1,
        'gafas': 1
    }
    
    # Probar asignación
    print("\n--- PRUEBA DE ASIGNACIÓN ---")
    exito_asignacion, resultado_asignacion = gestor.procesar_asignacion_dotacion(
        cedula_test, items_asignacion, "TEST_ASIGNACION_001"
    )
    
    # Probar cambio
    print("\n--- PRUEBA DE CAMBIO ---")
    exito_cambio, resultado_cambio = gestor.procesar_cambio_dotacion(
        cedula_test, items_cambio, "TEST_CAMBIO_001"
    )
    
    # Obtener reporte
    print("\n--- REPORTE DE STOCK ---")
    reporte = gestor.obtener_reporte_stock_unificado()
    
    if reporte:
        print(f"\n📊 STOCK UNIFICADO ({len(reporte)} items):")
        for item in reporte[:10]:  # Mostrar solo los primeros 10
            print(f"  {item['codigo_material']}: {item['cantidad_disponible']} {item['unidad_medida']} - {item['estado_stock']}")
    
    gestor.cerrar_conexion()

if __name__ == "__main__":
    test_stock_unificado()