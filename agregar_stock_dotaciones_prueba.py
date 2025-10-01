#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGREGAR STOCK DE PRUEBA PARA DOTACIONES

Este script agrega stock inicial para poder probar el sistema de dotaciones
con elementos VALORADO y NO VALORADO.

Autor: Sistema de Dotaciones
Fecha: 2025
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT'))
}

def agregar_stock_dotaciones():
    """Agregar stock inicial para pruebas de dotaciones"""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        print("🔄 Agregando stock inicial para dotaciones...")
        
        # Definir stock para diferentes elementos y estados
        stock_data = [
            # Pantalón - VALORADO
            ('pantalon', 'VALORADO', 'S', 10),
            ('pantalon', 'VALORADO', 'M', 15),
            ('pantalon', 'VALORADO', 'L', 12),
            ('pantalon', 'VALORADO', 'XL', 8),
            
            # Pantalón - NO VALORADO
            ('pantalon', 'NO VALORADO', 'S', 5),
            ('pantalon', 'NO VALORADO', 'M', 8),
            ('pantalon', 'NO VALORADO', 'L', 6),
            ('pantalon', 'NO VALORADO', 'XL', 4),
            
            # Camiseta Gris - VALORADO
        ('camiseta_gris', 'VALORADO', 'S', 20),
        ('camiseta_gris', 'VALORADO', 'M', 25),
        ('camiseta_gris', 'VALORADO', 'L', 18),
        ('camiseta_gris', 'VALORADO', 'XL', 12),
        
        # Camiseta Gris - NO VALORADO
        ('camiseta_gris', 'NO VALORADO', 'S', 10),
        ('camiseta_gris', 'NO VALORADO', 'M', 15),
        ('camiseta_gris', 'NO VALORADO', 'L', 12),
        ('camiseta_gris', 'NO VALORADO', 'XL', 8),
        ]
        
        # Insertar en tabla ingresos_dotaciones
        for tipo_elemento, estado, talla, cantidad in stock_data:
            cursor.execute("""
                INSERT INTO ingresos_dotaciones 
                (tipo_elemento, estado, cantidad, talla, fecha_ingreso, observaciones, usuario_registro)
                VALUES (%s, %s, %s, %s, NOW(), %s, %s)
            """, (
                tipo_elemento, 
                estado, 
                cantidad, 
                talla,
                f'Stock inicial de prueba - {estado}',
                'sistema_prueba'
            ))
            
            print(f"✅ {tipo_elemento} {estado} T{talla}: {cantidad} unidades")
        
        connection.commit()
        
        # Verificar stock total
        print("\n📊 RESUMEN DE STOCK AGREGADO:")
        cursor.execute("""
            SELECT tipo_elemento, estado, SUM(cantidad) as total
            FROM ingresos_dotaciones 
            WHERE DATE(fecha_ingreso) = CURDATE()
            GROUP BY tipo_elemento, estado
            ORDER BY tipo_elemento, estado
        """)
        
        resumen = cursor.fetchall()
        for item in resumen:
            print(f"   {item[0]} {item[1]}: {item[2]} unidades")
        
        print(f"\n✅ Stock inicial agregado exitosamente")
        print("🎯 Ahora puedes probar crear dotaciones con elementos VALORADO y NO VALORADO")
        
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Conexión cerrada")

if __name__ == "__main__":
    agregar_stock_dotaciones()