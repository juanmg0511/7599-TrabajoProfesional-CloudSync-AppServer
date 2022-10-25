# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# src/stats.py

# Basado en:
# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876

# Importacion de librerias necesarias
# OS para leer variables de entorno y logging para escribir los logs
import time
import sys
from datetime import date, datetime
# Flask, para la implementacion del servidor REST
from flask import g, request, json
from flask_restful import Resource, reqparse
from http import HTTPStatus
from bson import json_util

# Importacion de las configuracion del App Server
import app_server_config as config
# Importacion del archivo principal y helpers
import app_server as appServer
from src import helpers


# Funcion que actualiza en la base de datos las estadisticas del dia
def update_stats(response):
    appServer.app.logger.debug(helpers.log_request_id() +
                               'Updating daily stats data in DB.')

    # Escapeamos paths que no son de la api
    if (not(config.api_path in request.path)):
        appServer.app.logger.debug(helpers.log_request_id() +
                                   'Request is not from API path, skipping.')
        return response

    # Buscamos el registro de stats en la base de datos
    try:
        today_stats = appServer.\
                      db_log.\
                      stats.\
                      find_one({"date": {"$regex": str(date.today())}})
    except Exception as e:
        return helpers.handleLogDatabasebError(e)

    # Por default, vamos a asumir que no existe y que hay que
    # crearlo
    new_record = True
    if today_stats is not None:
        new_record = False

    # Inicializacion de variables para los calculos
    # Calculos sobre requests
    requests_number = 0 if new_record is True \
        else today_stats["requests_number"]
    requests_highscores = 0 if new_record is True \
        else today_stats["requests_highscores"]
    requests_game_progress = 0 if new_record is True \
        else today_stats["requests_game_progress"]
    requests_auth_api = 0 if new_record is True \
        else today_stats["requests_auth_api"]
    requests_error_400 = 0 if new_record is True \
        else today_stats["requests_error_400"]
    requests_error_401 = 0 if new_record is True \
        else today_stats["requests_error_401"]
    requests_error_404 = 0 if new_record is True \
        else today_stats["requests_error_404"]
    requests_error_405 = 0 if new_record is True \
        else today_stats["requests_error_405"]
    requests_error_500 = 0 if new_record is True \
        else today_stats["requests_error_500"]
    requests_error_503 = 0 if new_record is True \
        else today_stats["requests_error_503"]
    # Calculos sobre requests
    response_time_max = 0 if new_record is True \
        else today_stats["response_time_max"]
    response_time_min = sys.float_info.max if new_record is True \
        else today_stats["response_time_min"]
    response_time_avg = 0
    # Calculos sobre usuarios
    requests_highscores_post = 0 if new_record is True \
        else today_stats["highscores_new"]
    requests_highscores_delete = 0 if new_record is True \
        else today_stats["highscores_deleted"]
    requests_game_progress_post = 0 if new_record is True \
        else today_stats["game_progress_saved"]
    requests_game_progress_put = 0 if new_record is True \
        else today_stats["game_progress_updated"]
    requests_game_progress_delete = 0 if new_record is True \
        else today_stats["game_progress_deleted"]

    # Calculos y formatos de la informacion
    requests_number += 1

    now = time.time()
    duration = round(now - g.start, 6)

    if (duration < response_time_min):
        response_time_min = duration
    if (duration > response_time_max):
        response_time_max = duration
    response_time_avg = (response_time_min + response_time_max) / 2

    if ("/highscores" in request.path):
        requests_highscores += 1
        if (("POST" in request.method) and (str(HTTPStatus.CREATED.value) in
           str(response.status))):
            requests_highscores_post += 1
        if (("DELETE" in request.method) and (str(HTTPStatus.OK.value) in
           str(response.status))):
            requests_highscores_delete += 1

    if ("/gameprogress" in request.path):
        requests_game_progress += 1
        if (("POST" in request.method) and (str(HTTPStatus.CREATED.value) in
           str(response.status))):
            requests_game_progress_post += 1
        if (("PUT" in request.method) and (str(HTTPStatus.CREATED.value) in
           str(response.status))):
            requests_game_progress_post += 1
        if (("PUT" in request.method) and (str(HTTPStatus.OK.value) in
           str(response.status))):
            requests_game_progress_put += 1
        if (("DELETE" in request.method) and (str(HTTPStatus.OK.value) in
           str(response.status))):
            requests_game_progress_delete += 1

    if (("/users" in request.path)
       or ("/adminusers" in request.path)
       or ("/sessions" in request.path)
       or ("/recovery" in request.path)):
        requests_auth_api += 1

    if (str(HTTPStatus.BAD_REQUEST.value)
       in str(response.status)):
        requests_error_400 += 1

    if (str(HTTPStatus.UNAUTHORIZED.value)
       in str(response.status)):
        requests_error_401 += 1

    if (str(HTTPStatus.NOT_FOUND.value)
       in str(response.status)):
        requests_error_404 += 1

    if (str(HTTPStatus.METHOD_NOT_ALLOWED.value)
       in str(response.status)):
        requests_error_405 += 1

    if (str(HTTPStatus.INTERNAL_SERVER_ERROR.value)
       in str(response.status)):
        requests_error_500 += 1

    if (str(HTTPStatus.SERVICE_UNAVAILABLE.value)
       in str(response.status)):
        requests_error_503 += 1

    # Registro a crear/actualizar en la DB, para cada dia
    stat = {
        # fecha
        "date": str(date.today()) if new_record is True \
        else today_stats["date"],
        # cant requests en el dia
        "requests_number": requests_number,
        # hits endpoint highscores
        # hits endpoint gameprogress
        # hits endpoint authapi
        # requests por minuto para el dia (parcial hasta el ultimo update)
        "requests_highscores": requests_highscores,
        "requests_game_progress": requests_game_progress,
        "requests_auth_api": requests_auth_api,
        "requests_per_minute": requests_number/1440,
        # tiempo de respuesta maximo
        # tiempo de respuesta minimo
        # tiempo de respuesta promedio
        "response_time_max": response_time_max,
        "response_time_min": response_time_min,
        "response_time_avg": response_time_avg,
        # cantidad de highscores nuevos
        # cantidad de highscores borrados
        # cantidad de gameprogress guardados
        # cantidad de gameprogress borrados
        # cantidad recovery abiertos
        "highscores_new": requests_highscores_post,
        "highscores_deleted": requests_highscores_delete,
        "game_progress_saved": requests_game_progress_post,
        "game_progress_updated": requests_game_progress_put,
        "game_progress_deleted": requests_game_progress_delete,
        # errores 40X y 50X
        "requests_error_400": requests_error_400,
        "requests_error_401": requests_error_401,
        "requests_error_404": requests_error_404,
        "requests_error_405": requests_error_405,
        "requests_error_500": requests_error_500,
        "requests_error_503": requests_error_503
    }

    # Insertamos o actualizamos el registro en la base de datos
    try:
        if new_record is True:
            appServer.db_log.stats.insert_one(
                stat)
        else:
            appServer.db_log.stats.update_one(
                {"date": stat["date"]}, {'$set': stat})
    except Exception as e:
        return helpers.handleLogDatabasebError(e)

    appServer.app.logger.debug(helpers.log_request_id() +
                               'Daily stats data successfully updated in DB.')

    return response


