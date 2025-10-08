#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para poblar la tabla dotaciones en producción con datos de prueba
Este script ayuda a resolver el problema de stock cuando la tabla dotaciones está vacía
"""

import mysql.connector
import os
from datetime import datetime, date
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def conectar_bd_produccion():
    """Conectar a la base de datos de producción"""
    try:
        host_prod = os.getenv('DB_HOST_PROD', 'localhost')
        user_prod = os.getenv('DB_USER_PROD', 'root')
        pass_prod = os.getenv('DB_PASS_PROD', '')
        db_prod = os.getenv('DB_NAME_PROD', 'synapsis_db')
        
        print(f"🔗 Conectando a producción:")
        print(f"   Host: {host_prod}")
        print(f"   Usuario: {user_prod}")
        print(f"   Base de datos: {db_prod}")
        
        conexion = mysql.connector.connect(
            host=host_prod,
            user=user_prod,
            password=pass_prod,
            database=db_prod
        )
        return conexion
    except Exception as e:
        print(f"❌ Error conectando a BD producción: {e}")
        return None

def verificar_estructura_dotaciones(cursor):
    """Verificar la estructura de la tabla dotaciones"""
    try:
        cursor.execute("DESCRIBE dotaciones")
        estructura = cursor.fetchall()
        
        print("\n📋 ESTRUCTURA DE LA TABLA DOTACIONES:")
        print("-" * 60)
        for campo in estructura:
            print(f"   {campo[0]} - {campo[1]} - {campo[2]} - {campo[3]}")
        
        return True
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False

def obtener_recursos_operativos(cursor):
    """Obtener lista de recursos operativos disponibles"""
    try:
        cursor.execute("SELECT id, nombre FROM recurso_operativo LIMIT 10")
        recursos = cursor.fetchall()
        
        print("\n👥 RECURSOS OPERATIVOS DISPONIBLES:")
        print("-" * 50)
        for recurso in recursos:
            print(f"   ID: {recurso[0]} - Nombre: {recurso[1]}")
        
        return recursos
    except Exception as e:
        print(f"❌ Error obteniendo recursos operativos: {e}")
        return []

def verificar_dotaciones_existentes(cursor):
    """Verificar dotaciones existentes"""
    try:
        cursor.execute("SELECT COUNT(*) FROM dotaciones")
        count = cursor.fetchone()[0]
        
        print(f"\n📊 DOTACIONES EXISTENTES: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM dotaciones LIMIT 5")
            dotaciones = cursor.fetchall()
            print("\n📋 MUESTRA DE DOTACIONES EXISTENTES:")
            for dot in dotaciones:
                print(f"   {dot}")
        
        return count
    except Exception as e:
        print(f"❌ Error verificando dotaciones: {e}")
        return 0

def generar_datos_prueba_dotaciones(recursos_operativos):
    """Generar datos de prueba para dotaciones"""
    if not recursos_operativos:
        print("❌ No hay recursos operativos disponibles")
        return []
    
    # Tipos de elementos comunes en dotaciones
    tipos_elementos = [
        'pantalon', 'camiseta', 'botas', 'casco', 'guantes',
        'chaleco', 'gafas', 'cinturon', 'overol'
    ]
    
    datos_prueba = []
    fecha_actual = date.today()
    
    # Generar dotaciones para los primeros 3 recursos operativos
    for i, recurso in enumerate(recursos_operativos[:3]):
        for j, tipo_elemento in enumerate(tipos_elementos[:3]):  # Solo 3 tipos por recurso
            dotacion = {
                'recurso_operativo_id': recurso[0],
                'tipo_elemento': tipo_elemento,
                'cantidad': 1 + (i * j) % 3,  # Cantidad variable entre 1-3
                'fecha_asignacion': fecha_actual,
                'estado': 'activo'
            }
            datos_prueba.append(dotacion)
    
    return datos_prueba

def insertar_dotaciones_prueba(cursor, datos_prueba, confirmar=True):
    """Insertar dotaciones de prueba"""
    if not datos_prueba:
        print("❌ No hay datos de prueba para insertar")
        return False
    
    print(f"\n📝 DATOS DE PRUEBA A INSERTAR: {len(datos_prueba)} dotaciones")
    print("-" * 60)
    
    for i, dotacion in enumerate(datos_prueba[:5]):  # Mostrar solo las primeras 5
        print(f"   {i+1}. Recurso: {dotacion['recurso_operativo_id']}, "
              f"Elemento: {dotacion['tipo_elemento']}, "
              f"Cantidad: {dotacion['cantidad']}")
    
    if len(datos_prueba) > 5:
        print(f"   ... y {len(datos_prueba) - 5} más")
    
    if confirmar:
        respuesta = input("\n¿Deseas continuar con la inserción? (s/n): ")
        if respuesta.lower() != 's':
            print("❌ Inserción cancelada por el usuario")
            return False
    
    try:
        query = """
        INSERT INTO dotaciones 
        (recurso_operativo_id, tipo_elemento, cantidad, fecha_asignacion, estado)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        insertados = 0
        for dotacion in datos_prueba:
            try:
                cursor.execute(query, (
                    dotacion['recurso_operativo_id'],
                    dotacion['tipo_elemento'],
                    dotacion['cantidad'],
                    dotacion['fecha_asignacion'],
                    dotacion['estado']
                ))
                insertados += 1
            except Exception as e:
                print(f"⚠️  Error insertando dotación {dotacion}: {e}")
        
        print(f"\n✅ DOTACIONES INSERTADAS: {insertados}/{len(datos_prueba)}")
        return insertados > 0
        
    except Exception as e:
        print(f"❌ Error en inserción masiva: {e}")
        return False

