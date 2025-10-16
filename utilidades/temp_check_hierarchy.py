import mysql.connector
import os

# Configuración de la base de datos
config = {
    'user': 'root',
    'password': '732137A031E4b@',
    'host': 'localhost',
    'database': 'capired',
    'port': 3306
}

try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(buffered=True)
    
    print('=== REGISTRO DE CORTES CUERVO SANDRA CECILIA ===')
    cursor.execute("""
        SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, cargo, super, analista, estado, carpeta, cliente, ciudad
        FROM recurso_operativo 
        WHERE nombre LIKE '%CORTES CUERVO SANDRA CECILIA%' OR nombre LIKE '%SANDRA CECILIA%' OR nombre LIKE '%CORTES CUERVO%'
    """)
    sandra_records = cursor.fetchall()
    
    if sandra_records:
        for record in sandra_records:
            print(f'ID: {record[0]}')
            print(f'Cédula: {record[1]}')
            print(f'Nombre: {record[2]}')
            print(f'Cargo: {record[3]}')
            print(f'Super: {record[4]}')
            print(f'Analista: {record[5]}')
            print(f'Estado: {record[6]}')
            print(f'Carpeta: {record[7]}')
            print(f'Cliente: {record[8]}')
            print(f'Ciudad: {record[9]}')
            print('---')
    else:
        print('No se encontró registro de CORTES CUERVO SANDRA CECILIA')
    
    print('\n=== SUPERVISORES QUE TIENEN A SANDRA COMO ANALISTA ===')
    cursor.execute("""
        SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, cargo, super, analista, carpeta
        FROM recurso_operativo 
        WHERE analista LIKE '%CORTES CUERVO SANDRA CECILIA%' OR analista LIKE '%SANDRA CECILIA%' OR analista LIKE '%CORTES CUERVO%' OR analista LIKE '%SANDRA%'
    """)
    supervisors_under_sandra = cursor.fetchall()
    
    if supervisors_under_sandra:
        for record in supervisors_under_sandra:
            print(f'ID: {record[0]} - Cédula: {record[1]} - Nombre: {record[2]} - Cargo: {record[3]} - Super: {record[4]} - Analista: {record[5]} - Carpeta: {record[6]}')
    else:
        print('No se encontraron supervisores bajo Sandra')
    
    print('\n=== TODOS LOS SUPERVISORES (CARGO = SUPERVISORES) ===')
    cursor.execute("""
        SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, cargo, super, analista, carpeta
        FROM recurso_operativo 
        WHERE cargo = 'SUPERVISORES'
        ORDER BY nombre
    """)
    all_supervisors = cursor.fetchall()
    
    if all_supervisors:
        for record in all_supervisors:
            print(f'ID: {record[0]} - Cédula: {record[1]} - Nombre: {record[2]} - Cargo: {record[3]} - Super: {record[4]} - Analista: {record[5]} - Carpeta: {record[6]}')
    else:
        print('No se encontraron supervisores')
        
    print('\n=== TÉCNICOS QUE TIENEN A SANDRA COMO SUPER ===')
    cursor.execute("""
        SELECT id_codigo_consumidor, recurso_operativo_cedula, nombre, cargo, super, analista, carpeta
        FROM recurso_operativo 
        WHERE super LIKE '%CORTES CUERVO SANDRA CECILIA%' OR super LIKE '%SANDRA CECILIA%' OR super LIKE '%CORTES CUERVO%' OR super LIKE '%SANDRA%'
    """)
    technicians_under_sandra = cursor.fetchall()
    
    if technicians_under_sandra:
        for record in technicians_under_sandra:
            print(f'ID: {record[0]} - Cédula: {record[1]} - Nombre: {record[2]} - Cargo: {record[3]} - Super: {record[4]} - Analista: {record[5]} - Carpeta: {record[6]}')
    else:
        print('No se encontraron técnicos bajo Sandra')
        
except Exception as e:
    print(f'Error: {e}')
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()