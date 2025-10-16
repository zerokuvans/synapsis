#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Conectar a la base de datos
connection = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    charset='utf8mb4',
    collation='utf8mb4_unicode_ci'
)

cursor = connection.cursor(dictionary=True)

print('=== TÉCNICOS DISPONIBLES ===')
cursor.execute('SELECT recurso_operativo_cedula, carpeta, cargo FROM recurso_operativo LIMIT 5')
tecnicos = cursor.fetchall()
for t in tecnicos:
    cedula = t['recurso_operativo_cedula']
    carpeta = t['carpeta']
    cargo = t['cargo']
    print(f'Cédula: {cedula}, Carpeta: {carpeta}, Cargo: {cargo}')

print('\n=== CARPETAS EN PRESUPUESTO_CARPETA ===')
cursor.execute('SELECT presupuesto_carpeta FROM presupuesto_carpeta LIMIT 5')
carpetas = cursor.fetchall()
for c in carpetas:
    print(f'Carpeta: {c["presupuesto_carpeta"]}')

print('\n=== CARGOS EN PRESUPUESTO_CARGO ===')
cursor.execute('SELECT cargo FROM presupuesto_cargo LIMIT 5')
cargos = cursor.fetchall()
for c in cargos:
    print(f'Cargo: {c["cargo"]}')

cursor.close()
connection.close()