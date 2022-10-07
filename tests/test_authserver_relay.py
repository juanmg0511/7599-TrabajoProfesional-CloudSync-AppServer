# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# Unit test file
# tests/test_authserver_relay.py

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
        print("Starting testing the auth server relay of the app server...")

    @classmethod
    def tearDownClass(cls):
        print("Finished testing the auth server relay of the app server!")

    def test_private_endpoints_no_token_should_return_unauthorized(self):
        res = self.app.get('/api/v1/adminusers')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.post('/api/v1/adminusers')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.get('/api/v1/adminusers/testunituser_admin')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.put('/api/v1/adminusers/testunituser_admin')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.patch('/api/v1/adminusers/testunituser_admin')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.delete('/api/v1/adminusers/testunituser_admin')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.get('/api/v1/adminusers/testunituser_admin/sessions')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.get('/api/v1/users')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.get('/api/v1/users/testunituser')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.put('/api/v1/users/testunituser')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.patch('/api/v1/users/testunituser')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.delete('/api/v1/users/testunituser')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.get('/api/v1/users/testunituser/avatar')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.get('/api/v1/users/testunituser/sessions')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.get('/api/v1/sessions')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.get('/api/v1/sessions/token')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.delete('/api/v1/sessions/token')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.get('/api/v1/recovery')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.get('/api/v1/recovery/testunituser')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_all_admins_should_return_ok(self,
                                             mock_get):

        mock_get.side_effect = [
            aux_functions.mockCheckSessionAdmin("testunituser_admin"),
            aux_functions.mockCheckRelay(HTTPStatus.OK)]

        r = self.app.get('/api/v1/adminusers',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    @mock.patch("src.authserver_client.requests.post")
    @mock.patch("src.authserver_client.requests.get")
    def test_post_admin_should_return_created(self,
                                              mock_get_session,
                                              mock_relay,
                                              mock_get_session_2):

        mock_get_session.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")
        mock_relay.return_value = aux_functions.\
            mockCheckRelay(HTTPStatus.CREATED)
        mock_get_session_2.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")

        r = self.app.post('/api/v1/adminusers',
                          headers={'X-Auth-Token': 'AuthServer is mocked'},
                          json=dict(
                            any_payload=1,
                            response_is_mocked=1
                          ))
        self.assertEqual(HTTPStatus.CREATED, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_admin_should_return_ok(self,
                                        mock_get):

        mock_get.side_effect = [
            aux_functions.mockCheckSessionAdmin("testunituser_admin"),
            aux_functions.mockCheckRelay(HTTPStatus.OK)]

        r = self.app.get('/api/v1/adminusers/testunituser_admin',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    @mock.patch("src.authserver_client.requests.put")
    @mock.patch("src.authserver_client.requests.get")
    def test_put_admin_should_return_ok(self,
                                        mock_get_session,
                                        mock_relay,
                                        mock_get_session_2):

        mock_get_session.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")
        mock_relay.return_value = aux_functions.\
            mockCheckRelay(HTTPStatus.OK)
        mock_get_session_2.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")

        r = self.app.put('/api/v1/adminusers/testunituser_admin',
                         headers={'X-Auth-Token': 'AuthServer is mocked'},
                         json=dict(
                           any_payload=1,
                           response_is_mocked=1
                         ))
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    @mock.patch("src.authserver_client.requests.patch")
    @mock.patch("src.authserver_client.requests.get")
    def test_patch_admin_should_return_ok(self,
                                          mock_get_session,
                                          mock_relay,
                                          mock_get_session_2):

        mock_get_session.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")
        mock_relay.return_value = aux_functions.\
            mockCheckRelay(HTTPStatus.OK)
        mock_get_session_2.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")

        r = self.app.patch('/api/v1/adminusers/testunituser_admin',
                           headers={'X-Auth-Token': 'AuthServer is mocked'},
                           json=dict(
                             any_payload=1,
                             response_is_mocked=1
                           ))
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    @mock.patch("src.authserver_client.requests.delete")
    @mock.patch("src.authserver_client.requests.get")
    def test_delete_admin_should_return_ok(self,
                                           mock_get_session,
                                           mock_relay,
                                           mock_get_session_2):

        mock_get_session.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")
        mock_relay.return_value = aux_functions.\
            mockCheckRelay(HTTPStatus.OK)
        mock_get_session_2.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")

        r = self.app.delete('/api/v1/adminusers/testunituser_admin',
                            headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_admin_sessions_should_return_ok(self,
                                                 mock_get):

        mock_get.side_effect = [
            aux_functions.mockCheckSessionAdmin("testunituser_admin"),
            aux_functions.mockCheckRelay(HTTPStatus.OK)]

        r = self.app.get('/api/v1/adminusers/testunituser_admin/sessions',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_all_users_should_return_ok(self,
                                            mock_get):

        mock_get.side_effect = [
            aux_functions.mockCheckSessionAdmin("testunituser_admin"),
            aux_functions.mockCheckRelay(HTTPStatus.OK)]

        r = self.app.get('/api/v1/users',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.post")
    def test_post_user_should_return_created(self,
                                             mock_relay):

        mock_relay.return_value = aux_functions.\
            mockCheckRelay(HTTPStatus.CREATED)

        r = self.app.post('/api/v1/users',
                          headers={'X-Auth-Token': 'AuthServer is mocked'},
                          json=dict(
                            any_payload=1,
                            response_is_mocked=1
                          ))
        self.assertEqual(HTTPStatus.CREATED, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_user_should_return_ok(self,
                                       mock_get):

        mock_get.side_effect = [
            aux_functions.mockCheckSessionAdmin("testunituser_admin"),
            aux_functions.mockCheckRelay(HTTPStatus.OK)]

        r = self.app.get('/api/v1/users/testunituser',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    @mock.patch("src.authserver_client.requests.put")
    @mock.patch("src.authserver_client.requests.get")
    def test_put_user_should_return_ok(self,
                                       mock_get_session,
                                       mock_relay,
                                       mock_get_session_2):

        mock_get_session.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")
        mock_relay.return_value = aux_functions.\
            mockCheckRelay(HTTPStatus.OK)
        mock_get_session_2.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")

        r = self.app.put('/api/v1/users/testunituser',
                         headers={'X-Auth-Token': 'AuthServer is mocked'},
                         json=dict(
                           any_payload=1,
                           response_is_mocked=1
                         ))
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    @mock.patch("src.authserver_client.requests.patch")
    @mock.patch("src.authserver_client.requests.get")
    def test_patch_user_should_return_ok(self,
                                         mock_get_session,
                                         mock_relay,
                                         mock_get_session_2):

        mock_get_session.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")
        mock_relay.return_value = aux_functions.\
            mockCheckRelay(HTTPStatus.OK)
        mock_get_session_2.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")

        r = self.app.patch('/api/v1/users/testunituser',
                           headers={'X-Auth-Token': 'AuthServer is mocked'},
                           json=dict(
                             any_payload=1,
                             response_is_mocked=1
                           ))
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    @mock.patch("src.authserver_client.requests.delete")
    @mock.patch("src.authserver_client.requests.get")
    def test_delete_user_should_return_ok(self,
                                          mock_get_session,
                                          mock_relay,
                                          mock_get_session_2):

        mock_get_session.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")
        mock_relay.return_value = aux_functions.\
            mockCheckRelay(HTTPStatus.OK)
        mock_get_session_2.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")

        r = self.app.delete('/api/v1/users/testunituser',
                            headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_user_sessions_should_return_ok(self,
                                                mock_get):

        mock_get.side_effect = [
            aux_functions.mockCheckSessionAdmin("testunituser_admin"),
            aux_functions.mockCheckRelay(HTTPStatus.OK)]

        r = self.app.get('/api/v1/users/testunituser/sessions',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_user_exists_should_return_ok(self,
                                              mock_get):

        mock_get.side_effect = [
            aux_functions.mockCheckSessionAdmin("testunituser_admin"),
            aux_functions.mockCheckRelay(HTTPStatus.OK)]

        r = self.app.get('/api/v1/users/testunituser/exists',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_user_avatar_should_return_ok(self,
                                              mock_get):

        mock_get.side_effect = [
            aux_functions.mockCheckSessionAdmin("testunituser_admin"),
            aux_functions.mockCheckRelayAvatar(HTTPStatus.OK)]

        r = self.app.get('/api/v1/users/testunituser/avatar',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_user_avatar_should_return_bad_request(self,
                                                       mock_get):

        mock_get.side_effect = [
            aux_functions.mockCheckSessionAdmin("testunituser_admin"),
            aux_functions.mockCheckRelayAvatar(HTTPStatus.BAD_REQUEST)]

        r = self.app.get('/api/v1/users/testunituser/avatar',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.BAD_REQUEST, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_user_avatar_should_return_service_unavailable(self,
                                                               mock_get):

        mock_get.side_effect = [
            aux_functions.mockCheckSessionAdmin("testunituser_admin"),
            aux_functions.mockCheckRelay(HTTPStatus.SERVICE_UNAVAILABLE)]

        r = self.app.get('/api/v1/users/testunituser/avatar',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.SERVICE_UNAVAILABLE, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_all_sessions_should_return_ok(self,
                                               mock_get):

        mock_get.side_effect = [
            aux_functions.mockCheckSessionAdmin("testunituser_admin"),
            aux_functions.mockCheckRelay(HTTPStatus.OK)]

        r = self.app.get('/api/v1/sessions',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.post")
    def test_post_session_should_return_created(self,
                                                mock_relay):

        mock_relay.return_value = aux_functions.\
            mockCheckRelay(HTTPStatus.CREATED)

        r = self.app.post('/api/v1/sessions',
                          headers={'X-Auth-Token': 'AuthServer is mocked'},
                          json=dict(
                            any_payload=1,
                            response_is_mocked=1
                          ))
        self.assertEqual(HTTPStatus.CREATED, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_session_should_return_ok(self,
                                          mock_get):

        mock_get.side_effect = [
            aux_functions.mockCheckSessionAdmin("testunituser_admin"),
            aux_functions.mockCheckRelay(HTTPStatus.OK)]

        r = self.app.get('/api/v1/sessions/mock-token',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_session_another_user_should_return_unauthorized(self,
                                                                 mock_get):

        mock_get.side_effect = [
            aux_functions.mockCheckSessionUser("testunituser_another"),
            aux_functions.mockCheckRelay(HTTPStatus.OK)]

        r = self.app.get('/api/v1/sessions/mock-token',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.UNAUTHORIZED, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    @mock.patch("src.authserver_client.requests.delete")
    @mock.patch("src.authserver_client.requests.get")
    def test_delete_session_should_return_ok(self,
                                             mock_get_session,
                                             mock_relay,
                                             mock_get_session_2):

        mock_get_session.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")
        mock_relay.return_value = aux_functions.\
            mockCheckRelay(HTTPStatus.OK)
        mock_get_session_2.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")

        r = self.app.delete('/api/v1/sessions/fake-token',
                            headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    @mock.patch("src.authserver_client.requests.delete")
    @mock.patch("src.authserver_client.requests.get")
    def test_delete_all_sessions_should_return_ok(self,
                                                  mock_get_session,
                                                  mock_relay,
                                                  mock_get_session_2):

        mock_get_session.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")
        mock_relay.return_value = aux_functions.\
            mockCheckRelay(HTTPStatus.OK)
        mock_get_session_2.return_value = aux_functions.\
            mockCheckSessionAdmin("testunituser_admin")

        r = self.app.delete('/api/v1/sessions',
                            headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_all_recovery_should_return_ok(self,
                                               mock_get):

        mock_get.side_effect = [
            aux_functions.mockCheckSessionAdmin("testunituser_admin"),
            aux_functions.mockCheckRelay(HTTPStatus.OK)]

        r = self.app.get('/api/v1/recovery',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.post")
    def test_post_recovery_should_return_created(self,
                                                 mock_relay):

        mock_relay.return_value = aux_functions.\
            mockCheckRelay(HTTPStatus.CREATED)

        r = self.app.post('/api/v1/recovery',
                          headers={'X-Auth-Token': 'AuthServer is mocked'},
                          json=dict(
                            any_payload=1,
                            response_is_mocked=1
                          ))
        self.assertEqual(HTTPStatus.CREATED, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_recovery_should_return_ok(self,
                                           mock_get):

        mock_get.side_effect = [
            aux_functions.mockCheckSessionAdmin("testunituser_admin"),
            aux_functions.mockCheckRelay(HTTPStatus.OK)]

        r = self.app.get('/api/v1/recovery/mock-key',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.post")
    def test_post_recovery_should_return_ok(self,
                                            mock_relay):

        mock_relay.return_value = aux_functions.\
            mockCheckRelay(HTTPStatus.OK)

        r = self.app.post('/api/v1/recovery/mock-key',
                          headers={'X-Auth-Token': 'AuthServer is mocked'},
                          json=dict(
                            any_payload=1,
                            response_is_mocked=1
                          ))
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_auth_requestlog_should_return_ok(self,
                                                  mock_get):

        mock_get.side_effect = [
            aux_functions.mockCheckSessionAdmin("testunituser_admin"),
            aux_functions.mockCheckRelay(HTTPStatus.OK)]

        r = self.app.get('/api/v1/requestlogauthserver',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)


if __name__ == '__main__':
    unittest.main()
