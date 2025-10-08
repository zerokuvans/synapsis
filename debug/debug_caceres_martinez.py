import sys
import os
from datetime import datetime
import unicodedata

# Asegura que el proyecto raíz esté en sys.path para importar main
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

try:
    from main import get_db_connection
except Exception as e:
    print("[ERROR] No pude importar get_db_connection desde main:", e)
    get_db_connection = None


def strip_accents(s: str) -> str:
    if s is None:
        return ''
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def norm(s: str) -> str:
    return strip_accents((s or '').strip()).lower()


def debug_usuario_y_asistencia(cedula_objetivo: str, nombre_sesion_esperado: str = None):
    print("=== Debug Indicadores Operaciones: Usuario y Asistencia ===")
    print(f"Cedula objetivo: {cedula_objetivo}")
    if nombre_sesion_esperado:
        print(f"Nombre esperado en sesión: {nombre_sesion_esperado}")
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    print(f"Fecha de hoy: {fecha_hoy}")

    if get_db_connection is None:
        print("[FATAL] No hay función de conexión disponible. Verifique que main.py sea importable.")
        return

    conn = get_db_connection()
    if conn is None:
        print("[FATAL] No se pudo conectar a la base de datos.")
        return

    cur = conn.cursor(dictionary=True)

    # 1) Intentar obtener nombre exacto desde 'usuarios' (si existe)
    nombre_db = None
    try:
        cur.execute(
            """
            SELECT nombre, usuario, rol
            FROM usuarios
            WHERE cedula = %s
            LIMIT 1
            """,
            (cedula_objetivo,)
        )
        u = cur.fetchone()
        if u:
            nombre_db = u.get('nombre') or u.get('usuario')
            print(f"Usuario en 'usuarios': nombre='{u.get('nombre')}', usuario='{u.get('usuario')}', rol='{u.get('rol')}'")
        else:
            print("No se encontró el usuario en tabla 'usuarios'.")
    except Exception as e:
        print("[WARN] No pude consultar tabla 'usuarios':", e)

    # 2) Listar asistencias de hoy por cedula
    try:
        cur.execute(
            """
            SELECT cedula, super, fecha_asistencia
            FROM asistencia
            WHERE DATE(fecha_asistencia) = %s AND cedula = %s
            ORDER BY fecha_asistencia ASC
            """,
            (fecha_hoy, cedula_objetivo)
        )
        asistencias_cedula = cur.fetchall() or []
        print(f"Asistencias de hoy por cedula={cedula_objetivo}: {len(asistencias_cedula)}")
        for a in asistencias_cedula:
            print(f" - cedula={a['cedula']} | super='{a['super']}' | fecha={a['fecha_asistencia']}")
    except Exception as e:
        print("[ERROR] Consultando asistencias por cedula:", e)
        asistencias_cedula = []

    # 3) Si tenemos nombre_db, verificar coincidencia EXACTA por 'super'
    cnt_exact = 0
    if nombre_db:
        try:
            cur.execute(
                """
                SELECT COUNT(*) AS cnt
                FROM asistencia
                WHERE DATE(fecha_asistencia) = %s AND super = %s
                """,
                (fecha_hoy, nombre_db)
            )
            cnt_exact = (cur.fetchone() or {}).get('cnt', 0)
            print(f"Coincidencias EXACTAS hoy por super='{nombre_db}': {cnt_exact}")
        except Exception as e:
            print("[ERROR] Consultando coincidencia exacta por nombre_db:", e)

    # 4) Comparación normalizada (sin acentos y minúsculas) entre 'super' y nombre_db / nombre_sesion_esperado
    normalized_target_db = norm(nombre_db) if nombre_db else None
    normalized_target_session = norm(nombre_sesion_esperado) if nombre_sesion_esperado else None

    try:
        cur.execute(
            """
            SELECT super, fecha_asistencia
            FROM asistencia
            WHERE DATE(fecha_asistencia) = %s
            """,
            (fecha_hoy,)
        )
        filas_hoy = cur.fetchall() or []
        print(f"Total asistencias hoy (todas): {len(filas_hoy)}")
        for i, f in enumerate(filas_hoy[:10]):
            print(f" * {i+1:02d} super='{f['super']}' | fecha={f['fecha_asistencia']}")

        if normalized_target_db:
            normalized_matches_db = [f for f in filas_hoy if norm(f['super']) == normalized_target_db]
            print(f"Coincidencias NORMALIZADAS con nombre_db='{nombre_db}': {len(normalized_matches_db)}")
            for m in normalized_matches_db[:10]:
                print(f"   - match super='{m['super']}' | fecha={m['fecha_asistencia']}")

        if normalized_target_session:
            normalized_matches_session = [f for f in filas_hoy if norm(f['super']) == normalized_target_session]
            print(f"Coincidencias NORMALIZADAS con nombre_sesion='{nombre_sesion_esperado}': {len(normalized_matches_session)}")
            for m in normalized_matches_session[:10]:
                print(f"   - match super='{m['super']}' | fecha={m['fecha_asistencia']}")
    except Exception as e:
        print("[ERROR] Listando asistencias de hoy:", e)

    print("\n=== Diagnóstico ===")
    if cnt_exact > 0:
        print("- Hay coincidencias EXACTAS por 'super' con el nombre de BD. Si la sesión usa exactamente ese nombre, el botón debería aparecer activo.")
    elif asistencias_cedula:
        print("- Hay asistencias por cédula pero no coinciden por 'super'. Asegure que 'session[\"user_name\"]' sea exactamente el valor guardado en 'asistencia.super'.")
    else:
        print("- No se encontraron asistencias registradas hoy para este usuario.")

    print("\n=== Recomendaciones ===")
    print("1) Verifique cuál es el valor exacto de 'session[\"user_name\"]' en ejecución.")
    print("2) Asegure que el campo 'super' en 'asistencia' coincida EXACTAMENTE con ese valor (mismo texto, acentos, mayúsculas y espacios).")
    print("3) Ya hay fallback sin acentos/minúsculas en main.py; si aún bloquea, el valor de sesión podría diferir más (p. ej., espacios adicionales).")

    cur.close()
    conn.close()


if __name__ == '__main__':
    # Parámetros: cedula y opcionalmente nombre_sesion_esperado
    cedula = '1032402333'
    nombre_sesion = 'CACERES MARTINEZ CARLOS'  # Ajusta si conoces el valor exacto de sesión
    if len(sys.argv) > 1:
        cedula = sys.argv[1]
    if len(sys.argv) > 2:
        nombre_sesion = sys.argv[2]
    debug_usuario_y_asistencia(cedula, nombre_sesion)