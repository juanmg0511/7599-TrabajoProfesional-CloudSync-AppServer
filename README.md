# 75.99 Trabajo Profesional - "Juego Roguelike"

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)

## CloudSync - App Server
### Resumen

Repositorio correspondiente al desarrollo del trabajo final de la carrera **_"Ingeniería en Informática"_** de la **_"Facultad de Ingeniería de la Universidad de Buenos Aires" (FIUBA)_**.  
El mismo consiste en la creación de un juego en 2D con mecánicas _roguelike_ con especial enfasis en la generación de niveles de forma procedural. Este proyecto representa el servidor de aplicación de la plataforma CloudSync, diseñada para el juego.

## Integrantes

### Tutor

- Leandro Ferrigno

### Devs

- Juan Manuel Gonzalez
- Diego Martins Forgan

## Herramientas Utilizadas

- Docker
- Python
- Flask
- Gunicorn

## Ambientes

### Production (PR)
[![Build Status](https://app.travis-ci.com/juanmg0511/7599-TrabajoProfesional-CloudSync-AppServer.svg?branch=main)](https://app.travis-ci.com/juanmg0511/7599-TrabajoProfesional-CloudSync-AppServer)
[![Coverage Status](https://coveralls.io/repos/github/juanmg0511/7599-TrabajoProfesional-CloudSync-AppServer/badge.svg?branch=qa&kill_cache=1?)](https://coveralls.io/github/juanmg0511/7599-TrabajoProfesional-CloudSync-AppServer?branch=master&kill_cache=1?)  
https://fiuba-pr-7599-cs-app-server.herokuapp.com/

### Quality Assurance (QA)
[![Build Status](https://app.travis-ci.com/juanmg0511/7599-TrabajoProfesional-CloudSync-AppServer.svg?branch=qa)](https://app.travis-ci.com/juanmg0511/7599-TrabajoProfesional-CloudSync-AppServer)
[![Coverage Status](https://coveralls.io/repos/github/juanmg0511/7599-TrabajoProfesional-CloudSync-AppServer/badge.svg?branch=qa&kill_cache=1?)](https://coveralls.io/github/juanmg0511/7599-TrabajoProfesional-CloudSync-AppServer?branch=qa&kill_cache=1?)  
https://fiuba-qa-7599-cs-app-server.herokuapp.com/

### Development (DV - desarrollo local)

- Bajar el código
- Ejecutar en el root del repositorio: `docker-compose build`
- Ejecutar en el root del repositorio: `docker-compose up`
- El server estrá disponible en: **127.0.0.1:80**

#### Tests

- Ejecutar los siguientes comandos, con el ambiente levantado:  
`docker exec -u root -it app-server-flask bash -c "coverage run --omit */virtualenv/*,*/usr/* -m unittest tests/*.py -v"`   
`docker exec -u root -it app-server-flask bash -c "coverage report"`
