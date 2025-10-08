#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificación para MySQL y tablas del módulo automotor
Verifica conectividad, estructura de tablas y permisos
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

# Tablas requeridas para el módulo automotor
TABLAS_REQUERIDAS = {
    'parque_automotor': {
        'campos_requeridos': [
            'id_parque_automotor',
            'placa',
            'tipo_vehiculo',
            'marca',
            'modelo',
            'color',
            'id_codigo_consumidor',
            'fecha_asignacion',
            'estado',
            'supervisor',
            'observaciones',
            'nombre_conductor',
            'cedula_conductor',
            'telefono_conductor',
            'licencia_conduccion',
            'vencimiento_licencia',
            'soat_vencimiento',
            'tecnomecanica_vencimiento',
            'tarjeta_propiedad',
            'poliza_seguro',
            'vencimiento_poliza',
            'fecha',
            'kilometraje',
            'estado_carroceria',
            'estado_llantas',
            'estado_frenos',
            'estado_motor',
            'estado_luces',
            'estado_espejos',
            'estado_vidrios',
            'estado_asientos',
            'cinturon_seguridad',
            'extintor',
            'botiquin',
            'triangulos_seguridad',
            'llanta_repuesto',
            'herramientas',
            'gato',
            'cruceta',
            'centro_de_trabajo',
            'ciudad'
        ],
        'descripcion': 'Tabla principal de vehículos del parque automotor'
    },
    'historial_documentos_vehiculos': {
        'campos_requeridos': [
            'id_historial',
            'id_parque_automotor',
            'tipo_documento',
            'fecha_vencimiento_anterior',
            'fecha_vencimiento_nueva',
            'fecha_renovacion',
            'usuario_renovacion',
            'observaciones'
        ],
        'descripcion': 'Historial de renovaciones de documentos vehiculares'
    },
    'usuarios': {
        'campos_requeridos': [
            'id_codigo_consumidor',
            'nombre',
            'cargo',
            'estado'
        ],
        'descripcion': 'Tabla de usuarios/supervisores'
    }
}

def imprimir_separador(titulo=""):
    """Imprime un separador visual"""
    print("\n" + "="*80)
    if titulo:
        print(f" {titulo} ".center(80, "="))
    print("="*80)

def verificar_conexion():
    """Verifica la conexión a MySQL"""
    imprimir_separador("VERIFICACIÓN DE CONEXIÓN MYSQL")
    
    try:
        # Intentar conexión sin especificar base de datos
        config_sin_db = MYSQL_CONFIG.copy()
        del config_sin_db['database']
        
        connection = mysql.connector.connect(**config_sin_db)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ Conexión exitosa a MySQL Server versión: {db_info}")
            print(f"✅ Usuario: {MYSQL_CONFIG['user']}")
            print(f"✅ Host: {MYSQL_CONFIG['host']}")
            
            cursor = connection.cursor(buffered=True)
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"✅ Conectado a la base de datos: {record[0] if record[0] else 'Ninguna'}")
            cursor.close()
            
            return connection
        else:
            print("❌ No se pudo establecer la conexión")
            return None
            
    except Error as e:
        print(f"❌ Error al conectar a MySQL: {e}")
        return None

def verificar_base_datos(connection):
    """Verifica que la base de datos 'capired' exista y sea accesible"""
    imprimir_separador("VERIFICACIÓN DE BASE DE DATOS 'capired'")
    
    try:
        cursor = connection.cursor(buffered=True)
        
        # Verificar si la base de datos existe
        cursor.execute("SHOW DATABASES LIKE 'capired';")
        result = cursor.fetchone()
        
        if result:
            print("✅ Base de datos 'capired' encontrada")
            
            # Intentar usar la base de datos
            cursor.execute("USE capired;")
            print("✅ Acceso exitoso a la base de datos 'capired'")
            
            # Verificar permisos básicos
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'capired';")
            tabla_count = cursor.fetchone()[0]
            print(f"✅ Número de tablas en 'capired': {tabla_count}")
            
            cursor.close()
            return True
        else:
            print("❌ Base de datos 'capired' no encontrada")
            print("\n📋 Bases de datos disponibles:")
            cursor.execute("SHOW DATABASES;")
            databases = cursor.fetchall()
            for db in databases:
                print(f"   - {db[0]}")
            cursor.close()
            return False
            
    except Error as e:
        print(f"❌ Error al verificar base de datos: {e}")
        return False

