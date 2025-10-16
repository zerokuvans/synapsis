# Documentación del Proceso de Restauración
## Sistema de Dotaciones - Truncate Seguro

---

## 📋 Información General

**Fecha de creación:** 2025-01-24  
**Sistema:** Capired - Módulo de Dotaciones  
**Base de datos:** capired  
**Versión:** 1.0  

---

## 🎯 Objetivo

Este documento describe el proceso completo de restauración del sistema de dotaciones después de ejecutar el truncate seguro, incluyendo procedimientos de emergencia y recuperación de datos.

---

## 📊 Tablas Afectadas por el Truncate

### Tablas Principales del Sistema
1. **dotaciones** - Tabla principal de dotaciones
2. **cambios_dotacion** - Registro de cambios de dotación
3. **devolucion_dotaciones** - Devoluciones de dotación
4. **historial_vencimientos** - Historial de movimientos
5. **ingresos_dotaciones** - Asignaciones temporales

### Tablas Relacionadas (con FK)
6. **equipos_dotaciones**
7. **devoluciones_dotacion**
8. **cambios_dotaciones**
9. **asignaciones_equipos_dotaciones**
10. **devoluciones_historial**
11. **historial_notificaciones**
12. **devoluciones_elementos**
13. **devolucion_detalles**
14. **historial_cambios_dotaciones**
15. **cambios_dotaciones_detalle**
16. **movimientos_equipos_dotaciones**
17. **auditoria_estados_devolucion**

---

## 🔄 Tipos de Restauración

### 1. Restauración Completa (Recomendada)

**Cuándo usar:**
- Error crítico durante el truncate
- Pérdida de datos no planificada
- Corrupción de la base de datos
- Necesidad de volver al estado anterior completo

**Proceso:**
```bash
# 1. Detener servicios que usen la base de datos
sudo systemctl stop apache2
sudo systemctl stop nginx

# 2. Crear backup del estado actual (por seguridad)
mysqldump -h localhost -u root -p capired > backup_estado_actual_$(date +%Y%m%d_%H%M%S).sql

# 3. Restaurar desde backup completo
mysql -h localhost -u root -p capired < backup_pre_truncate_YYYYMMDD_HHMMSS.sql

# 4. Verificar restauración
mysql -h localhost -u root -p -e "USE capired; SELECT COUNT(*) FROM dotaciones;"

# 5. Reiniciar servicios
sudo systemctl start apache2
sudo systemctl start nginx
```

### 2. Restauración Selectiva

**Cuándo usar:**
- Solo algunas tablas necesitan restauración
- Truncate parcialmente exitoso
- Recuperación de datos específicos

**Proceso:**
```bash
# 1. Extraer datos específicos del backup
mysqldump -h localhost -u root -p capired tabla_especifica > tabla_especifica_restore.sql

# 2. Restaurar tabla específica
mysql -h localhost -u root -p capired < tabla_especifica_restore.sql

# 3. Verificar integridad
python verificacion_post_truncate.py
```

### 3. Restauración de Emergencia

**Cuándo usar:**
- Fallo crítico del sistema
- Corrupción de múltiples tablas
- Pérdida de conectividad durante el proceso

**Proceso:**
```bash
# 1. Modo de recuperación MySQL
mysql --force -h localhost -u root -p

# 2. Verificar estado de la base de datos
SHOW DATABASES;
USE capired;
SHOW TABLES;

# 3. Restauración forzada
SET FOREIGN_KEY_CHECKS = 0;
SOURCE backup_pre_truncate_YYYYMMDD_HHMMSS.sql;
SET FOREIGN_KEY_CHECKS = 1;

# 4. Reparar tablas si es necesario
REPAIR TABLE dotaciones;
REPAIR TABLE cambios_dotacion;
```

---

## 🛠️ Scripts de Restauración

### Script Principal: `restaurar_sistema.py`

