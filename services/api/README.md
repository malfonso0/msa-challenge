# **MSA API**

## **Descripción**

Esta es una API desarrollada con FastAPI, utilizada para el manejo de las votaciones en una eleccion y el calculo de los escaños.

## **Swagger**

La API cuenta con una documentación interactiva mediante Swagger. Puedes acceder a ella en:

* **http://localhost:8000/docs** (modo desarrollo)
* **http://localhost:8000/redoc** (modo producción)

En Swagger, puedes encontrar información detallada sobre cada endpoint, incluyendo:

* Descripción del endpoint
* Parámetros de entrada
* Tipos de datos de entrada
* Ejemplos de uso

## **Cómo correr el código**

1. Instala las dependencias: `pip install -r requirements.txt`
2. Corre el servidor: `uvicorn main:app --host 0.0.0.0 --port 8000`

## **Docker**

### Build

1. Construye la imagen: `docker build -t msa-api .`

### Compose

1. Levanta el contenedor: `docker-compose up -d`
2. Verifica el estado del contenedor: `docker-compose ps`
3. Detiene el contenedor: `docker-compose down`

## **Notas**

* Asegúrate de tener instalado Docker y Docker Compose en tu sistema.
* El archivo `docker-compose.yml` se encuentra en el directorio raíz del proyecto.
* El archivo `requirements.txt` se encuentra en el directorio `services/api`
