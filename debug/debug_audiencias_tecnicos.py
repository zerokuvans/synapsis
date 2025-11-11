import sys
import json
import mysql.connector
from datetime import datetime


DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4'
}


def conn():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"❌ Error conectando a DB: {e}")
        return None


def get_usuario_info(c, uid):
    cur = c.cursor(dictionary=True)
    cur.execute("SELECT id_codigo_consumidor, nombre, carpeta, super, id_roles, cargo, analista, estado FROM recurso_operativo WHERE id_codigo_consumidor = %s", (uid,))
    return cur.fetchone()


def listar_encuestas_tecnicos(c):
    cur = c.cursor(dictionary=True)
    cur.execute(
        """
        SELECT id_encuesta, titulo, dirigida_a, audiencia_carpetas, audiencia_supervisores, audiencia_tecnicos,
               estado, tipo_encuesta, fecha_inicio, fecha_fin
        FROM encuestas
        WHERE estado = 'activa' AND LOWER(dirigida_a) IN ('tecnico','tecnicos')
        ORDER BY fecha_inicio ASC, id_encuesta ASC
        """
    )
    return cur.fetchall() or []


def parse_list(val):
    if not val:
        return []
    if isinstance(val, list):
        return val
    try:
        return json.loads(val) or []
    except Exception:
        return []


def eval_encuesta_para_usuario(enc, u):
    dirigida = (enc.get('dirigida_a') or '').strip().lower()
    if dirigida in ('tecnico', 'técnico'):
        dirigida = 'tecnicos'

    if dirigida != 'tecnicos':
        return True, 'no_tecnicos'

    carpeta = (u.get('carpeta') or '').strip().lower()
    superv = (u.get('super') or '').strip().lower()
    uid = str(u.get('id_codigo_consumidor'))

    carps = [str(x).strip().lower() for x in parse_list(enc.get('audiencia_carpetas'))]
    sups = [str(x).strip().lower() for x in parse_list(enc.get('audiencia_supervisores'))]
    tecs = [str(x).strip() for x in parse_list(enc.get('audiencia_tecnicos'))]

    # Fechas
    ahora = datetime.now()
    fi = enc.get('fecha_inicio')
    ff = enc.get('fecha_fin')
    dentro_ventana = True
    try:
        if fi:
            fi_dt = fi if isinstance(fi, datetime) else datetime.strptime(str(fi), '%Y-%m-%d %H:%M:%S')
            if fi_dt > ahora:
                dentro_ventana = False
        if ff:
            ff_dt = ff if isinstance(ff, datetime) else datetime.strptime(str(ff), '%Y-%m-%d %H:%M:%S')
            if ff_dt < ahora:
                dentro_ventana = False
    except Exception:
        pass
    if not dentro_ventana:
        return False, 'fuera_de_ventana'

    # Técnicos explícitos
    if len(tecs) > 0 and uid not in set(tecs):
        return False, 'no_en_lista_tecnicos'

    # Supervisores explícitos
    if len(sups) > 0 and superv not in set(sups):
        return False, 'supervisor_no_match'

    # Carpetas explícitas
    if len(carps) > 0 and carpeta not in set(carps):
        return False, 'carpeta_no_match'

    return True, 'ok'


def main():
    if len(sys.argv) < 2:
        print("Uso: python debug_audiencias_tecnicos.py <id_usuario_1> [<id_usuario_2> ...]")
        sys.exit(1)
    ids = [int(x) for x in sys.argv[1:]]
    c = conn()
    if not c:
        return
    encuestas = listar_encuestas_tecnicos(c)
    print(f"📋 Encuestas activas para técnicos: {len(encuestas)}")
    for uid in ids:
        u = get_usuario_info(c, uid)
        if not u:
            print(f"— Usuario {uid} no encontrado")
            continue
        print(f"\n=== Usuario {uid}: {u.get('nombre')} • carpeta='{u.get('carpeta')}' • super='{u.get('super')}' ===")
        for e in encuestas:
            ok, motivo = eval_encuesta_para_usuario(e, u)
            print(f"  - Encuesta {e['id_encuesta']} '{e['titulo']}': {'INCLUIDA' if ok else 'EXCLUIDA'} ({motivo})")

    c.close()


if __name__ == '__main__':
    main()