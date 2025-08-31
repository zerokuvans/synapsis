#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para validar la sintaxis básica del archivo triggers_mysql_ferretero.sql
"""

import re
import sys

def validar_sintaxis_sql(archivo_sql):
    """
    Valida la sintaxis básica de un archivo SQL de triggers MySQL
    """
    errores = []
    warnings = []
    
    try:
        with open(archivo_sql, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except Exception as e:
        return [f"Error al leer el archivo: {e}"], []
    
    lineas = contenido.split('\n')
    
    # Contadores para validar estructura
    delimiters = 0
    create_triggers = 0
    drop_triggers = 0
    begin_count = 0
    end_count = 0
    if_count = 0
    end_if_count = 0
    
    # Validaciones línea por línea
    for i, linea in enumerate(lineas, 1):
        linea_limpia = linea.strip()
        
        # Ignorar comentarios y líneas vacías
        if not linea_limpia or linea_limpia.startswith('--') or linea_limpia.startswith('/*'):
            continue
            
        # Contar elementos estructurales
        if 'DELIMITER' in linea_limpia:
            delimiters += 1
            
        if linea_limpia.startswith('CREATE TRIGGER'):
            create_triggers += 1
            
        if linea_limpia.startswith('DROP TRIGGER'):
            drop_triggers += 1
            
        if linea_limpia == 'BEGIN':
            begin_count += 1
            
        if linea_limpia.startswith('END//'):
            end_count += 1
            
        if re.match(r'^\s*IF\s+', linea_limpia, re.IGNORECASE):
            if_count += 1
            
        if linea_limpia == 'END IF;':
            end_if_count += 1
            
        # Validar caracteres problemáticos
        if '\t' in linea and '    ' not in linea:
            warnings.append(f"Línea {i}: Contiene tabs, se recomienda usar espacios")
            
        # Validar sintaxis básica de MySQL
        if 'SIGNAL SQLSTATE' in linea_limpia and not re.search(r"SIGNAL SQLSTATE '\d{5}'", linea_limpia):
            errores.append(f"Línea {i}: Formato incorrecto de SIGNAL SQLSTATE")
            
    # Validaciones de estructura general
    if delimiters % 2 != 0:
        errores.append("Número impar de declaraciones DELIMITER (debe ser par)")
        
    if create_triggers != drop_triggers:
        warnings.append(f"Número de CREATE TRIGGER ({create_triggers}) no coincide con DROP TRIGGER ({drop_triggers})")
        
    if begin_count != end_count:
        errores.append(f"Número de BEGIN ({begin_count}) no coincide con END ({end_count})")
        
    if if_count != end_if_count:
        errores.append(f"Número de IF ({if_count}) no coincide con END IF ({end_if_count})")
        
    # Validar estructura específica de triggers
    patron_trigger = r'CREATE TRIGGER\s+(\w+)\s+(BEFORE|AFTER)\s+(INSERT|UPDATE|DELETE)\s+ON\s+(\w+)'
    triggers_encontrados = re.findall(patron_trigger, contenido, re.IGNORECASE)
    
    if len(triggers_encontrados) != create_triggers:
        errores.append("Algunos triggers no tienen la estructura correcta")
        
    return errores, warnings

def main():
    archivo_sql = 'triggers_mysql_ferretero.sql'
    
    print("=" * 60)
    print("VALIDADOR DE SINTAXIS - TRIGGERS MYSQL FERRETERO")
    print("=" * 60)
    
    errores, warnings = validar_sintaxis_sql(archivo_sql)
    
    if errores:
        print("\n❌ ERRORES ENCONTRADOS:")
        for error in errores:
            print(f"  • {error}")
    else:
        print("\n✅ No se encontraron errores de sintaxis")
        
    if warnings:
        print("\n⚠️  ADVERTENCIAS:")
        for warning in warnings:
            print(f"  • {warning}")
    else:
        print("\n✅ No se encontraron advertencias")
        
    print("\n" + "=" * 60)
    
    if errores:
        print("RESULTADO: El archivo tiene errores que deben corregirse")
        return 1
    else:
        print("RESULTADO: El archivo parece estar sintácticamente correcto")
        return 0

if __name__ == "__main__":
    sys.exit(main())