# Clase que entrega estadisticas del uso del servidor
class Stats(Resource):

    # verbo GET - obtener registros de estadisticas
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def get(self):
        appServer.app.logger.info(helpers.log_request_id() +
                                  'Server stats requested.')
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("sortascending", type=helpers.non_empty_string,
                                required=False, nullable=True)
            args = parser.parse_args()

        except Exception:
            statsResponseGet = {
                "code": -1,
                "message": "Bad request. Missing or wrong format for " +
                           "required arguments.",
                "data": None
            }
            return helpers.return_request(statsResponseGet,
                                          HTTPStatus.BAD_REQUEST)

        sort_ascending = str(args.get("sortascending", "False"))
        if (str(sort_ascending).
           lower().
           replace("\"", "").
           replace("'", "") == "true"):
            sort_ascending = 1
        else:
            sort_ascending = -1

        appServer.app.logger.debug(helpers.log_request_id() +
                                   "Sort ascending: " +
                                   str(sort_ascending))

        # Respuesta de estadisticas, incluye estadisticas generales
        # y la lista de dias
        try:
            # Obtenemos los registros de estadisticas
            daylyStatsCount = appServer.db_log.stats.\
                count_documents({})

            query_start = 0
            if ((daylyStatsCount > int(config.stats_days_to_keep)) and
               (sort_ascending == 1)):
                query_start = 1

            dailyStats = appServer.db_log.stats.\
                find({}).\
                skip(query_start).\
                limit(int(config.stats_days_to_keep)).\
                sort("date", sort_ascending)
            dailyStatsDict = [doc for doc in dailyStats]
            dailyStatsDictJson = json.\
                dumps(dailyStatsDict, default=json_util.default)
            dailyStatsArray = json.loads(dailyStatsDictJson)

            # Construimos la respuesta a devolver
            statsResponseGet = {
                "request_date:":
                datetime.utcnow().isoformat(),
                "registered_higshscores":
                appServer.db.highscores.
                count_documents({}),
                "registered_game_progress":
                appServer.db.gameprogress.
                count_documents({}),
                "daily_stats":
                dailyStatsArray
            }
        except Exception as e:
            return helpers.handleDatabasebError(e)

        return helpers.return_request(statsResponseGet, HTTPStatus.OK)
