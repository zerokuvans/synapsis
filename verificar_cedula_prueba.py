#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from datetime import datetime

connection = mysql.connector.connect(
    host='localhost',
    database='capired',
    user='root',
    password='732137A031E4b@'
)

cursor = connection.cursor(dictionary=True)

# Verificar si existe la cédula de prueba
cedula = '1030545270'
cursor.execute('SELECT * FROM recurso_operativo WHERE recurso_operativo_cedula = %s', (cedula,))
usuario = cursor.fetchone()

if usuario:
    print(f'✅ Usuario encontrado: {usuario["nombre"]}')
else:
    print(f'❌ Usuario con cédula {cedula} NO encontrado')
    
# Verificar registros de asistencia para hoy
fecha_hoy = datetime.now().date()
cursor.execute('SELECT * FROM asistencia WHERE cedula = %s AND DATE(fecha_asistencia) = %s', (cedula, fecha_hoy))
asistencia = cursor.fetchone()

if asistencia:
    print(f'✅ Registro de asistencia encontrado: ID {asistencia["id_asistencia"]}')
    print(f'   Hora inicio: {asistencia["hora_inicio"]}')
    print(f'   Estado: {asistencia["estado"]}')
    print(f'   Novedad: {asistencia["novedad"]}')
else:
    print(f'❌ No hay registro de asistencia para hoy')

cursor.close()
connection.close()