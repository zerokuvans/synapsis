#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para validar diferencias entre local y producción
en el cálculo de stock de dotaciones.

Este script ayuda a identificar por qué el cálculo funciona en local pero no en producción.
"""

import mysql.connector
import os
import json
from datetime import datetime
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('diagnostico_stock.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DiagnosticoStock:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'synapsis'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
        self.connection = None
        self.resultados = {
            'timestamp': datetime.now().isoformat(),
            'configuracion_db': {},
            'conectividad': False,
            'tablas_existentes': {},
            'vista_stock_dotaciones': {},
            'datos_muestra': {},
            'calculo_stock': {},
            'errores': []
        }
    
    def conectar_db(self):
        """Intenta conectar a la base de datos"""
        try:
            logger.info("Intentando conectar a la base de datos...")
            self.connection = mysql.connector.connect(**self.db_config)
            self.resultados['conectividad'] = True
            logger.info("✓ Conexión exitosa a la base de datos")
            return True
        except mysql.connector.Error as e:
            error_msg = f"Error de conexión a la base de datos: {e}"
            logger.error(error_msg)
            self.resultados['errores'].append(error_msg)
            self.resultados['conectividad'] = False
            return False
    
    def verificar_configuracion(self):
        """Verifica la configuración de la base de datos"""
        logger.info("Verificando configuración de base de datos...")
        
        # Ocultar password en los resultados
        config_segura = self.db_config.copy()
        config_segura['password'] = '***' if config_segura['password'] else 'NO_PASSWORD'
        
        self.resultados['configuracion_db'] = config_segura
        
        # Verificar variables de entorno
        variables_env = {
            'DB_HOST': os.getenv('DB_HOST'),
            'DB_PORT': os.getenv('DB_PORT'),
            'DB_USER': os.getenv('DB_USER'),
            'DB_PASSWORD': '***' if os.getenv('DB_PASSWORD') else None,
            'DB_NAME': os.getenv('DB_NAME')
        }
        
        self.resultados['configuracion_db']['variables_entorno'] = variables_env
        
        logger.info(f"Host: {config_segura['host']}")
        logger.info(f"Puerto: {config_segura['port']}")
        logger.info(f"Usuario: {config_segura['user']}")
        logger.info(f"Base de datos: {config_segura['database']}")
    
    def verificar_tablas(self):
        """Verifica que las tablas necesarias existan"""
        if not self.connection:
            return
        
        logger.info("Verificando existencia de tablas...")
        cursor = self.connection.cursor(dictionary=True)
        
        tablas_requeridas = ['stock_ferretero', 'dotaciones', 'cambios_dotacion']
        
        for tabla in tablas_requeridas:
            try:
                # Verificar si la tabla existe
                cursor.execute(f"SHOW TABLES LIKE '{tabla}'")
                existe = cursor.fetchone() is not None
                
                if existe:
                    # Obtener estructura de la tabla
                    cursor.execute(f"DESCRIBE {tabla}")
                    estructura = cursor.fetchall()
                    
                    # Contar registros
                    cursor.execute(f"SELECT COUNT(*) as total FROM {tabla}")
                    total_registros = cursor.fetchone()['total']
                    
                    self.resultados['tablas_existentes'][tabla] = {
                        'existe': True,
                        'total_registros': total_registros,
                        'estructura': estructura
                    }
                    
                    logger.info(f"✓ Tabla {tabla}: {total_registros} registros")
                else:
                    self.resultados['tablas_existentes'][tabla] = {
                        'existe': False,
                        'total_registros': 0,
                        'estructura': []
                    }
                    error_msg = f"✗ Tabla {tabla} no existe"
                    logger.error(error_msg)
                    self.resultados['errores'].append(error_msg)
                    
            except mysql.connector.Error as e:
                error_msg = f"Error verificando tabla {tabla}: {e}"
                logger.error(error_msg)
                self.resultados['errores'].append(error_msg)
    
    def verificar_vista_stock(self):
        """Verifica la vista vista_stock_dotaciones"""
        if not self.connection:
            return
        
        logger.info("Verificando vista vista_stock_dotaciones...")
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            # Verificar si la vista existe
            cursor.execute("SHOW TABLES LIKE 'vista_stock_dotaciones'")
            existe_vista = cursor.fetchone() is not None
            
            if existe_vista:
                # Obtener definición de la vista
                cursor.execute("SHOW CREATE VIEW vista_stock_dotaciones")
                definicion = cursor.fetchone()
                
                # Probar consulta a la vista
                cursor.execute("SELECT * FROM vista_stock_dotaciones LIMIT 5")
                muestra_datos = cursor.fetchall()
                
                self.resultados['vista_stock_dotaciones'] = {
                    'existe': True,
                    'definicion': definicion['Create View'] if definicion else None,
                    'muestra_datos': muestra_datos,
                    'total_registros': len(muestra_datos)
                }
                
                logger.info(f"✓ Vista vista_stock_dotaciones existe con {len(muestra_datos)} registros de muestra")
            else:
                self.resultados['vista_stock_dotaciones'] = {
                    'existe': False,
                    'definicion': None,
                    'muestra_datos': [],
                    'total_registros': 0
                }
                error_msg = "✗ Vista vista_stock_dotaciones no existe"
                logger.error(error_msg)
                self.resultados['errores'].append(error_msg)
                
        except mysql.connector.Error as e:
            error_msg = f"Error verificando vista vista_stock_dotaciones: {e}"
            logger.error(error_msg)
            self.resultados['errores'].append(error_msg)
    
    def obtener_datos_muestra(self):
        """Obtiene datos de muestra para análisis"""
        if not self.connection:
            return
        
        logger.info("Obteniendo datos de muestra...")
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            # Muestra de stock_ferretero
            cursor.execute("SELECT * FROM stock_ferretero LIMIT 3")
            self.resultados['datos_muestra']['stock_ferretero'] = cursor.fetchall()
            
            # Muestra de dotaciones
            cursor.execute("SELECT * FROM dotaciones LIMIT 3")
            self.resultados['datos_muestra']['dotaciones'] = cursor.fetchall()
            
            # Muestra de cambios_dotacion
            cursor.execute("SELECT * FROM cambios_dotacion LIMIT 3")
            self.resultados['datos_muestra']['cambios_dotacion'] = cursor.fetchall()
            
            # Materiales únicos
            cursor.execute("SELECT DISTINCT material_tipo FROM stock_ferretero ORDER BY material_tipo")
            materiales = cursor.fetchall()
            self.resultados['datos_muestra']['materiales_unicos'] = [m['material_tipo'] for m in materiales]
            
            logger.info(f"✓ Datos de muestra obtenidos: {len(materiales)} materiales únicos")
            
        except mysql.connector.Error as e:
            error_msg = f"Error obteniendo datos de muestra: {e}"
            logger.error(error_msg)
            self.resultados['errores'].append(error_msg)
    
    def probar_calculo_stock(self):
        """Prueba el cálculo de stock para un material específico"""
        if not self.connection:
            return
        
        logger.info("Probando cálculo de stock...")
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            # Obtener un material para probar
            cursor.execute("SELECT DISTINCT material_tipo FROM stock_ferretero LIMIT 1")
            material_test = cursor.fetchone()
            
            if not material_test:
                error_msg = "No hay materiales en stock_ferretero para probar"
                logger.error(error_msg)
                self.resultados['errores'].append(error_msg)
                return
            
            material = material_test['material_tipo']
            logger.info(f"Probando cálculo para material: {material}")
            
            # Stock inicial
            cursor.execute("""
                SELECT COALESCE(SUM(cantidad_disponible), 0) as stock_inicial
                FROM stock_ferretero 
                WHERE material_tipo = %s
            """, (material,))
            stock_inicial = cursor.fetchone()['stock_inicial']
            
            # Asignaciones
            cursor.execute(f"""
                SELECT COALESCE(SUM(
                    CASE 
                        WHEN %s = 'pantalon' THEN pantalon
                        WHEN %s = 'camisetagris' THEN camisetagris
                        WHEN %s = 'guerrera' THEN guerrera
                        WHEN %s = 'camisetapolo' THEN camisetapolo
                        WHEN %s = 'guantes_nitrilo' THEN guantes_nitrilo
                        WHEN %s = 'guantes_carnaza' THEN guantes_carnaza
                        WHEN %s = 'gafas' THEN gafas
                        WHEN %s = 'gorra' THEN gorra
                        WHEN %s = 'casco' THEN casco
                        WHEN %s = 'botas' THEN botas
                        ELSE 0
                    END
                ), 0) as total_asignaciones
                FROM dotaciones
            """, (material,) * 10)
            total_asignaciones = cursor.fetchone()['total_asignaciones']
            
            # Cambios
            cursor.execute(f"""
                SELECT COALESCE(SUM(
                    CASE 
                        WHEN %s = 'pantalon' THEN pantalon
                        WHEN %s = 'camisetagris' THEN camisetagris
                        WHEN %s = 'guerrera' THEN guerrera
                        WHEN %s = 'camisetapolo' THEN camisetapolo
                        WHEN %s = 'guantes_nitrilo' THEN guantes_nitrilo
                        WHEN %s = 'guantes_carnaza' THEN guantes_carnaza
                        WHEN %s = 'gafas' THEN gafas
                        WHEN %s = 'gorra' THEN gorra
                        WHEN %s = 'casco' THEN casco
                        WHEN %s = 'botas' THEN botas
                        ELSE 0
                    END
                ), 0) as total_cambios
                FROM cambios_dotacion
            """, (material,) * 10)
            total_cambios = cursor.fetchone()['total_cambios']
            
            # Cálculo final
            stock_actual = stock_inicial - total_asignaciones - total_cambios
            
            self.resultados['calculo_stock'] = {
                'material_prueba': material,
                'stock_inicial': stock_inicial,
                'total_asignaciones': total_asignaciones,
                'total_cambios': total_cambios,
                'stock_actual': stock_actual,
                'formula': f"{stock_inicial} - {total_asignaciones} - {total_cambios} = {stock_actual}"
            }
            
            logger.info(f"✓ Cálculo de stock para {material}: {stock_inicial} - {total_asignaciones} - {total_cambios} = {stock_actual}")
            
        except mysql.connector.Error as e:
            error_msg = f"Error en cálculo de stock: {e}"
            logger.error(error_msg)
            self.resultados['errores'].append(error_msg)
    
    def generar_reporte(self):
        """Genera el reporte final"""
        logger.info("Generando reporte de diagnóstico...")
        
        # Guardar resultados en JSON
        with open('diagnostico_stock_resultado.json', 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False, default=str)
        
        # Resumen en consola
        print("\n" + "="*60)
        print("RESUMEN DEL DIAGNÓSTICO DE STOCK")
        print("="*60)
        
        print(f"\n🔧 CONFIGURACIÓN:")
        print(f"   Host: {self.resultados['configuracion_db']['host']}")
        print(f"   Puerto: {self.resultados['configuracion_db']['port']}")
        print(f"   Base de datos: {self.resultados['configuracion_db']['database']}")
        
        print(f"\n🔌 CONECTIVIDAD: {'✓ OK' if self.resultados['conectividad'] else '✗ FALLO'}")
        
        print(f"\n📊 TABLAS:")
        for tabla, info in self.resultados['tablas_existentes'].items():
            status = "✓" if info['existe'] else "✗"
            registros = info['total_registros'] if info['existe'] else 0
            print(f"   {status} {tabla}: {registros} registros")
        
        print(f"\n👁️ VISTA STOCK: {'✓ OK' if self.resultados['vista_stock_dotaciones'].get('existe') else '✗ NO EXISTE'}")
        
        if self.resultados['calculo_stock']:
            calc = self.resultados['calculo_stock']
            print(f"\n🧮 CÁLCULO DE PRUEBA:")
            print(f"   Material: {calc['material_prueba']}")
            print(f"   Fórmula: {calc['formula']}")
        
        if self.resultados['errores']:
            print(f"\n❌ ERRORES ENCONTRADOS ({len(self.resultados['errores'])}):"))
            for i, error in enumerate(self.resultados['errores'], 1):
                print(f"   {i}. {error}")
        else:
            print(f"\n✅ NO SE ENCONTRARON ERRORES")
        
        print(f"\n📄 Reporte completo guardado en: diagnostico_stock_resultado.json")
        print(f"📄 Log detallado guardado en: diagnostico_stock.log")
        print("="*60)
    
    def ejecutar_diagnostico(self):
        """Ejecuta el diagnóstico completo"""
        logger.info("Iniciando diagnóstico de stock de dotaciones...")
        
        self.verificar_configuracion()
        
        if self.conectar_db():
            self.verificar_tablas()
            self.verificar_vista_stock()
            self.obtener_datos_muestra()
            self.probar_calculo_stock()
        
        self.generar_reporte()
        
        if self.connection:
            self.connection.close()
        
        logger.info("Diagnóstico completado")

if __name__ == '__main__':
    diagnostico = DiagnosticoStock()
    diagnostico.ejecutar_diagnostico()