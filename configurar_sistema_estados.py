import mysql.connector

# Conectar a la base de datos
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='732137A031E4b@',
    database='capired'
)

cursor = connection.cursor()

print('=== CONFIGURACIÓN DEL SISTEMA DE GESTIÓN DE ESTADOS ===\n')

# 1. Crear tabla de permisos de transición
print('1. Creando tabla permisos_transicion...')
cursor.execute("""
CREATE TABLE IF NOT EXISTS permisos_transicion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rol_id INT NOT NULL,
    estado_origen ENUM('REGISTRADA','EN_REVISION','APROBADA','RECHAZADA','COMPLETADA') NOT NULL,
    estado_destino ENUM('REGISTRADA','EN_REVISION','APROBADA','RECHAZADA','COMPLETADA') NOT NULL,
    permitido BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rol_id) REFERENCES roles(id_roles),
    UNIQUE KEY unique_transicion (rol_id, estado_origen, estado_destino)
)
""")
print('✓ Tabla permisos_transicion creada')

# 2. Crear tabla de auditoría de estados
print('2. Creando tabla auditoria_estados...')
cursor.execute("""
CREATE TABLE IF NOT EXISTS auditoria_estados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    devolucion_id INT NOT NULL,
    estado_anterior ENUM('REGISTRADA','EN_REVISION','APROBADA','RECHAZADA','COMPLETADA') NOT NULL,
    estado_nuevo ENUM('REGISTRADA','EN_REVISION','APROBADA','RECHAZADA','COMPLETADA') NOT NULL,
    usuario_id INT NOT NULL,
    motivo_cambio TEXT,
    fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (devolucion_id) REFERENCES devoluciones_dotacion(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(idusuarios)
)
""")
print('✓ Tabla auditoria_estados creada')

# 3. Crear tabla de configuración de notificaciones
print('3. Creando tabla configuracion_notificaciones...')
cursor.execute("""
CREATE TABLE IF NOT EXISTS configuracion_notificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evento_trigger VARCHAR(50) NOT NULL,
    estado_origen ENUM('REGISTRADA','EN_REVISION','APROBADA','RECHAZADA','COMPLETADA'),
    estado_destino ENUM('REGISTRADA','EN_REVISION','APROBADA','RECHAZADA','COMPLETADA') NOT NULL,
    destinatarios_roles JSON NOT NULL,
    plantilla_email_id INT,
    plantilla_sms_id INT,
    activo BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (plantilla_email_id) REFERENCES plantillas_email(id),
    FOREIGN KEY (plantilla_sms_id) REFERENCES plantillas_sms(id)
)
""")
print('✓ Tabla configuracion_notificaciones creada')

# 4. Insertar permisos básicos de transición
print('4. Configurando permisos de transición...')

# Permisos para rol administrativo (id_roles = 1)
permisos_admin = [
    (1, 'REGISTRADA', 'EN_REVISION', True),
    (1, 'REGISTRADA', 'RECHAZADA', True),
    (1, 'EN_REVISION', 'APROBADA', True),
    (1, 'EN_REVISION', 'RECHAZADA', True),
    (1, 'APROBADA', 'COMPLETADA', True),
    (1, 'APROBADA', 'RECHAZADA', True),
    (1, 'RECHAZADA', 'REGISTRADA', True),
]

# Permisos para rol técnicos (id_roles = 2)
permisos_tecnicos = [
    (2, 'REGISTRADA', 'EN_REVISION', True),
    (2, 'EN_REVISION', 'APROBADA', True),
    (2, 'EN_REVISION', 'RECHAZADA', True),
    (2, 'APROBADA', 'COMPLETADA', True),
]

# Permisos para rol logística (id_roles = 5)
permisos_logistica = [
    (5, 'REGISTRADA', 'EN_REVISION', True),
    (5, 'EN_REVISION', 'APROBADA', True),
    (5, 'EN_REVISION', 'RECHAZADA', True),
    (5, 'APROBADA', 'COMPLETADA', True),
    (5, 'APROBADA', 'RECHAZADA', True),
]

todos_permisos = permisos_admin + permisos_tecnicos + permisos_logistica

for permiso in todos_permisos:
    cursor.execute("""
        INSERT IGNORE INTO permisos_transicion 
        (rol_id, estado_origen, estado_destino, permitido) 
        VALUES (%s, %s, %s, %s)
    """, permiso)

print(f'✓ {len(todos_permisos)} permisos de transición configurados')

# 5. Configurar notificaciones básicas
print('5. Configurando notificaciones automáticas...')

notificaciones = [
    ('CAMBIO_ESTADO', None, 'EN_REVISION', '["administrativo", "tecnicos", "logistica"]'),
    ('CAMBIO_ESTADO', None, 'APROBADA', '["administrativo", "tecnicos"]'),
    ('CAMBIO_ESTADO', None, 'RECHAZADA', '["administrativo", "tecnicos"]'),
    ('CAMBIO_ESTADO', None, 'COMPLETADA', '["administrativo", "tecnicos", "logistica"]'),
]

for notif in notificaciones:
    cursor.execute("""
        INSERT IGNORE INTO configuracion_notificaciones 
        (evento_trigger, estado_origen, estado_destino, destinatarios_roles, activo) 
        VALUES (%s, %s, %s, %s, TRUE)
    """, notif)

print(f'✓ {len(notificaciones)} configuraciones de notificación creadas')

# Confirmar cambios
connection.commit()

# 6. Verificar configuración
print('\n=== VERIFICACIÓN DE CONFIGURACIÓN ===')

cursor.execute('SELECT COUNT(*) as total FROM permisos_transicion')
total_permisos = cursor.fetchone()[0]
print(f'✓ Permisos de transición configurados: {total_permisos}')

cursor.execute('SELECT COUNT(*) as total FROM configuracion_notificaciones WHERE activo = TRUE')
total_notif = cursor.fetchone()[0]
print(f'✓ Configuraciones de notificación activas: {total_notif}')

print('\n=== CONFIGURACIÓN COMPLETADA ===')
print('El sistema de gestión de estados está listo para usar.')
print('\nFuncionalidades disponibles:')
print('- ✓ Control de permisos por rol')
print('- ✓ Auditoría de cambios de estado')
print('- ✓ Notificaciones automáticas')
print('- ✓ Validación de transiciones')

cursor.close()
connection.close()