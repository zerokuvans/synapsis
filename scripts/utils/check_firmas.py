import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'synapsis'
}

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    # Verificar dotaciones firmadas
    cursor.execute('''
        SELECT id_dotacion, firmado, fecha_firma, usuario_firma, firma_imagen
        FROM dotaciones 
        WHERE firmado = 1 
        LIMIT 5
    ''')
    
    result = cursor.fetchall()
    
    print('Dotaciones firmadas:')
    if result:
        for r in result:
            print(f'ID: {r["id_dotacion"]}, Firmado: {r["firmado"]}, Fecha: {r["fecha_firma"]}, Usuario: {r["usuario_firma"]}, Tiene imagen: {"Sí" if r["firma_imagen"] else "No"}')
    else:
        print('No hay dotaciones firmadas')
    
    conn.close()
    
except Exception as e:
    print(f'Error: {e}')