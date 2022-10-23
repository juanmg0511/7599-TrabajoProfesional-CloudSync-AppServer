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
# importing ObjectId from bson library
from bson.objectid import ObjectId
from http import HTTPStatus

# Importacion de las configuracion del App Server
import app_server_config as config
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
            # Texto para filtrar los resultados
            parser.add_argument("user_filter",
                                type=helpers.
                                non_empty_and_safe_filter_username,
                                required=False,
                                nullable=False)
            # Columna a utilizar para ordenar los resultados, si no se
            # incluye se trabaja con natural order
            parser.add_argument("sort_column",
                                type=helpers.
                                non_empty_string,
                                required=False,
                                nullable=False)
            # Indica el tipo de orden a utilizar en el ordenamiento, se
            # aplica independientemente de si es especificada una columna o
            # no. El valor por default es ASCENDENTE (1)
            parser.add_argument("sort_order",
                                type=helpers.
                                non_empty_string,
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

        user_filter = args.get("user_filter", None)

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
            if (query_limit <= 0 or query_limit > int(config.page_max_size)):
                query_limit = int(config.page_max_size)
        else:
            query_limit = int(config.page_max_size)

        # Se construye el query para filtrar en base a los parametros
        # opcionales
        find_query = {}
        if (user_filter is not None):
            find_query["username"] = {
                "$regex": ".*" + str(user_filter) + ".*",
                "$options": 'i'
            }

        # Se construye el sort para ordenar el query. Si no se especifica,
        # se trabaja con el natural order
        array_column = False
        array_order = False
        query_sort_column_array = []
        query_sort_order_array = []
        query_sort = []

        query_sort_column = args.get("sort_column", None)
        query_sort_order = args.get("sort_order", None)

        if (query_sort_column is None):
            query_sort_column = "$natural"
        else:
            query_sort_column_array = query_sort_column.split(",")
            if len(query_sort_column_array) == 1:
                query_sort_column = query_sort_column_array[0]
                query_sort_column_array = []
            else:
                array_column = True

        if (query_sort_order is None):
            query_sort_order = 1
        else:
            query_sort_order_array = query_sort_order.split(",")
            if len(query_sort_order_array) == 1:
                try:
                    int(query_sort_order_array[0])
                except ValueError:
                    query_sort_order_array[0] = 1
                if int(query_sort_order_array[0]) != -1:
                    query_sort_order = 1
                else:
                    query_sort_order = -1
                query_sort_order_array = []
            else:
                array_order = True

        if ((array_column is False) and (array_order is False)):
            query_sort.append((
                str(query_sort_column).strip(),
                int(query_sort_order)
            ))

        if ((array_order != array_column) or
           (len(query_sort_column_array) != len(query_sort_order_array))):

            AllHighScoresResponseGet = {
                "code": -2,
                "message": "Bad request. Invalid combination of sort " +
                           "columns and orders provided.",
                "data": None
            }
            return helpers.return_request(AllHighScoresResponseGet,
                                          HTTPStatus.BAD_REQUEST)
        else:
            for index, item in enumerate(query_sort_column_array):
                if (query_sort_column_array[index] == ""):
                    query_sort_column_array[index] = " "

                try:
                    int(query_sort_order_array[index])
                except ValueError:
                    query_sort_order_array[index] = 1

                query_sort.append((
                    str(query_sort_column_array[index]).strip(),
                    int(query_sort_order_array[index])
                ))

        # Operacion de base de datos
        try:
            allHighScores = appServer.db.highscores.\
                            find(find_query).\
                            skip(query_start).\
                            limit(query_limit).\
                            sort(query_sort)
            allHighScoresCount = appServer.db.highscores.\
                count_documents(find_query)
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
    @helpers.deny_user_role
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("username",
                                type=helpers.
                                non_empty_and_safe_username,
                                required=True,
                                nullable=False)
            parser.add_argument("achieved_level",
                                type=int,
                                required=True,
                                nullable=False)
            parser.add_argument("difficulty_level",
                                type=int,
                                required=True,
                                nullable=False)
            parser.add_argument("time_elapsed",
                                type=helpers.non_empty_string,
                                required=True,
                                nullable=False)
            parser.add_argument("gold_collected",
                                type=int,
                                required=True,
                                nullable=False)
            parser.add_argument("high_score",
                                type=int,
                                required=True,
                                nullable=False)
            args = parser.parse_args()
        except Exception:
            AllHighScoresResponsePost = {
                "code": -1,
                "message": "Bad request. Missing required arguments.",
                "data": None
            }
            return helpers.return_request(AllHighScoresResponsePost,
                                          HTTPStatus.BAD_REQUEST)

        # Pasamos el usuario que viene en el path a minusculas
        username = str.lower(args["username"])
        appServer.app.logger.info(helpers.log_request_id() +
                                  "New high score for user '" +
                                  str(username) +
                                  "' requested.")

        highScoreToInsert = {
            "username": str(username),
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
# verbo GET - leer un registro de high score
# verbo PUT - actualizar un registro de high score
# verbo DELETE - borrar un registro de high score
class HighScores(Resource):

    # verbo GET - leer un registro de high score
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def get(self, id):
        appServer.app.logger.info(helpers.log_request_id() + "High score " +
                                  "record with id '" +
                                  id +
                                  "' requested.")

        try:
            id_search = ObjectId(id)
        except Exception:
            id_search = None

        try:
            existingHighScore = appServer.db.highscores.find_one({
                "_id": id_search
            })
        except Exception as e:
            return helpers.handleDatabasebError(e)

        if (existingHighScore is not None):
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
            return helpers.return_request(retrievedHighScore,
                                          HTTPStatus.OK)
        else:
            progressResponseGet = {
                "code": -1,
                "message": "High score record with id '" +
                           id +
                           "' not found.",
                "data": None
            }
            return helpers.return_request(progressResponseGet,
                                          HTTPStatus.NOT_FOUND)

    # verbo PUT - actualizar un registro de high score
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def put(self, id):
        appServer.app.logger.info(helpers.log_request_id() + "Highscore " +
                                  "record with id '" +
                                  id +
                                  "'update requested.")

        try:
            parser = reqparse.RequestParser()
            parser.add_argument("username",
                                type=helpers.
                                non_empty_and_safe_username,
                                required=True,
                                nullable=False)
            parser.add_argument("achieved_level",
                                type=int,
                                required=True,
                                nullable=False)
            parser.add_argument("difficulty_level",
                                type=int,
                                required=True,
                                nullable=False)
            parser.add_argument("time_elapsed",
                                type=helpers.non_empty_string,
                                required=True,
                                nullable=False)
            parser.add_argument("gold_collected",
                                type=int,
                                required=True,
                                nullable=False)
            parser.add_argument("high_score",
                                type=int,
                                required=True,
                                nullable=False)
            args = parser.parse_args()
        except Exception:
            AllHighScoresResponsePost = {
                "code": -1,
                "message": "Bad request. Missing required arguments.",
                "data": None
            }
            return helpers.return_request(AllHighScoresResponsePost,
                                          HTTPStatus.BAD_REQUEST)

        try:
            id_search = ObjectId(id)
        except Exception:
            id_search = None

        try:
            existingHighScore = appServer.db.highscores.find_one({
                "_id": id_search
            })
        except Exception as e:
            return helpers.handleDatabasebError(e)

        if (existingHighScore is not None):

            highScoreToUpdate = {
                "username": str.lower(args["username"]),
                "achieved_level": args["achieved_level"],
                "difficulty_level": args["difficulty_level"],
                "time_elapsed": args["time_elapsed"],
                "gold_collected": args["gold_collected"],
                "high_score": args["high_score"],
                "date_created": existingHighScore["date_created"],
                "date_updated": datetime.utcnow().isoformat()
            }
            highscoreResponsePut = highScoreToUpdate.copy()
            try:
                appServer.db.highscores.update_one(
                    {"_id": id_search},
                    {"$set": highScoreToUpdate}
                )
            except Exception as e:
                return helpers.handleDatabasebError(e)
            id_userToUpdate = str(existingHighScore["_id"])
            highscoreResponsePut["id"] = id_userToUpdate

            return helpers.return_request(highscoreResponsePut, HTTPStatus.OK)

        else:
            highscoreResponsePut = {
                "code": -1,
                "message": "High score record with id '" +
                           id +
                           "' not found.",
                "data": None
            }
            return helpers.return_request(highscoreResponsePut,
                                          HTTPStatus.NOT_FOUND)

    # verbo DELETE - borrar un registro de high score
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def delete(self, id):
        appServer.app.logger.info(helpers.log_request_id() + "High score " +
                                  "record with id '" +
                                  id +
                                  "' deletion requested.")

        try:
            id_search = ObjectId(id)
        except Exception:
            id_search = None

        try:
            existingHighScores = appServer.db.highscores.find_one({
                "_id": id_search
            })
        except Exception as e:
            return helpers.handleDatabasebError(e)
        if (existingHighScores is not None):

            try:
                appServer.db.highscores.delete_one({
                    "_id": id_search
                })
            except Exception as e:
                return helpers.handleDatabasebError(e)

            HighScoresResponseDelete = {
                "code": 0,
                "message": "High score record with id '" +
                           id +
                           "' deleted.",
                "data": None
            }
            return helpers.return_request(HighScoresResponseDelete,
                                          HTTPStatus.OK)
        HighScoresResponseDelete = {
            "code": -1,
            "message": "High score records with id '" +
                       id +
                       "' not found.",
            "data": None
        }
        return helpers.return_request(HighScoresResponseDelete,
                                      HTTPStatus.NOT_FOUND)


# Clase que define el endpoint para obtener los highscores de un usuario
# verbo GET - leer registros de high score del usuario
# verbo POST - nuevo high score para un usuario
# verbo DELETE - borrar todos registros de high score del usuario
class UserHighscores(Resource):

    # verbo GET - leer registros de high score del usuario
    @helpers.log_reqId
    @helpers.check_token
    @helpers.limit_own_user_role
    def get(self, username):
        # Pasamos el usuario que viene en el path a minusculas
        username = str.lower(username)

        appServer.app.logger.info(helpers.log_request_id() + "High score " +
                                  "records for user '" +
                                  username +
                                  "' requested.")

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
            # Columna a utilizar para ordenar los resultados, si no se
            # incluye se trabaja con natural order
            parser.add_argument("sort_column",
                                type=helpers.
                                non_empty_string,
                                required=False,
                                nullable=False)
            # Indica el tipo de orden a utilizar en el ordenamiento, se
            # aplica independientemente de si es especificada una columna o
            # no. El valor por default es ASCENDENTE (1)
            parser.add_argument("sort_order",
                                type=helpers.
                                non_empty_string,
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
            if (query_limit <= 0 or query_limit > int(config.page_max_size)):
                query_limit = int(config.page_max_size)
        else:
            query_limit = int(config.page_max_size)

        # Se construye el query para filtrar en base al usuario
        find_query = {
            "username": str(username)
        }

        # Se construye el sort para ordenar el query. Si no se especifica,
        # se trabaja con el natural order
        array_column = False
        array_order = False
        query_sort_column_array = []
        query_sort_order_array = []
        query_sort = []

        query_sort_column = args.get("sort_column", None)
        query_sort_order = args.get("sort_order", None)

        if (query_sort_column is None):
            query_sort_column = "$natural"
        else:
            query_sort_column_array = query_sort_column.split(",")
            if len(query_sort_column_array) == 1:
                query_sort_column = query_sort_column_array[0]
                query_sort_column_array = []
            else:
                array_column = True

        if (query_sort_order is None):
            query_sort_order = 1
        else:
            query_sort_order_array = query_sort_order.split(",")
            if len(query_sort_order_array) == 1:
                try:
                    int(query_sort_order_array[0])
                except ValueError:
                    query_sort_order_array[0] = 1
                if int(query_sort_order_array[0]) != -1:
                    query_sort_order = 1
                else:
                    query_sort_order = -1
                query_sort_order_array = []
            else:
                array_order = True

        if ((array_column is False) and (array_order is False)):
            query_sort.append((
                str(query_sort_column).strip(),
                int(query_sort_order)
            ))

        if ((array_order != array_column) or
           (len(query_sort_column_array) != len(query_sort_order_array))):

            AllHighScoresResponseGet = {
                "code": -2,
                "message": "Bad request. Invalid combination of sort " +
                           "columns and orders provided.",
                "data": None
            }
            return helpers.return_request(AllHighScoresResponseGet,
                                          HTTPStatus.BAD_REQUEST)
        else:
            for index, item in enumerate(query_sort_column_array):
                if (query_sort_column_array[index] == ""):
                    query_sort_column_array[index] = " "

                try:
                    int(query_sort_order_array[index])
                except ValueError:
                    query_sort_order_array[index] = 1

                query_sort.append((
                    str(query_sort_column_array[index]).strip(),
                    int(query_sort_order_array[index])
                ))

        # Operacion de base de datos
        try:
            existingHighScores = appServer.db.highscores.\
                                 find(find_query).\
                                 skip(query_start).\
                                 limit(query_limit).\
                                 sort(query_sort)
            existingHighScoresCount = appServer.db.highscores.\
                count_documents(find_query)
        except Exception as e:
            return helpers.handleDatabasebError(e)

        # Calculo de las URL hacia anterior y siguiente
        start_previous = query_start - query_limit
        start_next = query_start + query_limit
        if (start_previous < 0
           or (start_previous >= existingHighScoresCount)
           or (query_start == 0 and query_limit == 0)
           or (query_limit == 0)):
            url_previous = None
        else:
            url_previous = request.path +\
                           "?start=" +\
                           str(start_previous) +\
                           "&limit=" +\
                           str(query_limit)

        if (start_next >= existingHighScoresCount
           or (query_start == 0 and query_limit == 0)
           or (query_limit == 0)):
            url_next = None
        else:
            url_next = request.path +\
                       "?start=" +\
                       str(start_next) +\
                       "&limit=" +\
                       str(query_limit)

        AllHighScoresResultGet = []
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
            AllHighScoresResultGet.append(retrievedHighScore)

        # Construimos la respuesta paginada
        AllHighScoresResponseGet = {
            "total": existingHighScoresCount,
            "limit": query_limit,
            "next": url_next,
            "previous": url_previous,
            "results": AllHighScoresResultGet
        }
        return helpers.return_request(AllHighScoresResponseGet,
                                      HTTPStatus.OK)

    # verbo POST - nuevo high score para un usuario
    @helpers.log_reqId
    @helpers.check_token
    @helpers.limit_own_user_role
    def post(self, username):
        # Pasamos el usuario que viene en el path a minusculas
        username = str.lower(username)

        try:
            parser = reqparse.RequestParser()
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
                                  str(username) +
                                  "' requested.")

        highScoreToInsert = {
            "username": str(username),
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

    # verbo DELETE - borrar todos registros de high score del usuario
    @helpers.log_reqId
    @helpers.check_token
    @helpers.limit_own_user_role
    def delete(self, username):
        # Pasamos el usuario que viene en el path a minusculas
        username = str.lower(username)

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
