#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para simular problemas de cálculos en servidor MySQL
Este script reproduce el comportamiento de la función registrar_ferretero
para identificar dónde fallan los cálculos en el servidor.
"""

import mysql.connector
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """Obtener conexión a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'capired'),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            autocommit=False
        )
        return connection
    except mysql.connector.Error as e:
        print(f"❌ Error de conexión a MySQL: {e}")
        return None

def simular_calculo_limites(id_codigo_consumidor='12345'):
    """Simular el cálculo de límites como en registrar_ferretero"""
    print(f"\n🧮 SIMULANDO CÁLCULO DE LÍMITES PARA TÉCNICO: {id_codigo_consumidor}")
    print("=" * 70)
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 1. Verificar que el técnico existe (como en el código original)
        print("\n1. VERIFICANDO TÉCNICO:")
        cursor.execute('SELECT nombre, cargo, carpeta FROM recurso_operativo WHERE id_codigo_consumidor = %s', (id_codigo_consumidor,))
        tecnico = cursor.fetchone()
        
        if not tecnico:
            print(f"   ❌ Técnico {id_codigo_consumidor} no encontrado")
            # Crear un técnico de prueba
            print("   📝 Creando técnico de prueba...")
            cursor.execute("""
                INSERT IGNORE INTO recurso_operativo (id_codigo_consumidor, nombre, cargo, carpeta) 
                VALUES (%s, 'Técnico Prueba', 'FTTH INSTALACIONES', 'FTTH INSTALACIONES')
            """, (id_codigo_consumidor,))
            connection.commit()
            
            # Verificar nuevamente
            cursor.execute('SELECT nombre, cargo, carpeta FROM recurso_operativo WHERE id_codigo_consumidor = %s', (id_codigo_consumidor,))
            tecnico = cursor.fetchone()
        
        if tecnico:
            print(f"   ✅ Técnico encontrado: {tecnico['nombre']}")
            print(f"      - Cargo: {tecnico['cargo']}")
            print(f"      - Carpeta: {tecnico['carpeta']}")
        else:
            print("   ❌ No se pudo crear/encontrar técnico")
            return False
        
        # 2. Obtener fecha actual (como en el código original)
        print("\n2. OBTENIENDO FECHA ACTUAL:")
        fecha_actual = datetime.now()
        print(f"   - Fecha actual Python: {fecha_actual}")
        
        # También obtener fecha de MySQL para comparar
        cursor.execute("SELECT NOW() as mysql_now")
        mysql_time = cursor.fetchone()
        print(f"   - Fecha actual MySQL: {mysql_time['mysql_now']}")
        
        # 3. Obtener asignaciones previas (como en el código original)
        print("\n3. OBTENIENDO ASIGNACIONES PREVIAS:")
        cursor.execute("""
            SELECT 
                fecha_asignacion,
                silicona,
                amarres_negros,
                amarres_blancos,
                cinta_aislante,
                grapas_blancas,
                grapas_negras
            FROM ferretero 
            WHERE id_codigo_consumidor = %s
            ORDER BY fecha_asignacion DESC
        """, (id_codigo_consumidor,))
        asignaciones_previas = cursor.fetchall()
        
        print(f"   - Asignaciones encontradas: {len(asignaciones_previas)}")
        
        # Si no hay asignaciones, crear algunas de prueba
        if len(asignaciones_previas) == 0:
            print("   📝 Creando asignaciones de prueba...")
            fechas_prueba = [
                datetime.now() - timedelta(days=3),
                datetime.now() - timedelta(days=8),
                datetime.now() - timedelta(days=12)
            ]
            
            for i, fecha in enumerate(fechas_prueba):
                cursor.execute("""
                    INSERT INTO ferretero (
                        id_codigo_consumidor, fecha_asignacion, silicona, cinta_aislante
                    ) VALUES (%s, %s, %s, %s)
                """, (id_codigo_consumidor, fecha, 2, 1))
            
            connection.commit()
            
            # Obtener asignaciones nuevamente
            cursor.execute("""
                SELECT 
                    fecha_asignacion,
                    silicona,
                    amarres_negros,
                    amarres_blancos,
                    cinta_aislante,
                    grapas_blancas,
                    grapas_negras
                FROM ferretero 
                WHERE id_codigo_consumidor = %s
                ORDER BY fecha_asignacion DESC
            """, (id_codigo_consumidor,))
            asignaciones_previas = cursor.fetchall()
            print(f"   - Asignaciones creadas: {len(asignaciones_previas)}")
        
        # 4. Determinar área de trabajo (como en el código original)
        print("\n4. DETERMINANDO ÁREA DE TRABAJO:")
        carpeta = tecnico.get('carpeta', '').upper() if tecnico.get('carpeta') else ''
        cargo = tecnico.get('cargo', '').upper()
        
        # Límites como en el código original
        limites = {
            'FTTH INSTALACIONES': {
                'cinta_aislante': {'cantidad': 3, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 16, 'periodo': 7, 'unidad': 'días'},
            },
            'POSTVENTA': {
                'cinta_aislante': {'cantidad': 3, 'periodo': 15, 'unidad': 'días'},
                'silicona': {'cantidad': 12, 'periodo': 7, 'unidad': 'días'},
            }
        }
        
        area_trabajo = None
        if carpeta:
            for area in limites.keys():
                if area in carpeta:
                    area_trabajo = area
                    break
        
        if area_trabajo is None:
            area_trabajo = 'POSTVENTA'  # Por defecto
        
        print(f"   - Área de trabajo determinada: {area_trabajo}")
        
        # 5. Calcular consumo previo (AQUÍ ESTÁ EL CÁLCULO CRÍTICO)
        print("\n5. CALCULANDO CONSUMO PREVIO (CÁLCULO CRÍTICO):")
        contadores = {
            'cinta_aislante': 0,
            'silicona': 0,
        }
        
        print("   Procesando asignaciones:")
        for i, asignacion in enumerate(asignaciones_previas):
            fecha_asignacion = asignacion['fecha_asignacion']
            
            # ESTE ES EL CÁLCULO QUE PUEDE FALLAR EN EL SERVIDOR
            try:
                diferencia_dias = (fecha_actual - fecha_asignacion).days
                print(f"   - Asignación {i+1}: {fecha_asignacion} -> {diferencia_dias} días")
                
                # Verificar límite de cintas
                if diferencia_dias <= limites[area_trabajo]['cinta_aislante']['periodo']:
                    cantidad = int(asignacion.get('cinta_aislante', 0) or 0)
                    contadores['cinta_aislante'] += cantidad
                    print(f"     * Cinta aislante: +{cantidad} (total: {contadores['cinta_aislante']})")
                
                # Verificar límite de siliconas
                if diferencia_dias <= limites[area_trabajo]['silicona']['periodo']:
                    cantidad = int(asignacion.get('silicona', 0) or 0)
                    contadores['silicona'] += cantidad
                    print(f"     * Silicona: +{cantidad} (total: {contadores['silicona']})")
                    
            except Exception as e:
                print(f"   ❌ ERROR en cálculo de diferencia: {e}")
                print(f"      - fecha_actual: {fecha_actual} (tipo: {type(fecha_actual)})")
                print(f"      - fecha_asignacion: {fecha_asignacion} (tipo: {type(fecha_asignacion)})")
                return False
        
        # 6. Simular validación de nueva asignación
        print("\n6. SIMULANDO VALIDACIÓN DE NUEVA ASIGNACIÓN:")
        nueva_silicona = 2
        nueva_cinta = 1
        
        # Validar límites
        errores = []
        
        if contadores['cinta_aislante'] + nueva_cinta > limites[area_trabajo]['cinta_aislante']['cantidad']:
            limite = limites[area_trabajo]['cinta_aislante']
            error = f"Excede límite de {limite['cantidad']} cintas cada {limite['periodo']} días. Ya asignadas: {contadores['cinta_aislante']}"
            errores.append(error)
            print(f"   ❌ {error}")
        else:
            print(f"   ✅ Cinta aislante OK: {contadores['cinta_aislante']} + {nueva_cinta} <= {limites[area_trabajo]['cinta_aislante']['cantidad']}")
        
        if contadores['silicona'] + nueva_silicona > limites[area_trabajo]['silicona']['cantidad']:
            limite = limites[area_trabajo]['silicona']
            error = f"Excede límite de {limite['cantidad']} siliconas cada {limite['periodo']} días. Ya asignadas: {contadores['silicona']}"
            errores.append(error)
            print(f"   ❌ {error}")
        else:
            print(f"   ✅ Silicona OK: {contadores['silicona']} + {nueva_silicona} <= {limites[area_trabajo]['silicona']['cantidad']}")
        
        # 7. Resultado final
        print("\n7. RESULTADO FINAL:")
        if errores:
            print(f"   ❌ ASIGNACIÓN RECHAZADA - {len(errores)} errores")
            for error in errores:
                print(f"      - {error}")
        else:
            print("   ✅ ASIGNACIÓN APROBADA - Todos los límites OK")
        
        return len(errores) == 0
        
    except mysql.connector.Error as e:
        print(f"❌ Error MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if connection:
            connection.close()

def test_diferentes_zonas_horarias():
    """Probar cálculos con diferentes configuraciones de zona horaria"""
    print("\n🌍 PROBANDO DIFERENTES ZONAS HORARIAS")
    print("=" * 50)
    
    # Simular diferentes zonas horarias
    import pytz
    
    zonas = [
        'UTC',
        'America/Bogota',
        'America/New_York',
        'Europe/Madrid'
    ]
    
    fecha_base = datetime(2025, 1, 15, 10, 30, 0)
    
    print("Comparando cálculos de diferencia de días:")
    for zona in zonas:
        try:
            tz = pytz.timezone(zona)
            fecha_con_tz = tz.localize(fecha_base)
            fecha_actual = datetime.now(tz)
            
            diferencia = (fecha_actual - fecha_con_tz).days
            print(f"   - {zona}: {diferencia} días")
        except Exception as e:
            print(f"   - {zona}: Error - {e}")

def main():
    """Función principal de prueba"""
    print("🧪 PRUEBA DE CÁLCULOS EN SERVIDOR MYSQL")
    print("=" * 60)
    print("Este script simula exactamente el comportamiento de registrar_ferretero")
    print("para identificar dónde fallan los cálculos en el servidor.")
    
    # Ejecutar simulación
    resultado = simular_calculo_limites()
    
    # Probar zonas horarias
    test_diferentes_zonas_horarias()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBA")
    print("=" * 60)
    
    if resultado:
        print("✅ Los cálculos funcionan correctamente en este entorno")
        print("\n💡 Si fallan en el servidor, verificar:")
        print("   1. Zona horaria del servidor vs base de datos")
        print("   2. Versión de Python en el servidor")
        print("   3. Configuración de MySQL en el servidor")
        print("   4. Variables de entorno en el servidor")
    else:
        print("❌ Se detectaron problemas en los cálculos")
        print("\n🔧 Revisar los errores mostrados arriba")

if __name__ == "__main__":
    main()