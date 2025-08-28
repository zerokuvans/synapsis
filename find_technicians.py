#!/usr/bin/env python3
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# Configuración de la base de datos
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'capired')
}

try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    
    # Buscar técnicos disponibles
    cursor.execute("""
        SELECT id_codigo_consumidor, nombre, cargo, carpeta 
        FROM recurso_operativo 
        WHERE cargo LIKE '%TECNICO%' 
        ORDER BY id_codigo_consumidor 
        LIMIT 10
    """)
    
    tecnicos = cursor.fetchall()
    
    print("Técnicos disponibles:")
    for tecnico in tecnicos:
        print(f"ID: {tecnico['id_codigo_consumidor']}, Nombre: {tecnico['nombre']}, Cargo: {tecnico['cargo']}, Carpeta: {tecnico.get('carpeta', 'N/A')}")
    
    # Verificar asignaciones recientes del técnico ID 1
    print("\n=== Asignaciones recientes del técnico ID 1 ===")
    cursor.execute("""
        SELECT fecha_asignacion, silicona, amarres_negros, amarres_blancos, cinta_aislante
        FROM ferretero 
        WHERE id_codigo_consumidor = 1
        ORDER BY fecha_asignacion DESC
        LIMIT 5
    """)
    
    asignaciones = cursor.fetchall()
    for asignacion in asignaciones:
        print(f"Fecha: {asignacion['fecha_asignacion']}, Silicona: {asignacion['silicona']}, Amarres N: {asignacion['amarres_negros']}, Amarres B: {asignacion['amarres_blancos']}, Cinta: {asignacion['cinta_aislante']}")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()