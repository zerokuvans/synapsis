#!/usr/bin/env python3
import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost', 
        user='root', 
        password='732137A031E4b@', 
        database='capired'
    )
    cursor = connection.cursor(dictionary=True)
    
    print('📊 DATOS EN presupuesto_carpeta:')
    cursor.execute('SELECT * FROM presupuesto_carpeta')
    datos = cursor.fetchall()
    
    if datos:
        for i, dato in enumerate(datos, 1):
            carpeta = dato['presupuesto_carpeta']
            eventos = dato['presupuesto_eventos']
            diario = dato['presupuesto_diario']
            print(f'  {i}. Carpeta: {carpeta}')
            print(f'     Eventos: {eventos}')
            print(f'     Diario: {diario}')
            print()
    else:
        print('  ❌ No hay datos en presupuesto_carpeta')
        print('  ℹ️  Insertando datos de ejemplo...')
        
        # Insertar datos de ejemplo
        datos_ejemplo = [
            ('CARP001', 50, 150000),
            ('CARP002', 75, 200000),
            ('CARP003', 40, 120000),
            ('Carpeta Operativa 1', 50, 150000),
            ('Carpeta Operativa 2', 75, 200000),
            ('Carpeta Administrativa', 40, 120000)
        ]
        
        for carpeta, eventos, diario in datos_ejemplo:
            cursor.execute("""
                INSERT IGNORE INTO presupuesto_carpeta 
                (presupuesto_carpeta, presupuesto_eventos, presupuesto_diario) 
                VALUES (%s, %s, %s)
            """, (carpeta, eventos, diario))
        
        connection.commit()
        print('  ✅ Datos de ejemplo insertados')
        
        # Mostrar datos insertados
        cursor.execute('SELECT * FROM presupuesto_carpeta')
        datos_nuevos = cursor.fetchall()
        print('  📊 Datos insertados:')
        for i, dato in enumerate(datos_nuevos, 1):
            carpeta = dato['presupuesto_carpeta']
            eventos = dato['presupuesto_eventos']
            diario = dato['presupuesto_diario']
            print(f'    {i}. {carpeta} - Eventos: {eventos} - Diario: {diario}')
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f'❌ Error: {e}')