def verificar_impacto_stock(cursor):
    """Verificar el impacto en el cálculo de stock después de insertar dotaciones"""
    try:
        # Verificar vista de stock
        cursor.execute("SELECT * FROM vista_stock_dotaciones LIMIT 10")
        stock_vista = cursor.fetchall()
        
        print("\n📊 IMPACTO EN VISTA DE STOCK:")
        print("-" * 50)
        
        if stock_vista:
            for item in stock_vista:
                print(f"   {item}")
        else:
            print("   No hay datos en vista_stock_dotaciones")
        
        # Verificar totales por tipo de elemento
        cursor.execute("""
        SELECT tipo_elemento, SUM(cantidad) as total_asignado
        FROM dotaciones 
        GROUP BY tipo_elemento
        ORDER BY total_asignado DESC
        """)
        
        totales = cursor.fetchall()
        print("\n📈 TOTALES POR TIPO DE ELEMENTO:")
        print("-" * 40)
        for total in totales:
            print(f"   {total[0]}: {total[1]} unidades")
            
    except Exception as e:
        print(f"❌ Error verificando impacto: {e}")

def main():
    """Función principal"""
    print("🚀 INICIANDO POBLACIÓN DE DOTACIONES EN PRODUCCIÓN")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Conectar a producción
    conn = conectar_bd_produccion()
    if not conn:
        print("❌ No se pudo conectar a la base de datos de producción")
        print("💡 Verifica las variables de entorno en el archivo .env")
        return
    
    cursor = conn.cursor()
    
    try:
        # Verificar estructura
        if not verificar_estructura_dotaciones(cursor):
            return
        
        # Verificar dotaciones existentes
        count_existentes = verificar_dotaciones_existentes(cursor)
        
        # Obtener recursos operativos
        recursos = obtener_recursos_operativos(cursor)
        if not recursos:
            print("❌ No hay recursos operativos disponibles")
            return
        
        # Generar datos de prueba
        datos_prueba = generar_datos_prueba_dotaciones(recursos)
        
        # Insertar datos
        if insertar_dotaciones_prueba(cursor, datos_prueba):
            conn.commit()
            print("\n✅ TRANSACCIÓN CONFIRMADA")
            
            # Verificar impacto
            verificar_impacto_stock(cursor)
        else:
            conn.rollback()
            print("\n❌ TRANSACCIÓN CANCELADA")
    
    except Exception as e:
        print(f"❌ Error general: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()
    
    print("\n" + "="*80)
    print("✅ PROCESO COMPLETADO")
    print("💡 Ahora puedes probar el endpoint de refresh-stock-dotaciones")
    print("="*80)

if __name__ == "__main__":
    main()