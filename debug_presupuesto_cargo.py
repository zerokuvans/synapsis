#!/usr/bin/env python3
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

try:
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor(dictionary=True)
    
    print('=== ESTRUCTURA DE LA TABLA presupuesto_carpeta ===')
    cursor.execute('DESCRIBE presupuesto_carpeta')
    columns = cursor.fetchall()
    
    for col in columns:
        field = col["Field"]
        type_col = col["Type"]
        null_col = col["Null"]
        key_col = col["Key"]
        default_col = col["Default"]
        extra_col = col["Extra"]
        print(f'{field:20} | {type_col:20} | {null_col:5} | {key_col:5} | {default_col} | {extra_col}')
    
    print('\n=== DATOS DE EJEMPLO EN presupuesto_carpeta ===')
    cursor.execute('SELECT * FROM presupuesto_carpeta LIMIT 3')
    rows = cursor.fetchall()
    
    if rows:
        for i, row in enumerate(rows, 1):
            print(f'Registro {i}:')
            for key, value in row.items():
                print(f'  {key}: {value}')
            print()
    
    print('\n=== CREAR TABLA presupuesto_cargo ===')
    # Crear la tabla presupuesto_cargo basada en presupuesto_carpeta
    # pero cambiando 'carpeta' por 'cargo'
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS presupuesto_cargo (
        id int(11) NOT NULL AUTO_INCREMENT,
        cargo varchar(45) DEFAULT NULL,
        codigo_presupuesto varchar(45) DEFAULT NULL,
        descripcion_presupuesto varchar(255) DEFAULT NULL,
        PRIMARY KEY (id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    """
    
    cursor.execute(create_table_sql)
    connection.commit()
    print("Tabla presupuesto_cargo creada exitosamente")
    
    # Insertar algunos datos de ejemplo basados en los cargos existentes
    print('\n=== INSERTANDO DATOS DE EJEMPLO ===')
    
    # Obtener cargos únicos
    cursor.execute('SELECT DISTINCT cargo FROM recurso_operativo WHERE cargo IS NOT NULL AND cargo != ""')
    cargos = cursor.fetchall()
    
    insert_data = [
        ('TECNICO', 'PRES_TEC_001', 'Presupuesto para técnicos de campo'),
        ('DESARROLLADOR', 'PRES_DEV_001', 'Presupuesto para desarrolladores'),
        ('ANALISTA LOGISTICA', 'PRES_LOG_001', 'Presupuesto para analistas de logística'),
        ('SUPERVISORES', 'PRES_SUP_001', 'Presupuesto para supervisores'),
        ('ANALISTA', 'PRES_ANA_001', 'Presupuesto para analistas'),
        ('TECNICO DE TELECOMUNICACIONES', 'PRES_TEL_001', 'Presupuesto para técnicos de telecomunicaciones'),
        ('CONDUCTOR', 'PRES_CON_001', 'Presupuesto para conductores'),
        ('FTTH INSTALACIONES', 'PRES_FTT_001', 'Presupuesto para instalaciones FTTH')
    ]
    
    for cargo, codigo, descripcion in insert_data:
        try:
            cursor.execute(
                "INSERT INTO presupuesto_cargo (cargo, codigo_presupuesto, descripcion_presupuesto) VALUES (%s, %s, %s)",
                (cargo, codigo, descripcion)
            )
            print(f"Insertado: {cargo} - {codigo}")
        except Exception as e:
            print(f"Error insertando {cargo}: {e}")
    
    connection.commit()
    
    print('\n=== VERIFICAR DATOS INSERTADOS ===')
    cursor.execute('SELECT * FROM presupuesto_cargo')
    rows = cursor.fetchall()
    
    for row in rows:
        print(f"ID: {row['id']}, Cargo: {row['cargo']}, Código: {row['codigo_presupuesto']}, Descripción: {row['descripcion_presupuesto']}")
        
except Exception as e:
    print(f'Error: {e}')
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()