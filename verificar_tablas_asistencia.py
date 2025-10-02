#!/usr/bin/env python3
import mysql.connector

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'synapsis'
}

def verificar_tablas_asistencia():
    """Verificar qué tablas relacionadas con asistencia existen"""
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        print("🔍 VERIFICANDO TABLAS DE ASISTENCIA")
        print("=" * 50)
        
        # 1. Mostrar todas las tablas
        cursor.execute("SHOW TABLES")
        tablas = cursor.fetchall()
        
        print("📋 Todas las tablas en la base de datos:")
        tablas_relacionadas = []
        for tabla in tablas:
            nombre_tabla = list(tabla.values())[0]
            print(f"  - {nombre_tabla}")
            if 'asist' in nombre_tabla.lower() or 'attendance' in nombre_tabla.lower():
                tablas_relacionadas.append(nombre_tabla)
        
        print(f"\n🎯 Tablas relacionadas con asistencia encontradas: {len(tablas_relacionadas)}")
        for tabla in tablas_relacionadas:
            print(f"  ✅ {tabla}")
        
        # 2. Buscar tablas que contengan datos de técnicos con fechas
        print(f"\n🔍 Buscando tablas con datos de técnicos y fechas...")
        
        for tabla in tablas:
            nombre_tabla = list(tabla.values())[0]
            try:
                # Verificar estructura de la tabla
                cursor.execute(f"DESCRIBE {nombre_tabla}")
                columnas = cursor.fetchall()
                
                # Buscar columnas relacionadas con asistencia
                columnas_relevantes = []
                for col in columnas:
                    nombre_col = col['Field'].lower()
                    if any(keyword in nombre_col for keyword in ['cedula', 'fecha', 'hora', 'estado', 'novedad', 'tecnico', 'asist']):
                        columnas_relevantes.append(col['Field'])
                
                if len(columnas_relevantes) >= 3:  # Si tiene al menos 3 columnas relevantes
                    print(f"\n📊 Tabla potencial: {nombre_tabla}")
                    print(f"   Columnas relevantes: {', '.join(columnas_relevantes)}")
                    
                    # Verificar si tiene datos
                    cursor.execute(f"SELECT COUNT(*) as total FROM {nombre_tabla}")
                    total = cursor.fetchone()['total']
                    print(f"   Total registros: {total}")
                    
                    if total > 0:
                        # Mostrar algunos registros de ejemplo
                        cursor.execute(f"SELECT * FROM {nombre_tabla} LIMIT 3")
                        ejemplos = cursor.fetchall()
                        print(f"   Ejemplos de datos:")
                        for i, ejemplo in enumerate(ejemplos, 1):
                            print(f"     {i}. {ejemplo}")
            
            except Exception as e:
                # Ignorar errores de tablas que no se pueden consultar
                pass
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error durante verificación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_tablas_asistencia()