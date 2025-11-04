# Synapsis

Plataforma de gestión operativa para recursos de movilidad

## Ejecución
La aplicación principal se ejecuta desde `main.py` en el puerto `8080`.

```bash
python main.py
```

- URL local: `http://127.0.0.1:8080`
- URL LAN (si aplica): `http://<IP_local>:8080`
- Constructor de encuestas: `http://127.0.0.1:8080/lider/encuestas`

Para detener el servidor, usa `Ctrl + C` en la terminal.

## Requisitos
- Python 3.10+
- MySQL 8.0+
- Node.js 18.x (para futuras integraciones)

## Instalación
```bash
git clone https://github.com/zerokuvans/synapsis.git
cd synapsis
pip install -r requirements.txt
```

## Configuración
1. Crear archivo .env con las credenciales de la base de datos
2. Ejecutar `python setup_database.py`
3. Crear usuario inicial con `python create_test_user.py`

## Estructura del Proyecto
- `/models`: Definición de modelos de datos
- `/templates`: Vistas HTML
- `/static`: Recursos estáticos (CSS, JS, imágenes)

## Licencia
Proyecto bajo licencia MIT.