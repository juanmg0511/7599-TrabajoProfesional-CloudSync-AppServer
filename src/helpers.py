# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# src/helpers.py

# Basado en:
# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876

# Importacion de librerias necesarias
# OS para leer variables de entorno y logging para escribir los logs
import uuid
from datetime import datetime
# Flask, para la implementacion del servidor REST
from flask import g
from flask import request
from flask_log_request_id import current_request_id
from http import HTTPStatus
# Wraps, para implementacion de decorators
from functools import wraps

# Importacion del archivo principal
import app_server as appServer
# Importacion del cliente de AuthServer
from src import authserver_client


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


# Decorator que chequea si el toquen del request es valido
def check_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        session_token = request.headers.get("X-Auth-Token")
        if (not session_token):
            CheckSessionResponse = {
                "code": -1,
                "message": "Authorization token required.",
                "data": None
            }
            return return_request(CheckSessionResponse,
                                  HTTPStatus.UNAUTHORIZED)

        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       get_session(session_token)
        except Exception as e:
            CheckSessionResponse = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return return_request(CheckSessionResponse,
                                  HTTPStatus.SERVICE_UNAVAILABLE)

        if (response.status_code != HTTPStatus.OK):
            return response.json(), response.status_code

        g.session_token = session_token
        g.session_username = response.json()["username"]
        g.session_role = response.json()["user_role"]

        return f(*args, **kwargs)

    return wrapper


# Decorator que denega el acceso al enpoint para los
# usuarios con rol "user"
def deny_user_role(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if (g.session_role == "user"):
            appServer.app.logger.warning(log_request_id() +
                                         "User \"" +
                                         g.session_username +
                                         "\" is trying to access a " +
                                         "restricted endpoint! Please " +
                                         "check the request log for details.")
            DenyUserRoleResponse = {
                "code": -1,
                "message": "You do not have sufficient " +
                           "priviliges to use this resource.",
                "data": None
            }
            return return_request(DenyUserRoleResponse,
                                  HTTPStatus.UNAUTHORIZED)
        return f(*args, **kwargs)
    return wrapper


# Decorator que limita el acceso al enpoint para los
# usuarios con rol "user". Solo pueden operar sobre
# su propio usuario
def limit_own_user_role(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if ((g.session_role == "user")
           and
           (g.session_username not in request.base_url)):
            appServer.app.logger.warning(log_request_id() +
                                         "User \"" +
                                         g.session_username +
                                         "\" is trying to access a " +
                                         "restricted endpoint! Please " +
                                         "check the request log for details.")
            DenyUserRoleResponse = {
                "code": -1,
                "message": "You do not have sufficient " +
                           "priviliges to use this resource.",
                "data": None
            }
            return return_request(DenyUserRoleResponse,
                                  HTTPStatus.UNAUTHORIZED)
        return f(*args, **kwargs)
    return wrapper


# Decorator que limita el acceso al enpoint de sesiones
# para los usuarios con rol "user". Solo pueden operar
# sobre sus propias sesiones
def check_own_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if ((g.session_role == "user")
           and
           (g.session_token not in request.base_url)):
            appServer.app.logger.warning(log_request_id() +
                                         "User \"" +
                                         g.session_username +
                                         "\" is trying to access a " +
                                         "restricted endpoint! Please " +
                                         "check the request log for details.")
            DenyUserRoleResponse = {
                "code": -1,
                "message": "You do not have sufficient " +
                           "priviliges to use this resource.",
                "data": None
            }
            return return_request(DenyUserRoleResponse,
                                  HTTPStatus.UNAUTHORIZED)
        return f(*args, **kwargs)
    return wrapper


# Funcion que devuelve y guarda el requestID actual, o genera uno nuevo en
# caso de encontrarse vacio
def request_id():
    if getattr(g, 'request_id', None):
        return g.request_id

    headers = request.headers

    original_request_id = headers.get("X-Request-ID")
    g.request_id = str(original_request_id or uuid.uuid4())

    return g.request_id


# Funcion que guarda el user agent del request actual
def user_agent():
    g.user_agent = request.headers.get('User-Agent', '*')


# Funcion que detecta la presencia del header X-Admin
# y guarda el resultado
def is_admin():
    g.session_admin = request.headers.get("X-Admin", "").lower() == "true"


# Funcion que loguea los parametros configurados en variables de entorno
def config_log():

    if (appServer.app_env != "PROD"):
        appServer.app.logger.info("*****************************************")
        appServer.app.logger.info("This server is: " + appServer.app_env)
        appServer.app.logger.info("*****************************************")

    appServer.app.logger.debug("API key for AuthServer is: \"" +
                               str(appServer.api_auth_client_id) +
                               "\".")
    appServer.app.logger.info("AuthServer base URL is: \"" +
                              str(appServer.api_auth_client_url) +
                              "\".")
    appServer.app.logger.info("AuthServer API path is: \"" +
                              str(appServer.api_auth_client_path) +
                              "\".")
    appServer.app.logger.info("AuthServer API version is: \"" +
                              str(appServer.api_auth_client_version) +
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
