# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# src/helpers.py

# Basado en:
# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876

# Importacion de librerias necesarias
# OS para leer variables de entorno y logging para escribir los logs
import uuid
import re
from datetime import datetime
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


# Funcion que devuelve el mensaje de error en caso que se produzca algun
# problema durante la ejecucion de una operacion con la base de datos de
# logs
def handleLogDatabasebError(e):

    appServer.app.logger.warning(log_request_id() + "Error excecuting a " +
                                 "log database operation: " +
                                 str(e))

    return


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
    appServer.app.logger.debug("Log database name: " +
                               config.mongodb_log_database)
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

    appServer.app.logger.info("Prune interval for stats is: " +
                              str(config.prune_interval_stats) +
                              " seconds.")
    appServer.app.logger.info("Time period to keep stats is: " +
                              str(config.stats_days_to_keep) +
                              " days.")
    appServer.app.logger.info("CORS allowed origins: " +
                              str(config.cors_allowed_origins))
    appServer.app.logger.info("Force HTTPS: " +
                              str(config.talisman_force_https))
    if (config.talisman_force_https is False):
        appServer.app.logger.warning("Force HTTPS is DISABLED. " +
                                     "Please review Talisman config.")
    return 0


# Funcion que limpia la collection de stats de registros viejos
def prune_stats():

    # Comienzo del proceso
    appServer.app.logger.info("prune_stats: starting...")

    # Limpieza de stats
    try:
        statsToKeep = appServer.db_log.stats.find().\
            skip(0).\
            limit(int(config.stats_days_to_keep)).\
            sort("date", -1)

        idsStatsToKeep = []
        for stat in statsToKeep:
            idsStatsToKeep.append(stat["_id"])

        result = appServer.db_log.stats.delete_many({
            "_id": {"$nin": idsStatsToKeep}
        })
        statsDeleted = result.deleted_count

    except Exception as e:
        return handleLogDatabasebError(e)

    appServer.app.logger.info("prune_stats: deleted " +
                              str(statsDeleted) +
                              " expired stats records.")

    # Fin del proceso
    appServer.app.logger.info("prune_stats: done.")

    # Armamos el documento a guardar en la base de datos
    pruneLog = {
        "log_type": "task",
        "request_date": datetime.utcnow().isoformat(),
        "task_type": "prune old stats records",
        "api_version": "v" + config.api_version,
        "pruned_stats": statsDeleted
    }
    try:
        appServer.db_log.requestlog.insert_one(pruneLog)
    except Exception as e:
        return handleLogDatabasebError(e)
    appServer.app.logger.debug('Prune expired stat records: ' +
                               'task data successfully logged to DB.')

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


# Funcion que chequea si un nombre de usario es seguro para usar como filtro
def non_empty_and_safe_filter_username(u):

    if (not re.match("^[a-zA-Z0-9_.]+$", u)):
        raise ValueError("Invalid username.")
    return u


# Funcion que devuelve el request id, o None si no aplica
# formateado para el log default de Gunicorn
def log_request_id():
    return "[" + str(current_request_id()) + "] "


# Devuelve el contenido del archivo pasado por parametro
def loadTextFile(path):
    try:
        with open(path, "r") as path_fp:
            return str(path_fp.read())
    except Exception as e:
        return e
