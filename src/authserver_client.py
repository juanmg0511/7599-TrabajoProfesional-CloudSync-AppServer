# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# src/authserver_client.py

# Basado en:
# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876

# Importacion de librerias necesarias
# Flask, para la implementacion del servidor REST
from flask import g
# Requests, para las llamadas a la API del AuthServer
import requests

# Importacion de las configuracion del App Server
import app_server_config as config


# Clase encargada de realizar los requests al AuthServer y devolver el
# resultado. Debe garantizarse el manejo de errores al utilizar estos
# metodos, ya que aqui no se hace ningun tipo de validacion
class AuthAPIClient:

    # Construccion de los headers del request, se envia:
    # * API Key
    # * Request Id
    # * User agent
    # * Token de autorizacion
    # * Identificacion de usuario administrador
    #
    # Si alguna de estos keys no corresponde, se deja vacio
    @staticmethod
    def __headers():
        headers = {'X-Client-ID': config.api_auth_client_id,
                   'X-Request-ID': g.request_id,
                   'User-Agent': g.user_agent}
        if (g.session_token):
            headers['X-Auth-Token'] = g.session_token
        if (g.session_admin):
            headers['X-Admin'] = 'true'
        return headers

    ###########################################################################
    # Metodos para endpoint 'sessions' del AuthServer
    ###########################################################################
    @staticmethod
    def get_sessions(filters):
        return requests.get(config.api_auth_client_url + "/" +
                            config.api_auth_client_path + "/" +
                            config.api_auth_client_version + "/" +
                            "sessions",
                            params=filters,
                            headers=AuthAPIClient.__headers())

    @staticmethod
    def delete_all_sessions(session_token):
        return requests.delete(config.api_auth_client_url + "/" +
                               config.api_auth_client_path + "/" +
                               config.api_auth_client_version + "/" +
                               "sessions?token=" +
                               session_token,
                               headers=AuthAPIClient.__headers())

    @staticmethod
    def get_session(session_token):
        return requests.get(config.api_auth_client_url + "/" +
                            config.api_auth_client_path + "/" +
                            config.api_auth_client_version + "/" +
                            "sessions" + "/" +
                            session_token,
                            headers=AuthAPIClient.__headers())

    @staticmethod
    def delete_session(session_token):
        return requests.delete(config.api_auth_client_url + "/" +
                               config.api_auth_client_path + "/" +
                               config.api_auth_client_version + "/" +
                               "sessions" + "/" +
                               session_token,
                               headers=AuthAPIClient.__headers())

    @staticmethod
    def post_session(data):
        return requests.post(config.api_auth_client_url + "/" +
                             config.api_auth_client_path + "/" +
                             config.api_auth_client_version + "/" +
                             "sessions",
                             json=data,
                             headers=AuthAPIClient.__headers())

    ###########################################################################
    # Metodos para endpoint 'users' del AuthServer
    ###########################################################################
    @staticmethod
    def get_user(username):
        return requests.get(config.api_auth_client_url + "/" +
                            config.api_auth_client_path + "/" +
                            config.api_auth_client_version + "/" +
                            "users" + "/" +
                            username,
                            headers=AuthAPIClient.__headers())

    @staticmethod
    def delete_user(username):
        return requests.delete(config.api_auth_client_url + "/" +
                               config.api_auth_client_path + "/" +
                               config.api_auth_client_version + "/" +
                               "users" + "/" +
                               username,
                               headers=AuthAPIClient.__headers())

    @staticmethod
    def put_user(username, data):
        return requests.put(config.api_auth_client_url + "/" +
                            config.api_auth_client_path + "/" +
                            config.api_auth_client_version + "/" +
                            "users" + "/" +
                            username,
                            json=data,
                            headers=AuthAPIClient.__headers())

    @staticmethod
    def patch_user(username, data):
        return requests.patch(config.api_auth_client_url + "/" +
                              config.api_auth_client_path + "/" +
                              config.api_auth_client_version + "/" +
                              "users" + "/" +
                              username,
                              json=data,
                              headers=AuthAPIClient.__headers())

    @staticmethod
    def get_users(filters):
        return requests.get(config.api_auth_client_url + "/" +
                            config.api_auth_client_path + "/" +
                            config.api_auth_client_version + "/" +
                            "users",
                            params=filters,
                            headers=AuthAPIClient.__headers())

    @staticmethod
    def post_user(data):
        return requests.post(config.api_auth_client_url + "/" +
                             config.api_auth_client_path + "/" +
                             config.api_auth_client_version + "/" +
                             "users",
                             json=data,
                             headers=AuthAPIClient.__headers())

    @staticmethod
    def get_user_exists(username):
        return requests.get(config.api_auth_client_url + "/" +
                            config.api_auth_client_path + "/" +
                            config.api_auth_client_version + "/" +
                            "users" + "/" +
                            username + "/" +
                            "exists",
                            headers=AuthAPIClient.__headers())

    @staticmethod
    def get_user_sessions(username, filters):
        return requests.get(config.api_auth_client_url + "/" +
                            config.api_auth_client_path + "/" +
                            config.api_auth_client_version + "/" +
                            "users" + "/" +
                            username + "/" +
                            "sessions",
                            params=filters,
                            headers=AuthAPIClient.__headers())

    @staticmethod
    def delete_user_sessions(username):
        return requests.delete(config.api_auth_client_url + "/" +
                               config.api_auth_client_path + "/" +
                               config.api_auth_client_version + "/" +
                               "users" + "/" +
                               username + "/" +
                               "sessions",
                               headers=AuthAPIClient.__headers())

    ###########################################################################
    # Metodos para endpoint 'adminusers' del AuthServer
    ###########################################################################
    @staticmethod
    def get_adminuser(username):
        return requests.get(config.api_auth_client_url + "/" +
                            config.api_auth_client_path + "/" +
                            config.api_auth_client_version + "/" +
                            "adminusers" + "/" +
                            username,
                            headers=AuthAPIClient.__headers())

    @staticmethod
    def delete_adminuser(username):
        return requests.delete(config.api_auth_client_url + "/" +
                               config.api_auth_client_path + "/" +
                               config.api_auth_client_version + "/" +
                               "adminusers" + "/" +
                               username,
                               headers=AuthAPIClient.__headers())

    @staticmethod
    def put_adminuser(username, data):
        return requests.put(config.api_auth_client_url + "/" +
                            config.api_auth_client_path + "/" +
                            config.api_auth_client_version + "/" +
                            "adminusers" + "/" +
                            username,
                            json=data,
                            headers=AuthAPIClient.__headers())

    @staticmethod
    def patch_adminuser(username, data):
        return requests.patch(config.api_auth_client_url + "/" +
                              config.api_auth_client_path + "/" +
                              config.api_auth_client_version + "/" +
                              "adminusers" + "/" +
                              username,
                              json=data,
                              headers=AuthAPIClient.__headers())

    @staticmethod
    def get_adminusers(filters):
        return requests.get(config.api_auth_client_url + "/" +
                            config.api_auth_client_path + "/" +
                            config.api_auth_client_version + "/" +
                            "adminusers",
                            params=filters,
                            headers=AuthAPIClient.__headers())

    @staticmethod
    def post_adminuser(data):
        return requests.post(config.api_auth_client_url + "/" +
                             config.api_auth_client_path + "/" +
                             config.api_auth_client_version + "/" +
                             "adminusers",
                             json=data,
                             headers=AuthAPIClient.__headers())

    @staticmethod
    def get_adminuser_sessions(username, filters):
        return requests.get(config.api_auth_client_url + "/" +
                            config.api_auth_client_path + "/" +
                            config.api_auth_client_version + "/" +
                            "adminusers" + "/" +
                            username + "/" +
                            "sessions",
                            params=filters,
                            headers=AuthAPIClient.__headers())

    @staticmethod
    def delete_adminuser_sessions(username):
        return requests.delete(config.api_auth_client_url + "/" +
                               config.api_auth_client_path + "/" +
                               config.api_auth_client_version + "/" +
                               "adminusers" + "/" +
                               username + "/" +
                               "sessions",
                               headers=AuthAPIClient.__headers())

    ###########################################################################
    # Metodos para endpoint 'recovery' del AuthServer
    ###########################################################################
    @staticmethod
    def post_recovery_reset(username, data):
        return requests.post(config.api_auth_client_url + "/" +
                             config.api_auth_client_path + "/" +
                             config.api_auth_client_version + "/" +
                             "recovery" + "/" +
                             username,
                             json=data,
                             headers=AuthAPIClient.__headers())

    @staticmethod
    def get_recovery(username):
        return requests.get(config.api_auth_client_url + "/" +
                            config.api_auth_client_path + "/" +
                            config.api_auth_client_version + "/" +
                            "recovery" + "/" +
                            username,
                            headers=AuthAPIClient.__headers())

    @staticmethod
    def delete_recovery(username):
        return requests.delete(config.api_auth_client_url + "/" +
                               config.api_auth_client_path + "/" +
                               config.api_auth_client_version + "/" +
                               "recovery" + "/" +
                               username,
                               headers=AuthAPIClient.__headers())

    @staticmethod
    def post_recovery_request(data):
        return requests.post(config.api_auth_client_url + "/" +
                             config.api_auth_client_path + "/" +
                             config.api_auth_client_version + "/" +
                             "recovery",
                             json=data,
                             headers=AuthAPIClient.__headers())

    @staticmethod
    def get_recoveries(filters):
        return requests.get(config.api_auth_client_url + "/" +
                            config.api_auth_client_path + "/" +
                            config.api_auth_client_version + "/" +
                            "recovery",
                            params=filters,
                            headers=AuthAPIClient.__headers())

    ###########################################################################
    # Metodos para endpoint 'requestlog' del AuthServer
    ###########################################################################
    @staticmethod
    def get_requestlog(filters):
        return requests.get(config.api_auth_client_url + "/" +
                            config.api_auth_client_path + "/" +
                            config.api_auth_client_version + "/" +
                            "requestlog",
                            params=filters,
                            headers=AuthAPIClient.__headers())

    ###########################################################################
    # Metodos para endpoint 'stats' del AuthServer
    ###########################################################################
    @staticmethod
    def get_stats(filters):
        return requests.get(config.api_auth_client_url + "/" +
                            config.api_auth_client_path + "/" +
                            config.api_auth_client_version + "/" +
                            "stats",
                            params=filters,
                            headers=AuthAPIClient.__headers())
