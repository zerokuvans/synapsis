#!/usr/bin/env python3
"""
Script para crear la tabla de límites configurables del ferretero
Permite gestionar los límites de materiales por área de trabajo de forma dinámica
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT'))
}

def setup_limites_ferretero_table():
    """Crear tabla para gestionar límites configurables del ferretero"""
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("Creando tabla para límites configurables del ferretero...")
            
            # Crear tabla limites_ferretero
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS limites_ferretero (
                    id_limite INT AUTO_INCREMENT PRIMARY KEY,
                    area_trabajo VARCHAR(100) NOT NULL,
                    material_tipo ENUM('silicona', 'amarres_negros', 'amarres_blancos', 'cinta_aislante', 'grapas_blancas', 'grapas_negras') NOT NULL,
                    cantidad_limite INT NOT NULL DEFAULT 0,
                    periodo_dias INT NOT NULL DEFAULT 7,
                    unidad_medida VARCHAR(20) DEFAULT 'unidades',
                    descripcion TEXT,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    usuario_creacion VARCHAR(100),
                    usuario_actualizacion VARCHAR(100),
                    UNIQUE KEY unique_area_material (area_trabajo, material_tipo),
                    INDEX idx_area_trabajo (area_trabajo),
                    INDEX idx_material_tipo (material_tipo),
                    INDEX idx_activo (activo)
                )
            """)
            print("✓ Tabla limites_ferretero creada")
            
            # Insertar límites por defecto basados en el sistema actual
            limites_default = [
                # FTTH INSTALACIONES
                ('FTTH INSTALACIONES', 'cinta_aislante', 3, 15, 'unidades', 'Límite para técnicos de FTTH Instalaciones'),
                ('FTTH INSTALACIONES', 'silicona', 16, 7, 'unidades', 'Límite para técnicos de FTTH Instalaciones'),
                ('FTTH INSTALACIONES', 'amarres_negros', 50, 7, 'unidades', 'Límite para técnicos de FTTH Instalaciones'),
                ('FTTH INSTALACIONES', 'amarres_blancos', 50, 7, 'unidades', 'Límite para técnicos de FTTH Instalaciones'),
                ('FTTH INSTALACIONES', 'grapas_blancas', 100, 7, 'unidades', 'Límite para técnicos de FTTH Instalaciones'),
                ('FTTH INSTALACIONES', 'grapas_negras', 100, 7, 'unidades', 'Límite para técnicos de FTTH Instalaciones'),
                
                # INSTALACIONES DOBLES
                ('INSTALACIONES DOBLES', 'cinta_aislante', 3, 15, 'unidades', 'Límite para técnicos de Instalaciones Dobles'),
                ('INSTALACIONES DOBLES', 'silicona', 16, 7, 'unidades', 'Límite para técnicos de Instalaciones Dobles'),
                ('INSTALACIONES DOBLES', 'amarres_negros', 50, 7, 'unidades', 'Límite para técnicos de Instalaciones Dobles'),
                ('INSTALACIONES DOBLES', 'amarres_blancos', 50, 7, 'unidades', 'Límite para técnicos de Instalaciones Dobles'),
                ('INSTALACIONES DOBLES', 'grapas_blancas', 150, 7, 'unidades', 'Límite para técnicos de Instalaciones Dobles'),
                ('INSTALACIONES DOBLES', 'grapas_negras', 100, 7, 'unidades', 'Límite para técnicos de Instalaciones Dobles'),
                
                # POSTVENTA
                ('POSTVENTA', 'cinta_aislante', 3, 15, 'unidades', 'Límite para técnicos de Postventa'),
                ('POSTVENTA', 'silicona', 12, 7, 'unidades', 'Límite para técnicos de Postventa'),
                ('POSTVENTA', 'amarres_negros', 50, 7, 'unidades', 'Límite para técnicos de Postventa'),
                ('POSTVENTA', 'amarres_blancos', 50, 7, 'unidades', 'Límite para técnicos de Postventa'),
                ('POSTVENTA', 'grapas_blancas', 100, 7, 'unidades', 'Límite para técnicos de Postventa'),
                ('POSTVENTA', 'grapas_negras', 100, 7, 'unidades', 'Límite para técnicos de Postventa'),
                
                # MANTENIMIENTO FTTH
                ('MANTENIMIENTO FTTH', 'cinta_aislante', 1, 15, 'unidades', 'Límite para técnicos de Mantenimiento FTTH'),
                ('MANTENIMIENTO FTTH', 'silicona', 8, 7, 'unidades', 'Límite para técnicos de Mantenimiento FTTH'),
                ('MANTENIMIENTO FTTH', 'amarres_negros', 50, 15, 'unidades', 'Límite para técnicos de Mantenimiento FTTH'),
                ('MANTENIMIENTO FTTH', 'amarres_blancos', 50, 15, 'unidades', 'Límite para técnicos de Mantenimiento FTTH'),
                ('MANTENIMIENTO FTTH', 'grapas_blancas', 100, 7, 'unidades', 'Límite para técnicos de Mantenimiento FTTH'),
                ('MANTENIMIENTO FTTH', 'grapas_negras', 100, 7, 'unidades', 'Límite para técnicos de Mantenimiento FTTH'),
                
                # ARREGLOS HFC
                ('ARREGLOS HFC', 'cinta_aislante', 1, 15, 'unidades', 'Límite para técnicos de Arreglos HFC'),
                ('ARREGLOS HFC', 'silicona', 8, 7, 'unidades', 'Límite para técnicos de Arreglos HFC'),
                ('ARREGLOS HFC', 'amarres_negros', 50, 15, 'unidades', 'Límite para técnicos de Arreglos HFC'),
                ('ARREGLOS HFC', 'amarres_blancos', 50, 15, 'unidades', 'Límite para técnicos de Arreglos HFC'),
                ('ARREGLOS HFC', 'grapas_blancas', 100, 7, 'unidades', 'Límite para técnicos de Arreglos HFC'),
                ('ARREGLOS HFC', 'grapas_negras', 100, 7, 'unidades', 'Límite para técnicos de Arreglos HFC'),
                
                # CONDUCTOR
                ('CONDUCTOR', 'cinta_aislante', 99, 15, 'unidades', 'Límite para Conductores'),
                ('CONDUCTOR', 'silicona', 99, 7, 'unidades', 'Límite para Conductores'),
                ('CONDUCTOR', 'amarres_negros', 99, 15, 'unidades', 'Límite para Conductores'),
                ('CONDUCTOR', 'amarres_blancos', 99, 15, 'unidades', 'Límite para Conductores'),
                ('CONDUCTOR', 'grapas_blancas', 99, 7, 'unidades', 'Límite para Conductores'),
                ('CONDUCTOR', 'grapas_negras', 99, 7, 'unidades', 'Límite para Conductores'),
                
                # SUPERVISORES
                ('SUPERVISORES', 'cinta_aislante', 99, 15, 'unidades', 'Límite para Supervisores'),
                ('SUPERVISORES', 'silicona', 99, 7, 'unidades', 'Límite para Supervisores'),
                ('SUPERVISORES', 'amarres_negros', 99, 15, 'unidades', 'Límite para Supervisores'),
                ('SUPERVISORES', 'amarres_blancos', 99, 15, 'unidades', 'Límite para Supervisores'),
                ('SUPERVISORES', 'grapas_blancas', 99, 7, 'unidades', 'Límite para Supervisores'),
                ('SUPERVISORES', 'grapas_negras', 99, 7, 'unidades', 'Límite para Supervisores'),
                
                # BROWNFIELD
                ('BROWNFIELD', 'cinta_aislante', 5, 15, 'unidades', 'Límite para técnicos de Brownfield'),
                ('BROWNFIELD', 'silicona', 16, 7, 'unidades', 'Límite para técnicos de Brownfield'),
                ('BROWNFIELD', 'amarres_negros', 50, 15, 'unidades', 'Límite para técnicos de Brownfield'),
                ('BROWNFIELD', 'amarres_blancos', 50, 15, 'unidades', 'Límite para técnicos de Brownfield'),
                ('BROWNFIELD', 'grapas_blancas', 200, 15, 'unidades', 'Límite para técnicos de Brownfield'),
                ('BROWNFIELD', 'grapas_negras', 200, 15, 'unidades', 'Límite para técnicos de Brownfield'),
            ]
            
            # Insertar límites por defecto
            cursor.executemany("""
                INSERT IGNORE INTO limites_ferretero 
                (area_trabajo, material_tipo, cantidad_limite, periodo_dias, unidad_medida, descripcion, usuario_creacion) 
                VALUES (%s, %s, %s, %s, %s, %s, 'sistema')
            """, limites_default)
            
            print(f"✓ Insertados {cursor.rowcount} límites por defecto")
            
            # Crear tabla de historial de cambios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historial_limites_ferretero (
                    id_historial INT AUTO_INCREMENT PRIMARY KEY,
                    id_limite INT NOT NULL,
                    area_trabajo VARCHAR(100) NOT NULL,
                    material_tipo VARCHAR(50) NOT NULL,
                    cantidad_limite_anterior INT,
                    cantidad_limite_nueva INT,
                    periodo_dias_anterior INT,
                    periodo_dias_nuevo INT,
                    accion ENUM('creacion', 'modificacion', 'eliminacion') NOT NULL,
                    usuario VARCHAR(100) NOT NULL,
                    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    observaciones TEXT,
                    INDEX idx_limite (id_limite),
                    INDEX idx_fecha (fecha_cambio),
                    INDEX idx_usuario (usuario),
                    FOREIGN KEY (id_limite) REFERENCES limites_ferretero(id_limite) ON DELETE CASCADE
                )
            """)
            print("✓ Tabla historial_limites_ferretero creada")
            
            # Crear trigger para registrar cambios automáticamente
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS tr_limites_ferretero_update
                AFTER UPDATE ON limites_ferretero
                FOR EACH ROW
                BEGIN
                    INSERT INTO historial_limites_ferretero (
                        id_limite, area_trabajo, material_tipo, 
                        cantidad_limite_anterior, cantidad_limite_nueva,
                        periodo_dias_anterior, periodo_dias_nuevo,
                        accion, usuario, observaciones
                    ) VALUES (
                        NEW.id_limite, NEW.area_trabajo, NEW.material_tipo,
                        OLD.cantidad_limite, NEW.cantidad_limite,
                        OLD.periodo_dias, NEW.periodo_dias,
                        'modificacion', NEW.usuario_actualizacion,
                        CONCAT('Límite actualizado de ', OLD.cantidad_limite, ' a ', NEW.cantidad_limite, 
                               ' unidades. Período de ', OLD.periodo_dias, ' a ', NEW.periodo_dias, ' días.')
                    );
                END
            """)
            print("✓ Trigger de historial creado")
            
            connection.commit()
            print("\n✅ Configuración de límites ferretero completada exitosamente")
            
            # Mostrar resumen
            cursor.execute("SELECT COUNT(*) as total FROM limites_ferretero")
            total_limites = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT area_trabajo) as areas FROM limites_ferretero")
            total_areas = cursor.fetchone()[0]
            
            print(f"\n📊 Resumen:")
            print(f"   - Total de límites configurados: {total_limites}")
            print(f"   - Áreas de trabajo: {total_areas}")
            print(f"   - Materiales por área: 6")
            
    except Error as e:
        print(f"❌ Error MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Conexión a MySQL cerrada")

