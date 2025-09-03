#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la estructura actual de la tabla parque_automotor
y generar la lista de campos válidos para el endpoint de actualización
"""

import mysql.connector
from mysql.connector import Error

# Configuración de conexión
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def verificar_estructura_tabla():
    """Verifica la estructura actual de la tabla parque_automotor"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(buffered=True)
        
        print("🔍 VERIFICANDO ESTRUCTURA DE TABLA PARQUE_AUTOMOTOR")
        print("="*60)
        
        # Obtener estructura de la tabla
        cursor.execute("DESCRIBE parque_automotor")
        campos = cursor.fetchall()
        
        print(f"📊 Total de campos encontrados: {len(campos)}")
        print("\n📋 Estructura de la tabla:")
        
        campos_validos = []
        for campo in campos:
            field, type_info, null, key, default, extra = campo
            campos_validos.append(field)
            key_info = f" ({key})" if key else ""
            null_info = "NULL" if null == 'YES' else "NOT NULL"
            print(f"  ✅ {field:<30} {type_info:<20} {null_info}{key_info}")
        
        # Campos que el endpoint actual intenta actualizar
        campos_endpoint = [
            'placa', 'tipo_vehiculo', 'marca', 'modelo', 'color', 'supervisor',
            'id_codigo_consumidor', 'fecha_asignacion', 'estado', 'soat_vencimiento',
            'tecnomecanica_vencimiento', 'observaciones', 'vin', 'parque_automotorcol',
            'licencia', 'cedula_propietario', 'nombre_propietario', 'kilometraje_actual',
            'proximo_mantenimiento_km', 'fecha_ultimo_mantenimiento', 'proximo_mantenimiento',
            'ultimo_mantenimiento', 'fecha_actualizacion', 'numero_vin', 'propietario_cedula',
            'propietario_nombre', 'estado_carroceria', 'estado_llantas', 'estado_frenos',
            'estado_motor', 'estado_luces', 'estado_espejos', 'estado_vidrios',
            'estado_asientos', 'cinturon_seguridad', 'extintor', 'botiquin',
            'triangulos_seguridad', 'llanta_repuesto', 'herramientas', 'gato',
            'cruceta', 'centro_de_trabajo', 'ciudad', 'fecha', 'kilometraje',
            'licencia_conduccion', 'fecha_vencimiento_licencia'
        ]
        
        print("\n🔍 ANÁLISIS DE CAMPOS DEL ENDPOINT:")
        print("="*60)
        
        campos_validos_endpoint = []
        campos_invalidos = []
        
        for campo in campos_endpoint:
            if campo in campos_validos:
                campos_validos_endpoint.append(campo)
                print(f"  ✅ {campo:<30} - VÁLIDO")
            else:
                campos_invalidos.append(campo)
                print(f"  ❌ {campo:<30} - NO EXISTE")
        
        print(f"\n📈 RESUMEN:")
        print(f"  ✅ Campos válidos: {len(campos_validos_endpoint)}/{len(campos_endpoint)}")
        print(f"  ❌ Campos inválidos: {len(campos_invalidos)}")
        
        if campos_invalidos:
            print(f"\n❌ CAMPOS QUE CAUSAN ERROR:")
            for campo in campos_invalidos:
                print(f"  - {campo}")
        
        print(f"\n✅ CAMPOS VÁLIDOS PARA EL ENDPOINT:")
        print("campos_validos = [")
        for i, campo in enumerate(campos_validos_endpoint):
            coma = "," if i < len(campos_validos_endpoint) - 1 else ""
            print(f"    '{campo}'{coma}")
        print("]")
        
        cursor.close()
        connection.close()
        
        return campos_validos_endpoint, campos_invalidos
        
    except Error as e:
        print(f"❌ Error de base de datos: {e}")
        return [], []
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return [], []

if __name__ == "__main__":
    verificar_estructura_tabla()