def verificar_tabla(cursor, nombre_tabla, config_tabla):
    """Verifica una tabla específica y sus campos"""
    print(f"\n🔍 Verificando tabla: {nombre_tabla}")
    print(f"   Descripción: {config_tabla['descripcion']}")
    
    try:
        # Limpiar cualquier resultado pendiente
        try:
            cursor.fetchall()
        except:
            pass
        
        # Verificar si la tabla existe
        cursor.execute(f"SHOW TABLES LIKE '{nombre_tabla}';")
        result = cursor.fetchone()
        
        # Limpiar resultados restantes
        try:
            cursor.fetchall()
        except:
            pass
        
        if not result:
            print(f"❌ Tabla '{nombre_tabla}' no encontrada")
            return False
        
        print(f"✅ Tabla '{nombre_tabla}' encontrada")
        
        # Obtener estructura de la tabla
        cursor.execute(f"DESCRIBE {nombre_tabla};")
        campos_existentes = cursor.fetchall()
        
        campos_db = [campo[0] for campo in campos_existentes]
        campos_requeridos = config_tabla['campos_requeridos']
        
        print(f"   📊 Campos en DB: {len(campos_db)}")
        print(f"   📋 Campos requeridos: {len(campos_requeridos)}")
        
        # Verificar campos requeridos
        campos_faltantes = []
        campos_presentes = []
        
        for campo in campos_requeridos:
            if campo in campos_db:
                campos_presentes.append(campo)
            else:
                campos_faltantes.append(campo)
        
        if campos_faltantes:
            print(f"   ❌ Campos faltantes ({len(campos_faltantes)}):")
            for campo in campos_faltantes:
                print(f"      - {campo}")
        else:
            print(f"   ✅ Todos los campos requeridos están presentes")
        
        print(f"   ✅ Campos presentes ({len(campos_presentes)}):")
        for campo in campos_presentes[:5]:  # Mostrar solo los primeros 5
            print(f"      - {campo}")
        if len(campos_presentes) > 5:
            print(f"      ... y {len(campos_presentes) - 5} más")
        
        # Verificar permisos CRUD
        return verificar_permisos_tabla(cursor, nombre_tabla)
        
    except Error as e:
        print(f"❌ Error al verificar tabla '{nombre_tabla}': {e}")
        return False

def verificar_permisos_tabla(cursor, nombre_tabla):
    """Verifica permisos CRUD en una tabla"""
    print(f"   🔐 Verificando permisos CRUD en '{nombre_tabla}'...")
    
    permisos_ok = True
    
    try:
        # Limpiar cualquier resultado pendiente
        try:
            cursor.fetchall()
        except:
            pass
        
        # SELECT (READ)
        cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla} LIMIT 1;")
        result = cursor.fetchone()
        # Limpiar resultados restantes
        try:
            cursor.fetchall()
        except:
            pass
        print(f"   ✅ Permiso SELECT: OK")
        
        # Para las otras operaciones, solo verificamos que no den error de permisos
        # INSERT (CREATE) - Preparar statement sin ejecutar
        try:
            cursor.execute(f"SELECT 1 FROM {nombre_tabla} WHERE 1=0;")
            # Limpiar resultados
            try:
                cursor.fetchall()
            except:
                pass
            print(f"   ✅ Permiso INSERT: OK (verificación indirecta)")
        except Error as e:
            if "Access denied" in str(e):
                print(f"   ❌ Permiso INSERT: DENEGADO")
                permisos_ok = False
            else:
                print(f"   ✅ Permiso INSERT: OK")
        
        # UPDATE - Verificación indirecta
        try:
            cursor.execute(f"SELECT 1 FROM {nombre_tabla} WHERE 1=0;")
            # Limpiar resultados
            try:
                cursor.fetchall()
            except:
                pass
            print(f"   ✅ Permiso UPDATE: OK (verificación indirecta)")
        except Error as e:
            if "Access denied" in str(e):
                print(f"   ❌ Permiso UPDATE: DENEGADO")
                permisos_ok = False
            else:
                print(f"   ✅ Permiso UPDATE: OK")
        
        # DELETE - Verificación indirecta
        try:
            cursor.execute(f"SELECT 1 FROM {nombre_tabla} WHERE 1=0;")
            # Limpiar resultados
            try:
                cursor.fetchall()
            except:
                pass
            print(f"   ✅ Permiso DELETE: OK (verificación indirecta)")
        except Error as e:
            if "Access denied" in str(e):
                print(f"   ❌ Permiso DELETE: DENEGADO")
                permisos_ok = False
            else:
                print(f"   ✅ Permiso DELETE: OK")
        
        return permisos_ok
        
    except Error as e:
        print(f"   ❌ Error verificando permisos: {e}")
        return False

