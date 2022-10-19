# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# src/authserver_relay.py

# Basado en:
# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876

# Importacion de librerias necesarias
# Flask, para la implementacion del servidor REST
from flask_restful import Resource
from flask import request
from flask import g
from http import HTTPStatus

# Importacion del archivo principal
import app_server as appServer
# Importacion del cliente de AuthServer y helpers
from src import authserver_client
from src import helpers


###############################################################################
# Clases que definen los endpoints para el relay del AuthServer
# Consultar la documentacion del AuthServer para mas detalle
###############################################################################


###############################################################################
# Metodos para endpoint 'adminusers' del AuthServer
###############################################################################
# Clase que define el endpoint para trabajar con usuarios administradores
# Operaciones CRUD: Create, Read, Update, Delete
# verbo GET - listar usuarios
# verbo POST - nuevo usario
class AllAdminUsers(Resource):

    # verbo POST - nuevo usario administrador
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def post(self):
        try:
            response = authserver_client.\
                    AuthAPIClient.\
                    post_adminuser(request.get_json(force=True))
            return response.json(), response.status_code
        except Exception as e:
            ResponseAllAdminusersPost = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseAllAdminusersPost,
                                          HTTPStatus.SERVICE_UNAVAILABLE)

    # verbo GET - listar usuarios administradores
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def get(self):
        try:
            response = authserver_client.\
                    AuthAPIClient.\
                    get_adminusers(request.args)
            return response.json(), response.status_code
        except Exception as e:
            ResponseAllAdminusersGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseAllAdminusersGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)


# Clase que define el endpoint para trabajar con usuarios administradores
# Operaciones CRUD: Create, Read, Update, Delete
# verbo GET - leer usuario administrador
# verbo PUT - actualizar usuario administrador completo (sin contrasenia)
# verbo PATCH - actualizar contrasenia. solo permite op=replace y path=password
# verbo DELETE - borrar usuario administrador
class AdminUser(Resource):

    # verbo GET - leer usuario administrador
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def get(self, username):
        try:
            response = authserver_client.\
                    AuthAPIClient.\
                    get_adminuser(username)
            return response.json(), response.status_code
        except Exception as e:
            ResponseAdminusersGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseAdminusersGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)

    # verbo PUT - actualizar usuario completo, si no existe lo crea
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def put(self, username):
        try:
            response = authserver_client.\
                    AuthAPIClient.\
                    put_adminuser(username, request.get_json(force=True))
            return response.json(), response.status_code
        except Exception as e:
            ResponseAdminusersPut = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseAdminusersPut,
                                          HTTPStatus.SERVICE_UNAVAILABLE)

    # verbo PATCH - actualizar contrasenia.
    # solo permite op=replace y path=password
    # { "op": "replace", "path": "/password", "value": "" }
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def patch(self, username):
        try:
            response = authserver_client.\
                    AuthAPIClient.\
                    patch_adminuser(username, request.get_json(force=True))
            return response.json(), response.status_code
        except Exception as e:
            ResponseAdminusersPatch = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseAdminusersPatch,
                                          HTTPStatus.SERVICE_UNAVAILABLE)

    # verbo DELETE - borrar usuario administrador
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def delete(self, username):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       delete_adminuser(username)
            return response.json(), response.status_code
        except Exception as e:
            ResponseAdminusersDelete = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseAdminusersDelete,
                                          HTTPStatus.SERVICE_UNAVAILABLE)


# Clase que define el endpoint para obtener las sesiones de un usuario admin
# verbo GET - obtener sesiones vigentes del usuario admin
# verbo DELETE - cerrar todas las sesiones del usuario
class AdminUserSessions(Resource):

    # verbo GET - obtener sesiones vigentes del usuario admin
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def get(self, username):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       get_adminuser_sessions(username, request.args)
            return response.json(), response.status_code
        except Exception as e:
            ResponseAdminusersGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseAdminusersGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)

    # verbo DELETE - cerrar todas las sesiones del usuario
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def delete(self, username):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       delete_adminuser_sessions(username)
            return response.json(), response.status_code
        except Exception as e:
            ResponseUserSessionsGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseUserSessionsGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)


###############################################################################
# Metodos para endpoint 'users' del AuthServer
###############################################################################
# Clase que define el endpoint para trabajar con usuarios
# Operaciones CRUD: Create, Read, Update, Delete
# verbo GET - listar usuarios
# verbo POST - nuevo usario
class AllUsers(Resource):

    # verbo POST - nuevo usario
    @helpers.log_reqId
    def post(self):
        try:
            response = authserver_client.\
                    AuthAPIClient.\
                    post_user(request.get_json(force=True))
            return response.json(), response.status_code
        except Exception as e:
            ResponseAllUsersPost = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseAllUsersPost,
                                          HTTPStatus.SERVICE_UNAVAILABLE)

    # verbo GET - listar usuarios
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def get(self):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       get_users(request.args)
            return response.json(), response.status_code
        except Exception as e:
            ResponseAllUsersGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseAllUsersGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)


