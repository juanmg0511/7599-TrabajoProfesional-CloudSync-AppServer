# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# Unit test file, funciones auxiliares
# tests/aux_functions.py

# Basado en:
# https://dev.classmethod.jp/articles/mocking-around-with-python-and-unittest/

# Importacion de librerias necesarias
from unittest import mock
from http import HTTPStatus
from datetime import datetime, timedelta

# Importacion del archivo principal
import app_server


# Simula la respuesta del AuthServer ante un intento de inico de
# sesion con un usuario administrador
def mockCheckSessionAdmin(username):

    my_mock_response = mock.Mock(status_code=HTTPStatus.OK)
    my_mock_response.json.return_value = {
        "username": username,
        "user_role": "admin",
        "session_token": "eyJ0eXAiOiJKV1QiLDCJhbGciOiJIUzI1Ni" +
                         "J9.eyJpYXQiOjE2MTUzOTQ1MTcsIm5iZiI" +
                         "6MTY1NTM5NDUxNywianRpIjoiMjNkMTViM" +
                         "zgtMGEzMi00MmRmLWI5OTAtMTcxYjRmNjQ" +
                         "3NTFhIiwiaWRlbnRpdHkiOiJjbG91ZHN5b" +
                         "mNnb2WiLCJmcmVzaCI6ZmFsc2UsInR5cGU" +
                         "iOiJhY2Nlc3MifQ.1zORhdoT-_JkaPQXk9" +
                         "PMVzUL7oc9-vl9LkdZlCEcMMo",
        "expires": (datetime.utcnow() + timedelta(10)).isoformat(),
        "date_created": datetime.utcnow().isoformat(),
        "id": "62ab50d5c28756fa6c4eb88e"
    }

    return my_mock_response


# Simula la respuesta del AuthServer ante un intento de inico de
# sesion con un usuario
def mockCheckSessionUser(username):

    my_mock_response = mock.Mock(status_code=HTTPStatus.OK)
    my_mock_response.json.return_value = {
        "username": username,
        "user_role": "user",
        "session_token": "eyJ0eXAiOiJKV1QiLDCJhbGciOiJIUzI1Ni" +
                         "J9.eyJpYXQiOjE2NTUzOTQ1MTcsIm5iZiI" +
                         "6MTY1NTM5NDUxNywiANRpIjoiMjNkMTViM" +
                         "zgtMGEzMi00MmRmLWI5OTAtMTcxYjRmNjQ" +
                         "3NTFhIiwiaWRlbnRpdHkiOiJjbG91ZHN5b" +
                         "mNnb2WiLCJmcmVzaCI6ZmFsc2UsInR5cGU" +
                         "iOiJhY2Nlc3MifQ.1zORhdoT-_JkaPQXk9" +
                         "PMVzUL7ZZ9-vl9LkdZlCEcavo",
        "expires": (datetime.utcnow() + timedelta(10)).isoformat(),
        "date_created": datetime.utcnow().isoformat(),
        "id": "62ab50d5c28756fa6c4eb88f"
    }

    return my_mock_response


# Simula la respuesta del AuthServer ante un pedido a un endpoint
# privado de la API. No simulamos comportamiento, porque se prueba
# en los tests unitarios del AuthServer. Solo nos interesa testear
# el codigo de relay
def mockCheckRelay(return_value):

    my_mock_response = mock.Mock(status_code=return_value)
    my_mock_response.json.return_value = {}

    return my_mock_response


def mockCheckRelayUser(username):

    my_mock_response = mock.Mock(status_code=HTTPStatus.OK)
    my_mock_response.json.return_value = {
        "id": "62d443c6366edccbaa52cfec",
        "username": username,
        "first_name": "Damián",
        "last_name": "Marquesín Fernandez",
        "contact": {
            "email": "a.fake@email.com",
            "phone": "5555 5555"
        },
        "avatar": {
            "isUrl": True,
            "data": "http://www.google.com"
        },
        "login_service": False,
        "online": False,
        "account_closed": False,
        "date_created": datetime.utcnow().isoformat(),
        "date_updated": None
    }

    return my_mock_response


# Simula la respuesta del AuthServer ante un pedido a un endpoint
# privado de la API. Devuelve un objeto tipo usuario vacio, solo
# con informacion de avatar
def mockCheckRelayAvatar(return_value):

    my_mock_response = mock.Mock(status_code=return_value)
    my_mock_response.json.return_value = {
        "avatar": {
            "isUrl": True,
            "data": "http://www.google.com"
        }
    }

    return my_mock_response


# Crea un registro de request log en la base de datos, utilizando
# el path pasado como argumento
def createRequestLogEntry(request_path, username):

    my_mock_response = {
        "log_type": "request",
        "request_date": datetime.utcnow().isoformat(),
        "request_id": "9e7779e5-0b63-48de-aebb-8040dce3dea5",
        "remote_ip": "181.84.174.136",
        "host": "fiuba-qa-7599-cs-app-server.herokuapp.com",
        "api_version": "v1",
        "method": "GET",
        "path": request_path + "/" + username,
        "user_name": username,
        "user_role": "user",
        "session_token": "*",
        "status": "200 OK",
        "duration": "0.618958",
        "headers": {
            "Host": "fiuba-qa-7599-cs-app-server.herokuapp.com",
            "Connection": "close",
            "X-Auth-Token": "*",
            "User-Agent": "PostmanRuntime/7.29.0",
            "Accept": "*/*",
            "Cache-Control": "no-cache",
            "Postman-Token": "2d81431e-4f70-4a84-a572-53bf96ca878a",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Request-Id": "9e7779e5-0b63-48de-aebb-8040dce3dea5",
            "X-Forwarded-For": "181.84.174.136",
            "X-Forwarded-Proto": "http",
            "X-Forwarded-Port": "80",
            "Via": "1.1 vegur",
            "Connect-Time": "0",
            "X-Request-Start": "1655407785329",
            "Total-Route-Time": "0"
        },
        "args": {},
        "data": {},
        "response": {
            "id": "62ab84a5781d2f1f1540ead3",
            "username": username,
            "next_level": 5,
            "difficulty_level": 5,
            "date_created": datetime.utcnow().isoformat(),
            "date_updated": None
        }
    }

    app_server.db.requestlog.insert_one(my_mock_response)


# Crea un registro de game progress en la base de datos
def createGameProgress(username):

    my_mock_response = {
        "username": username,
        "next_level": 5,
        "difficulty_level": 5,
        "time_elapsed": "20:10:40.045",
        "gold_collected": 5000,
        "date_created": datetime.utcnow().isoformat(),
        "date_updated": None
    }

    app_server.db.gameprogress.insert_one(my_mock_response)
    return my_mock_response["_id"]


# Crea un registro de high score en la base de datos
def createHighScore(username):

    my_mock_response = {
        "username": username,
        "achieved_level": 2,
        "difficulty_level": 8,
        "time_elapsed": "20:10:40.045",
        "gold_collected": 5000,
        "high_score": 1000000,
        "date_created": datetime.utcnow().isoformat(),
        "date_updated": None
    }

    app_server.db.highscores.insert_one(my_mock_response)
    return my_mock_response["_id"]


# Borra los registros de game progress de la base de datos
def deleteGameProgress(username):

    app_server.db.gameprogress.delete_many({"username": username})


# Borra los registros de high scores de la base de datos
def deleteHighScores(username):

    app_server.db.highscores.delete_many({"username": username})
