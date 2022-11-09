# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# src/swagger_data.py

# Basado en:
# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876

# Importacion de librerias necesarias
# Flask, para la implementacion del servidor REST
from flask_restful import Resource
from flask import request
from http import HTTPStatus

# Importacion de las configuracion del App Server
import app_server_config as config
# Importacion del archivo principal y helpers
import app_server as appServer
from src import helpers


# Clase que define el endpoint que entrega la definicion de la API
# verbo GET - entregar definicion
class SwaggerData(Resource):
    def get(self):

        appServer.app.logger.info(helpers.log_request_id() +
                                  'API definition requested.')

        # Se configura el titulo y la URL base dinamicamente en base al
        # al ambiente en que se esta ejecutando
        appServer.swagger_data["info"]["title"] = \
            "FIUBA CloudSync API Reference"
        appServer.swagger_data["servers"] = [
            {
                "url": request.host_url + config.api_path[1:],
                "description": "App Server" + " - " + config.app_env
            }
        ]

        return helpers.return_request(appServer.swagger_data, HTTPStatus.OK)
