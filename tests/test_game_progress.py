# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# Unit test file
# tests/test_game_progress.py

# Basado en:
# https://dev.classmethod.jp/articles/mocking-around-with-python-and-unittest/

# Importacion de librerias necesarias
import unittest
from unittest import TestCase
from unittest import mock
from http import HTTPStatus
import logging

# Importacion del archivo principal
import app_server
from tests import aux_functions


class RequestLogTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        app = app_server.app
        app.logger.setLevel(logging.ERROR)
        app.config['TESTING'] = True
        cls.app = app.test_client()
        print("Starting testing path \"/gameprogress\" of the app server...")
        # Creamos los gameprogress a ser utilizados durante los tests
        aux_functions.createGameProgress("testunituser")
        aux_functions.createGameProgress("testunituser_2")
        aux_functions.createGameProgress("testunituser_3")
        aux_functions.createGameProgress("testunituser_delete")

    @classmethod
    def tearDownClass(cls):
        # Borramos los gameprogress generados para los tests
        aux_functions.deleteGameProgress("testunituser")
        aux_functions.deleteGameProgress("testunituser_2")
        aux_functions.deleteGameProgress("testunituser_3")
        aux_functions.deleteGameProgress("testunituser_new")
        print("Finished testing path \"/gameprogress\" of the app server!")

    def test_private_endpoints_no_token_should_return_unauthorized(self):
        res = self.app.get('/api/v1/gameprogress')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.put('/api/v1/gameprogress/testunituser')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.get('/api/v1/gameprogress/testunituser')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.delete('/api/v1/gameprogress/testunituser')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_put_valid_progress_should_return_ok(self,
                                                 mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.put('/api/v1/gameprogress/testunituser',
                         headers={'Content-Type': 'application/json',
                                  'X-Auth-Token': 'AuthServer is mocked'},
                         json=dict(
                           next_level=5,
                           difficulty_level=5,
                           time_elapsed="20:10:40.045",
                           gold_collected=5000
                         ))
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual("testunituser", r.json["username"])

    @mock.patch("src.authserver_client.requests.get")
    def test_put_valid_progress_should_return_created(self,
                                                      mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.put('/api/v1/gameprogress/testunituser_new',
                         headers={'Content-Type': 'application/json',
                                  'X-Auth-Token': 'AuthServer is mocked'},
                         json=dict(
                           next_level=5,
                           difficulty_level=5,
                           time_elapsed="20:10:40.045",
                           gold_collected=5000
                         ))
        self.assertEqual(HTTPStatus.CREATED, r.status_code)
        self.assertEqual("testunituser_new", r.json["username"])

    @mock.patch("src.authserver_client.requests.get")
    def test_put_invalid_progress_should_return_bad_req(self,
                                                        mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.put('/api/v1/gameprogress/testunituser',
                         headers={'Content-Type': 'application/json',
                                  'X-Auth-Token': 'AuthServer is mocked'},
                         json=dict(
                           difficulty_level=5
                         ))
        self.assertEqual(HTTPStatus.BAD_REQUEST, r.status_code)
        self.assertEqual(-1, r.json["code"])

    @mock.patch("src.authserver_client.requests.get")
    def test_get_non_existing_user_should_return_not_found(self,
                                                           mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/gameprogress/testunituser_not_found',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.NOT_FOUND, r.status_code)
        self.assertEqual(-1, r.json["code"])

    @mock.patch("src.authserver_client.requests.get")
    def test_get_existing_user_should_return_ok(self,
                                                mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/gameprogress/testunituser',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual("testunituser", r.json["username"])

    @mock.patch("src.authserver_client.requests.get")
    def test_delete_non_existin_user_should_return_not_found(self,
                                                             mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.delete('/api/v1/gameprogress/testunituser_not_found',
                            headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.NOT_FOUND, r.status_code)
        self.assertEqual(-1, r.json["code"])

    @mock.patch("src.authserver_client.requests.get")
    def test_delete_existing_user_should_return_ok(self,
                                                   mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.delete('/api/v1/gameprogress/testunituser_delete',
                            headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual(0, r.json["code"])

    @mock.patch("src.authserver_client.requests.get")
    def test_get_all_progress_should_return_ok(self,
                                               mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/gameprogress',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual(True, len(r.json) > 0)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_all_progress_paging_should_return_ok(self,
                                                      mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/gameprogress?start=1&limit=1',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual(True, len(r.json) > 0)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_all_progress_paging_inv_should_return_ok(self,
                                                          mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/gameprogress?start=-1&limit=-1',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual(True, len(r.json) > 0)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_all_progress_pag_inv_should_return_bad_req(self,
                                                            mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/gameprogress?start=a&limit=b',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.BAD_REQUEST, r.status_code)
        self.assertEqual(-1, r.json["code"])

    @mock.patch("src.authserver_client.requests.get")
    def test_get_all_progress_non_admin_should_return_unauth(self,
                                                             mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionUser(
                                            "testunituser_other")

        r = self.app.get('/api/v1/gameprogress',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.UNAUTHORIZED, r.status_code)
        self.assertEqual(True, len(r.json) > 0)

    @mock.patch("src.authserver_client.requests.get")
    def test_put_progress_other_user_should_return_unauth(self,
                                                          mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionUser(
                                            "testunituser_other")

        r = self.app.put('/api/v1/gameprogress/testunituser',
                         headers={'Content-Type': 'application/json',
                                  'X-Auth-Token': 'AuthServer is mocked'},
                         json=dict(
                           next_level=5,
                           difficulty_level=5
                         ))
        self.assertEqual(HTTPStatus.UNAUTHORIZED, r.status_code)
        self.assertEqual(-1, r.json["code"])


if __name__ == '__main__':
    unittest.main()