# Clase que define el endpoint para trabajar con usuarios
# Operaciones CRUD: Create, Read, Update, Delete
# verbo GET - leer usuario
# verbo PUT - actualizar usuario completo (sin contrasenia)
# verbo PATCH - actualizar contrasenia. solo permite op=replace y path=password
# verbo DELETE - borrar usuario
class User(Resource):

    # verbo GET - leer usuario
    @helpers.log_reqId
    @helpers.check_token
    def get(self, username):
        try:
            resp_auth = authserver_client.\
                        AuthAPIClient.\
                        get_user(username)
            return resp_auth.json(), resp_auth.status_code
        except Exception as e:
            ResponseUsersGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseUsersGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)

    # verbo PUT - actualizar usuario completo, si no existe lo crea
    @helpers.log_reqId
    @helpers.check_token
    @helpers.limit_own_user_role
    def put(self, username):
        try:
            resp_auth = authserver_client.\
                        AuthAPIClient.\
                        put_user(username, request.get_json(force=True))
            return resp_auth.json(), resp_auth.status_code
        except Exception as e:
            ResponseUsersPut = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseUsersPut,
                                          HTTPStatus.SERVICE_UNAVAILABLE)

    # verbo PATCH - actualizar contrasenia.
    # solo permite op=replace y path=password / path=avatar
    # { "op": "replace", "path": "/password", "value": "" }
    # { "op": "replace", "path": "/avatar", "value": "" }
    @helpers.log_reqId
    @helpers.check_token
    @helpers.limit_own_user_role
    def patch(self, username):
        try:
            response = authserver_client.\
                    AuthAPIClient.\
                    patch_user(username, request.get_json(force=True))
            return response.json(), response.status_code
        except Exception as e:
            ResponseUsersPatch = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseUsersPatch,
                                          HTTPStatus.SERVICE_UNAVAILABLE)

    # verbo DELETE - borrar usuario
    @helpers.log_reqId
    @helpers.check_token
    @helpers.limit_own_user_role
    def delete(self, username):
        try:
            # Antes de borrar el usuario, borramos su registro
            # de game progress
            appServer.db.gameprogress.delete_one({
                    "username": username
            })
            resp_auth = authserver_client.\
                AuthAPIClient.\
                delete_user(username)
            return resp_auth.json(), resp_auth.status_code
        except Exception as e:
            ResponseUsersDelete = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseUsersDelete,
                                          HTTPStatus.SERVICE_UNAVAILABLE)


# Clase que define el endpoint para obtener el avatar de un usuario
# verbo GET - obtener el avatar del usuario
class UserAvatar(Resource):

    # verbo GET - obtener el avatar del usuario
    @helpers.log_reqId
    @helpers.check_token
    def get(self, username):
        try:
            response_auth = authserver_client.\
                            AuthAPIClient.\
                            get_user(username)
            if (response_auth.status_code == HTTPStatus.OK):
                return helpers.return_request(response_auth.json()["avatar"],
                                              HTTPStatus.OK)
            else:
                return response_auth.json(), response_auth.status_code
        except Exception as e:
            ResponseUserAvatarGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseUserAvatarGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)


# Clase que define el endpoint para chequear si existe un usuario
# verbo GET - chequear si existe el usuario
class UserExists(Resource):

    # verbo GET - chequear si existe el usuario
    @helpers.log_reqId
    def get(self, username):
        try:
            response_auth = authserver_client.\
                            AuthAPIClient.\
                            get_user(username)
            if (response_auth.status_code == HTTPStatus.OK):
                ResponseUserExistsGet = {
                    "code": 0,
                    "message": "User '" + username + "' exists.",
                    "data": None
                }
                return helpers.return_request(ResponseUserExistsGet,
                                              HTTPStatus.OK)
            else:
                return response_auth.json(), response_auth.status_code
        except Exception as e:
            ResponseUserExistsGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseUserExistsGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)


# Clase que define el endpoint para obtener las sesiones de un usuario
# verbo GET - obtener sesiones vigentes del usuario
# verbo DELETE - cerrar todas las sesiones del usuario
class UserSessions(Resource):

    # verbo GET - obtener sesiones vigentes del usuario
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def get(self, username):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       get_user_sessions(username, request.args)
            return response.json(), response.status_code
        except Exception as e:
            ResponseUserSessionsGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseUserSessionsGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)

    # verbo DELETE - cerrar todas las sesiones del usuario
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def delete(self, username):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       delete_user_sessions(username)
            return response.json(), response.status_code
        except Exception as e:
            ResponseUserSessionsGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseUserSessionsGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)


