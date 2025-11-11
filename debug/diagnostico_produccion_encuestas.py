import mysql.connector
import json

def get_conn(env='dev'):
    if env == 'prod':
        # TODO: Ajustar credenciales de producción aquí si están disponibles
        cfg = {
            'host': 'localhost',
            'user': 'root',
            'password': '732137A031E4b@',
            'database': 'capired',
            'charset': 'utf8mb4',
        }
    else:
        cfg = {
            'host': 'localhost',
            'user': 'root',
            'password': '732137A031E4b@',
            'database': 'capired',
            'charset': 'utf8mb4',
        }
    return mysql.connector.connect(**cfg)

def listar_triggers(env='dev'):
    conn = get_conn(env)
    cur = conn.cursor(dictionary=True)
    cur.execute("SHOW TRIGGERS")
    triggers = cur.fetchall()
    print(f"=== TRIGGERS ({env}) ===")
    for t in triggers:
        print(json.dumps(t, default=str))
    cur.close()
    conn.close()

def revisar_estructura_encuestas(env='dev'):
    conn = get_conn(env)
    cur = conn.cursor(dictionary=True)
    cur.execute("SHOW CREATE TABLE encuestas")
    res = cur.fetchone()
    print(f"=== ENCUESTAS ({env}) ===")
    print(res['Create Table'] if res and 'Create Table' in res else res)
    cur.close()
    conn.close()

def revisar_respuestas(env='dev', encuesta_id=10):
    conn = get_conn(env)
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS total FROM encuesta_respuestas WHERE encuesta_id = %s", (encuesta_id,))
    print(f"=== RESPUESTAS ({env}) encuesta {encuesta_id} ===", cur.fetchone())
    cur.close()
    conn.close()

def revisar_votos(env='dev', encuesta_id=10):
    conn = get_conn(env)
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT COUNT(*) AS total FROM votos WHERE id_encuesta = %s", (encuesta_id,))
        print(f"=== VOTOS ({env}) encuesta {encuesta_id} ===", cur.fetchone())
    except Exception as e:
        print(f"No existe tabla votos en {env}: {e}")
    cur.close()
    conn.close()

if __name__ == '__main__':
    for env in ('dev','prod'):
        try:
            revisar_estructura_encuestas(env)
            listar_triggers(env)
            revisar_respuestas(env, encuesta_id=10)
            revisar_votos(env, encuesta_id=10)
        except Exception as e:
            print(f"Error en {env}: {e}")