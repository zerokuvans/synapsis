#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migración para datos existentes de devoluciones
Este script migra las devoluciones existentes al nuevo sistema de gestión de estados

Autor: Sistema de Gestión de Estados
Fecha: 2024
"""

import mysql.connector
import json
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MigracionDevoluciones:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.estadisticas = {
            'devoluciones_procesadas': 0,
            'auditorias_creadas': 0,
            'errores': 0,
            'warnings': 0
        }
    
    def conectar_bd(self):
        """Establece conexión con la base de datos"""
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='732137A031E4b@',
                database='capired'
            )
            self.cursor = self.connection.cursor(dictionary=True)
            logger.info("Conexión a base de datos establecida")
            return True
        except Exception as e:
            logger.error(f"Error al conectar a la base de datos: {str(e)}")
            return False
    
    def cerrar_conexion(self):
        """Cierra la conexión con la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Conexión cerrada")
    
    def verificar_tablas_necesarias(self):
        """Verifica que todas las tablas necesarias existan"""
        tablas_requeridas = [
            'devoluciones_dotacion',
            'auditoria_estados_devolucion',
            'configuracion_notificaciones',
            'historial_notificaciones',
            'roles',
            'usuarios'
        ]
        
        logger.info("Verificando existencia de tablas...")
        
        for tabla in tablas_requeridas:
            self.cursor.execute(f"SHOW TABLES LIKE '{tabla}'")
            if not self.cursor.fetchone():
                logger.error(f"Tabla requerida '{tabla}' no existe")
                return False
        
        logger.info("Todas las tablas requeridas existen")
        return True
    
    def obtener_devoluciones_existentes(self):
        """Obtiene todas las devoluciones existentes"""
        try:
            self.cursor.execute("""
                SELECT id, estado, created_at, updated_at, cliente_id, observaciones
                FROM devoluciones_dotacion
                ORDER BY id
            """)
            
            devoluciones = self.cursor.fetchall()
            logger.info(f"Encontradas {len(devoluciones)} devoluciones para migrar")
            return devoluciones
            
        except Exception as e:
            logger.error(f"Error al obtener devoluciones: {str(e)}")
            return []
    
    def crear_auditoria_inicial(self, devolucion):
        """Crea registro de auditoría inicial para una devolución"""
        try:
            # Buscar usuario administrador para asignar como responsable inicial
            self.cursor.execute("""
                SELECT id FROM usuarios 
                WHERE rol_id = (SELECT id FROM roles WHERE nombre = 'Administrador' LIMIT 1)
                AND activo = 1 
                LIMIT 1
            """)
            
            admin_user = self.cursor.fetchone()
            usuario_id = admin_user['id'] if admin_user else 1
            
            # Crear registro de auditoría
            self.cursor.execute("""
                INSERT INTO auditoria_estados_devolucion 
                (devolucion_id, estado_anterior, estado_nuevo, usuario_id, 
                 fecha_cambio, motivo, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                devolucion['id'],
                None,  # No hay estado anterior
                devolucion['estado'],
                usuario_id,
                devolucion['created_at'],
                'MIGRACION_INICIAL',
                f"Estado inicial migrado: {devolucion['estado']}"
            ))
            
            self.estadisticas['auditorias_creadas'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error al crear auditoría para devolución {devolucion['id']}: {str(e)}")
            self.estadisticas['errores'] += 1
            return False
    
    def validar_estado_devolucion(self, devolucion):
        """Valida y normaliza el estado de una devolución"""
        estados_validos = ['REGISTRADA', 'PROCESANDO', 'COMPLETADA', 'CANCELADA']
        estado_actual = devolucion['estado']
        
        if estado_actual in estados_validos:
            return estado_actual
        
        # Mapeo de estados antiguos a nuevos
        mapeo_estados = {
            'PENDIENTE': 'REGISTRADA',
            'EN_PROCESO': 'PROCESANDO',
            'FINALIZADA': 'COMPLETADA',
            'TERMINADA': 'COMPLETADA',
            'ANULADA': 'CANCELADA',
            'RECHAZADA': 'CANCELADA'
        }
        
        if estado_actual in mapeo_estados:
            nuevo_estado = mapeo_estados[estado_actual]
            logger.warning(f"Devolución {devolucion['id']}: Estado '{estado_actual}' mapeado a '{nuevo_estado}'")
            self.estadisticas['warnings'] += 1
            return nuevo_estado
        
        # Estado desconocido, asignar REGISTRADA por defecto
        logger.warning(f"Devolución {devolucion['id']}: Estado desconocido '{estado_actual}', asignando 'REGISTRADA'")
        self.estadisticas['warnings'] += 1
        return 'REGISTRADA'
    
    def actualizar_estado_devolucion(self, devolucion, nuevo_estado):
        """Actualiza el estado de una devolución si es necesario"""
        if devolucion['estado'] != nuevo_estado:
            try:
                self.cursor.execute("""
                    UPDATE devoluciones_dotacion 
                    SET estado = %s, updated_at = NOW()
                    WHERE id = %s
                """, (nuevo_estado, devolucion['id']))
                
                logger.info(f"Devolución {devolucion['id']}: Estado actualizado de '{devolucion['estado']}' a '{nuevo_estado}'")
                return True
                
            except Exception as e:
                logger.error(f"Error al actualizar estado de devolución {devolucion['id']}: {str(e)}")
                self.estadisticas['errores'] += 1
                return False
        
        return True
    
    def migrar_devolucion(self, devolucion):
        """Migra una devolución individual"""
        try:
            # Validar y normalizar estado
            estado_normalizado = self.validar_estado_devolucion(devolucion)
            
            # Actualizar estado si es necesario
            if not self.actualizar_estado_devolucion(devolucion, estado_normalizado):
                return False
            
            # Crear auditoría inicial
            devolucion_actualizada = devolucion.copy()
            devolucion_actualizada['estado'] = estado_normalizado
            
            if not self.crear_auditoria_inicial(devolucion_actualizada):
                return False
            
            self.estadisticas['devoluciones_procesadas'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error al migrar devolución {devolucion['id']}: {str(e)}")
            self.estadisticas['errores'] += 1
            return False
    
    def crear_configuraciones_notificacion_basicas(self):
        """Crea configuraciones básicas de notificación si no existen"""
        try:
            # Verificar si ya existen configuraciones
            self.cursor.execute("SELECT COUNT(*) as count FROM configuracion_notificaciones")
            count = self.cursor.fetchone()['count']
            
            if count > 0:
                logger.info("Ya existen configuraciones de notificación")
                return True
            
            logger.info("Creando configuraciones básicas de notificación...")
            
            # Configuraciones básicas
            configuraciones = [
                {
                    'evento_trigger': 'CAMBIO_ESTADO',
                    'estado_origen': None,
                    'estado_destino': 'PROCESANDO',
                    'tipo_notificacion': 'EMAIL',
                    'destinatarios_roles': json.dumps(['Supervisor', 'Administrador']),
                    'plantilla_email_id': 1,
                    'delay_minutos': 0,
                    'activo': True
                },
                {
                    'evento_trigger': 'CAMBIO_ESTADO',
                    'estado_origen': None,
                    'estado_destino': 'COMPLETADA',
                    'tipo_notificacion': 'EMAIL',
                    'destinatarios_roles': json.dumps(['Tecnico', 'Administrador']),
                    'plantilla_email_id': 2,
                    'delay_minutos': 0,
                    'activo': True
                }
            ]
            
            for config in configuraciones:
                self.cursor.execute("""
                    INSERT INTO configuracion_notificaciones 
                    (evento_trigger, estado_origen, estado_destino, tipo_notificacion,
                     destinatarios_roles, plantilla_email_id, plantilla_sms_id, 
                     delay_minutos, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    config['evento_trigger'],
                    config['estado_origen'],
                    config['estado_destino'],
                    config['tipo_notificacion'],
                    config['destinatarios_roles'],
                    config['plantilla_email_id'],
                    config.get('plantilla_sms_id'),
                    config['delay_minutos'],
                    config['activo']
                ))
            
            logger.info(f"Creadas {len(configuraciones)} configuraciones de notificación")
            return True
            
        except Exception as e:
            logger.error(f"Error al crear configuraciones de notificación: {str(e)}")
            return False
    
    def generar_reporte_migracion(self):
        """Genera un reporte de la migración"""
        logger.info("=" * 60)
        logger.info("REPORTE DE MIGRACIÓN")
        logger.info("=" * 60)
        logger.info(f"Devoluciones procesadas: {self.estadisticas['devoluciones_procesadas']}")
        logger.info(f"Auditorías creadas: {self.estadisticas['auditorias_creadas']}")
        logger.info(f"Warnings: {self.estadisticas['warnings']}")
        logger.info(f"Errores: {self.estadisticas['errores']}")
        
        if self.estadisticas['errores'] == 0:
            logger.info("✅ Migración completada exitosamente")
        else:
            logger.warning(f"⚠️ Migración completada con {self.estadisticas['errores']} errores")
        
        logger.info("=" * 60)
    
    def ejecutar_migracion(self):
        """Ejecuta el proceso completo de migración"""
        logger.info("Iniciando migración de devoluciones existentes...")
        
        if not self.conectar_bd():
            return False
        
        try:
            # Verificar tablas
            if not self.verificar_tablas_necesarias():
                return False
            
            # Crear configuraciones básicas
            self.crear_configuraciones_notificacion_basicas()
            
            # Obtener devoluciones
            devoluciones = self.obtener_devoluciones_existentes()
            
            if not devoluciones:
                logger.info("No hay devoluciones para migrar")
                return True
            
            # Migrar cada devolución
            logger.info(f"Iniciando migración de {len(devoluciones)} devoluciones...")
            
            for i, devolucion in enumerate(devoluciones, 1):
                logger.info(f"Procesando devolución {i}/{len(devoluciones)} (ID: {devolucion['id']})")
                self.migrar_devolucion(devolucion)
                
                # Commit cada 10 registros
                if i % 10 == 0:
                    self.connection.commit()
                    logger.info(f"Progreso: {i}/{len(devoluciones)} devoluciones procesadas")
            
            # Commit final
            self.connection.commit()
            
            # Generar reporte
            self.generar_reporte_migracion()
            
            return True
            
        except Exception as e:
            logger.error(f"Error durante la migración: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False
        
        finally:
            self.cerrar_conexion()

def main():
    """Función principal"""
    print("Script de Migración de Devoluciones")
    print("====================================")
    
    respuesta = input("¿Desea continuar con la migración? (s/N): ")
    if respuesta.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
        print("Migración cancelada")
        return
    
    migracion = MigracionDevoluciones()
    
    if migracion.ejecutar_migracion():
        print("\n✅ Migración completada. Revise el archivo 'migration.log' para más detalles.")
    else:
        print("\n❌ Error durante la migración. Revise el archivo 'migration.log' para más detalles.")

if __name__ == "__main__":
    main()