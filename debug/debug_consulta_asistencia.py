#!/usr/bin/env python3
import mysql.connector
from datetime import datetime

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'synapsis'
}

def debug_consulta_asistencia():
    """Debug de la consulta de asistencia específica"""
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        print("🔍 DEBUG CONSULTA ASISTENCIA")
        print("=" * 50)
        
        # Técnicos que sabemos que tienen datos
        tecnicos_test = [
            "1085176966",  # ARNACHE ARIAS JUAN CARLOS
            "1022359872",  # BERNAL MORALES LUIS NELSON
            "1033758324"   # DIAZ MORA FABIO NELSON
        ]
        
        fecha_test = "2025-10-02"
        
        for cedula in tecnicos_test:
            print(f"\n🔍 Probando cédula: {cedula}")
            print("-" * 30)
            
            # 1. Consulta con fecha específica (como en el endpoint)
            query_con_fecha = """
                SELECT 
                    a.carpeta_dia,
                    a.fecha_asistencia,
                    a.hora_inicio,
                    a.estado,
                    a.novedad,
                    ta.nombre_tipificacion,
                    ta.codigo_tipificacion,
                    ta.grupo as grupo_tipificacion,
                    pc.presupuesto_eventos,
                    pc.presupuesto_diario,
                    pc.presupuesto_carpeta as nombre_presupuesto_carpeta
                FROM asistencia a
                LEFT JOIN tipificacion_asistencia ta ON a.carpeta_dia = ta.codigo_tipificacion
                LEFT JOIN presupuesto_carpeta pc ON ta.nombre_tipificacion = pc.presupuesto_carpeta
                WHERE a.cedula = %s
                AND DATE(a.fecha_asistencia) = %s
                ORDER BY a.fecha_asistencia DESC
                LIMIT 1
            """
            
            cursor.execute(query_con_fecha, (cedula, fecha_test))
            resultado = cursor.fetchone()
            
            if resultado:
                print("✅ ENCONTRADO con fecha específica:")
                print(f"   Carpeta: {resultado['carpeta_dia']}")
                print(f"   Fecha: {resultado['fecha_asistencia']}")
                print(f"   Hora: {resultado['hora_inicio']}")
                print(f"   Estado: {resultado['estado']}")
                print(f"   Novedad: {resultado['novedad']}")
            else:
                print("❌ NO encontrado con fecha específica")
            
            # 2. Consulta directa para verificar qué datos existen
            query_directa = """
                SELECT 
                    cedula,
                    carpeta_dia,
                    fecha_asistencia,
                    hora_inicio,
                    estado,
                    novedad
                FROM asistencia 
                WHERE cedula = %s
                ORDER BY fecha_asistencia DESC
            """
            
            cursor.execute(query_directa, (cedula,))
            todos_registros = cursor.fetchall()
            
            print(f"\n📋 Todos los registros para {cedula}:")
            if todos_registros:
                for reg in todos_registros:
                    print(f"   Fecha: {reg['fecha_asistencia']} | Hora: {reg['hora_inicio']} | Estado: {reg['estado']}")
            else:
                print("   No hay registros")
            
            # 3. Verificar formato de fecha
            query_fecha_formato = """
                SELECT 
                    cedula,
                    fecha_asistencia,
                    DATE(fecha_asistencia) as fecha_solo,
                    hora_inicio,
                    estado,
                    novedad
                FROM asistencia 
                WHERE cedula = %s
                AND fecha_asistencia LIKE '2025-10-02%'
            """
            
            cursor.execute(query_fecha_formato, (cedula,))
            registros_fecha = cursor.fetchall()
            
            print(f"\n📅 Registros con fecha 2025-10-02:")
            if registros_fecha:
                for reg in registros_fecha:
                    print(f"   Fecha completa: {reg['fecha_asistencia']}")
                    print(f"   Fecha solo: {reg['fecha_solo']}")
                    print(f"   Hora: {reg['hora_inicio']} | Estado: {reg['estado']}")
            else:
                print("   No hay registros para 2025-10-02")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error durante debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_consulta_asistencia()