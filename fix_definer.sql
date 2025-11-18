-- Script para corregir el definer de objetos de base de datos
-- Cambiar de 'vnaranjos'@'localhost' a 'root'@'localhost'

USE capired;

-- Eliminar y recrear procedimientos con el definer correcto
DROP PROCEDURE IF EXISTS sp_generar_alertas_masivas;
DROP PROCEDURE IF EXISTS sp_generar_alertas_masivas_v2;

-- Eliminar triggers con definer incorrecto
DROP TRIGGER IF EXISTS actualizar_stock_entrada_ferretero;
DROP TRIGGER IF EXISTS actualizar_stock_entrada_general;
DROP TRIGGER IF EXISTS actualizar_stock_asignacion;
DROP TRIGGER IF EXISTS tr_parque_automotor_historial_insert_v2;
DROP TRIGGER IF EXISTS tr_parque_automotor_historial_insert_v3;
DROP TRIGGER IF EXISTS tr_parque_automotor_historial_update_v2;
DROP TRIGGER IF EXISTS tr_generar_alertas_vencimiento;
DROP TRIGGER IF EXISTS tr_parque_automotor_historial_update_v3;
DROP TRIGGER IF EXISTS alerta_stock_bajo;

-- Los triggers y procedimientos se recrearán automáticamente cuando se ejecuten los scripts correspondientes
-- o se puede hacer manualmente con el definer correcto

SELECT 'Objetos con definer incorrecto eliminados correctamente' AS resultado;