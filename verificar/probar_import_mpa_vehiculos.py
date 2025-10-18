import requests
import re
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"
IMPORT_URL = f"{BASE_URL}/api/mpa/vehiculos/import-excel"
CSV_PATH = r"C:\\Users\\vnaranjos\\OneDrive\\DESARROLLOS PROPIOS\\synapsis\\excel\\vehiculos.csv"

# Credenciales a usar
USERNAME = "80833959"
PASSWORD = "M4r14l4r@"


def obtener_csrf(html: str):
    """Extrae csrf_token si existe en el HTML."""
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


def main():
    print("=== Probar importación de MPA Vehículos desde CSV ===")
    print(f"- BASE_URL: {BASE_URL}")
    print(f"- CSV: {CSV_PATH}")

    if not Path(CSV_PATH).exists():
        print(f"❌ No se encuentra el archivo CSV en: {CSV_PATH}")
        return

    session = requests.Session()

    # Paso 1: obtener página de login para cookies y posible CSRF
    print("\n[1] Obteniendo página de login...")
    resp_login_page = session.get(LOGIN_URL, timeout=30)
    print(f"   Status: {resp_login_page.status_code}")
    csrf_token = obtener_csrf(resp_login_page.text)
    if csrf_token:
        print(f"   CSRF token encontrado: {csrf_token[:20]}...")
    else:
        print("   No se encontró CSRF token (puede no ser requerido)")

    # Paso 2: realizar login
    print("\n[2] Intentando login...")
    login_data = {
        "username": USERNAME,
        "password": PASSWORD,
    }
    if csrf_token:
        login_data["csrf_token"] = csrf_token

    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
    }

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

    print(f"   Cookies: {session.cookies}")

    # Paso 3: subir CSV al endpoint de importación
    print("\n[3] Subiendo CSV al endpoint /api/mpa/vehiculos/import-excel ...")
    files = {
        "file": (Path(CSV_PATH).name, open(CSV_PATH, "rb"), "text/csv")
    }

    try:
        resp_upload = session.post(IMPORT_URL, files=files, timeout=60)
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
        except Exception:
            pass
    except Exception as e:
        print(f"   ❌ Error al subir CSV: {e}")


if __name__ == "__main__":
    main()