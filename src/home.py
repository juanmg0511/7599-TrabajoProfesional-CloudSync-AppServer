# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# src/home.py

# Basado en:
# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876

# Importacion de librerias necesarias
# Flask, para la implementacion del servidor REST
from flask_restful import Resource
from http import HTTPStatus

# Importacion del archivo principal y helpers
import app_server as appServer
from src import helpers


# Clase que muestra la info del server, en la home '/'
class Home(Resource):
    @helpers.log_reqId
    def get(self):
        homeResponseGet = "7599-cloudsync-app-server-v" + \
                          appServer.server_version
        appServer.app.logger.info(helpers.log_request_id() +
                                  'Displaying home with server information.')
        return helpers.return_request(homeResponseGet, HTTPStatus.OK)


# Clase que devuelve el ping del servidor
class Ping(Resource):
    @helpers.log_reqId
    def get(self):
        appServer.app.logger.info(helpers.log_request_id() +
                                  'Ping requested.')
        pingResponseGet = {
            "code": 0,
            "message": "Ping.",
            "data": None
        }
        return helpers.return_request(pingResponseGet, HTTPStatus.OK)


# Clase que entrega informacion sobre el estado del servidor
class Status(Resource):
    @helpers.log_reqId
    def get(self):
        appServer.app.logger.info(helpers.log_request_id() +
                                  'Server status requested.')
        dbStatus = "offline"
        try:
            # Informacion sobre la instancia de DB, para DEBUG
            # dbInfo = appServer.cl.server_info()
            dbStatus = "online"
        except Exception:
            dbStatus = "offline"
        statusResponseGet = {
            "code": 0,
            "message": "7599-cloudsync-app-server-v" +
                       appServer.server_version,
            "data": {
                        "server_status": "online",
                        "database_status": dbStatus
                     }
        }
        return helpers.return_request(statusResponseGet, HTTPStatus.OK)
