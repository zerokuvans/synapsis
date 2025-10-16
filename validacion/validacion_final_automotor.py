#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validación final: Verificar que los campos críticos del formulario estén sincronizados con la DB
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

# Campos críticos del formulario que deben existir en la DB
CAMPOS_CRITICOS = {
    'placa': 'Placa del vehículo',
    'tipo_vehiculo': 'Tipo de vehículo',
    'vehiculo_asistio_operacion': 'Vehículo asistió a operación',
    'marca': 'Marca del vehículo',
    'modelo': 'Modelo del vehículo',
    'color': 'Color del vehículo',
    'id_codigo_consumidor': 'ID del conductor',
    'fecha_asignacion': 'Fecha de asignación',
    'licencia_conduccion': 'Licencia de conducción',
    'vencimiento_licencia': 'Vencimiento de licencia',
    'estado': 'Estado del vehículo',
    'soat_vencimiento': 'Vencimiento SOAT',
    'tecnomecanica_vencimiento': 'Vencimiento Tecnomecánica',
    'estado_carroceria': 'Estado carrocería',
    'estado_llantas': 'Estado llantas',
    'estado_frenos': 'Estado frenos',
    'estado_motor': 'Estado motor',
    'estado_luces': 'Estado luces',
    'estado_espejos': 'Estado espejos',
    'estado_vidrios': 'Estado vidrios',
    'estado_asientos': 'Estado asientos',
    'cinturon_seguridad': 'Cinturón de seguridad',
    'extintor': 'Extintor',
    'botiquin': 'Botiquín',
    'triangulos_seguridad': 'Triángulos de seguridad',
    'llanta_repuesto': 'Llanta de repuesto',
    'herramientas': 'Herramientas',
    'gato': 'Gato',
    'cruceta': 'Cruceta',
    'centro_de_trabajo': 'Centro de trabajo',
    'ciudad': 'Ciudad',
    'supervisor': 'Supervisor',
    'fecha': 'Fecha',
    'kilometraje': 'Kilometraje',
    'observaciones': 'Observaciones'
}

def imprimir_separador(titulo=""):
    """Imprime un separador visual"""
    print("\n" + "="*80)
    if titulo:
        print(f" {titulo} ".center(80, "="))
    print("="*80)

