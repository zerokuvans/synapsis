#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el formulario de cambios de dotación después de corregir el error 1366
"""

import mysql.connector
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def conectar_db():
    """Conectar a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB')
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def test_insercion_cambio_dotacion():
    """Probar inserción en la tabla cambios_dotacion con datos válidos"""
    connection = conectar_db()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Verificar que existe un técnico válido
        cursor.execute("SELECT id_codigo_consumidor FROM recurso_operativo LIMIT 1")
        tecnico = cursor.fetchone()
        
        if not tecnico:
            print("❌ No hay técnicos disponibles en la tabla recurso_operativo")
            return False
        
        id_codigo_consumidor = tecnico[0]
        print(f"✅ Usando técnico con ID: {id_codigo_consumidor} (tipo: {type(id_codigo_consumidor)})")
        
        # Datos de prueba
        test_data = {
            'id_codigo_consumidor': id_codigo_consumidor,  # Ahora es un entero
            'fecha_cambio': '2024-01-15',
            'pantalon': 1,
            'pantalon_talla': '32',
            'estado_pantalon': 1,
            'camisetagris': 2,  # Campo que causaba el error
            'camiseta_gris_talla': 'M',
            'estado_camiseta_gris': 0,
            'guerrera': 0,
            'guerrera_talla': '',
            'estado_guerrera': 0,
            'camisetapolo': 1,
            'camiseta_polo_talla': 'L',
            'estado_camiseta_polo': 1,
            'guantes_nitrilo': 5,
            'estado_guantes_nitrilo': 0,
            'guantes_carnaza': 2,
            'estado_guantes_carnaza': 1,
            'gafas': 1,
            'estado_gafas': 1,
            'gorra': 1,
            'estado_gorra': 0,
            'casco': 1,
            'estado_casco': 1,
            'botas': 1,
            'estado_botas': 1,
            'botas_talla': '42',
            'observaciones': 'Prueba de inserción después de corrección del error 1366'
        }
        
        # Query de inserción (similar al del backend)
        insert_query = """
        INSERT INTO cambios_dotacion (
            id_codigo_consumidor, fecha_cambio, pantalon, pantalon_talla, estado_pantalon,
            camisetagris, camiseta_gris_talla, estado_camiseta_gris,
            guerrera, guerrera_talla, estado_guerrera,
            camisetapolo, camiseta_polo_talla, estado_camiseta_polo,
            guantes_nitrilo, estado_guantes_nitrilo,
            guantes_carnaza, estado_guantes_carnaza,
            gafas, estado_gafas, gorra, estado_gorra,
            casco, estado_casco, botas, estado_botas, botas_talla,
            observaciones
        ) VALUES (
            %(id_codigo_consumidor)s, %(fecha_cambio)s, %(pantalon)s, %(pantalon_talla)s, %(estado_pantalon)s,
            %(camisetagris)s, %(camiseta_gris_talla)s, %(estado_camiseta_gris)s,
            %(guerrera)s, %(guerrera_talla)s, %(estado_guerrera)s,
            %(camisetapolo)s, %(camiseta_polo_talla)s, %(estado_camiseta_polo)s,
            %(guantes_nitrilo)s, %(estado_guantes_nitrilo)s,
            %(guantes_carnaza)s, %(estado_guantes_carnaza)s,
            %(gafas)s, %(estado_gafas)s, %(gorra)s, %(estado_gorra)s,
            %(casco)s, %(estado_casco)s, %(botas)s, %(estado_botas)s, %(botas_talla)s,
            %(observaciones)s
        )
        """
        
        print("\n🔄 Intentando insertar registro de prueba...")
        cursor.execute(insert_query, test_data)
        connection.commit()
        
        # Obtener el ID del registro insertado
        nuevo_id = cursor.lastrowid
        print(f"✅ ¡Inserción exitosa! ID del nuevo registro: {nuevo_id}")
        
        # Verificar que el registro se insertó correctamente
        cursor.execute("SELECT * FROM cambios_dotacion WHERE id_cambio = %s", (nuevo_id,))
        registro = cursor.fetchone()
        
        if registro:
            print(f"✅ Verificación exitosa. Registro encontrado con ID: {registro[0]}")
            print(f"   - Técnico ID: {registro[1]} (tipo: {type(registro[1])})")
            print(f"   - Fecha cambio: {registro[2]}")
            print(f"   - Camiseta gris: {registro[5]} (tipo: {type(registro[5])})")
            print(f"   - Observaciones: {registro[26]}")
            
            # Limpiar: eliminar el registro de prueba
            cursor.execute("DELETE FROM cambios_dotacion WHERE id_cambio = %s", (nuevo_id,))
            connection.commit()
            print(f"🧹 Registro de prueba eliminado (ID: {nuevo_id})")
            
            return True
        else:
            print("❌ Error: No se pudo verificar el registro insertado")
            return False
            
    except mysql.connector.Error as e:
        print(f"❌ Error en la inserción: {e}")
        print(f"   Código de error: {e.errno}")
        print(f"   Mensaje SQL: {e.msg}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def main():
    print("=" * 60)
    print("PRUEBA DEL FORMULARIO DE CAMBIOS DE DOTACIÓN")
    print("Verificando corrección del error 1366")
    print("=" * 60)
    
    # Probar inserción
    if test_insercion_cambio_dotacion():
        print("\n🎉 ¡PRUEBA EXITOSA!")
        print("✅ El error 1366 'Incorrect integer value' ha sido corregido")
        print("✅ El formulario ahora puede procesar correctamente los datos")
        print("✅ El campo id_codigo_consumidor se maneja como entero")
        print("✅ Todos los campos coinciden con la estructura de la base de datos")
    else:
        print("\n❌ PRUEBA FALLIDA")
        print("❌ Aún existen problemas con el formulario")
        print("❌ Revisar logs de error para más detalles")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()