#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modo de Prueba - Truncate Sistema Dotaciones

Este script simula el proceso de truncate sin realizar cambios reales,
permitiendo validar el impacto y detectar posibles problemas antes de
ejecutar el truncate real.

Autor: Sistema Capired
Fecha: 2025-01-24
Versión: 1.0
"""

import mysql.connector
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any
import os
from decimal import Decimal

class ModoPruebaTruncate:
    """Clase para simular y validar el proceso de truncate"""
    
    def __init__(self):
        """Inicializar configuración de prueba"""
        self.config_db = {
            'host': 'localhost',
            'user': 'root',
            'password': '732137A031E4b@',
            'database': 'capired',
            'charset': 'utf8mb4'
        }
        
        # Tablas a truncar en orden específico
        self.tablas_truncate = [
            'auditoria_estados_devolucion',
            'movimientos_equipos_dotaciones',
            'cambios_dotaciones_detalle',
            'historial_cambios_dotaciones',
            'devolucion_detalles',
            'devoluciones_elementos',
            'historial_notificaciones',
            'devoluciones_historial',
            'asignaciones_equipos_dotaciones',
            'cambios_dotaciones',
            'devoluciones_dotacion',
            'equipos_dotaciones',
            'ingresos_dotaciones',
            'historial_vencimientos',
            'devolucion_dotaciones',
            'cambios_dotacion',
            'dotaciones'
        ]
        
        self.reporte_prueba = {
            'fecha_prueba': datetime.now().isoformat(),
            'modo': 'SIMULACION',
            'tablas_analizadas': [],
            'impacto_estimado': {},
            'problemas_detectados': [],
            'recomendaciones': [],
            'tiempo_estimado': 0,
            'riesgos_identificados': []
        }
        
        # Configurar logging
        self.setup_logging()
    
    def setup_logging(self):
        """Configurar sistema de logging"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f'modo_prueba_truncate_{timestamp}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def conectar_db(self) -> mysql.connector.MySQLConnection:
        """Establecer conexión con la base de datos"""
        try:
            conexion = mysql.connector.connect(**self.config_db)
            self.logger.info("✅ Conexión a base de datos establecida")
            return conexion
        except mysql.connector.Error as e:
            self.logger.error(f"❌ Error de conexión: {e}")
            raise
    
    def analizar_tabla(self, conexion: mysql.connector.MySQLConnection, tabla: str) -> Dict[str, Any]:
        """Analizar una tabla específica antes del truncate"""
        cursor = conexion.cursor(dictionary=True)
        
        try:
            # Información básica de la tabla
            info_tabla = {
                'nombre': tabla,
                'existe': False,
                'registros': 0,
                'tamaño_mb': 0,
                'foreign_keys_entrantes': [],
                'foreign_keys_salientes': [],
                'triggers': [],
                'indices': [],
                'dependencias': []
            }
            
            # Verificar si la tabla existe
            cursor.execute("""
                SELECT COUNT(*) as existe 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s
            """, (self.config_db['database'], tabla))
            
            resultado = cursor.fetchone()
            if resultado['existe'] == 0:
                self.logger.warning(f"⚠️ Tabla {tabla} no existe")
                self.reporte_prueba['problemas_detectados'].append(
                    f"Tabla {tabla} no existe en la base de datos"
                )
                return info_tabla
            
            info_tabla['existe'] = True
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) as total FROM `{tabla}`")
            info_tabla['registros'] = cursor.fetchone()['total']
            
            # Obtener tamaño de la tabla
            cursor.execute("""
                SELECT 
                    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS tamaño_mb
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s
            """, (self.config_db['database'], tabla))
            
            resultado = cursor.fetchone()
            if resultado:
                info_tabla['tamaño_mb'] = resultado['tamaño_mb'] or 0
            
            # Foreign Keys entrantes (tablas que referencian esta tabla)
            cursor.execute("""
                SELECT 
                    table_name as tabla_origen,
                    column_name as columna_origen,
                    referenced_column_name as columna_destino
                FROM information_schema.key_column_usage 
                WHERE referenced_table_schema = %s 
                AND referenced_table_name = %s
                AND referenced_table_name IS NOT NULL
            """, (self.config_db['database'], tabla))
            
            info_tabla['foreign_keys_entrantes'] = cursor.fetchall()
            
            # Foreign Keys salientes (esta tabla referencia otras)
            cursor.execute("""
                SELECT 
                    column_name as columna_origen,
                    referenced_table_name as tabla_destino,
                    referenced_column_name as columna_destino
                FROM information_schema.key_column_usage 
                WHERE table_schema = %s 
                AND table_name = %s
                AND referenced_table_name IS NOT NULL
            """, (self.config_db['database'], tabla))
            
            info_tabla['foreign_keys_salientes'] = cursor.fetchall()
            
            # Triggers asociados
            cursor.execute("""
                SELECT trigger_name, event_manipulation, action_timing
                FROM information_schema.triggers 
                WHERE event_object_schema = %s 
                AND event_object_table = %s
            """, (self.config_db['database'], tabla))
            
            info_tabla['triggers'] = cursor.fetchall()
            
            # Índices
            cursor.execute("""
                SELECT index_name, column_name, non_unique
                FROM information_schema.statistics 
                WHERE table_schema = %s 
                AND table_name = %s
                ORDER BY index_name, seq_in_index
            """, (self.config_db['database'], tabla))
            
            info_tabla['indices'] = cursor.fetchall()
            
            self.logger.info(f"📊 Tabla {tabla}: {info_tabla['registros']} registros, {info_tabla['tamaño_mb']} MB")
            
            return info_tabla
            
        except mysql.connector.Error as e:
            self.logger.error(f"❌ Error analizando tabla {tabla}: {e}")
            self.reporte_prueba['problemas_detectados'].append(
                f"Error analizando tabla {tabla}: {str(e)}"
            )
            return info_tabla
        finally:
            cursor.close()
    
    def validar_dependencias(self, conexion: mysql.connector.MySQLConnection) -> List[str]:
        """Validar dependencias entre tablas"""
        problemas = []
        
        self.logger.info("🔍 Validando dependencias entre tablas...")
        
        for i, tabla in enumerate(self.tablas_truncate):
            # Verificar si hay tablas posteriores que dependen de esta
            tablas_posteriores = self.tablas_truncate[i+1:]
            
            cursor = conexion.cursor(dictionary=True)
            try:
                # Buscar FK que apunten a esta tabla desde tablas que se truncarán después
                for tabla_posterior in tablas_posteriores:
                    cursor.execute("""
                        SELECT COUNT(*) as dependencias
                        FROM information_schema.key_column_usage 
                        WHERE table_schema = %s 
                        AND table_name = %s
                        AND referenced_table_name = %s
                    """, (self.config_db['database'], tabla_posterior, tabla))
                    
                    resultado = cursor.fetchone()
                    if resultado['dependencias'] > 0:
                        problema = f"Dependencia detectada: {tabla_posterior} referencia {tabla} (orden incorrecto)"
                        problemas.append(problema)
                        self.logger.warning(f"⚠️ {problema}")
                        
            except mysql.connector.Error as e:
                self.logger.error(f"❌ Error validando dependencias para {tabla}: {e}")
            finally:
                cursor.close()
        
        return problemas
    
    def simular_truncate(self, conexion: mysql.connector.MySQLConnection) -> Dict[str, Any]:
        """Simular el proceso de truncate sin ejecutarlo"""
        self.logger.info("🎭 Iniciando simulación de truncate...")
        
        simulacion = {
            'tablas_procesadas': 0,
            'registros_afectados': 0,
            'tiempo_estimado_segundos': 0,
            'problemas_potenciales': [],
            'warnings': []
        }
        
        for tabla in self.tablas_truncate:
            self.logger.info(f"🔄 Simulando truncate de {tabla}...")
            
            cursor = conexion.cursor(dictionary=True)
            try:
                # Verificar si la tabla existe
                cursor.execute("""
                    SELECT COUNT(*) as existe 
                    FROM information_schema.tables 
                    WHERE table_schema = %s AND table_name = %s
                """, (self.config_db['database'], tabla))
                
                if cursor.fetchone()['existe'] == 0:
                    simulacion['warnings'].append(f"Tabla {tabla} no existe")
                    continue
                
                # Contar registros que serían eliminados
                cursor.execute(f"SELECT COUNT(*) as total FROM `{tabla}`")
                registros = cursor.fetchone()['total']
                
                simulacion['registros_afectados'] += registros
                simulacion['tablas_procesadas'] += 1
                
                # Estimar tiempo (aproximadamente 0.1 segundos por cada 1000 registros)
                tiempo_tabla = max(0.1, registros / 10000)
                simulacion['tiempo_estimado_segundos'] += tiempo_tabla
                
                # Verificar si hay datos críticos
                if registros > 10000:
                    simulacion['warnings'].append(
                        f"Tabla {tabla} tiene {registros} registros (tabla grande)"
                    )
                
                # Simular verificación de FK
                cursor.execute("""
                    SELECT COUNT(*) as fk_count
                    FROM information_schema.key_column_usage 
                    WHERE referenced_table_schema = %s 
                    AND referenced_table_name = %s
                """, (self.config_db['database'], tabla))
                
                fk_count = cursor.fetchone()['fk_count']
                if fk_count > 0:
                    simulacion['warnings'].append(
                        f"Tabla {tabla} tiene {fk_count} foreign keys entrantes"
                    )
                
                self.logger.info(f"✅ {tabla}: {registros} registros serían eliminados")
                
            except mysql.connector.Error as e:
                problema = f"Error simulando truncate de {tabla}: {str(e)}"
                simulacion['problemas_potenciales'].append(problema)
                self.logger.error(f"❌ {problema}")
            finally:
                cursor.close()
        
        return simulacion
    
    def generar_recomendaciones(self) -> List[str]:
        """Generar recomendaciones basadas en el análisis"""
        recomendaciones = []
        
        # Recomendaciones generales
        recomendaciones.extend([
            "Realizar backup completo antes del truncate real",
            "Ejecutar en horario de menor actividad del sistema",
            "Notificar a usuarios sobre mantenimiento programado",
            "Tener plan de rollback preparado",
            "Verificar espacio en disco para logs y backups"
        ])
        
        # Recomendaciones específicas basadas en problemas detectados
        if self.reporte_prueba['problemas_detectados']:
            recomendaciones.append("Resolver problemas detectados antes de proceder")
        
        total_registros = self.reporte_prueba['impacto_estimado'].get('registros_afectados', 0)
        if total_registros > 100000:
            recomendaciones.extend([
                "Considerar truncate por lotes para tablas muy grandes",
                "Monitorear uso de CPU y memoria durante el proceso"
            ])
        
        tiempo_estimado = self.reporte_prueba['impacto_estimado'].get('tiempo_estimado_segundos', 0)
        if tiempo_estimado > 300:  # 5 minutos
            recomendaciones.append("Proceso largo estimado - considerar ventana de mantenimiento extendida")
        
        return recomendaciones
    
    def ejecutar_prueba(self) -> str:
        """Ejecutar el modo de prueba completo"""
        self.logger.info("🚀 Iniciando modo de prueba para truncate del sistema")
        
        try:
            conexion = self.conectar_db()
            
            # Analizar cada tabla
            self.logger.info("📋 Analizando tablas del sistema...")
            for tabla in self.tablas_truncate:
                info_tabla = self.analizar_tabla(conexion, tabla)
                self.reporte_prueba['tablas_analizadas'].append(info_tabla)
            
            # Validar dependencias
            problemas_dependencias = self.validar_dependencias(conexion)
            self.reporte_prueba['problemas_detectados'].extend(problemas_dependencias)
            
            # Simular truncate
            simulacion = self.simular_truncate(conexion)
            self.reporte_prueba['impacto_estimado'] = simulacion
            
            # Generar recomendaciones
            self.reporte_prueba['recomendaciones'] = self.generar_recomendaciones()
            
            # Identificar riesgos
            self.identificar_riesgos()
            
            conexion.close()
            
            # Guardar reporte
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archivo_reporte = f'reporte_modo_prueba_{timestamp}.json'
            
            # Convertir Decimals a float para serialización JSON
            def decimal_converter(obj):
                if isinstance(obj, Decimal):
                    return float(obj)
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            with open(archivo_reporte, 'w', encoding='utf-8') as f:
                json.dump(self.reporte_prueba, f, indent=2, ensure_ascii=False, default=decimal_converter)
            
            self.logger.info(f"📄 Reporte guardado en: {archivo_reporte}")
            
            # Mostrar resumen
            self.mostrar_resumen()
            
            return archivo_reporte
            
        except Exception as e:
            self.logger.error(f"❌ Error crítico en modo de prueba: {e}")
            raise
    
    def identificar_riesgos(self):
        """Identificar riesgos potenciales del truncate"""
        riesgos = []
        
        # Riesgo por volumen de datos
        total_registros = self.reporte_prueba['impacto_estimado'].get('registros_afectados', 0)
        if total_registros > 50000:
            riesgos.append({
                'tipo': 'ALTO_VOLUMEN',
                'descripcion': f'Se eliminarán {total_registros} registros',
                'impacto': 'ALTO',
                'mitigacion': 'Backup completo y verificación de espacio en disco'
            })
        
        # Riesgo por dependencias
        if self.reporte_prueba['problemas_detectados']:
            riesgos.append({
                'tipo': 'DEPENDENCIAS',
                'descripcion': 'Problemas de dependencias detectados',
                'impacto': 'CRITICO',
                'mitigacion': 'Resolver problemas antes de proceder'
            })
        
        # Riesgo por tiempo de ejecución
        tiempo_estimado = self.reporte_prueba['impacto_estimado'].get('tiempo_estimado_segundos', 0)
        if tiempo_estimado > 600:  # 10 minutos
            riesgos.append({
                'tipo': 'TIEMPO_PROLONGADO',
                'descripcion': f'Tiempo estimado: {tiempo_estimado/60:.1f} minutos',
                'impacto': 'MEDIO',
                'mitigacion': 'Programar en ventana de mantenimiento'
            })
        
        self.reporte_prueba['riesgos_identificados'] = riesgos
    
    def mostrar_resumen(self):
        """Mostrar resumen del análisis"""
        print("\n" + "="*60)
        print("📊 RESUMEN DEL MODO DE PRUEBA")
        print("="*60)
        
        # Estadísticas generales
        tablas_existentes = sum(1 for t in self.reporte_prueba['tablas_analizadas'] if t['existe'])
        total_registros = self.reporte_prueba['impacto_estimado'].get('registros_afectados', 0)
        tiempo_estimado = self.reporte_prueba['impacto_estimado'].get('tiempo_estimado_segundos', 0)
        
        print(f"📋 Tablas analizadas: {len(self.reporte_prueba['tablas_analizadas'])}")
        print(f"✅ Tablas existentes: {tablas_existentes}")
        print(f"🗑️ Registros a eliminar: {total_registros:,}")
        print(f"⏱️ Tiempo estimado: {tiempo_estimado:.1f} segundos ({tiempo_estimado/60:.1f} minutos)")
        
        # Problemas detectados
        if self.reporte_prueba['problemas_detectados']:
            print(f"\n⚠️ PROBLEMAS DETECTADOS ({len(self.reporte_prueba['problemas_detectados'])})")
            for problema in self.reporte_prueba['problemas_detectados']:
                print(f"   • {problema}")
        
        # Riesgos identificados
        if self.reporte_prueba['riesgos_identificados']:
            print(f"\n🚨 RIESGOS IDENTIFICADOS ({len(self.reporte_prueba['riesgos_identificados'])})")
            for riesgo in self.reporte_prueba['riesgos_identificados']:
                print(f"   • {riesgo['tipo']}: {riesgo['descripcion']} (Impacto: {riesgo['impacto']})")
        
        # Recomendaciones principales
        print(f"\n💡 RECOMENDACIONES PRINCIPALES")
        for i, rec in enumerate(self.reporte_prueba['recomendaciones'][:5], 1):
            print(f"   {i}. {rec}")
        
        # Veredicto final
        print("\n" + "="*60)
        if not self.reporte_prueba['problemas_detectados']:
            print("✅ VEREDICTO: El sistema está listo para el truncate")
            print("   Puede proceder con el truncate real siguiendo las recomendaciones")
        else:
            print("❌ VEREDICTO: NO proceder con el truncate")
            print("   Resolver los problemas detectados antes de continuar")
        print("="*60)

def main():
    """Función principal"""
    print("🎭 MODO DE PRUEBA - TRUNCATE SISTEMA DOTACIONES")
    print("Este script simula el truncate sin realizar cambios reales\n")
    
    try:
        modo_prueba = ModoPruebaTruncate()
        archivo_reporte = modo_prueba.ejecutar_prueba()
        
        print(f"\n🎉 Modo de prueba completado exitosamente")
        print(f"📄 Reporte detallado guardado en: {archivo_reporte}")
        print("\n💡 Revise el reporte antes de proceder con el truncate real")
        
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())