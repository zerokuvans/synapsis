#!/usr/bin/env python
# Script para eliminar la función duplicada

print("Iniciando corrección de duplicación de rutas...")

try:
    with open('main.py', 'r', encoding='utf-8') as file:
        contenido = file.read()
        print(f"Archivo main.py cargado - {len(contenido)} caracteres")

    # Encontrar la primera ocurrencia
    primera_ocurrencia = contenido.find("@app.route('/logistica/guardar_asignacion', methods=['POST'])")
    if primera_ocurrencia == -1:
        print("ERROR: No se encontró la primera ocurrencia de la ruta")
        exit(1)
    else:
        print(f"Primera ocurrencia encontrada en posición {primera_ocurrencia}")

    # Encontrar la segunda ocurrencia
    segunda_ocurrencia = contenido.find("@app.route('/logistica/guardar_asignacion', methods=['POST'])", primera_ocurrencia + 1)
    
    if segunda_ocurrencia != -1:
        print(f"Segunda ocurrencia encontrada en posición {segunda_ocurrencia}")
        
        # Intentar encontrar el final de la función
        # Opciones para detectar el final de la función:
        
        # 1. Próxima definición de ruta
        siguiente_ruta = contenido.find("@app.route", segunda_ocurrencia + 1)
        # 2. Bloque principal if __name__
        if_name_main = contenido.find("if __name__ == '__main__':", segunda_ocurrencia)
        # 3. Función siguiente
        siguiente_def = contenido.find("\ndef ", segunda_ocurrencia + 1)
        
        # Determinar cuál está más cerca
        candidatos = [p for p in [siguiente_ruta, if_name_main, siguiente_def] if p != -1]
        
        if candidatos:
            fin_funcion = min(candidatos)
            print(f"Final de la función duplicada detectado en posición {fin_funcion}")
            
            # Conservamos todo antes de la segunda ocurrencia y después del final de la función
            nuevo_contenido = contenido[:segunda_ocurrencia] + contenido[fin_funcion:]
            
            # Hacer una copia de seguridad del archivo original
            import shutil
            shutil.copy2('main.py', 'main.py.bak')
            print("Copia de seguridad creada como main.py.bak")
            
            # Guardar el archivo corregido
            with open('main_fixed.py', 'w', encoding='utf-8') as file:
                file.write(nuevo_contenido)
            print(f"Archivo corregido guardado como main_fixed.py ({len(nuevo_contenido)} caracteres)")
            
            # Mostrar estadísticas
            caracteres_eliminados = len(contenido) - len(nuevo_contenido)
            print(f"Se eliminaron {caracteres_eliminados} caracteres correspondientes a la función duplicada")
        else:
            print("No se pudo determinar dónde termina la función duplicada")
    else:
        print("No se encontró una segunda ocurrencia de la ruta '/logistica/guardar_asignacion'")
except Exception as e:
    print(f"Error durante la ejecución: {str(e)}") 