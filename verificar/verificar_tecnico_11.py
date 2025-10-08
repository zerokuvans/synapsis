import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Conectar a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def verificar_datos_completos():
    """Verificar datos completos del técnico 11 y analistas"""
    connection = get_db_connection()
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    print("="*60)
    print("VERIFICACIÓN COMPLETA DE DATOS")
    print("="*60)
    
    # 1. Verificar técnico ID 11
    print("\n[1] DATOS DEL TÉCNICO ID 11:")
    cursor.execute("""
        SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula, 
               id_roles, estado, cargo, analista
        FROM recurso_operativo 
        WHERE id_codigo_consumidor = 11
    """)
    tecnico = cursor.fetchone()
    
    if tecnico:
        print(f"   ✅ Técnico encontrado:")
        print(f"      ID: {tecnico['id_codigo_consumidor']}")
        print(f"      Nombre: {tecnico['nombre']}")
        print(f"      Cédula: {tecnico['recurso_operativo_cedula']}")
        print(f"      Rol: {tecnico['id_roles']}")
        print(f"      Estado: {tecnico['estado']}")
        print(f"      Cargo: {tecnico['cargo']}")
        print(f"      Analista asignado: {tecnico['analista']}")
    else:
        print("   ❌ Técnico no encontrado")
        return
    
    # 2. Verificar ESPITIA BARON LICED JOANA
    print("\n[2] DATOS DE ESPITIA BARON LICED JOANA:")
    cursor.execute("""
        SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula, 
               id_roles, estado, cargo
        FROM recurso_operativo 
        WHERE nombre LIKE '%ESPITIA%BARON%LICED%JOANA%'
    """)
    espitia = cursor.fetchone()
    
    if espitia:
        print(f"   ✅ Usuario encontrado:")
        print(f"      ID: {espitia['id_codigo_consumidor']}")
        print(f"      Nombre: {espitia['nombre']}")
        print(f"      Cédula: {espitia['recurso_operativo_cedula']}")
        print(f"      Rol: {espitia['id_roles']}")
        print(f"      Estado: {espitia['estado']}")
        print(f"      Cargo: {espitia['cargo']}")
    else:
        print("   ❌ Usuario no encontrado")
    
    # 3. Verificar usuarios con cargo ANALISTA
    print("\n[3] USUARIOS CON CARGO 'ANALISTA':")
    cursor.execute("""
        SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula, 
               id_roles, estado, cargo
        FROM recurso_operativo 
        WHERE cargo = 'ANALISTA' AND estado = 'Activo'
        ORDER BY nombre
    """)
    analistas_cargo = cursor.fetchall()
    
    if analistas_cargo:
        print(f"   ✅ {len(analistas_cargo)} usuarios con cargo ANALISTA:")
        for analista in analistas_cargo:
            print(f"      - {analista['nombre']} (ID: {analista['id_codigo_consumidor']}, Rol: {analista['id_roles']})")
    else:
        print("   ❌ No hay usuarios con cargo ANALISTA")
    
    # 4. Verificar todos los cargos únicos
    print("\n[4] TODOS LOS CARGOS ÚNICOS EN EL SISTEMA:")
    cursor.execute("""
        SELECT DISTINCT cargo, COUNT(*) as cantidad
        FROM recurso_operativo 
        WHERE cargo IS NOT NULL AND cargo != ''
        GROUP BY cargo
        ORDER BY cargo
    """)
    cargos = cursor.fetchall()
    
    if cargos:
        print(f"   ✅ {len(cargos)} cargos diferentes:")
        for cargo in cargos:
            print(f"      - {cargo['cargo']}: {cargo['cantidad']} usuarios")
    else:
        print("   ❌ No se encontraron cargos")
    
    # 5. Verificar qué devuelve el endpoint /api/analistas
    print("\n[5] SIMULACIÓN DEL ENDPOINT /api/analistas:")
    cursor.execute("""
        SELECT id_codigo_consumidor, nombre, recurso_operativo_cedula 
        FROM recurso_operativo 
        WHERE cargo = 'ANALISTA' AND estado = 'Activo' 
        ORDER BY nombre
    """)
    resultado_endpoint = cursor.fetchall()
    
    if resultado_endpoint:
        print(f"   ✅ El endpoint devolvería {len(resultado_endpoint)} analistas:")
        for analista in resultado_endpoint:
            print(f"      - {analista['nombre']} (ID: {analista['id_codigo_consumidor']})")
    else:
        print("   ❌ El endpoint no devolvería ningún analista")
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    verificar_datos_completos()