# Resumen de Asistencia - Operación x Recurso Operativo

## 1. Descripción General

Nueva funcionalidad para el módulo "Resumen de Asistencia por Grupos" que incluye una tabla adicional llamada **"OPERACIÓN X RECURSO OPERATIVO"**. Esta tabla proporciona una vista agrupada de los recursos operativos por carpeta, excluyendo las ausencias del cálculo de porcentajes para obtener métricas más precisas de la distribución operativa real.

## 2. Funcionalidad Principal

### 2.1 Tabla "OPERACIÓN X RECURSO OPERATIVO"
- **Fuente de datos**: Tabla `asistencia` agrupada por columna `carpeta`
- **Métricas**: Cantidad de técnicos por grupo y porcentaje de distribución
- **Cálculo especial**: Las ausencias se excluyen del denominador para el cálculo de porcentajes

### 2.2 Lógica de Cálculo de Porcentajes
**Ejemplo práctico:**
- Total técnicos registrados: 65
- Técnicos en ausencias: 3
- Base para cálculo de porcentajes: 62 técnicos (65 - 3)
- Los porcentajes se calculan sobre los 62 técnicos operativos

## 3. Estructura de Datos

### 3.1 Consulta Principal
```sql
SELECT 
    t.grupo,
    t.nombre_tipificacion as carpeta,
    COUNT(DISTINCT a.id_codigo_consumidor) as total_tecnicos
FROM asistencia a
INNER JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
WHERE DATE(a.fecha_asistencia) BETWEEN %fecha_inicio% AND %fecha_fin%
    AND t.grupo IS NOT NULL 
    AND t.grupo != ''
    AND t.grupo NOT IN ('AUSENCIA INJUSTIFICADA', 'AUSENCIA JUSTIFICADA')
GROUP BY t.grupo, t.nombre_tipificacion
ORDER BY t.grupo, t.nombre_tipificacion
```

### 3.2 Cálculo de Base Operativa
```sql
SELECT COUNT(DISTINCT a.id_codigo_consumidor) as total_operativo
FROM asistencia a
INNER JOIN tipificacion_asistencia t ON a.carpeta_dia = t.codigo_tipificacion
WHERE DATE(a.fecha_asistencia) BETWEEN %fecha_inicio% AND %fecha_fin%
    AND t.grupo IS NOT NULL 
    AND t.grupo != ''
    AND t.grupo NOT IN ('AUSENCIA INJUSTIFICADA', 'AUSENCIA JUSTIFICADA')
```

## 4. Estructura de Respuesta API

### 4.1 Endpoint Modificado
**Ruta**: `/api/asistencia/resumen_agrupado`
**Método**: GET

### 4.2 Parámetros de Entrada
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| fecha_inicio | string (YYYY-MM-DD) | Sí | Fecha de inicio del rango |
| fecha_fin | string (YYYY-MM-DD) | Sí | Fecha de fin del rango |
| supervisor | string | No | Filtro por supervisor específico |

### 4.3 Estructura de Respuesta
```json
{
    "success": true,
    "data": {
        "operacion_recurso_operativo": [
            {
                "grupo": "ARREGLOS",
                "carpeta": "ARREGLOS HFC",
                "total_tecnicos": 8,
                "porcentaje": 12.90
            },
            {
                "grupo": "INSTALACIONES", 
                "carpeta": "FTTH INSTALACIONES",
                "total_tecnicos": 15,
                "porcentaje": 24.19
            }
        ],
        "resumen_grupos_tradicional": [
            {
                "grupo": "ARREGLOS",
                "total_tecnicos": 9,
                "porcentaje": 13.85
            }
        ],
        "totales": {
            "total_general": 65,
            "total_operativo": 62,
            "total_ausencias": 3
        },
        "fecha_inicio": "2025-10-03",
        "fecha_fin": "2025-10-03",
        "supervisor_filtro": null
    }
}
```

## 5. Interfaz de Usuario

### 5.1 Estructura de Tablas

#### Tabla 1: "OPERACIÓN X RECURSO OPERATIVO"
| GRUPO | CARPETA | TÉCNICOS | PORCENTAJE |
|-------|---------|----------|------------|
| ARREGLOS | ARREGLOS HFC | 8 | 12.90% |
| ARREGLOS | MANTENIMIENTO FTTH | 1 | 1.61% |
| INSTALACIONES | BROWNFIELD | 12 | 19.35% |
| INSTALACIONES | FTTH INSTALACIONES | 15 | 24.19% |
| POSTVENTA | POSTVENTA | 18 | 29.03% |
| POSTVENTA | POSTVENTA FTTH | 8 | 12.90% |
| **TOTAL OPERATIVO** | | **62** | **100%** |

