import requests
import re
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/"
IMPORT_URL = f"{BASE_URL}/api/mpa/licencias-conducir/import-excel"
CSV_PATH = r"C:\\Users\\vnaranjos\\OneDrive\\DESARROLLOS PROPIOS\\synapsis\\excel\\licencia.csv"

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


def subir_csv(session: requests.Session, csv_path: str):
    print(f"\n[3] Subiendo Licencias -> {csv_path}")
    path_obj = Path(csv_path)
    if not path_obj.exists():
        print(f"   ❌ CSV no encontrado: {csv_path}")
        return None

    files = {"file": (path_obj.name, open(csv_path, "rb"), "text/csv")}
    try:
        resp_upload = session.post(IMPORT_URL, files=files, timeout=120)
        print(f"   Status: {resp_upload.status_code}")
        ct = resp_upload.headers.get("Content-Type", "")
        print(f"   Content-Type: {ct}")
        body = resp_upload.text
        print("   Respuesta (primeros 500 chars):")
        print(body[:500])
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
    print("=== Reimportación de Licencias de Conducir ===")
    session = requests.Session()
    login(session)

    res = subir_csv(session, CSV_PATH)

    print("\n=== Resumen ===")
    if isinstance(res, dict):
        ok = res.get("success")
        ins = res.get("inserted")
        upd = res.get("updated")
        skp = res.get("skipped")
        print(f"- Licencias: success={ok}, inserted={ins}, updated={upd}, skipped={skp}")
        # Mostrar detalles de filas omitidas y ajustes de fecha_inicio si están disponibles
        if "skipped_details" in res:
            print("\nDetalles de omitidos:")
            for d in res.get("skipped_details", [])[:50]:
                print(f"  fila={d.get('row')} tecnico={d.get('tecnico', '-')}: {d.get('reason')}")
        if "ajustes_fecha_inicio" in res:
            print("\nAjustes de fecha_inicio (primeros 50):")
            for a in res.get("ajustes_fecha_inicio", [])[:50]:
                print(f"  fila={a.get('row')} tecnico={a.get('tecnico')}: {a.get('note')}")

        # Guardar respuesta en archivos para inspección
        try:
            out_json = Path(__file__).parent / "licencias_result.json"
            out_txt = Path(__file__).parent / "licencias_summary.txt"
            with open(out_json, "w", encoding="utf-8") as f:
                json.dump(res, f, ensure_ascii=False, indent=2)
            with open(out_txt, "w", encoding="utf-8") as f:
                f.write(f"success={ok} inserted={ins} updated={upd} skipped={skp}\n")
                f.write("Detalles de omitidos (máx 200):\n")
                for d in res.get("skipped_details", [])[:200]:
                    f.write(f"  fila={d.get('row')} tecnico={d.get('tecnico', '-')}: {d.get('reason')}\n")
                f.write("Ajustes fecha_inicio (máx 200):\n")
                for a in res.get("ajustes_fecha_inicio", [])[:200]:
                    f.write(f"  fila={a.get('row')} tecnico={a.get('tecnico')}: {a.get('note')}\n")
            print(f"\nArchivos guardados: {out_json} y {out_txt}")
        except Exception as e:
            print(f"No se pudo escribir archivos de salida: {e}")
    else:
        print("- Licencias: sin JSON o error")


if __name__ == "__main__":
    main()