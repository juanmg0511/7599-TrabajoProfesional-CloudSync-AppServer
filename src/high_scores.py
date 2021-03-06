# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# src/high_scores.py

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


# Clase que define el endpoint para trabajar con high scores
# Operaciones CRUD: Create, Read, Update, Delete
# verbo GET - listar high scores de todos los usuarios
# verbo POST - nuevo high score para un usuario
class AllHighScores(Resource):
    # verbo GET - listar high scores de todos los usuarios
    @helpers.log_reqId
    @helpers.check_token
    def get(self):
        appServer.app.logger.info(helpers.log_request_id() +
                                  'All high scores requested.')

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
            AllHighScoresResponseGet = {
                "code": -1,
                "message": "Bad request. Missing required arguments.",
                "data": None
            }
            return helpers.return_request(AllHighScoresResponseGet,
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
            allHighScores = appServer.db.highscores.\
                            find().\
                            skip(query_start).\
                            limit(query_limit)
            allHighScoresCount = appServer.db.highscores.\
                count_documents({})
        except Exception as e:
            return helpers.handleDatabasebError(e)

        # Calculo de las URL hacia anterior y siguiente
        start_previous = query_start - query_limit
        start_next = query_start + query_limit
        if (start_previous < 0
           or (start_previous >= allHighScoresCount)
           or (query_start == 0 and query_limit == 0)
           or (query_limit == 0)):
            url_previous = None
        else:
            url_previous = request.path +\
                           "?start=" +\
                           str(start_previous) +\
                           "&limit=" +\
                           str(query_limit)

        if (start_next >= allHighScoresCount
           or (query_start == 0 and query_limit == 0)
           or (query_limit == 0)):
            url_next = None
        else:
            url_next = request.path +\
                       "?start=" +\
                       str(start_next) +\
                       "&limit=" +\
                       str(query_limit)

        AllHighScoresResultsGet = []
        for existingHighScore in allHighScores:
            retrievedHighScore = {
                "id": str(existingHighScore["_id"]),
                "username": existingHighScore["username"],
                "achieved_level": existingHighScore["achieved_level"],
                "difficulty_level": existingHighScore["difficulty_level"],
                "time_elapsed": existingHighScore["time_elapsed"],
                "gold_collected": existingHighScore["gold_collected"],
                "high_score": existingHighScore["high_score"],
                "date_created": existingHighScore["date_created"],
                "date_updated": existingHighScore["date_updated"]
            }
            AllHighScoresResultsGet.append(retrievedHighScore)

        # Construimos la respuesta paginada
        AllHighScoresResponseGet = {
            "total": allHighScoresCount,
            "limit": query_limit,
            "next": url_next,
            "previous": url_previous,
            "results": AllHighScoresResultsGet
        }

        return helpers.return_request(AllHighScoresResponseGet, HTTPStatus.OK)

    # verbo POST - nuevo high score para un usuario
    @helpers.log_reqId
    @helpers.check_token
    @helpers.limit_own_user_role
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("username", type=helpers.non_empty_string,
                                required=True, nullable=False)
            parser.add_argument("achieved_level", type=int,
                                required=True, nullable=False)
            parser.add_argument("difficulty_level", type=int,
                                required=True, nullable=False)
            parser.add_argument("time_elapsed", type=helpers.non_empty_string,
                                required=True, nullable=False)
            parser.add_argument("gold_collected", type=int,
                                required=True, nullable=False)
            parser.add_argument("high_score", type=int,
                                required=True, nullable=False)
            args = parser.parse_args()
        except Exception:
            AllHighScoresResponsePost = {
                "code": -1,
                "message": "Bad request. Missing required arguments.",
                "data": None
            }
            return helpers.return_request(AllHighScoresResponsePost,
                                          HTTPStatus.BAD_REQUEST)

        appServer.app.logger.info(helpers.log_request_id() +
                                  "New high score for user '" +
                                  args["username"] +
                                  "' requested.")

        highScoreToInsert = {
            "username": args["username"],
            "achieved_level": args["achieved_level"],
            "difficulty_level": args["difficulty_level"],
            "time_elapsed": args["time_elapsed"],
            "gold_collected": args["gold_collected"],
            "high_score": args["high_score"],
            "date_created": datetime.utcnow().isoformat(),
            "date_updated": None
        }
        AllHighScoresResponsePost = highScoreToInsert.copy()
        try:
            appServer.db.highscores.insert_one(highScoreToInsert)
        except Exception as e:
            return helpers.handleDatabasebError(e)
        id_highScoreToInsert = str(highScoreToInsert["_id"])
        AllHighScoresResponsePost["id"] = id_highScoreToInsert
        AllHighScoresResponsePost.pop("password", None)

        return helpers.return_request(AllHighScoresResponsePost,
                                      HTTPStatus.CREATED)


# Clase que define el endpoint para trabajar con high scores
# Operaciones CRUD: Create, Read, Update, Delete
# verbo GET - leer registro de high score
# verbo DELETE - borrar registro de high score
class HighScores(Resource):

    # verbo GET - leer registros de high score
    @helpers.log_reqId
    @helpers.check_token
    @helpers.limit_own_user_role
    def get(self, username):
        appServer.app.logger.info(helpers.log_request_id() + "High score " +
                                  "records for user '" +
                                  username +
                                  "' requested.")

        try:
            existingHighScores = appServer.db.highscores.find(
                {"username": username})
        except Exception as e:
            return helpers.handleDatabasebError(e)

        AllHighScoresResponseGet = []
        for existingHighScore in existingHighScores:
            retrievedHighScore = {
                "id": str(existingHighScore["_id"]),
                "username": existingHighScore["username"],
                "achieved_level": existingHighScore["achieved_level"],
                "difficulty_level": existingHighScore["difficulty_level"],
                "time_elapsed": existingHighScore["time_elapsed"],
                "gold_collected": existingHighScore["gold_collected"],
                "high_score": existingHighScore["high_score"],
                "date_created": existingHighScore["date_created"],
                "date_updated": existingHighScore["date_updated"]
            }
            AllHighScoresResponseGet.append(retrievedHighScore)

        if (len(AllHighScoresResponseGet) == 0):
            progressResponseGet = {
                    "code": -1,
                    "message": "High score records for user '" +
                               username +
                               "' not found.",
                    "data": None
                }
            return helpers.return_request(progressResponseGet,
                                          HTTPStatus.NOT_FOUND)
        else:
            return helpers.return_request(AllHighScoresResponseGet,
                                          HTTPStatus.OK)

    # verbo DELETE - borrar registro de game progress
    @helpers.log_reqId
    @helpers.check_token
    @helpers.limit_own_user_role
    def delete(self, username):
        appServer.app.logger.info(helpers.log_request_id() + "High score " +
                                  "records for user '" +
                                  username +
                                  "' deletion requested.")

        try:
            existingHighScores = appServer.db.highscores.find_one(
                {"username": username})
        except Exception as e:
            return helpers.handleDatabasebError(e)
        if (existingHighScores is not None):

            try:
                appServer.db.highscores.delete_many({"username": username})
            except Exception as e:
                return helpers.handleDatabasebError(e)

            HighScoresResponseDelete = {
                "code": 0,
                "message": "High score records for user '"
                           + username +
                           "' deleted.",
                "data": None
            }
            return helpers.return_request(HighScoresResponseDelete,
                                          HTTPStatus.OK)
        HighScoresResponseDelete = {
            "code": -1,
            "message": "High score records for user '" +
                       username +
                       "' not found.",
            "data": None
        }
        return helpers.return_request(HighScoresResponseDelete,
                                      HTTPStatus.NOT_FOUND)
