#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Backup Completo de la Base de Datos
Parte del proceso de truncate seguro del sistema de dotaciones
"""

import mysql.connector
from mysql.connector import Error
import subprocess
import os
from datetime import datetime
import json

class BackupDatabase:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '732137A031E4b@',
            'database': 'capired'
        }
        self.backup_dir = 'backups'
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def crear_directorio_backup(self):
        """Crea el directorio de backup si no existe"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            print(f"✓ Directorio de backup creado: {self.backup_dir}")
        else:
            print(f"✓ Directorio de backup existe: {self.backup_dir}")
    
    def backup_completo_mysqldump(self):
        """Realiza backup completo usando mysqldump"""
        print("\n=== INICIANDO BACKUP COMPLETO CON MYSQLDUMP ===")
        
        backup_file = os.path.join(self.backup_dir, f'capired_backup_completo_{self.timestamp}.sql')
        
        # Comando mysqldump con opciones completas
        cmd = [
            'mysqldump',
            f'--host={self.config["host"]}',
            f'--user={self.config["user"]}',
            f'--password={self.config["password"]}',
            '--single-transaction',
            '--routines',
            '--triggers',
            '--events',
            '--add-drop-table',
            '--add-locks',
            '--create-options',
            '--disable-keys',
            '--extended-insert',
            '--lock-tables=false',
            '--quick',
            '--set-charset',
            self.config['database']
        ]
        
        try:
            print(f"Ejecutando backup a: {backup_file}")
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                # Verificar que el archivo se creó y tiene contenido
                if os.path.exists(backup_file) and os.path.getsize(backup_file) > 0:
                    size_mb = os.path.getsize(backup_file) / (1024 * 1024)
                    print(f"✓ Backup completo exitoso")
                    print(f"  Archivo: {backup_file}")
                    print(f"  Tamaño: {size_mb:.2f} MB")
                    return backup_file
                else:
                    print("❌ Error: Archivo de backup vacío o no creado")
                    return None
            else:
                print(f"❌ Error en mysqldump: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error ejecutando mysqldump: {e}")
            return None
    
    def backup_tablas_especificas(self, tablas_dotaciones):
        """Realiza backup específico de las tablas del sistema de dotaciones"""
        print("\n=== BACKUP ESPECÍFICO DE TABLAS DE DOTACIONES ===")
        
        backup_file = os.path.join(self.backup_dir, f'dotaciones_backup_{self.timestamp}.sql')
        
        # Filtrar solo las tablas que existen y no son vistas
        tablas_reales = []
        
        try:
            connection = mysql.connector.connect(**self.config)
            cursor = connection.cursor()
            
            for tabla in tablas_dotaciones:
                # Verificar si es una tabla real (no vista)
                cursor.execute(f"""
                    SELECT TABLE_TYPE 
                    FROM information_schema.tables 
                    WHERE table_schema = 'capired' AND table_name = '{tabla}'
                """)
                
                result = cursor.fetchone()
                if result and result[0] == 'BASE TABLE':
                    tablas_reales.append(tabla)
                elif result and result[0] == 'VIEW':
                    print(f"  ⚠️ Omitiendo vista: {tabla}")
                else:
                    print(f"  ⚠️ Tabla no encontrada: {tabla}")
            
            cursor.close()
            connection.close()
            
        except Error as e:
            print(f"❌ Error verificando tablas: {e}")
            return None
        
        if not tablas_reales:
            print("❌ No se encontraron tablas válidas para backup")
            return None
        
        # Comando mysqldump para tablas específicas
        cmd = [
            'mysqldump',
            f'--host={self.config["host"]}',
            f'--user={self.config["user"]}',
            f'--password={self.config["password"]}',
            '--single-transaction',
            '--add-drop-table',
            '--add-locks',
            '--create-options',
            '--disable-keys',
            '--extended-insert',
            '--lock-tables=false',
            '--quick',
            '--set-charset',
            self.config['database']
        ] + tablas_reales
        
        try:
            print(f"Respaldando {len(tablas_reales)} tablas a: {backup_file}")
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                if os.path.exists(backup_file) and os.path.getsize(backup_file) > 0:
                    size_mb = os.path.getsize(backup_file) / (1024 * 1024)
                    print(f"✓ Backup específico exitoso")
                    print(f"  Archivo: {backup_file}")
                    print(f"  Tamaño: {size_mb:.2f} MB")
                    print(f"  Tablas: {', '.join(tablas_reales)}")
                    return backup_file
                else:
                    print("❌ Error: Archivo de backup específico vacío")
                    return None
            else:
                print(f"❌ Error en backup específico: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error ejecutando backup específico: {e}")
            return None
    
    def generar_reporte_backup(self, backup_completo, backup_especifico, tablas_dotaciones):
        """Genera reporte detallado del backup"""
        reporte = {
            'timestamp': self.timestamp,
            'fecha_backup': datetime.now().isoformat(),
            'backup_completo': {
                'archivo': backup_completo,
                'exitoso': backup_completo is not None,
                'tamaño_mb': os.path.getsize(backup_completo) / (1024 * 1024) if backup_completo else 0
            },
            'backup_especifico': {
                'archivo': backup_especifico,
                'exitoso': backup_especifico is not None,
                'tamaño_mb': os.path.getsize(backup_especifico) / (1024 * 1024) if backup_especifico else 0
            },
            'tablas_sistema': tablas_dotaciones,
            'total_tablas': len(tablas_dotaciones)
        }
        
        reporte_file = os.path.join(self.backup_dir, f'reporte_backup_{self.timestamp}.json')
        
        try:
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print(f"\n✓ Reporte de backup generado: {reporte_file}")
            return reporte_file
            
        except Exception as e:
            print(f"❌ Error generando reporte: {e}")
            return None
    
    def ejecutar_backup_completo(self, tablas_dotaciones):
        """Ejecuta el proceso completo de backup"""
        print("\n" + "=" * 80)
        print("           PROCESO DE BACKUP COMPLETO - SISTEMA DOTACIONES")
        print("=" * 80)
        print(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base de datos: {self.config['database']}")
        print(f"Servidor: {self.config['host']}")
        
        # Crear directorio
        self.crear_directorio_backup()
        
        # Backup completo
        backup_completo = self.backup_completo_mysqldump()
        
        # Backup específico
        backup_especifico = self.backup_tablas_especificas(tablas_dotaciones)
        
        # Generar reporte
        reporte = self.generar_reporte_backup(backup_completo, backup_especifico, tablas_dotaciones)
        
        # Resumen final
        print("\n" + "=" * 80)
        print("                        RESUMEN DEL BACKUP")
        print("=" * 80)
        
        if backup_completo:
            print(f"✓ Backup completo: {backup_completo}")
        else:
            print("❌ Backup completo: FALLÓ")
        
        if backup_especifico:
            print(f"✓ Backup específico: {backup_especifico}")
        else:
            print("❌ Backup específico: FALLÓ")
        
        if reporte:
            print(f"✓ Reporte: {reporte}")
        
        # Validar que al menos uno fue exitoso
        if backup_completo or backup_especifico:
            print("\n🎉 BACKUP COMPLETADO EXITOSAMENTE")
            print("   El sistema está listo para el proceso de truncate")
            return True
        else:
            print("\n❌ BACKUP FALLÓ COMPLETAMENTE")
            print("   NO PROCEDER con el truncate hasta resolver los errores")
            return False

def main():
    # Tablas identificadas del sistema de dotaciones
    tablas_dotaciones = [
        'asignaciones_equipos_dotaciones',
        'cambios_dotacion',
        'cambios_dotaciones',
        'cambios_dotaciones_detalle',
        'devolucion_detalles',
        'devolucion_dotaciones',
        'devoluciones_dotacion',
        'devoluciones_elementos',
        'devoluciones_historial',
        'dotaciones',
        'equipos_dotaciones',
        'historial_cambios_dotaciones',
        'historial_notificaciones',
        'historial_vencimientos',
        'ingresos_dotaciones',
        'movimientos_equipos_dotaciones'
    ]
    
    backup = BackupDatabase()
    exito = backup.ejecutar_backup_completo(tablas_dotaciones)
    
    if exito:
        print("\n✅ Proceso de backup completado. Puede proceder con el truncate.")
        return 0
    else:
        print("\n❌ Proceso de backup falló. NO proceder con el truncate.")
        return 1

if __name__ == "__main__":
    exit(main())