def obtener_estructura_tabla():
    """Obtiene la estructura actual de la tabla parque_automotor"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(buffered=True)
        
        cursor.execute("DESCRIBE parque_automotor;")
        campos_db = cursor.fetchall()
        
        estructura = {}
        for campo in campos_db:
            field, type_info, null, key, default, extra = campo
            estructura[field] = {
                'tipo': type_info,
                'null': null == 'YES',
                'key': key,
                'default': default,
                'extra': extra
            }
        
        cursor.close()
        connection.close()
        
        return estructura
        
    except Error as e:
        print(f"Error obteniendo estructura de tabla: {e}")
        return {}

def validar_campos_criticos():
    """Valida que todos los campos críticos existan en la base de datos"""
    imprimir_separador("VALIDACIÓN FINAL DE CAMPOS CRÍTICOS")
    
    estructura_db = obtener_estructura_tabla()
    
    if not estructura_db:
        print("❌ No se pudo obtener la estructura de la base de datos")
        return False
    
    print(f"📊 Total de campos en la tabla: {len(estructura_db)}")
    print(f"📊 Campos críticos a validar: {len(CAMPOS_CRITICOS)}")
    
    campos_ok = 0
    campos_faltantes = []
    
    print("\n🔍 Validando campos críticos:")
    
    for campo_db, descripcion in CAMPOS_CRITICOS.items():
        if campo_db in estructura_db:
            tipo_db = estructura_db[campo_db]['tipo']
            print(f"  ✅ {campo_db:<30} ({tipo_db}) - {descripcion}")
            campos_ok += 1
        else:
            print(f"  ❌ {campo_db:<30} - FALTANTE - {descripcion}")
            campos_faltantes.append(campo_db)
    
    # Mostrar resultados
    print(f"\n📈 RESULTADOS:")
    print(f"  ✅ Campos encontrados: {campos_ok}/{len(CAMPOS_CRITICOS)} ({(campos_ok/len(CAMPOS_CRITICOS)*100):.1f}%)")
    print(f"  ❌ Campos faltantes: {len(campos_faltantes)}")
    
    if campos_faltantes:
        print(f"\n❌ CAMPOS FALTANTES:")
        for campo in campos_faltantes:
            print(f"  - {campo} ({CAMPOS_CRITICOS[campo]})")
        return False
    else:
        print(f"\n🎯 ¡TODOS LOS CAMPOS CRÍTICOS ESTÁN PRESENTES!")
        return True

def verificar_indices_optimizacion():
    """Verifica que los índices de optimización estén creados"""
    imprimir_separador("VERIFICACIÓN DE ÍNDICES DE OPTIMIZACIÓN")
    
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(buffered=True)
        
        cursor.execute("""
        SELECT INDEX_NAME, COLUMN_NAME, NON_UNIQUE
        FROM INFORMATION_SCHEMA.STATISTICS 
        WHERE TABLE_SCHEMA = 'capired' 
        AND TABLE_NAME = 'parque_automotor'
        AND INDEX_NAME != 'PRIMARY'
        ORDER BY INDEX_NAME, SEQ_IN_INDEX
        """)
        
        indices = cursor.fetchall()
        
        print(f"📊 Total de índices encontrados: {len(set([idx[0] for idx in indices]))}")
        
        # Agrupar índices
        indices_agrupados = {}
        for indice in indices:
            nombre_indice, columna, no_unico = indice
            if nombre_indice not in indices_agrupados:
                indices_agrupados[nombre_indice] = []
            indices_agrupados[nombre_indice].append(columna)
        
        print("\n📋 Índices creados:")
        for nombre_indice, columnas in indices_agrupados.items():
            columnas_str = ', '.join(columnas)
            print(f"  ✅ {nombre_indice:<40} ({columnas_str})")
        
        # Verificar índices críticos
        indices_criticos = [
            'idx_vehiculo_asistio_operacion',
            'idx_licencia_conduccion',
            'idx_vencimiento_licencia'
        ]
        
        print("\n🔍 Verificando índices críticos agregados:")
        indices_criticos_ok = 0
        for indice_critico in indices_criticos:
            if indice_critico in indices_agrupados:
                print(f"  ✅ {indice_critico} - OK")
                indices_criticos_ok += 1
            else:
                print(f"  ❌ {indice_critico} - FALTANTE")
        
        cursor.close()
        connection.close()
        
        return indices_criticos_ok == len(indices_criticos)
        
    except Error as e:
        print(f"❌ Error verificando índices: {e}")
        return False

def verificar_datos_muestra():
    """Verifica una muestra de datos para confirmar que los campos funcionan"""
    imprimir_separador("VERIFICACIÓN DE DATOS DE MUESTRA")
    
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(buffered=True)
        
        # Contar registros totales
        cursor.execute("SELECT COUNT(*) FROM parque_automotor")
        total_registros = cursor.fetchone()[0]
        print(f"📊 Total de registros en la tabla: {total_registros}")
        
        # Verificar campos críticos agregados
        cursor.execute("""
        SELECT 
            COUNT(CASE WHEN vehiculo_asistio_operacion IS NOT NULL THEN 1 END) as con_asistio,
            COUNT(CASE WHEN licencia_conduccion IS NOT NULL THEN 1 END) as con_licencia,
            COUNT(CASE WHEN vencimiento_licencia IS NOT NULL THEN 1 END) as con_vencimiento
        FROM parque_automotor
        """)
        
        estadisticas = cursor.fetchone()
        print(f"\n📈 Estadísticas de campos agregados:")
        print(f"  📊 Con vehiculo_asistio_operacion: {estadisticas[0]}/{total_registros}")
        print(f"  📊 Con licencia_conduccion: {estadisticas[1]}/{total_registros}")
        print(f"  📊 Con vencimiento_licencia: {estadisticas[2]}/{total_registros}")
        
        # Mostrar muestra de datos
        cursor.execute("""
        SELECT 
            placa, 
            vehiculo_asistio_operacion, 
            licencia_conduccion, 
            vencimiento_licencia,
            estado
        FROM parque_automotor 
        LIMIT 3
        """)
        
        muestra = cursor.fetchall()
        print(f"\n📋 Muestra de datos (primeros 3 registros):")
        for i, registro in enumerate(muestra, 1):
            placa, asistio, licencia, vencimiento, estado = registro
            print(f"  {i}. Placa: {placa}, Asistió: {asistio}, Licencia: {licencia or 'N/A'}, Vencimiento: {vencimiento or 'N/A'}, Estado: {estado}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"❌ Error verificando datos: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 VALIDACIÓN FINAL: FORMULARIO AUTOMOTOR vs TABLA PARQUE_AUTOMOTOR")
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. Validar campos críticos
        campos_ok = validar_campos_criticos()
        
        # 2. Verificar índices
        indices_ok = verificar_indices_optimizacion()
        
        # 3. Verificar datos de muestra
        datos_ok = verificar_datos_muestra()
        
        # Resultado final
        imprimir_separador("RESULTADO FINAL")
        
        if campos_ok and indices_ok and datos_ok:
            print("🎯 ¡VALIDACIÓN EXITOSA!")
            print("✅ Todos los campos críticos del formulario existen en la base de datos")
            print("✅ Los índices de optimización están creados")
            print("✅ Los datos de muestra confirman el funcionamiento")
            print("✅ El formulario y la base de datos están completamente sincronizados")
            print("\n🚀 El módulo automotor está listo para producción")
            return True
        else:
            print("⚠️  VALIDACIÓN CON PROBLEMAS")
            if not campos_ok:
                print("❌ Algunos campos críticos faltan en la base de datos")
            if not indices_ok:
                print("❌ Algunos índices de optimización no están creados")
            if not datos_ok:
                print("❌ Problemas con los datos de muestra")
            return False
        
    except Exception as e:
        print(f"💥 Error durante la validación: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Validación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)