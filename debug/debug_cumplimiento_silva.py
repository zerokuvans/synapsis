#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug para investigar el problema de conteo de cumplimiento
para el supervisor SILVA CASTRO DANIEL ALBERTO en la fecha 2025-10-08
"""

import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos (usando variables de entorno como en main.py)
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'synapsis'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'time_zone': '+00:00'
}

def conectar_db():
    """Conectar a la base de datos"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def debug_cumplimiento_silva():
    """Debug del conteo de cumplimiento para Silva Castro"""
    
    supervisor = "SILVA CASTRO DANIEL ALBERTO"
    fecha = "2025-10-08"
    
    print("=" * 80)
    print(f"🔍 DEBUG CUMPLIMIENTO - {supervisor}")
    print(f"📅 Fecha: {fecha}")
    print("=" * 80)
    
    conn = conectar_db()
    if not conn:
        return
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Consultar todos los registros para este supervisor y fecha
        print("\n1️⃣ CONSULTANDO REGISTROS EN ASISTENCIA...")
        query_all = """
        SELECT 
            cedula, tecnico, super, fecha_asistencia, hora_inicio, estado, novedad,
            DATE(fecha_asistencia) as fecha_solo
        FROM asistencia 
        WHERE super = %s 
        AND DATE(fecha_asistencia) = %s
        ORDER BY cedula, fecha_asistencia DESC, hora_inicio DESC
        """
        
        cursor.execute(query_all, (supervisor, fecha))
        registros = cursor.fetchall()
        
        print(f"📊 Total de registros encontrados: {len(registros)}")
        
        if not registros:
            print("❌ No se encontraron registros para este supervisor y fecha")
            return
        
        # 2. Mostrar todos los registros
        print("\n2️⃣ DETALLE DE TODOS LOS REGISTROS (INCLUYENDO DUPLICADOS):")
        print("-" * 140)
        print(f"{'CÉDULA':<12} {'TÉCNICO':<25} {'ESTADO RAW':<20} {'FECHA':<20} {'HORA':<10} {'NOVEDAD':<15}")
        print("-" * 140)
        
        # Contador de estados exactos
        estados_count = {}
        
        for i, registro in enumerate(registros, 1):
            hora_inicio = str(registro['hora_inicio']) if registro['hora_inicio'] is not None else 'N/A'
            estado_raw = registro['estado'] if registro['estado'] is not None else 'N/A'
            novedad = registro['novedad'] if registro['novedad'] is not None else 'N/A'
            
            # Contar estados exactos
            if estado_raw != 'N/A':
                estados_count[estado_raw] = estados_count.get(estado_raw, 0) + 1
            
            print(f"{registro['cedula']:<12} {registro['tecnico'][:24]:<25} '{estado_raw}'<{len(estado_raw) if estado_raw != 'N/A' else 3}> {str(registro['fecha_asistencia']):<20} {hora_inicio:<10} '{novedad}'")
        
        print(f"\n📊 CONTEO DE ESTADOS EXACTOS (TODOS LOS REGISTROS):")
        for estado, count in sorted(estados_count.items()):
            print(f"  '{estado}': {count}")
        
        # 3. Proceso de deduplicación (tomar el más reciente por cédula)
        print("\n3️⃣ PROCESO DE DEDUPLICACIÓN PASO A PASO:")
        print("-" * 80)
        
        registros_unicos = {}
        registros_eliminados = []
        
        for registro in registros:
            cedula = registro['cedula']
            estado_raw = registro['estado'] if registro['estado'] is not None else 'N/A'
            
            if cedula not in registros_unicos:
                registros_unicos[cedula] = registro
                print(f"✅ NUEVO: {cedula} - {registro['tecnico'][:20]} - Estado: '{estado_raw}'")
            else:
                # Comparar fechas de asistencia para tomar el más reciente
                fecha_actual = registro['fecha_asistencia']
                fecha_existente = registros_unicos[cedula]['fecha_asistencia']
                
                if fecha_actual > fecha_existente:
                    registro_anterior = registros_unicos[cedula]
                    registros_unicos[cedula] = registro
                    registros_eliminados.append(registro_anterior)
                    print(f"🔄 REEMPLAZADO: {cedula} - '{registro_anterior['estado']}' → '{estado_raw}'")
                else:
                    registros_eliminados.append(registro)
                    print(f"❌ ELIMINADO: {cedula} - '{estado_raw}' (más antiguo)")
        
        print(f"\n📋 REGISTROS ELIMINADOS EN DEDUPLICACIÓN:")
        for reg in registros_eliminados:
            estado_elim = reg['estado'] if reg['estado'] is not None else 'N/A'
            print(f"  {reg['cedula']} - {reg['tecnico'][:20]} - Estado: '{estado_elim}'")
        
        registros_finales = list(registros_unicos.values())
        print(f"📊 Registros únicos después de deduplicación: {len(registros_finales)}")
        
        # 4. Mostrar registros únicos
        print("\n4️⃣ REGISTROS ÚNICOS (MÁS RECIENTES POR CÉDULA):")
        print("-" * 120)
        print(f"{'CÉDULA':<12} {'TÉCNICO':<25} {'ESTADO':<15} {'FECHA':<20} {'HORA':<10}")
        print("-" * 120)
        
        for registro in registros_finales:
            hora_inicio = str(registro['hora_inicio']) if registro['hora_inicio'] is not None else 'N/A'
            estado = registro['estado'] if registro['estado'] is not None else 'N/A'
            print(f"{registro['cedula']:<12} {registro['tecnico'][:24]:<25} {estado:<15} {str(registro['fecha_asistencia']):<20} {hora_inicio:<10}")
        
        # 5. Conteo manual detallado de cumplimiento
        print("\n5️⃣ CONTEO MANUAL DETALLADO DE CUMPLIMIENTO:")
        print("-" * 80)
        
        # Contadores por estado exacto
        estados_finales_count = {}
        cumple_count = 0
        no_cumple_count = 0
        no_cumple_records = []
        otros_records = []
        estados_detalle = {}
        
        print("📋 ANÁLISIS ESTADO POR ESTADO:")
        for registro in registros_finales:
            estado = registro['estado']
            if estado is None:
                estado = 'NULL'
            
            # Contar estados exactos
            estados_finales_count[estado] = estados_finales_count.get(estado, 0) + 1
            
            estado_lower = estado.lower().strip() if estado != 'NULL' else 'null'
            
            # Contar estados
            if estado_lower not in estados_detalle:
                estados_detalle[estado_lower] = 0
            estados_detalle[estado_lower] += 1
            
            print(f"  {registro['cedula']} - {registro['tecnico'][:25]} - Estado: '{estado}' (lower: '{estado_lower}')")
            
            # Lógica de cumplimiento
            if estado_lower == 'cumple':
                cumple_count += 1
            elif estado_lower in ['no cumple', 'nocumple', 'no aplica', 'novedad']:
                no_cumple_count += 1
                no_cumple_records.append({
                    'cedula': registro['cedula'],
                    'tecnico': registro['tecnico'],
                    'estado': estado,
                    'estado_lower': estado_lower
                })
            else:
                otros_records.append({
                    'cedula': registro['cedula'],
                    'tecnico': registro['tecnico'],
                    'estado': estado,
                    'estado_lower': estado_lower
                })
        
        print(f"\n📊 CONTEO DE ESTADOS FINALES (DESPUÉS DE DEDUPLICACIÓN):")
        for estado, count in sorted(estados_finales_count.items()):
            print(f"  '{estado}': {count}")
        
        print(f"\n🎯 RESULTADO DEL CONTEO:")
        print(f"  ✅ Cumple: {cumple_count}")
        print(f"  ❌ No Cumple: {no_cumple_count}")
        if otros_records:
            print(f"  ❓ Otros: {len(otros_records)}")
        print(f"  📊 Total Procesados: {cumple_count + no_cumple_count + len(otros_records)}")
        
        print("\n📋 REGISTROS QUE CUENTAN COMO 'NO CUMPLE':")
        for record in no_cumple_records:
            print(f"  {record['cedula']} - {record['tecnico'][:30]} - Estado: '{record['estado']}' → '{record['estado_lower']}'")
        
        if otros_records:
            print("\n❓ REGISTROS CON ESTADOS NO RECONOCIDOS:")
            for record in otros_records:
                print(f"  {record['cedula']} - {record['tecnico'][:30]} - Estado: '{record['estado']}' → '{record['estado_lower']}'")
        
        # Verificación de variaciones de estado
        print("\n🔍 VERIFICACIÓN DE VARIACIONES DE ESTADO:")
        variaciones_no_cumple = ['no cumple', 'nocumple', 'no aplica', 'novedad', 'NO CUMPLE', 'NOCUMPLE', 'NO APLICA', 'NOVEDAD']
        
        for variacion in variaciones_no_cumple:
            count = sum(1 for reg in registros_finales if reg['estado'] and reg['estado'].lower().strip() == variacion.lower())
            if count > 0:
                print(f"  '{variacion}': {count} registros")
        
        # 6. Detalle de estados encontrados
        print("\n6️⃣ DETALLE DE ESTADOS ENCONTRADOS:")
        for estado, cantidad in estados_detalle.items():
            print(f"   {estado}: {cantidad}")
        
        # 7. Simular la lógica del endpoint
        print("\n7️⃣ SIMULANDO LÓGICA DEL ENDPOINT...")
        
        # Replicar exactamente la lógica del endpoint
        endpoint_cumple = 0
        endpoint_no_cumple = 0
        
        for registro in registros_finales:
            estado = registro.get('estado', '')
            if estado:
                estado_clean = estado.lower().strip()
                if estado_clean == 'cumple':
                    endpoint_cumple += 1
                elif estado_clean in ['nocumple', 'no cumple', 'no aplica', 'novedad']:
                    endpoint_no_cumple += 1
        
        print(f"🔄 Endpoint - CUMPLE: {endpoint_cumple}")
        print(f"🔄 Endpoint - NO CUMPLE: {endpoint_no_cumple}")
        
        # 8. Verificar si hay diferencias
        print("\n8️⃣ VERIFICACIÓN DE CONSISTENCIA:")
        if cumple_count == endpoint_cumple and no_cumple_count == endpoint_no_cumple:
            print("✅ Los conteos son consistentes")
        else:
            print("❌ HAY DIFERENCIAS EN LOS CONTEOS:")
            print(f"   Manual vs Endpoint - CUMPLE: {cumple_count} vs {endpoint_cumple}")
            print(f"   Manual vs Endpoint - NO CUMPLE: {no_cumple_count} vs {endpoint_no_cumple}")
        
        # 9. Mostrar registros que deberían contar como "No Cumple"
        print("\n9️⃣ REGISTROS QUE DEBERÍAN CONTAR COMO 'NO CUMPLE':")
        no_cumple_registros = []
        for registro in registros_finales:
            estado = registro.get('estado', '')
            if estado:
                estado_clean = estado.lower().strip()
                if estado_clean in ['nocumple', 'no cumple', 'no aplica', 'novedad']:
                    no_cumple_registros.append(registro)
        
        if no_cumple_registros:
            print("-" * 80)
            print(f"{'CÉDULA':<12} {'TÉCNICO':<25} {'ESTADO':<15}")
            print("-" * 80)
            for registro in no_cumple_registros:
                print(f"{registro['cedula']:<12} {registro['tecnico'][:24]:<25} {registro['estado']:<15}")
        else:
            print("❌ No se encontraron registros que deberían contar como 'No Cumple'")
        
        print("\n" + "=" * 80)
        print("🏁 DEBUG COMPLETADO")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error durante el debug: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    debug_cumplimiento_silva()