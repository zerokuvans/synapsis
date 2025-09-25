#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GESTOR DE STOCK UNIFICADO CON VALIDACIÓN POR ESTADO

Este script extiende el GestorStockUnificado para incluir validación
por estado de valoración (VALORADO/NO VALORADO) durante las asignaciones.

Autor: Sistema de Stock Unificado
Fecha: 2025-01-24
"""

import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os
import json
from validacion_stock_por_estado import ValidadorStockPorEstado

# Cargar variables de entorno
load_dotenv()

class GestorStockConValidacionEstado:
    def __init__(self):
        self.conexion = None
        self.conectar_bd()
        self.validador_estado = ValidadorStockPorEstado()
        self.mapeo_dotacion_ferreteria = {
            'pantalon': 'PANTALON_DOTACION',
            'camisetagris': 'CAMISA_GRIS_DOTACION',
            'guerrera': 'GUERRERA_DOTACION',
            'camisetapolo': 'POLO_DOTACION',
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
    
    def procesar_asignacion_dotacion_con_estado(self, cedula_tecnico, items_con_estado, referencia_operacion=None):
        """
        Procesar una asignación de dotación considerando el estado de valoración
        
        Args:
            cedula_tecnico: Cédula del técnico
            items_con_estado: Dict con formato {'item': {'cantidad': int, 'estado': 'VALORADO'/'NO VALORADO'}}
            referencia_operacion: Referencia opcional de la operación
        
        Returns:
            tuple: (exito, resultado_detallado)
        """
        print(f"\n=== PROCESANDO ASIGNACIÓN CON VALIDACIÓN POR ESTADO ===")
        print(f"Técnico: {cedula_tecnico}")
        print(f"Items con estado: {items_con_estado}")
        
        # Convertir formato para el validador
        items_dict = {item: datos['cantidad'] for item, datos in items_con_estado.items()}
        estados_dict = {item: datos['estado'] for item, datos in items_con_estado.items()}
        
        # Primero validar que hay stock suficiente por estado
        validacion_exitosa, mensaje_validacion = self.validador_estado.validar_asignacion_con_estados(
            int(cedula_tecnico), items_dict, estados_dict
        )
        
        if not validacion_exitosa:
            print(f"❌ Validación fallida: {mensaje_validacion}")
            return False, {
                'error': 'Validación de stock fallida',
                'detalle': mensaje_validacion,
                'exitosos': [],
                'fallidos': list(items_con_estado.keys())
            }
        
        print("✅ Validación de stock por estado exitosa")
        
        # Proceder con la asignación
        movimientos_exitosos = []
        movimientos_fallidos = []
        
        for tipo_elemento, datos in items_con_estado.items():
            cantidad = datos['cantidad']
            estado = datos['estado']
            
            if cantidad > 0:
                # Registrar el movimiento específico por estado
                exito, mensaje = self._registrar_movimiento_con_estado(
                    tipo_elemento, cantidad, estado, 'asignacion', 
                    cedula_tecnico, referencia_operacion
                )
                
                if exito:
                    movimientos_exitosos.append({
                        'elemento': tipo_elemento,
                        'cantidad': cantidad,
                        'estado': estado,
                        'mensaje': mensaje
                    })
                else:
                    movimientos_fallidos.append({
                        'elemento': tipo_elemento,
                        'cantidad': cantidad,
                        'estado': estado,
                        'error': mensaje
                    })
        
        # Resumen de la operación
        print(f"\n📊 RESUMEN DE ASIGNACIÓN CON ESTADO:")
        print(f"✅ Exitosos: {len(movimientos_exitosos)}")
        print(f"❌ Fallidos: {len(movimientos_fallidos)}")
        
        if movimientos_fallidos:
            print("\n❌ ERRORES:")
            for fallo in movimientos_fallidos:
                print(f"  - {fallo['elemento']} ({fallo['estado']}): {fallo['error']}")
        
        return len(movimientos_fallidos) == 0, {
            'exitosos': movimientos_exitosos,
            'fallidos': movimientos_fallidos
        }
    
    def _registrar_movimiento_con_estado(self, tipo_elemento, cantidad, estado, tipo_movimiento, cedula_tecnico, referencia_operacion):
        """
        Registrar un movimiento específico considerando el estado de valoración
        
        Args:
            tipo_elemento: Tipo de elemento (botas, pantalon, etc.)
            cantidad: Cantidad a mover
            estado: Estado de valoración (VALORADO/NO VALORADO)
            tipo_movimiento: Tipo de movimiento (asignacion, cambio, etc.)
            cedula_tecnico: Cédula del técnico
            referencia_operacion: Referencia de la operación
        
        Returns:
            tuple: (exito, mensaje)
        """
        if not self.conexion:
            return False, "Error de conexión"
        
        try:
            cursor = self.conexion.cursor()
            
            # Registrar en la tabla de movimientos específicos por estado
            insert_movimiento = """
                INSERT INTO movimientos_stock_por_estado 
                (tipo_elemento, cantidad, estado, tipo_movimiento, cedula_tecnico, 
                 referencia_operacion, fecha_movimiento, motivo)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s)
            """
            
            motivo = f"{tipo_movimiento.title()} de {tipo_elemento} ({estado})"
            
            cursor.execute(insert_movimiento, (
                tipo_elemento, cantidad, estado, tipo_movimiento, 
                cedula_tecnico, referencia_operacion, motivo
            ))
            
            self.conexion.commit()
            cursor.close()
            
            print(f"✅ Movimiento registrado: {tipo_elemento} - {cantidad} unidades ({estado})")
            return True, f"Movimiento registrado exitosamente: {cantidad} {tipo_elemento} ({estado})"
            
        except Exception as e:
            return False, f"Error registrando movimiento: {e}"
    
    def crear_tabla_movimientos_por_estado(self):
        """
        Crear tabla para registrar movimientos específicos por estado de valoración
        """
        if not self.conexion:
            return False
        
        try:
            cursor = self.conexion.cursor()
            
            crear_tabla = """
                CREATE TABLE IF NOT EXISTS movimientos_stock_por_estado (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tipo_elemento VARCHAR(50) NOT NULL,
                    cantidad INT NOT NULL,
                    estado ENUM('VALORADO', 'NO VALORADO') NOT NULL,
                    tipo_movimiento ENUM('asignacion', 'cambio', 'devolucion', 'ajuste') NOT NULL,
                    cedula_tecnico VARCHAR(20),
                    referencia_operacion VARCHAR(100),
                    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    motivo VARCHAR(200),
                    usuario_sistema VARCHAR(50) DEFAULT 'sistema_dotaciones',
                    INDEX idx_elemento_estado (tipo_elemento, estado),
                    INDEX idx_tecnico (cedula_tecnico),
                    INDEX idx_fecha (fecha_movimiento),
                    INDEX idx_tipo_movimiento (tipo_movimiento)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
            
            cursor.execute(crear_tabla)
            self.conexion.commit()
            cursor.close()
            
            print("✅ Tabla de movimientos por estado creada exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error creando tabla de movimientos por estado: {e}")
            return False
    
    def obtener_reporte_stock_por_estado(self):
        """
        Obtener reporte de stock diferenciado por estado de valoración
        
        Returns:
            dict: Reporte con stock por elemento y estado
        """
        reporte = {}
        
        elementos = ['botas', 'pantalon', 'camisetagris', 'guerrera', 'camisetapolo', 
                    'guantes_nitrilo', 'guantes_carnaza', 'gafas', 'gorra', 'casco']
        
        for elemento in elementos:
            stock_detallado = self.validador_estado.obtener_stock_detallado_por_estado(elemento)
            
            reporte[elemento] = {
                'VALORADO': stock_detallado.get('VALORADO', 0),
                'NO VALORADO': stock_detallado.get('NO VALORADO', 0),
                'TOTAL': stock_detallado.get('VALORADO', 0) + stock_detallado.get('NO VALORADO', 0)
            }
        
        return reporte
    
    def cerrar_conexion(self):
        """Cerrar conexión con la base de datos"""
        if self.conexion:
            self.conexion.close()
            self.validador_estado.cerrar_conexion()
            print("✅ Conexiones cerradas")


def test_gestor_con_estado():
    """Función de prueba para el gestor con validación por estado"""
    print("=== PRUEBA DEL GESTOR CON VALIDACIÓN POR ESTADO ===")
    
    gestor = GestorStockConValidacionEstado()
    
    # Crear tabla si no existe
    gestor.crear_tabla_movimientos_por_estado()
    
    # Obtener reporte de stock actual
    print("\n📊 STOCK ACTUAL POR ESTADO:")
    reporte = gestor.obtener_reporte_stock_por_estado()
    for elemento, stocks in reporte.items():
        print(f"{elemento}: VALORADO={stocks['VALORADO']}, NO VALORADO={stocks['NO VALORADO']}, TOTAL={stocks['TOTAL']}")
    
    # Simular asignación con estados específicos
    print("\n🧪 SIMULANDO ASIGNACIÓN CON ESTADOS:")
    items_con_estado = {
        'botas': {'cantidad': 1, 'estado': 'NO VALORADO'},
        'pantalon': {'cantidad': 1, 'estado': 'VALORADO'}
    }
    
    exito, resultado = gestor.procesar_asignacion_dotacion_con_estado(
        cedula_tecnico='12345678',
        items_con_estado=items_con_estado,
        referencia_operacion='TEST_ESTADO_001'
    )
    
    print(f"\n📋 RESULTADO DE LA ASIGNACIÓN:")
    print(f"Éxito: {exito}")
    print(f"Detalles: {json.dumps(resultado, indent=2, ensure_ascii=False)}")
    
    gestor.cerrar_conexion()

if __name__ == "__main__":
    test_gestor_con_estado()