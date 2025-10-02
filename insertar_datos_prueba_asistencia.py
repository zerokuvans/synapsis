#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from datetime import datetime
import pytz

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def insertar_datos_prueba():
    """Insertar datos de prueba en la tabla asistencia para la fecha actual"""
    try:
        print("=== INSERCIÓN DE DATOS DE PRUEBA PARA ASISTENCIA ===")
        
        # Obtener fecha actual en zona horaria de Bogotá
        bogota_tz = pytz.timezone('America/Bogota')
        fecha_actual = datetime.now(bogota_tz)
        
        print(f"Fecha actual: {fecha_actual.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Conectar a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("✅ Conectado a la base de datos MySQL")
        
        # Verificar si ya existen registros para hoy
        cursor.execute("""
            SELECT COUNT(*) FROM asistencia 
            WHERE DATE(fecha_asistencia) = %s
        """, (fecha_actual.date(),))
        
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"⚠️  Ya existen {count} registros para la fecha actual")
            respuesta = input("¿Desea eliminar estos registros y crear nuevos? (s/n): ")
            if respuesta.lower() != 's':
                print("Operación cancelada")
                return
            
            # Eliminar registros existentes
            cursor.execute("""
                DELETE FROM asistencia 
                WHERE DATE(fecha_asistencia) = %s
            """, (fecha_actual.date(),))
            
            connection.commit()
            print(f"✅ Se eliminaron {cursor.rowcount} registros existentes")
        
        # Datos de prueba con IDs reales de recurso_operativo
        datos_prueba = [
            {
                'cedula': '5694500',
                'tecnico': 'SILVA LANDAEZ MAIKEL SILVERIO',
                'carpeta_dia': 'BROWN',
                'carpeta': 'MANTENIMIENTO FTTH',
                'super': 'MUOZ URREGO JOSE MAURICIO',
                'id_codigo_consumidor': 94
            },
            {
                'cedula': '79815202',
                'tecnico': 'CHAVEZ CRUZ NESTOR RAUL',
                'carpeta_dia': 'MTTH1',
                'carpeta': 'MANTENIMIENTO FTTH',
                'super': 'SILVA CASTRO DANIEL ALBERTO',
                'id_codigo_consumidor': 24
            },
            {
                'cedula': '11165332',
                'tecnico': 'ESPITIA MORELO FARID ANDRES',
                'carpeta_dia': 'MTTH1',
                'carpeta': 'MANTENIMIENTO FTTH',
                'super': 'SILVA CASTRO DANIEL ALBERTO',
                'id_codigo_consumidor': 131
            },
            {
                'cedula': '1020761350',
                'tecnico': 'GOMEZ MONTAÑO FABIAN SNEITHER',
                'carpeta_dia': 'MTTH1',
                'carpeta': 'MANTENIMIENTO FTTH',
                'super': 'MALDONADO GARNICA JAVIER HERNANDO',
                'id_codigo_consumidor': 124
            },
            {
                'cedula': '84455827',
                'tecnico': 'OATE MERCADO ERNESTO RAFAEL',
                'carpeta_dia': 'MTTH1',
                'carpeta': 'MANTENIMIENTO FTTH',
                'super': 'CACERES MARTINEZ CARLOS',
                'id_codigo_consumidor': 54
            }
        ]
        
        # Insertar datos de prueba
        for dato in datos_prueba:
            cursor.execute("""
                INSERT INTO asistencia (
                    cedula, tecnico, carpeta_dia, carpeta, super, 
                    id_codigo_consumidor, fecha_asistencia
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                dato['cedula'],
                dato['tecnico'],
                dato['carpeta_dia'],
                dato['carpeta'],
                dato['super'],
                dato['id_codigo_consumidor'],
                fecha_actual
            ))
        
        connection.commit()
        print(f"✅ Se insertaron {len(datos_prueba)} registros de prueba")
        
        # Verificar los datos insertados
        cursor.execute("""
            SELECT id_asistencia, cedula, tecnico, fecha_asistencia
            FROM asistencia 
            WHERE DATE(fecha_asistencia) = %s
            ORDER BY id_asistencia
        """, (fecha_actual.date(),))
        
        registros = cursor.fetchall()
        
        print("\n📊 Registros insertados:")
        for registro in registros:
            print(f"  ID: {registro[0]}, Cédula: {registro[1]}, Técnico: {registro[2]}, Fecha: {registro[3]}")
        
        print("\n✅ Datos de prueba insertados correctamente")
        
    except mysql.connector.Error as e:
        print(f"\n❌ Error de MySQL: {e}")
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()
            print("🔌 Conexión a la base de datos cerrada")

if __name__ == "__main__":
    print("SCRIPT DE INSERCIÓN DE DATOS DE PRUEBA PARA ASISTENCIA")
    print("=" * 60)
    insertar_datos_prueba()