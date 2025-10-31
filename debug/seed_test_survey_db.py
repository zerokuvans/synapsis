import mysql.connector
import json

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
}

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def seed():
    conn = get_conn()
    cur = conn.cursor()
    titulo = 'Encuesta de prueba FTTH'
    descripcion = 'Encuesta temporal para validar popup en FTTH INSTALACIONES'
    estado = 'activa'
    anonima = 0
    visibilidad = 'publica'
    dirigida_a = 'tecnicos'
    audiencia_carpetas = json.dumps(['FTTH INSTALACIONES'], ensure_ascii=False)
    creado_por = 11

    cur.execute(
        """
        INSERT INTO encuestas (titulo, descripcion, estado, anonima, visibilidad, dirigida_a, audiencia_carpetas, fecha_inicio, fecha_fin, creado_por)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, NULL, %s)
        """,
        (titulo, descripcion, estado, anonima, visibilidad, dirigida_a, audiencia_carpetas, creado_por)
    )
    encuesta_id = cur.lastrowid

    # Pregunta de selección única requerida
    cur.execute(
        """
        INSERT INTO encuesta_preguntas (encuesta_id, tipo, texto, ayuda, requerida, orden, config_json)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (encuesta_id, 'seleccion_unica', '¿Estás conforme con tu kit?', None, 1, 0, None)
    )
    pregunta_id = cur.lastrowid

    # Opciones
    cur.execute(
        """
        INSERT INTO encuesta_opciones (pregunta_id, texto, valor, orden)
        VALUES (%s, %s, %s, %s)
        """,
        (pregunta_id, 'Sí', None, 0)
    )
    cur.execute(
        """
        INSERT INTO encuesta_opciones (pregunta_id, texto, valor, orden)
        VALUES (%s, %s, %s, %s)
        """,
        (pregunta_id, 'No', None, 1)
    )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Encuesta creada: id={encuesta_id}, pregunta={pregunta_id}")

if __name__ == '__main__':
    seed()