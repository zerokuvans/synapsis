import requests

r = requests.get('http://127.0.0.1:8080/login', allow_redirects=False)
print(f'Status: {r.status_code}')
print(f'Location: {r.headers.get("Location", "None")}')
print(f'Text: {r.text[:100]}...')