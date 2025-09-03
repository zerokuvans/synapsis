import mysql.connector
from mysql.connector import Error

def consultar_usuarios_logistica():
    """Consulta usuarios con rol de logística para pruebas"""
    
    try:
        # Configuración de conexión
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@',
            port=3306,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        if connection.is_connected():
            print("✓ Conexión exitosa a la base de datos")
            
            cursor = connection.cursor(dictionary=True)
            
            # 1. Consultar roles disponibles
            print("\n=== ROLES DISPONIBLES ===")
            cursor.execute("SELECT * FROM roles")
            roles = cursor.fetchall()
            
            for rol in roles:
                print(f"ID: {rol['id_roles']}, Nombre: {rol['nombre_rol']}")
            
            # 2. Buscar usuarios con rol de logística (asumiendo que es id 3 o 4)
            print("\n=== USUARIOS CON ROL DE LOGÍSTICA ===")
            cursor.execute("""
                SELECT 
                    ro.id_codigo_consumidor,
                    ro.recurso_operativo_cedula,
                    ro.nombre,
                    ro.estado,
                    r.nombre_rol,
                    ro.id_roles
                FROM recurso_operativo ro
                JOIN roles r ON ro.id_roles = r.id_roles
                WHERE r.nombre_rol LIKE '%logistica%' OR r.nombre_rol LIKE '%Logistica%'
                ORDER BY ro.nombre
            """)
            
            usuarios_logistica = cursor.fetchall()
            
            if usuarios_logistica:
                print(f"Encontrados {len(usuarios_logistica)} usuarios con rol de logística:")
                for usuario in usuarios_logistica:
                    print(f"  - Cédula: {usuario['recurso_operativo_cedula']}")
                    print(f"    Nombre: {usuario['nombre']}")
                    print(f"    Estado: {usuario['estado']}")
                    print(f"    Rol: {usuario['nombre_rol']} (ID: {usuario['id_roles']})")
                    print()
            else:
                print("No se encontraron usuarios con rol de logística")
                
                # Buscar todos los usuarios activos para ver qué roles tienen
                print("\n=== TODOS LOS USUARIOS ACTIVOS ===")
                cursor.execute("""
                    SELECT 
                        ro.recurso_operativo_cedula,
                        ro.nombre,
                        r.nombre_rol,
                        ro.id_roles
                    FROM recurso_operativo ro
                    JOIN roles r ON ro.id_roles = r.id_roles
                    WHERE ro.estado = 'Activo'
                    ORDER BY r.nombre_rol, ro.nombre
                """)
                
                todos_usuarios = cursor.fetchall()
                
                for usuario in todos_usuarios:
                    print(f"  - {usuario['recurso_operativo_cedula']} | {usuario['nombre']} | {usuario['nombre_rol']}")
            
            # 3. Verificar datos de vencimientos en la tabla
            print("\n=== VERIFICACIÓN DE DATOS DE VENCIMIENTOS ===")
            cursor.execute("""
                SELECT COUNT(*) as total_vehiculos
                FROM parque_automotor 
                WHERE estado = 'Activo'
            """)
            
            total = cursor.fetchone()
            print(f"Total de vehículos activos: {total['total_vehiculos']}")
            
            cursor.execute("""
                SELECT COUNT(*) as con_soat
                FROM parque_automotor 
                WHERE estado = 'Activo' AND soat_vencimiento IS NOT NULL
            """)
            
            con_soat = cursor.fetchone()
            print(f"Vehículos con fecha SOAT: {con_soat['con_soat']}")
            
            cursor.execute("""
                SELECT COUNT(*) as con_tecnomecanica
                FROM parque_automotor 
                WHERE estado = 'Activo' AND tecnomecanica_vencimiento IS NOT NULL
            """)
            
            con_tecno = cursor.fetchone()
            print(f"Vehículos con fecha tecnomecánica: {con_tecno['con_tecnomecanica']}")
            
            # Mostrar algunos ejemplos de vencimientos próximos
            cursor.execute("""
                SELECT 
                    placa,
                    soat_vencimiento,
                    tecnomecanica_vencimiento,
                    DATEDIFF(soat_vencimiento, CURDATE()) as dias_soat,
                    DATEDIFF(tecnomecanica_vencimiento, CURDATE()) as dias_tecnomecanica
                FROM parque_automotor 
                WHERE estado = 'Activo'
                AND (soat_vencimiento IS NOT NULL OR tecnomecanica_vencimiento IS NOT NULL)
                ORDER BY 
                    LEAST(
                        COALESCE(soat_vencimiento, '9999-12-31'),
                        COALESCE(tecnomecanica_vencimiento, '9999-12-31')
                    ) ASC
                LIMIT 5
            """)
            
            ejemplos = cursor.fetchall()
            
            if ejemplos:
                print("\nEjemplos de vencimientos (próximos):")
                for ejemplo in ejemplos:
                    print(f"  Placa: {ejemplo['placa']}")
                    if ejemplo['soat_vencimiento']:
                        print(f"    SOAT: {ejemplo['soat_vencimiento']} (días: {ejemplo['dias_soat']})")
                    if ejemplo['tecnomecanica_vencimiento']:
                        print(f"    Tecnomecánica: {ejemplo['tecnomecanica_vencimiento']} (días: {ejemplo['dias_tecnomecanica']})")
                    print()
            
            cursor.close()
            
    except Error as e:
        print(f"❌ Error de MySQL: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\n✓ Conexión cerrada")

if __name__ == "__main__":
    consultar_usuarios_logistica()