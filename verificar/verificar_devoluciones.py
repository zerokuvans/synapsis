import mysql.connector

try:
    # Conectar a la base de datos
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='732137A031E4b@',
        database='capired'
    )
    
    cursor = connection.cursor(dictionary=True)
    
    print("=== VERIFICACIÓN DE DEVOLUCIONES REGISTRADAS ===")
    
    # Verificar las últimas devoluciones registradas
    cursor.execute("""
        SELECT * FROM devoluciones_dotacion 
        ORDER BY id DESC 
        LIMIT 5
    """)
    devoluciones = cursor.fetchall()
    
    if devoluciones:
        print(f"\n📋 Últimas {len(devoluciones)} devoluciones registradas:")
        for i, dev in enumerate(devoluciones, 1):
            print(f"\n{i}. Devolución ID: {dev.get('id', 'N/A')}")
            print(f"   Técnico ID: {dev.get('tecnico_id', 'N/A')}")
            print(f"   Cliente ID: {dev.get('cliente_id', 'N/A')}")
            print(f"   Fecha: {dev.get('fecha_devolucion', 'N/A')}")
            print(f"   Motivo: {dev.get('motivo', 'N/A')}")
            print(f"   Estado: {dev.get('estado', 'N/A')}")
            print(f"   Observaciones: {dev.get('observaciones', 'N/A')}")
    else:
        print("\n❌ No se encontraron devoluciones registradas")
    
    # Verificar estructura de la tabla
    cursor.execute("DESCRIBE devoluciones_dotacion")
    estructura = cursor.fetchall()
    
    print(f"\n🏗️ Estructura de la tabla devoluciones_dotacion:")
    for campo in estructura:
        print(f"   {campo['Field']}: {campo['Type']} - {campo['Null']} - {campo['Key']}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")