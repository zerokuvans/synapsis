#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica que el endpoint /api/equipos_disponibles devuelve el equipo
SKYWDA7C5F9B con el campo 'observacion' incluido, usando login de CACERES.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8080"
USERNAME = "1032402333"  # Cedula de CACERES MARTINEZ CARLOS
PASSWORD = "CE1032402333"  # Según data/usuarios.csv
TARGET_SERIAL = "SKYWDA7C5F9B"


def main():
    s = requests.Session()
    print("=== LOGIN ===")
    try:
        s.get(f"{BASE_URL}/", timeout=10)
        resp = s.post(f"{BASE_URL}/", data={"username": USERNAME, "password": PASSWORD}, allow_redirects=True, timeout=20)
        print("Status:", resp.status_code, "URL:", resp.url)
    except Exception as e:
        print("Error en login:", e)
        return

    print("\n=== CONSULTA /api/equipos_disponibles ===")
    try:
        r = s.get(f"{BASE_URL}/api/equipos_disponibles", timeout=30)
        print("Status:", r.status_code, "Content-Type:", r.headers.get("Content-Type", ""))
        if r.status_code != 200:
            print("Body:", r.text[:500])
            return
        data = r.json()
        equipos = data.get("equipos", data)
        if isinstance(equipos, dict):
            for k in ["data", "rows", "items"]:
                if k in equipos and isinstance(equipos[k], list):
                    equipos = equipos[k]
                    break
            else:
                equipos = []
        print("Total equipos:", len(equipos))
        target = [e for e in equipos if str(e.get("serial", "")).strip() == TARGET_SERIAL]
        print("Encontrados:", len(target))
        if target:
            print("\n=== EQUIPO OBJETIVO ===")
            print(json.dumps(target[0], indent=2, ensure_ascii=False, default=str))
            obs = target[0].get("observacion")
            print("\nObservacion presente:", obs is not None)
            print("Observacion valor:", obs)
        else:
            print("No se encontró el serial", TARGET_SERIAL)
            print("Primeros 3 registros:")
            print(json.dumps(equipos[:3], indent=2, ensure_ascii=False, default=str))
    except Exception as e:
        print("Error consultando API:", e)


if __name__ == "__main__":
    main()