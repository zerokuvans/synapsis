import sys
from datetime import datetime
import unicodedata

try:
    from main import get_db_connection
except Exception as e:
    print("No pude importar get_db_connection desde main:", e)
    get_db_connection = None


def strip_accents(s: str) -> str:
    if s is None:
        return ''
    # Normaliza y quita diacríticos para comparar sin acentos
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def check_asistencia_for_name(nombre_super: str):
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    print(f"Fecha de hoy: {fecha_hoy}")
    print(f"Nombre a verificar (exacto): '{nombre_super}'")

    if get_db_connection is None:
        print("ERROR: No hay función de conexión disponible. Verifique main.py.")
        return

    conn = get_db_connection()
    if conn is None:
        print("ERROR: No se pudo conectar a la base de datos.")
        return

    cur = conn.cursor(dictionary=True)

    # Lista general de asistencias de hoy (para diagnóstico visual)
    cur.execute(
        """
        SELECT super, fecha_asistencia
        FROM asistencia
        WHERE DATE(fecha_asistencia) = %s
        ORDER BY fecha_asistencia ASC
        """,
        (fecha_hoy,)
    )
    filas = cur.fetchall()
    print(f"Total asistencias hoy: {len(filas)}")
    if filas:
        print("Asistencias de hoy (super | fecha_asistencia):")
        for f in filas:
            print(f" - {f['super']} | {f['fecha_asistencia']}")
    else:
        print("No hay asistencias registradas hoy.")

    # Chequeo exacto del nombre
    cur.execute(
        """
        SELECT COUNT(*) AS cnt
        FROM asistencia
        WHERE super = %s AND DATE(fecha_asistencia) = %s
        """,
        (nombre_super, fecha_hoy)
    )
    cnt_exact = (cur.fetchone() or {}).get('cnt', 0)
    print(f"Coincidencias EXACTAS para '{nombre_super}': {cnt_exact}")

    # Variaciones comunes del nombre (sin acentos y mayúsculas/minúsculas)
    base = nombre_super
    variations = {
        'original': base,
        'sin_acentos': strip_accents(base),
        'mayusculas': base.upper(),
        'minusculas': base.lower(),
        'sin_acentos_mayusculas': strip_accents(base).upper(),
        'sin_acentos_minusculas': strip_accents(base).lower(),
    }

    # Búsqueda flexible (contiene), útil para detectar espacios adicionales o complementos (p.ej. "SUPERVISOR CÁCERES")
    for tag, name in variations.items():
        cur.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM asistencia
            WHERE DATE(fecha_asistencia) = %s AND super LIKE %s
            """,
            (fecha_hoy, f"%{name}%")
        )
        cnt_like = (cur.fetchone() or {}).get('cnt', 0)
        print(f"Coincidencias LIKE para [{tag}]='{name}': {cnt_like}")

    # Análisis de normalización: comprueba si hay registros que normalizados coincidan
    normalized_target = strip_accents(nombre_super).lower()
    normalized_matches = [
        f for f in filas
        if strip_accents(f['super']).lower() == normalized_target
    ]
    print(f"Coincidencias normalizadas (sin acentos y en minúsculas) para '{nombre_super}': {len(normalized_matches)}")
    if normalized_matches:
        for f in normalized_matches:
            print(f" * match normalizado: {f['super']} | {f['fecha_asistencia']}")

    # Conclusión y recomendación
    print("\nDiagnóstico:")
    if cnt_exact > 0:
        print(" - Hay al menos una coincidencia EXACTA. El botón debería estar activo si la sesión usa exactamente ese 'super'.")
    elif normalized_matches:
        print(" - Existen asistencias que coinciden al normalizar acentos/caso, pero no exactamente. Posible desalineación entre 'session[\"user_name\"]' y el valor almacenado en 'asistencia.super'.")
    else:
        print(" - No se encontraron asistencias que coincidan con el nombre proporcionado hoy.")

    print("\nSugerencias:")
    print(" - Verifique que 'session[\"user_name\"]' coincide EXACTAMENTE con el campo 'super' en la tabla asistencia.")
    print(" - Si la diferencia es por acentos o mayúsculas, puede ajustarse la consulta en main.py para usar una comparación insensible a acentos/caso (p.ej., colación adecuada o normalización en aplicación).")
    print(" - Alternativamente, registre asistencia hoy usando exactamente el mismo nombre que aparece en la sesión.")

    cur.close()
    conn.close()


if __name__ == '__main__':
    # Permite pasar el nombre por argumento; por defecto usa 'Cáceres'
    nombre = 'Cáceres'
    if len(sys.argv) > 1:
        nombre = sys.argv[1]
    check_asistencia_for_name(nombre)