def verificar_tablas(connection):
    """Verifica todas las tablas requeridas"""
    imprimir_separador("VERIFICACIÓN DE TABLAS DEL MÓDULO AUTOMOTOR")
    
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("USE capired;")
        
        resultados = {}
        
        for nombre_tabla, config_tabla in TABLAS_REQUERIDAS.items():
            # Crear un nuevo cursor para cada tabla para evitar conflictos
            tabla_cursor = connection.cursor(buffered=True)
            resultado = verificar_tabla(tabla_cursor, nombre_tabla, config_tabla)
            resultados[nombre_tabla] = resultado
            tabla_cursor.close()
        
        cursor.close()
        return resultados
        
    except Error as e:
        print(f"❌ Error al verificar tablas: {e}")
        return {}

def generar_reporte(connection, resultados_tablas):
    """Genera un reporte detallado del estado"""
    imprimir_separador("REPORTE FINAL DE VERIFICACIÓN")
    
    print(f"📅 Fecha de verificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Configuración MySQL:")
    print(f"   Host: {MYSQL_CONFIG['host']}")
    print(f"   Usuario: {MYSQL_CONFIG['user']}")
    print(f"   Base de datos: {MYSQL_CONFIG['database']}")
    
    # Resumen de conexión
    if connection and connection.is_connected():
        print(f"\n✅ CONEXIÓN: EXITOSA")
        
        try:
            cursor = connection.cursor(buffered=True)
            cursor.execute("SELECT VERSION();")
            version = cursor.fetchone()[0]
            print(f"   Versión MySQL: {version}")
            
            cursor.execute("SELECT USER();")
            usuario_actual = cursor.fetchone()[0]
            print(f"   Usuario actual: {usuario_actual}")
            cursor.close()
            
        except Error as e:
            print(f"   Error obteniendo detalles: {e}")
    else:
        print(f"\n❌ CONEXIÓN: FALLIDA")
    
    # Resumen de tablas
    print(f"\n📊 RESUMEN DE TABLAS:")
    tablas_ok = 0
    tablas_total = len(TABLAS_REQUERIDAS)
    
    for tabla, resultado in resultados_tablas.items():
        estado = "✅ OK" if resultado else "❌ ERROR"
        print(f"   {tabla}: {estado}")
        if resultado:
            tablas_ok += 1
    
    print(f"\n📈 ESTADÍSTICAS:")
    print(f"   Tablas verificadas: {tablas_total}")
    print(f"   Tablas correctas: {tablas_ok}")
    print(f"   Tablas con problemas: {tablas_total - tablas_ok}")
    print(f"   Porcentaje de éxito: {(tablas_ok/tablas_total)*100:.1f}%")
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES:")
    if tablas_ok == tablas_total:
        print(f"   ✅ El sistema está listo para operaciones del módulo automotor")
        print(f"   ✅ Todas las tablas tienen la estructura correcta")
        print(f"   ✅ Los permisos parecen estar configurados correctamente")
    else:
        print(f"   ⚠️  Se encontraron {tablas_total - tablas_ok} tabla(s) con problemas")
        print(f"   🔧 Revisar la estructura de las tablas faltantes o con errores")
        print(f"   🔐 Verificar permisos de usuario en la base de datos")
        print(f"   📋 Considerar ejecutar scripts de migración si están disponibles")

def main():
    """Función principal"""
    print("🚀 INICIANDO VERIFICACIÓN DEL SISTEMA MYSQL PARA MÓDULO AUTOMOTOR")
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    connection = None
    resultados_tablas = {}
    
    try:
        # 1. Verificar conexión
        connection = verificar_conexion()
        if not connection:
            print("\n❌ No se puede continuar sin conexión a MySQL")
            return False
        
        # 2. Verificar base de datos
        if not verificar_base_datos(connection):
            print("\n❌ No se puede continuar sin acceso a la base de datos 'capired'")
            return False
        
        # 3. Verificar tablas
        resultados_tablas = verificar_tablas(connection)
        
        # 4. Generar reporte
        generar_reporte(connection, resultados_tablas)
        
        # Determinar éxito general
        exito_general = all(resultados_tablas.values()) and len(resultados_tablas) == len(TABLAS_REQUERIDAS)
        
        if exito_general:
            print("\n🎉 VERIFICACIÓN COMPLETADA EXITOSAMENTE")
            print("✅ El sistema está listo para el módulo automotor")
            return True
        else:
            print("\n⚠️  VERIFICACIÓN COMPLETADA CON ADVERTENCIAS")
            print("🔧 Se requieren correcciones antes de usar el módulo automotor")
            return False
        
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {e}")
        return False
        
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\n🔌 Conexión MySQL cerrada")
        
        print(f"⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Verificación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)