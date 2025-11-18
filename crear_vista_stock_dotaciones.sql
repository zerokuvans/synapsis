-- Script para crear la vista vista_stock_dotaciones
-- Este script puede ser ejecutado en cualquier base de datos que tenga las tablas:
-- - ingresos_dotaciones (con columnas: cantidad, tipo_elemento)
-- - dotaciones (con columnas para cada tipo de elemento)

-- Eliminar la vista si ya existe
DROP VIEW IF EXISTS vista_stock_dotaciones;

-- Crear la vista vista_stock_dotaciones
CREATE VIEW vista_stock_dotaciones AS
SELECT 
    'pantalon' AS tipo_elemento,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'pantalon'
    ) AS cantidad_ingresada,
    (
        SELECT COALESCE(SUM(pantalon), 0) 
        FROM dotaciones 
        WHERE pantalon IS NOT NULL AND pantalon > 0
    ) AS cantidad_entregada,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'pantalon'
    ) - (
        SELECT COALESCE(SUM(pantalon), 0) 
        FROM dotaciones 
        WHERE pantalon IS NOT NULL AND pantalon > 0
    ) AS saldo_disponible

UNION ALL

SELECT 
    'camisetagris' AS tipo_elemento,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'camisetagris'
    ) AS cantidad_ingresada,
    (
        SELECT COALESCE(SUM(camisetagris), 0) 
        FROM dotaciones 
        WHERE camisetagris IS NOT NULL AND camisetagris > 0
    ) AS cantidad_entregada,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'camisetagris'
    ) - (
        SELECT COALESCE(SUM(camisetagris), 0) 
        FROM dotaciones 
        WHERE camisetagris IS NOT NULL AND camisetagris > 0
    ) AS saldo_disponible

UNION ALL

SELECT 
    'guerrera' AS tipo_elemento,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'guerrera'
    ) AS cantidad_ingresada,
    (
        SELECT COALESCE(SUM(guerrera), 0) 
        FROM dotaciones 
        WHERE guerrera IS NOT NULL AND guerrera > 0
    ) AS cantidad_entregada,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'guerrera'
    ) - (
        SELECT COALESCE(SUM(guerrera), 0) 
        FROM dotaciones 
        WHERE guerrera IS NOT NULL AND guerrera > 0
    ) AS saldo_disponible

UNION ALL

SELECT 
    'camisetapolo' AS tipo_elemento,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'camisetapolo'
    ) AS cantidad_ingresada,
    (
        SELECT COALESCE(SUM(camisetapolo), 0) 
        FROM dotaciones 
        WHERE camisetapolo IS NOT NULL AND camisetapolo > 0
    ) AS cantidad_entregada,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'camisetapolo'
    ) - (
        SELECT COALESCE(SUM(camisetapolo), 0) 
        FROM dotaciones 
        WHERE camisetapolo IS NOT NULL AND camisetapolo > 0
    ) AS saldo_disponible

UNION ALL

SELECT 
    'botas' AS tipo_elemento,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'botas'
    ) AS cantidad_ingresada,
    (
        SELECT COALESCE(SUM(botas), 0) 
        FROM dotaciones 
        WHERE botas IS NOT NULL AND botas > 0
    ) AS cantidad_entregada,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'botas'
    ) - (
        SELECT COALESCE(SUM(botas), 0) 
        FROM dotaciones 
        WHERE botas IS NOT NULL AND botas > 0
    ) AS saldo_disponible

UNION ALL

SELECT 
    'guantes_nitrilo' AS tipo_elemento,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'guantes_nitrilo'
    ) AS cantidad_ingresada,
    (
        SELECT COALESCE(SUM(guantes_nitrilo), 0) 
        FROM dotaciones 
        WHERE guantes_nitrilo IS NOT NULL AND guantes_nitrilo > 0
    ) AS cantidad_entregada,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'guantes_nitrilo'
    ) - (
        SELECT COALESCE(SUM(guantes_nitrilo), 0) 
        FROM dotaciones 
        WHERE guantes_nitrilo IS NOT NULL AND guantes_nitrilo > 0
    ) AS saldo_disponible

UNION ALL

SELECT 
    'guantes_carnaza' AS tipo_elemento,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'guantes_carnaza'
    ) AS cantidad_ingresada,
    (
        SELECT COALESCE(SUM(guantes_carnaza), 0) 
        FROM dotaciones 
        WHERE guantes_carnaza IS NOT NULL AND guantes_carnaza > 0
    ) AS cantidad_entregada,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'guantes_carnaza'
    ) - (
        SELECT COALESCE(SUM(guantes_carnaza), 0) 
        FROM dotaciones 
        WHERE guantes_carnaza IS NOT NULL AND guantes_carnaza > 0
    ) AS saldo_disponible

UNION ALL

SELECT 
    'gafas' AS tipo_elemento,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'gafas'
    ) AS cantidad_ingresada,
    (
        SELECT COALESCE(SUM(gafas), 0) 
        FROM dotaciones 
        WHERE gafas IS NOT NULL AND gafas > 0
    ) AS cantidad_entregada,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'gafas'
    ) - (
        SELECT COALESCE(SUM(gafas), 0) 
        FROM dotaciones 
        WHERE gafas IS NOT NULL AND gafas > 0
    ) AS saldo_disponible

UNION ALL

SELECT 
    'gorra' AS tipo_elemento,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'gorra'
    ) AS cantidad_ingresada,
    (
        SELECT COALESCE(SUM(gorra), 0) 
        FROM dotaciones 
        WHERE gorra IS NOT NULL AND gorra > 0
    ) AS cantidad_entregada,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'gorra'
    ) - (
        SELECT COALESCE(SUM(gorra), 0) 
        FROM dotaciones 
        WHERE gorra IS NOT NULL AND gorra > 0
    ) AS saldo_disponible

UNION ALL

SELECT 
    'casco' AS tipo_elemento,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'casco'
    ) AS cantidad_ingresada,
    (
        SELECT COALESCE(SUM(casco), 0) 
        FROM dotaciones 
        WHERE casco IS NOT NULL AND casco > 0
    ) AS cantidad_entregada,
    (
        SELECT COALESCE(SUM(cantidad), 0) 
        FROM ingresos_dotaciones 
        WHERE tipo_elemento = 'casco'
    ) - (
        SELECT COALESCE(SUM(casco), 0) 
        FROM dotaciones 
        WHERE casco IS NOT NULL AND casco > 0
    ) AS saldo_disponible;

-- Verificar que la vista se creó correctamente
-- SELECT * FROM vista_stock_dotaciones;

/*
ESTRUCTURA DE LA VISTA:
- tipo_elemento: Nombre del elemento de dotación
- cantidad_ingresada: Total de unidades ingresadas al inventario
- cantidad_entregada: Total de unidades entregadas a personal
- saldo_disponible: Stock disponible (ingresadas - entregadas)

ELEMENTOS INCLUIDOS:
- pantalon
- camisetagris
- guerrera
- camisetapolo
- botas
- guantes_nitrilo
- guantes_carnaza
- gafas
- gorra
- casco

REQUISITOS DE TABLAS:
1. ingresos_dotaciones: tabla con ingresos de inventario
   - cantidad (INT): cantidad ingresada
   - tipo_elemento (VARCHAR): tipo de elemento

2. dotaciones: tabla con entregas a personal
   - Una columna por cada tipo de elemento (pantalon, camisetagris, etc.)
   - Cada columna debe ser INT y permitir NULL
*/