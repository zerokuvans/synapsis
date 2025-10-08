#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error

def buscar_analista_valido():
    """Buscar un analista válido para hacer las pruebas"""
    
    try:
        # Configuración de conexión
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            print("=== BUSCANDO ANALISTA VÁLIDO PARA PRUEBAS ===")
            print()
            
            # Buscar usuarios que sean analistas (que tengan técnicos asignados)
            print("1. Buscando usuarios que sean analistas (con técnicos asignados)...")
            cursor.execute("""
                SELECT DISTINCT
                    ro1.id_codigo_consumidor,
                    ro1.recurso_operativo_cedula,
                    ro1.nombre,
                    ro1.analista,
                    ro1.estado,
                    ro1.id_roles,
                    COUNT(ro2.id_codigo_consumidor) as tecnicos_asignados
                FROM recurso_operativo ro1
                LEFT JOIN recurso_operativo ro2 ON ro1.nombre = ro2.analista
                WHERE ro1.estado = 'Activo'
                AND ro2.analista IS NOT NULL
                GROUP BY ro1.id_codigo_consumidor, ro1.recurso_operativo_cedula, ro1.nombre, ro1.analista, ro1.estado, ro1.id_roles
                HAVING tecnicos_asignados > 0
                ORDER BY tecnicos_asignados DESC
                LIMIT 5
            """)
            
            analistas_con_tecnicos = cursor.fetchall()
            
            if analistas_con_tecnicos:
                print(f"✓ Encontrados {len(analistas_con_tecnicos)} analistas con técnicos asignados:")
                for analista in analistas_con_tecnicos:
                    print(f"  - {analista['nombre']}")
                    print(f"    Cédula: {analista['recurso_operativo_cedula']}")
                    print(f"    ID: {analista['id_codigo_consumidor']}")
                    print(f"    Estado: {analista['estado']}")
                    print(f"    ID Roles: {analista['id_roles']}")
                    print(f"    Técnicos asignados: {analista['tecnicos_asignados']}")
                    print()
                
                # Usar el primer analista para las pruebas
                analista_prueba = analistas_con_tecnicos[0]
                print(f"=== ANALISTA SELECCIONADO PARA PRUEBAS ===")
                print(f"Nombre: {analista_prueba['nombre']}")
                print(f"Cédula: {analista_prueba['recurso_operativo_cedula']}")
                print(f"ID: {analista_prueba['id_codigo_consumidor']}")
                print(f"Técnicos asignados: {analista_prueba['tecnicos_asignados']}")
                
                # Verificar algunos técnicos asignados a este analista
                print(f"\n2. Verificando técnicos asignados a {analista_prueba['nombre']}...")
                cursor.execute("""
                    SELECT 
                        recurso_operativo_cedula,
                        nombre,
                        estado,
                        analista
                    FROM recurso_operativo 
                    WHERE analista = %s
                    AND estado = 'Activo'
                    LIMIT 5
                """, (analista_prueba['nombre'],))
                
                tecnicos = cursor.fetchall()
                
                if tecnicos:
                    print(f"✓ Primeros 5 técnicos asignados:")
                    for tecnico in tecnicos:
                        print(f"  - {tecnico['nombre']} (Cédula: {tecnico['recurso_operativo_cedula']})")
                else:
                    print("✗ No se encontraron técnicos asignados")
                
                return analista_prueba
                
            else:
                print("✗ No se encontraron analistas con técnicos asignados")
                return None
            
    except Error as e:
        print(f"Error de MySQL: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    analista = buscar_analista_valido()
    if analista:
        print(f"\n=== CREDENCIALES PARA PRUEBAS ===")
        print(f"Usuario: {analista['recurso_operativo_cedula']}")
        print(f"Contraseña: 123456 (contraseña por defecto)")
        print(f"Nombre: {analista['nombre']}")
    else:
        print("\n✗ No se pudo encontrar un analista válido para las pruebas")