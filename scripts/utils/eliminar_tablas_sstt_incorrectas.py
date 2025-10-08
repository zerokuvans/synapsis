#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para eliminar las tablas incorrectas de SSTT (Soporte Técnico)
y limpiar la base de datos antes de crear las correctas para Seguridad y Salud en el Trabajo
"""

import mysql.connector
from datetime import datetime

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def eliminar_tablas_sstt_incorrectas():
    """Elimina las tablas incorrectas de SSTT (Soporte Técnico)"""
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=== ELIMINANDO TABLAS INCORRECTAS DE SSTT ===")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Lista de tablas incorrectas a eliminar
        tablas_incorrectas = [
            'sstt_escalamientos',
            'sstt_comentarios',
            'sstt_tickets',
            'sstt_equipos_soporte',
            'sstt_base_conocimiento',
            'sstt_prioridades',
            'sstt_categorias'
        ]
        
        # Verificar qué tablas existen
        cursor.execute("SHOW TABLES LIKE 'sstt_%'")
        tablas_existentes = [tabla[0] for tabla in cursor.fetchall()]
        
        if not tablas_existentes:
            print("✅ No se encontraron tablas SSTT para eliminar")
            return
        
        print(f"📋 Tablas SSTT encontradas: {len(tablas_existentes)}")
        for tabla in tablas_existentes:
            print(f"   - {tabla}")
        print()
        
        # Eliminar tablas en orden (considerando dependencias)
        tablas_eliminadas = 0
        for tabla in tablas_incorrectas:
            if tabla in tablas_existentes:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {tabla}")
                    print(f"🗑️  Tabla '{tabla}' eliminada")
                    tablas_eliminadas += 1
                except mysql.connector.Error as e:
                    print(f"❌ Error eliminando tabla '{tabla}': {e}")
        
        conn.commit()
        
        # Verificar eliminación
        cursor.execute("SHOW TABLES LIKE 'sstt_%'")
        tablas_restantes = cursor.fetchall()
        
        print(f"\n📊 Resumen:")
        print(f"   - Tablas eliminadas: {tablas_eliminadas}")
        print(f"   - Tablas restantes: {len(tablas_restantes)}")
        
        if tablas_restantes:
            print("   - Tablas que aún existen:")
            for tabla in tablas_restantes:
                print(f"     * {tabla[0]}")
        
        # También eliminar el rol incorrecto si existe
        cursor.execute("SELECT id FROM roles WHERE nombre = 'sstt' AND descripcion LIKE '%Soporte Técnico%'")
        rol_incorrecto = cursor.fetchone()
        
        if rol_incorrecto:
            cursor.execute("DELETE FROM roles WHERE id = %s", (rol_incorrecto[0],))
            conn.commit()
            print(f"\n🗑️  Rol SSTT incorrecto eliminado (ID: {rol_incorrecto[0]})")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 ¡Limpieza completada exitosamente!")
        print("    Ahora se puede proceder a crear las tablas correctas para")
        print("    Seguridad y Salud en el Trabajo")
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    eliminar_tablas_sstt_incorrectas()