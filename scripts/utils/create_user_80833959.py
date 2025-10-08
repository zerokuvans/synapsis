#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import hashlib
import sys

def create_user():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='732137A031E4b@',
            database='capired',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = connection.cursor()
        
        # Verificar si el usuario ya existe
        cursor.execute("""
            SELECT id_codigo_consumidor 
            FROM recurso_operativo 
            WHERE recurso_operativo_cedula = %s
        """, ('80833959',))
        
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("✅ El usuario 80833959 ya existe")
            return True
        
        # Crear hash de la contraseña usando bcrypt (como en los registros existentes)
        import bcrypt
        password = 'M4r14l4r@'
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Obtener el próximo ID disponible
        cursor.execute("SELECT MAX(id_codigo_consumidor) as max_id FROM recurso_operativo")
        result = cursor.fetchone()
        next_id = (result['max_id'] or 0) + 1
        
        # Insertar el nuevo usuario
        cursor.execute("""
            INSERT INTO recurso_operativo (
                id_codigo_consumidor,
                recurso_operativo_cedula,
                recurso_operativo_password,
                id_roles,
                estado,
                nombre,
                cargo,
                carpeta,
                cliente,
                ciudad,
                fecha_creacion
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            next_id,
            '80833959',
            password_hash,
            2,  # Rol de técnico
            'Activo',
            'USUARIO PRUEBA FERRETERO',
            'TECNICO',
            'FTTH INSTALACIONES',
            'DICO',
            'BOGOTA'
        ))
        
        connection.commit()
        
        print("✅ Usuario 80833959 creado exitosamente")
        print(f"   ID: 80833959")
        print(f"   Nombre: USUARIO PRUEBA FERRETERO")
        print(f"   Cargo: TECNICO")
        print(f"   Carpeta: FTTH INSTALACIONES")
        print(f"   Contraseña: {password}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al crear el usuario: {e}")
        return False

if __name__ == "__main__":
    create_user()