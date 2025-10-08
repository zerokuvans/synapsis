import mysql.connector

try:
    # Conectar a la base de datos
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='732137A031E4b@',
        database='capired'
    )
    
    cursor = connection.cursor()
    
    # Crear tabla devolucion_detalles
    create_table_query = """
    CREATE TABLE IF NOT EXISTS devolucion_detalles (
        id INT AUTO_INCREMENT PRIMARY KEY,
        devolucion_id INT NOT NULL,
        elemento VARCHAR(100) NOT NULL COMMENT 'Tipo de elemento: pantalon, camiseta, botas, etc.',
        talla VARCHAR(20) NULL COMMENT 'Talla del elemento si aplica',
        cantidad INT NOT NULL DEFAULT 1,
        estado_elemento ENUM('NUEVO', 'USADO_BUENO', 'USADO_REGULAR', 'DAÑADO') NOT NULL DEFAULT 'USADO_BUENO',
        observaciones TEXT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (devolucion_id) REFERENCES devoluciones_dotacion(id) ON DELETE CASCADE,
        INDEX idx_devolucion_id (devolucion_id),
        INDEX idx_elemento (elemento)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    cursor.execute(create_table_query)
    connection.commit()
    
    print("Tabla devolucion_detalles creada exitosamente")
    
    # Verificar la estructura de la tabla creada
    print("\nEstructura de la tabla devolucion_detalles:")
    cursor.execute("DESCRIBE devolucion_detalles")
    for row in cursor.fetchall():
        print(f"Campo: {row[0]}, Tipo: {row[1]}, Null: {row[2]}, Key: {row[3]}, Default: {row[4]}, Extra: {row[5]}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {str(e)}")