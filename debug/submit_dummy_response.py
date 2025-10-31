import requests
import json

BASE = 'http://127.0.0.1:8080'
ENCUESTA_ID = 1
USUARIO_ID = 11

def fetch_encuesta(encuesta_id):
    r = requests.get(f"{BASE}/api/encuestas/{encuesta_id}")
    r.raise_for_status()
    d = r.json()
    if not d.get('success'):
        raise RuntimeError('API no devolvió éxito al obtener encuesta')
    return d.get('encuesta') or {}, d.get('preguntas') or []

def construir_respuestas(preguntas):
    respuestas = []
    archivos = {}
    for p in preguntas:
        pid = p['id_pregunta']
        tipo = p['tipo']
        if tipo in ('texto','parrafo','fecha','hora'):
            respuestas.append({'pregunta_id': pid, 'tipo': tipo if tipo!='parrafo' else 'parrafo', 'valor_texto': 'OK'})
        elif tipo == 'numero':
            respuestas.append({'pregunta_id': pid, 'tipo': 'numero', 'valor_numero': 1})
        elif tipo in ('seleccion_unica','dropdown'):
            opciones = p.get('opciones') or []
            if opciones:
                respuestas.append({'pregunta_id': pid, 'tipo': 'seleccion_unica', 'opcion_id': opciones[0]['id_opcion']})
        elif tipo in ('opcion_multiple','checkbox'):
            opciones = p.get('opciones') or []
            if opciones:
                respuestas.append({'pregunta_id': pid, 'tipo': 'opcion_multiple', 'opcion_ids': [opciones[0]['id_opcion']]})
        elif tipo == 'imagen':
            # Simular archivo sencillo
            respuestas.append({'pregunta_id': pid, 'tipo': 'imagen'})
            archivos[f"file_{pid}"] = ('dummy.jpg', b'\xff\xd8\xff\xd9', 'image/jpeg')
        else:
            respuestas.append({'pregunta_id': pid, 'tipo': 'texto', 'valor_texto': 'OK'})
    return respuestas, archivos

def enviar_respuestas(encuesta_id, respuestas, archivos):
    if archivos:
        payload = json.dumps({'usuario_id': USUARIO_ID, 'respuestas': respuestas})
        files = { 'payload': (None, payload) }
        files.update(archivos)
        r = requests.post(f"{BASE}/api/encuestas/{encuesta_id}/respuestas", files=files)
    else:
        r = requests.post(f"{BASE}/api/encuestas/{encuesta_id}/respuestas", json={'usuario_id': USUARIO_ID, 'respuestas': respuestas})
    print('Status:', r.status_code)
    try:
        print('Body  :', r.json())
    except Exception:
        print('Body  :', r.text[:200])

def main():
    enc, preguntas = fetch_encuesta(ENCUESTA_ID)
    print(f"Encuesta: {enc.get('titulo')} ({ENCUESTA_ID}), preguntas={len(preguntas)}")
    respuestas, archivos = construir_respuestas(preguntas)
    enviar_respuestas(ENCUESTA_ID, respuestas, archivos)

if __name__ == '__main__':
    main()