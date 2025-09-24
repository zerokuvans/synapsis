#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Truncate Seguro para Sistema de Dotaciones
Realiza truncate de tablas manteniendo integridad referencial
"""

import mysql.connector
from mysql.connector import Error
import json
import os
import datetime
import subprocess
import sys
from pathlib import Path

class TruncateSeguroSistema:
    def __init__(self, modo_prueba=True):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '732137A031E4b@',
            'database': 'capired'
        }
        self.modo_prueba = modo_prueba
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Orden de truncate basado en análisis de FK
        self.orden_truncate = [
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
        
        # Mapeo de nombres de usuario a nombres reales de tabla
        self.mapeo_tablas = {
            "tabla_dotaciones": "dotaciones",
            "tabla_cambios": "cambios_dotacion",
            "tabla_devoluciones": "devolucion_dotaciones", 
            "tabla_historial": "historial_vencimientos",
            "tabla_temporales": "ingresos_dotaciones"
        }
        
        self.log_file = f"truncate_log_{self.timestamp}.txt"
        self.backup_file = f"backup_pre_truncate_{self.timestamp}.sql"
        self.resultados = {
            'inicio': None,
            'fin': None,
            'modo_prueba': modo_prueba,
            'backup_realizado': False,
            'tablas_procesadas': [],
            'errores': [],
            'warnings': [],
            'registros_eliminados': {},
            'tiempo_total': None
        }
        
    def log(self, mensaje, nivel="INFO"):
        """Registra mensaje en log y consola"""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] [{nivel}] {mensaje}"
        
        print(log_msg)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_msg + '\n')
        except Exception as e:
            print(f"Error escribiendo log: {e}")
    
    def conectar(self):
        """Establece conexión con la base de datos"""
        try:
            self.conexion = mysql.connector.connect(**self.config)
            self.cursor = self.conexion.cursor(dictionary=True)
            self.conexion.autocommit = False  # Control manual de transacciones
            self.log("✅ Conexión establecida con la base de datos")
            return True
        except Error as e:
            self.log(f"❌ Error de conexión: {e}", "ERROR")
            return False
    
    def verificar_tablas_existen(self):
        """Verifica que todas las tablas del sistema existan"""
        self.log("\n=== VERIFICANDO EXISTENCIA DE TABLAS ===")
        
        try:
            self.cursor.execute("SHOW TABLES")
            tablas_existentes = {row['Tables_in_capired'] for row in self.cursor.fetchall()}
            
            tablas_faltantes = []
            for tabla in self.orden_truncate:
                if tabla not in tablas_existentes:
                    tablas_faltantes.append(tabla)
            
            if tablas_faltantes:
                self.log(f"❌ Tablas faltantes: {tablas_faltantes}", "ERROR")
                return False
            
            self.log(f"✅ Todas las {len(self.orden_truncate)} tablas existen")
            return True
            
        except Error as e:
            self.log(f"❌ Error verificando tablas: {e}", "ERROR")
            return False
    
    def contar_registros_pre_truncate(self):
        """Cuenta registros antes del truncate"""
        self.log("\n=== CONTANDO REGISTROS PRE-TRUNCATE ===")
        
        conteos = {}
        total_registros = 0
        
        try:
            for tabla in self.orden_truncate:
                self.cursor.execute(f"SELECT COUNT(*) as total FROM {tabla}")
                count = self.cursor.fetchone()['total']
                conteos[tabla] = count
                total_registros += count
                
                if count > 0:
                    self.log(f"📊 {tabla}: {count:,} registros")
            
            self.log(f"\n📈 TOTAL DE REGISTROS: {total_registros:,}")
            
            if total_registros == 0:
                self.log("⚠️ No hay registros para eliminar", "WARNING")
                return conteos, False
            
            return conteos, True
            
        except Error as e:
            self.log(f"❌ Error contando registros: {e}", "ERROR")
            return {}, False
    
    def crear_backup_completo(self):
        """Crea backup completo de la base de datos"""
        self.log("\n=== CREANDO BACKUP COMPLETO ===")
        
        try:
            backup_cmd = [
                'mysqldump',
                '-h', self.config['host'],
                '-u', self.config['user'],
                f'-p{self.config["password"]}',
                '--single-transaction',
                '--routines',
                '--triggers',
                '--events',
                '--complete-insert',
                '--add-drop-table',
                self.config['database']
            ]
            
            self.log(f"🔄 Ejecutando backup a: {self.backup_file}")
            
            with open(self.backup_file, 'w', encoding='utf-8') as f:
                result = subprocess.run(
                    backup_cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
            
            # Verificar tamaño del backup
            backup_size = os.path.getsize(self.backup_file)
            self.log(f"✅ Backup creado: {backup_size:,} bytes")
            
            self.resultados['backup_realizado'] = True
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Error en mysqldump: {e.stderr}", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Error creando backup: {e}", "ERROR")
            return False
    
    def deshabilitar_foreign_keys(self):
        """Deshabilita temporalmente las foreign keys"""
        try:
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            self.log("🔓 Foreign key checks deshabilitadas")
            return True
        except Error as e:
            self.log(f"❌ Error deshabilitando FK: {e}", "ERROR")
            return False
    
    def habilitar_foreign_keys(self):
        """Rehabilita las foreign keys"""
        try:
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            self.log("🔒 Foreign key checks habilitadas")
            return True
        except Error as e:
            self.log(f"❌ Error habilitando FK: {e}", "ERROR")
            return False
    
    def truncate_tabla(self, tabla):
        """Trunca una tabla específica"""
        try:
            if self.modo_prueba:
                # En modo prueba, solo simular
                self.cursor.execute(f"SELECT COUNT(*) as total FROM {tabla}")
                count = self.cursor.fetchone()['total']
                self.log(f"🧪 [SIMULACIÓN] TRUNCATE {tabla} - {count} registros")
                self.resultados['registros_eliminados'][tabla] = count
                return True, count
            else:
                # Contar antes de truncar
                self.cursor.execute(f"SELECT COUNT(*) as total FROM {tabla}")
                count = self.cursor.fetchone()['total']
                
                # Ejecutar truncate real
                self.cursor.execute(f"TRUNCATE TABLE {tabla}")
                self.log(f"✂️ TRUNCATE {tabla} - {count} registros eliminados")
                self.resultados['registros_eliminados'][tabla] = count
                return True, count
                
        except Error as e:
            self.log(f"❌ Error truncando {tabla}: {e}", "ERROR")
            self.resultados['errores'].append({
                'tabla': tabla,
                'error': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            })
            return False, 0
    
    def ejecutar_truncate_secuencial(self):
        """Ejecuta truncate en el orden correcto"""
        modo_texto = "SIMULACIÓN" if self.modo_prueba else "EJECUCIÓN REAL"
        self.log(f"\n=== INICIANDO TRUNCATE - {modo_texto} ===")
        
        if not self.deshabilitar_foreign_keys():
            return False
        
        try:
            self.conexion.start_transaction()
            
            total_eliminados = 0
            tablas_exitosas = 0
            
            for i, tabla in enumerate(self.orden_truncate, 1):
                self.log(f"\n[{i}/{len(self.orden_truncate)}] Procesando: {tabla}")
                
                exito, count = self.truncate_tabla(tabla)
                
                if exito:
                    tablas_exitosas += 1
                    total_eliminados += count
                    self.resultados['tablas_procesadas'].append({
                        'tabla': tabla,
                        'registros_eliminados': count,
                        'orden': i,
                        'timestamp': datetime.datetime.now().isoformat()
                    })
                else:
                    self.log(f"❌ Fallo en tabla {tabla}, abortando proceso", "ERROR")
                    self.conexion.rollback()
                    return False
            
            if self.modo_prueba:
                self.log("\n🧪 MODO PRUEBA - Realizando ROLLBACK")
                self.conexion.rollback()
            else:
                self.log("\n💾 Confirmando cambios (COMMIT)")
                self.conexion.commit()
            
            self.log(f"\n✅ PROCESO COMPLETADO:")
            self.log(f"   Tablas procesadas: {tablas_exitosas}/{len(self.orden_truncate)}")
            self.log(f"   Total registros: {total_eliminados:,}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error en transacción: {e}", "ERROR")
            self.conexion.rollback()
            return False
        finally:
            self.habilitar_foreign_keys()
    
    def verificar_integridad_post_truncate(self):
        """Verifica la integridad después del truncate"""
        if self.modo_prueba:
            self.log("\n🧪 Saltando verificación (modo prueba)")
            return True
            
        self.log("\n=== VERIFICANDO INTEGRIDAD POST-TRUNCATE ===")
        
        try:
            # Verificar que las tablas estén vacías
            for tabla in self.orden_truncate:
                self.cursor.execute(f"SELECT COUNT(*) as total FROM {tabla}")
                count = self.cursor.fetchone()['total']
                
                if count > 0:
                    self.log(f"⚠️ {tabla} no está vacía: {count} registros", "WARNING")
                    self.resultados['warnings'].append(f"Tabla {tabla} no está completamente vacía")
                else:
                    self.log(f"✅ {tabla}: vacía")
            
            # Verificar constraints
            self.cursor.execute("""
                SELECT COUNT(*) as total 
                FROM information_schema.TABLE_CONSTRAINTS 
                WHERE CONSTRAINT_SCHEMA = 'capired' 
                AND CONSTRAINT_TYPE = 'FOREIGN KEY'
            """)
            fk_count = self.cursor.fetchone()['total']
            self.log(f"✅ Foreign Keys activas: {fk_count}")
            
            return True
            
        except Error as e:
            self.log(f"❌ Error verificando integridad: {e}", "ERROR")
            return False
    
    def generar_reporte_final(self):
        """Genera reporte final del proceso"""
        self.resultados['fin'] = datetime.datetime.now().isoformat()
        
        if self.resultados['inicio']:
            inicio = datetime.datetime.fromisoformat(self.resultados['inicio'])
            fin = datetime.datetime.fromisoformat(self.resultados['fin'])
            self.resultados['tiempo_total'] = str(fin - inicio)
        
        reporte_file = f"reporte_truncate_{self.timestamp}.json"
        
        try:
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(self.resultados, f, indent=2, ensure_ascii=False)
            
            self.log(f"\n📋 Reporte guardado: {reporte_file}")
            
            # Resumen en consola
            self.log("\n" + "=" * 80)
            self.log("                    RESUMEN FINAL")
            self.log("=" * 80)
            
            modo = "SIMULACIÓN" if self.modo_prueba else "EJECUCIÓN REAL"
            self.log(f"Modo: {modo}")
            self.log(f"Backup realizado: {'✅' if self.resultados['backup_realizado'] else '❌'}")
            self.log(f"Tablas procesadas: {len(self.resultados['tablas_procesadas'])}/{len(self.orden_truncate)}")
            self.log(f"Errores: {len(self.resultados['errores'])}")
            self.log(f"Warnings: {len(self.resultados['warnings'])}")
            
            total_eliminados = sum(self.resultados['registros_eliminados'].values())
            self.log(f"Total registros eliminados: {total_eliminados:,}")
            
            if self.resultados['tiempo_total']:
                self.log(f"Tiempo total: {self.resultados['tiempo_total']}")
            
            return reporte_file
            
        except Exception as e:
            self.log(f"❌ Error generando reporte: {e}", "ERROR")
            return None
    
    def ejecutar_proceso_completo(self):
        """Ejecuta el proceso completo de truncate seguro"""
        self.resultados['inicio'] = datetime.datetime.now().isoformat()
        
        self.log("\n" + "=" * 80)
        self.log("           TRUNCATE SEGURO - SISTEMA DE DOTACIONES")
        self.log("=" * 80)
        
        modo_texto = "MODO PRUEBA" if self.modo_prueba else "MODO PRODUCCIÓN"
        self.log(f"🔧 {modo_texto}")
        self.log(f"📅 Timestamp: {self.timestamp}")
        
        # Paso 1: Conectar
        if not self.conectar():
            return False
        
        try:
            # Paso 2: Verificar tablas
            if not self.verificar_tablas_existen():
                return False
            
            # Paso 3: Contar registros
            conteos, hay_datos = self.contar_registros_pre_truncate()
            
            if not hay_datos:
                self.log("ℹ️ No hay datos para procesar")
                return True
            
            # Paso 4: Backup (solo en modo producción)
            if not self.modo_prueba:
                if not self.crear_backup_completo():
                    self.log("❌ Backup falló, abortando proceso", "ERROR")
                    return False
            else:
                self.log("🧪 Saltando backup (modo prueba)")
            
            # Paso 5: Ejecutar truncate
            if not self.ejecutar_truncate_secuencial():
                return False
            
            # Paso 6: Verificar integridad
            if not self.verificar_integridad_post_truncate():
                return False
            
            # Paso 7: Generar reporte
            self.generar_reporte_final()
            
            self.log("\n🎉 PROCESO COMPLETADO EXITOSAMENTE")
            return True
            
        except Exception as e:
            self.log(f"❌ Error crítico: {e}", "ERROR")
            return False
            
        finally:
            if hasattr(self, 'cursor'):
                self.cursor.close()
            if hasattr(self, 'conexion'):
                self.conexion.close()
            self.log("🔌 Conexión cerrada")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Truncate Seguro del Sistema de Dotaciones')
    parser.add_argument('--produccion', action='store_true', 
                       help='Ejecutar en modo producción (por defecto: modo prueba)')
    parser.add_argument('--confirmar', action='store_true',
                       help='Confirmar ejecución en modo producción')
    
    args = parser.parse_args()
    
    # Validaciones de seguridad
    if args.produccion and not args.confirmar:
        print("❌ ERROR: Para ejecutar en modo producción debe usar --confirmar")
        print("   Ejemplo: python truncate_sistema_seguro.py --produccion --confirmar")
        return 1
    
    if args.produccion:
        print("\n⚠️ ADVERTENCIA: MODO PRODUCCIÓN")
        print("   Este proceso eliminará TODOS los datos de las tablas del sistema.")
        print("   Se creará un backup automático antes de proceder.")
        
        confirmacion = input("\n¿Está seguro de continuar? (escriba 'CONFIRMAR'): ")
        if confirmacion != 'CONFIRMAR':
            print("❌ Proceso cancelado por el usuario")
            return 1
    
    # Ejecutar proceso
    modo_prueba = not args.produccion
    truncate_seguro = TruncateSeguroSistema(modo_prueba=modo_prueba)
    
    exito = truncate_seguro.ejecutar_proceso_completo()
    
    if exito:
        if modo_prueba:
            print("\n✅ Simulación completada. Revisar logs para detalles.")
            print("   Para ejecutar en producción: --produccion --confirmar")
        else:
            print("\n✅ Truncate completado en modo producción.")
        return 0
    else:
        print("\n❌ El proceso falló. Revisar logs para detalles.")
        return 1

if __name__ == "__main__":
    exit(main())