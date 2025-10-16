#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Conectar a la base de datos
try:
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        charset='utf8mb4',
        collation='utf8mb4_unicode_ci'
    )

    cursor = connection.cursor(dictionary=True)

    print("🔍 INVESTIGACIÓN: brownfield + tecnico conductor")
    print("=" * 60)

    # 1. Verificar si 'brownfield' existe en presupuesto_carpeta
    print("\n1️⃣ VERIFICANDO 'brownfield' en presupuesto_carpeta:")
    cursor.execute("""
        SELECT presupuesto_carpeta, presupuesto_eventos, presupuesto_diario 
        FROM presupuesto_carpeta 
        WHERE presupuesto_carpeta LIKE '%brownfield%'
    """)
    brownfield_results = cursor.fetchall()
    
    if brownfield_results:
        print("✅ ENCONTRADO en presupuesto_carpeta:")
        for row in brownfield_results:
            print(f"   - Carpeta: '{row['presupuesto_carpeta']}'")
            print(f"   - Eventos: {row['presupuesto_eventos']}")
            print(f"   - Diario: {row['presupuesto_diario']}")
    else:
        print("❌ NO ENCONTRADO 'brownfield' en presupuesto_carpeta")
        
        # Buscar variaciones
        print("\n🔍 Buscando variaciones de 'brownfield':")
        cursor.execute("SELECT DISTINCT presupuesto_carpeta FROM presupuesto_carpeta")
        all_carpetas = cursor.fetchall()
        for carpeta in all_carpetas:
            if 'brown' in carpeta['presupuesto_carpeta'].lower():
                print(f"   - Encontrado similar: '{carpeta['presupuesto_carpeta']}'")

    # 2. Verificar si 'tecnico conductor' existe en presupuesto_cargo
    print("\n2️⃣ VERIFICANDO 'tecnico conductor' en presupuesto_cargo:")
    cursor.execute("""
        SELECT cargo, presupuesto_eventos, presupuesto_diario 
        FROM presupuesto_cargo 
        WHERE cargo LIKE '%conductor%'
    """)
    conductor_results = cursor.fetchall()
    
    if conductor_results:
        print("✅ ENCONTRADO cargos con 'conductor':")
        for row in conductor_results:
            print(f"   - Cargo: '{row['cargo']}'")
            print(f"   - Eventos: {row['presupuesto_eventos']}")
            print(f"   - Diario: {row['presupuesto_diario']}")
    else:
        print("❌ NO ENCONTRADO 'conductor' en presupuesto_cargo")
        
        # Buscar variaciones
        print("\n🔍 Buscando variaciones de 'conductor':")
        cursor.execute("SELECT DISTINCT cargo FROM presupuesto_cargo")
        all_cargos = cursor.fetchall()
        for cargo in all_cargos:
            if 'conduc' in cargo['cargo'].lower() or 'tecnic' in cargo['cargo'].lower():
                print(f"   - Encontrado similar: '{cargo['cargo']}'")

    # 3. Buscar técnicos con esta combinación específica
    print("\n3️⃣ BUSCANDO TÉCNICOS con brownfield + conductor:")
    cursor.execute("""
        SELECT recurso_operativo_cedula, carpeta, cargo 
        FROM recurso_operativo 
        WHERE carpeta LIKE '%brownfield%' AND cargo LIKE '%conductor%'
    """)
    tecnicos_brownfield = cursor.fetchall()
    
    if tecnicos_brownfield:
        print("✅ TÉCNICOS ENCONTRADOS con esta combinación:")
        for tecnico in tecnicos_brownfield:
            print(f"   - Cédula: {tecnico['recurso_operativo_cedula']}")
            print(f"   - Carpeta: '{tecnico['carpeta']}'")
            print(f"   - Cargo: '{tecnico['cargo']}'")
    else:
        print("❌ NO HAY TÉCNICOS con brownfield + conductor")
        
        # Buscar técnicos con brownfield
        print("\n🔍 Técnicos con 'brownfield':")
        cursor.execute("""
            SELECT recurso_operativo_cedula, carpeta, cargo 
            FROM recurso_operativo 
            WHERE carpeta LIKE '%brownfield%'
            LIMIT 5
        """)
        brownfield_tecnicos = cursor.fetchall()
        for tecnico in brownfield_tecnicos:
            print(f"   - Cédula: {tecnico['recurso_operativo_cedula']}, Carpeta: '{tecnico['carpeta']}', Cargo: '{tecnico['cargo']}'")
        
        # Buscar técnicos con conductor
        print("\n🔍 Técnicos con 'conductor':")
        cursor.execute("""
            SELECT recurso_operativo_cedula, carpeta, cargo 
            FROM recurso_operativo 
            WHERE cargo LIKE '%conductor%'
            LIMIT 5
        """)
        conductor_tecnicos = cursor.fetchall()
        for tecnico in conductor_tecnicos:
            print(f"   - Cédula: {tecnico['recurso_operativo_cedula']}, Carpeta: '{tecnico['carpeta']}', Cargo: '{tecnico['cargo']}'")

    # 4. Verificar valores exactos para debugging
    print("\n4️⃣ ANÁLISIS DE VALORES EXACTOS:")
    print("\nTodas las carpetas en presupuesto_carpeta:")
    cursor.execute("SELECT presupuesto_carpeta FROM presupuesto_carpeta ORDER BY presupuesto_carpeta")
    carpetas = cursor.fetchall()
    for i, carpeta in enumerate(carpetas[:10]):  # Mostrar solo las primeras 10
        print(f"   {i+1}. '{carpeta['presupuesto_carpeta']}'")
    if len(carpetas) > 10:
        print(f"   ... y {len(carpetas) - 10} más")

    print("\nTodos los cargos en presupuesto_cargo:")
    cursor.execute("SELECT cargo FROM presupuesto_cargo ORDER BY cargo")
    cargos = cursor.fetchall()
    for i, cargo in enumerate(cargos[:10]):  # Mostrar solo los primeros 10
        print(f"   {i+1}. '{cargo['cargo']}'")
    if len(cargos) > 10:
        print(f"   ... y {len(cargos) - 10} más")

    cursor.close()
    connection.close()
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSIÓN: Revisa los resultados arriba para identificar el problema")

except Exception as e:
    print(f"❌ Error de conexión: {str(e)}")