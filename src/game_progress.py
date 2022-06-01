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
            allProgress = appServer.db.gameprogress.find()
        except Exception as e:
            return helpers.handleDatabasebError(e)

        AllProgressResponseGet = []
        for existingUser in allProgress:
            retrievedProgress = {
                "id": str(existingUser["_id"]),
                "username": existingUser["username"],
                "next_level": existingUser["next_level"],
                "difficulty_level": existingUser["difficulty_level"],
                "date_created": existingUser["date_created"],
                "date_updated": existingUser["date_updated"]
            }
            AllProgressResponseGet.append(retrievedProgress)

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
