#!/usr/bin/env python3
"""
Script para agregar las columnas eventos y valor a la tabla asistencia
si no existen
"""

import mysql.connector

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def agregar_columnas_asistencia():
    """Agregar columnas eventos y valor a la tabla asistencia si no existen"""
    try:
        print("🔧 AGREGANDO COLUMNAS A TABLA ASISTENCIA")
        print("=" * 50)
        
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # 1. Verificar estructura actual
        print("📋 Estructura actual de la tabla asistencia:")
        cursor.execute("DESCRIBE asistencia")
        columnas = cursor.fetchall()
        
        columnas_existentes = [col['Field'] for col in columnas]
        tiene_eventos = 'eventos' in columnas_existentes
        tiene_valor = 'valor' in columnas_existentes
        
        print(f"  ¿Tiene columna 'eventos'? {tiene_eventos}")
        print(f"  ¿Tiene columna 'valor'? {tiene_valor}")
        
        # 2. Agregar columna eventos si no existe
        if not tiene_eventos:
            print("\n➕ Agregando columna 'eventos'...")
            cursor.execute("""
                ALTER TABLE asistencia 
                ADD COLUMN eventos INT DEFAULT 0 
                COMMENT 'Número de eventos presupuestados desde presupuesto_carpeta'
            """)
            print("✅ Columna 'eventos' agregada exitosamente")
        else:
            print("\n✅ Columna 'eventos' ya existe")
        
        # 3. Agregar columna valor si no existe
        if not tiene_valor:
            print("\n➕ Agregando columna 'valor'...")
            cursor.execute("""
                ALTER TABLE asistencia 
                ADD COLUMN valor DECIMAL(10,2) DEFAULT 0.00 
                COMMENT 'Valor presupuestado diario desde presupuesto_carpeta'
            """)
            print("✅ Columna 'valor' agregada exitosamente")
        else:
            print("\n✅ Columna 'valor' ya existe")
        
        # 4. Confirmar cambios
        connection.commit()
        
        # 5. Verificar estructura final
        print("\n📋 Estructura final de la tabla asistencia:")
        cursor.execute("DESCRIBE asistencia")
        columnas_finales = cursor.fetchall()
        
        for col in columnas_finales:
            if col['Field'] in ['eventos', 'valor']:
                print(f"  ✅ {col['Field']} ({col['Type']}) - {col['Comment']}")
        
        print("\n🎉 ¡Columnas agregadas exitosamente!")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error agregando columnas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    agregar_columnas_asistencia()