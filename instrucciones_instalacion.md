# Instrucciones para integrar el endpoint de Detalle de Técnicos

Para integrar correctamente el endpoint de detalle de técnicos en el archivo `main.py`, sigue estos pasos:

## 1. Importar el módulo api_detalle_tecnicos

Añade esta línea al inicio del archivo `main.py` junto con las demás importaciones:

```python
import api_detalle_tecnicos
```

## 2. Registrar el endpoint

Justo antes de la línea `if __name__ == '__main__':`, añade esta línea:

```python
# Registrar endpoint de detalle de tecnicos
obtener_detalle_tecnicos = api_detalle_tecnicos.register_endpoint(app, get_db_connection, login_required)
```

## 3. Reiniciar el servidor

Una vez realizados estos cambios, reinicia el servidor Flask:

```
python main.py
```

## 4. Verificar la instalación

Puedes verificar que el endpoint está correctamente instalado accediendo a:

```
http://localhost:8080/api/indicadores/detalle_tecnicos?fecha=2023-03-17&supervisor=NOMBRE_DEL_SUPERVISOR
```

El resultado debería ser un JSON con la información de los técnicos asignados al supervisor especificado, con sus estados de asistencia y preoperacional para la fecha indicada.

---

## Problemas comunes

Si encuentras errores al implementar estos cambios, verifica:

1. Que las tablas `tecnicos`, `asistencia` y `preoperacional` tengan los campos correctos
2. Que los parámetros de función `get_db_connection` y `login_required` sean los correctos
3. Que el formato de la fecha sea `YYYY-MM-DD` 