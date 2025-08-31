#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la estructura real de la tabla usuarios
"""

import mysql.connector
from datetime import datetime

def verificar_estructura_usuarios():
    """Verificar la estructura real de la tabla usuarios"""
    
    print("=== VERIFICACIÓN DE ESTRUCTURA DE USUARIOS ===")
    print(f"Fecha de verificación: {datetime.now()}")
    print()
    
    try:
        # Configuración de la base de datos
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '732137A031E4b@',
            'database': 'capired'
        }
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Verificar si existe la tabla usuarios
        cursor.execute("SHOW TABLES LIKE 'usuarios'")
        tabla_usuarios = cursor.fetchone()
        
        if tabla_usuarios:
            print("✅ Tabla 'usuarios' encontrada")
            
            # Obtener estructura de la tabla usuarios
            cursor.execute("DESCRIBE usuarios")
            estructura = cursor.fetchall()
            
            print("\n=== ESTRUCTURA DE LA TABLA USUARIOS ===")
            for campo in estructura:
                print(f"- {campo['Field']}: {campo['Type']} {'(NULL)' if campo['Null'] == 'YES' else '(NOT NULL)'} {campo.get('Extra', '')}")
            
            # Contar total de usuarios
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            total_usuarios = cursor.fetchone()['total']
            print(f"\n📊 Total de usuarios: {total_usuarios}")
            
            if total_usuarios > 0:
                # Obtener algunos registros de ejemplo para ver la estructura real
                cursor.execute("SELECT * FROM usuarios LIMIT 5")
                usuarios_ejemplo = cursor.fetchall()
                
                print("\n=== PRIMEROS 5 USUARIOS (EJEMPLO) ===")
                for i, usuario in enumerate(usuarios_ejemplo):
                    print(f"\nUsuario {i+1}:")
                    for campo, valor in usuario.items():
                        # Ocultar contraseñas por seguridad
                        if 'password' in campo.lower() or 'clave' in campo.lower():
                            valor = "[OCULTO]"
                        print(f"  {campo}: {valor}")
                
                # Buscar campos que puedan ser el username
                campos_posibles = []
                for campo in estructura:
                    nombre_campo = campo['Field'].lower()
                    if any(palabra in nombre_campo for palabra in ['user', 'usuario', 'login', 'nombre', 'cedula', 'documento']):
                        campos_posibles.append(campo['Field'])
                
                print(f"\n=== CAMPOS POSIBLES PARA USERNAME ===")
                for campo in campos_posibles:
                    print(f"- {campo}")
                
                # Buscar campos que puedan ser el rol
                campos_rol = []
                for campo in estructura:
                    nombre_campo = campo['Field'].lower()
                    if any(palabra in nombre_campo for palabra in ['rol', 'role', 'tipo', 'perfil', 'nivel']):
                        campos_rol.append(campo['Field'])
                
                print(f"\n=== CAMPOS POSIBLES PARA ROL ===")
                for campo in campos_rol:
                    print(f"- {campo}")
                    
                    # Mostrar valores únicos de este campo
                    try:
                        cursor.execute(f"SELECT DISTINCT {campo} FROM usuarios WHERE {campo} IS NOT NULL LIMIT 10")
                        valores = cursor.fetchall()
                        valores_lista = [str(list(v.values())[0]) for v in valores]
                        print(f"  Valores: {', '.join(valores_lista)}")
                    except Exception as e:
                        print(f"  Error al obtener valores: {e}")
            
        else:
            print("❌ Tabla 'usuarios' no encontrada")
            
            # Buscar otras tablas que puedan contener usuarios
            cursor.execute("SHOW TABLES")
            tablas = cursor.fetchall()
            
            print("\n=== TODAS LAS TABLAS DISPONIBLES ===")
            tablas_usuario = []
            for tabla in tablas:
                nombre_tabla = list(tabla.values())[0]
                print(f"- {nombre_tabla}")
                if any(palabra in nombre_tabla.lower() for palabra in ['user', 'usuario', 'login', 'auth', 'admin']):
                    tablas_usuario.append(nombre_tabla)
            
            if tablas_usuario:
                print(f"\n=== TABLAS RELACIONADAS CON USUARIOS ===")
                for tabla in tablas_usuario:
                    print(f"\n--- Estructura de {tabla} ---")
                    try:
                        cursor.execute(f"DESCRIBE {tabla}")
                        estructura = cursor.fetchall()
                        for campo in estructura:
                            print(f"  - {campo['Field']}: {campo['Type']}")
                        
                        # Contar registros
                        cursor.execute(f"SELECT COUNT(*) as total FROM {tabla}")
                        total = cursor.fetchone()['total']
                        print(f"  Total de registros: {total}")
                        
                    except Exception as e:
                        print(f"  Error al acceder a {tabla}: {e}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error al verificar estructura: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_estructura_usuarios()