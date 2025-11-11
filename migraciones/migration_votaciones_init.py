#!/usr/bin/env python3
"""
Migración inicial para el sistema de votaciones.
 - Agrega columnas en 'encuestas' para votaciones
 - Crea tablas 'candidatos' y 'votos'
"""

import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
    'autocommit': True
}


def run():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        def column_exists(table, column):
            cursor.execute(f"SHOW COLUMNS FROM {table} LIKE %s", (column,))
            return cursor.fetchone() is not None

        # Agregar columnas a 'encuestas'
        cols = [
            ("tipo_encuesta", "ENUM('encuesta','votacion') DEFAULT 'encuesta'"),
            ("mostrar_resultados", "TINYINT(1) DEFAULT 0"),
            ("fecha_inicio_votacion", "DATETIME NULL"),
            ("fecha_fin_votacion", "DATETIME NULL"),
        ]
        for col, defn in cols:
            if not column_exists('encuestas', col):
                cursor.execute(f"ALTER TABLE encuestas ADD COLUMN {col} {defn}")

        # Crear tabla candidatos
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS candidatos (
                id_candidato INT AUTO_INCREMENT PRIMARY KEY,
                id_encuesta INT NOT NULL,
                nombre VARCHAR(255) NOT NULL,
                descripcion TEXT NULL,
                foto_url VARCHAR(500) NULL,
                orden INT DEFAULT 0,
                fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_candidatos_encuesta FOREIGN KEY (id_encuesta)
                    REFERENCES encuestas(id_encuesta) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # Crear tabla votos
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS votos (
                id_voto INT AUTO_INCREMENT PRIMARY KEY,
                id_encuesta INT NOT NULL,
                id_candidato INT NOT NULL,
                id_usuario INT NOT NULL,
                fecha_voto DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45) NULL,
                UNIQUE KEY uniq_voto (id_encuesta, id_usuario),
                CONSTRAINT fk_votos_encuesta FOREIGN KEY (id_encuesta)
                    REFERENCES encuestas(id_encuesta) ON DELETE CASCADE,
                CONSTRAINT fk_votos_candidato FOREIGN KEY (id_candidato)
                    REFERENCES candidatos(id_candidato) ON DELETE CASCADE,
                CONSTRAINT fk_votos_usuario FOREIGN KEY (id_usuario)
                    REFERENCES usuarios(idusuarios) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        print("✅ Migración de votaciones aplicada correctamente")

    except Error as e:
        print(f"❌ Error aplicando migración de votaciones: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    run()