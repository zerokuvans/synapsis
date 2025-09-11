import mysql.connector
import bcrypt

try:
    # Conectar a la base de datos
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='732137A031E4b@',
        database='capired'
    )
    
    cursor = connection.cursor(dictionary=True)
    
    # Verificar si ya existe el usuario de prueba
    cursor.execute("""
        SELECT * FROM recurso_operativo 
        WHERE recurso_operativo_cedula = 'test_logistica'
    """)
    existing_user = cursor.fetchone()
    
    if existing_user:
        print("Usuario de prueba ya existe. Actualizando...")
        # Actualizar usuario existente
        password_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("""
            UPDATE recurso_operativo 
            SET id_roles = 5, estado = 'Activo', recurso_operativo_password = %s
            WHERE recurso_operativo_cedula = 'test_logistica'
        """, (password_hash,))
    else:
        print("Creando nuevo usuario de logística...")
        # Crear nuevo usuario
        password_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute("""
            INSERT INTO recurso_operativo 
            (recurso_operativo_cedula, nombre, recurso_operativo_password, id_roles, estado, cargo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            'test_logistica',
            'Usuario Logística Test',
            password_hash,
            5,  # ID del rol logística
            'Activo',
            'Logística'
        ))
    
    connection.commit()
    
    # Verificar que el usuario fue creado/actualizado correctamente
    cursor.execute("""
        SELECT recurso_operativo_cedula, nombre, id_roles, estado 
        FROM recurso_operativo 
        WHERE recurso_operativo_cedula = 'test_logistica'
    """)
    user = cursor.fetchone()
    
    if user:
        print(f"✓ Usuario creado/actualizado exitosamente:")
        print(f"  Cédula: {user['recurso_operativo_cedula']}")
        print(f"  Nombre: {user['nombre']}")
        print(f"  Rol ID: {user['id_roles']} (logística)")
        print(f"  Estado: {user['estado']}")
        print(f"  Contraseña: 123456")
    else:
        print("❌ Error: No se pudo crear/actualizar el usuario")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")