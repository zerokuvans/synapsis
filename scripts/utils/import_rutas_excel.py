#!/usr/bin/env python3
import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

def get_db_config():
    load_dotenv()
    return {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', '732137A031E4b@'),
        'database': os.getenv('MYSQL_DB', 'capired'),
        'port': int(os.getenv('MYSQL_PORT', 3306))
    }

def ensure_table(conn):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS mpa_rutas_tecnicos (
            id_ruta INT AUTO_INCREMENT PRIMARY KEY,
            cedula VARCHAR(32),
            nombre VARCHAR(255),
            lat_inicio DECIMAL(9,6),
            lon_inicio DECIMAL(9,6),
            lat_fin DECIMAL(9,6),
            lon_fin DECIMAL(9,6),
            fecha DATE NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )
    conn.commit()
    cur.close()

def main():
    try:
        import pandas as pd
    except Exception:
        print('ERROR: Falta dependencia pandas. Instala con pip install pandas.', file=sys.stderr)
        sys.exit(1)

    file_path = os.path.join(os.getcwd(), 'excel', 'DTA.xlsx')
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f'ERROR: No se encontró el archivo: {file_path}', file=sys.stderr)
        sys.exit(1)

    cfg = get_db_config()
    conn = mysql.connector.connect(**cfg)
    ensure_table(conn)

    df = pd.read_excel(file_path)
    df.columns = [str(c).strip() for c in df.columns]
    df.rename(columns={
        'Coordenada X Inicio': 'lat_inicio',
        'Coordenada Y Inicio': 'lon_inicio',
        'Coordenada X Fin': 'lat_fin',
        'Coordenada Y Fin': 'lon_fin',
        'Nombre': 'nombre'
    }, inplace=True)

    required = ['cedula', 'nombre', 'lat_inicio', 'lon_inicio', 'lat_fin', 'lon_fin']
    missing = [c for c in required if c not in df.columns]
    if missing:
        print('ERROR: Columnas faltantes: ' + ', '.join(missing), file=sys.stderr)
        sys.exit(1)

    def fix_num(x):
        s = str(x).strip().replace('..', '.')
        try:
            v = float(s)
        except Exception:
            return None
        return v

    for c in ['lat_inicio', 'lon_inicio', 'lat_fin', 'lon_fin']:
        df[c] = df[c].apply(fix_num)

    def in_range(lat, lon):
        return lat is not None and lon is not None and (-90 <= lat <= 90) and (-180 <= lon <= 180)

    df = df[[
        in_range(row['lat_inicio'], row['lon_inicio']) and in_range(row['lat_fin'], row['lon_fin'])
        for _, row in df.iterrows()
    ]]

    rows = []
    for _, r in df.iterrows():
        rows.append((
            str(r['cedula']).strip(),
            str(r['nombre']).strip(),
            float(r['lat_inicio']),
            float(r['lon_inicio']),
            float(r['lat_fin']),
            float(r['lon_fin'])
        ))

    cur = conn.cursor()
    cur.executemany(
        """
        INSERT INTO mpa_rutas_tecnicos (cedula, nombre, lat_inicio, lon_inicio, lat_fin, lon_fin)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        rows
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f'OK: Inserciones realizadas: {len(rows)}')

if __name__ == '__main__':
    main()