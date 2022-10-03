# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# src/helpers.py

# Basado en:
# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876

# Importacion de librerias necesarias
# OS para leer variables de entorno y logging para escribir los logs
import sys
import uuid
from datetime import datetime, timedelta
# Flask, para la implementacion del servidor REST
from flask import g
from flask import request
from flask_log_request_id import current_request_id
from http import HTTPStatus
# Python-Usernames, para la validacion de nombres de usuario
from usernames import is_safe_username
# Wraps, para implementacion de decorators
from functools import wraps

# Importacion de las configuracion del App Server
import app_server_config as config
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


# Decorator que chequea si el token del request es valido
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

        appServer.app.logger.debug(log_request_id() +
                                   "Valid session token provided: \"" +
                                   g.session_token +
                                   "\".")
        appServer.app.logger.info(log_request_id() +
                                  "Valid user \"" +
                                  g.session_username +
                                  "\" session with " +
                                  g.session_role +
                                  " privileges.")

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


# Funcion que devuelve el mensaje de error y se encarga de finalizar el
# request en caso que se produzca algun problema durante la ejecucion de
# una operacion con la base de datos
def handleDatabasebError(e):

    appServer.app.logger.error(log_request_id() + "Error excecuting a " +
                               "database operation. Please try again later.")

    DatabaseErrorResponse = {
        "code": -1,
        "message": "Error excecuting a database operation. " +
                   "Please try again later.",
        "data": str(e)
    }

    return return_request(DatabaseErrorResponse,
                          HTTPStatus.SERVICE_UNAVAILABLE)


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

    if (config.app_env != "PROD"):
        appServer.app.logger.warning("**************************************")
        appServer.app.logger.warning("* This server is: " + config.app_env)
        appServer.app.logger.warning("**************************************")

    appServer.app.logger.info("Database server: " +
                              config.mongodb_hostname)
    appServer.app.logger.debug("Database name: " +
                               config.mongodb_database)
    appServer.app.logger.debug("Database username: " +
                               config.mongodb_username)
    appServer.app.logger.debug("Database using SSL: " +
                               config.mongodb_ssl)
    appServer.app.logger.info("Database replica set: " +
                              config.mongodb_replica_set)
    appServer.app.logger.debug("Database auth source: " +
                               config.mongodb_auth_source)

    appServer.app.logger.debug("API key for AuthServer is: \"" +
                               str(config.api_auth_client_id) +
                               "\".")
    appServer.app.logger.info("AuthServer base URL is: \"" +
                              str(config.api_auth_client_url) +
                              "\".")
    appServer.app.logger.info("AuthServer API path is: \"" +
                              str(config.api_auth_client_path) +
                              "\".")
    appServer.app.logger.info("AuthServer API version is: \"" +
                              str(config.api_auth_client_version) +
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


# Funcion que chequea si un nombre de usario es valido
#
# https://pypi.org/project/python-usernames/
#
# Provides a default regex validator.
# Validates against list of banned words that should not be used as username.
#
# The default regular expression is as follows:
# ^                  beginning of string
# (?!_$)             no only _
# (?![-.])           no - or . at the beginning
# (?!.*[_.-]{2})     no __ or _. or ._ or .. or -- inside
# [a-zA-Z0-9_.-]+    allowed characters, atleast one must be present
# (?<![.-])          no - or . at the end
# $                  end of string
def non_empty_and_safe_username(u):
    if is_safe_username(u,
                        max_length=int(
                            config.username_max_length)) is False:
        raise ValueError("Invalid username.")
    return u


# Funcion que devuelve el request id, o None si no aplica
# formateado para el log default de Gunicorn
def log_request_id():
    return "[" + str(current_request_id()) + "] "


# Funcion que calcula las estadisticas de uso del servidor
def gatherStats(startdate, enddate, sort_ascending):

    # Calculamos numero de dias pedidos
    number_days = abs((enddate - startdate).days) + 1

    dailyStats = []
    for day in range(number_days):
        if (sort_ascending is True):
            date = startdate + timedelta(days=day)
        else:
            date = enddate - timedelta(days=day)

        # Calculos sobre requests
        requests_number = 0
        requests_highscores = 0
        requests_game_progress = 0
        requests_auth_api = 0
        requests_error_400 = 0
        requests_error_401 = 0
        requests_error_404 = 0
        requests_error_405 = 0
        requests_error_500 = 0
        requests_error_503 = 0
        # Calculos sobre requests
        response_time_max = 0
        response_time_min = sys.float_info.max
        # Calculos sobre datos
        requests_highscores_post = 0
        requests_highscores_delete = 0
        requests_game_progress_post = 0
        requests_game_progress_delete = 0

        # Tomamos los requests del dia, y hacemos los calculos
        try:
            day_requests = appServer.\
                db.\
                requestlog.\
                find({"$and": [{"request_date": {"$regex": str(date.date())}},
                     {"log_type": "request"}]})
        except Exception as e:
            return handleDatabasebError(e)
        while True:
            try:
                record = day_requests.next()
            except StopIteration:
                break

            requests_number += 1

            if (float(record["duration"]) < response_time_min):
                response_time_min = float(record["duration"])
            if (float(record["duration"]) > response_time_max):
                response_time_max = float(record["duration"])

            if ("/highscores" in record["path"]):
                requests_highscores += 1
                if (("POST" in record["method"])
                   and (str(HTTPStatus.CREATED.value)
                   in str(record["status"]))):
                    requests_highscores_post += 1
                if (("DELETE" in record["method"])
                   and (str(HTTPStatus.OK.value) in str(record["status"]))):
                    requests_highscores_delete += 1

            if ("/gameprogress" in record["path"]):
                requests_game_progress += 1
                if (("POST" in record["method"])
                   and (str(HTTPStatus.CREATED.value
                        or str(HTTPStatus.CREATED.value))
                   in str(record["status"]))):
                    requests_game_progress_post += 1
                if (("DELETE" in record["method"])
                   and (str(HTTPStatus.OK.value) in str(record["status"]))):
                    requests_game_progress_delete += 1

            if (("/users" in record["path"])
               or ("/adminusers" in record["path"])
               or ("/sessions" in record["path"])
               or ("/recovery" in record["path"])):
                requests_auth_api += 1

            if (str(HTTPStatus.BAD_REQUEST.value) in str(record["status"])):
                requests_error_400 += 1

            if (str(HTTPStatus.UNAUTHORIZED.value) in str(record["status"])):
                requests_error_401 += 1

            if (str(HTTPStatus.NOT_FOUND.value) in str(record["status"])):
                requests_error_404 += 1

            if (str(HTTPStatus.METHOD_NOT_ALLOWED.value)
               in str(record["status"])):
                requests_error_405 += 1

            if (str(HTTPStatus.INTERNAL_SERVER_ERROR.value)
               in str(record["status"])):
                requests_error_500 += 1

            if (str(HTTPStatus.SERVICE_UNAVAILABLE.value)
               in str(record["status"])):
                requests_error_503 += 1

        if (requests_number == 0):
            response_time_min = 0
            endpoint_most_requests = None
        else:
            requests = {requests_highscores: "/highscores",
                        requests_game_progress: "/gameprogress"}
            endpoint_most_requests = str(requests.get(max(requests)))

        # Registro a devolver en la respuesta, para cada dia
        stat = {
            # fecha
            "date": str(date.date()),
            # cant requests en el dia
            "requests_number": str(requests_number),
            # hits endpoint users
            # hits endpoint adminusers
            # hits endpoint sessions
            # hits endpoint recovery
            # requests por minuto para el dia
            "requests_highscores": str(requests_highscores),
            "requests_game_progress": str(requests_game_progress),
            "requests_auth_api": str(requests_auth_api),
            "requests_per_minute": str(float("{:.4f}".
                                       format(requests_number/1440))),
            "endpoint_most_requests": endpoint_most_requests,
            # tiempo de respuesta maximo
            # tiempo de respuesta minimo
            # tiempo de respuesta promedio
            "response_time_max": str(float("{:.4f}".
                                     format(response_time_max))),
            "response_time_min": str(float("{:.4f}".
                                     format(response_time_min))),
            "response_time_avg":  str(float("{:.4f}".
                                      format((response_time_max +
                                              response_time_min)/2))),
            # cantidad de usuarios nuevos
            # cantidad de usuario dados de baja
            # cantidad de sesiones abiertas
            # cantidad de sesiones cerradas
            # cantidad recovery abiertos
            "highscores_new": str(requests_highscores_post),
            "highscores_deleted": str(requests_highscores_delete),
            "game_progress_saved": str(requests_game_progress_post),
            "game_progress_deleted": str(requests_game_progress_delete),
            # errores 500
            "requests_error_400": str(requests_error_400),
            "requests_error_401": str(requests_error_401),
            "requests_error_404": str(requests_error_404),
            "requests_error_405": str(requests_error_405),
            "requests_error_500": str(requests_error_500),
            "requests_error_503": str(requests_error_503)
        }
        dailyStats.append(stat)

    # Respuesta de estadisticas, incluye estadisticas generales
    # y la lista de dias
    try:
        statsResult = {
                "request_date:":
                datetime.utcnow().isoformat(),
                "requested_days":
                number_days,
                "registered_higshscores":
                appServer.db.highscores.count_documents({}),
                "registered_game_progress":
                appServer.db.gameprogress.count_documents({}),
                "daily_stats":
                dailyStats
            }
    except Exception as e:
        return handleDatabasebError(e)

    return statsResult
