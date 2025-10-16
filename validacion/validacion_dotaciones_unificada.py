#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDACIÓN UNIFICADA PARA DOTACIONES

Este script implementa validaciones para prevenir inserciones duplicadas
y asegurar la integridad de datos en operaciones de dotación.

Autor: Sistema de Validación
Fecha: 2025-01-24
"""

import mysql.connector
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import hashlib

# Cargar variables de entorno
load_dotenv()

class ValidadorDotaciones:
    def __init__(self):
        self.conexion = None
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
    
    def generar_hash_operacion(self, tipo_operacion, cedula_tecnico, items_dict, fecha=None):
        """Generar hash único para una operación de dotación"""
        if fecha is None:
            fecha = datetime.now().strftime('%Y-%m-%d')
        
        # Crear string único basado en los parámetros
        items_str = '|'.join([f"{k}:{v}" for k, v in sorted(items_dict.items()) if v > 0])
        operacion_str = f"{tipo_operacion}|{cedula_tecnico}|{items_str}|{fecha}"
        
        # Generar hash MD5
        return hashlib.md5(operacion_str.encode()).hexdigest()
    
    def validar_duplicado_asignacion(self, id_codigo_consumidor, items_dict, tolerancia_minutos=5):
        """Validar si existe una asignación duplicada reciente"""
        if not self.conexion:
            return False, "Error de conexión a la base de datos"
        
        try:
            cursor = self.conexion.cursor(dictionary=True)
            
            # Buscar asignaciones recientes del mismo técnico
            fecha_limite = datetime.now() - timedelta(minutes=tolerancia_minutos)
            
            query = """
                 SELECT * FROM dotaciones 
                 WHERE id_codigo_consumidor = %s 
                 AND fecha_registro >= %s
                 ORDER BY fecha_registro DESC
                 LIMIT 10
             """
            
            cursor.execute(query, (id_codigo_consumidor, fecha_limite))
            asignaciones_recientes = cursor.fetchall()
            
            # Verificar si alguna asignación reciente es idéntica
            for asignacion in asignaciones_recientes:
                items_existentes = {
                    'pantalon': asignacion.get('pantalon', 0) or 0,
                    'camisetagris': asignacion.get('camisetagris', 0) or 0,
                    'guerrera': asignacion.get('guerrera', 0) or 0,
                    'camisetapolo': asignacion.get('camisetapolo', 0) or 0,
                    'botas': asignacion.get('botas', 0) or 0,
                    'guantes_nitrilo': asignacion.get('guantes_nitrilo', 0) or 0,
                    'guantes_carnaza': asignacion.get('guantes_carnaza', 0) or 0,
                    'gafas': asignacion.get('gafas', 0) or 0,
                    'gorra': asignacion.get('gorra', 0) or 0,
                    'casco': asignacion.get('casco', 0) or 0
                }
                
                # Comparar items
                if items_existentes == items_dict:
                    cursor.close()
                    return False, f"Asignación duplicada detectada. Última asignación idéntica: {asignacion['fecha_asignacion']}"
            
            cursor.close()
            return True, "Validación exitosa - No hay duplicados"
            
        except Exception as e:
            return False, f"Error validando duplicados: {e}"
    
    def validar_duplicado_cambio(self, id_codigo_consumidor, items_dict, tolerancia_minutos=5):
        """Validar si existe un cambio de dotación duplicado reciente"""
        if not self.conexion:
            return False, "Error de conexión a la base de datos"
        
        try:
            cursor = self.conexion.cursor(dictionary=True)
            
            # Buscar cambios recientes del mismo técnico
            fecha_limite = datetime.now() - timedelta(minutes=tolerancia_minutos)
            
            query = """
                 SELECT * FROM cambios_dotacion 
                 WHERE id_codigo_consumidor = %s 
                 AND fecha_registro >= %s
                 ORDER BY fecha_registro DESC
                 LIMIT 10
             """
            
            cursor.execute(query, (id_codigo_consumidor, fecha_limite))
            cambios_recientes = cursor.fetchall()
            
            # Verificar si algún cambio reciente es idéntico
            for cambio in cambios_recientes:
                items_existentes = {
                    'pantalon': cambio.get('pantalon', 0) or 0,
                    'camisetagris': cambio.get('camisetagris', 0) or 0,
                    'guerrera': cambio.get('guerrera', 0) or 0,
                    'camisetapolo': cambio.get('camisetapolo', 0) or 0,
                    'botas': cambio.get('botas', 0) or 0,
                    'guantes_nitrilo': cambio.get('guantes_nitrilo', 0) or 0,
                    'guantes_carnaza': cambio.get('guantes_carnaza', 0) or 0,
                    'gafas': cambio.get('gafas', 0) or 0,
                    'gorra': cambio.get('gorra', 0) or 0,
                    'casco': cambio.get('casco', 0) or 0
                }
                
                # Comparar items
                if items_existentes == items_dict:
                    cursor.close()
                    return False, f"Cambio duplicado detectado. Último cambio idéntico: {cambio['fecha_cambio']}"
            
            cursor.close()
            return True, "Validación exitosa - No hay duplicados"
            
        except Exception as e:
            return False, f"Error validando duplicados: {e}"
    
    def validar_stock_disponible(self, items_dict):
        """Validar que hay stock suficiente para la operación"""
        if not self.conexion:
            return False, "Error de conexión a la base de datos", {}
        
        try:
            cursor = self.conexion.cursor(dictionary=True)
            
            stock_insuficiente = []
            stock_actual = {}
            
            for tipo_elemento, cantidad_solicitada in items_dict.items():
                if cantidad_solicitada > 0:
                    # Consultar stock disponible
                    query = """
                        SELECT saldo_disponible 
                        FROM vista_stock_dotaciones 
                        WHERE tipo_elemento = %s
                    """
                    
                    cursor.execute(query, (tipo_elemento,))
                    resultado = cursor.fetchone()
                    
                    if resultado:
                        stock_disponible = resultado['saldo_disponible']
                        stock_actual[tipo_elemento] = stock_disponible
                        
                        if stock_disponible < cantidad_solicitada:
                            stock_insuficiente.append({
                                'elemento': tipo_elemento,
                                'solicitado': cantidad_solicitada,
                                'disponible': stock_disponible,
                                'faltante': cantidad_solicitada - stock_disponible
                            })
                    else:
                        stock_insuficiente.append({
                            'elemento': tipo_elemento,
                            'solicitado': cantidad_solicitada,
                            'disponible': 0,
                            'faltante': cantidad_solicitada
                        })
            
            cursor.close()
            
            if stock_insuficiente:
                mensaje = "Stock insuficiente para los siguientes elementos:\n"
                for item in stock_insuficiente:
                    mensaje += f"- {item['elemento']}: Solicitado {item['solicitado']}, Disponible {item['disponible']}, Faltante {item['faltante']}\n"
                return False, mensaje, stock_actual
            
            return True, "Stock suficiente para la operación", stock_actual
            
        except Exception as e:
            return False, f"Error validando stock: {e}", {}
    
    def validar_integridad_operacion(self, tipo_operacion, id_codigo_consumidor, items_dict):
        """Validación completa de integridad para una operación"""
        print(f"\n=== VALIDANDO {tipo_operacion.upper()} ===")
        print(f"ID Código Consumidor: {id_codigo_consumidor}")
        print(f"Items: {items_dict}")
        
        # 1. Validar duplicados
        if tipo_operacion == 'asignacion':
            es_valido, mensaje = self.validar_duplicado_asignacion(id_codigo_consumidor, items_dict)
        else:
            es_valido, mensaje = self.validar_duplicado_cambio(id_codigo_consumidor, items_dict)
        
        if not es_valido:
            print(f"❌ Validación de duplicados: {mensaje}")
            return False, mensaje
        
        print(f"✅ Validación de duplicados: {mensaje}")
        
        # 2. Validar stock disponible
        stock_valido, stock_mensaje, stock_actual = self.validar_stock_disponible(items_dict)
        
        if not stock_valido:
            print(f"❌ Validación de stock: {stock_mensaje}")
            return False, stock_mensaje
        
        print(f"✅ Validación de stock: {stock_mensaje}")
        
        # 3. Generar hash de operación para logging
        hash_operacion = self.generar_hash_operacion(tipo_operacion, id_codigo_consumidor, items_dict)
        print(f"🔐 Hash de operación: {hash_operacion}")
        
        return True, {
            'mensaje': 'Validación completa exitosa',
            'hash_operacion': hash_operacion,
            'stock_actual': stock_actual
        }
    
    def crear_log_validacion(self, tipo_operacion, id_codigo_consumidor, items_dict, resultado_validacion):
        """Crear log de la validación realizada"""
        if not self.conexion:
            return False
        
        try:
            cursor = self.conexion.cursor()
            
            # Crear tabla de logs si no existe
            crear_tabla_log = """
                CREATE TABLE IF NOT EXISTS logs_validacion_dotaciones (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tipo_operacion VARCHAR(50) NOT NULL,
                    id_codigo_consumidor INT NOT NULL,
                    items_json TEXT,
                    hash_operacion VARCHAR(32),
                    resultado_validacion TEXT,
                    fecha_validacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_codigo_fecha (id_codigo_consumidor, fecha_validacion),
                    INDEX idx_hash (hash_operacion)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
            
            cursor.execute(crear_tabla_log)
            
            # Insertar log
            import json
            items_json = json.dumps(items_dict)
            resultado_json = json.dumps(resultado_validacion) if isinstance(resultado_validacion, dict) else str(resultado_validacion)
            
            hash_operacion = self.generar_hash_operacion(tipo_operacion, id_codigo_consumidor, items_dict)
            
            insertar_log = """
                INSERT INTO logs_validacion_dotaciones 
                (tipo_operacion, id_codigo_consumidor, items_json, hash_operacion, resultado_validacion)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.execute(insertar_log, (
                tipo_operacion,
                id_codigo_consumidor,
                items_json,
                hash_operacion,
                resultado_json
            ))
            
            self.conexion.commit()
            cursor.close()
            
            print(f"📝 Log de validación creado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error creando log: {e}")
            return False
    
    def cerrar_conexion(self):
        """Cerrar conexión a la base de datos"""
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
            print("✅ Conexión cerrada")

def test_validaciones():
    """Función de prueba para las validaciones"""
    validador = ValidadorDotaciones()
    
    if not validador.conexion:
        print("❌ No se pudo establecer conexión con la base de datos")
        return
    
    # Datos de prueba
    id_codigo_consumidor_test = 1
    items_test = {
        'pantalon': 2,
        'camisetagris': 1,
        'guerrera': 0,
        'camisetapolo': 0,
        'botas': 1,
        'guantes_nitrilo': 0,
        'guantes_carnaza': 0,
        'gafas': 0,
        'gorra': 0,
        'casco': 0
    }
    
    print("\n=== PRUEBA DE VALIDACIONES ===")
    
    # Probar validación de asignación
    resultado_asignacion = validador.validar_integridad_operacion('asignacion', id_codigo_consumidor_test, items_test)
    print(f"\nResultado asignación: {resultado_asignacion}")
    
    # Probar validación de cambio
    resultado_cambio = validador.validar_integridad_operacion('cambio', id_codigo_consumidor_test, items_test)
    print(f"\nResultado cambio: {resultado_cambio}")
    
    # Crear logs
    validador.crear_log_validacion('asignacion', id_codigo_consumidor_test, items_test, resultado_asignacion)
    validador.crear_log_validacion('cambio', id_codigo_consumidor_test, items_test, resultado_cambio)
    
    validador.cerrar_conexion()

if __name__ == "__main__":
    test_validaciones()