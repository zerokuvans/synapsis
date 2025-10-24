import mysql.connector
from mysql.connector import Error

def check_user_1019112308():
    try:
        # Configuración de la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            print("=== VERIFICACIÓN DEL USUARIO 1019112308 ===")
            
            # 1. Buscar usuario por cédula
            print("\n1. Buscando usuario por cédula 1019112308...")
            cursor.execute("SELECT * FROM recurso_operativo WHERE recurso_operativo_cedula = %s", ('1019112308',))
            user = cursor.fetchone()
            
            if user:
                print(f"   ✅ Usuario encontrado:")
                print(f"   - ID: {user['id_codigo_consumidor']}")
                print(f"   - Cédula: {user['recurso_operativo_cedula']}")
                print(f"   - Nombre: {user['nombre']}")
                print(f"   - Rol: {user['id_roles']}")
                print(f"   - Contraseña: {user['recurso_operativo_password']}")
                print(f"   - Estado: {user['estado']}")
                
                # 2. Verificar si tiene vehículo asignado
                print(f"\n2. Verificando vehículo asignado...")
                cursor.execute("SELECT placa FROM recurso_operativo WHERE recurso_operativo_cedula = %s", ('1019112308',))
                result = cursor.fetchone()
                if result and result['placa']:
                    print(f"   ✅ Vehículo asignado: {result['placa']}")
                else:
                    print("   ⚠️ No tiene vehículo asignado")
                    
            else:
                print("   ❌ Usuario no encontrado")
                
                # Buscar usuarios similares
                print("\n   Buscando usuarios con cédulas similares...")
                cursor.execute("SELECT recurso_operativo_cedula, nombre FROM recurso_operativo WHERE recurso_operativo_cedula LIKE %s LIMIT 10", ('%1019112308%',))
                similar_users = cursor.fetchall()
                
                if similar_users:
                    print("   Usuarios similares encontrados:")
                    for user in similar_users:
                        print(f"   - {user['recurso_operativo_cedula']}: {user['nombre']}")
                else:
                    print("   No se encontraron usuarios similares")
            
    except Error as e:
        print(f"Error de conexión: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    check_user_1019112308()