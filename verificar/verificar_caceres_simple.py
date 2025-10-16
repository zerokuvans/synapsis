import mysql.connector

def verificar_caceres():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='capired',
            user='root',
            password='732137A031E4b@'
        )
        cursor = connection.cursor()
        
        # Verificar usuario en recurso_operativo
        cursor.execute("""
            SELECT recurso_operativo_cedula, nombre, id_roles, estado
            FROM recurso_operativo 
            WHERE recurso_operativo_cedula = %s
        """, ('1032402333',))
        
        usuario = cursor.fetchone()
        if usuario:
            print(f"Usuario encontrado: {usuario[1]} - Rol: {usuario[2]} - Estado: {usuario[3]}")
        else:
            print("Usuario no encontrado en recurso_operativo")
            return
        
        # Verificar registros de asistencia por cedula
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM asistencia 
            WHERE supervisor = %s
            AND fecha_asistencia >= '2025-10-01' 
            AND fecha_asistencia <= '2025-10-31'
        """, ('1032402333',))
        
        resultado = cursor.fetchone()
        print(f"Registros por cedula: {resultado[0]}")
        
        # Verificar registros de asistencia por nombre
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM asistencia 
            WHERE supervisor LIKE %s
            AND fecha_asistencia >= '2025-10-01' 
            AND fecha_asistencia <= '2025-10-31'
        """, ('%CACERES%',))
        
        resultado = cursor.fetchone()
        print(f"Registros por nombre CACERES: {resultado[0]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verificar_caceres()