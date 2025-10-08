#!/usr/bin/env python3
import mysql.connector

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def verificar_estructura_asistencia():
    """Verificar la estructura de la tabla asistencia"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("🔍 ESTRUCTURA DE LA TABLA ASISTENCIA")
        print("=" * 50)
        
        # Obtener estructura de la tabla
        cursor.execute("DESCRIBE asistencia")
        columns = cursor.fetchall()
        
        print("Columnas de la tabla 'asistencia':")
        for column in columns:
            print(f"  - {column[0]} ({column[1]}) - {column[3] if column[3] else 'NOT NULL'}")
        
        print("\n🔍 VERIFICANDO DATOS DE ASISTENCIA PARA TÉCNICOS DE ESPITIA")
        print("=" * 60)
        
        # Verificar datos específicos
        cursor.execute("""
            SELECT 
                a.cedula,
                a.fecha_asistencia,
                a.hora_inicio,
                a.estado,
                a.novedad,
                ro.nombre
            FROM asistencia a
            LEFT JOIN recurso_operativo ro ON a.cedula = ro.recurso_operativo_cedula
            WHERE DATE(a.fecha_asistencia) = '2025-10-02'
            AND ro.analista = 'ESPITIA BARON LICED JOANA'
        """)
        
        resultados = cursor.fetchall()
        
        if resultados:
            print(f"✅ Encontrados {len(resultados)} registros:")
            for resultado in resultados:
                print(f"  - {resultado[5]} (Cédula: {resultado[0]})")
                print(f"    Fecha: {resultado[1]}")
                print(f"    Hora: {resultado[2]}")
                print(f"    Estado: {resultado[3]}")
                print(f"    Novedad: {resultado[4]}")
                print()
        else:
            print("❌ No se encontraron registros")
        
        # Verificar también la consulta exacta que usa el endpoint
        print("\n🔍 PROBANDO CONSULTA DEL ENDPOINT")
        print("=" * 40)
        
        # Obtener un técnico de ejemplo
        cursor.execute("""
            SELECT recurso_operativo_cedula 
            FROM recurso_operativo 
            WHERE analista = 'ESPITIA BARON LICED JOANA' 
            LIMIT 1
        """)
        
        tecnico_ejemplo = cursor.fetchone()
        if tecnico_ejemplo:
            cedula_ejemplo = tecnico_ejemplo[0]
            print(f"Probando con cédula: {cedula_ejemplo}")
            
            # Consulta exacta del endpoint
            cursor.execute("""
                SELECT 
                    a.carpeta_dia,
                    a.fecha_asistencia,
                    a.hora_inicio,
                    a.estado,
                    a.novedad
                FROM asistencia a
                WHERE a.cedula = %s
                AND DATE(a.fecha_asistencia) = %s
                ORDER BY a.fecha_asistencia DESC
                LIMIT 1
            """, (cedula_ejemplo, '2025-10-02'))
            
            resultado = cursor.fetchone()
            if resultado:
                print("✅ Consulta del endpoint funciona:")
                print(f"  Carpeta: {resultado[0]}")
                print(f"  Fecha: {resultado[1]}")
                print(f"  Hora: {resultado[2]}")
                print(f"  Estado: {resultado[3]}")
                print(f"  Novedad: {resultado[4]}")
            else:
                print("❌ La consulta del endpoint no devuelve resultados")
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    verificar_estructura_asistencia()