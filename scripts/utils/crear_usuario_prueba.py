#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error
import bcrypt

def crear_usuario_prueba():
    """Crear un usuario de prueba para testing"""
    try:
        # Configuración de la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@',
            port=3306
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Datos del usuario de prueba
            cedula_prueba = 'test123'
            password_prueba = 'admin'
            nombre_prueba = 'USUARIO DE PRUEBA'
            rol_prueba = 1  # Administrativo
            
            print("=== CREANDO USUARIO DE PRUEBA ===")
            print(f"Cédula: {cedula_prueba}")
            print(f"Contraseña: {password_prueba}")
            print(f"Nombre: {nombre_prueba}")
            print(f"Rol: {rol_prueba}")
            
            # Verificar si el usuario ya existe
            cursor.execute("""
                SELECT recurso_operativo_cedula 
                FROM recurso_operativo 
                WHERE recurso_operativo_cedula = %s
            """, (cedula_prueba,))
            
            if cursor.fetchone():
                print("\n⚠️  El usuario de prueba ya existe. Actualizando contraseña...")
                
                # Encriptar la nueva contraseña
                hashed_password = bcrypt.hashpw(password_prueba.encode('utf-8'), bcrypt.gensalt())
                
                # Actualizar la contraseña
                cursor.execute("""