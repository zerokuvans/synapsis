#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector

def check_presupuesto_carpeta():
    """Verificar si existe la tabla presupuesto_carpeta y su estructura"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root', 
            password='732137A031E4b@',
            database='capired'
        )
        cursor = conn.cursor()
        
        # Verificar si existe la tabla presupuesto_carpeta
        cursor.execute("""
            SELECT COUNT(*) as existe 
            FROM information_schema.tables 
            WHERE table_schema = 'capired' AND table_name = 'presupuesto_carpeta'
        """)
        
        resultado = cursor.fetchone()
        print(f'Tabla presupuesto_carpeta existe: {resultado[0] > 0}')
        
        if resultado[0] > 0:
            print('\nEstructura de presupuesto_carpeta:')
            cursor.execute('DESCRIBE presupuesto_carpeta')
            for col in cursor.fetchall():
                print(f'  {col[0]}: {col[1]}')
                
            print('\nPrimeros 5 registros de presupuesto_carpeta:')
            cursor.execute('SELECT * FROM presupuesto_carpeta LIMIT 5')
            for row in cursor.fetchall():
                print(f'  {row}')
        else:
            print('\nTablas disponibles que contienen "presupuesto" o "carpeta":')
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'capired' 
                AND (table_name LIKE '%presupuesto%' OR table_name LIKE '%carpeta%')
            """)
            
            tablas = cursor.fetchall()
            for tabla in tablas:
                print(f'  - {tabla[0]}')
                
            if not tablas:
                print('  No se encontraron tablas relacionadas')
                
                # Mostrar todas las tablas disponibles
                print('\nTodas las tablas disponibles:')
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'capired'
                    ORDER BY table_name
                """)
                
                todas_tablas = cursor.fetchall()
                for tabla in todas_tablas:
                    print(f'  - {tabla[0]}')
                
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    check_presupuesto_carpeta()