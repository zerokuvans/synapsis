#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para implementar las correcciones críticas del módulo automotor
Crea tabla faltante y agrega campos requeridos
"""

import mysql.connector
from mysql.connector import Error
import sys
from datetime import datetime

# Configuración de conexión
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def imprimir_separador(titulo=""):
    """Imprime un separador visual"""
    print("\n" + "="*80)
    if titulo:
        print(f" {titulo} ".center(80, "="))
    print("="*80)

def ejecutar_sql(cursor, sql, descripcion):
    """Ejecuta una consulta SQL con manejo de errores"""
    try:
        print(f"\n🔧 {descripcion}...")
        cursor.execute(sql)
        print(f"✅ {descripcion} - COMPLETADO")
        return True
    except Error as e:
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            print(f"⚠️  {descripcion} - YA EXISTE (omitiendo)")
            return True
        else:
            print(f"❌ {descripcion} - ERROR: {e}")
            return False

def crear_tabla_historial_documentos(cursor):
    """Crea la tabla historial_documentos_vehiculos"""
    imprimir_separador("CREANDO TABLA HISTORIAL_DOCUMENTOS_VEHICULOS")
    
    sql_crear_tabla = """
    CREATE TABLE IF NOT EXISTS `historial_documentos_vehiculos` (
      `id_historial` int NOT NULL AUTO_INCREMENT,
      `id_parque_automotor` int NOT NULL,
      `tipo_documento` varchar(50) NOT NULL,
      `fecha_vencimiento_anterior` date DEFAULT NULL,
      `fecha_vencimiento_nueva` date NOT NULL,
      `fecha_renovacion` datetime DEFAULT CURRENT_TIMESTAMP,
      `usuario_renovacion` varchar(100) DEFAULT NULL,
      `observaciones` text,
      `estado_documento` varchar(20) DEFAULT 'Vigente',
      `numero_documento` varchar(100) DEFAULT NULL,
      `entidad_expedidora` varchar(100) DEFAULT NULL,
      `costo_renovacion` decimal(10,2) DEFAULT NULL,
      `fecha_creacion` timestamp DEFAULT CURRENT_TIMESTAMP,
      `fecha_actualizacion` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id_historial`),
      KEY `idx_historial_vehiculo` (`id_parque_automotor`),
      KEY `idx_historial_documento` (`tipo_documento`),
      KEY `idx_historial_vencimiento` (`fecha_vencimiento_nueva`),
      KEY `idx_historial_estado` (`estado_documento`),
      KEY `idx_historial_fecha_renovacion` (`fecha_renovacion`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """
    
    return ejecutar_sql(cursor, sql_crear_tabla, "Crear tabla historial_documentos_vehiculos")

def agregar_foreign_key_historial(cursor):
    """Agrega la foreign key a la tabla historial"""
    sql_foreign_key = """
    ALTER TABLE `historial_documentos_vehiculos` 
    ADD CONSTRAINT `fk_historial_vehiculo` 
    FOREIGN KEY (`id_parque_automotor`) 
    REFERENCES `parque_automotor` (`id_parque_automotor`) 
    ON DELETE CASCADE ON UPDATE CASCADE;
    """
    
    return ejecutar_sql(cursor, sql_foreign_key, "Agregar foreign key a historial_documentos_vehiculos")

def agregar_campos_inspeccion_fisica(cursor):
    """Agrega campos de inspección física a parque_automotor"""
    imprimir_separador("AGREGANDO CAMPOS DE INSPECCIÓN FÍSICA")
    
    campos_inspeccion = [
        ("estado_carroceria", "varchar(20) DEFAULT 'Bueno'"),
        ("estado_llantas", "varchar(20) DEFAULT 'Bueno'"),
        ("estado_frenos", "varchar(20) DEFAULT 'Bueno'"),
        ("estado_motor", "varchar(20) DEFAULT 'Bueno'"),
        ("estado_luces", "varchar(20) DEFAULT 'Bueno'"),
        ("estado_espejos", "varchar(20) DEFAULT 'Bueno'"),
        ("estado_vidrios", "varchar(20) DEFAULT 'Bueno'"),
        ("estado_asientos", "varchar(20) DEFAULT 'Bueno'"),
        ("estado_direccion", "varchar(20) DEFAULT 'Bueno'"),
        ("estado_suspension", "varchar(20) DEFAULT 'Bueno'"),
        ("estado_escape", "varchar(20) DEFAULT 'Bueno'"),
        ("estado_bateria", "varchar(20) DEFAULT 'Bueno'"),
        ("nivel_aceite_motor", "varchar(20) DEFAULT 'Bueno'"),
        ("nivel_liquido_frenos", "varchar(20) DEFAULT 'Bueno'"),
        ("nivel_refrigerante", "varchar(20) DEFAULT 'Bueno'"),
        ("presion_llantas", "varchar(20) DEFAULT 'Bueno'")
    ]
    
    exitos = 0
    for campo, tipo in campos_inspeccion:
        sql = f"ALTER TABLE `parque_automotor` ADD COLUMN `{campo}` {tipo};"
        if ejecutar_sql(cursor, sql, f"Agregar campo {campo}"):
            exitos += 1
    
    print(f"\n📊 Campos de inspección física: {exitos}/{len(campos_inspeccion)} agregados")
    return exitos == len(campos_inspeccion)

def agregar_campos_elementos_seguridad(cursor):
    """Agrega campos de elementos de seguridad a parque_automotor"""
    imprimir_separador("AGREGANDO CAMPOS DE ELEMENTOS DE SEGURIDAD")
    
    campos_seguridad = [
        ("cinturon_seguridad", "varchar(5) DEFAULT 'Sí'"),
        ("extintor", "varchar(5) DEFAULT 'Sí'"),
        ("botiquin", "varchar(5) DEFAULT 'Sí'"),
        ("triangulos_seguridad", "varchar(5) DEFAULT 'Sí'"),
        ("llanta_repuesto", "varchar(5) DEFAULT 'Sí'"),
        ("herramientas", "varchar(5) DEFAULT 'Sí'"),
        ("gato", "varchar(5) DEFAULT 'Sí'"),
        ("cruceta", "varchar(5) DEFAULT 'Sí'"),
        ("chaleco_reflectivo", "varchar(5) DEFAULT 'Sí'"),
        ("linterna", "varchar(5) DEFAULT 'Sí'"),
        ("cables_arranque", "varchar(5) DEFAULT 'No'"),
        ("kit_carretera", "varchar(5) DEFAULT 'Sí'")
    ]
    
    exitos = 0
    for campo, tipo in campos_seguridad:
        sql = f"ALTER TABLE `parque_automotor` ADD COLUMN `{campo}` {tipo};"
        if ejecutar_sql(cursor, sql, f"Agregar campo {campo}"):
            exitos += 1
    
    print(f"\n📊 Campos de elementos de seguridad: {exitos}/{len(campos_seguridad)} agregados")
    return exitos == len(campos_seguridad)

def agregar_campos_operativos(cursor):
    """Agrega campos operativos adicionales a parque_automotor"""
    imprimir_separador("AGREGANDO CAMPOS OPERATIVOS ADICIONALES")
    
    campos_operativos = [
        ("centro_de_trabajo", "varchar(100) DEFAULT NULL"),
        ("ciudad", "varchar(50) DEFAULT NULL"),
        ("supervisor", "varchar(100) DEFAULT NULL"),
        ("observaciones", "text DEFAULT NULL"),
        ("fecha_ultima_inspeccion", "date DEFAULT NULL"),
        ("proxima_inspeccion", "date DEFAULT NULL"),
        ("estado_general", "varchar(20) DEFAULT 'Bueno'"),
        ("requiere_mantenimiento", "varchar(5) DEFAULT 'No'"),
        ("fecha_ingreso_taller", "date DEFAULT NULL"),
        ("fecha_salida_taller", "date DEFAULT NULL"),
        ("costo_ultimo_mantenimiento", "decimal(10,2) DEFAULT NULL"),
        ("taller_mantenimiento", "varchar(100) DEFAULT NULL")
    ]
    
    exitos = 0
    for campo, tipo in campos_operativos:
        sql = f"ALTER TABLE `parque_automotor` ADD COLUMN `{campo}` {tipo};"
        if ejecutar_sql(cursor, sql, f"Agregar campo {campo}"):
            exitos += 1
    
    print(f"\n📊 Campos operativos adicionales: {exitos}/{len(campos_operativos)} agregados")
    return exitos == len(campos_operativos)

def crear_indices_adicionales(cursor):
    """Crea índices adicionales para optimizar consultas"""
    imprimir_separador("CREANDO ÍNDICES ADICIONALES")
    
    indices = [
        ("idx_parque_automotor_centro_trabajo", "parque_automotor", "centro_de_trabajo"),
        ("idx_parque_automotor_ciudad", "parque_automotor", "ciudad"),
        ("idx_parque_automotor_supervisor", "parque_automotor", "supervisor"),
        ("idx_parque_automotor_estado_general", "parque_automotor", "estado_general"),
        ("idx_parque_automotor_ultima_inspeccion", "parque_automotor", "fecha_ultima_inspeccion"),
        ("idx_parque_automotor_proxima_inspeccion", "parque_automotor", "proxima_inspeccion"),
        ("idx_parque_automotor_mantenimiento", "parque_automotor", "requiere_mantenimiento")
    ]
    
    exitos = 0
    for nombre_indice, tabla, campo in indices:
        sql = f"CREATE INDEX `{nombre_indice}` ON `{tabla}` (`{campo}`);"
        if ejecutar_sql(cursor, sql, f"Crear índice {nombre_indice}"):
            exitos += 1
    
    print(f"\n📊 Índices adicionales: {exitos}/{len(indices)} creados")
    return exitos == len(indices)

def insertar_datos_iniciales_historial(cursor):
    """Inserta datos iniciales en la tabla historial basados en datos existentes"""
    imprimir_separador("INSERTANDO DATOS INICIALES EN HISTORIAL")
    
    # Migrar datos de SOAT existentes
    sql_soat = """
    INSERT INTO historial_documentos_vehiculos 
    (id_parque_automotor, tipo_documento, fecha_vencimiento_nueva, observaciones)
    SELECT 
        id_parque_automotor,
        'SOAT' as tipo_documento,
        soat_vencimiento as fecha_vencimiento_nueva,
        'Migración automática de datos existentes' as observaciones
    FROM parque_automotor 
    WHERE soat_vencimiento IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM historial_documentos_vehiculos h 
        WHERE h.id_parque_automotor = parque_automotor.id_parque_automotor 
        AND h.tipo_documento = 'SOAT'
    );
    """
    
    # Migrar datos de Tecnomecánica existentes
    sql_tecnomecanica = """
    INSERT INTO historial_documentos_vehiculos 
    (id_parque_automotor, tipo_documento, fecha_vencimiento_nueva, observaciones)
    SELECT 
        id_parque_automotor,
        'Tecnomecánica' as tipo_documento,
        tecnomecanica_vencimiento as fecha_vencimiento_nueva,
        'Migración automática de datos existentes' as observaciones
    FROM parque_automotor 
    WHERE tecnomecanica_vencimiento IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM historial_documentos_vehiculos h 
        WHERE h.id_parque_automotor = parque_automotor.id_parque_automotor 
        AND h.tipo_documento = 'Tecnomecánica'
    );
    """
    
    # Migrar datos de Póliza existentes
    sql_poliza = """
    INSERT INTO historial_documentos_vehiculos 
    (id_parque_automotor, tipo_documento, fecha_vencimiento_nueva, observaciones)
    SELECT 
        id_parque_automotor,
        'Póliza de Seguro' as tipo_documento,
        vencimiento_poliza as fecha_vencimiento_nueva,
        'Migración automática de datos existentes' as observaciones
    FROM parque_automotor 
    WHERE vencimiento_poliza IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM historial_documentos_vehiculos h 
        WHERE h.id_parque_automotor = parque_automotor.id_parque_automotor 
        AND h.tipo_documento = 'Póliza de Seguro'
    );
    """
    
    exitos = 0
    if ejecutar_sql(cursor, sql_soat, "Migrar datos de SOAT al historial"):
        exitos += 1
    if ejecutar_sql(cursor, sql_tecnomecanica, "Migrar datos de Tecnomecánica al historial"):
        exitos += 1
    if ejecutar_sql(cursor, sql_poliza, "Migrar datos de Póliza al historial"):
        exitos += 1
    
    # Obtener estadísticas de migración
    try:
        cursor.execute("SELECT COUNT(*) FROM historial_documentos_vehiculos;")
        total_registros = cursor.fetchone()[0]
        print(f"\n📊 Total de registros en historial: {total_registros}")
        
        cursor.execute("""
            SELECT tipo_documento, COUNT(*) as cantidad 
            FROM historial_documentos_vehiculos 
            GROUP BY tipo_documento;
        """)
        estadisticas = cursor.fetchall()
        
        print("\n📋 Distribución por tipo de documento:")
        for tipo, cantidad in estadisticas:
            print(f"   • {tipo}: {cantidad} registros")
            
    except Error as e:
        print(f"⚠️  Error obteniendo estadísticas: {e}")
    
    return exitos == 3

def verificar_correcciones(cursor):
    """Verifica que todas las correcciones se hayan aplicado correctamente"""
    imprimir_separador("VERIFICANDO CORRECCIONES IMPLEMENTADAS")
    
    verificaciones = []
    
    # Verificar tabla historial_documentos_vehiculos
    try:
        cursor.execute("SHOW TABLES LIKE 'historial_documentos_vehiculos';")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM historial_documentos_vehiculos;")
            count = cursor.fetchone()[0]
            verificaciones.append(("Tabla historial_documentos_vehiculos", True, f"{count} registros"))
        else:
            verificaciones.append(("Tabla historial_documentos_vehiculos", False, "No existe"))
    except Error as e:
        verificaciones.append(("Tabla historial_documentos_vehiculos", False, str(e)))
    
    # Verificar campos agregados a parque_automotor
    campos_verificar = [
        'estado_carroceria', 'estado_llantas', 'estado_frenos', 'estado_motor',
        'cinturon_seguridad', 'extintor', 'botiquin', 'triangulos_seguridad',
        'centro_de_trabajo', 'ciudad', 'supervisor', 'observaciones'
    ]
    
    try:
        cursor.execute("DESCRIBE parque_automotor;")
        campos_existentes = [campo[0] for campo in cursor.fetchall()]
        
        campos_encontrados = 0
        for campo in campos_verificar:
            if campo in campos_existentes:
                campos_encontrados += 1
        
        verificaciones.append((
            "Campos agregados a parque_automotor", 
            campos_encontrados == len(campos_verificar),
            f"{campos_encontrados}/{len(campos_verificar)} campos"
        ))
        
    except Error as e:
        verificaciones.append(("Campos agregados a parque_automotor", False, str(e)))
    
    # Verificar foreign keys
    try:
        cursor.execute("""
            SELECT CONSTRAINT_NAME 
            FROM information_schema.TABLE_CONSTRAINTS 
            WHERE TABLE_SCHEMA = 'capired' 
            AND TABLE_NAME = 'historial_documentos_vehiculos' 
            AND CONSTRAINT_TYPE = 'FOREIGN KEY';
        """)
        fks = cursor.fetchall()
        verificaciones.append((
            "Foreign keys en historial", 
            len(fks) > 0,
            f"{len(fks)} foreign keys"
        ))
    except Error as e:
        verificaciones.append(("Foreign keys en historial", False, str(e)))
    
    # Mostrar resultados
    print("\n📋 RESULTADOS DE VERIFICACIÓN:")
    exitos = 0
    for descripcion, exito, detalle in verificaciones:
        estado = "✅" if exito else "❌"
        print(f"   {estado} {descripcion}: {detalle}")
        if exito:
            exitos += 1
    
    print(f"\n📊 Verificaciones exitosas: {exitos}/{len(verificaciones)}")
    return exitos == len(verificaciones)

def main():
    """Función principal"""
    print("🚀 INICIANDO CORRECCIONES CRÍTICAS DEL MÓDULO AUTOMOTOR")
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    connection = None
    
    try:
        # Conectar a MySQL
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        
        if not connection.is_connected():
            print("❌ No se pudo conectar a MySQL")
            return False
        
        print(f"✅ Conectado a MySQL Server")
        cursor = connection.cursor(buffered=True)
        
        # Ejecutar correcciones en orden
        pasos = [
            (crear_tabla_historial_documentos, "Crear tabla historial_documentos_vehiculos"),
            (agregar_foreign_key_historial, "Agregar foreign key a historial"),
            (agregar_campos_inspeccion_fisica, "Agregar campos de inspección física"),
            (agregar_campos_elementos_seguridad, "Agregar campos de elementos de seguridad"),
            (agregar_campos_operativos, "Agregar campos operativos adicionales"),
            (crear_indices_adicionales, "Crear índices adicionales"),
            (insertar_datos_iniciales_historial, "Insertar datos iniciales en historial"),
            (verificar_correcciones, "Verificar correcciones implementadas")
        ]
        
        exitos = 0
        for i, (funcion, descripcion) in enumerate(pasos, 1):
            print(f"\n🔄 PASO {i}/{len(pasos)}: {descripcion}")
            if funcion(cursor):
                exitos += 1
                print(f"✅ PASO {i} COMPLETADO")
            else:
                print(f"❌ PASO {i} FALLÓ")
            
            # Commit después de cada paso exitoso
            if exitos == i:
                connection.commit()
        
        # Resultado final
        imprimir_separador("RESULTADO FINAL")
        print(f"📊 Pasos completados: {exitos}/{len(pasos)}")
        print(f"📈 Porcentaje de éxito: {(exitos/len(pasos))*100:.1f}%")
        
        if exitos == len(pasos):
            print("\n🎉 ¡TODAS LAS CORRECCIONES IMPLEMENTADAS EXITOSAMENTE!")
            print("✅ El módulo automotor está listo para funcionar completamente")
            return True
        else:
            print(f"\n⚠️  SE COMPLETARON {exitos} DE {len(pasos)} CORRECCIONES")
            print("🔧 Revisar los errores anteriores y ejecutar nuevamente")
            return False
        
    except Error as e:
        print(f"\n💥 ERROR CRÍTICO: {e}")
        return False
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión MySQL cerrada")
        
        print(f"⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Correcciones interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)