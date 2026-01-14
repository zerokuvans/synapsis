import os
import sys
import mysql.connector
from datetime import datetime, date

def get_db_connection():
    try:
        host = os.getenv('MYSQL_HOST') or 'localhost'
        user = os.getenv('MYSQL_USER') or 'root'
        password = os.getenv('MYSQL_PASSWORD') or '732137A031E4b@'
        database = os.getenv('MYSQL_DB') or os.getenv('MYSQL_DATABASE') or 'capired'
        port_val = os.getenv('MYSQL_PORT')
        if port_val:
            connection = mysql.connector.connect(host=host, user=user, password=password, database=database, port=int(port_val))
        else:
            connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        return connection
    except mysql.connector.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def n(v):
    try:
        return int(v or 0)
    except Exception:
        return 0

def s(v):
    try:
        return str(v or '').strip()
    except Exception:
        return ''

def compute_malos(row):
    bm_fields = [
        'estado_fisico_espejos_laterales','estado_fisico_pito','estado_fisico_freno_servicio','estado_fisico_manillares','estado_fisico_guayas','estado_fisico_tanque_combustible','estado_fisico_encendido','estado_fisico_pedales','estado_fisico_guardabarros','estado_fisico_sillin_tapiceria','estado_fisico_tablero','estado_fisico_mofle_silenciador','estado_fisico_kit_arrastre','estado_fisico_reposa_pies','estado_fisico_pata_lateral_central','estado_fisico_tijera_amortiguador','estado_fisico_bateria','luces_altas_bajas','luces_direccionales_delanteros','luces_direccionales_traseros','luces_luz_placa','luces_stop','prevension_casco','prevension_guantes','prevension_rodilleras','prevension_coderas','llantas_labrado_llantas','llantas_rines','llantas_presion_aire','otros_aceite','otros_suspension_direccion','otros_caja_cambios','otros_conexiones_electricas'
    ]
    bm_synonyms = {
        'prevension_casco': ['prevencion_casco'],
        'prevension_guantes': ['prevencion_guantes'],
        'prevension_rodilleras': ['prevencion_rodilleras'],
        'prevension_coderas': ['prevencion_coderas']
    }
    malos = 0
    for k in bm_fields:
        v = row.get(k)
        if v is None and k in bm_synonyms:
            for alt in bm_synonyms[k]:
                if row.get(alt) is not None:
                    v = row.get(alt)
                    break
        if s(v).upper() in ('M','MALO'):
            malos += 1
    return malos

def compute_dias_restantes(fi):
    fi_date = None
    if fi:
        try:
            fi_date = fi.date() if hasattr(fi, 'date') else datetime.strptime(str(fi)[:19], '%Y-%m-%d %H:%M:%S').date()
        except Exception:
            try:
                fi_date = datetime.strptime(str(fi)[:10], '%Y-%m-%d').date()
            except Exception:
                fi_date = None
    if not fi_date:
        return None
    try:
        hoy = date.today()
        trans = (hoy - fi_date).days
        d = 5 - trans
        return d if d > 0 else 0
    except Exception:
        return None

def main():
    conn = get_db_connection()
    if not conn:
        print('Error de conexión a la base de datos')
        sys.exit(1)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT *
        FROM mpa_inspeccion_vehiculo
        ORDER BY fecha_inspeccion DESC
        LIMIT 300
    """)
    rows = cur.fetchall() or []
    resultados = []
    for row in rows:
        malos = compute_malos(row)
        if malos <= 0:
            continue
        fi = row.get('fecha_inspeccion')
        dias = compute_dias_restantes(fi)
        cedula = s(row.get('recurso_operativo_cedula'))
        idc = row.get('id_codigo_consumidor')
        placa = s(row.get('placa'))
        nombre = s(row.get('nombre'))
        matched_by = None
        try:
            original_id = row.get('id_mpa_inspeccion_vehiculo')
            if cedula:
                cur.execute("""
                    SELECT id_mpa_inspeccion_vehiculo
                    FROM mpa_inspeccion_vehiculo
                    WHERE recurso_operativo_cedula = %s
                    ORDER BY fecha_inspeccion DESC
                    LIMIT 1
                """, (cedula,))
                r1 = cur.fetchone()
                if r1 and r1.get('id_mpa_inspeccion_vehiculo') == original_id:
                    matched_by = 'cedula'
            if not matched_by and idc:
                cur.execute("""
                    SELECT id_mpa_inspeccion_vehiculo
                    FROM mpa_inspeccion_vehiculo
                    WHERE id_codigo_consumidor = %s
                    ORDER BY fecha_inspeccion DESC
                    LIMIT 1
                """, (idc,))
                r2 = cur.fetchone()
                if r2 and r2.get('id_mpa_inspeccion_vehiculo') == original_id:
                    matched_by = 'id'
            if not matched_by and placa:
                cur.execute("""
                    SELECT id_mpa_inspeccion_vehiculo
                    FROM mpa_inspeccion_vehiculo
                    WHERE placa = %s
                    ORDER BY fecha_inspeccion DESC
                    LIMIT 1
                """, (placa,))
                r3 = cur.fetchone()
                if r3 and r3.get('id_mpa_inspeccion_vehiculo') == original_id:
                    matched_by = 'placa'
            if not matched_by and nombre:
                cur.execute("""
                    SELECT id_mpa_inspeccion_vehiculo
                    FROM mpa_inspeccion_vehiculo
                    WHERE nombre = %s
                    ORDER BY fecha_inspeccion DESC
                    LIMIT 1
                """, (nombre,))
                r4 = cur.fetchone()
                if r4 and r4.get('id_mpa_inspeccion_vehiculo') == original_id:
                    matched_by = 'nombre'
        except Exception:
            pass
        resultados.append({
            'id': original_id,
            'cedula': cedula,
            'id_codigo_consumidor': idc,
            'nombre': nombre,
            'placa': placa,
            'malos': malos,
            'dias_restantes': dias,
            'matched_by': matched_by
        })
    print('Usuarios con inspección y fallas pendientes:')
    for r in resultados[:50]:
        print(f"- {r['cedula'] or r['id_codigo_consumidor']} | {r['nombre']} | placa {r['placa']} | malos {r['malos']} | dias {r['dias_restantes']} | matched_by {r['matched_by']}")
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
