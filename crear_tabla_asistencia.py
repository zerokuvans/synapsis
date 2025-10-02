#!/usr/bin/env python3
import mysql.connector

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def crear_tabla_asistencia():
    """Crear la tabla asistencia con la estructura completa"""
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("🔧 CREANDO TABLA ASISTENCIA")
        print("=" * 40)
        
        # 1. Crear tabla tipificacion_asistencia si no existe
        print("1. Creando tabla tipificacion_asistencia...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tipificacion_asistencia (
                id_tipificacion INT AUTO_INCREMENT PRIMARY KEY,
                codigo_tipificacion VARCHAR(50) NOT NULL UNIQUE,
                nombre_tipificacion VARCHAR(200),
                grupo VARCHAR(100),
                estado CHAR(1) DEFAULT '1',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Crear tabla presupuesto_carpeta si no existe
        print("2. Creando tabla presupuesto_carpeta...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS presupuesto_carpeta (
                id_presupuesto INT AUTO_INCREMENT PRIMARY KEY,
                presupuesto_carpeta VARCHAR(100) NOT NULL,
                presupuesto_eventos DECIMAL(10,2),
                presupuesto_diario DECIMAL(10,2),
                estado CHAR(1) DEFAULT '1',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Crear tabla asistencia con estructura completa
        print("3. Creando tabla asistencia...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asistencia (
                id_asistencia INT AUTO_INCREMENT PRIMARY KEY,
                cedula VARCHAR(45) NOT NULL,
                tecnico VARCHAR(45) NOT NULL,
                carpeta_dia VARCHAR(45) NOT NULL,
                carpeta VARCHAR(45) NOT NULL,
                super VARCHAR(45) NOT NULL,
                fecha_asistencia DATETIME NOT NULL,
                id_codigo_consumidor INT,
                hora_inicio TIME NOT NULL,
                estado VARCHAR(45) NOT NULL,
                novedad VARCHAR(45) NOT NULL,
                INDEX idx_cedula (cedula),
                INDEX idx_fecha (fecha_asistencia),
                INDEX idx_cedula_fecha (cedula, fecha_asistencia)
            )
        """)
        
        connection.commit()
        print("✅ Tablas creadas exitosamente")
        
        # 4. Insertar datos de ejemplo para las analistas
        print("\n4. Insertando datos de ejemplo...")
        
        # Insertar tipificaciones de ejemplo
        tipificaciones = [
            ('CARP001', 'Carpeta Operativa 1', 'OPERATIVO'),
            ('CARP002', 'Carpeta Operativa 2', 'OPERATIVO'),
            ('CARP003', 'Carpeta Administrativa', 'ADMINISTRATIVO')
        ]
        
        for codigo, nombre, grupo in tipificaciones:
            cursor.execute("""
                INSERT IGNORE INTO tipificacion_asistencia 
                (codigo_tipificacion, nombre_tipificacion, grupo) 
                VALUES (%s, %s, %s)
            """, (codigo, nombre, grupo))
        
        # Insertar presupuestos de ejemplo
        presupuestos = [
            ('Carpeta Operativa 1', 1000.00, 50.00),
            ('Carpeta Operativa 2', 1500.00, 75.00),
            ('Carpeta Administrativa', 800.00, 40.00)
        ]
        
        for nombre, eventos, diario in presupuestos:
            cursor.execute("""
                INSERT IGNORE INTO presupuesto_carpeta 
                (presupuesto_carpeta, presupuesto_eventos, presupuesto_diario) 
                VALUES (%s, %s, %s)
            """, (nombre, eventos, diario))
        
        # Insertar datos de asistencia de ejemplo para técnicos de ESPITIA
        tecnicos_espitia = [
            ('1085176966', 'ARNACHE ARIAS JUAN CARLOS'),
            ('1022359872', 'BERNAL MORALES LUIS NELSON'),
            ('1033758324', 'DIAZ MORA FABIO NELSON'),
            ('1020809768', 'PADILLA MORALES LUIS ALFONSO'),
            ('1019093439', 'SANCHEZ PEA JUAN GABRIEL'),
            ('80034211', 'VELANDIA REDONDO DIEGO ALEXANDER')
        ]
        
        asistencias_ejemplo = [
            ('1085176966', 'ARNACHE ARIAS JUAN CARLOS', 'CARP001', 'CARP001', 'ESPITIA BARON LICED JOANA', '2025-10-02 08:30:00', 1, '08:30:00', 'CUMPLE', ''),
            ('1022359872', 'BERNAL MORALES LUIS NELSON', 'CARP002', 'CARP002', 'ESPITIA BARON LICED JOANA', '2025-10-02 09:15:00', 2, '09:15:00', 'NOVEDAD', 'Llegó tarde por tráfico'),
            ('1033758324', 'DIAZ MORA FABIO NELSON', 'CARP001', 'CARP001', 'ESPITIA BARON LICED JOANA', '2025-10-02 08:00:00', 3, '08:00:00', 'NO CUMPLE', ''),
            ('1020809768', 'PADILLA MORALES LUIS ALFONSO', 'CARP003', 'CARP003', 'ESPITIA BARON LICED JOANA', '2025-10-02 00:00:00', 4, '00:00:00', '', ''),
            ('1019093439', 'SANCHEZ PEA JUAN GABRIEL', 'CARP002', 'CARP002', 'ESPITIA BARON LICED JOANA', '2025-10-02 00:00:00', 5, '00:00:00', '', ''),
            ('80034211', 'VELANDIA REDONDO DIEGO ALEXANDER', 'CARP001', 'CARP001', 'ESPITIA BARON LICED JOANA', '2025-10-02 00:00:00', 6, '00:00:00', '', '')
        ]
        
        for asistencia in asistencias_ejemplo:
            cursor.execute("""
                INSERT IGNORE INTO asistencia 
                (cedula, tecnico, carpeta_dia, carpeta, super, fecha_asistencia, 
                 id_codigo_consumidor, hora_inicio, estado, novedad) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, asistencia)
        
        connection.commit()
        print("✅ Datos de ejemplo insertados")
        
        # 5. Verificar que todo se creó correctamente
        print("\n5. Verificando estructura creada...")
        
        cursor.execute("DESCRIBE asistencia")
        columnas = cursor.fetchall()
        print("📋 Estructura de la tabla asistencia:")
        for col in columnas:
            print(f"  - {col[0]} ({col[1]})")
        
        cursor.execute("SELECT COUNT(*) FROM asistencia")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total de registros en asistencia: {total}")
        
        if total > 0:
            cursor.execute("SELECT * FROM asistencia LIMIT 3")
            ejemplos = cursor.fetchall()
            print("📝 Ejemplos de registros:")
            for i, ejemplo in enumerate(ejemplos, 1):
                print(f"  {i}. Cédula: {ejemplo[1]}, Técnico: {ejemplo[2]}, Fecha: {ejemplo[6]}, Hora: {ejemplo[8]}, Estado: {ejemplo[9]}")
        
        cursor.close()
        connection.close()
        
        print("\n🎉 ¡Tabla asistencia creada y configurada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante creación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    crear_tabla_asistencia()