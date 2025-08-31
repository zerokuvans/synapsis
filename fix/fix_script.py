# Script para eliminar la línea 'import json' redundante
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# La línea a eliminar es la que contiene solo 'import json' después de 'mas_asignados = cursor.fetchall()'
new_lines = []
prev_line = ""
skip_next_import_json = False

for line in lines:
    if skip_next_import_json and line.strip() == "import json":
        skip_next_import_json = False
        continue
    
    if "mas_asignados = cursor.fetchall()" in prev_line and line.strip() == "":
        skip_next_import_json = True
    
    new_lines.append(line)
    prev_line = line

# Guardar el archivo corregido
with open('main_fixed.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Archivo corregido guardado como main_fixed.py") 