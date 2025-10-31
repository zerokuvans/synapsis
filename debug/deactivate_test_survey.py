import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
}

def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    # Desactivar encuestas de prueba por título y/o ID conocida
    # 1) Por título exacto
    cur.execute(
        """
        UPDATE encuestas
        SET estado = 'borrador'
        WHERE estado = 'activa' AND titulo = %s
        """,
        ("Encuesta de prueba FTTH",)
    )
    affected_title = cur.rowcount

    # 2) También intentar por ID 8 (la que se sembró en pruebas)
    cur.execute(
        """
        UPDATE encuestas
        SET estado = 'borrador'
        WHERE estado = 'activa' AND id_encuesta = %s
        """,
        (8,)
    )
    affected_id = cur.rowcount

    conn.commit()
    cur.close()
    conn.close()

    print(f"Encuestas desactivadas por título: {affected_title}")
    print(f"Encuestas desactivadas por ID=8: {affected_id}")

if __name__ == '__main__':
    main()