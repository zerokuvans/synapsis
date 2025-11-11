import mysql.connector
import json
import sys

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
}

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def show_encuesta(encuesta_id=10):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT id_encuesta, titulo, descripcion, estado, tipo_encuesta,
               dirigida_a, audiencia_carpetas, audiencia_supervisores, audiencia_tecnicos,
               fecha_inicio, fecha_fin, creado_por
        FROM encuestas
        WHERE id_encuesta = %s
        """,
        (encuesta_id,)
    )
    enc = cur.fetchone()
    print("=== ENCUESTA ===")
    print(json.dumps(enc, default=str, indent=2))
    cur.close()
    conn.close()

def _resolver_audiencias_usuario(conn, user_id):
    """Replica la lógica de encuestas_api._resolver_audiencias_usuario"""
    auds = set()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT id_roles, UPPER(COALESCE(cargo, '')) AS cargo, 
               COALESCE(super, 0) AS es_supervisor, COALESCE(analista, 0) AS es_analista
        FROM recurso_operativo
        WHERE id_codigo_consumidor = %s
        """,
        (user_id,)
    )
    row = cur.fetchone() or {}
    # Técnicos por id_roles == 2
    if row.get('id_roles') == 2:
        auds.add('tecnicos')
    cargo = (row.get('cargo') or '').upper()
    if row.get('es_analista') in (1, True) or 'ANALISTA' in cargo:
        auds.add('analistas')
    if row.get('es_supervisor') in (1, True) or 'SUPERVIS' in cargo:
        auds.add('supervisores')
    cur.close()
    # Siempre se incluye 'todos'
    return ['todos'] + list(auds)

def simulate_endpoint_for_user(encuesta_id=10, user_id=11):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    reasons = []

    # Cargar encuesta y usuario
    cur.execute("SELECT * FROM encuestas WHERE id_encuesta = %s", (encuesta_id,))
    e = cur.fetchone() or {}
    cur.execute("SELECT id_codigo_consumidor, carpeta, super, id_roles, nombre FROM recurso_operativo WHERE id_codigo_consumidor = %s", (user_id,))
    u = cur.fetchone() or {}

    # Ventana activa
    cur.execute(
        """
        SELECT (
            (e.estado = 'activa') AND
            (e.fecha_inicio IS NULL OR e.fecha_inicio <= NOW()) AND
            (e.fecha_fin IS NULL OR e.fecha_fin >= NOW())
        ) AS activa_y_en_ventana
        FROM encuestas e WHERE e.id_encuesta = %s
        """,
        (encuesta_id,)
    )
    ventana = (cur.fetchone() or {}).get('activa_y_en_ventana')
    if not ventana:
        reasons.append('fuera_de_ventana_o_no_activa')

    dirigida_a = (e.get('dirigida_a') or 'todos')
    valores = _resolver_audiencias_usuario(conn, user_id)
    if dirigida_a not in valores:
        reasons.append(f'dirigida_a_no_coincide:{dirigida_a} no en {valores}')

    tipo = (e.get('tipo_encuesta') or 'encuesta')
    if tipo == 'votacion':
        cur.execute("SELECT COUNT(*) AS total FROM votos WHERE id_encuesta = %s AND id_usuario = %s", (encuesta_id, user_id))
        if (cur.fetchone() or {}).get('total', 0) > 0:
            reasons.append('ya_voto')
    else:
        cur.execute("SELECT COUNT(*) AS total FROM encuesta_respuestas WHERE encuesta_id = %s AND usuario_id = %s AND estado = 'enviada'", (encuesta_id, user_id))
        if (cur.fetchone() or {}).get('total', 0) > 0:
            reasons.append('ya_respondio')

    # Filtros finos para tecnicos en client-side del endpoint
    carpeta_usuario = (u.get('carpeta') or '').strip()
    super_usuario = (u.get('super') or '').strip()
    # Carpetas
    try:
        aud_carpetas = json.loads(e.get('audiencia_carpetas') or 'null')
    except Exception:
        aud_carpetas = None
    if dirigida_a == 'tecnicos' and isinstance(aud_carpetas, list) and aud_carpetas:
        if not any((carpeta_usuario or '').lower() == (c or '').strip().lower() for c in aud_carpetas):
            reasons.append('carpeta_no_permitida')
    # Supervisores
    try:
        aud_super = json.loads(e.get('audiencia_supervisores') or 'null')
    except Exception:
        aud_super = None
    if dirigida_a == 'tecnicos' and isinstance(aud_super, list) and aud_super:
        if not any((super_usuario or '').lower() == (s or '').strip().lower() for s in aud_super):
            reasons.append('supervisor_no_permitido')
    # Tecnicos específicos
    try:
        aud_tecnicos = json.loads(e.get('audiencia_tecnicos') or 'null')
    except Exception:
        aud_tecnicos = None
    if dirigida_a == 'tecnicos' and isinstance(aud_tecnicos, list) and aud_tecnicos:
        if str(user_id) not in set(str(t) for t in aud_tecnicos):
            reasons.append('usuario_no_listado_en_tecnicos')

    endpoint_incluir = (len(reasons) == 0)
    print(f"\n=== Usuario {user_id} ===")
    print(json.dumps({'usuario': u, 'encuesta': {
        'id_encuesta': e.get('id_encuesta'),
        'tipo_encuesta': tipo,
        'estado': e.get('estado'),
        'dirigida_a': dirigida_a,
        'audiencia_carpetas': e.get('audiencia_carpetas'),
        'audiencia_supervisores': e.get('audiencia_supervisores'),
        'audiencia_tecnicos': e.get('audiencia_tecnicos'),
        'fecha_inicio': e.get('fecha_inicio'),
        'fecha_fin': e.get('fecha_fin'),
    }, 'audiencias_usuario': valores}, default=str, indent=2))
    print("Razones de exclusión:", reasons if reasons else 'ninguna')
    print("Endpoint incluiría:", endpoint_incluir)

    cur.close()
    conn.close()
    return endpoint_incluir, reasons

if __name__ == '__main__':
    show_encuesta(10)
    # Permitir pasar usuarios por argumentos: python debug_encuesta_10.py 11 71 89
    users = [11, 71]
    if len(sys.argv) > 1:
        users = [int(a) for a in sys.argv[1:]]
    for uid in users:
        simulate_endpoint_for_user(encuesta_id=10, user_id=uid)