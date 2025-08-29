#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script interactivo para ejecutar triggers MySQL en localhost
Permite al usuario ingresar sus credenciales de MySQL
"""

import mysql.connector
import getpass
import os
import sys

def conectar_mysql_interactivo():
    """
    Conecta a MySQL pidiendo credenciales al usuario
    """
    print("🔐 CONFIGURACIÓN DE CONEXIÓN MYSQL")
    print("=" * 50)
    
    # Solicitar credenciales
    host = input("Host (presiona Enter para 'localhost'): ").strip() or "localhost"
    puerto = input("Puerto (presiona Enter para '3306'): ").strip() or "3306"
    usuario = input("Usuario: ").strip()
    
    if not usuario:
        print("❌ El usuario es obligatorio")
        return None
    
    password = getpass.getpass("Contraseña (se ocultará al escribir): ")
    
    try:
        puerto = int(puerto)
        print(f"\n🔍 Conectando a {host}:{puerto} como {usuario}...")
        
        conexion = mysql.connector.connect(
            host=host,
            port=puerto,
            user=usuario,
            password=password,
            autocommit=True
        )
        
        print("✅ Conexión exitosa!")
        return conexion
        
    except mysql.connector.Error as e:
        print(f"❌ Error de conexión: {e}")
        return None
    except ValueError:
        print("❌ El puerto debe ser un número")
        return None

def seleccionar_base_datos(conexion):
    """
    Permite al usuario seleccionar o crear una base de datos
    """
    cursor = conexion.cursor()
    
    print("\n📊 SELECCIÓN DE BASE DE DATOS")
    print("=" * 50)
    
    # Mostrar bases de datos existentes
    try:
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall() 
                    if db[0] not in ['information_schema', 'performance_schema', 'mysql', 'sys']]
        
        if databases:
            print("Bases de datos disponibles:")
            for i, db in enumerate(databases, 1):
                print(f"  {i}. {db}")
        
        print("\nOpciones:")
        print("  - Escribe el nombre de una base de datos existente")
        print("  - Escribe un nombre nuevo para crear una base de datos")
        print("  - Presiona Enter para usar 'ferretero'")
        
        db_name = input("\nBase de datos: ").strip() or "ferretero"
        
        # Verificar si existe
        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        existe = cursor.fetchone() is not None
        
        if not existe:
            respuesta = input(f"\n⚠️  La base de datos '{db_name}' no existe. ¿Crearla? (s/N): ")
            if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
                cursor.execute(f"CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"✅ Base de datos '{db_name}' creada")
            else:
                print("❌ Operación cancelada")
                return None
        
        # Seleccionar la base de datos
        cursor.execute(f"USE `{db_name}`")
        print(f"✅ Usando base de datos: {db_name}")
        return db_name
        
    except mysql.connector.Error as e:
        print(f"❌ Error al seleccionar base de datos: {e}"