```python
#!/usr/bin/env python3
# Script de restauración automática

import subprocess
import sys
import os
from datetime import datetime

def restaurar_desde_backup(archivo_backup):
    """Restaura la base de datos desde un archivo de backup"""
    try:
        cmd = [
            'mysql',
            '-h', 'localhost',
            '-u', 'root',
            '-p732137A031E4b@',
            'capired'
        ]
        
        with open(archivo_backup, 'r') as f:
            result = subprocess.run(
                cmd,
                stdin=f,
                capture_output=True,
                text=True
            )
        
        if result.returncode == 0:
            print(f"✅ Restauración exitosa desde {archivo_backup}")
            return True
        else:
            print(f"❌ Error en restauración: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python restaurar_sistema.py <archivo_backup.sql>")
        sys.exit(1)
    
    archivo = sys.argv[1]
    if not os.path.exists(archivo):
        print(f"❌ Archivo no encontrado: {archivo}")
        sys.exit(1)
    
    print(f"🔄 Iniciando restauración desde {archivo}")
    if restaurar_desde_backup(archivo):
        print("🎉 Restauración completada")
        sys.exit(0)
    else:
        print("❌ Restauración falló")
        sys.exit(1)
```

### Script de Verificación Post-Restauración

```bash
#!/bin/bash
# verificar_restauracion.sh

echo "🔍 Verificando restauración del sistema..."

# Verificar conexión a la base de datos
mysql -h localhost -u root -p732137A031E4b@ -e "SELECT 1" capired
if [ $? -eq 0 ]; then
    echo "✅ Conexión a base de datos OK"
else
    echo "❌ Error de conexión a base de datos"
    exit 1
fi

# Verificar tablas principales
for tabla in dotaciones cambios_dotacion devolucion_dotaciones; do
    count=$(mysql -h localhost -u root -p732137A031E4b@ -se "SELECT COUNT(*) FROM $tabla" capired)
    echo "📊 $tabla: $count registros"
done

# Ejecutar verificación completa
python verificacion_post_truncate.py

echo "✅ Verificación completada"
```

---

## 📁 Ubicación de Archivos de Backup

### Estructura de Directorios
```
synapsis/
├── backups/
│   ├── backup_pre_truncate_YYYYMMDD_HHMMSS.sql
│   ├── backup_completo_YYYYMMDD_HHMMSS.sql
│   └── backup_selectivo_YYYYMMDD_HHMMSS.sql
├── logs/
│   ├── truncate_log_YYYYMMDD_HHMMSS.txt
│   └── restauracion_log_YYYYMMDD_HHMMSS.txt
└── reportes/
    ├── reporte_truncate_YYYYMMDD_HHMMSS.json
    └── verificacion_post_truncate_YYYYMMDD_HHMMSS.json
```

### Convención de Nombres
- **Backup pre-truncate:** `backup_pre_truncate_YYYYMMDD_HHMMSS.sql`
- **Backup completo:** `backup_completo_YYYYMMDD_HHMMSS.sql`
- **Logs:** `truncate_log_YYYYMMDD_HHMMSS.txt`
- **Reportes:** `reporte_truncate_YYYYMMDD_HHMMSS.json`

---

## ⚠️ Procedimientos de Emergencia

### Escenario 1: Fallo Durante el Truncate

**Síntomas:**
- Proceso interrumpido abruptamente
- Algunas tablas truncadas, otras no
- Errores de integridad referencial

**Solución:**
1. **NO PÁNICO** - Los datos están en el backup
2. Ejecutar restauración completa inmediatamente
3. Verificar integridad post-restauración
4. Analizar logs para identificar causa del fallo

```bash
# Restauración de emergencia
mysql -h localhost -u root -p capired < backup_pre_truncate_YYYYMMDD_HHMMSS.sql
python verificacion_post_truncate.py
```

### Escenario 2: Corrupción de Backup

**Síntomas:**
- Archivo de backup corrupto
- Errores de sintaxis SQL
- Backup incompleto

**Solución:**
1. Verificar backups alternativos
2. Usar backup más reciente disponible
3. Restauración selectiva si es necesario

```bash
# Verificar integridad del backup
head -n 20 backup_pre_truncate_YYYYMMDD_HHMMSS.sql
tail -n 20 backup_pre_truncate_YYYYMMDD_HHMMSS.sql

# Buscar backups alternativos
ls -la backup_*.sql | sort -k9
```

