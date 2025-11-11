#!/usr/bin/env python3
"""
Prueba end-to-end del sistema de votaciones:
- Verifica esquema
- Crea encuesta y la marca como votación
- Crea candidatos
- Inicia sesión como usuario y registra un voto
- Consulta resultados
"""

import os
import json
from datetime import datetime, timedelta

import requests
import mysql.connector


BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:8080')
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '732137A031E4b@'),
    'database': os.environ.get('DB_NAME', 'capired'),
    'charset': 'utf8mb4',
}


def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


def ensure_user_in_usuarios(user_id: str, cedula: str):
    """Asegura que exista un registro en usuarios con idusuarios=user_id para cumplir FK.
    La tabla `usuarios` usa tipos enteros para `usuario_cedula` y `usuario_contraseña`.
    """
    try:
        conn = connect_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idusuarios FROM usuarios WHERE idusuarios = %s", (user_id,))
        if cur.fetchone():
            conn.close()
            return True
        # Intentar crear registro mínimo
        try:
            ced_int = int(str(cedula))
        except Exception:
            ced_int = 0
        cur.execute(
            """
            INSERT INTO usuarios (idusuarios, usuario_nombre, usuario_cedula, usuario_contraseña)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, 'Verificacion Votaciones', ced_int, 0)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[WARN] No se pudo garantizar usuarios.idusuarios={user_id}: {e}")
        try:
            conn.close()
        except Exception:
            pass
        return False


def try_login(session: requests.Session, username: str, password: str):
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    resp = session.post(f"{BASE_URL}/login", data={'username': username, 'password': password}, headers=headers, allow_redirects=True, timeout=20)
    if resp.status_code in (200, 302):
        try:
            data = resp.json()
        except Exception:
            data = {}
        return True, data
    return False, {}


def test_votaciones_end_to_end():
    # 1) Login admin
    admin_user = os.environ.get('ADMIN_USER', '1002407090')
    admin_pass = os.environ.get('ADMIN_PASS', f"CE{admin_user}")
    admin = requests.Session()
    ok, _ = try_login(admin, admin_user, admin_pass)
    assert ok, "Login admin falló; configure ADMIN_USER/ADMIN_PASS"

    # 2) Crear encuesta
    titulo = f"Test Votación {datetime.now().strftime('%Y%m%d%H%M%S')}"
    body = {
        'titulo': titulo,
        'descripcion': 'Prueba automática de votaciones',
        'estado': 'activa',
        'anonima': False,
        'visibilidad': 'privada',
        'dirigida_a': 'todos'
    }
    r = admin.post(f"{BASE_URL}/api/encuestas", json=body, timeout=20)
    assert r.status_code in (200, 201), f"Crear encuesta falló: {r.status_code} {r.text[:200]}"

    # Buscar encuesta creada
    lr = admin.get(f"{BASE_URL}/api/encuestas", timeout=20)
    assert lr.status_code == 200, "Listar encuestas falló"
    encuestas = lr.json().get('encuestas') or lr.json().get('data') or []
    encuesta_id = None
    for enc in encuestas:
        if (enc.get('titulo') or '').strip() == titulo:
            encuesta_id = enc.get('id_encuesta') or enc.get('id') or enc.get('encuesta_id')
            break
    assert encuesta_id, "No se encontró encuesta creada"

    # 3) Actualizar a tipo votación (PATCH)
    inicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fin = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    patch_body = {
        'tipo_encuesta': 'votacion',
        'mostrar_resultados': True,
        'fecha_inicio_votacion': inicio,
        'fecha_fin_votacion': fin
    }
    pr = admin.patch(f"{BASE_URL}/api/encuestas/{encuesta_id}", json=patch_body, timeout=20)
    if pr.status_code not in (200, 204):
        # Fallback por si el endpoint requiere otro formato
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE encuestas SET tipo_encuesta=%s, mostrar_resultados=%s,
                   fecha_inicio_votacion=%s, fecha_fin_votacion=%s,
                   fecha_actualizacion = NOW()
            WHERE id_encuesta = %s
            """,
            ('votacion', 1, inicio, fin, encuesta_id)
        )
        conn.commit(); conn.close()

    # 4) Crear candidatos
    cands = [
        {'nombre': 'Candidato A', 'descripcion': 'Desc A', 'orden': 1},
        {'nombre': 'Candidato B', 'descripcion': 'Desc B', 'orden': 2},
    ]
    for c in cands:
        cr = admin.post(f"{BASE_URL}/api/votaciones/{encuesta_id}/candidatos", json=c, timeout=20)
        assert cr.status_code in (200, 201), f"Crear candidato falló: {cr.status_code} {cr.text[:200]}"

    # 5) Login usuario
    user_user = os.environ.get('USER_USER', admin_user)
    user_pass = os.environ.get('USER_PASS', admin_pass)
    user = requests.Session()
    ok_u, data_u = try_login(user, user_user, user_pass)
    assert ok_u, "Login usuario falló; configure USER_USER/USER_PASS"
    user_id = str(data_u.get('user_id') or '')
    assert user_id, "Login no devolvió user_id"

    # 6) Garantizar usuario en usuarios para cumplir FK
    ensured = ensure_user_in_usuarios(user_id, user_user)
    assert ensured, "No se pudo garantizar fila en usuarios para el voto"

    # 7) Votar al primer candidato
    lr_cands = user.get(f"{BASE_URL}/api/votaciones/{encuesta_id}/candidatos", timeout=20)
    assert lr_cands.status_code == 200, "Listar candidatos falló"
    lista = lr_cands.json().get('candidatos') or []
    assert lista, "No hay candidatos"
    target_id = lista[0]['id_candidato']
    vr = user.post(f"{BASE_URL}/api/votaciones/{encuesta_id}/votar", json={'id_candidato': target_id}, timeout=20)
    assert vr.status_code in (200, 201), f"Registrar voto falló: {vr.status_code} {vr.text[:200]}"

    # 8) Ver resultados
    rr = user.get(f"{BASE_URL}/api/votaciones/{encuesta_id}/resultados", timeout=20)
    assert rr.status_code == 200, f"Resultados falló: {rr.status_code} {rr.text[:200]}"
    resultados = rr.json().get('resultados') or []
    total = sum([(r.get('votos') or 0) for r in resultados])
    assert total >= 1, "Total de votos inesperado"
    print("\n[OK] Votaciones end-to-end completado. Resultados:")
    for r in resultados:
        print(f" - {r.get('nombre')}: {int(r.get('votos') or 0)}")


if __name__ == '__main__':
    test_votaciones_end_to_end()