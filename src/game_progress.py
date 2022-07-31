# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# src/game_progress.py

# Basado en:
# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876

# Importacion de librerias necesarias
# OS para leer variables de entorno y logging para escribir los logs
from datetime import datetime
# Flask, para la implementacion del servidor REST
from flask_restful import Resource, reqparse
from flask import request
from http import HTTPStatus

# Importacion del archivo principal y helpers
import app_server as appServer
from src import helpers


# Clase que define el endpoint para trabajar con game progress
# Operaciones CRUD: Create, Read, Update, Delete
# verbo GET - listar game progress de todos los usuarios
class AllProgress(Resource):
    # verbo GET - listar game progress de todos los usuarios
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def get(self):
        appServer.app.logger.info(helpers.log_request_id() +
                                  'All game progress records requested.')

        try:
            parser = reqparse.RequestParser()
            # Primer registro de la collection a mostrar
            # El indice arranca en 0!
            parser.add_argument("start",
                                type=int,
                                required=False,
                                nullable=False)
            # Cantidad de registros de la collection a
            # mostrar por pagina
            # Si es igual a 0 es como si no estuviera
            parser.add_argument("limit",
                                type=int,
                                required=False,
                                nullable=False)
            args = parser.parse_args()
        except Exception:
            AllProgressResponseGet = {
                "code": -1,
                "message": "Bad request. Missing required arguments.",
                "data": None
            }
            return helpers.return_request(AllProgressResponseGet,
                                          HTTPStatus.BAD_REQUEST)

        # Parseo de los parametros para el pagindo
        query_start = str(args.get("start", 0))
        if (query_start != "None"):
            query_start = int(query_start)
            if (query_start < 0):
                query_start = 0
        else:
            query_start = 0
        query_limit = str(args.get("limit", 0))
        if (query_limit != "None"):
            query_limit = int(query_limit)
            if (query_limit < 0):
                query_limit = 0
        else:
            query_limit = 0

        try:
            allProgress = appServer.db.gameprogress.\
                          find().\
                          skip(query_start).\
                          limit(query_limit)
            allProgressCount = appServer.db.gameprogress.\
                count_documents({})
        except Exception as e:
            return helpers.handleDatabasebError(e)

        # Calculo de las URL hacia anterior y siguiente
        start_previous = query_start - query_limit
        start_next = query_start + query_limit
        if (start_previous < 0
           or (start_previous >= allProgressCount)
           or (query_start == 0 and query_limit == 0)
           or (query_limit == 0)):
            url_previous = None
        else:
            url_previous = request.path +\
                           "?start=" +\
                           str(start_previous) +\
                           "&limit=" +\
                           str(query_limit)

        if (start_next >= allProgressCount
           or (query_start == 0 and query_limit == 0)
           or (query_limit == 0)):
            url_next = None
        else:
            url_next = request.path +\
                       "?start=" +\
                       str(start_next) +\
                       "&limit=" +\
                       str(query_limit)

        AllProgressResultsGet = []
        for existingUser in allProgress:
            retrievedProgress = {
                "id": str(existingUser["_id"]),
                "username": existingUser["username"],
                "next_level": existingUser["next_level"],
                "difficulty_level": existingUser["difficulty_level"],
                "time_elapsed": existingUser["time_elapsed"],
                "gold_collected": existingUser["gold_collected"],
                "date_created": existingUser["date_created"],
                "date_updated": existingUser["date_updated"]
            }
            AllProgressResultsGet.append(retrievedProgress)

        # Construimos la respuesta paginada
        AllProgressResponseGet = {
            "total": allProgressCount,
            "limit": query_limit,
            "next": url_next,
            "previous": url_previous,
            "results": AllProgressResultsGet
        }

        return helpers.return_request(AllProgressResponseGet, HTTPStatus.OK)


