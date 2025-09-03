#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar datos de vencimientos en la tabla parque_automotor
"""

import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'port': 3306
}

def verificar_vencimientos():
    """
    Verifica los datos de vencimientos en la tabla parque_automotor
    """
    connection = None
    cursor = None
    
    try:
        print("🔍 Conectando a la base de datos...")
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        print("✅ Conexión exitosa")
        print("\n" + "="*80)
        print("📊 VERIFICACIÓN DE DATOS DE VENCIMIENTOS")
        print("="*80)
        
        # 1. Verificar estructura de la tabla
        print("\n1️⃣ Verificando estructura de la tabla parque_automotor...")
        cursor.execute("DESCRIBE parque_automotor")
        columns = cursor.fetchall()
        
        vencimiento_fields = []
        for col in columns:
            if 'vencimiento' in col['Field'].lower() or 'fecha' in col['Field'].lower():
                vencimiento_fields.append(col['Field'])
        
        print(f"   📋 Campos relacionados con fechas/vencimientos encontrados: {len(vencimiento_fields)}")
        for field in vencimiento_fields:
            print(f"      - {field}")
        
        # 2. Contar total de vehículos
        print("\n2️⃣ Contando total de vehículos...")
        cursor.execute("SELECT COUNT(*) as total FROM parque_automotor")
        total_vehiculos = cursor.fetchone()['total']
        print(f"   🚗 Total de vehículos en la tabla: {total_vehiculos}")
        
        # 3. Verificar datos de vencimientos específicos
        print("\n3️⃣ Verificando datos de vencimientos específicos...")
        
        # Verificar vencimiento de SOAT
        if 'soat_vencimiento' in vencimiento_fields:
            cursor.execute("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN soat_vencimiento IS NOT NULL THEN 1 END) as con_fecha
                FROM parque_automotor
            """)
            result = cursor.fetchone()
            print(f"   🛡️ SOAT: {result['con_fecha']}/{result['total']} vehículos tienen fecha de vencimiento")
        
        # Verificar vencimiento de tecnomecánica
        if 'tecnomecanica_vencimiento' in vencimiento_fields:
            cursor.execute("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN tecnomecanica_vencimiento IS NOT NULL THEN 1 END) as con_fecha
                FROM parque_automotor
            """)
            result = cursor.fetchone()
            print(f"   🔧 Tecnomecánica: {result['con_fecha']}/{result['total']} vehículos tienen fecha de vencimiento")
        
        # 4. Verificar vencimientos próximos (30 días)
        print("\n4️⃣ Verificando vencimientos próximos (30 días)...")
        fecha_limite = datetime.now() + timedelta(days=30)
        
        vencimientos_proximos = []
        
        for field in ['soat_vencimiento', 'tecnomecanica_vencimiento']:
            if field in vencimiento_fields:
                cursor.execute(f"""
                    SELECT COUNT(*) as proximos
                    FROM parque_automotor 
                    WHERE {field} IS NOT NULL 
                    AND {field} <= %s
                    AND {field} >= CURDATE()
                """, (fecha_limite.date(),))
                
                result = cursor.fetchone()
                vencimientos_proximos.append((field, result['proximos']))
                print(f"   ⚠️ {field}: {result['proximos']} vencimientos en los próximos 30 días")
        
        # 5. Verificar vencimientos vencidos
        print("\n5️⃣ Verificando vencimientos vencidos...")
        
        for field in ['soat_vencimiento', 'tecnomecanica_vencimiento']:
            if field in vencimiento_fields:
                cursor.execute(f"""
                    SELECT COUNT(*) as vencidos
                    FROM parque_automotor 
                    WHERE {field} IS NOT NULL 
                    AND {field} < CURDATE()
                """)
                
                result = cursor.fetchone()
                print(f"   🚨 {field}: {result['vencidos']} vencimientos vencidos")
        
        # 6. Mostrar algunos ejemplos de datos
        print("\n6️⃣ Ejemplos de datos (primeros 5 vehículos con vencimientos)...")
        
        fields_to_select = ['placa', 'tipo_vehiculo'] + vencimiento_fields
        fields_str = ', '.join(fields_to_select)
        
        cursor.execute(f"""
            SELECT {fields_str}
            FROM parque_automotor 
            WHERE soat_vencimiento IS NOT NULL 
               OR tecnomecanica_vencimiento IS NOT NULL
            LIMIT 5
        """)
        
        ejemplos = cursor.fetchall()
        
        if ejemplos:
            print("   📋 Ejemplos de vehículos con datos de vencimiento:")
            for vehiculo in ejemplos:
                print(f"      🚗 Placa: {vehiculo.get('placa', 'N/A')} - Tipo: {vehiculo.get('tipo_vehiculo', 'N/A')}")
                for field in vencimiento_fields:
                    if vehiculo.get(field):
                        print(f"         - {field}: {vehiculo[field]}")
                print()
        else:
            print("   ❌ No se encontraron vehículos con datos de vencimiento")
        
        # 7. Verificar si hay datos en general
        print("\n7️⃣ Resumen general...")
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_vehiculos,
                COUNT(CASE WHEN soat_vencimiento IS NOT NULL THEN 1 END) as con_soat,
                COUNT(CASE WHEN tecnomecanica_vencimiento IS NOT NULL THEN 1 END) as con_tecnomecanica
            FROM parque_automotor
        """)
        
        resumen = cursor.fetchone()
        
        print(f"   📊 Total de vehículos: {resumen['total_vehiculos']}")
        print(f"   🛡️ Con fecha de SOAT: {resumen['con_soat']} ({(resumen['con_soat']/resumen['total_vehiculos']*100):.1f}%)")
        print(f"   🔧 Con fecha de tecnomecánica: {resumen['con_tecnomecanica']} ({(resumen['con_tecnomecanica']/resumen['total_vehiculos']*100):.1f}%)")
        
        # Diagnóstico
        print("\n" + "="*80)
        print("🔍 DIAGNÓSTICO")
        print("="*80)
        
        if resumen['total_vehiculos'] == 0:
            print("❌ No hay vehículos en la tabla parque_automotor")
        elif resumen['con_soat'] == 0 and resumen['con_tecnomecanica'] == 0:
            print("❌ No hay datos de vencimientos en ningún vehículo")
            print("   💡 Esto explica por qué la sección de vencimientos no muestra datos")
        else:
            print("✅ Se encontraron datos de vencimientos")
            if any(count > 0 for _, count in vencimientos_proximos):
                print("⚠️ Hay vencimientos próximos que deberían mostrarse")
            else:
                print("ℹ️ No hay vencimientos próximos en los siguientes 30 días")
        
        print("\n✅ Verificación completada")
        
    except Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    verificar_vencimientos()