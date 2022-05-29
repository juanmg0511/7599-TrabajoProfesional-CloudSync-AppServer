# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# src/helpers.py

# Basado en:
# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876

# Importacion de librerias necesarias
# OS para leer variables de entorno y logging para escribir los logs
from datetime import datetime
# Flask, para la implementacion del servidor REST
from flask_log_request_id import current_request_id
# Wraps, para implementacion de decorators
from functools import wraps

# Importacion del archivo principal
import app_server as appServer


# Decorator que loguea el request ID de los headers como info
def log_reqId(view_function):
    @wraps(view_function)
    def check_and_log_req_id(*args, **kwargs):
        appServer.app.logger.info(log_request_id() +
                                  "Request ID: \"" +
                                  str(current_request_id()) +
                                  "\".")
        return view_function(*args, **kwargs)
    return check_and_log_req_id


# Funcion que loguea los parametros configurados en variables de entorno
def config_log():

    if (appServer.app_env != "PROD"):
        appServer.app.logger.info("*****************************************")
        appServer.app.logger.info("This server is: " + appServer.app_env)
        appServer.app.logger.info("*****************************************")

    appServer.app.logger.debug("API key for AuthServer is: \"" +
                               str(appServer.api_auth_client_id) +
                               "\".")
    appServer.app.logger.info("AuthServer base URL is: " +
                              str(appServer.api_auth_client_url) +
                              "\".")

    return 0


# Funcion que devuelve los return de los requests
def return_request(message, status):

    # Loguea el mensaje a responder, y su codigo HTTP
    appServer.app.logger.debug(log_request_id() + str(message))
    appServer.app.logger.info(log_request_id() +
                              "Returned HTTP: " +
                              str(status.value))

    return message, status


# Funcion que chequea si un string esta vacio
def non_empty_string(s):
    if not s:
        raise ValueError("Must not be empty string.")
    return s


# Funcion que chequea si una fecha es valida
def non_empty_date(d):
    try:
        d = datetime.strptime(d, "%Y-%m-%d")
    except Exception:
        raise ValueError("Must be valid date.")
    return d


# Funcion que devuelve el request id, o None si no aplica
# formateado para el log default de Gunicorn
def log_request_id():
    return "[" + str(current_request_id()) + "] "
