#!/usr/bin/env python3
import mysql.connector
from datetime import datetime

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def verificar_asistencia_completa():
    """Verificar todos los datos de asistencia para la fecha 2025-10-02"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        fecha_buscar = "2025-10-02"
        
        print(f"🔍 VERIFICANDO ASISTENCIA PARA {fecha_buscar}")
        print("=" * 60)
        
        # Buscar todos los registros de asistencia para esa fecha
        cursor.execute("""
            SELECT 
                a.id_asistencia,
                a.cedula,
                a.fecha_asistencia,
                a.hora_inicio,
                a.estado,
                a.novedad,
                a.carpeta_dia,
                ro.nombre as nombre_tecnico
            FROM asistencia a
            LEFT JOIN recurso_operativo ro ON a.cedula = ro.recurso_operativo_cedula
            WHERE DATE(a.fecha_asistencia) = %s
            ORDER BY a.cedula
        """, (fecha_buscar,))
        
        registros = cursor.fetchall()
        
        if not registros:
            print(f"❌ No se encontraron registros de asistencia para {fecha_buscar}")
            return
        
        print(f"✅ Se encontraron {len(registros)} registros de asistencia:")
        print()
        
        for i, registro in enumerate(registros, 1):
            print(f"{i}. {registro['nombre_tecnico']} (Cédula: {registro['cedula']})")
            print(f"   ID Asistencia: {registro['id_asistencia']}")
            print(f"   Fecha: {registro['fecha_asistencia']}")
            print(f"   Hora Inicio: {registro['hora_inicio']}")
            print(f"   Estado: {registro['estado']}")
            print(f"   Novedad: {registro['novedad']}")
            print(f"   Carpeta Día: {registro['carpeta_dia']}")
            print()
        
        # Verificar específicamente los técnicos de la analista ESPITIA
        print("\n🔍 VERIFICANDO TÉCNICOS DE ESPITIA BARON LICED JOANA:")
        print("=" * 60)
        
        cursor.execute("""
            SELECT 
                ro.recurso_operativo_cedula as cedula,
                ro.nombre as nombre_tecnico,
                a.hora_inicio,
                a.estado,
                a.novedad,
                a.carpeta_dia
            FROM recurso_operativo ro
            LEFT JOIN asistencia a ON ro.recurso_operativo_cedula = a.cedula 
                AND DATE(a.fecha_asistencia) = %s
            WHERE ro.analista = 'ESPITIA BARON LICED JOANA'
            ORDER BY ro.nombre
        """, (fecha_buscar,))
        
        tecnicos_espitia = cursor.fetchall()
        
        con_datos = 0
        sin_datos = 0
        
        for tecnico in tecnicos_espitia:
            if tecnico['hora_inicio'] or tecnico['estado'] or tecnico['novedad']:
                con_datos += 1
                print(f"✅ {tecnico['nombre_tecnico']} ({tecnico['cedula']}): CON DATOS")
                print(f"   Hora: {tecnico['hora_inicio']}")
                print(f"   Estado: {tecnico['estado']}")
                print(f"   Novedad: {tecnico['novedad']}")
                print(f"   Carpeta: {tecnico['carpeta_dia']}")
            else:
                sin_datos += 1
                print(f"❌ {tecnico['nombre_tecnico']} ({tecnico['cedula']}): SIN DATOS")
            print()
        
        print(f"📊 RESUMEN PARA ANALISTA ESPITIA:")
        print(f"   Total técnicos: {len(tecnicos_espitia)}")
        print(f"   Con datos de asistencia: {con_datos}")
        print(f"   Sin datos de asistencia: {sin_datos}")
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    verificar_asistencia_completa()