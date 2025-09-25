#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico simple para validar el stock de dotaciones
"""

import mysql.connector
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def main():
    print("=" * 60)
    print("DIAGNÓSTICO DE STOCK DE DOTACIONES")
    print("=" * 60)
    
    # Configuración de base de datos
    db_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DB', 'capired'),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    print(f"\n🔧 CONFIGURACIÓN:")
    print(f"   Host: {db_config['host']}")
    print(f"   Puerto: {db_config['port']}")
    print(f"   Usuario: {db_config['user']}")
    print(f"   Base de datos: {db_config['database']}")
    print(f"   Password: {'***' if db_config['password'] else 'NO_PASSWORD'}")
    
    # Intentar conexión
    try:
        print(f"\n🔌 PROBANDO CONEXIÓN...")
        connection = mysql.connector.connect(**db_config)
        print(f"✓ Conexión exitosa")
        
        cursor = connection.cursor(dictionary=True)
        
        # Verificar tablas
        print(f"\n📊 VERIFICANDO TABLAS:")
        tablas = ['stock_ferretero', 'dotaciones', 'cambios_dotacion']
        
        for tabla in tablas:
            try:
                cursor.execute(f"SELECT COUNT(*) as total FROM {tabla}")
                total = cursor.fetchone()['total']
                print(f"   ✓ {tabla}: {total} registros")
            except Exception as e:
                print(f"   ✗ {tabla}: Error - {e}")
        
        # Verificar vista
        print(f"\n👁️ VERIFICANDO VISTA:")
        try:
            cursor.execute("SELECT COUNT(*) as total FROM vista_stock_dotaciones")
            total = cursor.fetchone()['total']
            print(f"   ✓ vista_stock_dotaciones: {total} registros")
        except Exception as e:
            print(f"   ✗ vista_stock_dotaciones: Error - {e}")
        
        # Probar cálculo de stock
        print(f"\n🧮 PROBANDO CÁLCULO DE STOCK:")
        try:
            # Obtener un material
            cursor.execute("SELECT DISTINCT material_tipo FROM stock_ferretero LIMIT 1")
            material_test = cursor.fetchone()
            
            if material_test:
                material = material_test['material_tipo']
                print(f"   Material de prueba: {material}")
                
                # Stock inicial
                cursor.execute("""
                    SELECT COALESCE(SUM(cantidad_disponible), 0) as stock_inicial
                    FROM stock_ferretero 
                    WHERE material_tipo = %s
                """, (material,))
                stock_inicial = cursor.fetchone()['stock_inicial']
                
                # Asignaciones
                query_asignaciones = f"""
                    SELECT COALESCE(SUM(
                        CASE 
                            WHEN %s = 'pantalon' THEN pantalon
                            WHEN %s = 'camisetagris' THEN camisetagris
                            WHEN %s = 'guerrera' THEN guerrera
                            WHEN %s = 'camisetapolo' THEN camisetapolo
                            WHEN %s = 'guantes_nitrilo' THEN guantes_nitrilo
                            WHEN %s = 'guantes_carnaza' THEN guantes_carnaza
                            WHEN %s = 'gafas' THEN gafas
                            WHEN %s = 'gorra' THEN gorra
                            WHEN %s = 'casco' THEN casco
                            WHEN %s = 'botas' THEN botas
                            ELSE 0
                        END
                    ), 0) as total_asignaciones
                    FROM dotaciones
                """
                cursor.execute(query_asignaciones, (material,) * 10)
                total_asignaciones = cursor.fetchone()['total_asignaciones']
                
                # Cambios
                query_cambios = f"""
                    SELECT COALESCE(SUM(
                        CASE 
                            WHEN %s = 'pantalon' THEN pantalon
                            WHEN %s = 'camisetagris' THEN camisetagris
                            WHEN %s = 'guerrera' THEN guerrera
                            WHEN %s = 'camisetapolo' THEN camisetapolo
                            WHEN %s = 'guantes_nitrilo' THEN guantes_nitrilo
                            WHEN %s = 'guantes_carnaza' THEN guantes_carnaza
                            WHEN %s = 'gafas' THEN gafas
                            WHEN %s = 'gorra' THEN gorra
                            WHEN %s = 'casco' THEN casco
                            WHEN %s = 'botas' THEN botas
                            ELSE 0
                        END
                    ), 0) as total_cambios
                    FROM cambios_dotacion
                """
                cursor.execute(query_cambios, (material,) * 10)
                total_cambios = cursor.fetchone()['total_cambios']
                
                # Cálculo final
                stock_actual = stock_inicial - total_asignaciones - total_cambios
                
                print(f"   Stock inicial: {stock_inicial}")
                print(f"   Total asignaciones: {total_asignaciones}")
                print(f"   Total cambios: {total_cambios}")
                print(f"   Stock actual: {stock_actual}")
                print(f"   Fórmula: {stock_inicial} - {total_asignaciones} - {total_cambios} = {stock_actual}")
                
            else:
                print(f"   ✗ No hay materiales en stock_ferretero")
                
        except Exception as e:
            print(f"   ✗ Error en cálculo: {e}")
        
        # Verificar endpoint
        print(f"\n🌐 VERIFICANDO ENDPOINT:")
        try:
            # Simular el mismo cálculo que hace el endpoint
            cursor.execute("SELECT DISTINCT material_tipo FROM stock_ferretero ORDER BY material_tipo")
            materiales = cursor.fetchall()
            print(f"   ✓ Materiales encontrados: {len(materiales)}")
            
            for material_row in materiales[:3]:  # Solo los primeros 3
                material = material_row['material_tipo']
                
                # Mismo cálculo que en el endpoint
                cursor.execute("""
                    SELECT COALESCE(SUM(cantidad_disponible), 0) as stock_inicial
                    FROM stock_ferretero 
                    WHERE material_tipo = %s
                """, (material,))
                stock_inicial = cursor.fetchone()['stock_inicial']
                
                print(f"     - {material}: Stock inicial = {stock_inicial}")
                
        except Exception as e:
            print(f"   ✗ Error verificando endpoint: {e}")
        
        connection.close()
        print(f"\n✅ DIAGNÓSTICO COMPLETADO")
        
    except mysql.connector.Error as e:
        print(f"\n❌ ERROR DE CONEXIÓN: {e}")
        print(f"\nPOSIBLES CAUSAS:")
        print(f"   1. Servidor de base de datos no está ejecutándose")
        print(f"   2. Credenciales incorrectas")
        print(f"   3. Base de datos no existe")
        print(f"   4. Problemas de red/firewall")
        print(f"   5. Variables de entorno no configuradas")
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
    
    print("=" * 60)

if __name__ == '__main__':
    main()