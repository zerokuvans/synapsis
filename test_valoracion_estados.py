#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que los estados de valoración
se muestren correctamente basados en la tabla cambios_dotacion
"""

import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT'))
}

def test_valoracion_estados_db():
    """
    Prueba directa en la base de datos para verificar que los estados
    de valoración se almacenen y recuperen correctamente
    """
    
    try:
        print("=" * 60)
        print("PRUEBA DE ESTADOS DE VALORACIÓN - BASE DE DATOS")
        print("=" * 60)
        print(f"Fecha de prueba: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Conectar a la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        print("✅ Conexión a la base de datos exitosa")
        print()
        
        # Consultar registros con estados de valoración
        query = """
        SELECT 
            id_codigo_consumidor,
            pantalon, estado_pantalon,
            botas, estado_botas,
            camisetagris, estado_camiseta_gris,
            camisetapolo, estado_camiseta_polo,
            fecha_registro
        FROM cambios_dotacion 
        WHERE (estado_pantalon IS NOT NULL OR estado_botas IS NOT NULL 
               OR estado_camiseta_gris IS NOT NULL OR estado_camiseta_polo IS NOT NULL)
        ORDER BY fecha_registro DESC 
        LIMIT 10
        """
        
        cursor.execute(query)
        registros = cursor.fetchall()
        
        print(f"Total de registros con estados encontrados: {len(registros)}")
        print()
        
        if registros:
            print("ANÁLISIS DE ESTADOS DE VALORACIÓN EN BD:")
            print("-" * 50)
            
            for i, registro in enumerate(registros, 1):
                print(f"\nRegistro #{i}")
                print(f"Técnico ID: {registro['id_codigo_consumidor']}")
                print(f"Fecha: {registro['fecha_registro']}")
                
                # Verificar cada elemento
                elementos = [
                    ('Pantalón', registro['pantalon'], registro['estado_pantalon']),
                    ('Botas', registro['botas'], registro['estado_botas']),
                    ('Camiseta Gris', registro['camisetagris'], registro['estado_camiseta_gris']),
                    ('Camiseta Polo', registro['camisetapolo'], registro['estado_camiseta_polo'])
                ]
                
                print("Elementos modificados:")
                for nombre, cantidad, estado in elementos:
                    if cantidad and cantidad > 0:
                        print(f"  • {nombre}: Cantidad={cantidad}, Estado={estado or 'SIN ESTADO'}")
                        
                        # Verificar consistencia del estado
                        if estado in ['VALORADO', 'NO VALORADO']:
                            print(f"    ✅ Estado válido: {estado}")
                        elif estado is None:
                            print(f"    ⚠️  Estado no definido")
                        else:
                            print(f"    ❌ Estado inválido: {estado}")
                
                print("-" * 30)
        else:
            print("❌ No se encontraron registros con estados de valoración")
            print("Esto podría indicar que:")
            print("1. No hay cambios registrados")
            print("2. Los estados no se están guardando correctamente")
            print("3. La estructura de la tabla es diferente")
        
        # Verificar estructura de la tabla
        print("\nVERIFICACIÓN DE ESTRUCTURA:")
        print("-" * 30)
        
        cursor.execute("SHOW COLUMNS FROM cambios_dotacion LIKE 'estado_%'")
        columnas_estado = cursor.fetchall()
        
        print(f"Columnas de estado encontradas: {len(columnas_estado)}")
        for columna in columnas_estado:
            print(f"  • {columna['Field']}: {columna['Type']}")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    print("\n" + "=" * 60)
    print("FIN DE LA PRUEBA")
    print("=" * 60)

def test_sql_query_simulation():
    """
    Simula la consulta SQL que usa el endpoint para verificar
    que los datos se recuperen correctamente
    """
    
    try:
        print("\n" + "=" * 60)
        print("SIMULACIÓN DE CONSULTA SQL DEL ENDPOINT")
        print("=" * 60)
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Consulta similar a la del endpoint (simplificada)
        query = """
        SELECT 
            cd.id_codigo_consumidor,
            cd.fecha_cambio,
            cd.fecha_registro,
            cd.observaciones,
            cd.pantalon, cd.pantalon_talla, cd.estado_pantalon,
            cd.botas, cd.botas_talla, cd.estado_botas,
            cd.camisetagris, cd.camiseta_gris_talla, cd.estado_camiseta_gris,
            cd.camisetapolo, cd.camiseta_polo_talla, cd.estado_camiseta_polo,
            ro.nombre as tecnico_nombre,
            ro.recurso_operativo_cedula as tecnico_cedula
        FROM cambios_dotacion cd
        LEFT JOIN recurso_operativo ro ON cd.id_codigo_consumidor = ro.recurso_operativo_cedula
        WHERE (cd.pantalon > 0 OR cd.botas > 0 OR cd.camisetagris > 0 OR cd.camisetapolo > 0)
        ORDER BY cd.fecha_registro DESC
        LIMIT 5
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        print(f"Resultados de la consulta: {len(resultados)}")
        print()
        
        for resultado in resultados:
            print(f"Técnico: {resultado['tecnico_nombre']} (Cédula: {resultado['tecnico_cedula']})")
            print(f"Fecha cambio: {resultado['fecha_cambio']}")
            
            # Simular procesamiento de elementos
            elementos = []
            
            if resultado['pantalon'] and resultado['pantalon'] > 0:
                elementos.append({
                    'elemento': 'Pantalón',
                    'cantidad': resultado['pantalon'],
                    'talla': resultado['pantalon_talla'],
                    'estado_valoracion': resultado['estado_pantalon'],
                    'es_valorado': resultado['estado_pantalon'] == 'VALORADO'
                })
            
            if resultado['botas'] and resultado['botas'] > 0:
                elementos.append({
                    'elemento': 'Botas',
                    'cantidad': resultado['botas'],
                    'talla': resultado['botas_talla'],
                    'estado_valoracion': resultado['estado_botas'],
                    'es_valorado': resultado['estado_botas'] == 'VALORADO'
                })
            
            if resultado['camisetagris'] and resultado['camisetagris'] > 0:
                elementos.append({
                    'elemento': 'Camiseta Gris',
                    'cantidad': resultado['camisetagris'],
                    'talla': resultado['camiseta_gris_talla'],
                    'estado_valoracion': resultado['estado_camiseta_gris'],
                    'es_valorado': resultado['estado_camiseta_gris'] == 'VALORADO'
                })
            
            if resultado['camisetapolo'] and resultado['camisetapolo'] > 0:
                elementos.append({
                    'elemento': 'Camiseta Polo',
                    'cantidad': resultado['camisetapolo'],
                    'talla': resultado['camiseta_polo_talla'],
                    'estado_valoracion': resultado['estado_camiseta_polo'],
                    'es_valorado': resultado['estado_camiseta_polo'] == 'VALORADO'
                })
            
            print("Elementos procesados:")
            for elemento in elementos:
                estado_texto = "VALORADO" if elemento['es_valorado'] else "NO VALORADO"
                print(f"  • {elemento['elemento']}: {elemento['cantidad']} - {estado_texto}")
                print(f"    Estado original: {elemento['estado_valoracion']}")
                print(f"    es_valorado: {elemento['es_valorado']}")
            
            print("-" * 40)
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_valoracion_estados_db()
    test_sql_query_simulation()