import os
import json
import re
from typing import List

import requests
import mysql.connector
from mysql.connector import Error

# Carga de variables desde .env si existe
ENV_PATH = os.path.join(os.getcwd(), '.env')
if os.path.exists(ENV_PATH):
    try:
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except Exception as e:
        print(f"⚠️ No se pudo leer .env: {e}")

BASE_URLS = [
    os.getenv('APP_BASE_URL') or 'http://127.0.0.1:8080',
    'http://192.168.0.77:8080'
]

ENDPOINT = '/api/analistas/codigos'
LOGIN_PATH = '/login'

REQUIRED_COLUMNS = ['tecnologia', 'categoria', 'nombre']


def log(msg: str):
    print(msg, flush=True)


def check_server_running() -> List[str]:
    log("\n== Verificando servidor Flask ==")
    alive = []
    for base in BASE_URLS:
        url = base + LOGIN_PATH
        try:
            resp = requests.get(url, timeout=5, allow_redirects=False)
            log(f"  {base}: status {resp.status_code}, redirect={resp.is_redirect}")
            if resp.status_code in (200, 302):
                alive.append(base)
        except requests.exceptions.RequestException as e:
            log(f"  {base}: sin respuesta ({e})")
    if not alive:
        log("  ❌ Ningún servidor respondió. Inicia main.py en puerto 8080.")
    else:
        log(f"  ✅ Servidores activos: {', '.join(alive)}")
    return alive


def test_api(base_url: str):
    log("\n== Probando endpoint /api/analistas/codigos ==")
    url = base_url + ENDPOINT
    try:
        resp = requests.get(url, timeout=10, allow_redirects=False)
        log(f"  GET {url} -> status {resp.status_code}")
        log(f"  Headers: {dict(resp.headers)}")
        if resp.is_redirect:
            log("  ⚠️ Redirección detectada (posible falta de autenticación).")
            log(f"  Location: {resp.headers.get('Location')}")
        if resp.status_code == 200:
            ct = resp.headers.get('Content-Type','')
            if 'application/json' in ct:
                data = resp.json()
                log(f"  ✅ JSON con {len(data)} registros")
            else:
                log(f"  ❌ Content-Type inesperado: {ct}")
        elif resp.status_code in (401, 403):
            log("  ⚠️ No autenticado o sin permisos. Inicia sesión y reintenta.")
        elif resp.status_code == 500:
            log("  ❌ Error 500 del servidor. Revisar logs.")
        else:
            log(f"  ❌ Status inesperado: {resp.status_code}")
    except requests.exceptions.RequestException as e:
        log(f"  ❌ Error de conexión: {e}")


def get_db_config():
    return {
        'host': os.getenv('MYSQL_HOST'),
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DB'),
        'port': int(os.getenv('MYSQL_PORT') or 3306),
    }


def check_db_connection():
    log("\n== Verificando conexión a MySQL ==")
    cfg = get_db_config()
    try:
        cnx = mysql.connector.connect(**cfg)
        log("  ✅ Conexión establecida")
        return cnx
    except Error as e:
        log(f"  ❌ Error de conexión: {e}")
        return None


def check_table_structure(cnx):
    log("\n== Verificando estructura de base_codigos_facturacion ==")
    try:
        cur = cnx.cursor()
        cur.execute("SHOW COLUMNS FROM base_codigos_facturacion")
        cols = [row[0] for row in cur.fetchall()]
        log(f"  Columnas: {', '.join(cols)}")
        missing = [c for c in REQUIRED_COLUMNS if c not in cols]
        if missing:
            log(f"  ❌ Faltan columnas: {', '.join(missing)}")
        else:
            log("  ✅ Columnas requeridas presentes: tecnologia, categoria, nombre")
        cur.close()
        return cols
    except Error as e:
        log(f"  ❌ Error consultando columnas: {e}")
        return []


def test_sql_queries(cnx):
    log("\n== Probando consultas SQL clave ==")
    queries = [
        (
            "Principal /api/analistas/codigos",
            """
            SELECT 
                 id_base_codigos_facturacion AS idbase_codigos_facturacion,,
                codigo_codigos_facturacion,
                nombre_codigos_facturacion,
                tecnologia,
                instrucciones_de_uso_codigos_facturacion,
                categoria,
                nombre,
                facturable_codigos_facturacion
            FROM base_codigos_facturacion
            ORDER BY codigo_codigos_facturacion ASC
            LIMIT 5
            """
        ),
        (
            "Grupos",
            """
            SELECT DISTINCT nombre
            FROM base_codigos_facturacion
            WHERE nombre IS NOT NULL AND nombre != ''
            ORDER BY nombre ASC
            LIMIT 5
            """
        ),
        (
            "Tecnologias",
            """
            SELECT DISTINCT tecnologia
            FROM base_codigos_facturacion
            WHERE tecnologia IS NOT NULL AND tecnologia != ''
            ORDER BY tecnologia ASC
            LIMIT 5
            """
        ),
        (
            "Agrupaciones",
            """
            SELECT DISTINCT categoria
            FROM base_codigos_facturacion
            WHERE categoria IS NOT NULL AND categoria != ''
            ORDER BY categoria ASC
            LIMIT 5
            """
        ),
    ]
    try:
        cur = cnx.cursor()
        for title, q in queries:
            log(f"  - {title}")
            try:
                cur.execute(q)
                rows = cur.fetchall()
                log(f"    ✅ OK, {len(rows)} filas")
            except Error as e:
                log(f"    ❌ Error SQL: {e}")
                msg = str(e)
                m = re.search(r"Unknown column '([^']+)'", msg)
                if m:
                    log(f"    ➤ Columna faltante detectada: {m.group(1)}")
        cur.close()
    except Error as e:
        log(f"  ❌ Error ejecutando pruebas SQL: {e}")


def main():
    alive = check_server_running()
    base = alive[0] if alive else BASE_URLS[0]
    test_api(base)

    cnx = check_db_connection()
    if cnx:
        cols = check_table_structure(cnx)
        test_sql_queries(cnx)
        try:
            cnx.close()
        except Exception:
            pass

    log("\n== Diagnóstico terminado ==")


if __name__ == '__main__':
    main()