import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='732137A031E4b@',
        database='capired'
    )
    cursor = connection.cursor(dictionary=True)
    
    print('🔍 VERIFICANDO TABLA presupuesto_cargo...')
    
    # Verificar si la tabla existe
    cursor.execute("SELECT COUNT(*) as existe FROM information_schema.tables WHERE table_schema = 'capired' AND table_name = 'presupuesto_cargo'")
    resultado = cursor.fetchone()
    
    if resultado['existe'] == 0:
        print('❌ Tabla presupuesto_cargo NO existe. Creándola...')
        
        # Crear la tabla presupuesto_cargo
        cursor.execute("""
            CREATE TABLE presupuesto_cargo (
                id INT AUTO_INCREMENT PRIMARY KEY,
                presupuesto_cargo VARCHAR(100) NOT NULL UNIQUE,
                presupuesto_eventos INT DEFAULT 0,
                presupuesto_diario DECIMAL(10,2) DEFAULT 0.00,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                estado VARCHAR(20) DEFAULT 'Activo'
            )
        """)
        
        print('✅ Tabla presupuesto_cargo creada exitosamente')
        
        # Insertar datos de ejemplo
        datos_ejemplo = [
            ('TECNICO', 8, 120000),
            ('ANALISTA LOGISTICA', 6, 100000),
            ('DESARROLLADOR', 4, 150000),
            ('LIDER', 10, 180000)
        ]
        
        for cargo, eventos, diario in datos_ejemplo:
            cursor.execute("INSERT INTO presupuesto_cargo (presupuesto_cargo, presupuesto_eventos, presupuesto_diario) VALUES (%s, %s, %s)", (cargo, eventos, diario))
            print(f'   ✅ {cargo}: {eventos} eventos, ${diario:,}')
        
        connection.commit()
        print('✅ Datos de ejemplo insertados')
        
    else:
        print('✅ Tabla presupuesto_cargo YA existe')
    
    print('\n📊 DATOS ACTUALES:')
    cursor.execute('SELECT * FROM presupuesto_cargo ORDER BY presupuesto_cargo')
    datos = cursor.fetchall()
    for i, dato in enumerate(datos, 1):
        print(f'  {i}. {dato["presupuesto_cargo"]}: {dato["presupuesto_eventos"]} eventos, ${dato["presupuesto_diario"]:,}')
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f'❌ Error: {e}')