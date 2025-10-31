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

def list_active_surveys():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT id_encuesta, titulo, descripcion, estado, dirigida_a, audiencia_carpetas,
               fecha_inicio, fecha_fin
        FROM encuestas
        WHERE estado = 'activa'
          AND (fecha_inicio IS NULL OR fecha_inicio <= NOW())
          AND (fecha_fin IS NULL OR fecha_fin >= NOW())
        ORDER BY id_encuesta DESC
        """
    )
    rows = cur.fetchall()
    print(f"Total encuestas activas: {len(rows)}")
    for r in rows:
        aud = r.get('audiencia_carpetas')
        try:
            aud_list = json.loads(aud) if aud else None
        except Exception:
            aud_list = None
        print(f"- #{r['id_encuesta']} '{r['titulo']}' dirigida_a={r['dirigida_a']} carpetas={aud_list}")
    cur.close()
    conn.close()

def simulate_filter_for_user(user_id=11):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT carpeta, id_roles FROM recurso_operativo WHERE id_codigo_consumidor = %s", (user_id,))
    u = cur.fetchone() or {}
    carpeta_usuario = (u.get('carpeta') or '').strip()
    print(f"Usuario {user_id} carpeta='{carpeta_usuario}' rol={u.get('id_roles')}")
    cur.execute(
        """
        SELECT id_encuesta, titulo, dirigida_a, audiencia_carpetas
        FROM encuestas
        WHERE estado = 'activa'
          AND (fecha_inicio IS NULL OR fecha_inicio <= NOW())
          AND (fecha_fin IS NULL OR fecha_fin >= NOW())
          AND dirigida_a IN ('todos','tecnicos','analistas','supervisores')
        ORDER BY id_encuesta DESC
        """
    )
    rows = cur.fetchall() or []
    visibles = []
    for enc in rows:
        if enc.get('dirigida_a') == 'tecnicos' and enc.get('audiencia_carpetas'):
            try:
                lista = json.loads(enc.get('audiencia_carpetas'))
            except Exception:
                lista = None
            if not carpeta_usuario:
                continue
            if isinstance(lista, list) and any(carpeta_usuario.lower() == (c or '').strip().lower() for c in lista):
                visibles.append(enc)
        else:
            visibles.append(enc)
    print(f"Encuestas visibles para usuario {user_id}: {len(visibles)}")
    for v in visibles:
        print(f"  -> #{v['id_encuesta']} '{v['titulo']}' dirigida_a={v['dirigida_a']}")
    cur.close()
    conn.close()

if __name__ == '__main__':
    list_active_surveys()
    simulate_filter_for_user(11)