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

def asignar_analista():
    """Asignar ESPITIA BARON LICED JOANA como analista del técnico ALARCON SALAS LUIS HERNANDO"""
    connection = get_db_connection()
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    print("="*60)
    print("ASIGNACIÓN DE ANALISTA AL TÉCNICO")
    print("="*60)
    
    try:
        # 1. Verificar datos actuales
        print("\n[1] VERIFICANDO DATOS ACTUALES:")
        
        # Verificar técnico
        cursor.execute("""
            SELECT id_codigo_consumidor, nombre, analista
            FROM recurso_operativo 
            WHERE id_codigo_consumidor = 11
        """)
        tecnico = cursor.fetchone()
        
        if tecnico:
            print(f"   ✅ Técnico: {tecnico['nombre']}")
            print(f"      Analista actual: '{tecnico['analista']}'")
        else:
            print("   ❌ Técnico no encontrado")
            return
        
        # Verificar analista
        cursor.execute("""
            SELECT id_codigo_consumidor, nombre, cargo
            FROM recurso_operativo 
            WHERE nombre = 'ESPITIA BARON LICED JOANA'
        """)
        analista = cursor.fetchone()
        
        if analista:
            print(f"   ✅ Analista: {analista['nombre']}")
            print(f"      Cargo: {analista['cargo']}")
        else:
            print("   ❌ Analista no encontrado")
            return
        
        # 2. Realizar la asignación
        print("\n[2] REALIZANDO ASIGNACIÓN:")
        
        cursor.execute("""
            UPDATE recurso_operativo 
            SET analista = %s 
            WHERE id_codigo_consumidor = %s
        """, (analista['nombre'], tecnico['id_codigo_consumidor']))
        
        connection.commit()
        
        print(f"   ✅ Analista '{analista['nombre']}' asignado al técnico '{tecnico['nombre']}'")
        
        # 3. Verificar la asignación
        print("\n[3] VERIFICANDO ASIGNACIÓN:")
        
        cursor.execute("""
            SELECT id_codigo_consumidor, nombre, analista
            FROM recurso_operativo 
            WHERE id_codigo_consumidor = 11
        """)
        tecnico_actualizado = cursor.fetchone()
        
        if tecnico_actualizado and tecnico_actualizado['analista'] == analista['nombre']:
            print(f"   ✅ Asignación exitosa!")
            print(f"      Técnico: {tecnico_actualizado['nombre']}")
            print(f"      Analista asignado: {tecnico_actualizado['analista']}")
        else:
            print("   ❌ Error en la asignación")
        
    except Error as e:
        print(f"❌ Error en la operación: {e}")
        connection.rollback()
    
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    print("Este script asignará a ESPITIA BARON LICED JOANA como analista del técnico ALARCON SALAS LUIS HERNANDO")
    respuesta = input("¿Desea continuar? (s/n): ")
    
    if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        asignar_analista()
    else:
        print("Operación cancelada")