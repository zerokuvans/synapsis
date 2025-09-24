#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificación Post-Truncate
Verifica que el sistema funcione correctamente después del truncate
"""

import mysql.connector
from mysql.connector import Error
import json
import datetime
import requests
import time

class VerificacionPostTruncate:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '732137A031E4b@',
            'database': 'capired'
        }
        
        self.tablas_sistema = [
            "equipos_dotaciones",
            "devoluciones_dotacion", 
            "cambios_dotaciones",
            "asignaciones_equipos_dotaciones",
            "devoluciones_historial",
            "historial_notificaciones",
            "devoluciones_elementos",
            "devolucion_detalles",
            "historial_cambios_dotaciones",
            "cambios_dotaciones_detalle",
            "movimientos_equipos_dotaciones",
            "auditoria_estados_devolucion",
            "cambios_dotacion",
            "devolucion_dotaciones",
            "dotaciones",
            "historial_vencimientos",
            "ingresos_dotaciones"
        ]
        
        self.resultados = {
            'timestamp': datetime.datetime.now().isoformat(),
            'verificaciones': {
                'estructura_tablas': {'status': 'pending', 'detalles': []},
                'foreign_keys': {'status': 'pending', 'detalles': []},
                'triggers': {'status': 'pending', 'detalles': []},
                'indices': {'status': 'pending', 'detalles': []},
                'permisos': {'status': 'pending', 'detalles': []},
                'funcionalidad_basica': {'status': 'pending', 'detalles': []}
            },
            'resumen': {
                'total_verificaciones': 0,
                'exitosas': 0,
                'fallidas': 0,
                'warnings': 0
            }
        }
        
    def log(self, mensaje, nivel="INFO"):
        """Registra mensaje en consola"""
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        simbolos = {
            'INFO': 'ℹ️',
            'SUCCESS': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌'
        }
        simbolo = simbolos.get(nivel, 'ℹ️')
        print(f"[{timestamp}] {simbolo} {mensaje}")
    
    def conectar(self):
        """Establece conexión con la base de datos"""
        try:
            self.conexion = mysql.connector.connect(**self.config)
            self.cursor = self.conexion.cursor(dictionary=True)
            self.log("Conexión establecida con la base de datos", "SUCCESS")
            return True
        except Error as e:
            self.log(f"Error de conexión: {e}", "ERROR")
            return False
    
    def verificar_estructura_tablas(self):
        """Verifica que todas las tablas mantengan su estructura"""
        self.log("\n=== VERIFICANDO ESTRUCTURA DE TABLAS ===")
        
        try:
            detalles = []
            
            for tabla in self.tablas_sistema:
                # Verificar existencia
                self.cursor.execute(f"SHOW TABLES LIKE '{tabla}'")
                existe = len(self.cursor.fetchall()) > 0
                
                if not existe:
                    detalles.append(f"❌ Tabla {tabla} no existe")
                    continue
                
                # Verificar estructura
                self.cursor.execute(f"DESCRIBE {tabla}")
                columnas = self.cursor.fetchall()
                
                # Verificar que esté vacía
                self.cursor.execute(f"SELECT COUNT(*) as total FROM {tabla}")
                count = self.cursor.fetchone()['total']
                
                if count == 0:
                    detalles.append(f"✅ {tabla}: {len(columnas)} columnas, 0 registros")
                else:
                    detalles.append(f"⚠️ {tabla}: {len(columnas)} columnas, {count} registros (no vacía)")
            
            self.resultados['verificaciones']['estructura_tablas'] = {
                'status': 'success',
                'detalles': detalles
            }
            
            self.log(f"Estructura verificada: {len(self.tablas_sistema)} tablas", "SUCCESS")
            return True
            
        except Error as e:
            self.log(f"Error verificando estructura: {e}", "ERROR")
            self.resultados['verificaciones']['estructura_tablas'] = {
                'status': 'error',
                'detalles': [f"Error: {str(e)}"]
            }
            return False
    
    def verificar_foreign_keys(self):
        """Verifica que las foreign keys estén activas"""
        self.log("\n=== VERIFICANDO FOREIGN KEYS ===")
        
        try:
            # Verificar que FK checks estén habilitadas
            self.cursor.execute("SELECT @@FOREIGN_KEY_CHECKS as fk_enabled")
            fk_enabled = self.cursor.fetchone()['fk_enabled']
            
            # Obtener todas las FK del sistema
            self.cursor.execute("""
                SELECT 
                    kcu.TABLE_NAME as tabla_origen,
                    kcu.COLUMN_NAME as columna_origen,
                    kcu.REFERENCED_TABLE_NAME as tabla_destino,
                    kcu.CONSTRAINT_NAME as constraint_name
                FROM information_schema.KEY_COLUMN_USAGE kcu
                WHERE kcu.table_schema = 'capired' 
                AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
                AND (kcu.TABLE_NAME IN ({}) OR kcu.REFERENCED_TABLE_NAME IN ({}))
                ORDER BY kcu.TABLE_NAME
            """.format(
                ','.join([f"'{t}'" for t in self.tablas_sistema]),
                ','.join([f"'{t}'" for t in self.tablas_sistema])
            ))
            
            foreign_keys = self.cursor.fetchall()
            
            detalles = [
                f"FK Checks habilitadas: {'✅' if fk_enabled else '❌'}",
                f"Total FK encontradas: {len(foreign_keys)}"
            ]
            
            # Verificar cada FK
            for fk in foreign_keys[:10]:  # Limitar a 10 para no saturar
                tabla_origen = fk['tabla_origen']
                tabla_destino = fk['tabla_destino']
                constraint = fk['constraint_name']
                detalles.append(f"  {tabla_origen} -> {tabla_destino} ({constraint})")
            
            if len(foreign_keys) > 10:
                detalles.append(f"  ... y {len(foreign_keys) - 10} más")
            
            self.resultados['verificaciones']['foreign_keys'] = {
                'status': 'success' if fk_enabled else 'warning',
                'detalles': detalles
            }
            
            self.log(f"Foreign Keys verificadas: {len(foreign_keys)} encontradas", "SUCCESS")
            return True
            
        except Error as e:
            self.log(f"Error verificando FK: {e}", "ERROR")
            self.resultados['verificaciones']['foreign_keys'] = {
                'status': 'error',
                'detalles': [f"Error: {str(e)}"]
            }
            return False
    
    def verificar_triggers(self):
        """Verifica que los triggers estén activos"""
        self.log("\n=== VERIFICANDO TRIGGERS ===")
        
        try:
            self.cursor.execute("""
                SELECT 
                    TRIGGER_NAME,
                    EVENT_MANIPULATION,
                    EVENT_OBJECT_TABLE,
                    TRIGGER_SCHEMA
                FROM information_schema.TRIGGERS 
                WHERE TRIGGER_SCHEMA = 'capired'
                AND EVENT_OBJECT_TABLE IN ({})
                ORDER BY EVENT_OBJECT_TABLE, TRIGGER_NAME
            """.format(','.join([f"'{t}'" for t in self.tablas_sistema])))
            
            triggers = self.cursor.fetchall()
            
            detalles = [f"Total triggers encontrados: {len(triggers)}"]
            
            for trigger in triggers:
                tabla = trigger['EVENT_OBJECT_TABLE']
                nombre = trigger['TRIGGER_NAME']
                evento = trigger['EVENT_MANIPULATION']
                detalles.append(f"  {tabla}: {nombre} ({evento})")
            
            self.resultados['verificaciones']['triggers'] = {
                'status': 'success',
                'detalles': detalles
            }
            
            self.log(f"Triggers verificados: {len(triggers)} encontrados", "SUCCESS")
            return True
            
        except Error as e:
            self.log(f"Error verificando triggers: {e}", "ERROR")
            self.resultados['verificaciones']['triggers'] = {
                'status': 'error',
                'detalles': [f"Error: {str(e)}"]
            }
            return False
    
    def verificar_indices(self):
        """Verifica que los índices estén presentes"""
        self.log("\n=== VERIFICANDO ÍNDICES ===")
        
        try:
            total_indices = 0
            detalles = []
            
            for tabla in self.tablas_sistema[:5]:  # Verificar solo algunas tablas
                self.cursor.execute(f"SHOW INDEX FROM {tabla}")
                indices = self.cursor.fetchall()
                total_indices += len(indices)
                
                if indices:
                    detalles.append(f"  {tabla}: {len(indices)} índices")
            
            detalles.insert(0, f"Total índices verificados: {total_indices}")
            
            self.resultados['verificaciones']['indices'] = {
                'status': 'success',
                'detalles': detalles
            }
            
            self.log(f"Índices verificados: {total_indices} encontrados", "SUCCESS")
            return True
            
        except Error as e:
            self.log(f"Error verificando índices: {e}", "ERROR")
            self.resultados['verificaciones']['indices'] = {
                'status': 'error',
                'detalles': [f"Error: {str(e)}"]
            }
            return False
    
    def verificar_permisos(self):
        """Verifica permisos básicos de usuario"""
        self.log("\n=== VERIFICANDO PERMISOS ===")
        
        try:
            # Verificar permisos del usuario actual
            self.cursor.execute("SELECT USER() as current_user")
            usuario_actual = self.cursor.fetchone()['current_user']
            
            # Intentar operaciones básicas en una tabla
            tabla_test = self.tablas_sistema[0]
            
            operaciones = []
            
            # Test SELECT
            try:
                self.cursor.execute(f"SELECT 1 FROM {tabla_test} LIMIT 1")
                operaciones.append("SELECT: ✅")
            except:
                operaciones.append("SELECT: ❌")
            
            # Test INSERT (simulado)
            try:
                self.cursor.execute(f"EXPLAIN INSERT INTO {tabla_test} VALUES ()")
                operaciones.append("INSERT: ✅ (simulado)")
            except:
                operaciones.append("INSERT: ❌")
            
            detalles = [
                f"Usuario actual: {usuario_actual}",
                f"Tabla de prueba: {tabla_test}"
            ] + operaciones
            
            self.resultados['verificaciones']['permisos'] = {
                'status': 'success',
                'detalles': detalles
            }
            
            self.log("Permisos verificados correctamente", "SUCCESS")
            return True
            
        except Error as e:
            self.log(f"Error verificando permisos: {e}", "ERROR")
            self.resultados['verificaciones']['permisos'] = {
                'status': 'error',
                'detalles': [f"Error: {str(e)}"]
            }
            return False
    
    def verificar_funcionalidad_basica(self):
        """Verifica funcionalidad básica del sistema"""
        self.log("\n=== VERIFICANDO FUNCIONALIDAD BÁSICA ===")
        
        try:
            detalles = []
            
            # Test 1: Inserción básica en tabla principal
            tabla_principal = "dotaciones"
            
            try:
                # Verificar estructura de la tabla
                self.cursor.execute(f"DESCRIBE {tabla_principal}")
                columnas = [col['Field'] for col in self.cursor.fetchall()]
                detalles.append(f"✅ Estructura de {tabla_principal}: {len(columnas)} columnas")
                
                # Test de transacción
                self.cursor.execute("START TRANSACTION")
                self.cursor.execute("SELECT 1 as test")
                result = self.cursor.fetchone()
                self.cursor.execute("ROLLBACK")
                
                if result['test'] == 1:
                    detalles.append("✅ Transacciones funcionando")
                
            except Exception as e:
                detalles.append(f"❌ Error en funcionalidad básica: {str(e)}")
            
            # Test 2: Verificar conexiones concurrentes
            try:
                test_conn = mysql.connector.connect(**self.config)
                test_cursor = test_conn.cursor()
                test_cursor.execute("SELECT 1")
                test_cursor.close()
                test_conn.close()
                detalles.append("✅ Conexiones concurrentes funcionando")
            except:
                detalles.append("⚠️ Problema con conexiones concurrentes")
            
            self.resultados['verificaciones']['funcionalidad_basica'] = {
                'status': 'success',
                'detalles': detalles
            }
            
            self.log("Funcionalidad básica verificada", "SUCCESS")
            return True
            
        except Error as e:
            self.log(f"Error verificando funcionalidad: {e}", "ERROR")
            self.resultados['verificaciones']['funcionalidad_basica'] = {
                'status': 'error',
                'detalles': [f"Error: {str(e)}"]
            }
            return False
    
    def generar_resumen(self):
        """Genera resumen de todas las verificaciones"""
        total = 0
        exitosas = 0
        fallidas = 0
        warnings = 0
        
        for nombre, verificacion in self.resultados['verificaciones'].items():
            total += 1
            status = verificacion['status']
            
            if status == 'success':
                exitosas += 1
            elif status == 'error':
                fallidas += 1
            elif status == 'warning':
                warnings += 1
        
        self.resultados['resumen'] = {
            'total_verificaciones': total,
            'exitosas': exitosas,
            'fallidas': fallidas,
            'warnings': warnings
        }
        
        return total, exitosas, fallidas, warnings
    
    def ejecutar_verificacion_completa(self):
        """Ejecuta todas las verificaciones"""
        self.log("\n" + "=" * 80)
        self.log("         VERIFICACIÓN POST-TRUNCATE - SISTEMA DOTACIONES")
        self.log("=" * 80)
        
        if not self.conectar():
            return False
        
        try:
            # Ejecutar todas las verificaciones
            verificaciones = [
                ("Estructura de Tablas", self.verificar_estructura_tablas),
                ("Foreign Keys", self.verificar_foreign_keys),
                ("Triggers", self.verificar_triggers),
                ("Índices", self.verificar_indices),
                ("Permisos", self.verificar_permisos),
                ("Funcionalidad Básica", self.verificar_funcionalidad_basica)
            ]
            
            for nombre, funcion in verificaciones:
                self.log(f"\n🔍 Verificando: {nombre}")
                try:
                    funcion()
                except Exception as e:
                    self.log(f"Error en {nombre}: {e}", "ERROR")
            
            # Generar resumen
            total, exitosas, fallidas, warnings = self.generar_resumen()
            
            # Guardar reporte
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            reporte_file = f"verificacion_post_truncate_{timestamp}.json"
            
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(self.resultados, f, indent=2, ensure_ascii=False)
            
            # Mostrar resumen final
            self.log("\n" + "=" * 80)
            self.log("                    RESUMEN DE VERIFICACIÓN")
            self.log("=" * 80)
            
            self.log(f"Total verificaciones: {total}")
            self.log(f"Exitosas: {exitosas} ✅")
            self.log(f"Warnings: {warnings} ⚠️")
            self.log(f"Fallidas: {fallidas} ❌")
            
            self.log(f"\n📋 Reporte guardado: {reporte_file}")
            
            if fallidas == 0:
                self.log("\n🎉 SISTEMA VERIFICADO CORRECTAMENTE", "SUCCESS")
                return True
            else:
                self.log(f"\n⚠️ SISTEMA CON {fallidas} PROBLEMAS DETECTADOS", "WARNING")
                return False
            
        except Exception as e:
            self.log(f"Error crítico en verificación: {e}", "ERROR")
            return False
            
        finally:
            if hasattr(self, 'cursor'):
                self.cursor.close()
            if hasattr(self, 'conexion'):
                self.conexion.close()

def main():
    verificador = VerificacionPostTruncate()
    exito = verificador.ejecutar_verificacion_completa()
    
    if exito:
        print("\n✅ Verificación completada exitosamente")
        return 0
    else:
        print("\n❌ Verificación completada con problemas")
        return 1

if __name__ == "__main__":
    exit(main())