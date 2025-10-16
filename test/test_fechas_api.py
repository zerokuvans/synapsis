#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar directamente la API de fechas de usuarios
"""

import mysql.connector
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'capired'),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def simular_api_obtener_usuario(id_usuario):
    """Simular exactamente lo que hace la API obtener_usuario"""
    print(f"🔍 SIMULANDO API /obtener_usuario/{id_usuario}")
    print("="*50)
    
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if connection is None:
            return {'error': 'Error de conexión a la base de datos'}
        
        cursor = connection.cursor(dictionary=True)
        
        # Ejecutar la misma consulta que usa la API
        cursor.execute("""
            SELECT 
                id_codigo_consumidor,
                recurso_operativo_cedula,
                nombre,
                id_roles,
                estado,
                cargo,
                carpeta,
                cliente,
                ciudad,
                super,
                analista,
                fecha_ingreso,
                fecha_retiro
            FROM recurso_operativo 
            WHERE id_codigo_consumidor = %s
        """, (id_usuario,))
        
        usuario = cursor.fetchone()
        
        if not usuario:
            return {'error': 'Usuario no encontrado'}
        
        print("✅ Datos obtenidos de la base de datos:")
        print(f"   fecha_ingreso: {usuario['fecha_ingreso']} (tipo: {type(usuario['fecha_ingreso'])})")
        print(f"   fecha_retiro: {usuario['fecha_retiro']} (tipo: {type(usuario['fecha_retiro'])})")
        
        # Convertir fechas datetime a string como lo haría JSON
        if isinstance(usuario['fecha_ingreso'], datetime):
            usuario['fecha_ingreso'] = usuario['fecha_ingreso'].strftime('%Y-%m-%d')
        
        if isinstance(usuario['fecha_retiro'], datetime):
            usuario['fecha_retiro'] = usuario['fecha_retiro'].strftime('%Y-%m-%d')
        
        print("\n📤 Respuesta JSON que se enviaría al frontend:")
        print(json.dumps(usuario, indent=2, default=str))
        
        return usuario
        
    except mysql.connector.Error as e:
        return {'error': str(e)}
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def probar_actualizacion_fecha(id_usuario, nueva_fecha_ingreso):
    """Probar actualización de fecha"""
    print(f"\n🔄 PROBANDO ACTUALIZACIÓN DE FECHA")
    print("="*50)
    
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if connection is None:
            print("❌ Error de conexión")
            return False
        
        cursor = connection.cursor()
        
        # Actualizar fecha
        cursor.execute("""
            UPDATE recurso_operativo 
            SET fecha_ingreso = %s 
            WHERE id_codigo_consumidor = %s
        """, (nueva_fecha_ingreso, id_usuario))
        
        connection.commit()
        
        print(f"✅ Fecha actualizada a: {nueva_fecha_ingreso}")
        print(f"   Filas afectadas: {cursor.rowcount}")
        
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error al actualizar: {e}")
        return False
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def main():
    print("🧪 PRUEBA COMPLETA DE FECHAS DE USUARIOS")
    print("="*60)
    
    # ID del usuario que sabemos que existe
    id_usuario = 1
    
    # 1. Probar obtener usuario (estado actual)
    print("1️⃣ ESTADO ACTUAL:")
    resultado = simular_api_obtener_usuario(id_usuario)
    
    if 'error' in resultado:
        print(f"❌ Error: {resultado['error']}")
        return
    
    fecha_original = resultado.get('fecha_ingreso', '')
    
    # 2. Actualizar a una nueva fecha
    nueva_fecha = "2024-10-16"
    print(f"\n2️⃣ ACTUALIZANDO FECHA A: {nueva_fecha}")
    if probar_actualizacion_fecha(id_usuario, nueva_fecha):
        
        # 3. Verificar que la actualización funcionó
        print(f"\n3️⃣ VERIFICANDO ACTUALIZACIÓN:")
        resultado_actualizado = simular_api_obtener_usuario(id_usuario)
        
        if 'error' not in resultado_actualizado:
            fecha_nueva = resultado_actualizado.get('fecha_ingreso', '')
            if fecha_nueva == nueva_fecha:
                print(f"✅ ¡ÉXITO! La fecha se actualizó correctamente: {fecha_nueva}")
            else:
                print(f"❌ ERROR: Fecha esperada {nueva_fecha}, pero se obtuvo {fecha_nueva}")
        
        # 4. Restaurar fecha original si existía
        if fecha_original:
            print(f"\n4️⃣ RESTAURANDO FECHA ORIGINAL: {fecha_original}")
            probar_actualizacion_fecha(id_usuario, fecha_original)
            
            # Verificar restauración
            resultado_restaurado = simular_api_obtener_usuario(id_usuario)
            if 'error' not in resultado_restaurado:
                fecha_restaurada = resultado_restaurado.get('fecha_ingreso', '')
                if fecha_restaurada == fecha_original:
                    print(f"✅ Fecha original restaurada correctamente: {fecha_restaurada}")
                else:
                    print(f"⚠️  Fecha restaurada: {fecha_restaurada} (original: {fecha_original})")
    
    print(f"\n🏁 PRUEBA COMPLETADA")
    print("="*60)
    
    # Conclusiones
    print("\n📋 CONCLUSIONES:")
    print("1. Si las fechas se actualizan y leen correctamente aquí,")
    print("   el problema está en el frontend (JavaScript/HTML)")
    print("2. Si hay errores aquí, el problema está en el backend")
    print("3. Verificar los logs de la consola del navegador para más detalles")

if __name__ == "__main__":
    main()