#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector

# Configuración de la base de datos
config = {
    'user': 'root',
    'password': '732137A031E4b@',
    'host': 'localhost',
    'database': 'capired'
}

def investigar_duplicados():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        
        print('🔍 INVESTIGANDO DUPLICADOS EN TABLA ASISTENCIA')
        print('=' * 60)
        
        # Consulta EXACTA del endpoint corregido para verificar si funciona
        query_endpoint = """
        SELECT 
            a.cedula,
            a.tecnico,
            a.carpeta,
            a.super,
            a.carpeta_dia,
            a.eventos AS eventos,
            a.valor,
            a.estado,
            a.novedad,
            a.id_asistencia,
            a.fecha_asistencia
        FROM asistencia a
        WHERE a.super = 'SILVA CASTRO DANIEL ALBERTO' AND DATE(a.fecha_asistencia) = '2025-10-08'
        AND a.id_asistencia = (
            SELECT MAX(a2.id_asistencia)
            FROM asistencia a2
            WHERE a2.cedula = a.cedula 
            AND a2.super = 'SILVA CASTRO DANIEL ALBERTO' 
            AND DATE(a2.fecha_asistencia) = '2025-10-08'
        )
        ORDER BY a.tecnico
        """
        
        cursor.execute(query_endpoint)
        registros = cursor.fetchall()
        
        print(f"📊 Registros devueltos por consulta del endpoint: {len(registros)}")
        
        # Verificar duplicados por cédula
        cedulas_vistas = {}
        duplicados = []
        
        print("\n📋 REGISTROS DEVUELTOS:")
        for i, registro in enumerate(registros, 1):
            try:
                cedula = registro[0]
                tecnico = registro[1]
                id_asistencia = registro[9]
                
                if cedula in cedulas_vistas:
                    duplicados.append({
                        'cedula': cedula,
                        'tecnico': tecnico,
                        'primera_aparicion': cedulas_vistas[cedula],
                        'segunda_aparicion': i,
                        'id_asistencia': id_asistencia
                    })
                    print(f"🔴 DUPLICADO #{len(duplicados)}: {cedula} - {tecnico} (ID: {id_asistencia})")
                else:
                    cedulas_vistas[cedula] = i
                    print(f"✅ Fila {i:2d}: {cedula} - {tecnico} (ID: {id_asistencia})")
            except Exception as e:
                print(f"❌ Error procesando registro {i}: {e}")
                print(f"   Registro: {registro}")
        
        print(f"\n📊 RESUMEN:")
        print(f"   Total registros: {len(registros)}")
        print(f"   Técnicos únicos: {len(cedulas_vistas)}")
        print(f"   Duplicados encontrados: {len(duplicados)}")
        
        if duplicados:
            print(f"🔴 ¡PROBLEMA! La consulta del endpoint aún devuelve {len(duplicados)} duplicados")
        else:
            print("✅ ¡PERFECTO! La consulta del endpoint no devuelve duplicados")
        
        # Buscar TODOS los duplicados para esa fecha y supervisor
        query_todos_duplicados = """
        SELECT 
            cedula, 
            tecnico, 
            COUNT(*) as cantidad_registros
        FROM asistencia 
        WHERE super = 'SILVA CASTRO DANIEL ALBERTO' 
        AND DATE(fecha_asistencia) = '2025-10-08'
        GROUP BY cedula, tecnico
        HAVING COUNT(*) > 1
        ORDER BY cantidad_registros DESC
        """
        
        cursor.execute(query_todos_duplicados)
        todos_duplicados = cursor.fetchall()
        
        print(f'\n📊 RESUMEN DE DUPLICADOS (Fecha: 2025-10-08):')
        print(f'Total técnicos con duplicados: {len(todos_duplicados)}')
        
        if todos_duplicados:
            print('\nTécnicos duplicados:')
            for dup in todos_duplicados:
                print(f'  - {dup["tecnico"]} (Cédula: {dup["cedula"]}): {dup["cantidad_registros"]} registros')
        
        # Verificar el conteo total
        cursor.execute("""
        SELECT COUNT(DISTINCT cedula) as tecnicos_unicos,
               COUNT(*) as total_registros
        FROM asistencia 
        WHERE super = 'SILVA CASTRO DANIEL ALBERTO' 
        AND DATE(fecha_asistencia) = '2025-10-08'
        """)
        
        conteo = cursor.fetchone()
        print(f'\n📈 ESTADÍSTICAS:')
        print(f'Técnicos únicos (por cédula): {conteo["tecnicos_unicos"]}')
        print(f'Total registros en tabla: {conteo["total_registros"]}')
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    investigar_duplicados()