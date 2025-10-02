#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from datetime import datetime
import pytz

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def debug_update_issue():
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        cedula = "1030545270"
        
        # Obtener fecha actual en zona horaria de Bogotá
        bogota_tz = pytz.timezone('America/Bogota')
        fecha_actual = datetime.now(bogota_tz).date()
        
        print(f"🔍 Depurando problema de actualización para cédula: {cedula}")
        print(f"📅 Fecha actual: {fecha_actual}")
        print("=" * 60)
        
        # 1. Verificar si existe el registro
        cursor.execute("""
            SELECT id_asistencia, cedula, tecnico, fecha_asistencia, hora_inicio, estado, novedad
            FROM asistencia 
            WHERE cedula = %s AND DATE(fecha_asistencia) = %s
            ORDER BY fecha_asistencia DESC
            LIMIT 1
        """, (cedula, fecha_actual))
        
        registro = cursor.fetchone()
        
        if registro:
            print("✅ Registro encontrado:")
            for key, value in registro.items():
                print(f"   {key}: {value}")
            
            id_asistencia = registro['id_asistencia']
            print(f"\n🔧 Intentando actualizar registro con ID: {id_asistencia}")
            
            # 2. Intentar actualización directa
            print("\n📝 Probando actualización de hora_inicio...")
            cursor.execute("UPDATE asistencia SET hora_inicio = %s WHERE id_asistencia = %s", ("10:30", id_asistencia))
            print(f"   Filas afectadas: {cursor.rowcount}")
            
            if cursor.rowcount > 0:
                connection.commit()
                print("   ✅ Actualización exitosa")
                
                # Verificar el cambio
                cursor.execute("SELECT hora_inicio FROM asistencia WHERE id_asistencia = %s", (id_asistencia,))
                resultado = cursor.fetchone()
                print(f"   📋 Nuevo valor: {resultado['hora_inicio']}")
            else:
                print("   ❌ No se pudo actualizar")
                
                # Verificar si el registro aún existe
                cursor.execute("SELECT COUNT(*) as count FROM asistencia WHERE id_asistencia = %s", (id_asistencia,))
                count_result = cursor.fetchone()
                print(f"   🔍 Registros con ID {id_asistencia}: {count_result['count']}")
        else:
            print("❌ No se encontró registro para la fecha actual")
            
            # Buscar registros para esta cédula en cualquier fecha
            cursor.execute("""
                SELECT id_asistencia, cedula, fecha_asistencia, hora_inicio, estado, novedad
                FROM asistencia 
                WHERE cedula = %s
                ORDER BY fecha_asistencia DESC
                LIMIT 5
            """, (cedula,))
            
            registros = cursor.fetchall()
            if registros:
                print(f"\n📋 Últimos 5 registros para cédula {cedula}:")
                for reg in registros:
                    print(f"   ID: {reg['id_asistencia']}, Fecha: {reg['fecha_asistencia']}")
            else:
                print(f"\n❌ No hay registros para cédula {cedula}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    debug_update_issue()