# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# app_server.py

# Basado en:
# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876

# Importacion de librerias necesarias
# OS para leer variables de entorno y logging para escribir los logs
import os
import logging
# Flask, para la implementacion del servidor REST
from flask import Flask
from flask import g
from flask_restful import Api
from flask_log_request_id import RequestID
from flask_cors import CORS
# PyMongo para el manejo de MongoDB
from flask_pymongo import PyMongo
# Flask-Talisman para el manejo de SSL
from flask_talisman import Talisman

# Importacion de clases necesarias
from src import home, authserver_relay, game_progress, high_scores,\
                requestlog, helpers

# Version de API y Server
api_version = "1"
server_version = "1.00"

# Valores default
# Solo para ejecutar en forma directa!
app_debug_default = True
app_port_default = 8000

# Para todos los modos
app_env_default = "DEV"
api_auth_client_id_default = "44dd22ca-836d-40b6-aa49-7981ded03667"
api_auth_client_url_default = "http://127.0.0.1:81"
api_auth_client_path_default = "api"
api_auth_client_version_default = "v1"
mongodb_hostname_default = "127.0.0.1"
mongodb_database_default = "app-server-db"
mongodb_username_default = "appserveruser"
mongodb_password_default = "*"
mongodb_ssl_default = "false"
mongodb_replica_set_default = "None"
mongodb_auth_source_default = "None"

# Agregamos un root para todos los enpoints, con la api version
api_path = "/api/v" + api_version

# Inicializacion de la api
app = Flask(__name__)
api = Api(app)

# Inicializacion del parser de request ID
RequestID(app)

# Habilitacion de CORS
CORS(app)

# Lectura de la configuración de ambiente
app_env = os.environ.get("APP_ENV",
                         app_env_default)
# Lectura de la API KEY utilizada por el AuthServer
api_auth_client_id = os.environ.get("API_AUTH_CLIENT_ID",
                                    api_auth_client_id_default)
# Lectura de la URL de conexion al AuthServer
api_auth_client_url = os.environ.get("API_AUTH_CLIENT_URL",
                                     api_auth_client_url_default)
api_auth_client_path = os.environ.get("API_AUTH_CLIENT_PATH",
                                      api_auth_client_path_default)
api_auth_client_version = os.environ.get("API_AUTH_CLIENT_VERSION",
                                         api_auth_client_version_default)
# Lectura de la configuracion del servidor de base de datos
mongodb_hostname = os.environ.get("MONGODB_HOSTNAME",
                                  mongodb_hostname_default)
mongodb_database = os.environ.get("MONGODB_DATABASE",
                                  mongodb_database_default)
mongodb_username = os.environ.get("MONGODB_USERNAME",
                                  mongodb_username_default)
mongodb_password = os.environ.get("MONGODB_PASSWORD",
                                  mongodb_password_default)
mongodb_ssl = os.environ.get("MONGODB_SSL",
                             mongodb_ssl_default)
mongodb_replica_set = os.environ.get("MONGODB_REPLICA_SET",
                                     mongodb_replica_set_default)
mongodb_auth_source = os.environ.get("MONGODB_AUTH_SOURCE",
                                     mongodb_auth_source_default)


# Inicializacion de la base de datos, MongoDB
app.config["MONGO_URI"] = "mongodb://" + \
                          mongodb_username + \
                          ":" + \
                          mongodb_password + \
                          "@" + \
                          mongodb_hostname + \
                          "/" + \
                          mongodb_database + \
                          "?ssl=" + \
                          mongodb_ssl +\
                          ("" if (mongodb_replica_set == "None") else
                              ("&replicaSet=" + mongodb_replica_set)) + \
                          ("" if (mongodb_auth_source) == "None" else
                              ("&authSource=" + mongodb_auth_source)) + \
                          "&retryWrites=true" + \
                          "&w=majority"

mongo = PyMongo(app)
db = mongo.db
cl = mongo.cx


