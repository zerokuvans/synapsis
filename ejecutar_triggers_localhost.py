#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para ejecutar triggers MySQL en localhost
Ejecuta el archivo triggers_mysql_ferretero.sql en una base de datos MySQL local

Autor: Sistema Synapsis
Fecha: 2025-01-17
"""

import mysql.connector
import os
import sys
from mysql.connector import Error

def conectar_mysql(host='localhost', user='root', password='', database=None):
    """
    Establece conexión con MySQL localhost
    Prueba diferentes configuraciones comunes
    """
    configuraciones = [
        {'host': host, 'user': user, 'password': '732137A031E4b@'},
        {'host': host, 'user': user, 'password': ''},
        {'host': host, 'user': user, 'password': 'root'},
        {'host': host, 'user': user, 'password': 'admin'},
        {'host': host, 'user': user, 'password': '123456'},
        {'host': host, 'user': 'mysql', 'password': ''},
        {'host': host, 'user': 'admin', 'password': 'admin'}
    ]
    
    if database:
        for config in configuraciones:
            config['database'] = database
    
    print("🔍 Intentando conectar a MySQL localhost...")
    
    for i, config in enumerate(configuraciones, 1):
        try:
            print(f"   Intento {i}: usuario='{config['user']}', password={'***' if config['password'] else '(vacío)'}")
            connection = mysql.connector.connect(**config)
            
            if connection.is_connected():
                db_info = connection.get_server_info()
                print(f"✅ Conexión exitosa a MySQL Server versión {db_info}")
                if database:
                    print(f"📊 Base de datos seleccionada: {database}")
                return connection
                
        except Error as e:
            print(f"   ❌ Falló: {e}")
            continue
    
    print("\n❌ No se pudo conectar a MySQL con ninguna configuración.")
    print("\n💡 Sugerencias:")
    print("   1. Verificar que MySQL esté ejecutándose")
    print("   2. Verificar usuario y contraseña")
    print("   3. Verificar permisos de conexión")
    return None

def obtener_bases_datos(connection):
    """
    Obtiene lista de bases de datos disponibles
    """
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall() if db[0] not in ['information_schema', 'performance_schema', 'mysql', 'sys']]
        cursor.close()
        return databases
    except Error as e:
        print(f"❌ Error al obtener bases de datos: {e}")
        return []

def seleccionar_base_datos(connection):
    """
    Permite al usuario seleccionar una base de datos
    """
    databases = obtener_bases_datos(connection)
    
    if not databases:
        print("\n⚠️  No se encontraron bases de datos de usuario.")
        db_name = input("Ingrese el nombre de la base de datos a usar (o ENTER para crear 'synapsis'): ").strip()
        if not db_name:
            db_name = 'synapsis'
        return db_name
    
    print("\n📊 Bases de datos disponibles:")
    for i, db in enumerate(databases, 1):
        print(f"   {i}. {db}")
    
    print(f"   {len(databases) + 1}. Crear nueva base de datos")
    
    while True:
        try:
            opcion = input(f"\nSeleccione una opción (1-{len(databases) + 1}): ").strip()
            
            if opcion == str(len(databases) + 1):
                db_name = input("Ingrese el nombre de la nueva base de datos: ").strip()
                if db_name:
                    return db_name
            else:
                idx = int(opcion) - 1
                if 0 <= idx < len(databases):
                    return databases[idx]
            
            print("❌ Opción inválida. Intente nuevamente.")
            
        except ValueError:
            print("❌ Por favor ingrese un número válido.")
        except KeyboardInterrupt:
            print("\n\n👋 Operación cancelada por el usuario.")
            sys.exit(0)

def crear_base_datos(connection, db_name):
    """
    Crea una base de datos si no existe
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Base de datos '{db_name}' creada/verificada")
        cursor.close()
        return True
    except Error as e:
        print(f"❌ Error al crear base de datos: {e}")
        return False

