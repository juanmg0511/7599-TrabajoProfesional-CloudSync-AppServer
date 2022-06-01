# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# src/requestlog.py

# Basado en:
# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876

# Importacion de librerias necesarias
# OS para leer variables de entorno y logging para escribir los logs
import time
from datetime import datetime, timedelta
# Flask, para la implementacion del servidor REST
from flask import g, request
from flask_restful import Resource, reqparse
from flask_log_request_id import current_request_id
from http import HTTPStatus

# Importacion del archivo principal y helpers
import app_server as appServer
from src import helpers


# Funcion que inicializa el timer para loguear el tiempo de
# respuesta de un request
def start_timer():
    g.start = time.time()
    appServer.app.logger.debug(helpers.log_request_id() + 'Timer started.')


# Funcion que guarda en la base de datos el log del request
def log_request(response):
    appServer.app.logger.debug(helpers.log_request_id() +
                               'Logging request data to DB.')
    # Escapeamos paths que no son de la api
    if (not(appServer.api_path in request.path)):
        appServer.app.logger.debug(helpers.log_request_id() +
                                   'Request is not from API path, skipping.')
        return response

    # Logueamos en la base de datos los datos del request
    # Calculos y formatos de la informacion
    now = time.time()
    duration = str(round(now - g.start, 6))
    request_id = str(current_request_id())
    ip_address = str(request.headers.get("X-Forwarded-For",
                                         request.remote_addr))
    host = str(request.host.split(":", 1)[0])
    method = request.method
    status = str(response.status)
    path = request.path
    args = request.args.to_dict()
    # Parseamos los request headers a a un diccionario
    try:
        headers = dict(request.headers)
    except Exception:
        headers = {}
    # Parseamos el request data a un diccionario
    try:
        data = eval(str(request.data.decode("utf-8")))
    except Exception:
        data = {}

    # Maskeamos las passwords del registro a loguear
    if "password" in data:
        data["password"] = "*"
    if "new_password" in data:
        data["new_password"] = "*"
    if (("PATCH" in method) and ("value" in data) and ("path" in data)
       and ("/password" in data["path"])):
        data["value"] = "*"

    # Parseamos la response a un diccionario
    try:
        # No logueamos las respuestas de pedidos de log!
        if (("requestlog" in path)
           and (response.status_code == HTTPStatus.OK)):
            resp_data = "*"
        else:
            resp_data = eval(str(response.data.decode("utf-8")))
    except Exception:
        resp_data = str(response.data.decode("utf-8"))

    # Armamos el documento a guardar en la base de datos
    requestLog = {
        "log_type": "request",
        "request_date": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "remote_ip": ip_address,
        "host": host,
        "api_version": "v" + appServer.api_version,
        "method": method,
        "path": path,
        "status": status,
        "duration": duration,
        "headers": headers,
        "args": args,
        "data": data,
        "response": resp_data
    }

    # Insertamos el registro en la base de datos
    try:
        appServer.db.requestlog.insert_one(requestLog)
    except Exception as e:
        return helpers.handleDatabasebError(e)
    appServer.app.logger.debug(helpers.log_request_id() +
                               'Request data successfully logged to DB.')
    return response


