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

def setup_database():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Crear tabla de roles si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    id_roles INT AUTO_INCREMENT PRIMARY KEY,
                    nombre_rol VARCHAR(50) NOT NULL
                )
            """)
            
            # Crear tabla de recursos operativos si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recurso_operativo (
                    id_codigo_consumidor INT AUTO_INCREMENT PRIMARY KEY,
                    recurso_operativo_cedula VARCHAR(20) UNIQUE NOT NULL,
                    recurso_operativo_password VARCHAR(255) NOT NULL,
                    id_roles INT,
                    estado VARCHAR(20) DEFAULT 'Activo',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_roles) REFERENCES roles(id_roles)
                )
            """)
            
            # Crear tabla de registro de actividad si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    action VARCHAR(50) NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES recurso_operativo(id_codigo_consumidor)
                )
            """)
            
            # Crear tabla preoperacional si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preoperacional (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    centro_de_trabajo VARCHAR(255),
                    ciudad VARCHAR(255),
                    supervisor VARCHAR(255),
                    vehiculo_asistio_operacion VARCHAR(255),
                    tipo_vehiculo VARCHAR(255),
                    placa_vehiculo VARCHAR(255),
                    modelo_vehiculo VARCHAR(255),
                    marca_vehiculo VARCHAR(255),
                    licencia_conduccion VARCHAR(255),
                    fecha_vencimiento_licencia DATE,
                    fecha_vencimiento_soat DATE,
                    fecha_vencimiento_tecnomecanica DATE,
                    estado_espejos VARCHAR(255),
                    bocina_pito VARCHAR(255),
                    frenos VARCHAR(255),
                    encendido VARCHAR(255),
                    estado_bateria VARCHAR(255),
                    estado_amortiguadores VARCHAR(255),
                    estado_llantas VARCHAR(255),
                    kilometraje_actual INT,
                    luces_altas_bajas VARCHAR(255),
                    direccionales_delanteras_traseras VARCHAR(255),
                    elementos_prevencion_seguridad_vial_casco VARCHAR(255),
                    casco_certificado VARCHAR(255),
                    casco_identificado VARCHAR(255),
                    estado_guantes VARCHAR(255),
                    estado_rodilleras VARCHAR(255),
                    impermeable VARCHAR(255),
                    observaciones TEXT,
                    estado_fisico_vehiculo_espejos VARCHAR(255),
                    estado_fisico_vehiculo_bocina_pito VARCHAR(255),
                    estado_fisico_vehiculo_frenos VARCHAR(255),
                    estado_fisico_vehiculo_encendido VARCHAR(255),
                    estado_fisico_vehiculo_bateria VARCHAR(255),
                    estado_fisico_vehiculo_amortiguadores VARCHAR(255),
                    estado_fisico_vehiculo_llantas VARCHAR(255),
                    estado_fisico_vehiculo_luces_altas VARCHAR(255),
                    estado_fisico_vehiculo_luces_bajas VARCHAR(255),
                    estado_fisico_vehiculo_direccionales_delanteras VARCHAR(255),
                    estado_fisico_vehiculo_direccionales_traseras VARCHAR(255),
                    elementos_prevencion_seguridad_vial_guantes VARCHAR(255),
                    elementos_prevencion_seguridad_vial_rodilleras VARCHAR(255),
                    elementos_prevencion_seguridad_vial_coderas VARCHAR(255),
                    elementos_prevencion_seguridad_vial_impermeable VARCHAR(255),
                    casco_identificado_placa VARCHAR(255)
                )
            """)
            
            # Insertar roles por defecto si no existen
            roles = {
                1: 'administrativo',
                2: 'tecnicos',
                3: 'operativo',
                4: 'contabilidad',
                5: 'logistica'
            }
            
            for role_id, role_name in roles.items():
                cursor.execute("""
                    INSERT IGNORE INTO roles (id_roles, nombre_rol)
                    VALUES (%s, %s)
                """, (role_id, role_name))
            
            # Agregar nuevos campos a recurso_operativo si no existen
            try:
                cursor.execute("ALTER TABLE recurso_operativo ADD COLUMN IF NOT EXISTS estado VARCHAR(20) DEFAULT 'Activo'")
            except Error:
                print("Campo 'estado' ya existe")
                
            try:
                cursor.execute("ALTER TABLE recurso_operativo ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            except Error:
                print("Campo 'created_at' ya existe")
                
            try:
                cursor.execute("ALTER TABLE recurso_operativo ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
            except Error:
                print("Campo 'updated_at' ya existe")
            
            connection.commit()
            print("Base de datos configurada exitosamente")
            
    except Error as e:
        print(f"Error: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión cerrada")

if __name__ == "__main__":
    setup_database()