###############################################################################
# Metodos para endpoint 'sessions' del AuthServer
###############################################################################
# Clase que define el endpoint para trabajar con sesiones
# Operaciones CRUD: Create, Read, Update, Delete
# verbo GET - listar sesiones activas
# verbo POST - crear sesion, si existe refresca el token
# verbo DELETE - cerrar sesion de todos los usuarios,
# menos la sesion que hace el pedido
class AllSessions(Resource):

    # verbo POST - crear sesion, si existe refresca el token
    @helpers.log_reqId
    def post(self):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       post_session(request.get_json(force=True))
            return response.json(), response.status_code
        except Exception as e:
            ResponseSessionPost = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseSessionPost,
                                          HTTPStatus.SERVICE_UNAVAILABLE)

    # verbo GET - listar sesiones
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def get(self):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       get_sessions(request.args)
            return response.json(), response.status_code
        except Exception as e:
            ResponseSessionGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseSessionGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)

    # verbo DELETE - cerrar sesion de todos los usuarios,
    # menos la sesion que hace el pedido
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def delete(self):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       delete_all_sessions(g.session_token)
            return response.json(), response.status_code
        except Exception as e:
            ResponseSessionDelete = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseSessionDelete,
                                          HTTPStatus.SERVICE_UNAVAILABLE)


# Clase que define el endpoint para trabajar con sesiones
# Operaciones CRUD: Create, Read, Update, Delete
# verbo GET - checkear sesion
# verbo DELETE - cerrar sesion
class Session(Resource):

    # verbo GET - checkear sesion
    @helpers.log_reqId
    @helpers.check_token
    @helpers.check_own_session
    def get(self, token):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       get_session(token)
            return response.json(), response.status_code
        except Exception as e:
            ResponseSessionResponseGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseSessionResponseGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)

    # verbo DELETE - cerrar sesion
    @helpers.log_reqId
    @helpers.check_token
    @helpers.check_own_session
    def delete(self, token):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       delete_session(token)
            return response.json(), response.status_code
        except Exception as e:
            ResponseSessionDelete = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseSessionDelete,
                                          HTTPStatus.SERVICE_UNAVAILABLE)


###############################################################################
# Metodos para endpoint 'recovery' del AuthServer
###############################################################################
# Clases que permiten realizar la recuperacion de contraseña
# SOLO PARA USUARIOS DE LA APP
# verbo GET - recuperar todos los pedidos de recupero de contraseña
# verbo POST - crear pedido de recupero de contraseña, si ya existe uno lo
# pisa y lo regenera
class AllRecovery(Resource):

    # verbo GET - recuperar todos los pedidos de recupero de contraseña
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def get(self):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       get_recoveries(request.args)
            return response.json(), response.status_code
        except Exception as e:
            ResponseAllRecoveryGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseAllRecoveryGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)

    # verbo POST - crear pedido de recupero de contraseña, si ya existe uno lo
    # pisa y lo regenera
    @helpers.log_reqId
    def post(self):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       post_recovery_request(request.get_json(force=True))
            return response.json(), response.status_code
        except Exception as e:
            ResponseAllRecoveryPost = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseAllRecoveryPost,
                                          HTTPStatus.SERVICE_UNAVAILABLE)


# Clases que permiten realizar la recuperacion de contraseña
# SOLO PARA USUARIOS DE LA APP
# verbo GET - recuperar un pedido especifico de recupero de contraseña
# verbo POST - cambia la password del usuario, y borra el pedido de
# recuperacion de contraseña, si los datos coinciden
# verbo DELETE - borra el pedido de recuperacion de contraseña de
# un usuario
class Recovery(Resource):

    # verbo GET - recuperar un pedido especifico de recupero de contraseña
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def get(self, username):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       get_recovery(username)
            return response.json(), response.status_code
        except Exception as e:
            ResponseRecoveryGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseRecoveryGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)

    # verbo POST - cambia la password del usuario, y borra el pedido de
    # recuperacion de contraseña, si los datos coinciden
    @helpers.log_reqId
    def post(self, username):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       post_recovery_reset(username,
                                           request.get_json(force=True))
            return response.json(), response.status_code
        except Exception as e:
            ResponseRecoveryPost = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseRecoveryPost,
                                          HTTPStatus.SERVICE_UNAVAILABLE)

    # verbo DELETE - borra el pedido de recuperacion de contraseña de
    # un usuario
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def delete(self, username):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       delete_recovery(username)
            return response.json(), response.status_code
        except Exception as e:
            ResponseRecoveryGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseRecoveryGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)


###############################################################################
# Metodos para endpoint 'requestlog' del AuthServer
###############################################################################

# Clase que entrega los registros del request log
class AuthRequestLog(Resource):

    # verbo GET - obtener registros del request log entre fechas
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def get(self):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       get_requestlog(request.args)
            return response.json(), response.status_code
        except Exception as e:
            ResponseRequestLogGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseRequestLogGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)


###############################################################################
# Metodos para endpoint 'requestlog' del AuthServer
###############################################################################

# Clase que entrega estadisticas del uso del servidor
class AuthStats(Resource):

    # verbo GET - obtener registros de estadisticas
    @helpers.log_reqId
    @helpers.check_token
    @helpers.deny_user_role
    def get(self):
        try:
            response = authserver_client.\
                       AuthAPIClient.\
                       get_stats(request.args)
            return response.json(), response.status_code
        except Exception as e:
            ResponseStatsGet = {
                "code": -1,
                "message": str(e),
                "data": None
            }
            return helpers.return_request(ResponseStatsGet,
                                          HTTPStatus.SERVICE_UNAVAILABLE)