# Clase que define el endpoint para trabajar con game progress
# Operaciones CRUD: Create, Read, Update, Delete
# verbo GET - leer registro de game progress
# verbo PUT - actualizar registro completo de game progress,
#             si no existe lo crea
# verbo DELETE - borrar registro de game progress
class Progress(Resource):

    # verbo GET - leer registro de game progress
    @helpers.log_reqId
    @helpers.check_token
    @helpers.limit_own_user_role
    def get(self, username):
        appServer.app.logger.info(helpers.log_request_id() + "Game progress " +
                                  "record for user '" +
                                  username +
                                  "' requested.")

        try:
            existingGameProgress = appServer.db.gameprogress.find_one(
                {"username": username})
        except Exception as e:
            return helpers.handleDatabasebError(e)

        if (existingGameProgress is not None):
            progressResponseGet = {
                "id": str(existingGameProgress["_id"]),
                "username": existingGameProgress["username"],
                "next_level": existingGameProgress["next_level"],
                "difficulty_level": existingGameProgress["difficulty_level"],
                "time_elapsed": existingGameProgress["time_elapsed"],
                "gold_collected": existingGameProgress["gold_collected"],
                "date_created": existingGameProgress["date_created"],
                "date_updated": existingGameProgress["date_updated"]
            }
            return helpers.return_request(progressResponseGet,
                                          HTTPStatus.OK)

        progressResponseGet = {
            "code": -1,
            "message": "Game progress record for user '" +
                       username +
                       "' not found.",
            "data": None
        }
        return helpers.return_request(progressResponseGet,
                                      HTTPStatus.NOT_FOUND)

    # verbo PUT - actualizar registro completo de game progress,
    #             si no existe lo crea
    @helpers.log_reqId
    @helpers.check_token
    @helpers.limit_own_user_role
    def put(self, username):
        appServer.app.logger.info(helpers.log_request_id() + "Game progress " +
                                  "record for user '" +
                                  username +
                                  "'update requested.")

        try:
            parser = reqparse.RequestParser()
            parser.add_argument("next_level", type=int,
                                required=True, nullable=False)
            parser.add_argument("difficulty_level", type=int,
                                required=True, nullable=False)
            parser.add_argument("time_elapsed", type=helpers.non_empty_string,
                                required=True, nullable=False)
            parser.add_argument("gold_collected", type=int,
                                required=True, nullable=False)
            args = parser.parse_args()
        except Exception:
            progressResponsePut = {
                "code": -1,
                "message": "Bad request. Missing required arguments.",
                "data": None
            }
            return helpers.return_request(progressResponsePut,
                                          HTTPStatus.BAD_REQUEST)

        try:
            existingGameProgress = appServer.db.gameprogress.find_one(
                {"username": username})
        except Exception as e:
            return helpers.handleDatabasebError(e)
        if (existingGameProgress is not None):

            progressToUpdate = {
                "next_level": args["next_level"],
                "difficulty_level": args["difficulty_level"],
                "time_elapsed": args["time_elapsed"],
                "gold_collected": args["gold_collected"],
                "date_created": existingGameProgress["date_created"],
                "date_updated": datetime.utcnow().isoformat()
            }

            progressResponsePut = progressToUpdate.copy()
            try:
                appServer.db.gameprogress.update_one(
                    {"username": username}, {'$set': progressToUpdate})
            except Exception as e:
                return helpers.handleDatabasebError(e)
            id_userToUpdate = str(existingGameProgress["_id"])
            progressResponsePut["username"] = existingGameProgress["username"]
            progressResponsePut["id"] = id_userToUpdate

            return helpers.return_request(progressResponsePut, HTTPStatus.OK)
        else:
            progressToInsert = {
                "username": username,
                "next_level": args["next_level"],
                "difficulty_level": args["difficulty_level"],
                "time_elapsed": args["time_elapsed"],
                "gold_collected": args["gold_collected"],
                "date_created": datetime.utcnow().isoformat(),
                "date_updated": None
                }
            progressResponsePut = progressToInsert.copy()
            try:
                appServer.db.gameprogress.insert_one(progressToInsert)
            except Exception as e:
                return helpers.handleDatabasebError(e)
            id_progressToInsert = str(progressToInsert["_id"])
            progressResponsePut["id"] = id_progressToInsert

            return helpers.return_request(progressResponsePut,
                                          HTTPStatus.CREATED)

    # verbo DELETE - borrar registro de game progress
    @helpers.log_reqId
    @helpers.check_token
    @helpers.limit_own_user_role
    def delete(self, username):
        appServer.app.logger.info(helpers.log_request_id() + "Game progress " +
                                  "record for user '" +
                                  username +
                                  "' deletion requested.")

        try:
            existingGameProgress = appServer.db.gameprogress.find_one(
                {"username": username})
        except Exception as e:
            return helpers.handleDatabasebError(e)
        if (existingGameProgress is not None):

            try:
                appServer.db.gameprogress.delete_many({"username": username})
            except Exception as e:
                return helpers.handleDatabasebError(e)

            progressResponseDelete = {
                "code": 0,
                "message": "Game progress record for user '" + username +
                           "' deleted.",
                "data": None
            }
            return helpers.return_request(progressResponseDelete,
                                          HTTPStatus.OK)

        progressResponseDelete = {
            "code": -1,
            "message": "Game progress record for user '" +
                       username +
                       "' not found.",
            "data": None
        }
        return helpers.return_request(progressResponseDelete,
                                      HTTPStatus.NOT_FOUND)
