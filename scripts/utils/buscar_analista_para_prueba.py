#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para buscar un usuario analista válido para hacer pruebas
"""

import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'database': 'capired',
    'user': 'root',
    'password': '732137A031E4b@',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def buscar_analista_para_prueba():
    """Buscar un usuario analista activo para hacer pruebas"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        print("=== BÚSQUEDA DE ANALISTA PARA PRUEBAS ===")
        
        # 1. Buscar analistas activos
        print("\n[1] Buscando analistas activos...")
        cursor.execute("""
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula as cedula,
                nombre,
                cargo,
                estado,
                id_roles
            FROM recurso_operativo 
            WHERE cargo = 'ANALISTA' 
            AND estado = 'Activo'
            ORDER BY nombre
            LIMIT 5
        """)
        analistas = cursor.fetchall()
        
        if analistas:
            print(f"   ✅ Encontrados {len(analistas)} analistas activos:")
            for i, analista in enumerate(analistas, 1):
                print(f"      {i}. {analista['nombre']}")
                print(f"         Cédula: {analista['cedula']}")
                print(f"         ID: {analista['id_codigo_consumidor']}")
                print(f"         Rol ID: {analista['id_roles']}")
                print()
        else:
            print("   ❌ No se encontraron analistas activos")
            return None
        
        # 2. Buscar técnicos asignados al primer analista
        primer_analista = analistas[0]
        print(f"[2] Buscando técnicos asignados a: {primer_analista['nombre']}")
        
        cursor.execute("""
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula as cedula,
                nombre as tecnico,
                carpeta,
                super as supervisor,
                analista
            FROM recurso_operativo 
            WHERE analista = %s
            AND estado = 'Activo'
            ORDER BY nombre
            LIMIT 5
        """, (primer_analista['nombre'],))
        
        tecnicos = cursor.fetchall()
        
        if tecnicos:
            print(f"   ✅ {primer_analista['nombre']} tiene {len(tecnicos)} técnicos asignados:")
            for i, tecnico in enumerate(tecnicos, 1):
                print(f"      {i}. {tecnico['tecnico']}")
                print(f"         Cédula: {tecnico['cedula']}")
                print(f"         Supervisor: {tecnico['supervisor']}")
                print()
        else:
            print(f"   ⚠️  {primer_analista['nombre']} no tiene técnicos asignados")
        
        # 3. Verificar si algún técnico tiene datos de asistencia hoy
        if tecnicos:
            print(f"[3] Verificando datos de asistencia para hoy...")
            
            tecnicos_con_asistencia = []
            for tecnico in tecnicos:
                cursor.execute("""
                    SELECT 
                        cedula, tecnico, hora_inicio, estado, novedad, carpeta_dia
                    FROM asistencia 
                    WHERE cedula = %s
                    AND DATE(fecha_asistencia) = CURDATE()
                    ORDER BY fecha_asistencia DESC
                    LIMIT 1
                """, (tecnico['cedula'],))
                
                asistencia = cursor.fetchone()
                if asistencia:
                    tecnicos_con_asistencia.append({
                        'tecnico': tecnico,
                        'asistencia': asistencia
                    })
            
            if tecnicos_con_asistencia:
                print(f"   ✅ {len(tecnicos_con_asistencia)} técnicos tienen datos de asistencia hoy:")
                for item in tecnicos_con_asistencia:
                    tecnico = item['tecnico']
                    asistencia = item['asistencia']
                    print(f"      - {tecnico['tecnico']} (Cédula: {tecnico['cedula']})")
                    print(f"        Hora: {asistencia['hora_inicio']}, Estado: {asistencia['estado']}, Novedad: {asistencia['novedad']}")
            else:
                print(f"   ⚠️  Ningún técnico tiene datos de asistencia para hoy")
        
        # 4. Mostrar recomendación
        print(f"\n[4] RECOMENDACIÓN PARA PRUEBAS:")
        print(f"   📋 Analista recomendado: {primer_analista['nombre']}")
        print(f"   🔑 Cédula para login: {primer_analista['cedula']}")
        print(f"   👥 Técnicos asignados: {len(tecnicos)}")
        
        if tecnicos_con_asistencia:
            print(f"   ✅ Técnicos con datos de asistencia: {len(tecnicos_con_asistencia)}")
            print(f"   💡 Este analista es ideal para probar el endpoint")
        else:
            print(f"   ⚠️  Sin datos de asistencia para hoy")
            print(f"   💡 Aún se puede probar la estructura del endpoint")
        
        cursor.close()
        connection.close()
        
        return primer_analista
        
    except Error as e:
        print(f"❌ Error de conexión: {e}")
        return None

if __name__ == "__main__":
    buscar_analista_para_prueba()