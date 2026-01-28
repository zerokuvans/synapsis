#!/usr/bin/env python3
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '732137A031E4b@',
    'database': 'capired',
    'charset': 'utf8mb4',
    'autocommit': True
}

def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute('DESCRIBE dotaciones')
    existing = [r[0] for r in cur.fetchall()]
    base = [
        'cliente','id_codigo_consumidor','pantalon','pantalon_talla',
        'camisetagris','camiseta_gris_talla','guerrera','guerrera_talla',
        'chaqueta','chaqueta_talla','camisetapolo','camiseta_polo_talla',
        'guantes_nitrilo','guantes_carnaza','gafas','gorra','casco','botas','botas_talla',
        'arnes','eslinga','tie_of','mosqueton','pretales',
        'estado_pantalon','estado_camisetagris','estado_guerrera','estado_chaqueta',
        'estado_camiseta_polo','estado_guantes_nitrilo','estado_guantes_carnaza',
        'estado_gafas','estado_gorra','estado_casco','estado_botas',
        'estado_arnes','estado_eslinga','estado_tie_of','estado_mosqueton','estado_pretales'
    ]
    cols = [c for c in base if c in existing]
    ph = ', '.join([f"%({c})s" for c in cols])
    query = f"INSERT INTO dotaciones ({', '.join(cols)}, fecha_registro) VALUES ({ph}, NOW())"
    params = {c: None for c in cols}
    params['cliente'] = 'Prueba API'
    params['id_codigo_consumidor'] = 0
    for c in cols:
        if c.startswith('estado_') and params[c] is None:
            params[c] = 'NO VALORADO'
    print('QUERY:', query)
    print('PARAM_KEYS:', cols)
    cur.execute(query, params)
    print('OK ID:', cur.lastrowid)
    conn.commit()
    cur.close(); conn.close()

if __name__ == '__main__':
    main()