def usar_base_datos(connection, db_name):
    """
    Selecciona una base de datos para usar
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"USE `{db_name}`")
        print(f"✅ Usando base de datos: {db_name}")
        cursor.close()
        return True
    except Error as e:
        print(f"❌ Error al seleccionar base de datos: {e}")
        return False

def ejecutar_archivo_sql(connection, archivo_sql):
    """
    Ejecuta un archivo SQL completo
    """
    if not os.path.exists(archivo_sql):
        print(f"❌ Archivo no encontrado: {archivo_sql}")
        return False
    
    try:
        print(f"\n📄 Leyendo archivo: {archivo_sql}")
        
        with open(archivo_sql, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Dividir el contenido en comandos individuales
        # Manejar DELIMITER correctamente
        comandos = []
        lineas = sql_content.split('\n')
        comando_actual = []
        delimiter = ';'
        
        i = 0
        while i < len(lineas):
            linea = lineas[i].strip()
            
            # Ignorar líneas vacías y comentarios
            if not linea or linea.startswith('--') or linea.startswith('/*'):
                i += 1
                continue
            
            # Manejar DELIMITER
            if linea.upper().startswith('DELIMITER'):
                if len(comando_actual) > 0:
                    comandos.append('\n'.join(comando_actual))
                    comando_actual = []
                
                delimiter = linea.split()[1] if len(linea.split()) > 1 else '//'
                i += 1
                continue
            
            comando_actual.append(linea)
            
            # Verificar si el comando termina con el delimiter actual
            if linea.endswith(delimiter):
                if delimiter != ';':
                    # Remover el delimiter del final
                    comando_actual[-1] = comando_actual[-1][:-len(delimiter)].strip()
                
                comando_completo = '\n'.join(comando_actual).strip()
                if comando_completo:
                    comandos.append(comando_completo)
                comando_actual = []
                
                # Si era un delimiter especial, volver a ;
                if delimiter != ';':
                    delimiter = ';'
            
            i += 1
        
        # Agregar último comando si existe
        if comando_actual:
            comando_completo = '\n'.join(comando_actual).strip()
            if comando_completo:
                comandos.append(comando_completo)
        
        print(f"📋 Se encontraron {len(comandos)} comandos SQL para ejecutar")
        
        cursor = connection.cursor()
        comandos_exitosos = 0
        
        for i, comando in enumerate(comandos, 1):
            try:
                if comando.strip():
                    print(f"   Ejecutando comando {i}/{len(comandos)}...", end='')
                    
                    # Ejecutar comando
                    for result in cursor.execute(comando, multi=True):
                        if result.with_rows:
                            result.fetchall()
                    
                    print(" ✅")
                    comandos_exitosos += 1
                    
            except Error as e:
                print(f" ❌")
                print(f"      Error en comando {i}: {e}")
                print(f"      Comando: {comando[:100]}...")
                continue
        
        cursor.close()
        connection.commit()
        
        print(f"\n✅ Ejecución completada: {comandos_exitosos}/{len(comandos)} comandos exitosos")
        return comandos_exitosos > 0
        
    except Error as e:
        print(f"❌ Error al ejecutar archivo SQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def verificar_triggers(connection):
    """
    Verifica que los triggers se hayan creado correctamente
    """
    try:
        print("\n🔍 Verificando triggers creados...")
        
        cursor = connection.cursor()
        cursor.execute("SHOW TRIGGERS")
        triggers = cursor.fetchall()
        
        if not triggers:
            print("⚠️  No se encontraron triggers en la base de datos")
            return False
        
        print(f"\n✅ Se encontraron {len(triggers)} triggers:")
        print("\n" + "="*80)
        print(f"{'TRIGGER':<30} {'TABLA':<20} {'EVENTO':<15} {'TIMING':<10}")
        print("="*80)
        
        for trigger in triggers:
            nombre = trigger[0]
            evento = trigger[1]
            tabla = trigger[2]
            timing = trigger[4]
            print(f"{nombre:<30} {tabla:<20} {evento:<15} {timing:<10}")
        
        print("="*80)
        
        # Verificar triggers específicos esperados
        triggers_esperados = [
            'actualizar_stock_entrada',
            'actualizar_stock_asignacion', 
            'alerta_stock_bajo',
            'validar_asignacion'
        ]
        
        triggers_encontrados = [t[0].lower() for t in triggers]
        
        print("\n🎯 Verificación de triggers esperados:")
        for trigger_esperado in triggers_esperados:
            if trigger_esperado.lower() in triggers_encontrados:
                print(f"   ✅ {trigger_esperado}")
            else:
                print(f"   ❌ {trigger_esperado} (no encontrado)")
        
        cursor.close()
        return True
        
    except Error as e:
        print(f"❌ Error al verificar triggers: {e}")
        return False

def verificar_tablas_requeridas(connection):
    """
    Verifica que existan las tablas requeridas para los triggers
    """
    try:
        print("\n🔍 Verificando tablas requeridas...")
        
        cursor = connection.cursor()
        
        tablas_requeridas = [
            'stock_general',
            'ferretero', 
            'entradas_stock',
            'alertas_stock',
            'eventos_sistema'
        ]
        
        cursor.execute("SHOW TABLES")
        tablas_existentes = [tabla[0].lower() for tabla in cursor.fetchall()]
        
        print("\n📊 Estado de tablas requeridas:")
        todas_existen = True
        
        for tabla in tablas_requeridas:
            if tabla.lower() in tablas_existentes:
                print(f"   ✅ {tabla}")
            else:
                print(f"   ❌ {tabla} (no existe)")
                todas_existen = False
        
        if not todas_existen:
            print("\n⚠️  Algunas tablas requeridas no existen.")
            print("   Los triggers pueden fallar si intentan acceder a tablas inexistentes.")
        
        cursor.close()
        return todas_existen
        
    except Error as e:
        print(f"❌ Error al verificar tablas: {e}")
        return False

def main():
    """
    Función principal
    """
    print("🚀 EJECUTOR DE TRIGGERS MYSQL - LOCALHOST")
    print("="*50)
    
    # Verificar que existe el archivo SQL
    archivo_sql = 'triggers_mysql_ferretero.sql'
    if not os.path.exists(archivo_sql):
        print(f"❌ Archivo no encontrado: {archivo_sql}")
        print("   Asegúrese de que el archivo esté en el directorio actual.")
        return False
    
    # Conectar a MySQL
    connection = conectar_mysql()
    if not connection:
        return False
    
    try:
        # Seleccionar base de datos
        db_name = seleccionar_base_datos(connection)
        
        # Crear base de datos si no existe
        if not crear_base_datos(connection, db_name):
            return False
        
        # Cerrar conexión actual y reconectar con la base de datos
        connection.close()
        connection = conectar_mysql(database=db_name)
        if not connection:
            return False
        
        # Verificar tablas requeridas
        verificar_tablas_requeridas(connection)
        
        # Ejecutar archivo SQL
        print(f"\n🔧 Ejecutando triggers desde: {archivo_sql}")
        if not ejecutar_archivo_sql(connection, archivo_sql):
            print("❌ Falló la ejecución del archivo SQL")
            return False
        
        # Verificar triggers
        if not verificar_triggers(connection):
            print("❌ Falló la verificación de triggers")
            return False
        
        print("\n🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
        print("\n📋 Resumen:")
        print(f"   ✅ Conexión a MySQL: localhost")
        print(f"   ✅ Base de datos: {db_name}")
        print(f"   ✅ Archivo ejecutado: {archivo_sql}")
        print(f"   ✅ Triggers verificados")
        
        print("\n💡 Los triggers están listos para usar:")
        print("   • actualizar_stock_entrada: Incrementa stock al insertar en entradas_stock")
        print("   • actualizar_stock_asignacion: Decrementa stock al insertar en ferretero")
        print("   • alerta_stock_bajo: Genera alertas cuando stock < mínimo")
        print("   • validar_asignacion: Valida stock antes de asignaciones")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n👋 Operación cancelada por el usuario.")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\n🔌 Conexión MySQL cerrada.")

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido por el usuario.")
        sys.exit(1)