#!/usr/bin/env python3
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired'
}

def verificar():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    print("\n=== Verificando esquema de votaciones ===")

    def show_table(name):
        cur.execute(f"SHOW TABLES LIKE '{name}'")
        exists = cur.fetchone() is not None
        print(f"Tabla {name}: {'OK' if exists else 'NO EXISTE'}")
        if exists:
            cur.execute(f"DESCRIBE {name}")
            cols = cur.fetchall()
            for c in cols:
                print(f"  - {c[0]}: {c[1]}")

    # Columnas en encuestas
    print("\nColumnas en encuestas:")
    cur.execute("SHOW COLUMNS FROM encuestas LIKE 'tipo_encuesta'")
    print("  tipo_encuesta:", 'OK' if cur.fetchone() else 'NO')
    cur.execute("SHOW COLUMNS FROM encuestas LIKE 'mostrar_resultados'")
    print("  mostrar_resultados:", 'OK' if cur.fetchone() else 'NO')
    cur.execute("SHOW COLUMNS FROM encuestas LIKE 'fecha_inicio_votacion'")
    print("  fecha_inicio_votacion:", 'OK' if cur.fetchone() else 'NO')
    cur.execute("SHOW COLUMNS FROM encuestas LIKE 'fecha_fin_votacion'")
    print("  fecha_fin_votacion:", 'OK' if cur.fetchone() else 'NO')

    show_table('candidatos')
    show_table('votos')
    conn.close()
    print("\n✓ Verificación finalizada")

if __name__ == '__main__':
    verificar()