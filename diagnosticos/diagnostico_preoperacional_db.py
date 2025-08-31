#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para la tabla preoperacional
Base de datos: capired
Usuario: root
Clave: 732137A031E4b@
"""

import mysql.connector
from datetime import datetime, date

def diagnostico_preoperacional():
    """Diagnóstico completo de la tabla preoperacional"""
    
    print("=== DIAGNÓSTICO DE TABLA PREOPERACIONAL ===")
    print(f"Fecha de diagnóstico: {datetime.now()}")
    print(f"Base de datos: capired")
    print()
    
    try:
        # 1. Conectarse a la base de datos
        print("1. 🔌 CONECTANDO A LA BASE DE DATOS...")
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '732137A031E4b@',
            'database': 'capired'
        }
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        print("   ✅ Conexión exitosa")
        
        # 2. Verificar existencia de la tabla
        print("\n2. 📋 VERIFICANDO TABLA PREOPERACIONAL...")
        cursor.execute("SHOW TABLES LIKE 'preoperacional'")
        tabla_existe = cursor.fetchone()
        
        if not tabla_existe:
            print("   ❌ Tabla 'preoperacional' no encontrada")
            cursor.execute("SHOW TABLES")
            tablas = cursor.fetchall()
            print("   📋 Tablas disponibles:")
            for tabla in tablas:
                print(f"      - {list(tabla.values())[0]}")
            return
        
        print("   ✅ Tabla 'preoperacional' encontrada")
        
        # 3. Mostrar estructura de la tabla
        print("\n3. 🏗️  ESTRUCTURA DE LA TABLA PREOPERACIONAL")
        cursor.execute("DESCRIBE preoperacional")
        estructura = cursor.fetchall()
        
        print(f"   📊 Total de campos: {len(estructura)}")
        print("   📋 Campos y tipos:")
        
        campos_supervisor = []
        campos_estado_fisico = []
        campos_fecha = []
        todos_los_campos = []
        
        for i, campo in enumerate(estructura, 1):
            campo_nombre = campo['Field']
            campo_tipo = campo['Type']
            es_null = 'NULL' if campo['Null'] == 'YES' else 'NOT NULL'
            
            print(f"      {i:2d}. {campo_nombre:<50} | {campo_tipo:<25} | {es_null}")
            
            todos_los_campos.append(campo_nombre)
            
            # Identificar campos relacionados con supervisor
            if 'supervisor' in campo_nombre.lower():
                campos_supervisor.append(campo_nombre)
            
            # Identificar campos de estado físico del vehículo
            if 'estado_fisico' in campo_nombre.lower() or ('vehiculo' in campo_nombre.lower() and 'estado' in campo_nombre.lower()):
                campos_estado_fisico.append(campo_nombre)
            
            # Identificar campos de fecha
            if 'fecha' in campo_nombre.lower() or 'date' in campo_tipo.lower():
                campos_fecha.append(campo_nombre)
        
        print(f"\n   🔍 Campos relacionados con supervisor ({len(campos_supervisor)}):")
        for campo in campos_supervisor:
            print(f"      - {campo}")
        
        print(f"\n   🚗 Campos de estado físico del vehículo ({len(campos_estado_fisico)}):")
        for campo in campos_estado_fisico:
            print(f"      - {campo}")
        
        print(f"\n   📅 Campos de fecha ({len(campos_fecha)}):")
        for campo in campos_fecha:
            print(f"      - {campo}")
        
        # 4. Contar total de registros
        print("\n4. 📊 CONTEO TOTAL DE REGISTROS")
        cursor.execute("SELECT COUNT(*) as total FROM preoperacional")
        total_registros = cursor.fetchone()['total']
        print(f"   📈 Total de registros: {total_registros:,}")
        
        if total_registros == 0:
            print("   ⚠️  No hay registros en la tabla")
            return
        
        # 5. Mostrar primeros 10 registros
        print("\n5. 📋 PRIMEROS 10 REGISTROS")
        
        # Usar solo los primeros 5 campos para evitar salida muy larga
        campos_muestra = todos_los_campos[:5]
        query_campos = ', '.join(campos_muestra)
        
        cursor.execute(f"SELECT {query_campos} FROM preoperacional LIMIT 10")
        registros = cursor.fetchall()
        
        for i, registro in enumerate(registros, 1):
            print(f"   Registro {i}:")
            for campo in campos_muestra:
                valor = registro.get(campo, 'N/A')
                print(f"      {campo}: {valor}")
            print()
        
        # 6. Análisis de campos de fecha (si existen)
        if campos_fecha:
            print("\n6. 📅 ANÁLISIS DE FECHAS")
            campo_fecha_principal = campos_fecha[0]
            
            try:
                cursor.execute(f"""
                    SELECT 
                        MIN({campo_fecha_principal}) as fecha_minima,
                        MAX({campo_fecha_principal}) as fecha_maxima,
                        COUNT(*) as total_con_fecha
                    FROM preoperacional
                    WHERE {campo_fecha_principal} IS NOT NULL
                """)
                
                info_fechas = cursor.fetchone()
                print(f"   📅 Campo principal de fecha: {campo_fecha_principal}")
                print(f"   📊 Rango: {info_fechas['fecha_minima']} a {info_fechas['fecha_maxima']}")
                print(f"   📈 Registros con fecha: {info_fechas['total_con_fecha']:,}")
                
                # Contar registros del mes actual
                fecha_actual = date.today()
                cursor.execute(f"""
                    SELECT COUNT(*) as total 
                    FROM preoperacional 
                    WHERE YEAR({campo_fecha_principal}) = %s AND MONTH({campo_fecha_principal}) = %s
                """, (fecha_actual.year, fecha_actual.month))
                registros_mes_actual = cursor.fetchone()['total']
                print(f"   📊 Registros en {fecha_actual.strftime('%B %Y')}: {registros_mes_actual:,}")
                
            except Exception as e:
                print(f"   ⚠️  Error al analizar fechas: {e}")
        
        # 7. Análisis de supervisores (si existen)
        if campos_supervisor:
            print("\n7. 👥 ANÁLISIS DE SUPERVISORES")
            campo_supervisor_principal = campos_supervisor[0]
            
            try:
                cursor.execute(f"""
                    SELECT 
                        {campo_supervisor_principal} as supervisor,
                        COUNT(*) as total_registros
                    FROM preoperacional 
                    WHERE {campo_supervisor_principal} IS NOT NULL 
                        AND {campo_supervisor_principal} != ''
                    GROUP BY {campo_supervisor_principal}
                    ORDER BY total_registros DESC
                    LIMIT 10
                """)
                
                supervisores = cursor.fetchall()
                
                print(f"   📊 Campo principal de supervisor: {campo_supervisor_principal}")
                print(f"   📋 Top 10 supervisores por registros:")
                
                for i, supervisor in enumerate(supervisores, 1):
                    nombre = supervisor['supervisor']
                    total = supervisor['total_registros']
                    print(f"      {i:2d}. {nombre:<40} | {total:4d} registros")
                
                # Verificar valores nulos/vacíos
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN {campo_supervisor_principal} IS NULL THEN 1 ELSE 0 END) as nulos,
                        SUM(CASE WHEN {campo_supervisor_principal} = '' THEN 1 ELSE 0 END) as vacios,
                        SUM(CASE WHEN {campo_supervisor_principal} IS NOT NULL AND {campo_supervisor_principal} != '' THEN 1 ELSE 0 END) as validos
                    FROM preoperacional
                """)
                
                estadisticas = cursor.fetchone()
                total = estadisticas['total']
                nulos = estadisticas['nulos']
                vacios = estadisticas['vacios']
                validos = estadisticas['validos']
                
                porcentaje_validos = (validos / total * 100) if total > 0 else 0
                
                print(f"\n   📊 Estadísticas de {campo_supervisor_principal}:")
                print(f"      Total: {total:,} | Válidos: {validos:,} ({porcentaje_validos:.1f}%) | Nulos: {nulos:,} | Vacíos: {vacios:,}")
                
            except Exception as e:
                print(f"   ⚠️  Error al analizar supervisores: {e}")
        
        # 8. Análisis de campos de estado físico (si existen)
        if campos_estado_fisico:
            print("\n8. 🚗 ANÁLISIS DE ESTADO FÍSICO DEL VEHÍCULO")
            
            print(f"   📋 Campos de estado físico encontrados ({len(campos_estado_fisico)}):")
            for campo in campos_estado_fisico:
                print(f"      - {campo}")
            
            # Mostrar ejemplos de los primeros 3 campos
            campos_muestra_estado = campos_estado_fisico[:3]
            if campos_muestra_estado:
                try:
                    query_estado = ', '.join(['id_preoperacional'] + campos_muestra_estado)
                    cursor.execute(f"SELECT {query_estado} FROM preoperacional LIMIT 5")
                    ejemplos_estado = cursor.fetchall()
                    
                    print(f"\n   📋 Ejemplos de los primeros {len(campos_muestra_estado)} campos:")
                    for i, ejemplo in enumerate(ejemplos_estado, 1):
                        print(f"      Registro {i}:")
                        for campo in campos_muestra_estado:
                            if campo in ejemplo:
                                valor = ejemplo[campo]
                                print(f"         {campo}: {valor}")
                        print()
                        
                except Exception as e:
                    print(f"   ⚠️  Error al mostrar ejemplos de estado físico: {e}")
        
        cursor.close()
        connection.close()
        
        print("\n=== DIAGNÓSTICO COMPLETADO ===")
        print("\n💡 RECOMENDACIONES:")
        print("   - Verificar que los campos utilizados en el endpoint coincidan con los encontrados")
        print("   - Revisar la lógica de consulta del endpoint /api/indicadores/estado_vehiculos")
        print("   - Asegurar que los nombres de campos sean exactos (sensibles a mayúsculas/minúsculas)")
        
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnostico_preoperacional()