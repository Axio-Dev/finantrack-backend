# FinanTrack Backend

## Siga este README para poder levantar el backend de FinanTrack

### Instalaciones necesarias
1. Docker
2. Poetry
3. Python
4. PostgreSQL

## Instrucciones

- Copie el repositorio en la carpeta que desee
- Una vez que lo haga entre a la carpeta root del proyecto
- Una vez dentro de la carpeta corra el siguiente comando:
```
poetry install    
```
- El anterior comando instalará las dependencias necesarias para poder levantar el proyecto

## Levantando FinanTrack con Docker
- Si es de su elección correr el proyecto con Docker, debe de ejecutar el siguiente comando
```
docker compose build
```
 - Este comando comenzará a crear la imagen de Docker

- Después ejecute el siguiente comando
```
docker compose up
```
 - Este comando creará y levantará el contenedor

- Ahora el contenedor debe de estar corriendo con los siguientes services:
 - db
 - web
 - Cada uno de estos services representan la base de datos y el servidor web de Django
