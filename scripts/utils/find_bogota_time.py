# Script para encontrar las líneas donde se usa get_bogota_datetime()

with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'get_bogota_datetime()' in line:
            print(f'Línea {i+1}: {line.strip()}')