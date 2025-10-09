import mysql.connector

def verificar_y_crear_presupuesto_cargo():
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
        cursor.execute("""
            SELECT COUNT(*) as existe 
            FROM information_schema.tables 
            WHERE table_schema = 'capired' 
            AND table_name = 'presupuesto_cargo'
        """)
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
            
            # Insertar datos de ejemplo basados en los cargos existentes
            print('📊 Insertando datos de ejemplo...')
            
            # Obtener cargos únicos de recurso_operativo
            cursor.execute("""
                SELECT DISTINCT cargo 
                FROM recurso_operativo 
                WHERE cargo IS NOT NULL 
                AND cargo != '' 
                AND cargo != 'None'
            """)
            cargos = cursor.fetchall()
            
            # Insertar presupuestos para cada cargo
            for cargo_data in cargos:
                cargo = cargo_data['cargo']
                if cargo:
                    # Asignar valores de presupuesto según el tipo de cargo
                    if 'TECNICO' in cargo.upper():
                        eventos = 8
                        diario = 120000
                    elif 'ANALISTA' in cargo.upper():
                        eventos = 6
                        diario = 100000
                    elif 'DESARROLLADOR' in cargo.upper():
                        eventos = 4
                        diario = 150000
                    elif 'LIDER' in cargo.upper() or 'SUPERVISOR' in cargo.upper():
                        eventos = 10
                        diario = 180000
                    else:
                        eventos = 5
                        diario = 80000
                    
                    cursor.execute("""
                        INSERT INTO presupuesto_cargo 
                        (presupuesto_cargo, presupuesto_eventos, presupuesto_diario) 
                        VALUES (%s, %s, %s)
                    """, (cargo, eventos, diario))
                    
                    print(f'   ✅ {cargo}: {eventos} eventos, ${diario:,}')
            
            connection.commit()
            print('✅ Datos de ejemplo insertados')
            
        else:
            print('✅ Tabla presupuesto_cargo YA existe')
        
        # Mostrar estructura y datos actuales
        print('\n📋 ESTRUCTURA DE presupuesto_cargo:')
        cursor.execute('DESCRIBE presupuesto_cargo')
        columnas = cursor.fetchall()
        for col in columnas:
            print(f'  - {col["Field"]} ({col["Type"]})')
        
        print('\n📊 DATOS ACTUALES:')
        cursor.execute('SELECT * FROM presupuesto_cargo ORDER BY presupuesto_cargo')
        datos = cursor.fetchall()
        for i, dato in enumerate(datos, 1):
            print(f'  {i}. {dato["presupuesto_cargo"]}: {dato["presupuesto_eventos"]} eventos, ${dato["presupuesto_diario"]:,}')
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == "__main__":
    verificar_y_crear_presupuesto_cargo()