# Inicializacion - para cuando ejecuta gunicorn + flask
# Server hook "on_starting", ejecuta 1 sola vez antes de forkear los workers
def on_starting(server):
    # Ejemplos de logs, para los distintos niveles
    # app.logger.debug('This is a DEBUG message!')
    # app.logger.info('This is an INFO message!')
    # app.logger.warning('This is a WARNING message!')
    # app.logger.error('This is an ERROR message!')
    # app.logger.critical('This is a CRITICAL message!')

    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.logger.debug("Log system configured for Gunicorn.")

    # Logueo de los valores configurados mediante variables de entorno
    helpers.config_log()


# Request log, inicializacion de los decorators
# Llamada antes de cada request
@app.before_request
def before_request():
    app.logger.debug(helpers.log_request_id() +
                     'Excecuting before request actions.')
    # Valores necesarios para procesar los requests
    g.request_id = None
    g.user_agent = None
    g.session_username = None
    g.session_role = None
    g.session_token = None
    g.session_admin = None
    # Inicializacion de valores
    # El token de sesion y el rol del usurio
    # se inicizan por medio de helpers.check_token,
    # utilizado como decorator en los requests que
    # necesitan autorizacion
    helpers.request_id()
    helpers.user_agent()
    helpers.is_admin()

    requestlog.start_timer()


# Llamada luego de cada request
@app.after_request
def after_request(response):
    app.logger.debug(helpers.log_request_id() +
                     'Excecuting after request actions.')
    requestlog.log_request(response)
    response.headers.add('X-Request-ID', g.request_id)

    return response


# Defincion de los endpoints del server
api.add_resource(home.Home,
                 "/")
api.add_resource(home.Ping,
                 "/ping")
api.add_resource(home.Stats,
                 "/stats")
api.add_resource(home.Status,
                 "/status")
api.add_resource(authserver_relay.AllAdminUsers,
                 api_path + "/adminusers")
api.add_resource(authserver_relay.AdminUser,
                 api_path + "/adminusers/<string:username>")
api.add_resource(authserver_relay.AdminUserSessions,
                 api_path + "/adminusers/<string:username>/sessions")
api.add_resource(authserver_relay.AllUsers,
                 api_path + "/users")
api.add_resource(authserver_relay.User,
                 api_path + "/users/<string:username>")
api.add_resource(authserver_relay.UserAvatar,
                 api_path + "/users/<string:username>/avatar")
api.add_resource(authserver_relay.UserExists,
                 api_path + "/users/<string:username>/exists")
api.add_resource(authserver_relay.UserSessions,
                 api_path + "/users/<string:username>/sessions")
api.add_resource(authserver_relay.AllSessions,
                 api_path + "/sessions")
api.add_resource(authserver_relay.Session,
                 api_path + "/sessions/<string:token>")
api.add_resource(authserver_relay.AllRecovery,
                 api_path + "/recovery")
api.add_resource(authserver_relay.Recovery,
                 api_path + "/recovery/<string:username>")
api.add_resource(authserver_relay.AuthRequestLog,
                 api_path + "/requestlogauthserver")
api.add_resource(requestlog.RequestLog,
                 api_path + "/requestlog")
api.add_resource(game_progress.AllProgress,
                 api_path + "/gameprogress")
api.add_resource(game_progress.Progress,
                 api_path + "/gameprogress/<string:username>")
api.add_resource(high_scores.AllHighScores,
                 api_path + "/highscores")
api.add_resource(high_scores.HighScores,
                 api_path + "/highscores/<string:username>")

# Wrappeamos con Talisman a la aplicacion Flask
# Solo permitimos http para el ambiente de desarrollo
Talisman(app,
         force_https=(False if app_env == "DEV" else True),
         content_security_policy=None)

# Inicio del server en forma directa con WSGI
# Toma el puerto y modo de las variables de entorno
# PORT
# APP_DEBUG - "True, False"
if __name__ == '__main__':
    # Si se ejecuta con WSGI, el log level es DEBUG
    app.logger.setLevel("DEBUG")
    app.logger.debug("Log system configured for WSGI.")
    # Seteo de modo debug y puerto - tomado de variables de entorno
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG",
                                       app_debug_default)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", os.environ.get("PORT",
                                      app_port_default))
    # Logueo de los valores configurados mediante variables de entorno
    helpers.config_log()
    app.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
