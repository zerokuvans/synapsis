import mysql.connector
from mysql.connector import Error
import bcrypt

print("=== Verificación de usuarios en MySQL ===")

try:
    # Configuración de conexión MySQL (basada en .env)
    connection = mysql.connector.connect(
        host='localhost',
        database='capired',
        user='root',
        password='732137A031E4b@',
        port=3306
    )
    
    if connection.is_connected():
        print("✓ Conexión exitosa a MySQL")
        
        cursor = connection.cursor(dictionary=True)
        
        # 1. Verificar qué tablas existen
        print("\n1. Tablas en la base de datos:")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table in tables:
            table_name = list(table.values())[0]
            print(f"   - {table_name}")
        
        # 2. Verificar tabla de usuarios
        print("\n2. Verificando tabla recurso_operativo (usuarios):")
        try:
            cursor.execute("SELECT COUNT(*) as total FROM recurso_operativo")
            result = cursor.fetchone()
            print(f"   Total de usuarios: {result['total']}")
            
            if result['total'] > 0:
                cursor.execute("SELECT id, usuario, nombre, activo FROM recurso_operativo LIMIT 5")
                usuarios = cursor.fetchall()
                print("   Usuarios disponibles:")
                for usuario in usuarios:
                    print(f"     - ID: {usuario['id']}, Usuario: {usuario['usuario']}, Nombre: {usuario['nombre']}, Activo: {usuario['activo']}")
            else:
                print("   No hay usuarios registrados")
                
        except Error as e:
            print(f"   ✗ Error consultando usuarios: {e}")
        
        # 3. Verificar tabla parque_automotor
        print("\n3. Verificando tabla parque_automotor:")
        try:
            cursor.execute("SELECT COUNT(*) as total FROM parque_automotor")
            result = cursor.fetchone()
            print(f"   Total de vehículos: {result['total']}")
            
            if result['total'] > 0:
                # Verificar vehículos con vencimientos
                cursor.execute("""
                    SELECT COUNT(*) as con_soat 
                    FROM parque_automotor 
                    WHERE soat_vencimiento IS NOT NULL AND soat_vencimiento != ''
                """)
                result_soat = cursor.fetchone()
                
                cursor.execute("""
                    SELECT COUNT(*) as con_tecno 
                    FROM parque_automotor 
                    WHERE tecnomecanica_vencimiento IS NOT NULL AND tecnomecanica_vencimiento != ''
                """)
                result_tecno = cursor.fetchone()
                
                print(f"   Vehículos con SOAT: {result_soat['con_soat']}")
                print(f"   Vehículos con Tecnomecánica: {result_tecno['con_tecno']}")
                
                # Mostrar algunos ejemplos
                cursor.execute("""
                    SELECT placa, tipo_vehiculo, soat_vencimiento, tecnomecanica_vencimiento 
                    FROM parque_automotor 
                    WHERE (soat_vencimiento IS NOT NULL AND soat_vencimiento != '') 
                       OR (tecnomecanica_vencimiento IS NOT NULL AND tecnomecanica_vencimiento != '')
                    LIMIT 3
                """)
                ejemplos = cursor.fetchall()
                if ejemplos:
                    print("   Ejemplos de vehículos con vencimientos:")
                    for vehiculo in ejemplos:
                        print(f"     - Placa: {vehiculo['placa']}, Tipo: {vehiculo['tipo_vehiculo']}")
                        print(f"       SOAT: {vehiculo['soat_vencimiento']}, Tecnomecánica: {vehiculo['tecnomecanica_vencimiento']}")
            else:
                print("   No hay vehículos registrados")
                
        except Error as e:
            print(f"   ✗ Error consultando vehículos: {e}")
        
        # 4. Crear usuario de prueba si no existe
        print("\n4. Verificando/creando usuario de prueba:")
        try:
            cursor.execute("SELECT * FROM recurso_operativo WHERE usuario = 'admin'")
            admin_user = cursor.fetchone()
            
            if admin_user:
                print("   ✓ Usuario 'admin' ya existe")
                print(f"   Datos: {admin_user}")
            else:
                print("   Usuario 'admin' no existe, creando...")
                # Crear hash de la contraseña
                password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
                
                cursor.execute("""
                    INSERT INTO recurso_operativo (usuario, password, nombre, activo) 
                    VALUES (%s, %s, %s, %s)
                """, ('admin', password_hash.decode('utf-8'), 'Administrador', 1))
                
                connection.commit()
                print("   ✓ Usuario 'admin' creado exitosamente")
                
        except Error as e:
            print(f"   ✗ Error manejando usuario admin: {e}")
        
except Error as e:
    print(f"✗ Error conectando a MySQL: {e}")
    print("Verifica que MySQL esté corriendo y la base de datos 'synapsis' exista")
    
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("\n✓ Conexión cerrada")

print("\n=== Fin de la verificación ===")