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
    
    print("=== VERIFICAR RELACIÓN ENTRE TABLAS ===")
    
    # Verificar qué contiene el campo tecnico en mpa_licencia_conducir
    cursor.execute("SELECT tecnico, tipo_licencia, fecha_vencimiento FROM capired.mpa_licencia_conducir")
    licencias = cursor.fetchall()
    print("Datos en mpa_licencia_conducir:")
    for lic in licencias:
        print(f"  tecnico: '{lic['tecnico']}' - tipo: {lic['tipo_licencia']} - vencimiento: {lic['fecha_vencimiento']}")
    
    print("\n=== VERIFICAR SI 'tecnico' ES id_codigo_consumidor ===")
    # Verificar si el campo tecnico corresponde a id_codigo_consumidor
    cursor.execute("""
        SELECT ro.id_codigo_consumidor, ro.recurso_operativo_cedula, ro.nombre
        FROM capired.recurso_operativo ro
        WHERE ro.id_codigo_consumidor IN (SELECT DISTINCT tecnico FROM capired.mpa_licencia_conducir WHERE tecnico IS NOT NULL)
    """)
    
    tecnicos_con_licencia = cursor.fetchall()
    print("Técnicos que tienen licencia (por id_codigo_consumidor):")
    for tec in tecnicos_con_licencia:
        print(f"  ID: {tec['id_codigo_consumidor']} - Cédula: {tec['recurso_operativo_cedula']} - Nombre: {tec['nombre']}")
    
    print("\n=== PROBAR JOIN CORRECTO ===")
    # Probar el JOIN usando id_codigo_consumidor en lugar de cedula
    cursor.execute("""
        SELECT 
            ro.id_codigo_consumidor,
            ro.recurso_operativo_cedula,
            ro.nombre,
            mlc.tipo_licencia,
            mlc.fecha_vencimiento
        FROM capired.recurso_operativo ro
        LEFT JOIN capired.mpa_licencia_conducir mlc ON ro.id_codigo_consumidor = mlc.tecnico
        WHERE mlc.tipo_licencia IS NOT NULL
    """)
    
    resultado = cursor.fetchall()
    print("Resultado del JOIN correcto:")
    for res in resultado:
        print(f"  ID: {res['id_codigo_consumidor']} - Cédula: {res['recurso_operativo_cedula']} - Nombre: {res['nombre']}")
        print(f"    Licencia: {res['tipo_licencia']} - Vencimiento: {res['fecha_vencimiento']}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f'Error: {e}')