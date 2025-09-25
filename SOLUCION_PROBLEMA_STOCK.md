# 🔧 SOLUCIÓN AL PROBLEMA DE CÁLCULO DE STOCK EN PRODUCCIÓN

## 📋 RESUMEN DEL PROBLEMA

El cálculo de stock funciona correctamente en el entorno local pero **NO funciona en producción**. El problema principal identificado es que **la tabla `dotaciones` está vacía en producción**, lo que causa que el cálculo de stock sea incorrecto.

## 🔍 DIAGNÓSTICO REALIZADO

### ✅ Problema Identificado
- **Tabla `dotaciones` vacía**: 0 registros en producción vs datos en local
- **Vista `vista_stock_dotaciones`**: Puede no existir o no funcionar correctamente en producción
- **Endpoint funcional**: El endpoint `/api/refresh-stock-dotaciones` funciona en local
- **Cálculo incorrecto**: Sin datos en `dotaciones`, el stock calculado es siempre 0

### 📊 Análisis de Datos
```sql
-- Fórmula de cálculo actual:
stock_actual = stock_inicial - total_asignaciones - total_cambios

-- Problema: total_asignaciones = 0 (porque dotaciones está vacía)
-- Resultado: stock_actual = stock_inicial (incorrecto)
```

## 🛠️ SOLUCIÓN PASO A PASO

### 1️⃣ CONFIGURAR VARIABLES DE ENTORNO

**Crear archivo `.env` con configuración de producción:**

```bash
# Copiar .env.example como .env
cp .env.example .env
```

**Editar `.env` con los datos reales de producción:**
```env
# Base de datos de producción
DB_HOST_PROD=tu-servidor-produccion.com
DB_USER_PROD=tu_usuario_prod
DB_PASS_PROD=tu_password_prod
DB_NAME_PROD=synapsis_db

# URL de la API en producción
API_URL_PROD=https://tu-servidor-produccion.com
```

### 2️⃣ VERIFICAR ESTADO DE PRODUCCIÓN

**Ejecutar diagnóstico completo:**
```bash
python verificar_produccion.py
```

Este script verificará:
- ✅ Conectividad a base de datos de producción
- ✅ Existencia de tablas importantes
- ✅ Cantidad de registros en cada tabla
- ✅ Existencia de la vista `vista_stock_dotaciones`
- ✅ Funcionamiento del endpoint en producción

### 3️⃣ POBLAR TABLA DOTACIONES EN PRODUCCIÓN

**Ejecutar script de población:**
```bash
python poblar_dotaciones_produccion.py
```

Este script:
- ✅ Conecta a la base de datos de producción
- ✅ Verifica la estructura de la tabla `dotaciones`
- ✅ Obtiene recursos operativos disponibles
- ✅ Genera datos de prueba realistas
- ✅ Inserta dotaciones de prueba
- ✅ Verifica el impacto en el cálculo de stock

### 4️⃣ VERIFICAR FUNCIONAMIENTO

**Probar endpoint después de poblar datos:**
```bash
# Probar localmente primero
python test_endpoint_stock.py

# Luego verificar en producción
curl -X POST https://tu-servidor-produccion.com/api/refresh-stock-dotaciones
```

## 📁 ARCHIVOS CREADOS

| Archivo | Propósito |
|---------|----------|
| `verificar_produccion.py` | Diagnóstico completo de diferencias entre entornos |
| `poblar_dotaciones_produccion.py` | Poblar tabla dotaciones con datos de prueba |
| `diagnostico_problema_stock.py` | Análisis detallado del problema de stock |
| `test_endpoint_stock.py` | Pruebas del endpoint de refresh stock |
| `.env.example` | Plantilla de configuración de entorno |
| `SOLUCION_PROBLEMA_STOCK.md` | Esta documentación |

## 🔧 COMANDOS ÚTILES

### Verificar Estado de Tablas
```sql
-- Verificar registros en dotaciones
SELECT COUNT(*) FROM dotaciones;

-- Verificar vista de stock
SELECT * FROM vista_stock_dotaciones LIMIT 10;

-- Verificar cálculo manual
SELECT 
    sf.material,
    sf.cantidad as stock_inicial,
    COALESCE(SUM(d.cantidad), 0) as total_asignaciones
FROM stock_ferretero sf
LEFT JOIN dotaciones d ON sf.material = d.tipo_elemento
GROUP BY sf.material, sf.cantidad;
```

### Limpiar Datos de Prueba (si es necesario)
```sql
-- CUIDADO: Solo ejecutar si necesitas limpiar datos de prueba
DELETE FROM dotaciones WHERE estado = 'activo' AND fecha_asignacion = CURDATE();
```

## ⚠️ CONSIDERACIONES IMPORTANTES

### 🔒 Seguridad
- ✅ Nunca commitear el archivo `.env` al repositorio
- ✅ Usar credenciales específicas para producción
- ✅ Verificar permisos de base de datos antes de ejecutar scripts

### 🗄️ Base de Datos
- ✅ Hacer backup antes de modificar datos en producción
- ✅ Probar scripts en entorno de staging primero
- ✅ Verificar que la vista `vista_stock_dotaciones` existe

### 🌐 Conectividad
- ✅ Verificar que el servidor de producción esté accesible
- ✅ Confirmar que los puertos de base de datos estén abiertos
- ✅ Validar credenciales de acceso

## 🚀 PASOS DE IMPLEMENTACIÓN EN PRODUCCIÓN

### Fase 1: Diagnóstico
1. Configurar variables de entorno
2. Ejecutar `verificar_produccion.py`
3. Documentar diferencias encontradas

### Fase 2: Corrección
1. Hacer backup de la base de datos
2. Ejecutar `poblar_dotaciones_produccion.py`
3. Verificar que los datos se insertaron correctamente

### Fase 3: Validación
1. Probar endpoint `/api/refresh-stock-dotaciones`
2. Verificar que el cálculo de stock sea correcto
3. Monitorear logs por errores

### Fase 4: Monitoreo
1. Implementar logging adicional
2. Configurar alertas para tabla dotaciones vacía
3. Documentar proceso para futuras referencias

## 📞 SOPORTE

Si encuentras problemas durante la implementación:

1. **Verificar logs**: Revisar logs del servidor y base de datos
2. **Conectividad**: Confirmar acceso a base de datos de producción
3. **Permisos**: Verificar permisos de usuario de base de datos
4. **Datos**: Confirmar que las tablas relacionadas tienen datos

## ✅ CHECKLIST DE VERIFICACIÓN

- [ ] Variables de entorno configuradas
- [ ] Conectividad a base de datos de producción verificada
- [ ] Tabla `dotaciones` poblada con datos
- [ ] Vista `vista_stock_dotaciones` funcionando
- [ ] Endpoint `/api/refresh-stock-dotaciones` respondiendo correctamente
- [ ] Cálculo de stock mostrando valores correctos
- [ ] Logs sin errores relacionados con stock

---

**📅 Fecha de creación:** 2025-09-25  
**🔧 Versión:** 1.0  
**👨‍💻 Autor:** SOLO Coding Assistant