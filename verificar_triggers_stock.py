#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificación Completa de Triggers MySQL - Sistema Ferretero
=====================================================================

Este script verifica que los triggers de MySQL estén funcionando correctamente
y que el sistema de stock se actualice automáticamente.

Funcionalidades:
1. Verificar existencia de triggers
2. Mostrar estado inicial del stock
3. Realizar inserción de prueba
4. Verificar actualización automática del stock
5. Limpiar datos de prueba
6. Generar reporte completo

Autor: Sistema Synapsis
Fecha: 2025-01-17
"""

import mysql.connector
import os
from datetime import datetime
import sys
from typing import Dict, List, Tuple, Optional

class VerificadorTriggersStock:
    def __init__(self):
        self.conexion = None
        self.cursor = None
        self.resultados = {
            'triggers_existentes': [],
            'stock_inicial': {},
            'stock_final': {},
            'insercion_exitosa': False,
            'actualizacion_automatica': False,
            'errores': []
        }
        self.materiales_prueba = {
            'silicona': 2,
            'grapas_blancas': 3,
            'grapas_negras': 1,
            'cinta_aislante': 1,
            'amarres_negros': 2,
            'amarres_blancos': 1
        }
        
    def conectar_bd(self) -> bool:
        """Establece conexión con la base de datos MySQL"""
        try:
            # Configuración de conexión (ajustar según tu configuración)
            config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', 'synapsis'),
                'charset': 'utf8mb4',
                'autocommit': True
            }
            
            print