#### Tabla 2: "RESUMEN TRADICIONAL POR GRUPOS" (Existente)
| GRUPO | CARPETA | TÉCNICOS | PORCENTAJE |
|-------|---------|----------|------------|
| ARREGLOS | ARREGLOS HFC | 8 | 12.31% |
| AUSENCIA INJUSTIFICADA | AUSENCIA INJUSTIFICADA | 2 | 3.08% |
| AUSENCIA JUSTIFICADA | MANTENIMIENTO FTTH | 1 | 1.54% |
| **TOTAL GENERAL** | | **65** | **100%** |

### 5.2 Elementos de Interfaz

#### Filtros (Compartidos)
- **Supervisor**: Dropdown con opción "Todos los supervisores"
- **Fecha Inicio**: Input tipo date
- **Fecha Fin**: Input tipo date
- **Botón Actualizar**: Recarga ambas tablas

#### Indicadores Visuales
- **Badge verde**: Total operativo (excluye ausencias)
- **Badge azul**: Total general (incluye ausencias)
- **Badge naranja**: Total ausencias

## 6. Reglas de Negocio

### 6.1 Exclusión de Ausencias
- **Grupos excluidos del cálculo operativo**:
  - AUSENCIA INJUSTIFICADA
  - AUSENCIA JUSTIFICADA
- **Impacto**: Los porcentajes en la tabla "OPERACIÓN X RECURSO OPERATIVO" se calculan solo sobre técnicos operativos

### 6.2 Validaciones
- **Rango de fechas**: Máximo 1 año
- **Fechas futuras**: No permitidas
- **Formato de fecha**: YYYY-MM-DD obligatorio

### 6.3 Comportamiento por Defecto
- **Sin fechas**: Usa fecha actual
- **Sin supervisor**: Muestra todos los supervisores
- **Sin datos**: Muestra mensaje informativo

## 7. Casos de Uso

### 7.1 Caso Principal
**Actor**: Supervisor/Administrador
**Objetivo**: Analizar distribución operativa real sin considerar ausencias
**Flujo**:
1. Selecciona rango de fechas
2. Opcionalmente filtra por supervisor
3. Hace clic en "Actualizar"
4. Revisa tabla "OPERACIÓN X RECURSO OPERATIVO" para métricas operativas
5. Compara con tabla tradicional para análisis completo

### 7.2 Caso de Análisis Comparativo
**Escenario**: Comparar eficiencia operativa vs. asistencia total
**Beneficio**: 
- Tabla 1 muestra distribución real de trabajo operativo
- Tabla 2 muestra distribución total incluyendo ausencias
- Permite identificar impacto de ausencias en la operación

## 8. Consideraciones Técnicas

### 8.1 Performance
- **Índices requeridos**: 
  - `asistencia.fecha_asistencia`
  - `asistencia.carpeta_dia`
  - `tipificacion_asistencia.codigo_tipificacion`

### 8.2 Compatibilidad
- **Mantiene funcionalidad existente**: La tabla tradicional sigue funcionando igual
- **Retrocompatibilidad**: API mantiene estructura existente y agrega nuevos campos

### 8.3 Escalabilidad
- **Consultas optimizadas**: Uso de DISTINCT para evitar duplicados
- **Filtros eficientes**: Índices en campos de filtro principales
- **Límite de rango**: Máximo 1 año para evitar consultas pesadas

## 9. Beneficios del Negocio

### 9.1 Métricas Operativas Precisas
- **Visibilidad real**: Porcentajes basados en técnicos realmente operativos
- **Planificación mejorada**: Distribución de recursos sin distorsión por ausencias
- **KPIs operativos**: Métricas enfocadas en productividad real

### 9.2 Análisis Comparativo
- **Impacto de ausencias**: Diferencia entre totales operativos y generales
- **Eficiencia por grupo**: Identificación de grupos más productivos
- **Tendencias operativas**: Análisis temporal de distribución de recursos

### 9.3 Toma de Decisiones
- **Redistribución de personal**: Basada en carga operativa real
- **Identificación de necesidades**: Grupos con mayor demanda operativa
- **Optimización de recursos**: Asignación eficiente según métricas reales