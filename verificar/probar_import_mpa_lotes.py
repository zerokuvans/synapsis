import requests
import re
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"
IMPORTS = [
    {"name": "Tecnico Mecánica", "url": f"{BASE_URL}/api/mpa/tecnico_mecanica/import-excel", "csv": r"C:\\Users\\vnaranjos\\OneDrive\\DESARROLLOS PROPIOS\\synapsis\\excel\\TECNICO.csv"},
    {"name": "SOAT", "url": f"{BASE_URL}/api/mpa/soat/import-excel", "csv": r"C:\\Users\\vnaranjos\\OneDrive\\DESARROLLOS PROPIOS\\synapsis\\excel\\soat.csv"},
    {"name": "Licencias de Conducir", "url": f"{BASE_URL}/api/mpa/licencias-conducir/import-excel", "csv": r"C:\\Users\\vnaranjos\\OneDrive\\DESARROLLOS PROPIOS\\synapsis\\excel\\licencia.csv"},
]

USERNAME = "80833959"
PASSWORD = "M4r14l4r@"


def obtener_csrf(html: str):
    patterns = [
        r'name="csrf_token"\s+value="([^"]+)"',
        r'<input[^>]*name=["\']csrf_token["\'][^>]*value=["\']([^"\'>]+)["\']',
        r'csrf_token["\']\s*:\s*["\']([^"\'>]+)["\']'
    ]
    for p in patterns:
        m = re.search(p, html)
        if m:
            return m.group(1)
    return None


def login(session: requests.Session):
    print("[1] Obteniendo página de login...")
    resp_login_page = session.get(LOGIN_URL, timeout=30)
    print(f"   Status: {resp_login_page.status_code}")
    csrf_token = obtener_csrf(resp_login_page.text)

    print("[2] Intentando login...")
    login_data = {"username": USERNAME, "password": PASSWORD}
    if csrf_token:
        login_data["csrf_token"] = csrf_token

    headers = {"X-Requested-With": "XMLHttpRequest", "Content-Type": "application/x-www-form-urlencoded"}
    resp_login = session.post(LOGIN_URL, data=login_data, headers=headers, allow_redirects=True, timeout=30)
    print(f"   Status: {resp_login.status_code}")
    print(f"   URL final: {resp_login.url}")

    login_ok = False
    if "dashboard" in resp_login.url.lower():
        login_ok = True
    else:
        try:
            j = resp_login.json()
            if j.get("status") == "success" or j.get("message", "").lower().startswith("inicio"):
                login_ok = True
        except Exception:
            pass
    if not login_ok:
        print("   ⚠️ No se pudo confirmar login por URL/JSON; continuaremos con cookies actuales.")


def subir_csv(session: requests.Session, name: str, url: str, csv_path: str):
    print(f"\n[3] Subiendo {name} -> {csv_path}")
    path_obj = Path(csv_path)
    if not path_obj.exists():
        print(f"   ❌ CSV no encontrado: {csv_path}")
        return None

    files = {"file": (path_obj.name, open(csv_path, "rb"), "text/csv")}
    try:
        resp_upload = session.post(url, files=files, timeout=120)
        print(f"   Status: {resp_upload.status_code}")
        ct = resp_upload.headers.get("Content-Type", "")
        print(f"   Content-Type: {ct}")
        body = resp_upload.text
        print("   Respuesta (primeros 400 chars):")
        print(body[:400])
        try:
            j = resp_upload.json()
            print("\nJSON:")
            print(json.dumps(j, ensure_ascii=False, indent=2))
            return j
        except Exception:
            return None
    except Exception as e:
        print(f"   ❌ Error al subir CSV: {e}")
        return None


def main():
    print("=== Importación en lote MPA: Técnico, SOAT, Licencias ===")
    session = requests.Session()
    login(session)

    resultados = {}
    for item in IMPORTS:
        j = subir_csv(session, item["name"], item["url"], item["csv"])
        resultados[item["name"]] = j

    print("\n=== Resumen ===")
    for name, res in resultados.items():
        if isinstance(res, dict):
            ok = res.get("success")
            ins = res.get("inserted")
            upd = res.get("updated")
            skp = res.get("skipped")
            print(f"- {name}: success={ok}, inserted={ins}, updated={upd}, skipped={skp}")
        else:
            print(f"- {name}: sin JSON o error")


if __name__ == "__main__":
    main()