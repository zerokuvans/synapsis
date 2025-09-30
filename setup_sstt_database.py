#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar la base de datos del módulo SSTT (Seguridad y Salud en el Trabajo)
"""

import mysql.connector
from datetime import datetime

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def limpiar_tablas_anteriores():
    """Elimina las tablas incorrectas de soporte técnico"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🧹 Limpiando tablas anteriores...")
        
        # Eliminar restricciones de clave foránea primero
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Lista de tablas a eliminar
        tablas_a_eliminar = [
            'sstt_tickets', 'sstt_comentarios', 'sstt_escalamientos',
            'sstt_equipos_soporte', 'sstt_base_conocimiento', 
            'sstt_prioridades', 'sstt_categorias'
        ]
        
        for tabla in tablas_a_eliminar:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {tabla}")
                print(f"   ✅ Tabla '{tabla}' eliminada")
            except Exception as e:
                print(f"   ⚠️  Error eliminando '{tabla}': {e}")
        
        # Reactivar restricciones
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error en limpieza: {e}")

def crear_estructura_sstt():
    """Crea la estructura de base de datos para Seguridad y Salud en el Trabajo"""
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=== CONFIGURACIÓN DE BASE DE DATOS MÓDULO SSTT ===")
        print("    (Seguridad y Salud en el Trabajo)")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        print("✅ Conectado a la base de datos MySQL")
        print()
        
        # 1. Tabla de tipos de riesgo
        print("🔧 Creando tabla 'sstt_tipos_riesgo'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sstt_tipos_riesgo (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                color VARCHAR(7) DEFAULT '#FF0000',
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ Tabla 'sstt_tipos_riesgo' creada")
        
        # 2. Tabla de inspecciones de seguridad
        print("🔧 Creando tabla 'sstt_inspecciones'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sstt_inspecciones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(200) NOT NULL,
                descripcion TEXT,
                area VARCHAR(100),
                responsable_inspeccion VARCHAR(100),
                fecha_inspeccion DATE NOT NULL,
                estado ENUM('programada', 'en_proceso', 'completada', 'cancelada') DEFAULT 'programada',
                prioridad ENUM('baja', 'media', 'alta', 'critica') DEFAULT 'media',
                observaciones TEXT,
                usuario_creador INT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_creador) REFERENCES recurso_operativo(id_codigo_consumidor)
            )
        """)
        print("   ✅ Tabla 'sstt_inspecciones' creada")
        
        # 3. Tabla de hallazgos de inspección
        print("🔧 Creando tabla 'sstt_hallazgos'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sstt_hallazgos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                inspeccion_id INT NOT NULL,
                tipo_riesgo_id INT NOT NULL,
                descripcion TEXT NOT NULL,
                ubicacion VARCHAR(200),
                nivel_riesgo ENUM('bajo', 'medio', 'alto', 'critico') DEFAULT 'medio',
                accion_correctiva TEXT,
                responsable_accion VARCHAR(100),
                fecha_limite DATE,
                estado ENUM('abierto', 'en_proceso', 'cerrado', 'verificado') DEFAULT 'abierto',
                evidencia_foto VARCHAR(255),
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inspeccion_id) REFERENCES sstt_inspecciones(id) ON DELETE CASCADE,
                FOREIGN KEY (tipo_riesgo_id) REFERENCES sstt_tipos_riesgo(id)
            )
        """)
        print("   ✅ Tabla 'sstt_hallazgos' creada")
        
        # 4. Tabla de capacitaciones
        print("🔧 Creando tabla 'sstt_capacitaciones'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sstt_capacitaciones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(200) NOT NULL,
                descripcion TEXT,
                tipo ENUM('presencial', 'virtual', 'mixta') DEFAULT 'presencial',
                duracion_horas DECIMAL(4,2),
                instructor VARCHAR(100),
                fecha_programada DATETIME,
                fecha_realizacion DATETIME,
                lugar VARCHAR(200),
                estado ENUM('programada', 'en_curso', 'completada', 'cancelada') DEFAULT 'programada',
                capacidad_maxima INT DEFAULT 20,
                material_apoyo VARCHAR(255),
                certificacion_requerida BOOLEAN DEFAULT FALSE,
                usuario_creador INT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_creador) REFERENCES recurso_operativo(id_codigo_consumidor)
            )
        """)
        print("   ✅ Tabla 'sstt_capacitaciones' creada")
        
        # 5. Tabla de asistencia a capacitaciones
        print("🔧 Creando tabla 'sstt_asistencia_capacitaciones'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sstt_asistencia_capacitaciones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                capacitacion_id INT NOT NULL,
                usuario_id INT NOT NULL,
                asistio BOOLEAN DEFAULT FALSE,
                calificacion DECIMAL(3,1),
                certificado_emitido BOOLEAN DEFAULT FALSE,
                observaciones TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (capacitacion_id) REFERENCES sstt_capacitaciones(id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES recurso_operativo(id_codigo_consumidor),
                UNIQUE KEY unique_asistencia (capacitacion_id, usuario_id)
            )
        """)
        print("   ✅ Tabla 'sstt_asistencia_capacitaciones' creada")
        
        # 6. Tabla de incidentes/accidentes
        print("🔧 Creando tabla 'sstt_incidentes'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sstt_incidentes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tipo ENUM('incidente', 'accidente', 'casi_accidente') NOT NULL,
                fecha_ocurrencia DATETIME NOT NULL,
                lugar VARCHAR(200) NOT NULL,
                descripcion TEXT NOT NULL,
                persona_afectada VARCHAR(100),
                cedula_afectado VARCHAR(20),
                testigos TEXT,
                causas_inmediatas TEXT,
                causas_basicas TEXT,
                acciones_inmediatas TEXT,
                acciones_correctivas TEXT,
                responsable_investigacion VARCHAR(100),
                estado ENUM('reportado', 'investigando', 'cerrado') DEFAULT 'reportado',
                gravedad ENUM('leve', 'moderado', 'grave', 'muy_grave') DEFAULT 'leve',
                dias_incapacidad INT DEFAULT 0,
                costo_estimado DECIMAL(10,2),
                usuario_reporta INT,
                fecha_reporte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_reporta) REFERENCES recurso_operativo(id_codigo_consumidor)
            )
        """)
        print("   ✅ Tabla 'sstt_incidentes' creada")
        
        # 7. Tabla de elementos de protección personal (EPP)
        print("🔧 Creando tabla 'sstt_epp_control'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sstt_epp_control (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                tipo_epp VARCHAR(100) NOT NULL,
                marca VARCHAR(100),
                modelo VARCHAR(100),
                fecha_entrega DATE NOT NULL,
                fecha_vencimiento DATE,
                estado ENUM('nuevo', 'bueno', 'regular', 'malo', 'reemplazado') DEFAULT 'nuevo',
                observaciones TEXT,
                entregado_por VARCHAR(100),
                recibido_conforme BOOLEAN DEFAULT TRUE,
                fecha_devolucion DATE,
                motivo_devolucion TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES recurso_operativo(id_codigo_consumidor)
            )
        """)
        print("   ✅ Tabla 'sstt_epp_control' creada")
        
        # Insertar datos iniciales
        print("\n📊 Insertando datos iniciales...")
        
        # Tipos de riesgo básicos
        tipos_riesgo = [
            ('Riesgo Físico', 'Ruido, vibraciones, temperaturas extremas, radiaciones', '#FF6B6B'),
            ('Riesgo Químico', 'Exposición a sustancias químicas peligrosas', '#4ECDC4'),
            ('Riesgo Biológico', 'Exposición a microorganismos patógenos', '#45B7D1'),
            ('Riesgo Ergonómico', 'Posturas inadecuadas, movimientos repetitivos', '#96CEB4'),
            ('Riesgo Psicosocial', 'Estrés laboral, carga mental, violencia', '#FFEAA7'),
            ('Riesgo Mecánico', 'Máquinas, herramientas, caídas, golpes', '#DDA0DD'),
            ('Riesgo Eléctrico', 'Contacto con energía eléctrica', '#FFB347'),
            ('Riesgo Locativo', 'Condiciones de las instalaciones', '#98D8C8')
        ]
        
        for nombre, descripcion, color in tipos_riesgo:
            cursor.execute("""
                INSERT IGNORE INTO sstt_tipos_riesgo (nombre, descripcion, color) 
                VALUES (%s, %s, %s)
            """, (nombre, descripcion, color))
        
        conn.commit()
        print("   ✅ Datos iniciales insertados")
        
        # Verificar tablas creadas
        print("\n🔍 Verificando tablas creadas...")
        cursor.execute("SHOW TABLES LIKE 'sstt_%'")
        tablas = cursor.fetchall()
        
        print(f"   ✅ {len(tablas)} tablas SSTT creadas:")
        for tabla in tablas:
            print(f"      - {tabla[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 ¡Configuración de base de datos SSTT completada exitosamente!")
        print("    Módulo: Seguridad y Salud en el Trabajo")
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    limpiar_tablas_anteriores()
    crear_estructura_sstt()