# Clase que entrega los registros del request log
class RequestLog(Resource):

    # verbo GET - obtener registros del request log entre fechas
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def get(self):
        appServer.app.logger.info(helpers.log_request_id() +
                                  'Request log requested.')
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("startdate", type=helpers.non_empty_date,
                                required=True, nullable=False)
            parser.add_argument("enddate", type=helpers.non_empty_date,
                                required=True, nullable=False)
            parser.add_argument("sortascending", type=helpers.non_empty_string,
                                required=False, nullable=True)
            parser.add_argument("filter", type=helpers.non_empty_string,
                                required=False, nullable=False)
            args = parser.parse_args()
        except Exception:
            requeslogResponseGet = {
                "code": -1,
                "message": "Bad request. Missing or wrong format " +
                           "for required arguments.",
                "data": None
            }
            return helpers.return_request(requeslogResponseGet,
                                          HTTPStatus.BAD_REQUEST)

        if (args["startdate"] > args["enddate"]):
            requeslogResponseGet = {
                "code": -2,
                "message": "Bad request. Start date greater than end date.",
                "data": None
            }
            return helpers.return_request(requeslogResponseGet,
                                          HTTPStatus.BAD_REQUEST)

        if (args["filter"] is not None):
            try:
                filter_value = eval(str(args["filter"]))
                comparator = helpers.non_empty_string(
                                filter_value.get("comparator", ""))
                field = helpers.non_empty_string(filter_value.get("field", ""))
                value = helpers.non_empty_string(filter_value.get("value", ""))

                if (comparator not in ["eq", "in"]):
                    raise ValueError("Invalid comparator.")
            except Exception:
                requeslogResponseGet = {
                    "code": -3,
                    "message": "Bad request. Worng format for filter " +
                               "object, please see API documentation.",
                    "data": None
                }
                return helpers.return_request(requeslogResponseGet,
                                              HTTPStatus.BAD_REQUEST)

        sort_ascending = str(args.get("sortascending", "False"))
        if (str(sort_ascending).
           lower().
           replace("\"", "").
           replace("'", "") == "true"):
            sort_ascending = True
        else:
            sort_ascending = False

        appServer.app.logger.debug(helpers.log_request_id() +
                                   "Start date: " +
                                   str(args["startdate"].date()))
        appServer.app.logger.debug(helpers.log_request_id() +
                                   "End date: " +
                                   str(args["enddate"].date()))
        appServer.app.logger.debug(helpers.log_request_id() +
                                   "Sort ascending: " +
                                   str(sort_ascending))
        if (args["filter"] is not None):
            appServer.app.logger.debug(helpers.log_request_id() +
                                       "Filter: " +
                                       str(filter_value))

        # Calculamos numero de dias pedidos
        startdate = args["startdate"]
        enddate = args["enddate"]
        number_days = abs((enddate - startdate).days) + 1

        numRecords = 0
        logRecords = []
        for day in range(number_days):

            # Calculamos el dia actual, de acuerdo al ordenamiento pedido
            if (sort_ascending is True):
                date = startdate + timedelta(days=day)
            else:
                date = enddate - timedelta(days=day)

            # Armamos el query a ejecutar para el dia
            query = {"request_date": {"$regex": str(date.date())}}
            if (args["filter"] is not None):
                if (comparator == "eq"):
                    query = {"$and": [
                                {"request_date": {
                                    "$regex": str(date.date())
                                    }},
                                {
                                    field: value
                                }]}
                if (comparator == "in"):
                    query = {"$and": [
                                {"request_date": {
                                    "$regex": str(date.date())
                                    }},
                                {
                                    field: {
                                        "$regex": value,
                                        "$options": "i"
                                        }
                                }]}

            # Tomamos los requests del dia, y hacemos los calculos
            if (sort_ascending is True):
                try:
                    day_records = appServer.db.requestlog.find(query)
                except Exception as e:
                    return helpers.handleDatabasebError(e)
            else:
                try:
                    day_records = appServer.db.requestlog.\
                                find(query).\
                                sort([("_id", -1)])
                except Exception as e:
                    return helpers.handleDatabasebError(e)

            while True:
                try:
                    record = day_records.next()
                except StopIteration:
                    break

                numRecords += 1
                try:
                    record["_id"] = str(record["_id"])
                    record_data = eval(str(record))
                except Exception:
                    record_data = {}

                logRecords.append(record_data)

        requeslogResponseGet = {
            "request_date:": datetime.utcnow().isoformat(),
            "requested_days": str(number_days),
            "records_retrieved": str(numRecords),
            "request_log": logRecords
        }
        # No logueamos lo que devolvemos, porque es enorme!
        appServer.app.logger.info(helpers.log_request_id() +
                                  "Returned HTTP: " +
                                  str(HTTPStatus.OK.value))
        return requeslogResponseGet, HTTPStatus.OK
