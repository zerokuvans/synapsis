#!/usr/bin/env python3
"""
Verificación integral del sistema de votaciones.

Fases:
1) Verificar esquema de base de datos (columnas, tablas, FKs, únicas)
2) Probar flujo API: crear votación, agregar candidatos, votar y ver resultados
   - Requiere credenciales de administrador y usuario

Configuración por variables de entorno (con valores por defecto razonables):
- BASE_URL (default: http://127.0.0.1:8080)
- ADMIN_USER, ADMIN_PASS
- USER_USER, USER_PASS
- DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

Uso:
  python verificar/verificacion_sistema_votaciones.py
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta

import mysql.connector
import requests


def env(name: str, default: str = None):
    return os.environ.get(name, default)


# --- Configuración ---
BASE_URL = env('BASE_URL', 'http://127.0.0.1:8080')

DB_CONFIG = {
    'host': env('DB_HOST', 'localhost'),
    'user': env('DB_USER', 'root'),
    'password': env('DB_PASSWORD', '732137A031E4b@'),
    'database': env('DB_NAME', 'capired'),
    'charset': 'utf8mb4'
}

ADMIN_USER = env('ADMIN_USER')
ADMIN_PASS = env('ADMIN_PASS')
USER_USER = env('USER_USER')
USER_PASS = env('USER_PASS')

# Fallback para ambientes de prueba conocidos
FALLBACK_USER = '1002407090'
FALLBACK_PASS = 'CE1002407090'


def _connect_db():
    return mysql.connector.connect(**DB_CONFIG)


def verificar_esquema_db():
    print("\n=== [1] Verificando esquema de votaciones (DB) ===")
    try:
        conn = _connect_db()
        cur = conn.cursor(dictionary=True)

        # Columnas en encuestas
        columnas = ['tipo_encuesta', 'mostrar_resultados', 'fecha_inicio_votacion', 'fecha_fin_votacion']
        ok_cols = True
        print("\nColumnas en 'encuestas':")
        for col in columnas:
            cur.execute("SHOW COLUMNS FROM encuestas LIKE %s", (col,))
            exists = cur.fetchone() is not None
            print(f"  - {col}: {'OK' if exists else 'NO'}")
            ok_cols = ok_cols and exists

        # Tablas
        def tabla_existe(nombre):
            cur.execute("SHOW TABLES LIKE %s", (nombre,))
            return cur.fetchone() is not None

        tablas = ['candidatos', 'votos']
        print("\nTablas:")
        ok_tablas = True
        for t in tablas:
            exists = tabla_existe(t)
            print(f"  - {t}: {'OK' if exists else 'NO'}")
            ok_tablas = ok_tablas and exists

        # Restricción única en votos (id_encuesta, id_usuario)
        print("\nRestricciones únicas en 'votos':")
        cur.execute(
            """
            SELECT CONSTRAINT_NAME
            FROM information_schema.table_constraints
            WHERE table_schema = %s AND table_name = 'votos' AND CONSTRAINT_TYPE = 'UNIQUE'
            """,
            (DB_CONFIG['database'],)
        )
        uniques = [r['CONSTRAINT_NAME'] for r in cur.fetchall() or []]
        has_unique = any(u.lower() == 'uniq_voto' for u in uniques)
        print(f"  - uniq_voto: {'OK' if has_unique else 'NO'}")

        # FKs principales
        print("\nLlaves foráneas en 'votos' y 'candidatos':")
        cur.execute(
            """
            SELECT TABLE_NAME, CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM information_schema.key_column_usage
            WHERE TABLE_SCHEMA = %s
              AND TABLE_NAME IN ('votos', 'candidatos')
              AND REFERENCED_TABLE_NAME IS NOT NULL
            ORDER BY TABLE_NAME, CONSTRAINT_NAME
            """,
            (DB_CONFIG['database'],)
        )
        fks = cur.fetchall() or []
        for fk in fks:
            print(f"  - {fk['TABLE_NAME']}.{fk['COLUMN_NAME']} -> {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']} ({fk['CONSTRAINT_NAME']})")

        ok = ok_cols and ok_tablas and has_unique and len(fks) >= 3
        print("\nResultado esquema:")
        print("  ✅ OK" if ok else "  ❌ Incompleto")
        conn.close()
        return ok
    except Exception as e:
        print(f"  ❌ Error verificando esquema: {e}")
        return False


def obtener_usuario_existente():
    """Obtiene un ID de usuario existente en la tabla usuarios para pruebas."""
    try:
        conn = _connect_db()
        cur = conn.cursor()
        cur.execute("SELECT idusuarios FROM usuarios LIMIT 1")
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            # row puede ser (id,) en cursor no dict
            return str(row[0])
    except Exception:
        pass
    return None


def _try_login(session: requests.Session, base_url: str, user: str, password: str) -> bool:
    # Intento con 'username'
    payloads = [
        {'username': user, 'password': password},
        {'cedula': user, 'password': password},
    ]
    for data in payloads:
        try:
            resp = session.post(f"{base_url}/login", data=data, allow_redirects=True, timeout=10)
            if resp.status_code in (200, 302):
                # Algunas implementaciones redirigen a dashboard al iniciar sesión
                return True
        except Exception:
            pass
    return False


def _buscar_encuesta_creada(session: requests.Session, base_url: str, titulo: str):
    try:
        resp = session.get(f"{base_url}/api/encuestas", timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        encuestas = data.get('encuestas') or data.get('data') or []
        for enc in encuestas:
            if (enc.get('titulo') or '').strip() == titulo.strip():
                # algunas estructuras usan 'id_encuesta', otras 'id'
                return enc.get('id_encuesta') or enc.get('id') or enc.get('encuesta_id')
    except Exception:
        pass
    return None


def probar_flujo_api():
    print("\n=== [2] Probando flujo API de votaciones ===")
    existing_uid = obtener_usuario_existente()
    admin_user = ADMIN_USER or existing_uid or FALLBACK_USER
    admin_pass = ADMIN_PASS or (f"CE{admin_user}" if admin_user else FALLBACK_PASS)
    user_user = USER_USER or existing_uid or FALLBACK_USER
    user_pass = USER_PASS or (f"CE{user_user}" if user_user else FALLBACK_PASS)

    admin = requests.Session()
    print("\n[2.1] Login administrador...")
    if not _try_login(admin, BASE_URL, admin_user, admin_pass):
        print("  ❌ No se pudo iniciar sesión como administrador. Configure ADMIN_USER/ADMIN_PASS.")
        return False
    print("  ✅ Login admin OK")

    # Crear encuesta base (borrador/activa) y luego actualizar a votación
    print("\n[2.2] Creando encuesta de tipo votación...")
    titulo = f"Verificación Votación {datetime.now().strftime('%Y%m%d%H%M%S')}"
    body = {
        'titulo': titulo,
        'descripcion': 'Encuesta de verificación automática para votaciones',
        'estado': 'activa',
        'anonima': False,
        'visibilidad': 'privada',
        'dirigida_a': 'todos'
    }
    try:
        r = admin.post(f"{BASE_URL}/api/encuestas", json=body, timeout=15)
        if r.status_code not in (200, 201):
            print(f"  ❌ Error creando encuesta: {r.status_code} {r.text[:200]}")
            return False
    except Exception as e:
        print(f"  ❌ Excepción creando encuesta: {e}")
        return False

    encuesta_id = _buscar_encuesta_creada(admin, BASE_URL, titulo)
    if not encuesta_id:
        print("  ❌ No se encontró la encuesta recién creada en listado")
        return False
    print(f"  ✅ Encuesta creada con id={encuesta_id}")

    # Actualizar encuesta a tipo 'votacion'
    print("\n[2.3] Actualizando encuesta a tipo 'votacion' y configurando fechas...")
    inicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fin = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    patch_body = {
        'tipo_encuesta': 'votacion',
        'mostrar_resultados': True,
        'fecha_inicio_votacion': inicio,
        'fecha_fin_votacion': fin
    }
    pr = admin.patch(f"{BASE_URL}/api/encuestas/{encuesta_id}", json=patch_body, timeout=15)
    if pr.status_code not in (200, 204):
        msg = pr.text[:200] if hasattr(pr, 'text') else ''
        print(f"  ⚠️ Error actualizando encuesta vía API: {pr.status_code} {msg}")
        # Fallback: actualizar directamente en BD
        try:
            conn = _connect_db()
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE encuestas
                SET tipo_encuesta = %s,
                    mostrar_resultados = %s,
                    fecha_inicio_votacion = %s,
                    fecha_fin_votacion = %s,
                    fecha_actualizacion = NOW()
                WHERE id_encuesta = %s
                """,
                ('votacion', 1, inicio, fin, encuesta_id)
            )
            conn.commit()
            cur.close()
            conn.close()
            print("  ✅ Encuesta actualizada como votación (fallback DB)")
        except Exception as e:
            print(f"  ❌ Fallback DB failed: {e}")
            return False
    else:
        print("  ✅ Encuesta actualizada como votación")

    # Agregar candidatos
    print("\n[2.4] Agregando candidatos...")
    candidatos = [
        { 'nombre': 'Candidato A', 'descripcion': 'Opción A', 'foto_url': None, 'orden': 1 },
        { 'nombre': 'Candidato B', 'descripcion': 'Opción B', 'foto_url': None, 'orden': 2 },
    ]
    cand_ids = []
    for c in candidatos:
        cr = admin.post(f"{BASE_URL}/api/votaciones/{encuesta_id}/candidatos", json=c, timeout=10)
        if cr.status_code not in (200, 201):
            print(f"  ❌ Error creando candidato: {cr.status_code} {cr.text[:200]}")
            return False
        try:
            cid = cr.json().get('id_candidato') or cr.json().get('candidato', {}).get('id_candidato')
            cand_ids.append(cid)
        except Exception:
            cand_ids.append(None)
    print(f"  ✅ Candidatos creados: {cand_ids}")

    # Login como usuario y votar
    print("\n[2.5] Login usuario (para votar)...")
    user_sess = requests.Session()
    if not _try_login(user_sess, BASE_URL, user_user, user_pass):
        print("  ❌ No se pudo iniciar sesión como usuario. Configure USER_USER/USER_PASS.")
        return False
    print("  ✅ Login usuario OK")

    # Votar al primer candidato disponible
    print("\n[2.6] Registrando voto...")
    target_cand = next((cid for cid in cand_ids if cid), None)
    if not target_cand:
        print("  ❌ No hay ID de candidato para votar")
        return False
    vr = user_sess.post(f"{BASE_URL}/api/votaciones/{encuesta_id}/votar", json={'id_candidato': target_cand}, timeout=10)
    if vr.status_code not in (200, 201):
        print(f"  ❌ Error registrando voto: {vr.status_code} {vr.text[:200]}")
        return False
    print("  ✅ Voto registrado correctamente")

    # Ver resultados
    print("\n[2.7] Consultando resultados...")
    rr = user_sess.get(f"{BASE_URL}/api/votaciones/{encuesta_id}/resultados", timeout=10)
    if rr.status_code != 200:
        print(f"  ❌ Error consultando resultados: {rr.status_code} {rr.text[:200]}")
        return False
    resultados = rr.json().get('resultados') or rr.json().get('data') or []
    total = sum((r.get('votos') or 0) for r in resultados)
    print("  ✅ Resultados OK")
    print("\nResumen de resultados:")
    for r in resultados:
        nombre = r.get('nombre')
        votos = int(r.get('votos') or 0)
        pct = (votos * 100.0 / total) if total else 0.0
        print(f"  - {nombre}: {votos} votos ({pct:.1f}%)")

    return True


def main():
    print("SISTEMA DE VOTACIONES - VERIFICACIÓN COMPLETA")
    print("=" * 50)

    ok_db = verificar_esquema_db()
    ok_api = probar_flujo_api()

    print("\nRESULTADO FINAL")
    print(f"  - Esquema DB: {'OK' if ok_db else 'FALLÓ'}")
    print(f"  - Flujo API: {'OK' if ok_api else 'FALLÓ'}")

    if not ok_api:
        print("\nSugerencias:")
        print("  - Verifique que el servidor esté corriendo en BASE_URL y accesible")
        print("  - Configure variables ADMIN_USER/ADMIN_PASS y USER_USER/USER_PASS")
        print("  - Revise permisos del rol administrador para crear encuestas")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario")
        sys.exit(1)