### Escenario 3: Pérdida Total de Datos

**Síntomas:**
- No hay backups disponibles
- Múltiples fallos del sistema
- Corrupción de la base de datos

**Solución:**
1. **CONTACTAR INMEDIATAMENTE AL ADMINISTRADOR**
2. Verificar backups automáticos del sistema
3. Revisar logs de MySQL para recuperación
4. Considerar recuperación desde replicas

```bash
# Buscar backups automáticos
find /var/backups -name "*capired*" -type f
find /tmp -name "*backup*" -type f

# Verificar logs de MySQL
sudo tail -f /var/log/mysql/error.log
```

---

## 🔍 Verificación Post-Restauración

### Checklist de Verificación

- [ ] **Conexión a base de datos funcional**
- [ ] **Todas las tablas presentes**
- [ ] **Conteo de registros correcto**
- [ ] **Foreign keys activas**
- [ ] **Triggers funcionando**
- [ ] **Índices presentes**
- [ ] **Permisos correctos**
- [ ] **Funcionalidad básica operativa**

### Comandos de Verificación

```sql
-- Verificar estructura
SHOW TABLES;

-- Contar registros en tablas principales
SELECT 'dotaciones' as tabla, COUNT(*) as registros FROM dotaciones
UNION ALL
SELECT 'cambios_dotacion', COUNT(*) FROM cambios_dotacion
UNION ALL
SELECT 'devolucion_dotaciones', COUNT(*) FROM devolucion_dotaciones;

-- Verificar foreign keys
SELECT @@FOREIGN_KEY_CHECKS;

-- Verificar triggers
SELECT TRIGGER_NAME, EVENT_OBJECT_TABLE 
FROM information_schema.TRIGGERS 
WHERE TRIGGER_SCHEMA = 'capired';
```

---

## 📞 Contactos de Emergencia

### Equipo Técnico
- **Administrador de Base de Datos:** [Contacto DBA]
- **Desarrollador Principal:** [Contacto Dev]
- **Administrador de Sistemas:** [Contacto SysAdmin]

### Escalación
1. **Nivel 1:** Desarrollador del sistema
2. **Nivel 2:** Administrador de base de datos
3. **Nivel 3:** Administrador de sistemas
4. **Nivel 4:** Gerencia técnica

---

## 📝 Registro de Incidentes

### Plantilla de Reporte

```
FECHA: ___________
HORA: ____________
USUARIO: __________

DESCRIPCIÓN DEL PROBLEMA:
_________________________________

PASOS REALIZADOS:
1. ____________________________
2. ____________________________
3. ____________________________

RESULTADO:
_________________________________

TIEMPO DE RESOLUCIÓN: __________

LECCIONES APRENDIDAS:
_________________________________
```

---

## 🔄 Mantenimiento y Mejoras

### Recomendaciones

1. **Backups Automáticos**
   - Configurar backups diarios automáticos
   - Retención de 30 días mínimo
   - Verificación de integridad semanal

2. **Monitoreo**
   - Alertas de espacio en disco
   - Monitoreo de performance de BD
   - Logs centralizados

3. **Documentación**
   - Actualizar este documento regularmente
   - Documentar cambios en el esquema
   - Mantener inventario de scripts

4. **Pruebas**
   - Pruebas de restauración mensuales
   - Simulacros de emergencia trimestrales
   - Validación de procedimientos

---

## 📚 Referencias

- [Documentación MySQL - Backup and Recovery](https://dev.mysql.com/doc/refman/8.0/en/backup-and-recovery.html)
- [Guía de Mejores Prácticas - Backup de BD]()
- [Manual del Sistema Capired]()
- [Procedimientos de Emergencia TI]()

---

**Última actualización:** 2025-01-24  
**Versión del documento:** 1.0  
**Próxima revisión:** 2025-04-24  

---

> ⚠️ **IMPORTANTE:** Este documento debe mantenerse actualizado y accesible para todo el equipo técnico. En caso de emergencia, seguir los procedimientos en el orden especificado y documentar todas las acciones realizadas.