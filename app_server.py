# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# app_server.py

# Basado en:
# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876

# Importacion de librerias necesarias
# Logging para escribir los logs
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

# Importacion de las configuracion del App Server
import app_server_config as config
# Importacion de clases necesarias
from src import home, authserver_relay, game_progress, high_scores,\
                requestlog, helpers

# Inicializacion de la api
app = Flask(__name__)
api = Api(app)

# Inicializacion del parser de request ID
RequestID(app)

# Habilitacion de CORS
CORS(app)

# Inicializacion de la base de datos, MongoDB
app.config["MONGO_URI"] = "mongodb://" + \
                          config.mongodb_username + \
                          ":" + \
                          config.mongodb_password + \
                          "@" + \
                          config.mongodb_hostname + \
                          "/" + \
                          config.mongodb_database + \
                          "?ssl=" + \
                          config.mongodb_ssl +\
                          ("" if (config.mongodb_replica_set == "None") else
                              ("&replicaSet=" +
                                  config.mongodb_replica_set)) + \
                          ("" if (config.mongodb_auth_source) == "None" else
                              ("&authSource=" +
                                  config.mongodb_auth_source)) + \
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
                 config.api_path + "/adminusers")
api.add_resource(authserver_relay.AdminUser,
                 config.api_path + "/adminusers/<string:username>")
api.add_resource(authserver_relay.AdminUserSessions,
                 config.api_path + "/adminusers/<string:username>/sessions")
api.add_resource(authserver_relay.AllUsers,
                 config.api_path + "/users")
api.add_resource(authserver_relay.User,
                 config.api_path + "/users/<string:username>")
api.add_resource(authserver_relay.UserAvatar,
                 config.api_path + "/users/<string:username>/avatar")
api.add_resource(authserver_relay.UserExists,
                 config.api_path + "/users/<string:username>/exists")
api.add_resource(authserver_relay.UserSessions,
                 config.api_path + "/users/<string:username>/sessions")
api.add_resource(high_scores.UserHighscores,
                 config.api_path + "/users/<string:username>/highscores")
api.add_resource(game_progress.UserProgress,
                 config.api_path + "/users/<string:username>/gameprogress")
api.add_resource(authserver_relay.AllSessions,
                 config.api_path + "/sessions")
api.add_resource(authserver_relay.Session,
                 config.api_path + "/sessions/<string:token>")
api.add_resource(authserver_relay.AllRecovery,
                 config.api_path + "/recovery")
api.add_resource(authserver_relay.Recovery,
                 config.api_path + "/recovery/<string:username>")
api.add_resource(authserver_relay.AuthRequestLog,
                 config.api_path + "/requestlogauthserver")
api.add_resource(requestlog.RequestLog,
                 config.api_path + "/requestlog")
api.add_resource(game_progress.AllProgress,
                 config.api_path + "/gameprogress")
api.add_resource(game_progress.Progress,
                 config.api_path + "/gameprogress/<string:id>")
api.add_resource(high_scores.AllHighScores,
                 config.api_path + "/highscores")
api.add_resource(high_scores.HighScores,
                 config.api_path + "/highscores/<string:id>")

# Wrappeamos con Talisman a la aplicacion Flask
# Solo permitimos http para el ambiente de desarrollo
Talisman(app,
         force_https=(False if config.app_env == "DEV" else True),
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
    ENVIRONMENT_DEBUG = config.app_debug
    ENVIRONMENT_PORT = config.app_port
    # Logueo de los valores configurados mediante variables de entorno
    helpers.config_log()
    app.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
