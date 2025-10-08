import mysql.connector
from mysql.connector import Error

print("=== Verificación de estructura de tablas ===")

try:
    # Configuración de conexión MySQL
    connection = mysql.connector.connect(
        host='localhost',
        database='capired',
        user='root',
        password='732137A031E4b@',
        port=3306
    )
    
    if connection.is_connected():
        print("✓ Conexión exitosa a MySQL")
        
        cursor = connection.cursor()
        
        # 1. Estructura de tabla recurso_operativo
        print("\n1. Estructura de tabla recurso_operativo:")
        cursor.execute("DESCRIBE recurso_operativo")
        columns = cursor.fetchall()
        for column in columns:
            print(f"   - {column[0]} ({column[1]}) - {column[3]} - {column[4]}")
        
        # 2. Estructura de tabla parque_automotor
        print("\n2. Estructura de tabla parque_automotor:")
        cursor.execute("DESCRIBE parque_automotor")
        columns = cursor.fetchall()
        for column in columns:
            print(f"   - {column[0]} ({column[1]}) - {column[3]} - {column[4]}")
        
        # 3. Verificar algunos registros de usuarios
        print("\n3. Primeros 3 usuarios en recurso_operativo:")
        cursor.execute("SELECT * FROM recurso_operativo LIMIT 3")
        usuarios = cursor.fetchall()
        
        # Obtener nombres de columnas
        cursor.execute("SHOW COLUMNS FROM recurso_operativo")
        column_names = [column[0] for column in cursor.fetchall()]
        print(f"   Columnas: {column_names}")
        
        for i, usuario in enumerate(usuarios):
            print(f"   Usuario {i+1}: {dict(zip(column_names, usuario))}")
        
        # 4. Verificar algunos registros de vehículos
        print("\n4. Primeros 3 vehículos en parque_automotor:")
        cursor.execute("SELECT * FROM parque_automotor LIMIT 3")
        vehiculos = cursor.fetchall()
        
        # Obtener nombres de columnas
        cursor.execute("SHOW COLUMNS FROM parque_automotor")
        column_names = [column[0] for column in cursor.fetchall()]
        print(f"   Columnas: {column_names}")
        
        for i, vehiculo in enumerate(vehiculos):
            print(f"   Vehículo {i+1}: {dict(zip(column_names, vehiculo))}")
        
        # 5. Buscar vehículos con fechas de vencimiento válidas
        print("\n5. Vehículos con fechas de vencimiento:")
        
        # Primero verificar qué columnas de fecha existen
        cursor.execute("SHOW COLUMNS FROM parque_automotor")
        columns = cursor.fetchall()
        date_columns = [col[0] for col in columns if 'vencimiento' in col[0].lower() or 'fecha' in col[0].lower()]
        print(f"   Columnas de fecha encontradas: {date_columns}")
        
        if date_columns:
            # Construir consulta dinámica
            select_fields = ['placa'] + date_columns
            query = f"SELECT {', '.join(select_fields)} FROM parque_automotor WHERE "
            conditions = []
            for col in date_columns:
                conditions.append(f"({col} IS NOT NULL AND {col} != '' AND {col} != '0000-00-00')")
            query += " OR ".join(conditions) + " LIMIT 5"
            
            print(f"   Consulta: {query}")
            
            try:
                cursor.execute(query)
                vehiculos_con_fechas = cursor.fetchall()
                
                if vehiculos_con_fechas:
                    for vehiculo in vehiculos_con_fechas:
                        data = dict(zip(select_fields, vehiculo))
                        print(f"     - {data}")
                else:
                    print("     No se encontraron vehículos con fechas válidas")
            except Error as e:
                print(f"     Error en consulta de fechas: {e}")
        
except Error as e:
    print(f"✗ Error conectando a MySQL: {e}")
    
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("\n✓ Conexión cerrada")

print("\n=== Fin de la verificación ===")