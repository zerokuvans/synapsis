import mysql.connector

def verificar_base_datos(database_name):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database=database_name,
            user='root',
            password='732137A031E4b@'
        )
        
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES LIKE 'mpa_%'")
        tables = cursor.fetchall()
        
        print(f'\n📊 Tablas MPA en base de datos {database_name}:')
        for table in tables:
            print(f'  - {table[0]}')
            
        # Verificar específicamente las tablas de vencimientos
        print(f'\n🔍 Verificando tablas específicas en {database_name}:')
        for table_name in ['mpa_soat', 'mpa_tecnico_mecanica', 'mpa_licencia_conducir']:
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            result = cursor.fetchone()
            if result:
                print(f'  ✓ {table_name} existe')
                # Contar registros
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f'    📈 Registros: {count}')
            else:
                print(f'  ✗ {table_name} NO existe')
                
        connection.close()
        return True
        
    except Exception as e:
        print(f'❌ Error conectando a {database_name}: {e}')
        return False

# Verificar ambas bases de datos
print('🔍 VERIFICANDO BASES DE DATOS PARA TABLAS MPA')
print('=' * 50)

# Verificar capired
capired_ok = verificar_base_datos('capired')

# Verificar synapsis
synapsis_ok = verificar_base_datos('synapsis')

if not capired_ok and not synapsis_ok:
    print('\n❌ No se pudo conectar a ninguna base de datos')
elif capired_ok and not synapsis_ok:
    print('\n✅ Las tablas están en la base de datos CAPIRED')
elif not capired_ok and synapsis_ok:
    print('\n✅ Las tablas están en la base de datos SYNAPSIS')
else:
    print('\n⚠️ Ambas bases de datos están disponibles')