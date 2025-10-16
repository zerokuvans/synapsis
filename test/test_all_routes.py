import requests

# Probar varias rutas
routes_to_test = ['/login', '/dashboard', '/lider', '/mpa', '/logistica/automotor']

for route in routes_to_test:
    try:
        r = requests.get(f'http://127.0.0.1:8080{route}', allow_redirects=False)
        print(f'{route}: Status {r.status_code}')
        if r.status_code == 302:
            print(f'  -> Redirect to: {r.headers.get("Location", "None")}')
    except Exception as e:
        print(f'{route}: Error - {e}')