def verificar_instalacion():
    """Verificar que las tablas se crearon correctamente"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        print("\n🔍 Verificando instalación...")
        
        # Verificar tabla principal
        cursor.execute("SHOW TABLES LIKE 'limites_ferretero'")
        if cursor.fetchone():
            print("✓ Tabla limites_ferretero existe")
            
            cursor.execute("SELECT COUNT(*) as total FROM limites_ferretero")
            total = cursor.fetchone()['total']
            print(f"✓ Total de registros: {total}")
        else:
            print("❌ Tabla limites_ferretero no existe")
        
        # Verificar tabla de historial
        cursor.execute("SHOW TABLES LIKE 'historial_limites_ferretero'")
        if cursor.fetchone():
            print("✓ Tabla historial_limites_ferretero existe")
        else:
            print("❌ Tabla historial_limites_ferretero no existe")
            
        # Mostrar algunas áreas configuradas
        cursor.execute("SELECT DISTINCT area_trabajo FROM limites_ferretero ORDER BY area_trabajo")
        areas = cursor.fetchall()
        print(f"\n📋 Áreas configuradas:")
        for area in areas:
            print(f"   - {area['area_trabajo']}")
            
    except Error as e:
        print(f"❌ Error en verificación: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("🚀 Iniciando configuración de límites ferretero...")
    setup_limites_ferretero_table()
    verificar_instalacion()
    print("\n✅ Proceso completado")