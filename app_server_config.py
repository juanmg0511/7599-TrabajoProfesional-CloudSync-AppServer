# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# app_server_config.py

# Basado en:
# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876

# Importacion de librerias necesarias
# OS para leer variables de entorno
import os


###############################################################################
#
# Seccion de Configuracion
#
###############################################################################


# Version de API y Server
api_version = "1"
server_version = "1.00"


# Agregamos un root para todos los enpoints, con la api version
api_path = "/api/v" + api_version


###############################################################################
#
# Seccion de Valores por default
#
###############################################################################


# Solo para ejecutar en forma directa!
app_debug_default = True
app_port_default = 8000


# Para todos los modos
app_env_default = "DEV"
page_max_size_default = 100
prune_interval_stats_seconds_default = 86400
stats_days_to_keep_default = 30
api_auth_client_id_default = "44dd22ca-836d-40b6-aa49-7981ded03667"
api_auth_client_url_default = "http://127.0.0.1:81"
api_auth_client_path_default = "api"
api_auth_client_version_default = "v1"
mongodb_hostname_default = "127.0.0.1"
mongodb_database_default = "app-server-db"
mongodb_log_database_default = "app-server-log"
mongodb_username_default = "appserveruser"
mongodb_password_default = "*"
mongodb_ssl_default = "false"
mongodb_replica_set_default = "None"
mongodb_auth_source_default = "None"
username_max_length_default = 64


###############################################################################
#
# Seccion de lectura de variables de entorno
# Lee de docker-compose.yml al ejecutar el ambiente DEV
#
###############################################################################


# Lectura de la configuración de ambiente
app_env = os.environ.get("APP_ENV",
                         app_env_default)
app_debug = os.environ.get("APP_DEBUG",
                           app_debug_default)
app_port = os.environ.get("APP_PORT", os.environ.get("PORT",
                          app_port_default))


# Lectura de la longitud maxima para usernames
username_max_length = os.environ.get("USERNAME_MAX_LENGTH",
                                     username_max_length_default)


# Lectura del tamanio maximo de pagina para la devolucion de resultados
page_max_size = os.environ.get("PAGE_MAX_SIZE",
                               page_max_size_default)


# Lectura del intervalo de limpieza de recovery, en segundos
prune_interval_stats = \
    os.environ.get("PRUNE_INTERVAL_STATS_SECONDS",
                   prune_interval_stats_seconds_default)


# Lectura de la cantidad de dias que deben mantenerse los stats
stats_days_to_keep = os.environ.get("STATS_DAYS_TO_KEEP",
                                    stats_days_to_keep_default)


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
mongodb_log_database = os.environ.get("MONGODB_LOG_DATABASE",
                                      mongodb_log_database_default)
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
